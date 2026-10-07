"""Hardware-aware config generation for downloaded LLMs.

Takes the detected hardware and the model registry, then generates
``ConfigProfile`` objects that pick the right quantization, context size and
VRAM slicing strategy so the model fits in the available GPU memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from .hardware_spec import HardwareSpec
from .loader import discover_models
from .models import ConfigProfile, Model, estimate_vram_gb

# Hardware tiers: <min_free_vram_gb> -> config override applied when the model
# would otherwise not fit.  The value is the config key that a llama-swap user
# would set (e.g. nGpuLayers, ctxSize).
TIER_OVERRIDES: dict[float, dict[str, str | int]] = {
    # Laptop GPUs (~10 GB free) -> cap context, prefer Q4_K_M.
    10.0: {"n_gpu_layers": 999999, "ctxSize": "16384"},
    # Integrated / modest discrete GPUs (~15 GB free).
    15.0: {"n_gpu_layers": 999999, "ctxSize": "32768"},
    # Mid-range discrete (~20 GB free).
    20.0: {"n_gpu_layers": 999999, "ctxSize": "65536"},
}


def detect_tier(hw: HardwareSpec) -> float:
    """Return the VRAM-free tier threshold for the given hardware.

    A lower threshold means more aggressive capping. Laptop GPUs (RTX 5070 Max-Q
    ~8 GB) are tier 10 GB.
    """
    free_gb = hw.gpu_free_gb
    if free_gb <= 10:
        return 10.0
    if free_gb <= 15:
        return 15.0
    if free_gb <= 20:
        return 20.0
    return 20.0


def cap_context(
    model: Model, tier_override: dict[str, str | int] | None
) -> tuple[int, int]:
    """Return (ctx_size, memory_safe_ctx) for a model.

    Prefers the hardware-safe context verified in the JSON metadata; otherwise
    falls back to a context capped to the model's declared context.
    """
    safe = model.memory_safe_context or 0
    if safe > 0:
        return safe, safe
    return model.context_length, model.context_length


def generate_profiles(
    *,
    hardware: HardwareSpec,
    models: list[Model] | None = None,
    models_dir: str | None = None,
) -> list[ConfigProfile]:
    """Generate a hardware-aware profile for every model in the registry."""
    models = models or discover_models()
    models_dir = models_dir or "/home/waflores/.lmstudio/models/lmstudio-community"
    tier = detect_tier(hardware)
    profiles: list[ConfigProfile] = []

    for model in models:
        if not model.path:
            # Nothing to run; still produce a profile so the UI can show the
            # model's availability status.
            profiles.append(
                ConfigProfile(
                    model_id=model.model_id,
                    model_name=model.full_name,
                    quantization=model.quantization,
                    size_gb=model.size_gb,
                    ctx_size=model.context_length,
                    device=model.device,
                    path="",
                    fit_status="not_found",
                    kv_gb=0.0,
                    generated_at=datetime.now(UTC).isoformat(),
                )
            )
            continue

        # Determine the context the model should run at.
        ctx_size, memory_safe_ctx = cap_context(model, TIER_OVERRIDES.get(tier))

        # Check whether the model fits in the available VRAM at the chosen
        # context.  ``fits_in`` uses the KV-cache estimate plus the file size.
        vram_for_model = estimate_vram_gb(model, ctx_size)
        fits = vram_for_model <= (hardware.gpu_free_gb if hardware.gpu_free_gb else 0.0)

        if not fits and tier > 10.0:
            # Try a more aggressive cap for this tier.
            for _tval, override in sorted(TIER_OVERRIDES.items()):
                if _tval >= tier:
                    ctx_size, _ = cap_context(model, override)
                    vram_for_model = estimate_vram_gb(model, ctx_size)
                    if vram_for_model <= (
                        hardware.gpu_free_gb if hardware.gpu_free_gb else 0.0
                    ):
                        fits = True
                        break

        if not fits:
            # Reduction candidates in ascending order of aggressiveness.
            for reduction in (8192, 1024, 256):
                ctx_size, _ = cap_context(model, {"ctxSize": str(reduction)})
                vram_for_model = estimate_vram_gb(model, ctx_size)
                if vram_for_model <= (
                    hardware.gpu_free_gb if hardware.gpu_free_gb else 0.0
                ):
                    fits = True
                    break

        if not fits:
            fit_status = "over_vram"
        elif ctx_size < memory_safe_ctx:
            fit_status = "fits_with_capping"
        else:
            fit_status = "fits"

        profiles.append(
            ConfigProfile(
                model_id=model.model_id,
                model_name=model.full_name,
                quantization=model.quantization,
                size_gb=model.size_gb,
                ctx_size=ctx_size,
                temp=model.extra.get("temp", 0.7),
                top_k=model.extra.get("top_k", 40),
                top_p=model.extra.get("top_p", 0.9),
                n_predict=model.extra.get("n_predict", 512),
                device=model.device,
                n_gpu_layers=str(
                    TIER_OVERRIDES.get(tier, {}).get("n_gpu_layers", "all")
                ),
                max_tokens=model.max_tokens or 512,
                path=model.path,
                generated_at=datetime.now(UTC).isoformat(),
                kv_gb=vram_for_model,
                fit_status=fit_status,
            )
        )

    return profiles


@dataclass
class Config:
    """Top-level configuration for the web app."""

    hardware: HardwareSpec
    profiles: list[ConfigProfile] = field(default_factory=list)
    models: list[Model] = field(default_factory=list)
    generated_at: str = ""
    base_models_dir: str = ""

    @property
    def free_vram_gb(self) -> float:
        """VRAM still available for the next swap."""
        used = sum(
            p.kv_gb + p.size_gb + 0.35 for p in self.profiles if p.fit_status == "fits"
        )
        return max(0.0, self.hardware.gpu_free_gb - used)

    @property
    def total_vram_gb(self) -> float:
        return self.hardware.gpu_memory_gb


def build_config(*, hardware: HardwareSpec | None = None) -> Config:
    """Discover models and generate profiles in one call."""
    hardware = hardware or _detect_and_return()
    models = discover_models()
    profiles = generate_profiles(hardware=hardware, models=models)
    return Config(
        hardware=hardware,
        profiles=profiles,
        models=models,
        generated_at=datetime.now(UTC).isoformat(),
        base_models_dir="/home/waflores/.lmstudio/models/lmstudio-community",
    )


def _to_serializable(obj) -> dict:
    """Convert domain objects to plain dicts for JSON templating."""
    if obj is None:
        return None
    if isinstance(obj, Config):
        return {
            "hardware": _to_serializable(obj.hardware),
            "profiles": [_to_serializable(p) for p in obj.profiles],
            "models": [_to_serializable(m) for m in obj.models],
            "generated_at": obj.generated_at,
            "base_models_dir": obj.base_models_dir,
        }
    if isinstance(obj, HardwareSpec):
        return {
            "cpu_cores": obj.cpu_cores,
            "gpu_name": obj.gpu_name,
            "gpu_memory_gb": obj.gpu_memory_gb,
            "gpu_free_gb": obj.gpu_free_gb,
            "system_ram_gb": obj.system_ram_gb,
            "system_disk_gb": obj.system_disk_gb,
        }
    if isinstance(obj, Model):
        return {
            "name": obj.name,
            "full_name": obj.full_name,
            "size_gb": obj.size_gb,
            "context_length": obj.context_length,
            "max_tokens": obj.max_tokens,
            "quantization": obj.quantization,
            "precision": obj.precision,
            "device": obj.device,
            "hardware": obj.hardware,
            "status": obj.status,
            "version": obj.version,
            "model_id": obj.model_id,
            "hardware_constraint": obj.hardware_constraint,
            "memory_safe_context": obj.memory_safe_context,
            "path": obj.path,
            "parameter_label": obj.parameter_label,
            "extra": obj.extra,
        }
    if isinstance(obj, ConfigProfile):
        return {
            "model_id": obj.model_id,
            "model_name": obj.model_name,
            "quantization": obj.quantization,
            "size_gb": obj.size_gb,
            "ctx_size": obj.ctx_size,
            "temp": obj.temp,
            "top_k": obj.top_k,
            "top_p": obj.top_p,
            "n_predict": obj.n_predict,
            "device": obj.device,
            "n_gpu_layers": obj.n_gpu_layers,
            "max_tokens": obj.max_tokens,
            "path": obj.path,
            "generated_at": obj.generated_at,
            "kv_gb": obj.kv_gb,
            "fit_status": obj.fit_status,
        }
    # Fall back to attribute lookup (dataclasses / simple objects).
    if hasattr(obj, "__dict__"):
        return {k: _to_serializable(v) for k, v in obj.__dict__.items()}
    return str(obj)


def _detect_and_return():
    # Import here to avoid circular imports.
    from .hardware import detect_hardware

    return detect_hardware()
