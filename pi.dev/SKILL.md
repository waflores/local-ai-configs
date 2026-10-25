# pi.dev Agent Skills

This is the pi.dev skill entry for the local-config repo.

## How pi.dev reads this repo

pi.dev (https://pi.dev) is a remote agent harness that reads `AGENTS.md` and `SKILL.md`
from the repo root, or `pi.dev/SKILL.md` for a dedicated skill entry point. On this
repo, pi.dev is configured to:

1. Read `AGENTS.md` — the platform-neutral entry point (generic, no agent branding)
1. Read `SKILL.md` — the generic entry point (with "for Hermes Agent only" label)

## Quick reference

- **Repo root:** `AGENTS.md` + `SKILL.md`
- **pi.dev skill entry:** `pi.dev/SKILL.md` (this file)
- **Docs index:** `docs/README.md` → `docs/monorepo.md` → the subfolder you need

## Stack

- **llama-swap** — model management + swapping (API on 127.0.0.1:10001)
- **llm_manager** — Flask UI (127.0.0.1:5000) + FastAPI docs (5001)
- **Nix** — build + formatting flake (x86_64-linux only)
- **uv** — Python package management + dev shell

## Build / dev / check

```bash
nix flake show        # show outputs
nix flake check       # CI gate
nix fmt               # format (treefmt-nix: ruff, nixfmt, yamlfmt, etc.)
nix develop .#default # enter dev shell
```

## Key files

- `llama-swap/config.yaml` — model registry (6 models)
- `context-verification/*.json` — per-model verification metadata
- `llm_manager/loader.py` — model discovery pipeline
- `llm_manager/configurator.py` — hardware-aware profile generation
- `flake.nix` + `nix/` — Nix packaging and formatting

## Agent-specific docs

- **Hermes-only:** `.hermes.md`, `.hermes/` (plans, skills)

## Related

- `AGENTS.md` — generic platform-neutral entry point
- `CLAUDE.md` — Claude Code mirror (same content)
- `docs/` — documentation index
