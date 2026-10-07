"""Domain models for the LLM manager web application."""

from __future__ import annotations

from dataclasses import dataclass, field

from .quantization import (
    BF16,
    F16,
    FP8,
    Q2_K,
    Q3_K_M,
    Q4_K_M,
    Q5_K_M,
    Q5_K_M_K_V,
    Q8_0,
    VALID_QUANTIZATIONS,
)

# Bits per weight used for the GGUF file size -> parameter count conversion.
BITS_PER_QUANT: dict[str, int] = {
    Q4_K_M: 4,
    Q5_K_M: 5,
    Q5_K_M_K_V: 5,
    Q8_0: 8,
    FP8: 8,
    F16: 16,
    BF16: 16,
    Q3_K_M: 3,
    Q2_K: 2,
}

# Empirical KV-cache estimate: megabytes of KV cache per token per 1B of parameters.
KV_BYTES_PER_TOKEN_PER_B: dict[str, float] = {
    Q4_K_M: 0.015,
    Q5_K_M: 0.020,
    Q5_K_M_K_V: 0.022,
    Q8_0: 0.025,
    FP8: 0.020,
    F16: 0.035,
    BF16: 0.035,
    Q3_K_M: 0.010,
    Q2_K: 0.007,
}


def estimate_vram_gb(model: Model, ctx_size: int) -> float:
    """Estimate the GPU memory the given model needs at the given context size.

    Combines: model file size + KV-cache (params_b * KV_bytes_per_token_per_B
    * context) + overhead constant.

    KV_BYTES_PER_TOKEN_PER_B gives megabytes of KV cache per token for each
    billion parameters, so the KV term is simply the product of the three.
    """
    BITS_PER_QUANT.get(model.quantization, 4)

    # File size already known in GB.
    file_gb = model.size_gb

    # KV-cache memory: (params in billions) * (MB/token/B) * (context tokens)
    params_b = model.parameters_b
    kv_mb = 0.0
    if params_b:
        kv_mb = (
            params_b
            * KV_BYTES_PER_TOKEN_PER_B.get(model.quantization, 0.02)
            * max(1, ctx_size)
        )
    kv_gb = kv_mb / 1024.0

    # Small overhead to cover fused attention, metadata, and padding.
    overhead_gb = 0.35

    return file_gb + kv_gb + overhead_gb


@dataclass
class Model:
    """A downloaded LLM and its parameter metadata."""

    name: str
    full_name: str
    size_gb: float = 0.0
    context_length: int = 0
    max_tokens: int = 0
    quantization: str = Q4_K_M
    precision: str = "gguf"
    device: str = "cuda"
    hardware: str = ""
    status: str = "available"  # available | loaded | swapped
    version: str = ""
    model_id: str = ""
    hardware_constraint: str = ""
    memory_safe_context: int = 0
    path: str = ""
    parameter_label: str = ""
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.quantization not in VALID_QUANTIZATIONS:
            self.quantization = Q4_K_M

    @property
    def parameters_b(self) -> float | None:
        """Approximate parameter count in billions, derived from size + quantization."""
        if self.size_gb <= 0:
            return None
        bpp = BITS_PER_QUANT.get(self.quantization, 4)
        return (self.size_gb * 1e9) / (bpp / 8) / 1e9

    @property
    def parameter_count(self) -> float | None:
        """Alias for parameters_b kept for backwards compatibility."""
        return self.parameters_b

    @property
    def kv_gb(self) -> float:
        """Estimated KV-cache memory for the model's current context."""
        return estimate_vram_gb(self, self.context_length)

    def fits_in(self, vram_gb: float, ctx_size: int) -> bool:
        """Return True if this model fits in the given VRAM at the given context."""
        return estimate_vram_gb(self, ctx_size) <= vram_gb


@dataclass
class ConfigProfile:
    """A generated configuration for a single model, hardware-aware."""

    model_id: str
    model_name: str
    quantization: str
    size_gb: float = 0.0
    ctx_size: int = 0
    temp: float = 0.7
    top_k: int = 40
    top_p: float = 0.9
    n_predict: int = 512
    device: str = "cuda"
    n_gpu_layers: str = "all"
    max_tokens: int = 512
    path: str = ""
    generated_at: str = ""
    kv_gb: float = 0.0
    fit_status: str = "fits"  # fits | over_vram | fits_with_capping


# Convenience aliases for the module-level namespace.
Quantization = str
