# Parameter Optimizer Scripts

This directory contains scripts to help you find optimal parameters for your llama-swap models, based on patterns from [llama-throughput-lab](https://github.com/alexziskind1/llama-throughput-lab).

## Overview

These tools help you:

1. **Analyze** your current model configurations
1. **Benchmark** different parameter combinations
1. **Generate** optimized configurations
1. **Compare** performance across models

## Quick Start

### 1. Start llama-swap

```bash
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001
```

### 2. Analyze a single model

```bash
cd /home/waflores/DevFolder/ai/local-config/llama-swap/parameter-optimizer
python3 parameter-optimizer.py \
  --model Meta-Llama-3.1-8B-Instruct \
  --analyze
```

### 3. Run benchmarks

```bash
python3 parameter-optimizer.py \
  --model Meta-Llama-3.1-8B-Instruct \
  --benchmark
```

### 4. Analyze all models

```bash
python3 batch-analyzer.py \
  --analyze-all \
  --output-dir /home/waflores/DevFolder/ai/local-config/logs/parameter-analysis
```

### 5. Generate optimized config

```bash
python3 batch-analyzer.py \
  --generate-config \
  --output-dir /home/waflores/DevFolder/ai/local-config/logs/parameter-analysis
```

## Available Scripts

### `parameter-optimizer.py`

Main optimization script for individual models.

**Options:**
| Flag | Description |
|------|-------------|
| `--model` | Model name (required) |
| `--config` | Path to llama-swap config |
| `--benchmark` | Run throughput benchmarks |
| `--analyze` | Analyze current configuration |
| `--optimize` | Generate optimized configuration |
| `--all` | Run all analyses |
| `--output-dir` | Output directory for results |

**Examples:**

```bash
# Analyze configuration
python3 parameter-optimizer.py \
  --model Meta-Llama-3.1-8B-Instruct \
  --analyze

# Run benchmarks
python3 parameter-optimizer.py \
  --model CodeLlama-7B-Instruct \
  --benchmark

# Run all analyses
python3 parameter-optimizer.py \
  --model Qwen3.5-9B-GGUF \
  --all
```

### `batch-analyzer.py`

Analyze all models in your configuration at once.

**Options:**
| Flag | Description |
|------|-------------|
| `--config` | Path to llama-swap config |
| `--analyze-all` | Analyze all models |
| `--generate-config` | Generate optimized config file |
| `--output-dir` | Output directory for results |

**Examples:**

```bash
# Analyze all models
python3 batch-analyzer.py \
  --analyze-all \
  --output-dir logs/parameter-analysis

# Generate optimized config
python3 batch-analyzer.py \
  --generate-config \
  --output-dir logs/parameter-analysis
```

### `quick-benchmark.sh`

Quick bash script for running simple benchmarks.

**Usage:**

```bash
./quick-benchmark.sh --model Meta-Llama-3.1-8B-Instruct
./quick-benchmark.sh --model CodeLlama-7B-Instruct --temp 0.9
```

## Understanding Parameters

### Context Size (`--ctx-size`)

The context window size in tokens. Recommended values:

| Model Size | Recommended Context |
|------------|---------------------|
| ≤ 4B | 12,333 - 16,384 |
| 7-8B | 16,384 |
| 12-14B | 32,768 |
| 18-24B | 65,536 |
| ≥ 27B | 131,072 |

### Temperature (`--temp`)

Controls randomness in token selection:

| Use Case | Recommended Temp |
|----------|------------------|
| Creative writing | 0.8 - 1.0 |
| General chat | 0.7 |
| Coding | 0.5 - 0.7 |
| Reasoning | 0.6 |
| Instruction following | 0.5 |

### Top-K / Top-P Sampling

Controls token selection diversity:

| Setting | Description |
|---------|-------------|
| `top_k=40` | Consider top 40 tokens |
| `top_p=0.9` | Consider top 90% probability |
| `top_k=20` | More focused (Qwen models) |
| `top_p=0.95` | More diverse sampling |

### Special Parameters

| Parameter | Purpose |
|-----------|---------|
| `--min-p` | Minimum probability threshold (Qwen models) |
| `--reasoning` | Enable reasoning mode (Nemotron, Qwen3.5) |
| `--reasoning-format` | Reasoning output format (deepseek, etc.) |
| `--reasoning-budget` | Max tokens for reasoning |
| `--cache-ram` | RAM spillover for cache (A2B models) |

## Model-Specific Recommendations

### Llama Models

- **8B**: `ctxSize=16384`, `temp=0.7`, `top_k=40`, `top_p=0.9`
- **14B**: `ctxSize=32768`, `temp=0.7`
- **30B+**: `ctxSize=65536-131072`, `temp=0.6`

### CodeLlama

- `ctxSize=16384`, `temp=0.8`, `top_k=40` (higher temp for creativity)

### Qwen Models

- **4B**: `ctxSize=123333`, `temp=0.7`
- **9B**: `ctxSize=262144`, `temp=0.6`, `min_p=0`, `top_k=20`, `top_p=0.95`
- **27B**: `ctxSize=1024`, `temp=0.7`

### Mistral Models

- **3B**: `ctxSize=133333`, `temp=0.7`
- **12B**: `ctxSize=1024`, `temp=0.7`

### Nemotron

- `ctxSize=113333`, with reasoning parameters enabled

### Phi Models

- **4B**: `ctxSize=123333`, `temp=0.7`
- **Reasoning**: `ctxSize=1024`, `temp=0.7`

### Gemma

- `ctxSize=18000`, `temp=0.7`

### Specialized Models

- **Zerank**: Use Vulkan device, disable reasoning
- **OlmOCR**: `ctxSize=32727`, standard params
- **Devstral**: `ctxSize=1024`, `temp=0.7`

## Output Files

Results are saved to the output directory:

| File | Description |
|------|-------------|
| `*_analysis.json` | Configuration analysis for a model |
| `*_benchmark.json` | Benchmark results |
| `optimized-*.json` | Optimized parameters |
| `optimized-config.yaml` | Complete optimized config |

## Interpreting Results

### Analysis Output

```
Model: Meta-Llama-3.1-8B-Instruct
Issues: 0
Recommendations: 0
Notes:
  - Medium-small model - balanced for general-purpose tasks
```

### Benchmark Output

```
Throughput: 45.2 tokens/s
Latency: 22.1 ms
```

Higher throughput and lower latency = better performance.

## Best Practices

1. **Start with defaults**: Use the recommended parameters as a baseline
1. **Benchmark before optimizing**: Run benchmarks to find optimal settings
1. **Test with your workload**: Different tasks may prefer different parameters
1. **Monitor VRAM**: Ensure context size doesn't exceed available memory
1. **Use smaller contexts for swapped models**: Free up VRAM for active models

## Troubleshooting

### Model not found

```
Error: Model 'XXX' not found in configuration.
```

Ensure the model name matches exactly (case-sensitive).

### Connection refused

```
llama-swap is not running. Please start it first.
```

Start llama-swap before running benchmarks.

### Out of memory

Reduce `ctxSize` or enable model swapping with smaller contexts.

## See Also

- [llama-throughput-lab](https://github.com/alexziskind1/llama-throughput-lab) - Throughput testing framework
- [llama-swap](https://github.com/mostlygeek/llama-swap) - Model swapping proxy
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - LLM inference library

## License

These scripts are provided as-is for your local development use.
