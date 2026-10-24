# llama-swap Configuration

High-performance local LLM inference on an RTX 5070 Max-Q, using **llama-swap** to
load/unload GGUF models across two GPUs (CUDA0 active, Vulkan0 storage, Vulkan1 fallback).

- **Stack:** llama-swap, llama-server, llama-cpp-python, Nix (flake), uv
- **Hardware:** NVIDIA RTX 5070 Max-Q (8 GB VRAM) + Intel (ARL) (23 GB shared) + NVIDIA RTX 5070
- **Models:** 22 GGUF models discovered from `context-verification/*.json` + on-disk scanning

The repo mirror: `llama-swap` (model config + benchmarks) and `llm_manager` (Python Flask app
with model registry, hardware-aware config generation, and a web UI). `nix/` wraps it all into
a reproducible package on x86_64-linux only.

______________________________________________________________________

## Quick start

```bash
# 1. Enter the dev shell (includes uv + the Python package built by Nix)
nix develop .#default

# 2. Start llama-swap (listens on 127.0.0.1:10001)
/home/waflores/bin/llama-swap \
  --config llama-swap/config.yaml \
  --listen 127.0.0.1:10001

# 3. Health check
curl http://127.0.0.1:10001/health

# 4. Start the web app (Flask, port 5000)
uv run python -m llm_manager.webapp
# Open http://127.0.0.1:5000/
```

## Performance targets

| Metric | Target |
|--------|--------|
| Model swap time | < 2s |
| Generation speed (7B) | > 10 t/s |
| VRAM utilization | < 70% |
| Context efficiency | > 80% |

## Layout at a glance

```
local-config/
├── llama-swap/               # Model config (config.yaml: 22 models) + benchmarks
├── llm_manager/              # Flask package: registry, hardware, profiles, web UI
├── nix/                      # treefmt-nix formatter infra + blueprint flake
├── context-verification/     # 22 JSON verification metadata files (source of truth)
├── .agents/                  # Agent intent layer (config.json, README.md, agents/)
├── docs/                     # Layered documentation
├── flake.nix / pyproject.toml  # Build definitions
```

Detailed docs are below. This file intentionally stays short — for anything else, read the
sub-docs in this order:

1. [llama-swap/README.md](llama-swap/README.md) — what llama-swap is, its API, 22-model inventory
1. [docs/README.md](docs/README.md) — overview of the documentation set and where to look
1. [docs/nix-formatting.md](docs/nix-formatting.md) — the Nix formatter infrastructure
1. [docs/monorepo.md](docs/monorepo.md) — how the repo is organized (and why)
1. [llm_manager/](docs/llm_manager.md) — the Python package: architecture, discovery, profiling
