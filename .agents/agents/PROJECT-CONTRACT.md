# PROJECT-CONTRACT

## Purpose

This project orchestrates local LLM inference using `llama-swap` and `llama-server`.

## Core Stack

- `llama-server`: Inference engine
- `llama-swap`: Model orchestration layer
- `nix`: Dependency and build system

## Other Experiments

- `context-verification`: Security-focused context verification.
- `nix`: Nix-based build system.

## Machine-Readable Authority Block

```yaml
authority:
  folder: ".agents"
  priority: "high"
  instructions:
    - "Consult .agents/agents/ for project-specific AI agent instructions."
    - "Consult .agents/config.json for project-specific configuration."
    - "Consult .agents/prompts/ for project-specific prompts."
```

## Critical Rules

- `ctxSize` must match model capacity (no OOM).
- `llama-swap` uses `CUDA` for active models, `Vulkan` for swapped models.
- `llama-server` expects models at `/home/waflores/.lmstudio/models`.

## Common Issues

- **Syntax Error:** Check for trailing quotes in `llama-swap/config.yaml`.
- **OOM Error:** Reduce `ctxSize` for large models.
- **Model Not Found:** Ensure the model path is correct in `llama-swap/config.yaml`.

## Hello World Path

1. Start `llama-swap` with `/home/waflores/bin/llama-swap -config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml -watch-config`
1. Install `continue.dev` and use `cn` to chat with models.
