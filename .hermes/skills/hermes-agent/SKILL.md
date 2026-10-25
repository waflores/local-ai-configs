# Hermes Agent skill

This is the Hermes Agent skill entry for the local-config repo.

## Quick reference

- `hermes doctor` — health check
- `nix flake show` / `nix flake check` / `nix fmt` — build & format (x86_64-linux)
- `nix develop .#default` — dev shell
- `uv run python -m llm_manager.webapp` — Flask UI (127.0.0.1:5000)
- `uv run uvicorn llm_manager.api_docs:app --port 5001` — FastAPI docs (5001)
- `curl http://127.0.0.1:10001/health` — llama-swap health

## Generic agent docs

- `AGENTS.md` — generic, platform-neutral entry point
- `CLAUDE.md` — Claude Code mirror
- `docs/README.md` — documentation index

## Related

- `.hermes/` — Hermes memory, plans, skills (Hermes-only)
