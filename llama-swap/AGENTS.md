# CONFIG-TUNING-GUIDE.md

## Purpose

This document provides a structured, reproducible testing framework for lesser intelligent AI agents to iterate on llama-swap configuration values.

## Prerequisites Checklist

Before starting any tests, ensure:

- [ ] **llama-swap is installed** in the target environment
- [ ] **Model files are downloaded** to the specified root directory
- [ ] **CUDA drivers** are installed and accessible
- [ ] **Environment variables** are set (see `inferhost.env`)
- [ ] **Python dependencies** (pip install llama-swap) are installed

## Standard Testing Workflow

### Step 1: Initialize Test Session

```bash
# Navigate to project root
cd /home/waflores/DevFolder/ai/local-config

# Create test session log
mkdir -p logs/test-session-YYYYMMDD-HHMMSS
touch logs/test-session-YYYYMMDD-HHMMSS/iteration.log
```

### Step 2: Load Configuration Template

```bash
# Copy base config to test location
cp llama-swap/config.yaml tests/current-config.yaml

# Edit with test parameters (use sed for automation)
sed -i 's/ROOT_DIR: .*/ROOT_DIR: /home/waflores/DevFolder/ai/local-config/inferhost/models/g' tests/current-config.yaml
```

### Step 3: Run Test Case

```bash
# Execute single test case
python -m llama_server.main --config tests/current-config.yaml --verbose

# Or run benchmark script
python tests/run_benchmark.py --config tests/current-config.yaml --model-name test-model
```

### Step 4: Capture Results

```bash
# Log to iteration file
echo "=== Test Run $(date) ===" >> logs/test-session-YYYYMMDD-HHMMSS/iteration.log
echo "Config: tests/current-config.yaml" >> logs/test-session-YYYYMMDD-HHMMSS/iteration.log
```

### Step 5: Analyze and Iterate

```bash
# Check for errors
grep -i "error\|exception\|failed" logs/test-session-YYYYMMDD-HHMMSS/iteration.log

# If successful, increment parameter and retest
# Example: Increase batch-size by 1
sed -i 's/batch-size: .*/batch-size: 1/' tests/current-config.yaml
```

## Test Case Templates

### Template 1: Basic Model Load Test

```yaml
# tests/basic-load-test.yaml
ROOT_DIR: /home/waflores/DevFolder/ai/local-config/inferhost/models
BACKEND: cuda
MODEL: "Qwen/Qwen2.5-1.5B-Instruct:Q4_K_M"
MAX_CONCURRENT_REQUESTS: 1
MAX_TOTAL_TOKENS: 4096
MODEL_PATH: "${ROOT_DIR}/Qwen/Qwen2.5-1.5B-Instruct"
```

**Expected Behavior:**

- Model loads into VRAM within 5 seconds
- First token generated within 2 seconds
- No VRAM overflow errors

**Success Criteria:**

- [ ] No errors in logs
- [ ] Model appears in llama-swap model list
- [ ] Generation completes without hanging

______________________________________________________________________

### Template 2: VRAM Optimization Test

```yaml
# tests/vram-opt-test.yaml
ROOT_DIR: /home/waflores/DevFolder/ai/local-config/inferhost/models
BACKEND: cuda
MODEL: "Meta-Llama-3-8B-Instruct:Q4_K_M"
MAX_CONCURRENT_REQUESTS: 1
MAX_TOTAL_TOKENS: 8192
MAX_VRAM: 8192  # 8GB VRAM
MODEL_PATH: "${ROOT_DIR}/Meta-Llama-3-8B-Instruct"
```

**Expected Behavior:**

- Model fits within VRAM constraints
- No OOM (Out of Memory) errors
- Generation speed > 5 tokens/sec

**Success Criteria:**

- [ ] No OOM errors
- [ ] Generation completes
- [ ] Speed meets minimum threshold

______________________________________________________________________

### Template 3: Context Length Test

```yaml
# tests/context-length-test.yaml
ROOT_DIR: /home/waflores/DevFolder/ai/local-config/inferhost/models
BACKEND: cuda
MODEL: "Qwen/Qwen2.5-1.5B-Instruct:Q4_K_M"
MAX_CONCURRENT_REQUESTS: 1
MAX_TOTAL_TOKENS: 16384  # Test with 16k context
CONTEXT_WINDOW: 8192
MODEL_PATH: "${ROOT_DIR}/Qwen/Qwen2.5-1.5B-Instruct"
```

**Expected Behavior:**

- Handles long context without errors
- No memory fragmentation issues
- Generation quality maintained

**Success Criteria:**

- [ ] No context overflow errors
- [ ] Generation completes
- [ ] Output is coherent

______________________________________________________________________

### Template 4: Batch Size Test

```yaml
# tests/batch-size-test.yaml
ROOT_DIR: /home/waflores/DevFolder/ai/local-config/inferhost/models
BACKEND: cuda
MODEL: "Qwen/Qwen2.5-1.5B-Instruct:Q4_K_M"
MAX_CONCURRENT_REQUESTS: 2
MAX_TOTAL_TOKENS: 4096
MODEL_PATH: "${ROOT_DIR}/Qwen/Qwen2.5-1.5B-Instruct"
```

**Expected Behavior:**

- Handles multiple concurrent requests
- No request queuing delays
- Consistent generation speed

**Success Criteria:**

- [ ] Multiple requests processed
- [ ] No request failures
- [ ] Speed remains consistent

______________________________________________________________________

### Template 5: Model Swap Test

```yaml
# tests/model-swap-test.yaml
ROOT_DIR: /home/waflores/DevFolder/ai/local-config/inferhost/models
BACKEND: cuda
MODEL: "Qwen/Qwen2.5-1.5B-Instruct:Q4_K_M"
MAX_CONCURRENT_REQUESTS: 1
MAX_TOTAL_TOKENS: 4096
MODEL_PATH: "${ROOT_DIR}/Qwen/Qwen2.5-1.5B-Instruct"
SWAP_ENABLED: true
SWAP_ON_IDLE: 300  # Swap after 5 minutes of inactivity
```

**Expected Behavior:**

- Model swaps out after idle period
- Model loads back on next request
- No data loss during swap

**Success Criteria:**

- [ ] Model swaps out (VRAM freed)
- [ ] Model loads back on request
- [ ] No corruption errors

## Parameter Tuning Checklist

| Parameter | Range to Test | Impact | Priority |
|-----------|---------------|--------|----------|
| `MAX_TOTAL_TOKENS` | 4096, 8192, 16384 | Memory usage | High |
| `MAX_CONCURRENT_REQUESTS` | 1, 2, 4 | Throughput | Medium |
| `CONTEXT_WINDOW` | 2048, 4096, 8192 | Context handling | High |
| `MAX_VRAM` | 6144, 7168, 8192 | VRAM allocation | Critical |
| `SWAP_ON_IDLE` | 300, 600, 900 | Swap frequency | Low |

## Common Issues and Solutions

### Issue: "CUDA out of memory"

**Cause:** Model too large for VRAM
**Solution:**

1. Reduce `MAX_TOTAL_TOKENS` by 50%
1. Use lower quantization (Q3_K_M instead of Q4_K_M)
1. Enable swap for this model

### Issue: "Context overflow"

**Cause:** Context window too large for model
**Solution:**

1. Reduce `MAX_TOTAL_TOKENS`
1. Use smaller model for shorter contexts

### Issue: "Slow generation"

**Cause:** Batch size too high or VRAM constrained
**Solution:**

1. Reduce `MAX_CONCURRENT_REQUESTS`
1. Increase `MAX_VRAM` (if available)
1. Use higher quantization (Q5_K_M)

### Issue: "Model fails to swap"

**Cause:** Insufficient disk space or swap disabled
**Solution:**

1. Enable `SWAP_ENABLED: true`
1. Check disk space in model root folder
1. Verify swap path is writable

## Result Logging Template

```markdown
## Iteration Log: [Date]

### Configuration Tested
- File: `tests/current-config.yaml`
- Model: `Qwen/Qwen2.5-1.5B-Instruct:Q4_K_M`

### Parameters
- MAX_TOTAL_TOKENS: 4096
- MAX_CONCURRENT_REQUESTS: 1
- MAX_VRAM: 8192
- CONTEXT_WINDOW: 8192

### Results
- **Status:** [ ] PASS / [ ] FAIL
- **Load Time:** X seconds
- **Generation Speed:** X tokens/sec
- **VRAM Used:** X / 8192 MB
- **Errors:** None / [List errors]

### Observations
- [What worked]
- [What didn't work]
- [Unexpected behavior]

### Next Steps
- [Parameter to adjust]
- [Value to test next]

---
```

## Success Metrics

### Minimum Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Model Load Time | < 5s | < 10s |
| First Token | < 2s | < 5s |
| Generation Speed | > 10 t/s | > 5 t/s |
| VRAM Utilization | < 70% | < 90% |
| Context Efficiency | > 80% | > 50% |

### Quality Targets

| Metric | Target |
|--------|--------|
| Error Rate | 0% | < 5% |
| Context Retention | 100% | > 95% |
| Swap Integrity | 100% | > 99% |

## Iteration Protocol

1. **Start with Template 1** (Basic Load) - ensure model loads
1. **Run Template 2** (VRAM) - verify memory constraints
1. **Run Template 3** (Context) - test context handling
1. **Run Template 4** (Batch) - test concurrency
1. **Run Template 5** (Swap) - test swapping behavior
1. **Adjust parameters** based on results
1. **Log findings** using Result Logging Template
1. **Repeat** until all targets met

## Environment Setup

```bash
# Source environment variables
source /home/waflores/DevFolder/ai/local-config/inferhost/inferhost.env

# Verify CUDA is accessible
cuda-device-query

# Check VRAM available
cat /proc/driver/nvidia/gpu/0/vram_total

# Verify model files exist
ls -la /home/waflores/DevFolder/ai/local-config/inferhost/models/
```

______________________________________________________________________

**Last Updated:** 2026-06-13
**Author:** Configuration Analyst Agent
**Status:** Phase 1 - Foundation
