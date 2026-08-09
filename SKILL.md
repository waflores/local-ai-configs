# llama-swap Agent Skills

## Overview

This project uses **llama-swap** as the primary interface for all AI agent interactions. The system provides a high-performance model swapping infrastructure that leverages your NVIDIA RTX 5070 Max-Q GPU for optimal inference performance.

## Core Capabilities

### Model Management

- **Model Loading/Unloading** - Swap between models on-demand
- **Performance Benchmarking** - Measure inference speed and latency
- **Resource Monitoring** - Track VRAM, RAM, and swap usage
- **Health Checking** - Verify model availability and readiness

### Inference Operations

- **Chat Completion** - Interactive conversations
- **Code Generation** - Python, C, C++ code completion
- **Reasoning Tasks** - Complex problem solving
- **Context Management** - Handle long-context tasks efficiently

## Available Commands

### `/models` - List Available Models

```bash
curl http://127.0.0.1:10001/v1/models
```

**Response:**

```json
{
  "object": "list",
  "data": [
    {
      "id": "CodeLlama-7B-Instruct",
      "object": "model",
      "created": 1718668800,
      "owned_by": "llama-swap"
    }
  ]
}
```

### `/load <model-name>` - Load a Specific Model

```bash
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Meta-Llama-3.1-8B-Instruct",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "ttl": 600
  }'
```

### `/unload <model-name>` - Unload a Model

```bash
curl -X DELETE http://127.0.0.1:10001/v1/models/Meta-Llama-3.1-8B-Instruct
```

### `/health` - Check System Health

```bash
curl http://127.0.0.1:10001/health
```

**Response:**

```json
{
  "status": "ok",
  "models": [
    {
      "id": "CodeLlama-7B-Instruct",
      "status": "loaded"
    }
  ]
}
```

### `/inference` - Run Inference Request

```bash
curl -X POST http://127.0.0.1:10001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "CodeLlama-7B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": "Write a Python function to sort an array"
      }
    ],
    "max_tokens": 100
  }'
```

### `/benchmark <model-name>` - Run Performance Benchmark

```bash
/home/waflores/DevFolder/ai/local-config/llama-swap/run_benchmarks.py \
  --model CodeLlama-7B-Instruct \
  --output benchmarks/results.json
```

### `/config-analyze` - Analyze Configuration

```bash
/home/waflores/DevFolder/ai/local-config/llama-swap/config-analyzer.sh
```

## Model Inventory

| Model | Parameters | Size (Q4_K_M) | Use Case |
|-------|------------|---------------|----------|
| CodeLlama-7B-Instruct | 7B | ~4 GB | Python, general coding |
| Meta-Llama-3.1-8B-Instruct | 8B | ~5 GB | General tasks |
| Qwen3.5-9B-GGUF | 9B | ~5.6 GB | General tasks |
| Qwen3.6-27B-GGUF | 27B | ~16.5 GB | Advanced tasks |
| DeepSeek-R1-0528-Qwen3-8B-GGUF | 8B | ~5 GB | Reasoning |
| Ministral-3-3B-Instruct-2512-GGUF | 3B | ~2 GB | Fast completions |
| Ministral-3-14B-Reasoning-2512-GGUF | 14B | ~8 GB | Reasoning tasks |
| Mistral-Nemo-Instruct-2407-GGUF | 13B | ~6.5 GB | Balanced performance |
| Phi-4-mini-reasoning-GGUF | 3B | ~2.5 GB | Lightweight tasks |
| Phi-4-reasoning-plus-GGUF | 13B | ~9 GB | Advanced reasoning |
| gemma-4-E4B-it-GGUF | 8B | ~5.3 GB | General tasks |
| NVIDIA-Nemotron-3-Nano-4B-GGUF | 4B | ~2.8 GB | NVIDIA-optimized |
| Devstral-Small-2-24B-Instruct-2512-GGUF | 24B | ~14 GB | Advanced reasoning |
| LFM2-24B-A2B-GGUF | 24B | ~14.4 GB | Embeddings |
| Qwen3-VL-8B-Instruct-GGUF | 8B | ~5 GB | Vision-language |
| olmOCR-2-7B-1025-GGUF | 8B | ~4.7 GB | OCR tasks |
| granite-4-h-tiny | 7B | ~4 GB | IBM's code model |
| zerank-1-small-gguf | - | - | Reranking |
| zerank-2-gguf | - | - | Embeddings |
| rnj-1-instruct-GGUF | - | - | General tasks |

## Hardware Configuration

### GPU Devices

| Device | Type | Memory | Status |
|--------|------|--------|--------|
| CUDA0 | NVIDIA RTX 5070 | 7.7 GB | Active inference |
| Vulkan0 | Intel (ARL) | 23.6 GB | Model storage |
| Vulkan1 | NVIDIA RTX 5070 | 8.1 GB | Fallback |

### Performance Targets

| Metric | Target |
|--------|--------|
| Model Load Time | < 5s |
| Model Unload Time | < 2s |
| Swap Operation | < 2s |
| Inference Speed (7B) | > 10 t/s |
| VRAM Utilization | < 70% |

## Configuration Files

- **`llama-swap/config.yaml`** - Main configuration with model definitions
- **`SKILL.md`** - This file - Agent commands and capabilities
- **`README.md`** - Project vision and documentation
- **`AGENTS.md`** - Testing agent responsibilities

## Quick Reference

### Start llama-swap

```bash
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001
```

### Check Health

```bash
curl http://127.0.0.1:10001/health
```

### List Models

```bash
curl http://127.0.0.1:10001/v1/models
```

### Access Benchmarks

```bash
/home/waflores/DevFolder/ai/local-config/llama-swap/run_benchmarks.py
```

## Best Practices

1. **Use Q4_K_M or Q5_K_M quantization** - Balance between quality and size
1. **Prefer CUDA for active models** - Better performance on RTX 5070
1. **Use Vulkan for swapped models** - Free up VRAM for active models
1. **Monitor VRAM usage** - Keep below 70% for optimal performance
1. **Set appropriate context sizes** - Match task requirements
1. **Enable flash-attn** - Improves inference speed

## Troubleshooting

### Model Load Timeout

```bash
# Increase health check timeout
healthCheckTimeout: 60
```

### VRAM Overflow

```bash
# Reduce context size or enable swapping
macros.ctxSize: '131072'
groups.swappable.exclusive: true
```

### Performance Issues

```bash
# Verify CUDA is accessible
nvidia-smi

# Check available VRAM
cat /proc/driver/nvidia/gpu/0/vram_total
```

______________________________________________________________________

**Last Updated:** 2026-06-20
**Status:** Production-ready
**Version:** 1.0
