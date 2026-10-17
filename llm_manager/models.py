import json
import os
import subprocess
from dataclasses import dataclass, field

from .config import ModelConfig
from .quantization import (
    VALID_QUANTIZATIONS,
    BF16,
    FP8,
    F16,
    Q2_K,
    Q3_K_M,
    Q4_K_M,
    Q5_K_M,
    Q5_K_M_K_V,
    Q8_0,
)


@dataclass
class Model:
    """A single LLM model in the registry.

    This is the canonical model descriptor used by the model discovery
    machinery.  It combines on-disk metadata (path, size) with verification
    data (context, memory-safe context) and extra metadata (declared context,
    recommended context, status).
    """

    name: str
    full_name: str
    size_gb: float = 0.0
    context_length: int = 0
    quantization: str = Q4_K_M
    precision: str = "gguf"
    device: str = "auto"
    status: str = "available"
    version: str = ""
    model_id: str = ""
    hardware_constraint: str = ""
    memory_safe_context: int = 0
    parameter_label: str = ""
    path: str = ""
    extra: dict = field(default_factory=dict)
    max_tokens: int = 512
    hardware: str | None = None

    def __post_init__(self) -> None:
        # Validate quantization; fall back to Q4_K_M for unknown tags.
        if self.quantization not in VALID_QUANTIZATIONS:
            self.quantization = Q4_K_M

    @property
    def kv_bytes_per_token(self) -> float:
        """Estimated KV-cache bytes per token for this model.

        Derived from the model size and memory-safe context: at the memory-safe
        context, the KV cache is typically ~30% of the model size (Q8_0 precision)
        or ~15% (Q4_0 precision).  Falls back to a rough default by parameter
        count when the memory-safe context is unknown.
        """
        if (
            self.memory_safe_context
            and self.memory_safe_context > 0
            and self.size_gb > 0
        ):
            return (self.size_gb * 1e9 * 0.30) / self.memory_safe_context
        # Fallback: rough estimates by parameter count range.
        if self.parameters_b:
            params = self.parameters_b * 1e9
            if params <= 3e9:
                return 190_000
            elif params <= 6e9:
                return 230_000
            elif params <= 12e9:
                return 250_000
        return 280_000

    @property
    def parameters_b(self) -> float | None:
        """Estimated parameter count in billions, or None if size is unknown.

        Derived from the file size and the quantization: e.g. a 4 GB file
        at Q4_K_M (0.5 bytes/param) holds ~8 billion parameters.
        """
        if self.size_gb <= 0:
            return None
        bytes_per_param = {
            Q4_K_M: 0.5,
            Q5_K_M: 0.625,
            Q5_K_M_K_V: 0.625,
            Q8_0: 1.0,
            FP8: 1.0,
            F16: 2.0,
            BF16: 2.0,
            Q3_K_M: 0.375,
            Q2_K: 0.25,
        }.get(self.quantization, 0.5)
        return self.size_gb / bytes_per_param

    def fits_in(self, vram_gb: float, ctx_size: int = 0) -> bool:
        """Check if this model fits in the given VRAM and context budget.

        VRAM needed is roughly the model size plus ~10% overhead, scaled up if
        the requested context exceeds the memory-safe context limit.  The
        context term is a no-op when ``memory_safe_context`` is unknown.
        """
        vram_needed = self.size_gb * 1.1
        if ctx_size > 0 and self.memory_safe_context > 0:
            ctx_ratio = ctx_size / self.memory_safe_context
            vram_needed *= ctx_ratio
        return vram_gb >= vram_needed


# ---------------------------------------------------------------------------
# Configurator types
# ---------------------------------------------------------------------------
@dataclass
class ConfigProfile:
    """A generated configuration profile for a single model."""

    model_id: str
    model_name: str
    quantization: str
    size_gb: float = 0.0
    ctx_size: int = 0
    fit_status: str = "fits"
    vram_needed: float = 0.0
    device: str = "cpu"
    path: str = ""
    kv_gb: float = 0.0
    # KV-cache precision used by llama.cpp: 8 = Q8_0, 4 = Q4_0
    kv_bits: int = 8
    # Estimated VRAM the model needs at the chosen ctx_size and kv_bits
    vram_for_model: float = 0.0
    # Estimated RAM the model needs (weights + KV cache)
    ram_gb: float = 0.0
    generated_at: str = ""
    temp: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    n_predict: int = 512
    n_gpu_layers: str = "all"
    max_tokens: int = 512


def _estimate_ram_gb(model: Model, ctx_size: int, kv_bits: int = 8) -> float:
    """Estimate the RAM (system memory) needed for a model at a given context.

    Total memory = model weight + KV cache.  The KV-cache precision
    (``kv_bits``: 8 = Q8_0, 4 = Q4_0) scales the KV-cache bytes per token.
    Returns the estimated RAM usage in GB.
    """
    base = model.size_gb * 1.1
    kv_bytes_per_token = model.kv_bytes_per_token * (kv_bits / 8.0)
    if ctx_size > 0:
        base += (ctx_size * kv_bytes_per_token) / 1024.0**3
    return base


def estimate_vram_gb(model: Model, ctx_size: int, kv_bits: int = 8) -> float:
    """Estimate the VRAM needed for a model at a given context size.

    Uses the model's size, the requested context, the model's memory-safe
    context (if known), and the KV-cache precision (``kv_bits``: 8 = Q8_0,
    4 = Q4_0).  Returns the estimated VRAM in GB.

    The formula is:
        vram = model_size_gb * 1.1 + (ctx_size * kv_bytes_per_token / (1024**3)) * (kv_bits / 8)
    where ``kv_bytes_per_token`` is the model's estimated KV-cache bytes per
    token at Q8_0 precision (4 bytes/token).
    """
    # Model weight + ~10% runtime overhead.
    base = model.size_gb * 1.1
    # KV-cache bytes per token at Q8_0, scaled by precision (Q4_0 = 4 bits, Q8_0 = 8 bits).
    kv_bytes_per_token = model.kv_bytes_per_token * (kv_bits / 8.0)
    # Add KV-cache memory for the requested context.
    if ctx_size > 0:
        base += (ctx_size * kv_bytes_per_token) / 1024.0**3
    return base


class ModelLoader:
    """Loads model definitions from JSON verification files and config.yaml,
    building a unified model registry ready for UI display."""

    def __init__(self):
        self._models = {}
        self._config_path = (
            "/home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml"
        )
        self._context_dir = (
            "/home/waflores/DevFolder/ai/local-config/context-verification"
        )
        self._load_config_yaml()

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def load_all(self):
        """Parse every JSON model file and the config.yaml into ModelConfig objects."""
        self._models.clear()
        self._load_config_yaml()
        self._parse_json_files()
        self._populate_default_constraints()
        return list(self._models.values())

    def get_models(self, device="auto"):
        """Return models suitable for the given device (auto = all)."""
        if device == "auto":
            return list(self._models.values())
        # Core match: models whose device matches the requested device.
        matched = [
            m for m in self._models.values() if device.lower() in m.device.lower()
        ]
        # Fallback: append models marked as CPU-only when the requested device
        # is CPU- or GPU-compatible but none of the requested devices matched.
        if not matched:
            matched = [m for m in self._models.values() if m.device == "cpu"]
        return matched

    def get_available(self):
        """Return only models currently available for use."""
        return [m for m in self._models.values() if m.status == "available"]

    def get_loaded(self):
        """Return models currently loaded into the active device."""
        return [m for m in self._models.values() if m.status == "loaded"]

    def get_swapped(self):
        """Return models currently stored in swap (not loaded)."""
        return [m for m in self._models.values() if m.status == "swapped"]

    @property
    def model_count(self):
        return len(self._models)

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                   #
    # ------------------------------------------------------------------ #

    def _load_config_yaml(self):
        """Read llama-swap/config.yaml for global constraints."""
        if not os.path.exists(self._config_path):
            return
        try:
            with open(self._config_path, "r") as f:
                config = {}
                for line in f:
                    line = line.rstrip()
                    if not line or line.startswith(("#", "  ")):
                        continue
                    if ":" in line:
                        key, _, value = line.partition(":")
                        key = key.strip()
                        value = value.strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        config[key] = value
        except Exception as exc:
            print(f"[MODELLOADER] warning: could not parse config.yaml: {exc}")
        self._config = config

    def _parse_json_files(self):
        """Parse every lms-*.json in the context-verification directory."""
        if not os.path.isdir(self._context_dir):
            return

        for json_path in self._context_dir.glob("*.json"):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                for entry in data.get("models", []):
                    if not entry:
                        continue
                    # The "model" field is a dot-separated ID like
                    #   lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m:latest
                    model_id = entry.get("model", "")
                    if not model_id:
                        continue
                    # Parse the tag: everything before :latest
                    model_name, _, tag = model_id.rpartition(":")
                    tag = tag or "latest"

                    # Try to extract model name from the path part
                    # e.g. "qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m" -> "Qwen3 6B (Q4_K_M)"
                    model_short = self._parse_model_name(model_name)

                    # Size from the JSON field
                    size_gb = float(entry.get("modelSizeGB", 0))
                    float(entry.get("targetTokens", 0))
                    int(
                        entry.get("suggestedContext", 0)
                        or entry.get("recommendedContext", 0)
                    )

                    memory_safe = int(entry.get("memoryLimitedContext", 0))

                    config = ModelConfig(
                        name=model_name,
                        full_name=model_short,
                        parameters=(
                            model_name.split("-")[1]
                            if "-b-" in model_name
                            else model_name.split("-")[0]
                        ),
                        size_gb=size_gb,
                        context_length=int(entry.get("targetTokens", 0)),
                        quantization=self._extract_quantization(model_name),
                        precision="gguf",
                        device="auto",
                        hardware="",
                        status="available",
                        version=tag,
                        model_id=model_id,
                        hardware_constraint="",
                        memory_safe_context=int(memory_safe),
                    )

                    self._models[model_name] = config
            except Exception as exc:
                print(f"[MODELLOADER] warning: could not parse {json_path}: {exc}")

    def _populate_default_constraints(self):
        """Apply known hardware constraints for the RTX 5070 Max-Q + Intel UG."""
        vram = 8.0  # GPU VRAM in GB

        for model in self._models.values():
            model_constraint = (
                f"Max {int(vram / model.size_gb) if model.size_gb > 0 else 999} models"
            )
            if model.size_gb > 6:
                model_constraint = f"VRAM: {model.size_gb:.1f} GB (needs {vram:.1f} GB)"
            model.hardware_constraint = model_constraint

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_model_name(model_id: str):
        """Convert a model ID like 'qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m'
        into readable text."""
        parts = model_id.split("-", 3)
        if len(parts) < 3:
            return model_id
        prefix = parts[0].capitalize().replace("-", " ")
        size = parts[2].capitalize()  # e.g. "Qwen3 6B"
        quant = parts[3].capitalize().replace("-", " ").replace("_", " ")
        return f"{prefix} {size} ({quant})"

    @staticmethod
    def _extract_quantization(model_id: str):
        """Extract quantization tag from model ID."""
        if "-q4_k_m" in model_id:
            return "Q4_K_M"
        if "-q5_k_m" in model_id:
            return "Q5_K_M"
        if "-bf16" in model_id:
            return "BF16"
        if "-q4_k_m_k_v" in model_id:
            return "Q4_K_M_K_V"
        if "-q5_k_m_k_v" in model_id:
            return "Q5_K_M_K_V"
        return "Q4_K_M"  # default

    def _get_vram_available(self):
        """Return estimated VRAM available on CUDA0."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory_free"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.splitlines():
                if "MiB" in line:
                    return int(line.split()[-1].replace("MiB", "")) / (1024 * 1024)
        except Exception:
            pass
        return 0.0

    def _get_total_memory(self):
        """Return total system RAM in GB."""
        try:
            result = subprocess.run(
                ["free", "-m", "--output=value=mem_total"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.splitlines():
                if "Mem total" in line:
                    return float(line.split()[-1]) / 1024
        except Exception:
            pass
        return 0.0

    # ------------------------------------------------------------------ #
    #  Public helpers (for the CLI)                                        #
    # ------------------------------------------------------------------ #

    def print_model_summary(self):
        """Print a neatly formatted summary of all known models."""
        models = sorted(self._models.values(), key=lambda m: m.size_gb)
        print(f"\n{'=' * 72}")
        print(f"  LLM Model Registry: {len(self._models)} models")
        print(f"  {'=' * 72}")
        print(f"  {'Model':<42} {'Size':>8} {'Context':>10} {'Quant':>8} {'VRAM':>10}")
        print(f"  {'-' * 72}")
        for m in models:
            vram = m.size_gb * 8  # Q4_K_M ≈ 0.25 GB/GB
            ctx = str(m.context_length)
            if len(ctx) > 9:
                ctx = "..." + ctx[-6:]
            print(
                f"  {m.full_name:<42} {m.size_gb:>7.1f} GB {ctx:>10} "
                f"{m.quantization:>8} {vram:>8.1f} GB"
            )
        print(f"{'=' * 72}")

    def print_device_constraints(self):
        """Print hardware constraints for each model."""
        vram = self._get_vram_available()
        print(f"\n  VRAM available: {vram:.1f} GB")
        print("  Max models simultaneously (8GB VRAM / 2.5B ≈ 3): 3-4 small models")
        print()
        for model in sorted(self._models.values(), key=lambda m: m.size_gb):
            print(f"  - {model.full_name}: {model.hardware_constraint}")

    def save_model_list(self, output="models.json"):
        """Save the complete model registry to a JSON file."""
        data = {}
        for model in self._models.values():
            data[model.model_id] = {
                "full_name": model.full_name,
                "parameters": model.parameters,
                "size_gb": round(model.size_gb, 2),
                "context_length": model.context_length,
                "quantization": model.quantization,
                "precision": model.precision,
                "status": model.status,
                "version": model.version,
                "constraints": model.hardware_constraint,
            }
        with open(output, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved model list to {output}")

    def load_model_list(self, path="models.json"):
        """Load a previously saved model list."""
        if not os.path.exists(path):
            print(f"  No model list file at {path}. Run load_all() first.")
            return {}
        with open(path, "r") as f:
            data = json.load(f)
        return data

    @property
    def config(self):
        return self._config


# Module-level loader instance
model_loader = ModelLoader()
