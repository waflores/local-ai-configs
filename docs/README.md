# docs/

The documentation is organized by **progressive disclosure**: short entry points at the top,
deeper detail in sub-docs. Start here, then jump to the doc you actually need.

## Reading order for agents

This repo is a monorepo of four subprojects. Read in this order:

1. `README.md` (root) — system overview, quick start, hardpaths note
1. `docs/README.md` — this file (documentation index)
1. `docs/monorepo.md` — directory layout + phase plan
1. The subfolder you need:
   - `llama-swap/` — model config + benchmarks
   - `llm_manager/` — Python package: architecture, web UI, tests
   - `nix/` — Nix flake + formatting
   - `context-verification/` — 22 model JSON metadata
   - `other_experiments/` — experimental, non-portable (hardcoded paths)

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
