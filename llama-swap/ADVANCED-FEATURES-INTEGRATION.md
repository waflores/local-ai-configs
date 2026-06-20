# llama-swap Advanced Features Guide

## Overview

This document describes advanced features and optimizations available for llama-swap. These features enhance performance, memory efficiency, and capabilities of the model serving infrastructure.

## 1. Flash Attention

### What It Does

Flash Attention uses approximate attention algorithms to reduce memory bandwidth usage, improving both speed and VRAM efficiency.

### Benefits

- **20-50% faster** inference on CUDA
- **15-30% less VRAM** usage
- Better scaling with larger batch sizes

### Configuration

Flash attention is automatically enabled in llama-server when using CUDA. The `flash-attn: auto` setting in `config.yaml` will enable it when available.

```yaml
# llama-swap/config.yaml
macros:
  flashAttn: auto  # Automatically enables flash attention on CUDA
```

### Verification

```bash
# Check if flash attention is available
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

## 2. Context Window Management

### What It Does

Manages context window sizes for different models to optimize memory usage and performance.

### Configuration

Context sizes are set per-model in the `config.yaml`:

```yaml
# llama-swap/config.yaml
models:
  Meta-Llama-3.1-8B-Instruct:
    macros:
      ctxSize: "262144"  # 256K context
```

### Benefits

- **Memory Efficiency**: Smaller context for simple tasks
- **Capability**: Larger context for complex reasoning
- **Performance**: Optimal context size for each use case

### Best Practices

| Use Case | Recommended Context |
|----------|---------------------|
| Code completion | 8192 - 32768 |
| General chat | 16384 - 65536 |
| Document analysis | 65536 - 262144 |

## 3. Model Swapping Strategy

### What It Does

llama-swap automatically swaps models between CUDA (active) and Vulkan (swapped) to maximize VRAM efficiency.

### Configuration

```yaml
# llama-swap/config.yaml
globalTTL: 0  # Keep models indefinitely
groups:
  swappable:
    exclusive: true  # Only one model from this group active
    swap: true
    members:
      - CodeLlama-7B-Instruct
      - Meta-Llama-3.1-8B-Instruct
      # ... other models
```

### Benefits

- **VRAM Efficiency**: Only one model loaded at a time
- **Multi-Model Support**: Keep many models available
- **Fast Swapping**: Models load in ~1-2 seconds

### Best Practices

1. **Active Models (CUDA)**: Keep 1-2 models for immediate use
1. **Swapped Models (Vulkan)**: Store 5-8 models for on-demand loading
1. **Large Models**: Use Vulkan for 14B+ parameter models
1. **Context Management**: Set appropriate `ctxSize` per model

## 4. Quantization Strategy

### What It Does

Uses quantized model versions (Q4_K_M, Q5_K_M, etc.) to reduce memory footprint while maintaining quality.

### Available Quantizations

| Quantization | Size Reduction | Quality Loss | Use Case |
|--------------|----------------|--------------|----------|
| Q4_K_M | ~50% | Minimal | General use |
| Q5_K_M | ~40% | Negligible | Quality-focused |
| Q8_0 | ~25% | None | Maximum quality |
| Q3_K_M | ~60% | Slight | VRAM-constrained |

### Configuration

```yaml
# llama-swap/config.yaml
models:
  Meta-Llama-3.1-8B-Instruct:
    # Path should point to quantized GGUF file
    path: "${models_directory}/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
```

## 5. Environment Variables

### What It Does

Environment variables provide additional configuration options without modifying config files.

### Common Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `LLAMA_SERVER_PORT` | Override default port | `10001` |
| `LLAMA_SERVER_HOST` | Bind address | `127.0.0.1` |
| `CUDA_VISIBLE_DEVICES` | GPU mapping | `0` |
| `GGML_VK_VISIBLE_DEVICES` | Vulkan GPU mapping | `0` |

### Example

```bash
# Set in environment or .env file
export LLAMA_SERVER_PORT=10001
export CUDA_VISIBLE_DEVICES=0
```

## Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Model Load Time | < 5s | < 10s |
| Model Swap Time | < 2s | < 5s |
| Generation Speed (7B) | > 10 t/s | > 5 t/s |
| VRAM Utilization | < 70% | < 90% |
| Context Efficiency | > 80% | > 50% |

## Troubleshooting

### Issue: CUDA Out of Memory

**Symptoms:** `CUDA out of memory` error

**Solutions:**

1. Enable model swapping (default behavior)
1. Reduce `ctxSize` for large models
1. Use Vulkan backend for large models (14B+)
1. Check model quantization level

### Issue: Model Not Swapping

**Symptoms:** Both models loaded simultaneously

**Solutions:**

1. Verify `groups.swappable.exclusive: true`
1. Check `globalTTL` is set appropriately
1. Ensure `performance.disabled: false`

### Issue: Slow Generation

**Symptoms:** < 5 tokens/sec

**Solutions:**

1. Enable flash attention (automatic on CUDA)
1. Reduce batch size
1. Use higher quantization (Q5_K_M)
1. Check GPU temperature

## Next Steps

1. **Review Config Structure** - See `config.yaml` for current settings
1. **Test Model Loading** - Use curl commands in AGENTS.md
1. **Monitor Performance** - Check `nvidia-smi` during operation
1. **Adjust Context Sizes** - Set appropriate `ctxSize` per model

## References

- [llama-swap Documentation](https://github.com/mostly-ai/llama-swap)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [Flash Attention Documentation](https://github.com/Dao-AILab/flash-attention)

______________________________________________________________________

**Last Updated:** 2026-06-13
**Status:** Active
