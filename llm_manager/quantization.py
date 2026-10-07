"""Hardware specification dataclasses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HardwareSpec:
    """System hardware specifications."""

    cpu_cores: int = 0
    gpu_name: str = ""
    gpu_memory_gb: float = 0.0
    gpu_free_gb: float = 0.0
    system_ram_gb: float = 0.0
    system_disk_gb: float = 0.0


# Named quantizations, kept as plain constants for readability.
Q4_K_M = "Q4_K_M"
Q5_K_M = "Q5_K_M"
Q5_K_M_K_V = "Q5_K_M_K_V"
Q8_0 = "Q8_0"
FP8 = "FP8"
F16 = "F16"
BF16 = "BF16"
Q3_K_M = "Q3_K_M"
Q2_K = "Q2_K"

VALID_QUANTIZATIONS = [
    Q4_K_M,
    Q5_K_M,
    Q5_K_M_K_V,
    Q8_0,
    FP8,
    F16,
    BF16,
    Q3_K_M,
    Q2_K,
]
