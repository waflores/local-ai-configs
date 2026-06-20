# llama-swap

## Purpose

llama-swap is a model management tool that allows you to load and unload large language models (LLMs) dynamically. It uses `llama-server` for inference and supports multiple GPU backends (CUDA, Vulkan).

## Core Stack

- **llama-server**: Inference engine
- **llama-swap**: Model management and swapping tool

## Authority

This project uses the `.continue` folder to define AI agent behavior. Agents should consult `.continue/agents/` for project-specific instructions.

## Model Location

Models are stored at `/home/waflores/.lmstudio/models`.

See Root README.md for complete model inventory.

## Hardware

- **GPU**: NVIDIA GeForce RTX 5070 Max-Q (~8 GB VRAM)
- **Secondary GPU**: Intel Integrated Graphics (~23 GB shared)
- **RAM**: ~33 GB total (~20 GB currently used)

## Getting Started

### 1. Start llama-swap

```bash
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001 \
  --watch-config
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
    "messages": [
      {
        "role": "user",
        "content": "What is 2+2?"
      }
    ],
    "max_tokens": 100
  }'
```

## Configuration

See `config.yaml` for model configurations. Key settings:

- **groups.swappable**: Models that can be swapped between CUDA and Vulkan
- **macros**: Global settings (flash-attn, ctxSize, threads, etc.)
- **models**: Per-model configurations with custom paths and settings

## Advanced Features

See `ADVANCED-FEATURES-INTEGRATION.md` for:

- Flash Attention configuration
- Context window management
- Model swapping strategy
- Quantization options
- Environment variables

## Testing

See `AGENTS.md` for:

- Health check commands
- Model loading tests
- Swap operation tests
- Inference tests
- Common issues and solutions

## Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Model Load Time | < 5s | < 10s |
| Model Swap Time | < 2s | < 5s |
| Generation Speed (7B) | > 10 t/s | > 5 t/s |
| VRAM Utilization | < 70% | < 90% |

## Troubleshooting

### CUDA Out of Memory

- Enable model swapping (default behavior)
- Reduce `ctxSize` for large models
- Use Vulkan backend for 14B+ models

### Model Not Swapping

- Verify `groups.swappable.exclusive: true`
- Check `globalTTL` is set appropriately
- Ensure `performance.disabled: false`

### Slow Generation

- Flash attention is automatic on CUDA
- Reduce batch size if needed
- Use higher quantization (Q5_K_M)

## References

- [llama-swap Documentation](https://github.com/mostly-ai/llama-swap)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)

______________________________________________________________________

**Last Updated:** 2026-06-13
**Status:** Active
