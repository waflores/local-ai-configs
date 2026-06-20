# llama-swap Configuration Agent

## Purpose

This agent handles configuration, testing, and validation of llama-swap. It provides structured workflows for model management, performance benchmarking, and system health monitoring.

## Responsibilities

- Run model load/unload tests
- Validate VRAM usage and constraints
- Test context window handling
- Verify model swapping behavior
- Collect performance metrics
- Document test results
- Manage system health and availability
- Provide configuration recommendations

## Quick Reference

### Start llama-swap

```bash
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001
```

### Verify Health

```bash
curl http://127.0.0.1:10001/health
```

### List Models

```bash
curl http://127.0.0.1:10001/v1/models
```

### Load Model

```bash
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Meta-Llama-3.1-8B-Instruct",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "ttl": 600
  }'
```

### Run Inference

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

### Run Benchmarks

```bash
/home/waflores/DevFolder/ai/local-config/llama-swap/run_benchmarks.py \
  --model CodeLlama-7B-Instruct \
  --output benchmarks/results.json
```

## Test Cases

### Model Load Test

```yaml
test_name: "model_load"
model: "Meta-Llama-3.1-8B-Instruct"
expected_vram_mb: 5120
expected_load_time_seconds: 5
```

### Model Unload Test

```yaml
test_name: "model_unload"
model: "Meta-Llama-3.1-8B-Instruct"
expected_free_vram_mb: 7500
```

### Model Swap Test

```yaml
test_name: "model_swap"
models:
  - "Meta-Llama-3.1-8B-Instruct"
  - "CodeLlama-7B-Instruct"
expected_concurrent_models: 1
```

### Inference Latency Test

```yaml
test_name: "inference_latency"
model: "Meta-Llama-3.1-8B-Instruct"
prompt: "Count from 1 to 10"
expected_tokens_per_second: 10
```

### Context Window Test

```yaml
test_name: "context_window"
model: "Meta-Llama-3.1-8B-Instruct"
context_size: 262144
expected_max_tokens: 8192
```

## Result Logging Format

```markdown
## Test Results: [Date]

### Configuration
- Config File: `llama-swap/config.yaml`
- Backend: CUDA0

### Tests Run

#### Model Load
- **Model:** Meta-Llama-3.1-8B-Instruct
- **Status:** ✅ PASS / ❌ FAIL
- **Load Time:** X.XXs (expected: < 5s)
- **VRAM Used:** X.XX GB (expected: < 5.12 GB)
- **Errors:** None / [List errors]

#### Model Swap
- **Status:** ✅ PASS / ❌ FAIL
- **Concurrent Models:** X (expected: 1)
- **VRAM After Swap:** X.XX GB
- **Errors:** None / [List errors]

#### Inference
- **Status:** ✅ PASS / ❌ FAIL
- **Tokens/sec:** X.XX (expected: > 10)
- **Latency:** X.XXs
- **Errors:** None / [List errors]

### Summary
- **Total Tests:** X
- **Passed:** X
- **Failed:** X
- **Notes:** [Any observations]
```

## Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Model Load Time | < 5s | < 10s |
| Model Unload Time | < 2s | < 5s |
| Swap Operation | < 2s | < 5s |
| Inference Speed | > 10 t/s | > 5 t/s |
| VRAM Utilization | < 70% | < 90% |
| Context Retention | 100% | > 95% |

## Common Issues

### Issue: Model Load Timeout

**Symptoms:** Model takes > 10s to load

**Solutions:**

1. Check model file integrity
1. Verify CUDA device is accessible
1. Reduce quantization (Q4_K_M → Q3_K_M)
1. Increase `healthCheckTimeout` in config

### Issue: VRAM Overflow

**Symptoms:** CUDA out of memory errors

**Solutions:**

1. Reduce model context size
1. Enable model swapping
1. Use Vulkan backend for swapped models
1. Check `macros.ctxSize` value

### Issue: Model Not Swapping

**Symptoms:** Both models loaded simultaneously

**Solutions:**

1. Verify `groups.swappable.exclusive: true`
1. Check `models.<model>.ttl` is set
1. Ensure `performance.disabled: false`

### Issue: Inference Errors

**Symptoms:** Generation fails or produces errors

**Solutions:**

1. Verify model path is correct
1. Check `macros.device` is CUDA0
1. Verify `flash-attn` setting
1. Check model quantization compatibility

## Environment Setup

```bash
# Verify CUDA is accessible
nvidia-smi

# Check VRAM available
nvidia-smi --query-gpu=memory_total,memory_free --format=csv

# Verify model files exist
ls -la /home/waflores/.lmstudio/models/lmstudio-community/
```

## Integration

______________________________________________________________________

**Last Updated:** 2026-06-20\
**Status:** Production-ready\
**Version:** 1.0
