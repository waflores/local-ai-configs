"""Hardware detection for the LLM manager.

Reads the local machine (nvidia-smi for CUDA, free for RAM, nproc for CPU)
and exposes a HardwareSpec object. All I/O is injectable so unit tests can
override it without touching the real system.
"""

from __future__ import annotations

import subprocess

from .hardware_spec import HardwareSpec


def _run(cmd, **kwargs):
    """Run a subprocess, returning a CompletedProcess. Safe to monkeypatch in tests."""
    return subprocess.run(cmd, capture_output=True, text=True, check=False, **kwargs)


def detect_hardware() -> HardwareSpec:
    """Detect local hardware and return a HardwareSpec."""
    spec = HardwareSpec()

    # --- CUDA GPU (nvidia-smi) ---
    try:
        proc = _run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ],
            check=False,
        )
        for line in proc.stdout.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                spec.gpu_name = parts[0]
                try:
                    spec.gpu_memory_gb = float(parts[1]) / 1024.0
                except ValueError:
                    pass
                try:
                    spec.gpu_free_gb = float(parts[2]) / 1024.0
                except ValueError:
                    pass
                break
    except Exception:
        pass

    # --- System RAM (free -m) ---
    try:
        proc = _run(["free", "-m"], check=False)
        for line in proc.stdout.splitlines():
            parts = line.split()
            if parts and parts[0] == "Mem:" and len(parts) >= 2:
                try:
                    spec.system_ram_gb = float(parts[1]) / 1024.0
                except ValueError:
                    pass
                break
    except Exception:
        pass

    # --- CPU cores (nproc) ---
    try:
        proc = _run(["nproc"], check=False)
        for line in proc.stdout.splitlines():
            if line.strip():
                try:
                    spec.cpu_cores = int(line.strip())
                except ValueError:
                    pass
                break
    except Exception:
        pass

    return spec
