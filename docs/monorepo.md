# monorepo.md

How the repository is organized and why.

## Why this exists

This project grew organically; this file documents the current layout and the rules
for adding new code.

## Directory map

```
local-config/
├── llama-swap/               # Model config + benchmark scripts
├── llm_manager/              # Python package: registry, hardware, profiles, web UI
├── context-verification/     # 22 model JSON metadata files (source of truth)
├── nix/                      # treefmt-nix + blueprint flake (x86_64-linux only)
├── .agents/                  # Agent intent layer (config.json, README, agents/)
├── docs/                     # Documentation (progressive disclosure)
├── other_experiments/        # Experimental: inferhost, llamastash. NOT portable.
├── flake.nix / pyproject.toml  # Build definitions
├── pi.dev/                   # pi.dev-specific skill entry point
```

## Rules

- **Core stack** (llama-swap, llm_manager, nix, context-verification, .agents, docs) gets
  first-class docs and review.
- **`other_experiments/`** is experimental and not portable (hardcoded absolute paths).
  Treat it as throwaway; do not rely on it in docs or CI.
- **`context-verification/`** is data, not code. The 22 JSON files are the model registry
  source of truth — the Python app reads them at runtime.
- **No top-level Python files.** Everything Python lives in `llm_manager/` (or its own
  subdirectory in `other_experiments/`).
- **Tests stay with the package:** `llm_manager/tests/`.
- **Build system:** Nix flake (x86_64-linux only) + uv for Python packaging.
