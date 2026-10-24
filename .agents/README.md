# .agents

## Purpose

The `.agents` folder is the **intent layer** for this LLM manager and llama-swap configuration project. It contains AI agent definitions and project-specific configuration instructions for AI coding assistants.

## Structure

- `agents/`: AI agent definitions and instructions for configuration tasks
- `config.json`: Machine-readable project authority and configuration
- `README.md`: This file

## Authority

AI agents should consult this folder for project-specific configuration instructions.

## Documentation layer

Progressive-disclosure documentation lives in `docs/`. Start with:

1. [README.md](../README.md) — the system overview
1. [docs/README.md](./README.md) — the documentation index
1. [README.md](../llama-swap/README.md) — model registry + API
1. [docs/llm_manager.md](../docs/llm_manager.md) — Python app architecture
1. [docs/monorepo.md](../docs/monorepo.md) — directory structure + phase plan
1. [docs/inference-tuning.md](../docs/inference-tuning.md) — performance math

## Getting Started

1. Consult `.agents/agents/PROJECT-CONTRACT.md` for project overview and critical rules
1. Consult `.agents/config.json` for project-specific configuration.
1. Consult `.agents/README.md` for intent layer documentation
