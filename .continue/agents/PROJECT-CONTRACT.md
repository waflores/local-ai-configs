# PROJECT-CONTRACT

## Purpose

This project orchestrates local LLM inference using `llama-swap` and `continue.dev`.

## Core Stack

- `continue.dev`: IDE agent for AI-assisted development.
- `llama-swap`: Model orchestration layer for `llama-server`.

## Other Experiments

- `context-verification`: Security-focused context verification.
- `nix`: Nix-based build system.
- `llamastash`: Rust-based model proxy (experimental).

## Machine-Readable Authority Block

```yaml
authority:
  folder: ".continue"
  priority: "high"
  instructions:
    - "Consult .continue/agents/ for project-specific AI agent instructions."
    - "Consult .continue/config.json for project-specific configuration."
    - "Consult .continue/prompts/ for project-specific prompts."
```

## Critical Rules

- `ctxSize` must match model capacity (no OOM).
- `llama-swap` uses `CUDA` for active models, `Vulkan` for swapped models.
- `continue.dev` expects models at `/home/waflores/DevFolder/ai/local-config/inferhost/models`.

## Common Issues

- **Syntax Error:** Check for trailing quotes in `llama-swap/config.yaml`.
- **OOM Error:** Reduce `ctxSize` for large models.
- **Model Not Found:** Ensure the model path is correct in `llama-swap/config.yaml`.

## Hello World Path

1. Start `llama-swap` with `./inferhost/bin/llama-swap --config /home/waflores/DevFolder/ai/local-config/inferhost/config.yaml`
1. Install `continue.dev` and use `cn` to chat with models.
