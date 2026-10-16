"""Hardware-aware config generation for downloaded LLMs.

Takes the detected hardware and the model registry, then generates
``ConfigProfile`` objects that pick the right quantization, context size,
KV-cache precision and VRAM slicing strategy so the model fits in the
available GPU memory.
"""


from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .hardware_spec import HardwareSpec
from .loader import discover_models
from .models import (
    ConfigProfile,
    Model,
    _estimate_ram_gb,
    estimate_vram_gb,
)


# Hardware tiers: <min_free_vram_gb> -> config override applied when the model
# would otherwise not fit.  The value is the config key that a llama-swap
# user would set (e.g. nGpuLayers, ctxSize).
TIER_OVERRIDES: dict[float, dict[str, str | int]] = {
    # Laptop GPUs (~10 GB free) -> cap context, prefer Q4_K_M.
    10.0: {"n_gpu_layers": 999999, "ctxSize": "16384"},
    # Integrated / modest discrete GPUs (~15 GB free).
    15.0: {"n_gpu_layers": 999999, "ctxSize": "32768"},
    # Mid-range discrete (~20 GB free).
    20.0: {"n_gpu_layers": 999999, "ctxSize": "65536"},
}

# KV cache bits used when no per-model override is present.
DEFAULT_KV_BITS = 8  # Q8_0 (high quality)
Q4_K_M_KV_BITS = 4   # Q4_K_M KV precision (halves KV-cache memory)

# Context reduction ladder if a model still doesn't fit after tier capping.
CONTEXT_REDUCTION_LADDER = (8192, 1024, 256)


def detect_tier(hw: HardwareSpec) -> float:
    """Return the VRAM-free tier threshold for the given hardware.

    A lower threshold means more aggressive capping. Laptop GPUs (RTX 5070
    Max-Q ~8 GB) are tier 10 GB.
    """
    free_gb = hw.gpu_free_gb
    if free_gb <= 10:
        return 10.0
    if free_gb <= 15:
        return 15.0
    if free_gb <= 20:
        return 20.0
    return 20.0


def _kv_bytes_per_token(model: Model) -> float:
    """Estimate the KV-cache bytes per token for a model.

    Derived from the model size and the memory-safe context (if known);
    otherwise a rough default for the model's parameter range.
    """
    if model.memory_safe_context and model.memory_safe_context > 0:
        # At the memory-safe context the model fits with ~30% overhead.
        # The margin above the raw model size is the KV cache.
        overhead_gb = model.size_gb * 0.30
        return (overhead_gb * 1e9) / model.memory_safe_context
    # Rough defaults by parameter range.
    if model.size_gb <= 3:
        return 190_000
    elif model.size_gb <= 6:
        return 230_000
    elif model.size_gb <= 12:
        return 250_000
    return 280_000


def _kv_bytes_with_precision(kv_bytes: float, kv_bits: int) -> float:
    """Scale KV bytes by precision (Q4_0 = 4 bits, Q8_0 = 8 bits)."""
    return kv_bytes * (kv_bits / 8.0)


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


def optimize_context(
    *,
    model: Model,
    max_ctx: int,
    kv_bits: int,
    vram_limit_gb: float,
) -> int:
    """Return the largest ctx_size that fits in vram_limit_gb.

    Starts at ``max_ctx`` (already capped by the hardware tier) and reduces
    it algebraically until the estimated VRAM fits.
    """
    if max_ctx <= 0:
        return 0
    kv_bytes = _kv_bytes_per_token(model)
    # Model weight + fixed overhead.
    base = model.size_gb * 1.1
    ctx = max_ctx
    while ctx > 256:
        kv_bytes_scaled = _kv_bytes_with_precision(kv_bytes, kv_bits)
        vram = base + (ctx * kv_bytes_scaled / 1024.0**3)
        if vram <= vram_limit_gb:
            return ctx
        ctx = int(ctx * 0.85)  # reduce ~15% per step
    # Try the reduction ladder (larger, safer drops) if we dropped below 256.
    for reduction in CONTEXT_REDUCTION_LADDER:
        if reduction <= 256:
            ctx = reduction
            kv_bytes_scaled = _kv_bytes_with_precision(kv_bytes, kv_bits)
            vram = base + (ctx * kv_bytes_scaled / 1024.0**3)
            if vram <= vram_limit_gb:
                return ctx
    return 0


def generate_profiles(
    *,
    hardware: HardwareSpec,
    models: list[Model] | None = None,
    models_dir: str | None = None,
    kv_bits: int = 8,
    ram_limit_gb: float | None = None,
) -> list[ConfigProfile]:
    """Generate a hardware-aware profile for every model in the registry.

    Parameters:
        kv_bits: Default KV-cache precision (8 = Q8_0, 4 = Q4_0).  Models with
            a dedicated KV-quantization tag (e.g. Q4_K_M_K_V) get their own KV
            precision from the loader.
        ram_limit_gb: Optional RAM limit in GB.  If set, models that exceed this
            limit are capped to a smaller context or marked "over_ram".
    """
    models = models or discover_models()
    models_dir = models_dir or "/home/waflores/.lmstudio/models/lmstudio-community"
    tier = detect_tier(hardware)
    profiles: list[ConfigProfile] = []

    for model in models:
        if not model.path:
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

        # Determine the context the model should run at (tier override first).
        ctx_size, memory_safe_ctx = cap_context(model, TIER_OVERRIDES.get(tier))

        # Try to fit the model at the desired context.
        vram_for_model = estimate_vram_gb(model, ctx_size, kv_bits)
        free_vram = hardware.gpu_free_gb or 0.0
        # RAM limit: either explicit (ram_limit_gb) or the system's total RAM.
        ram_limit = (
            ram_limit_gb if ram_limit_gb is not None else hardware.system_ram_gb
        )

        # Fit check:
        #   - VRAM constraint: the model's weights + KV cache must fit in GPU VRAM,
        #     unless RAM is available to hold the overflow (weights always in RAM).
        #   - RAM constraint: weights + spilled KV cache must fit in RAM.
        # Total memory needed = vram_for_model (weights + KV cache)
        # VRAM holds min(vram_for_model, free_vram)
        # RAM holds the rest: max(0, vram_for_model - free_vram) + weights
        ram_for_weights = model.size_gb * 1.1
        ram_for_overflow_kv = max(0.0, vram_for_model - free_vram)
        ram_needed = ram_for_weights + ram_for_overflow_kv

        if ram_limit_gb is not None:
            fits = ram_needed <= ram_limit
        else:
            fits = vram_for_model <= free_vram
            if not fits and tier > 10.0:
                # Apply a tier-specific cap for a larger GPU.
                for _tval, override in sorted(TIER_OVERRIDES.items()):
                    if _tval >= tier:
                        ctx_size, _ = cap_context(model, override)
                        vram_for_model = estimate_vram_gb(model, ctx_size, kv_bits)
                        if vram_for_model <= free_vram:
                            fits = True
                            break

        if not fits:
            # Industrial-strength sweep: try KV-bit precision toggles and
            # context reductions until we find a fit or give up.
            for kvb in (8, 4):
                for reduction in CONTEXT_REDUCTION_LADDER:
                    candidate_ctx = min(ctx_size, reduction)
                    if candidate_ctx <= 0:
                        continue
                    vram_for_model = estimate_vram_gb(model, candidate_ctx, kvb)
                    # RAM check: weights + spilled KV cache must fit within RAM limit
                    ram_needed = ram_for_weights + max(0.0, vram_for_model - free_vram)
                    if vram_for_model <= free_vram or ram_needed <= ram_limit:
                        ctx_size = candidate_ctx
                        kv_bits = kvb
                        fits = True
                        break
                if fits:
                    break

        if not fits:
            fit_status = "over_vram"
        elif ctx_size < memory_safe_ctx:
            fit_status = "fits_with_capping"
        else:
            fit_status = "fits"

        # Estimate the final VRAM and RAM at the chosen context and KV precision.
        kv_bytes_per_token = model.kv_bytes_per_token * (kv_bits / 8.0)
        final_kv_gb = (ctx_size * kv_bytes_per_token) / 1024.0**3
        final_vram = estimate_vram_gb(model, ctx_size, kv_bits)
        ram_gb = _estimate_ram_gb(model, ctx_size, kv_bits)

        profiles.append(
            ConfigProfile(
                model_id=model.model_id,
                model_name=model.full_name,
                quantization=model.quantization,
                size_gb=model.size_gb,
                ctx_size=ctx_size,
                kv_bits=kv_bits,
                fit_status=fit_status,
                # Parameters tunable via llama.cpp
                n_gpu_layers=str(
                    TIER_OVERRIDES.get(tier, {}).get("n_gpu_layers", "all")
                ),
                temp=model.extra.get("temp", 0.7),
                top_k=model.extra.get("top_k", 40),
                top_p=model.extra.get("top_p", 0.9),
                n_predict=model.extra.get("n_predict", 512),
                device=model.device,
                max_tokens=model.max_tokens or 512,
                path=model.path,
                kv_gb=final_kv_gb,
                vram_for_model=final_vram,
                ram_gb=ram_gb,
                generated_at=datetime.now(UTC).isoformat(),
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
    # RAM limit in GB (if any).  When set, models that exceed this limit are
    # capped to a smaller context or marked "over_ram".
    ram_limit_gb: float | None = None

    @property
    def free_vram_gb(self) -> float:
        """VRAM still available for the next swap."""
        used = sum(
            p.kv_gb + p.size_gb + 0.35
            for p in self.profiles
            if p.fit_status == "fits"
        )
        return max(0.0, self.hardware.gpu_free_gb - used)

    @property
    def total_vram_gb(self) -> float:
        return self.hardware.gpu_memory_gb

    @property
    def free_ram_gb(self) -> float:
        """RAM still available for the next swap."""
        used = sum(p.ram_gb for p in self.profiles if p.fit_status == "fits")
        return max(0.0, self.hardware.system_ram_gb - used) if self.ram_limit_gb else 0.0


def build_config(
    *,
    hardware: HardwareSpec | None = None,
    ram_limit_gb: float | None = None,
) -> Config:
    """Discover models and generate profiles in one call."""
    hardware = hardware or _detect_and_return()
    models = discover_models()
    profiles = generate_profiles(hardware=hardware, models=models, ram_limit_gb=ram_limit_gb)
    return Config(
        hardware=hardware,
        profiles=profiles,
        models=models,
        generated_at=datetime.now(UTC).isoformat(),
        base_models_dir="/home/waflores/.lmstudio/models/lmstudio-community",
        ram_limit_gb=ram_limit_gb,
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
            "ram_limit_gb": obj.ram_limit_gb,
            # Derived totals for the configs page summary. They are computed
            # above in the dataclass and re-added here so a fresh /reload can
            # re-render the summary without a round trip to the frontend.
            "total_vram_gb": obj.total_vram_gb,
            "free_vram_gb": obj.free_vram_gb,
            "models_count": len(obj.models),
            "profiles_count": len(obj.profiles),
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
            "kv_bits": obj.kv_bits,
            "fit_status": obj.fit_status,
            "temp": obj.temp,
            "top_k": obj.top_k,
            "top_p": obj.top_p,
            "n_predict": obj.n_predict,
            "device": obj.device,
            "n_gpu_layers": obj.n_gpu_layers,
            "max_tokens": obj.max_tokens,
            "path": obj.path,
            "kv_gb": obj.kv_gb,
            "vram_for_model": obj.vram_for_model,
            "ram_gb": obj.ram_gb,
            "generated_at": obj.generated_at,
        }
    if hasattr(obj, "__dict__"):
        return {k: _to_serializable(v) for k, v in obj.__dict__.items()}
    return str(obj)


def _detect_and_return():
    from .hardware import detect_hardware

    return detect_hardware()
