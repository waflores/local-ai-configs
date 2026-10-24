# monorepo.md

How the repository is organized and why.

## Why this exists

The project grew organically; this doc is the source of truth for the current layout, the
phase plan, and the rules for adding new code.

## Directory map

```
local-config/
├── llama-swap/               # Core: model config + benchmark scripts
├── llm_manager/              # Core: Python Flask package (registry + web UI + tests)
├── context-verification/     # JSON metadata: source of truth for 22 model defs
├── nix/                      # treefmt-nix module + bridge + blueprint wiring
├── .agents/                  # Agent intent layer (config.json, README, agents/)
├── docs/                     # Documentation (this folder)
├── other_experiments/        # Experimental: NOT part of the core stack
├── flake.nix / pyproject.toml  # Build definitions
```

## Rules

- **Core stack** (llama-swap, llm_manager, nix) gets first-class docs and review.
- **`other_experiments/`** is experimental and not portable (hardcoded absolute paths).
  Treat it as throwaway; do not rely on it in docs or CI.
- **`context-verification/`** is data, not code. The 22 JSON files are the model registry
  source of truth — the Python app reads it at runtime.
- **No top-level Python files.** Everything Python lives in `llm_manager/` (or its own
  subdirectory in `other_experiments/`).
- **Tests stay with the package:** `llm_manager/tests/`.

## Phase plan

| Phase | State | Content |
|-------|-------|---------|
| 1 Foundation | Complete | Basic config, docs, simplified Nix flake |
| 2 Directory & admin portal | Complete | Flask `/admin`, `/dirs`, directory picker |
| 3 Completion | Complete | Tuning page, DB persistence, disk crawling, configs page |

(Phases 4+ are planned but not yet in the tree.)
