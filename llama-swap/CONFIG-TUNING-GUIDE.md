# Llama-Swap Configuration Tuning Guide

## Purpose

This document provides a structured approach for testing and tuning llama-swap configuration values. Use this to systematically experiment with different settings and document results.

______________________________________________________________________

## 📋 Test Case Templates

### Template 1: Basic Model Loading Test

```yaml
test_case: basic_load
model_name: <MODEL_NAME>
model_path: <PATH_TO_MODEL>
target_vram_gb: <MAX_VRAM>
target_ram_gb: <MAX_RAM>

# Parameters to test (adjust one at a time)
context_length: 4096
max_tokens: 2048
num_threads: 8
num_batch_size: 512
flash_attn: true
offload_dir: /path/to/offload
offload_limit: 1.0

# Expected behavior
expected_vram_usage: <GB>
expected_ram_usage: <GB>
expected_latency_ms: <MS>

# Commands to run
test_commands:
  - "llama-swap load --model <MODEL_NAME>"
  - "llama-swap unload --model <MODEL_NAME>"
  - "nvidia-smi"  # Check VRAM usage

# Success criteria
success_criteria:
  - "Model loads without OOM errors"
  - "VRAM usage within target limits"
  - "Generation completes successfully"
```

______________________________________________________________________

### Template 2: VRAM Optimization Test

```yaml
test_case: vram_optimization
model_name: <MODEL_NAME>
model_path: <PATH_TO_MODEL>
target_vram_gb: <MAX_VRAM>
target_ram_gb: <MAX_RAM>

# VRAM thresholds
vram_threshold_percent: 70
vram_threshold_bytes: <BYTES>

# Offload settings
offload_limit: 0.8
offload_limit_percent: 80
offload_threshold_percent: 60

# Context settings
context_length: 4096
max_tokens: 1024

# Test scenarios
scenarios:
  - name: "full_load"
    description: "Load model entirely on GPU"
    offload_limit: 1.0
    expected_vram: <GB>
  
  - name: "partial_offload"
    description: "Offload layers to CPU when VRAM high"
    offload_limit: 0.8
    expected_vram: <GB>
  
  - name: "aggressive_offload"
    description: "Aggressive offloading for max VRAM headroom"
    offload_limit: 0.5
    expected_vram: <GB>

# Commands
test_commands:
  - "llama-swap load --model <MODEL_NAME> --offload-limit <LIMIT>"
  - "sleep 5"
  - "nvidia-smi"
  - "llama-swap unload --model <MODEL_NAME>"

# Success criteria
success_criteria:
  - "VRAM stays below threshold"
  - "Model still generates correctly"
  - "No quality degradation"
```

______________________________________________________________________

### Template 3: Context Length Test

```yaml
test_case: context_length
model_name: <MODEL_NAME>
model_path: <PATH_TO_MODEL>

# Context settings to test
context_lengths:
  - 2048
  - 4096
  - 8192
  - 16384

# For each context length
for_each_context:
  - name: test_generation
    max_tokens: 512
    prompt: "Write a short Python function that calculates fibonacci numbers."
    expected_completion: true
  
  - name: test_vram
    check_vram_after: true
    expected_vram_gb: <LIMIT>

# Commands
test_commands:
  - "llama-swap load --model <MODEL_NAME> --context-length <LENGTH>"
  - "Send test prompt"
  - "llama-swap unload --model <MODEL_NAME>"
  - "nvidia-smi"

# Success criteria
success_criteria:
  - "Generation completes without OOM"
  - "Output quality maintained"
  - "VRAM usage acceptable"
```

______________________________________________________________________

### Template 4: Batch Size Test

```yaml
test_case: batch_size
model_name: <MODEL_NAME>
model_path: <PATH_TO_MODEL>

# Batch sizes to test
batch_sizes:
  - 512
  - 1024
  - 2048
  - 4096

# For each batch size
for_each_batch:
  - name: test_speed
    prompt: "Write a C++ function that sorts an array."
    expected_tokens_per_second: <TPS>
  
  - name: test_memory
    check_memory_after: true
    expected_ram_gb: <LIMIT>

# Commands
test_commands:
  - "llama-swap load --model <MODEL_NAME> --batch-size <SIZE>"
  - "Send test prompt"
  - "llama-swap unload --model <MODEL_NAME>"
  - "nvidia-smi"

# Success criteria
success_criteria:
  - "Generation speed acceptable"
  - "No memory errors"
  - "Quality maintained"
```

______________________________________________________________________

### Template 5: Model Swapping Test

```yaml
test_case: model_swap
model_name_1: <MODEL_NAME_1>
model_path_1: <PATH_TO_MODEL_1>
model_name_2: <MODEL_NAME_2>
model_path_2: <PATH_TO_MODEL_2>

# Swap threshold settings
swap_threshold_percent: 80
swap_threshold_bytes: <BYTES>

# VRAM budget
target_vram_gb: <MAX_VRAM>

# Test scenarios
scenarios:
  - name: "swap_small_to_large"
    description: "Swap smaller model out when loading larger"
    load_model_1: true
    load_model_2: true
    expected_swap: true
  
  - name: "swap_large_to_small"
    description: "Swap larger model out when loading smaller"
    load_model_1: true
    unload_model_1: true
    load_model_2: true
    expected_swap: true

# Commands
test_commands:
  - "llama-swap load --model <MODEL_NAME_1>"
  - "nvidia-smi"
  - "llama-swap load --model <MODEL_NAME_2>"
  - "nvidia-smi"  # Check for swap
  - "llama-swap unload --model <MODEL_NAME_2>"
  - "llama-swap unload --model <MODEL_NAME_1>"

# Success criteria
success_criteria:
  - "Only one model loaded at a time"
  - "Swap occurs at threshold"
  - "No VRAM overflow"
```

______________________________________________________________________

## 🎯 Parameter Tuning Checklist

### VRAM Optimization Parameters

| Parameter | Range | Impact | Test Priority |
|-----------|-------|--------|---------------|
| `offload_limit` | 0.5 - 1.0 | VRAM headroom | 🔴 High |
| `offload_threshold_percent` | 50 - 80 | Swap timing | 🟡 Medium |
| `vram_threshold_percent` | 60 - 80 | Trigger point | 🔴 High |
| `context_length` | 2048 - 16384 | VRAM usage | 🔴 High |
| `num_batch_size` | 256 - 4096 | Speed vs memory | 🟡 Medium |

### Performance Parameters

| Parameter | Range | Impact | Test Priority |
|-----------|-------|--------|---------------|
| `num_threads` | 1 - 32 | CPU utilization | 🟡 Medium |
| `flash_attn` | true/false | Speed | 🟢 Low |
| `max_tokens` | 512 - 4096 | Generation time | 🟡 Medium |

### Quality Parameters

| Parameter | Range | Impact | Test Priority |
|-----------|-------|--------|---------------|
| `context_length` | 2048 - 16384 | Context window | 🔴 High |
| `num_gqa` | 1 - 8 | Attention heads | 🟢 Low |
| `num_attention_heads` | 8 - 128 | Attention quality | 🟢 Low |

______________________________________________________________________

## 📊 Testing Workflow

### Step 1: Single Model Load Test

```bash
# 1. Test basic load
llama-swap load --model <MODEL> --offload-limit 1.0

# 2. Check VRAM
nvidia-smi

# 3. Test generation
# Send test prompt

# 4. Unload
llama-swap unload --model <MODEL>
```

**Document:**

- ✅ Did it load?
- ✅ VRAM usage: \_\_\_ GB
- ✅ Generation speed: \_\_\_ tokens/sec
- ✅ Any errors? \_\_\_

### Step 2: VRAM Optimization

```bash
# 1. Test with offload
llama-swap load --model <MODEL> --offload-limit 0.8

# 2. Check VRAM
nvidia-smi

# 3. Test generation
# Send test prompt

# 4. Unload
llama-swap unload --model <MODEL>
```

**Document:**

- ✅ VRAM usage: \_\_\_ GB (was \_\_\_ GB)
- ✅ Generation still works? Yes/No
- ✅ Quality degraded? Yes/No

### Step 3: Context Length Test

```bash
# 1. Test different context lengths
for ctx in 2048 4096 8192; do
  llama-swap load --model <MODEL> --context-length $ctx
  nvidia-smi
  llama-swap unload --model <MODEL>
done
```

**Document:**

- ✅ VRAM at 2048: \_\_\_ GB
- ✅ VRAM at 4096: \_\_\_ GB
- ✅ VRAM at 8192: \_\_\_ GB
- ✅ Max acceptable: \_\_\_ GB

### Step 4: Model Swap Test

```bash
# 1. Load model 1
llama-swap load --model <MODEL1>

# 2. Load model 2 (should swap)
llama-swap load --model <MODEL2>

# 3. Check VRAM
nvidia-smi

# 4. Unload both
llama-swap unload --model <MODEL2>
llama-swap unload --model <MODEL1>
```

**Document:**

- ✅ Model 1 loaded: \_\_\_ GB VRAM
- ✅ Model 2 loaded (swapped?): Yes/No
- ✅ VRAM after swap: \_\_\_ GB
- ✅ Works correctly? Yes/No

______________________________________________________________________

## 📝 Result Logging Template

```markdown
## Test Results: <MODEL_NAME>

### Basic Load Test
- **Status**: ✅ Pass / ❌ Fail
- **VRAM Used**: ___ GB / ___ GB (target)
- **Generation Speed**: ___ tokens/sec
- **Errors**: None / <describe>

### VRAM Optimization
- **Best offload_limit**: ___
- **VRAM with optimization**: ___ GB
- **Quality impact**: None / Slight / Significant

### Context Length
- **Max context**: ___ tokens
- **VRAM at max context**: ___ GB
- **Recommended**: ___ tokens

### Performance
- **Batch size**: ___
- **Tokens/sec**: ___
- **CPU threads**: ___

### Overall Assessment
- **Recommended config**: <paste config snippet>
- **Notes**: <any observations>
```

______________________________________________________________________

## 🚨 Common Issues & Solutions

### Issue: OOM (Out of Memory)

**Symptoms**: `CUDA out of memory` error

**Solutions**:

1. Reduce `offload_limit` from 1.0 to 0.8
1. Reduce `context_length` from 4096 to 2048
1. Reduce `num_batch_size` from 1024 to 512
1. Check if model fits at all: `llama-server --check-memory`

### Issue: Slow Generation

**Symptoms**: < 5 tokens/sec

**Solutions**:

1. Increase `num_batch_size`
1. Enable `flash_attn: true`
1. Increase `num_threads` (if multi-core CPU)
1. Check CUDA version compatibility

### Issue: Quality Degradation

**Symptoms**: Garbled text, wrong answers

**Solutions**:

1. Increase `offload_limit` (keep more on GPU)
1. Reduce `max_tokens`
1. Check model file integrity
1. Try different quantization (Q4_K_M → Q5_K_M)

### Issue: Model Doesn't Swap

**Symptoms**: Both models loaded, high VRAM usage

**Solutions**:

1. Lower `vram_threshold_percent` from 80 to 60
1. Lower `swap_threshold_percent` from 80 to 70
1. Check `offload_dir` is writable
1. Verify models.toml has correct paths

______________________________________________________________________

## 📈 Performance Targets

### VRAM Utilization

| Model Size | Target VRAM | Max VRAM | Offload Limit |
|------------|-------------|----------|---------------|
| < 5GB | < 6GB | < 7GB | 0.9 |
| 5-10GB | < 10GB | < 12GB | 0.8 |
| 10-15GB | < 15GB | < 18GB | 0.7 |
| > 15GB | < 20GB | < 24GB | 0.6 |

### Generation Speed Targets

| Model Size | Target TPS | Min TPS | Batch Size |
|------------|------------|---------|------------|
| < 5GB | > 20 | > 10 | 1024-2048 |
| 5-10GB | > 15 | > 8 | 512-1024 |
| 10-15GB | > 10 | > 5 | 256-512 |
| > 15GB | > 5 | > 2 | 256 |

### Context Window

| Use Case | Recommended | Max |
|----------|-------------|-----|
| Code completion | 2048 | 4096 |
| General chat | 4096 | 8192 |
| Long documents | 8192 | 16384 |

______________________________________________________________________

## ✅ Validation Checklist

Before committing a configuration:

- [ ] Model loads without OOM errors
- [ ] VRAM usage within target limits
- [ ] Generation speed meets minimum targets
- [ ] Output quality is acceptable
- [ ] Model unloads cleanly
- [ ] Swap behavior works correctly
- [ ] Configuration documented with results
- [ ] Notes on any edge cases added

______________________________________________________________________

## 🔄 Iteration Log Template

````markdown
## Iteration #<N>: <MODEL_NAME> Tuning

**Date**: <YYYY-MM-DD>
**Session**: <session-id or description>

### Configuration Tested
```yaml
# Paste the config snippet tested
````

### Results

- **VRAM Usage**: \_\_\_ GB (target: \_\_\_ GB)
- **Generation Speed**: \_\_\_ tokens/sec (target: \_\_\_ TPS)
- **Context Length**: \_\_\_ tokens (max tested: \_\_\_)
- **Quality**: ✅ Good / ⚠️ Acceptable / ❌ Poor

### Issues Encountered

- \<issue 1>
- \<issue 2>

### Solutions Tried

- \<solution 1>
- \<solution 2>

### Final Configuration

```yaml
# The working configuration
```

### Notes

<observations and learnings>

### Next Steps

<what to test next>
```

______________________________________________________________________

## 📚 References

- \[llama-swap documentation\](https://github.com/mc3x LLC/llama-swap)
- [llama.cpp documentation](https://github.com/ggerganov/llama.cpp)
- [HuggingFace model hub](https://huggingface.co/models)

______________________________________________________________________

*Last updated: 2026-06-12*
*Status: Active tuning phase*
