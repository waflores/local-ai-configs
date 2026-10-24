# llama-swap

## Purpose

llama-swap is a model management tool that allows you to load and unload large language models (LLMs) dynamically. It uses `llama-server` for inference and supports multiple GPU backends (CUDA, Vulkan).

## Core Stack

- **llama-server**: Inference engine
- **llama-swap**: Model management and swapping tool

## Authority

This project uses the `.agents` folder to define AI agent behavior. Agents should consult `.agents/agents/` for project-specific instructions.

## Model inventory

22 models are defined in `llama-swap/config.yaml` and verified by `context-verification/*.json`.

### Model discovery

Models are discovered via two complementary mechanisms:

1. **Static verification metadata** (`context-verification/*.json`) — JSON files provide model metadata (name, size, context, quantization tags).
1. **On-disk discovery** (`loader.discover_models_on_disk()`) — the LLM manager walks the models directory (`/home/waflores/.lmstudio/models`) for live `.gguf` files, computing sizes dynamically.

The `discover_models()` function combines both sources: JSON metadata provides the registry, and on-disk discovery provides live file paths. Each model's path is resolved via:

1. **config.yaml path override** (if the model is listed in `llama-swap/config.yaml` with a `model_path`)
1. **Directory mapping** (`model_directory_mapping()`) — case-insensitive lookup of model directory → canonical path
1. **Directory scanning** (`_finalize_residual_paths()`) — walks the full models tree to find matching GGUF files, handling quantized filenames (e.g., `Q4_K_M`, `Q3_K_L`, `Q8_0`)

See `docs/llama-swap.md` for the full model inventory table.

## Getting Started

### 1. Start llama-swap

```bash
/home/waflores/bin/llama-swap \
  --config llama-swap/config.yaml \
  --listen 127.0.0.1:10001
```

### 2. Verify Health

```bash
curl http://127.0.0.1:10001/health
```

### 3. List Available Models

```bash
curl http://127.0.0.1:10001/v1/models
```

### 4. Load a Model

```bash
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Meta-Llama-3.1-8B-Instruct",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "ttl": 600
  }'
```

### 5. Test Inference

```bash
curl -X POST http://127.0.0.1:10001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Meta-Llama-3.1-8B-Instruct",
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "max_tokens": 100
  }'
```

## Configuration

See `config.yaml` for model configurations. Key settings:

- **groups.swappable**: Models that can be swapped between CUDA and Vulkan
- **macros**: Global settings (flash-attn, ctxSize, threads, etc.)
- **models**: Per-model configurations with custom paths and settings

## Advanced Features

See `docs/inference-tuning.md` for context/tuning guidance. Also see `llama-swap/CONFIG-TUNING-GUIDE.md` and `llama-swap/ADVANCED-FEATURES-INTEGRATION.md`.

______________________________________________________________________

**Last Updated:** 2026-06-13
**Status:** Active

## Unsloth Resources

https://unsloth.ai/docs/models/qwen3.5
https://unsloth.ai/docs/integrations/hermes-agent
https://unsloth.ai/docs/models/tutorials/llama-4-how-to-run-and-fine-tune
https://unsloth.ai/docs/basics/dynamic-3.0-ggufs
https://unsloth.ai/docs/models/qwen3.8

## Example Benchmark

https://github.com/ggml-org/llama.cpp/discussions/15013
