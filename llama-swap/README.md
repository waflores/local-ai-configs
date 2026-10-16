# llama-swap

## Purpose

llama-swap is a model management tool that allows you to load and unload large language models (LLMs) dynamically. It uses `llama-server` for inference and supports multiple GPU backends (CUDA, Vulkan).

## Core Stack

- **llama-server**: Inference engine
- **llama-swap**: Model management and swapping tool

## Authority

This project uses the `.agents` folder to define AI agent behavior. Agents should consult `.agents/agents/` for project-specific instructions.

## 📦 Model Inventory

### Model Location

Models are stored at `/home/waflores/.lmstudio/models`.

**Total Models:** 22 models across various architectures

### Model Discovery

Models are discovered via two complementary mechanisms:

1. **Static verification metadata** (`context-verification/*.json`) — 22 non-mmproj JSON files provide model metadata (name, size, context, quantization tags).
1. **On-disk discovery** (`loader.discover_models_on_disk()`) — the LLM manager walks the models directory (`/home/waflores/.lmstudio/models`) for live `.gguf` files, computing sizes dynamically.

The `discover_models()` function combines both sources: JSON metadata provides the registry, and on-disk discovery provides live file paths. Each model's path is resolved via:

1. **config.yaml path override** (if the model is listed in `llama-swap/config.yaml` with a `model_path`)
1. **Directory mapping** (`model_directory_mapping()`) — case-insensitive lookup of model directory → canonical path
1. **Directory scanning** (`_finalize_residual_paths()`) — walks the full models tree to find matching GGUF files, handling quantized filenames (e.g., `Q4_K_M`, `Q3_K_L`, `Q8_0`)

### Full Model Inventory

| Model | Parameters | Size (Q4_K_M / Q8_0) | Use Case |
|-------|------------|---------------------|----------|
| Codellama-7B-Instruct | 7B | ~4 GB | Python, general coding |
| DeepSeek-R1-0528-Qwen3-8B | 8B | ~5 GB | Reasoning |
| Devstral-Small-2-24B-Instruct-2512 | 24B | ~14 GB | Advanced reasoning |
| Gemma-4-E4B-it | 8B | ~5.3 GB | General tasks |
| Granite-4.0-h-tiny | 7B | ~4 GB | IBM's code model |
| LFM2-24B-A2B | 24B | ~14.4 GB | Embeddings |
| Meta-Llama-3.1-8B-Instruct | 8B | ~5 GB | General tasks |
| Ministral-3-14B-Reasoning-2512 | 14B | ~8 GB | Reasoning tasks |
| Ministral-3-3B-Instruct-2512 | 3B | ~2 GB | Fast completions |
| Mistral-Nemo-Instruct-2407 | 13B | ~6.5 GB | Balanced performance |
| NVIDIA-Nemotron-3-Nano-4B | 4B | ~2.8 GB | NVIDIA-optimized |
| olmOCR-2-7B-1025 | 8B | ~4.7 GB | OCR tasks |
| Phi-4-mini-reasoning | 3B | ~2.5 GB | Lightweight tasks |
| Phi-4-reasoning-plus | 13B | ~9 GB | Advanced reasoning |
| Qwen3-4B-Thinking-2507 | 4B | ~4 GB | Thinking/reasoning |
| Qwen3.5-9B | 9B | ~5.6 GB | General tasks |
| Qwen3.6-27B | 27B | ~16.5 GB | Advanced tasks |
| Qwen3-VL-8B-Instruct | 8B | ~5 GB | Vision-language |
| rnj-1-instruct | - | - | General tasks |
| zerank-1-small | - | - | Reranking |
| zerank-2 | - | - | Embeddings |
| llama2:latest | 7B | ~3.6 GB | Base model reference (no disk path) |

*Note: `llama2:latest` is a base-model reference from verification metadata with no installed `.gguf` file, so it has no resolved disk path.*

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

## Unsloth Resources

https://unsloth.ai/docs/models/qwen3.5
https://unsloth.ai/docs/integrations/hermes-agent
https://unsloth.ai/docs/models/tutorials/llama-4-how-to-run-and-fine-tune
https://unsloth.ai/docs/basics/dynamic-3.0-ggufs
https://unsloth.ai/docs/models/qwen3.8

## Example Benchmark

https://github.com/ggml-org/llama.cpp/discussions/15013
