# local-config

A monorepo of local LLM tooling: model management (`llama-swap`), a Flask/FastAPI
model registry (`llm_manager`), a Nix build + formatting flake (`nix`), and a
22-model metadata registry (`context-verification`). Also contains experimental
subfolders (`other_experiments/`) and a removed project (`billion-context/` — see
note below).

## How to read this repo as an AI agent

1. **Start here:** this file.
1. **Then:** `README.md` — system overview + quick start.
1. **Then:** `docs/README.md` — documentation index (7 files, progressive disclosure).
1. **Then:** the subfolder you care about (`llama-swap/`, `llm_manager/`, `nix/`,
   `context-verification/`, or `other_experiments/`).

## Repo layout

| Path | What it is |
|------|-----------|
| `llama-swap/` | Model config (22 models), benchmarks, parameter optimizer |
| `llm_manager/` | Python package: model registry, hardware-aware profiles, Flask web UI + FastAPI docs |
| `nix/` | treefmt-nix + blueprint flake (x86_64-linux only) |
| `context-verification/` | 22 model JSON metadata (source of truth for the model registry) |
| `other_experiments/` | Experimental: inferhost, llamastash. **Hardcoded absolute paths. Not portable.** |
| `billion-context/` | **Removed from git.** See note below. |

> **Note on `billion-context/`:** This directory was removed from the repo and is
> not tracked by git. Do not reference it in docs or config. If you still see it
> mounted, treat it as transient.

## Build / dev / check (x86_64-linux only)

```bash
nix flake show        # show outputs
nix flake check       # CI gate
nix fmt               # format (treefmt-nix: ruff, nixfmt, yamlfmt, etc.)
nix build .#packages.x86_64-linux.local-config   # build Python package
nix develop .#default # enter dev shell
```

## Python (inside nix develop or your own venv)

```bash
uv run python -m llm_manager.webapp      # Flask UI on 127.0.0.1:5000
uv run uvicorn llm_manager.api_docs:app --port 5001  # FastAPI docs on 5001
uv run pytest
uv run ruff check
uv run ruff format --check
```

## Key files

- `llama-swap/config.yaml` — model registry (22 models)
- `context-verification/*.json` — per-model verification metadata
- `llm_manager/loader.py` — model discovery pipeline (JSON metadata + config.yaml + on-disk scan)
- `llm_manager/configurator.py` — hardware-aware profile generation
- `flake.nix` + `nix/` — Nix packaging and formatting

## Hardpaths note

This repo is a **user-specific config** for a machine at `/home/waflores/`. The
model paths live in `llama-swap/config.yaml`; the Python package reads them via
env vars (`LLM_MANAGER_*`) with machine defaults. To adapt to another machine,
edit `llama-swap/config.yaml` and/or set `LLM_MANAGER_MODELS_DIR` etc.

## Agent-specific docs

- **Hermes-only:** `.hermes.md`, `.hermes/` (plans, skills)
- **Generic:** this file + `CLAUDE.md` + `docs/`
