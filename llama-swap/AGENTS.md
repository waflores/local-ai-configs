# llama-swap Configuration Testing Agent

## Purpose

This agent handles testing and validation of llama-swap configurations. It provides structured testing workflows for verifying model loading, swapping, and performance.

## Responsibilities

- Run model load/unload tests
- Validate VRAM usage and constraints
- Test context window handling
- Verify model swapping behavior
- Collect performance metrics
- Document test results

## Testing Commands

### Run All Models Test

```bash
# Test all configured models
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001

# Verify health endpoint
curl http://127.0.0.1:10001/health

# List available models
curl http://127.0.0.1:10001/v1/models
```

### Test Single Model

```bash
# Load specific model
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Meta-Llama-3.1-8B-Instruct",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
    "ttl": 600
  }'
```

### Test Model Swap

```bash
# Load first model
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Meta-Llama-3.1-8B-Instruct",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    "ttl": 600
  }'

# Load second model (should swap first)
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CodeLlama-7B-Instruct",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/CodeLlama-7B-Instruct-GGUF",
    "ttl": 600
  }'
```

### Test Inference

```bash
# Test chat completion
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

## Test Cases

### Test Case 1: Model Load

```yaml
# tests/model-load.yaml
test_name: "model_load"
model: "Meta-Llama-3.1-8B-Instruct"
expected_vram_mb: 5120
expected_load_time_seconds: 10
```

### Test Case 2: Model Unload

```yaml
# tests/model-unload.yaml
test_name: "model_unload"
model: "Meta-Llama-3.1-8B-Instruct"
expected_free_vram_mb: 7500
```

### Test Case 3: Model Swap

```yaml
# tests/model-swap.yaml
test_name: "model_swap"
models:
  - "Meta-Llama-3.1-8B-Instruct"
  - "CodeLlama-7B-Instruct"
expected_concurrent_models: 1
```

### Test Case 4: Inference Latency

```yaml
# tests/inference-latency.yaml
test_name: "inference_latency"
model: "Meta-Llama-3.1-8B-Instruct"
prompt: "Count from 1 to 10"
expected_tokens_per_second: 10
```

### Test Case 5: Context Window

```yaml
# tests/context-window.yaml
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
- **Load Time:** X.XXs (expected: < 10s)
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
# Source environment variables
source /home/waflores/DevFolder/ai/local-config/other_experiments/inferhost/inferhost.env

# Verify CUDA is accessible
nvidia-smi

# Check VRAM available
cat /proc/driver/nvidia/gpu/0/vram_total

# Verify model files exist
ls -la /home/waflores/.lmstudio/models/lmstudio-community/
```

## Integration with continue.dev

The testing agent integrates with continue.dev for:

- Inline code suggestions
- Chat with codebase
- Documentation generation

Configure continue.dev to use llama-swap models:

```json
// .continue/config.json
{
  "models": [
    {
      "provider": "llama-swap",
      "name": "Meta-Llama-3.1-8B-Instruct",
      "host": "http://127.0.0.1:10001"
    }
  ]
}
```

______________________________________________________________________

**Last Updated:** 2026-06-13
**Status:** Phase 1 - Foundation
