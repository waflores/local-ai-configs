# docs/

The documentation is organized by **progressive disclosure**: short entry points at the top,
deeper detail in sub-docs. Start here, then jump to the doc you actually need.

## First, decide what you need

| I want to… | Read first |
|------------|------------|
| Understand what this system does | [README.md](../README.md) |
| Use llama-swap from the CLI / curl | [llama-swap/README.md](../llama-swap/README.md) |
| Understand the Python app architecture | [docs/llm_manager.md](llm_manager.md) |
| Rebuild / format / test with Nix | [nix-formatting.md](nix-formatting.md) |
| Understand how the repo is organized | [monorepo.md](monorepo.md) |
| Tweak model parameters / context / VRAM | [inference-tuning.md](inference-tuning.md) |
| Know which files matter | [projdoc/index.md](projdoc/index.md) |

## Documentation set

| Doc | Purpose |
|-----|---------|
| [nix-formatting.md](nix-formatting.md) | treefmt-nix formatter infrastructure (`nix fmt`, Ruff rules) |
| [monorepo.md](monorepo.md) | Repository layout and phase plan |
| [inference-tuning.md](inference-tuning.md) | Hardware-aware context tuning, OOM prevention |
| [llama-swap.md](llama-swap.md) | llama-swap config, API, model inventory, performance |
| [llm_manager.md](llm_manager.md) | Python package: model discovery, hardware-aware configs, web UI |
| [projdoc/index.md](projdoc/index.md) | Project corpus index — file-map, domain map, reading order |

## Conventions

- Entry-point docs are short (2–5 min read). Deep-dive docs are modular.
- Every doc starts with a "Why this exists" and a "Where the code lives" section.
- Paths are relative to the repo root (`local-config/`).
