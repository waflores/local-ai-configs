# llama-swap Configuration - High-Performance Local LLM Inference

## 🤖 Machine-Readable Header

```yaml
config:
  name: llama-swap
  core_stack:
    - llama-server
    - llama-swap
    - nix
  authority:
    folder: ".agents"
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

## 📁 Repository Structure

This is a monorepo centered on managing `llama-swap` configurations for a local LLM, with `nix` managing third-party dependencies where possible.

```text
local-config/
├── .agents/                  # Generic AI agent definitions
├── llama-swap/               # llama-swap config + benchmark scripts
├── llm_manager/              # Python package (Flask web app + tests)
├── other_experiments/        # Experimental: inferhost, llamastash
├── context-verification/     # Model verification JSON metadata
├── nix/                      # treefmt-nix module + formatter bridge
├── docs/                     # Documentation
├── flake.nix                 # Single flake entry point
├── pyproject.toml            # Python project metadata (uv/uv2nix)
├── .coverage                 # Coverage data (pytest-cov)
└── htmlcov/                  # HTML coverage reports
```

## ⚙️ Configuration

| File | Purpose |
|------|---------|
| `flake.nix` | Single flake entry point; restricted to `x86_64-linux` only |
| `pyproject.toml` | Python project metadata (name, version, dependencies) |
| `nix/treefmt.nix` | treefmt-nix module — declares formatters (ruff, ruff-format, nixfmt, etc.) |
| `nix/formatter.nix` | Bridge evaluator for treefmt-nix |
| `nix/packages/default.nix` | Blueprint packages output (`packages.local-config`) |
| `nix/devshells/default.nix` | Blueprint devShells output |
| `nix/pyproject.nix` | `buildPythonPackage` builder for the Python package |
| `.agents/` | Generic AI agent definitions and project intent layer |
| `llama-swap/config.yaml` | llama-swap model configuration |

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

### Model Discovery

Models are discovered via two complementary mechanisms:

1. **Static verification metadata** (`context-verification/*.json`) — 22 non-mmproj JSON files provide model metadata (name, size, context, quantization tags).
1. **On-disk discovery** (`loader.discover_models_on_disk()`) — the LLM manager walks the models directory (`/home/waflores/.lmstudio/models`) for live `.gguf` files, computing sizes dynamically.

The `discover_models()` function combines both sources: JSON metadata provides the registry, and on-disk discovery provides live file paths. Each model's path is resolved via:

1. **config.yaml path override** (if the model is listed in `llama-swap/config.yaml` with a `model_path`)
1. **Directory mapping** (`model_directory_mapping()`) — case-insensitive lookup of model directory → canonical path
1. **Directory scanning** (`_finalize_residual_paths()`) — walks the full models tree to find matching GGUF files, handling quantized filenames (e.g., `Q4_K_M`, `Q3_K_L`, `Q8_0`)

### Full Model Inventory

| Model | Parameters | Size (Q4_K_M / Q8_0) | Use Case |
|-------|------------|---------------------|----------|
| Codellama-7B-Instruct | 7B | ~4 GB | Python, general coding |
| DeepSeek-R1-0528-Qwen3-8B | 8B | ~5 GB | Reasoning |
| Devstral-Small-2-24B-Instruct-2512 | 24B | ~14 GB | Advanced reasoning |
| Gemma-4-E4B-it | 8B | ~5.3 GB | General tasks |
| Granite-4.0-h-tiny | 7B | ~4 GB | IBM's code model |
| LFM2-24B-A2B | 24B | ~14.4 GB | Embeddings |
| Meta-Llama-3.1-8B-Instruct | 8B | ~5 GB | General tasks |
| Ministral-3-14B-Reasoning-2512 | 14B | ~8 GB | Reasoning tasks |
| Ministral-3-3B-Instruct-2512 | 3B | ~2 GB | Fast completions |
| Mistral-Nemo-Instruct-2407 | 13B | ~6.5 GB | Balanced performance |
| NVIDIA-Nemotron-3-Nano-4B | 4B | ~2.8 GB | NVIDIA-optimized |
| olmOCR-2-7B-1025 | 8B | ~4.7 GB | OCR tasks |
| Phi-4-mini-reasoning | 3B | ~2.5 GB | Lightweight tasks |
| Phi-4-reasoning-plus | 13B | ~9 GB | Advanced reasoning |
| Qwen3-4B-Thinking-2507 | 4B | ~4 GB | Thinking/reasoning |
| Qwen3.5-9B | 9B | ~5.6 GB | General tasks |
| Qwen3.6-27B | 27B | ~16.5 GB | Advanced tasks |
| Qwen3-VL-8B-Instruct | 8B | ~5 GB | Vision-language |
| rnj-1-instruct | - | - | General tasks |
| zerank-1-small | - | - | Reranking |
| zerank-2 | - | - | Embeddings |
| llama2:latest | 7B | ~3.6 GB | Base model reference (no disk path) |

*Note: `llama2:latest` is a base-model reference from verification metadata with no installed `.gguf` file, so it has no resolved disk path.*
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
- [x] Test coverage expansion (70% → 95%) — 187 tests across `test_webapp.py`
- [x] Webapp front-page context (hardware + Configuration Summary via `index()` route)
- [x] Fully qualified model paths (config-key resolution + directory mapping + directory scanning)
- [x] LLm Manager CLI: `uv run python -m llm_manager.webapp` (dev) or `uv run python -m llm_manager.main` (CLI)

### Phase 2: Directory & Admin Portal (Completed)
- [x] Admin panel for the directories (`/admin`)
- [x] Directory configuration (`/dirs` API: add/delete)
- [x] Directory picker widget (native folder picker via `webkitdirectory` input)
- [x] Consolidated admin portal with model counts per directory

### Phase 3: Completion (Completed)
- [x] Per-model llama.cpp tuning page (`/tuning`)
- [x] Admin portal consolidation (`/admin`)
- [x] Directory picker widget (native folder picker via `webkitdirectory` input)
- [x] Database persistence of discovered models (`config_store.py`)
- [x] Disk crawling for `.gguf` model files (`loader.py: discover_models_on_disk()`)
- [x] Models list regenerated fresh on every request (`discover_models()`)
- [x] `POST /reload` forces full refresh

## 📚 Documentation

### Configuration Files

- **`llama-swap/config.yaml`** - Main model configuration
- **`SKILL.md`** - Agent commands and capabilities
- **`README.md`** - This file - Project overview
- **`AGENTS.md`** - Testing agent responsibilities
- **`docs/nix-formatting.md`** - Nix formatting infrastructure (treefmt-nix, nix fmt, ruff)
- **`docs/monorepo.md`** - Monorepo structure guide

### Benchmarks

- **`llama-swap/run_benchmarks.py`** - Performance testing
- **`llama-swap/run_llama_bench.sh`** - Shell script wrapper
- **`llama-swap/benchmarks/`** - Results directory

### Documentation Standards

- Clear problem statements
- Configuration details
- Expected vs actual results
- Actionable recommendations

### Phase 3: Completion (Current)
- [x] Per-model llama.cpp tuning page (`/tuning`)
- [x] Admin portal consolidation (`/admin`)
- [x] Directory picker widget (native folder picker via `webkitdirectory` input)
- [x] Database persistence of discovered models (`config_store.py`)
- [x] Disk crawling for `.gguf` model files (`loader.py: discover_models_on_disk()`)
- [x] Models list regenerated fresh on every request (`discover_models()`)
- [x] `POST /reload` forces full refresh

## 📚 Documentation

### Configuration Files

- **`llama-swap/config.yaml`** - Main model configuration
- **`SKILL.md`** - Agent commands and capabilities
- **`README.md`** - This file - Project overview
- **`AGENTS.md`** - Testing agent responsibilities
- **`docs/nix-formatting.md`** - Nix formatting infrastructure (treefmt-nix, nix fmt, ruff)
- **`docs/monorepo.md`** - Monorepo structure guide

### Benchmarks

- **`llama-swap/run_benchmarks.py`** - Performance testing
- **`llama-swap/run_llama_bench.sh`** - Shell script wrapper
- **`llama-swap/benchmarks/`** - Results directory

### Documentation Standards

- Clear problem statements
- Configuration details
- Expected vs actual results
- Actionable recommendations

### API Documentation (FastAPI)

The FastAPI app (`llm_manager.api_docs`) documents the JSON API that the Flask web app
exposes, reusing the same domain objects (`discover_models()`, `build_config()`,
`save_tuning_profile()`, `add_dir()`, ...) so the docs mirror what the UI does.

**Two ways to browse the docs:**

1. **Flask app (recommended, same server)** — the Flask app proxies the docs to
   `/api-docs` (iframe to the FastAPI Swagger UI):

   ```bash
   cd /home/waflores/DevFolder/ai/local-config
   uv run python -m llm_manager.webapp        # Flask (port 5000)
   ```

   Then open **http://127.0.0.1:5000/api-docs**. The page embeds the Swagger UI
   and links to ReDoc (both served by the FastAPI app on port 5001).

2. **FastAPI app (standalone)** — run the FastAPI docs app directly:

   ```bash
   cd /home/waflores/DevFolder/ai/local-config
   uv run uvicorn llm_manager.api_docs:app --port 5001
   ```

   Then open **http://127.0.0.1:5001/docs** (Swagger UI) or
   **http://127.0.0.1:5001/redoc** (ReDoc).

**Endpoints documented** (all under the above URLs):

|| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/models` | Unified model registry |
| `GET`  | `/hardware` | Detected hardware |
| `GET`  | `/configs` | Last persisted configuration |
| `GET`  | `/configs/export.json` | Config as JSON |
| `GET`  | `/configs/export.yaml` | Config as YAML (download) |
| `POST` | `/tuning` | Save a per-model llama.cpp tuning profile |
| `POST` | `/dirs` | Add or delete a model directory (`action`, `path`) |
| `POST` | `/reload` | Refresh the model registry + hardware |
|--------|------|-------------|
| `GET` | `/models` | Unified model registry |
| `GET` | `/hardware` | Detected hardware |
| `GET` | `/configs` | Last persisted configuration |
| `GET` | `/configs/export.json` | Config as JSON |
| `GET` | `/configs/export.yaml` | Config as YAML (download) |
| `POST` | `/tuning` | Save a per-model llama.cpp tuning profile |
| `POST` | `/dirs` | Add or delete a model directory (`action`, `path`) |
| `POST` | `/reload` | Refresh the model registry + hardware |

The FastAPI app is also documented by its own auto-generated spec at
`/openapi.json` (used by both Swagger UI and ReDoc).

| Component | Technology | Purpose |
|-----------|------------|---------|
| Inference Engine | llama.cpp | Model serving |
| Swapping | llama-swap | Model management |
| GPU Backend | CUDA (RTX 5070) | Primary inference |
| Secondary GPU | Vulkan (Intel) | Model storage |
| CPU Offload | OpenBLAS | Fallback computation |

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
| 1.1 | 2026-10-15 | Test coverage expanded to 95% (181 tests); webapp front-page context; fully qualified model paths; LLm Manager CLI documented |
| 1.0 | 2026-06-20 | Initial configuration with 22 models, benchmarking infrastructure |

______________________________________________________________________

*Last updated: 2026-10-16*
*Status: Phase 3 - Completion*
*Next milestones: Cleanup; webapp usability verification*

## Notes

We can size up the models by running this command:

```bash
llama-fit-params --model ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf -lv 5 --log-colors off 2>&1 > /dev/null | grep -vP '^\S*\s+D'

# This example code seems to not be performant - but an example nonetheless
llama-gguf ~/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf r n

find ~/.lmstudio/models/ -path '*/mmproj*' -prune -o -name '*.gguf' -print -exec llama-fit-params -lv 1 --model "{}" --fit-target 0 \;
```
