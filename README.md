# llama-swap Configuration

High-performance local LLM inference on an RTX 5070 Max-Q, using **llama-swap** to
load/unload GGUF models across two GPUs (CUDA0 active, Vulkan0 storage, Vulkan1 fallback).

- **Stack:** llama-swap, llama-server, llama-cpp-python, Nix (flake), uv
- **Hardware:** NVIDIA RTX 5070 Max-Q (8 GB VRAM) + Intel (ARL) (23 GB shared) + NVIDIA RTX 5070
- **Models:** 22 GGUF models discovered from `context-verification/*.json` + on-disk scanning

This repo is a **user-specific config** for a machine at `/home/waflores/`. Model
paths live in `llama-swap/config.yaml`; the Python package (`llm_manager/`) reads
them via env vars (`LLM_MANAGER_*`) with machine defaults. To adapt to another
machine, edit `llama-swap/config.yaml` and/or set the env vars below.

## How to use this repo as an AI agent

| Agent | Entry point | Docs to read |
|-------|-------------|--------------|
| **pi.dev** (https://pi.dev) | `AGENTS.md` + `SKILL.md` at repo root, or `pi.dev/SKILL.md` in any file | `AGENTS.md`, `SKILL.md`, `CLAUDE.md`, `docs/` |
| **Codex / OpenCode / Claude** | `AGENTS.md` + `CLAUDE.md` at repo root | `AGENTS.md`, `CLAUDE.md`, `docs/` |
| **Hermes Agent** (Nous Research) | `.hermes.md` (Hermes-only) + `.hermes/` skills | `.hermes.md`, `.hermes/skills/hermes-agent/SKILL.md`, `docs/` |

This repo is a **monorepo** of four subprojects. After the agent entry point,
read in this order:

1. `README.md` (root) — system overview, quick start, path adaptation
1. `docs/README.md` — documentation index
1. `docs/monorepo.md` — directory layout + phase plan
1. The subfolder you need:
   - `llama-swap/` — model config + benchmarks
   - `llm_manager/` — Python package (registry, hardware, profiles, web UI)
   - `nix/` — Nix flake + formatting
   - `context-verification/` — 22 model JSON metadata
   - `other_experiments/` — experimental, non-portable

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

### Env vars for path adaptation

| Variable | Default | Purpose |
|----------|---------|---------|
| `LLM_MANAGER_MODELS_DIR` | `/home/waflores/.lmstudio/models/lmstudio-community` | Where GGUF models live |
| `LLM_MANAGER_CONTEXT_DIR` | `context-verification/` | Model verification metadata |
| `LLM_MANAGER_CONFIG_YAML` | `llama-swap/config.yaml` | llama-swap model config |

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
├── other_experiments/        # Experimental: inferhost, llamastash. NOT portable.
└── billion-context/          # Removed from git.
```

## Agent-specific docs

- **Hermes-only:** `.hermes.md`, `.hermes/` (plans, skills)
- **Generic:** `AGENTS.md` + `CLAUDE.md` + `docs/`

## Detailed docs

For anything else, read the sub-docs in this order:

1. [llama-swap/README.md](llama-swap/README.md) — what llama-swap is, its API, 22-model inventory
1. [docs/README.md](docs/README.md) — overview of the documentation set and where to look
1. [docs/nix-formatting.md](docs/nix-formatting.md) — the Nix formatter infrastructure
1. [docs/monorepo.md](docs/monorepo.md) — how the repo is organized (and why)
1. [llm_manager/](docs/llm_manager.md) — the Python package: architecture, discovery, profiling
