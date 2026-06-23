# Llama-Swap Performance Notes

> Collection of benchmark results, experiments, and observations from `config.yaml` comments and testing.

______________________________________________________________________

## 📊 Qwythos-9B-Claude-Mythos-5-1M Benchmarks

### Baseline Performance

| Metric | Value | Context Size |
|--------|-------|--------------|
| Prompt Speed | 817.8 t/s | 115,968 tokens |
| Generation Speed | 45.8 t/s | 115,968 tokens |

### TurboQuant Optimization

| Metric | Value | Context Size |
|--------|-------|--------------|
| Prompt Speed | 746.8 t/s | 210,000 tokens |
| Generation Speed | 43.2 t/s | 210,000 tokens |

**Note:** TurboQuant provides ~8.6% prompt speed improvement but ~5.4% generation speed decrease.

### Cache Type Experiments

| Cache Type K | Cache Type V | Result |
|--------------|--------------|--------|
| eden4 | eden3 | Tested |
| q4_0 | q4_0 | Tested |
| turbo4 | turbo3 | Tested (with turboquant) |

### Command Line Tests

```bash
# Baseline (no turboquant)
./build/bin/llama-cli -lv 3 --model ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf \
  --n-gpu-layers all --cpu-moe --no-mmap --mlock \
  --cache-type-k eden4 --cache-type-v eden3 \
  --reasoning off

# With q4_0 cache
llama-cli -lv 6 --model ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf \
  --n-gpu-layers all --cpu-moe --no-mmap --mlock \
  --cache-type-k q4_0 --cache-type-v q4_0

# TurboQuant enabled
./build/bin/llama-cli -lv 3 --model ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf \
  --n-gpu-layers all --cpu-moe --cache-type-k turbo4 --cache-type-v turbo3 \
  --no-mmap --mlock --reasoning off --ctx-size 210000
```

______________________________________________________________________

## 📊 IBM Granite 4.1 Benchmarks

### TODO: Fine-tuning Required

This model appears to need fine-tuning for optimal performance.

### Baseline Performance

| Metric | Value |
|--------|-------|
| Prompt Speed | 406.2 t/s |
| Generation Speed | 49.9 t/s |

### Alternative Runner Comparison

| Runner | Prompt Speed | Generation Speed |
|--------|--------------|------------------|
| llama-cli (baseline) | 406.2 t/s | 49.9 t/s |
| Custom runner | 266.7 t/s | 44.7 t/s |

**Note:** The alternative runner shows ~34% slower prompt processing and ~11% slower generation.

### Configuration Experiments

#### CPU MoE Configuration

```bash
./build/bin/llama-cli -lv 3 --model ~/.lmstudio/models/ibm-granite/granite-4.1-8b-GGUF/granite-4.1-8b-Q4_K_M.gguf \
  --n-gpu-layers 999 --n-cpu-moe 35 \
  --no-mmap --mlock --ctx-size 16350
```

#### Eden Cache Types

```bash
./build/bin/llama-cli -lv 3 --model ~/.lmstudio/models/ibm-granite/granite-4.1-8b-GGUF/granite-4.1-8b-Q4_K_M.gguf \
  --n-gpu-layers 999 --n-cpu-moe 35 \
  --cache-type-k eden4 --cache-type-v eden3 \
  --no-mmap --mlock --ctx-size 60000
```

______________________________________________________________________

## 📝 Model-Specific Notes

### FastContext-1.0-4B-SFT

> "interesting - a little dull"

______________________________________________________________________

## 🔧 Configuration Comments

### YAML Schema

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/mostlygeek/llama-swap/refs/heads/main/config-schema.json
```

______________________________________________________________________

## 📈 Performance Summary Table

| Model | Prompt Speed (t/s) | Generation Speed (t/s) | Context Size | Notes |
|-------|-------------------|------------------------|--------------|-------|
| Qwythos-9B-Claude-Mythos-5-1M | 817.8 | 45.8 | 115,968 | Baseline |
| Qwythos-9B-Claude-Mythos-5-1M (turboquant) | 746.8 | 43.2 | 210,000 | Optimized |
| Granite-4.1 | 406.2 | 49.9 | 16,350 | Needs fine-tuning |
| Granite-4.1 (alt runner) | 266.7 | 44.7 | 60,000 | Slower runner |

______________________________________________________________________

## 🎯 Key Observations

1. **Qwythos-9B-Claude-Mythos-5-1M** shows excellent prompt processing speeds (800+ t/s)
1. **TurboQuant** provides modest improvements (~8%) but slight generation speed trade-off
1. **Granite-4.1** has the lowest prompt speed but highest generation speed among tested models
1. **Cache type selection** significantly impacts performance - eden4/eden3 and turbo4/turbo3 show promise
1. **CPU MoE** configuration (`--n-cpu-moe 35`) appears beneficial for MoE models

______________________________________________________________________

## 📅 Last Updated

2026-06-20

______________________________________________________________________

*This file was created by extracting benchmark data and notes from `llama-swap/config.yaml` comments.*
