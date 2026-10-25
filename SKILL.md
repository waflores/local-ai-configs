# llama-swap Agent Skills

> **For Hermes Agent only.** For generic AI harnesses (pi.dev, Codex, OpenCode,
> Claude), read `AGENTS.md` or `CLAUDE.md` at the repo root.

## Overview

This project uses **llama-swap** as the primary interface for all AI agent
interactions. The system provides high-performance model swapping infrastructure
leveraging NVIDIA RTX 5070 Max-Q GPU for optimal inference performance.

## Core Capabilities

### Model Management

- **Model Loading/Unloading** - Swap between models on-demand
- **Performance Benchmarking** - Measure inference speed and latency
- **Resource Monitoring** - Track VRAM, RAM, and swap usage
- **Health Checking** - Verify model availability and readiness

### Inference Operations

- **Chat Completion** - Interactive conversations
- **Code Generation** - Python, C, C++ code completion
- **Reasoning Tasks** - Complex problem solving
- **Context Management** - Handle long-context tasks efficiently

## Available Commands

### `/nix-check` - Run Nix Health Check

```bash
nix flake show && nix flake check && nix fmt --check
```

**Purpose:** Verify the Nix flake is healthy (must succeed before committing).

### `/health` - Health Check

```bash
curl http://127.0.0.1:10001/health
```

### `/list-models` - List Loaded Models

```bash
curl http://127.0.0.1:10001/v1/models
```

### `/load <model-name>` - Load a Specific Model

```bash
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IBM Granite 4 Tiny",
    "path": "/home/waflores/.lmstudio/models/lmstudio-community/IBM-Granite-4-Tiny-GGUF/granite-4-h-tiny-Q4_K_M.gguf",
    "ttl": 600
  }'
```

### `/unload <model-name>` - Unload a Model

```bash
curl -X DELETE http://127.0.0.1:10001/v1/models/IBM Granite 4 Tiny
```

### `/bench <model-name>` - Benchmark a Model

```bash
/home/waflores/DevFolder/ai/local-config/llama-swap/run_benchmarks.py \
  --model <model-name> \
  --output benchmarks/results.json
```

NOTE: `run_benchmarks.py` and `run_llama_bench.sh` are placeholders. See
`llama-swap/README.md` for the benchmark status.

### `/models` - List Available Models

```bash
curl http://127.0.0.1:10001/v1/models
```

### `/nix-check` command is for Hermes Agent only. See `AGENTS.md` for

generic, platform-neutral repo documentation.

## Nix Commands

### Build

```bash
nix build .#packages.x86_64-linux.local-config
```

### Develop Shell

```bash
nix develop .#default
```

### Format

```bash
nix fmt
```

### Check

```bash
nix flake check
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Model Swap Time | < 2s |
| Generation Speed (7B) | > 10 t/s |
| VRAM Utilization | < 70% |
| Context Efficiency | > 80% |

## Model Inventory

| Model | Parameters | Size (Q4_K_M) | Device |
|-------|------------|---------------|--------|
| CodeLlama-7B-Instruct | 7B | ~4 GB | CUDA0 |
| Meta-Llama-3.1-8B-Instruct | 8B | ~5 GB | CUDA0 |
| Qwen3.5-9B-GGUF | 9B | ~5.6 GB | CUDA0 |
| Qwen3.6-27B-GGUF | 27B | ~16.5 GB | CUDA0 |
| DeepSeek-R1-0528-Qwen3-8B-GGUF | 8B | ~5 GB | CUDA0 |
| Ministral-3-3B-Instruct-2512-GGUF | 3B | ~2 GB | CUDA0 |
| Ministral-3-14B-Reasoning-2512-GGUF | 14B | ~8 GB | CUDA0 |
| Mistral-Nemo-Instruct-2407-GGUF | 13B | ~6.5 GB | CUDA0 |
| Phi-4-mini-reasoning-GGUF | 3B | ~2.5 GB | CUDA0 |
| Phi-4-reasoning-plus-GGUF | 13B | ~9 GB | CUDA0 |
| gemma-4-E4B-it-GGUF | 8B | ~5.3 GB | CUDA0 |
| NVIDIA-Nemotron-3-Nano-4B-GGUF | 4B | ~2.8 GB | CUDA0 |
| Devstral-Small-2-24B-Instruct-2512-GGUF | 24B | ~14 GB | CUDA0 |
| LFM2-24B-A2B-GGUF | 24B | ~14.4 GB | CUDA0 |
| Qwen3-VL-8B-Instruct-GGUF | 8B | ~5 GB | CUDA0 |
| olmOCR-2-7B-1025-GGUF | 8B | ~4.7 GB | CUDA0 |
| granite-4-h-tiny | 7B | ~4 GB | CUDA0 |

## Quick Start

1. **Start llama-swap:**

```bash
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001
```

2. **Health check:**

```bash
curl http://127.0.0.1:10001/health
```

3. **Load a model:**

```bash
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{"name": "CodeLlama-7B-Instruct", "path": "/home/waflores/.lmstudio/models/lmstudio-community/CodeLlama-7B-Instruct-GGUF/CodeLlama-7B-Instruct-Q4_K_M.gguf", "ttl": 600}'
```

4. **Run benchmarks:**

```bash
/home/waflores/DevFolder/ai/local-config/llama-swap/run_benchmarks.py \
  --model CodeLlama-7B-Instruct \
  --output benchmarks/results.json
```

## Configuration Files

| File | Purpose |
|------|---------|
| llama-swap/config.yaml | llama-swap model definitions (22 models) |
| flake.nix | Nix flake (x86_64-linux only) |
| pyproject.toml | Python project metadata (uv) |
| nix/treefmt.nix | treefmt-nix formatter declaration |
| nix/formatter.nix | treefmt-nix bridge |
| nix/pyproject.nix | buildPythonPackage builder |
| nix/packages/default.nix | blueprint packages output |
| nix/devshells/default.nix | blueprint devShells output |
| nix/checks/pre-commit-check.nix | pre-commit check wired to treefmt |
| .agents/config.json | Machine-readable project authority |

## Core Rules

1. **Always run `nix flake show`, `nix flake check`, and `nix fmt` before declaring work complete.**
1. **Never commit secrets** — replace API keys, tokens, and credentials with `[REDACTED]`.
1. **Keep Python code PEP 8** — Ruff rules are centralized in pyproject.toml.
1. **Platforms:** x86_64-linux only. No cross-compilation.
1. **Model quantization:** prefer Q4_K_M or Q5_K_M.
