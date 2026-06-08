# Llama-Swap + Continue.dev Configuration Journey

## 🎯 Project Vision

Create an optimized local LLM setup using **llama-swap** integrated with **continue.dev VSCode extension** to enhance coding productivity for Python, C, and C++ projects. The system will leverage the **NVIDIA RTX 5070 Max-Q** GPU with intelligent model swapping to maximize resource utilization.

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

### Code-Specialized Models

| Model | Parameters | Size (Q4_K_M) | Use Case |
|-------|------------|---------------|----------|
| CodeLlama-7B-Instruct | 7B | ~4 GB | Python, general coding |
| Granite-4.0-h-tiny | 7B | ~4 GB | IBM's code model |

### Mistral Family

| Model | Parameters | Size (Q4_K_M) | Use Case |
|-------|------------|---------------|----------|
| Ministral-3B | 3B | ~2 GB | Fast completions |
| Ministral-14B | 14B | ~8 GB | Reasoning tasks |
| Devstral-24B | 24B | ~14 GB | Advanced reasoning |
| Mistral-Nemo-13B | 13B | ~6.5 GB | Balanced performance |

### Qwen Family

| Model | Parameters | Size (Q4_K_M) | Use Case |
|-------|------------|---------------|----------|
| DeepSeek-R1-8B | 8B | ~5 GB | Reasoning |
| Qwen3.5-9B | 9B | ~5.6 GB | General tasks |
| Qwen3.6-27B | 27B | ~16.5 GB | Advanced tasks |
| Qwen3-VL-8B | 8B | ~5 GB | Vision-language |

### NVIDIA Models

| Model | Parameters | Size (Q4_K_M) | Use Case |
|-------|------------|---------------|----------|
| Nemotron-3-Nano-4B | 4B | ~2.8 GB | Optimized for NVIDIA |

### Phi Family

| Model | Parameters | Size (Q4_K_M) | Use Case |
|-------|------------|---------------|----------|
| Phi-4-mini | 3B | ~2.5 GB | Lightweight tasks |
| Phi-4-reasoning-plus | 13B | ~9 GB | Advanced reasoning |

### Other Models

| Model | Parameters | Size | Use Case |
|-------|------------|------|----------|
| LFM2-24B-A2B | 24B | ~14.4 GB | Embeddings |
| gemma-4-E4B-it | 8B | ~5.3 GB | General tasks |
| olmOCR-2-7B | 8B | ~4.7 GB | OCR tasks |

**Total Models:** 22 models across various architectures

## 🎯 Goals & Objectives

### Primary Goals

1. **Optimize Resource Utilization**

   - Use CUDA (RTX 5070) for active models requiring speed
   - Use Vulkan (Intel) for model swapping and storage
   - Balance VRAM usage across models

1. **Enable Advanced continue.dev Features**

   - Code completion (inline suggestions)
   - Chat with codebase
   - Natural language to code generation
   - Documentation generation
   - Refactoring suggestions

1. **Support Multiple Programming Languages**

   - Python (primary)
   - C/C++ (secondary)
   - Cross-language understanding

### Performance Targets

- **Latency:** < 2s for model swap operations
- **Throughput:** > 10 tokens/sec for 7B models
- **Context Window:** Support 32K+ tokens for complex tasks

## 🚀 Strategy Overview

### Model Swapping Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    Model Swapping                        │
├─────────────────────────────────────────────────────────┤
│  Active Models (CUDA)    │  Swapped Models (Vulkan)     │
│  ┌────────────────────┐  │  ┌─────────────────────────┐ │
│  │ CodeLlama-7B       │  │  │ Ministral-3B            │ │
│  │ (Python coding)     │◄─┼──┼──► Available on-demand  │ │
│  └────────────────────┘  │  │                         │ │
│  ┌────────────────────┐  │  │                         │ │
│  │ Nemotron-4B        │  │  │ Phi-4-mini              │ │
│  │ (Fast completions)  │  │  └─────────────────────────┘ │
│  └────────────────────┘  │                               │
│                         │  ┌─────────────────────────┐  │
│  ┌────────────────────┐  │  │ Qwen3.5-9B             │ │
│  │ Granite-7B         │  │  │ (C/C++ projects)       │ │
│  │ (C/C++ projects)   │  │  └─────────────────────────┘ │
│  └────────────────────┘  │                               │
└─────────────────────────────────────────────────────────┘
```

### Resource Allocation Strategy

- **Active Models (CUDA):** Keep 1-2 models loaded for immediate use
- **Swapped Models (Vulkan):** Store 5-8 models for on-demand loading
- **RAM Spillover:** Use system RAM (~20 GB free) for additional models
- **Context Management:** Use smaller context windows for simple tasks

## 📋 Configuration Roadmap

### Phase 1: Foundation (Current)

- [x] Hardware analysis
- [x] Model inventory assessment
- [ ] Basic llama-swap configuration
- [ ] continue.dev integration
- [ ] Initial model loading strategy

### Phase 2: Optimization

- [ ] CUDA/Vulkan integration testing
- [ ] Model swapping performance benchmarks
- [ ] Context window optimization
- [ ] Quantization strategy refinement

### Phase 3: Advanced Features

- [ ] Multi-model concurrent loading
- [ ] Smart model selection based on task
- [ ] C/C++ specific optimizations
- [ ] Vision-language model integration

### Phase 4: Production

- [ ] Performance monitoring
- [ ] Resource usage optimization
- [ ] Documentation completion
- [ ] Best practices compilation

## 📊 Documentation Structure

### Technical Deep-Dives

- Configuration examples
- Architecture decisions
- Performance analysis
- Troubleshooting guides

### Performance Benchmarks

- Model loading times
- Generation speeds
- Memory usage patterns
- Swap operation timings

### Iteration Logs

- What was tried
- What worked
- What didn't work and why
- Lessons learned

### Quick Start Guides

- Common use cases
- Model selection guides
- Configuration templates

## 🔧 Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Inference Engine** | llama.cpp / vLLM | Model serving |
| **Swapping** | llama-swap | Model management |
| **IDE Integration** | continue.dev VSCode | Code intelligence |
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

This project will be documented iteratively. Each session will:

1. **Review** previous configurations and results
1. **Experiment** with new configurations
1. **Benchmark** performance improvements
1. **Document** findings and lessons learned
1. **Refine** based on results

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | Initial | Hardware analysis, model inventory, vision document |

______________________________________________________________________

*Last updated: 2026*
*Status: Phase 1 - Foundation*
*Next milestone: Basic llama-swap configuration*
