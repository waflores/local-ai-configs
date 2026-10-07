"""
Configuration and data constants for the LLM Manager web application.
"""

from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a single LLM model."""

    name: str
    full_name: str
    parameters: str
    size_gb: float
    context_length: int = 0
    max_tokens: int = 0
    quantization: str = "Q4_K_M"
    precision: str = "gguf"
    device: str = "cpu"
    hardware: str = ""
    status: str = "available"
    version: str = ""
    model_id: str = ""
    hardware_constraint: str = ""
    memory_safe_context: int = 0


@dataclass
class HardwareSpec:
    """System hardware specifications."""

    cpu_cores: int = 0
    gpu_name: str = ""
    gpu_memory_gb: float = 0.0
    gpu_free_gb: float = 0.0
    system_ram_gb: float = 0.0
    system_disk_gb: float = 0.0


@dataclass
class SwapConfig:
    """Model swapping configuration."""

    enable_swapping: bool = True
    auto_swap: bool = False
    max_concurrent: int = 2
    swap_ttl: int = 3600
    use_vulkan: bool = True


@dataclass
class InferenceConfig:
    """Inference settings."""

    device: str = "cpu"
    temperature: float = 0.7
    max_tokens: int = 512
    n: int = 1
    top_p: float = 0.95
    top_k: int = 50
    frequency_penalty: float = 0.0
    repetition_penalty: float = 1.0


# Default configuration values
DEFAULTS = {
    "model_search_path": "/home/waflores/.lmstudio/models",
    "log_file": "inference.log",
    "cache_file": "model_cache.json",
    "allow_invalid_config": True,
    "allow_disabled_config": True,
}

VALID_QUANTIZATIONS = [
    "q4_k_m",
    "q5_k_m",
    "q4_k_m_k_v",
    "q5_k_m_k_v",
    "f16",
    "bf16",
    "fp8",
]
VALID_DEVICES = ["cpu", "cuda", "vulkan"]


# Anti-pattern warnings
ANTI_PATTERNS = {
    "loading_all_at_once": "Loading all models simultaneously will exceed VRAM. "
    "Use model swapping to load only needed models.",
    "using_f16_on_limited_gpu": "FP16/BF16 precision on RTX 5070 (8GB VRAM) will "
    "limit to 2-3 models. Use Q4_K_M quantization for 22 models.",
}

# Allowed model types for GPU execution
GPU_ALLOWED_MODELS = [
    "codellama",
    "llama3",
    "llama3.1",
    "llama3.2",
    "qwen3",
    "devstral",
    "ministral",
    "phi-4",
    "gemma",
    "nemotron",
    "llama2",
    "phi",
    "mistral",
    "gemma",
    "code",
    "opt",
    "llama3",
    "phi",
    "llama2",
]
