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
