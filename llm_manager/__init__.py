"""llm_manager - A web app for managing downloaded LLMs and generating hardware-aware configurations.

Provides:
  - Model registry (discovered from JSON verification files + llama-swap config)
  - Hardware detection (CUDA VRAM, RAM, CPU)
  - Hardware-aware config generation (quantization + context capping)
  - A Flask UI to inspect models, hardware, and generated configurations
"""
