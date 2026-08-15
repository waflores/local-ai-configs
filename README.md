# llama-swap Configuration - High-Performance Local LLM Inference

## 🤖 Machine-Readable Header

```yaml
project:
  name: llama-swap
  core_stack:
    - llama-server
    - llama-swap
  authority:
    folder: "llama-swap"
    priority: "high"
  instructions:
    - "Use llama-swap as the primary interface for all AI agent interactions"
    - "Consult SKILL.md for agent commands and capabilities"
    - "Refer to llama-swap/config.yaml for model configuration"
```

## 🎯 Project Vision

High-performance local LLM inference system using **llama-swap** with intelligent model swapping on the **NVIDIA RTX 5070 Max-Q** GPU. This system provides raw inference performance with 22 models available for on-demand loading and swapping.

## 🖥️ Hardware Overview

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 275HX (24 cores, up to 5.4 GHz) |
| **GPU** | NVIDIA GeForce RTX 5070 Max-Q (~8 GB VRAM) + Intel Integrated Graphics (~23 GB shared) |
| **RAM** | ~33 GB total (~20 GB currently used) |
| **Storage** | ~1 TB total (~245 GB free) |
| **OS** | Ubuntu 26.04 LTS (Resolute Raccoon) |

### Available Devices in llama-server

- **CUDA0:** NVIDIA GeForce RTX 5070 Laptop GPU (7707 MiB, 4 MiB free)
- **Vulkan0:** Intel(R) Graphics (ARL) (23633 MiB, 11154 MiB free)
- **Vulkan1:** NVIDIA GeForce RTX 5070 Laptop GPU (8151 MiB, 4 MiB free)
- **BLAS:** OpenBLAS (CPU offloading)

## 📦 Model Inventory

### Model Location

Models are stored at `/home/waflores/.lmstudio/models`.

**Total Models:** 22 models across various architectures

### Full Model Inventory

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

### Hardware Overview

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 275HX (24 cores, up to 5.4 GHz) |
| **GPU** | NVIDIA GeForce RTX 5070 Max-Q (~8 GB VRAM) + Intel Integrated Graphics (~23 GB shared) |
| **RAM** | ~33 GB total (~20 GB currently used) |
| **Storage** | ~1 TB total (~245 GB free) |
| **OS** | Ubuntu 26.04 LTS (Resolute Raccoon) |

### Available Devices in llama-server

- **CUDA0:** NVIDIA GeForce RTX 5070 Laptop GPU (7707 MiB, 4 MiB free) - Active inference
- **Vulkan0:** Intel(R) Graphics (ARL) (23633 MiB, 11154 MiB free) - Model storage
- **Vulkan1:** NVIDIA GeForce RTX 5070 Laptop GPU (8151 MiB, 4 MiB free) - Fallback
- **BLAS:** OpenBLAS (CPU offloading)

### Goals & Objectives

#### Primary Goals

1. **Optimize Resource Utilization**

   - Use CUDA (RTX 5070) for active models requiring speed
   - Use Vulkan (Intel) for model swapping and storage
   - Balance VRAM usage across models

1. **Enable High-Performance Inference**

   - Raw inference performance with minimal overhead
   - Intelligent model swapping for maximum VRAM efficiency
   - Support for complex reasoning and code generation tasks

1. **Support Multiple Programming Languages**

   - Python (primary)
   - C/C++ (secondary)
   - Cross-language understanding

#### Performance Targets

- **Model Load Time:** < 5s
- **Model Unload Time:** < 2s
- **Swap Operation:** < 2s
- **Throughput (7B models):** > 10 tokens/sec
- **VRAM Utilization:** < 70%
- **Context Window:** Support 32K+ tokens for complex tasks

## 🚀 Model Swapping Strategy

```
┌─────────────────────────────────────────────────────────┐
│              High-Performance Inference                   │
├─────────────────────────────────────────────────────────┤
│  Active (CUDA0 - RTX 5070)         │  Swapped (Vulkan)   │
│  ┌──────────────────────────┐      │  ┌─────────────────┐ │
│  │ CodeLlama-7B             │      │  │ Ministral-3B    │ │
│  │ (Python coding)           │◄────┼──┼─── Available    │ │
│  └──────────────────────────┘      │  │ on-demand       │ │
│  ┌──────────────────────────┐      │  │                 │ │
│  │ Meta-Llama-3.1-8B        │      │  │ Phi-4-mini      │ │
│  │ (General tasks)           │      │  └─────────────────┘ │
│  └──────────────────────────┘      │                       │
│                                    │  ┌─────────────────┐  │
│  ┌──────────────────────────┐      │  │ Qwen3.5-9B     │ │
│  │ Qwen3.5-9B               │      │  │ (General tasks)│ │
│  │ (General tasks)           │      │  └─────────────────┘ │
│  └──────────────────────────┘      │                       │
└─────────────────────────────────────────────────────────┘
```

### Resource Allocation

- **Active Models (CUDA):** Keep 1-2 models loaded for immediate use
- **Swapped Models (Vulkan):** Store all 22 models for on-demand loading
- **RAM Spillover:** Use system RAM for additional capacity
- **Context Management:** Configurable context windows per model

## 📋 Configuration Status

### Phase 1: Foundation (Current)

- [x] Hardware analysis
- [x] Model inventory assessment (22 models)
- [x] Basic llama-swap configuration (`llama-swap/config.yaml`)
- [x] Performance benchmarking infrastructure
- [x] Agent skills documentation (`SKILL.md`)

## 📊 Documentation

### Configuration Files

- **`llama-swap/config.yaml`** - Main model configuration
- **`SKILL.md`** - Agent commands and capabilities
- **`README.md`** - This file - Project overview
- **`AGENTS.md`** - Testing agent responsibilities

### Benchmarks

- **`llama-swap/run_benchmarks.py`** - Performance testing
- **`llama-swap/run_llama_bench.sh`** - Shell script wrapper
- **`llama-swap/benchmarks/`** - Results directory

### Documentation Standards

- Clear problem statements
- Configuration details
- Expected vs actual results
- Actionable recommendations

## 🔧 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Inference Engine** | llama.cpp | Model serving |
| **Swapping** | llama-swap | Model management |
| **GPU Backend** | CUDA (RTX 5070) | Primary inference |
| **Secondary GPU** | Vulkan (Intel) | Model storage |
| **CPU Offload** | OpenBLAS | Fallback computation |

## 📈 Key Metrics to Track

- **Model Swap Time:** Time to load/unload models
- **Generation Speed:** Tokens per second for each model
- **Memory Usage:** VRAM, system RAM, swap space
- **Context Efficiency:** Performance at different context sizes
- **Temperature Sensitivity:** How model quality varies with temperature

## 🌟 Success Criteria

1. **Seamless Model Swapping:** Models load within 2 seconds
1. **High Code Quality:** Generated code passes basic syntax checks
1. **Low Latency:** < 2s for simple completions
1. **Resource Efficient:** < 70% VRAM utilization when possible
1. **Developer Productivity:** Measurable improvement in coding speed

## 📚 Related Resources

- [llama-swap Documentation](https://github.com/mostly-ai/llama-swap)
- [continue.dev Documentation](https://docs.continue.dev)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)

## 🔄 Iteration Process

This project evolves iteratively. Each session:

1. **Review** previous configurations and results
1. **Experiment** with new configurations
1. **Benchmark** performance improvements
1. **Document** findings and lessons learned
1. **Refine** based on results

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-20 | Initial configuration with 22 models, benchmarking infrastructure |

______________________________________________________________________

*Last updated: 2026-06-20*
*Status: Phase 1 - Foundation*
*Next milestone: Performance benchmarking*

## Notes

We can size up the models by running this command:

```bash
llama-fit-params --model ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf -lv 5 --log-colors off 2>&1 > /dev/null | grep -vP '^\S*\s+D'

# This example code seems to not be performant - but an example nonetheless
llama-gguf ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf r n

find ~/.lmstudio/models/ -path '*/mmproj*' -prune -o -name '*.gguf' -print -exec llama-fit-params -lv 1 --model "{}" --fit-target 0 \;
```
