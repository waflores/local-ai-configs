# llama-swap Configuration — Agent Documentation

## 🤖 Primary Agent: Hermes Agent

This repository is optimized for **Hermes Agent** (Nous Research). When working in this repo, Hermes Agent is the primary agent — it reads `.hermes.md`, `AGENTS.md`, `SKILL.md`, and `docs/` to understand project context and perform tasks.

### Hermes Agent — Project Context

- **Repo root:** /home/waflores/DevFolder/ai/local-config
- **Hermes home:** /home/waflores/.hermes/ (profiles, skills, memory, plugins)
- **Hermes skills:** /home/waflores/.hermes/skills/autonomous-ai-agents/hermes-agent/
- **Hermes docs:** https://hermes-agent.nousresearch.com/docs/

### Hermes Agent — Quick Reference

```bash
# Health check / doctor
hermes doctor

# Python environment (uv)
uv run python -c "print('ok')"

# Nix (x86_64-linux only)
nix flake show
nix flake check
nix fmt
nix build .#packages.x86_64-linux.local-config
nix develop .#default

# llama-swap (running)
curl http://127.0.0.1:10001/health
curl http://127.0.0.1:10001/v1/models
```

### Hermes Agent — Core Rules

1. **Always run `nix flake show`, `nix flake check`, and `nix fmt` before declaring work complete.**
1. **Never commit secrets** — replace API keys, tokens, and credentials with `[REDACTED]`.
1. **Keep Python code PEP 8** — Ruff rules are centralized in pyproject.toml.
1. **Platforms:** x86_64-linux only. No cross-compilation.
1. **Model quantization:** prefer Q4_K_M or Q5_K_M.

______________________________________________________________________

## 📁 Repository Structure

```text
local-config/
├── .agents/                          # Generic AI agent definitions
│   ├── config.json                   # Machine-readable project authority
│   ├── environment.json
│   ├── README.md                     # Intent layer documentation
│   └── agents/
│       ├── PROJECT-CONTRACT.md
│       ├── breaking-change-detector.md
│       ├── dependency-security-review.md
│       ├── error-message-quality.md
│       ├── input-validation.md
│       └── test-coverage.md
├── llama-swap/                       # llama-swap config + benchmark scripts
│   ├── config.yaml                   # Model definitions (22 models)
│   ├── run_benchmarks.py
│   ├── run_llama_bench.sh
│   ├── README.md
│   ├── parameter-optimizer/
│   │   ├── batch-analyzer.py
│   │   ├── parameter-optimizer.py
│   │   └── README.md
│   └── read-models/run.py
├── llm_manager/                      # Python package (Flask web app)
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── main.py
│   ├── configurator.py
│   ├── hardware.py
│   ├── hardware_spec.py
│   ├── loader.py
│   ├── model_paths.py
│   ├── quantization.py
│   ├── webapp.py
│   ├── templates/                    # Flask templates (package-local)
│   └── tests/                        # Tests for llm_manager
├── other_experiments/                # Experimental: inferhost, llamastash
├── context-verification/             # Model JSON metadata
├── nix/                              # treefmt-nix module + formatter bridge
│   ├── pyproject.nix                 # buildPythonPackage builder
│   ├── packages/default.nix          # blueprint packages output
│   ├── devshells/default.nix         # blueprint devShells output
│   ├── formatter.nix                 # bridge to treefmt-nix
│   ├── treefmt.nix                   # formatter declaration
│   └── checks/
│       └── pre-commit-check.nix
├── docs/
│   ├── nix-formatting.md             # Nix formatting infrastructure
│   └── monorepo.md                   # Monorepo reorganization plan
├── flake.nix                         # Single flake entry point
├── flake.lock
├── pyproject.toml                    # Python project metadata
├── uv.lock
├── .python-version
├── .envrc
├── README.md
└── SKILL.md                          # Agent commands and capabilities
```

### Key Files

| File | Purpose |
|------|---------|
| llama-swap/config.yaml | 22 model definitions (CUDA0 active, Vulkan0/Vulkan1 swapped) |
| flake.nix | Single flake entry point (x86_64-linux only) |
| pyproject.toml | Python project metadata (uv/uv2nix) |
| nix/pyproject.nix | buildPythonPackage builder |
| nix/treefmt.nix | treefmt-nix module (formatter declaration) |
| nix/formatter.nix | treefmt-nix bridge |
| nix/packages/default.nix | blueprint packages output |
| nix/devshells/default.nix | blueprint devShells output |
| nix/checks/pre-commit-check.nix | pre-commit check wired to treefmt |
| .agents/config.json | Machine-readable project authority |
| SKILL.md | Agent commands and capabilities |

______________________________________________________________________

## 🦊 llama-swap — Local LLM Management

### Overview

llama-swap manages 22 GGUF models for local LLM inference on **NVIDIA RTX 5070 Max-Q**. It uses llama-server for inference with CUDA (active) and Vulkan (swapped) backends.

### Hardware

| Device | Type | Memory | Role |
|--------|------|--------|------|
| CUDA0 | NVIDIA RTX 5070 | 7.7 GB | Active inference |
| Vulkan0 | Intel (ARL) | 23.6 GB | Model storage |
| Vulkan1 | NVIDIA RTX 5070 | 8.1 GB | Fallback |

### Model Inventory

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
| zerank-1-small-gguf | — | — | — |
| zerank-2-gguf | — | — | — |
| rnj-1-instruct-GGUF | — | — | — |

### Performance Targets

| Metric | Target |
|--------|--------|
| Model Swap Time | < 2s |
| Generation Speed (7B) | > 10 t/s |
| VRAM Utilization | < 70% |
| Context Efficiency | > 80% |

### Command Reference

```bash
# Start llama-swap
/home/waflores/bin/llama-swap \
  --config /home/waflores/DevFolder/ai/local-config/llama-swap/config.yaml \
  --listen 127.0.0.1:10001

# Health check
curl http://127.0.0.1:10001/health

# List models
curl http://127.0.0.1:10001/v1/models

# Load a model
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{"name": "CodeLlama-7B-Instruct", "path": "/home/waflores/.lmstudio/models/lmstudio-community/CodeLlama-7B-Instruct-GGUF/CodeLlama-7B-Instruct-Q4_K_M.gguf", "ttl": 600}'

# Unload a model
curl -X DELETE http://127.0.0.1:10001/v1/models/CodeLlama-7B-Instruct

# Run benchmarks
/home/waflores/DevFolder/ai/local-config/llama-swap/run_benchmarks.py \
  --model CodeLlama-7B-Instruct \
  --output benchmarks/results.json
```

______________________________________________________________________

## 🧰 CLI Reference — Nix

### flake outputs (x86_64-linux only)

| Output | Command |
|--------|---------|
| packages | nix build .#packages.x86_64-linux.local-config |
| devShells | nix develop .#default |
| formatter | nix fmt |
| checks | nix flake check |

### Commands

| Command | Purpose |
|---------|---------|
| nix flake show | Show flake outputs (must succeed before committing) |
| nix flake check | Run all flake checks (must pass) |
| nix fmt | Run treefmt-nix (runs ruff-check + ruff-format) |
| nix build .#packages.x86_64-linux.local-config | Build the Python package |
| nix develop .#default | Enter the dev shell |

______________________________________________________________________

## 🔍 Agent Tool Discovery Order

When an agent needs to find tools or information, search in this order:

1. **.agents/ directory** — agent definitions, config, environment:
   - agents/ — agent definitions (PROJECT-CONTRACT, breaking-change-detector, dependency-security-review, error-message-quality, input-validation, test-coverage)
   - config.json — machine-readable project authority
   - environment.json — environment configuration
   - README.md — intent layer documentation
1. **AGENTS.md** — this file (primary intent layer)
1. **README.md** — project vision, goals, roadmap
1. **SKILL.md** — agent commands and capabilities
1. **docs/**:
   - nix-formatting.md — Nix formatting infrastructure
   - monorepo.md — monorepo structure and phase plan
1. **Configuration files**:
   - flake.nix — Nix flake
   - pyproject.toml — Python project
   - llama-swap/config.yaml — llama-swap model definitions

______________________________________________________________________

## 👥 Agent Roles

| Role | Primary | Responsibilities |
|------|---------|------------------|
| **Hermes Agent** | Primary | Execute tasks, read documentation, run benchmarks, manage the monorepo |
| **Lead Developer** | Will | Vision, configuration architecture, decision-making |
| **Research Assistant** | — | Configuration research, benchmarking, documentation |
| **Configuration Analyst** | — | Hardware-aware model loading, quantization optimization |
| **Performance Benchmarking** | — | Speed tests, swap timings, memory analysis, performance reports |
| **Documentation Agent** | — | Technical writing, deep-dives, quick-start guides |

______________________________________________________________________

## 📋 Agent Responsibilities Matrix

| Task | Hermes | Lead | Research | Config | Benchmark | Doc |
|------|--------|------|----------|--------|-----------|-----|
| Define vision | ✅ | ✅ | | | | |
| Select models | ✅ | ✅ | | | | |
| Configure system | ✅ | ✅ | | ✅ | | |
| Run benchmarks | ✅ | | | | ✅ | |
| Analyze results | ✅ | ✅ | | | ✅ | |
| Write docs | ✅ | | ✅ | | | ✅ |
| Make decisions | ✅ | ✅ | | | | |

______________________________________________________________________

## 🚀 Collaboration Workflow

### Configuration Iteration Cycle

1. **[Hermes]** Read context: .hermes.md, AGENTS.md, SKILL.md, docs/
1. **[Lead]** Define requirements and performance goals
1. **[Hermes + Research]** Research configurations, benchmark alternatives
1. **[Hermes]** Configure: update llama-swap/config.yaml, flake.nix, pyproject.toml
1. **[Hermes + Benchmark]** Run benchmarks, measure metrics
1. **[Documentation]** Update docs, write iteration log
1. **[Lead]** Review outcomes, decide next steps

### Decision Making Process

#### Level 1 — Quick Decisions (Immediate)

- Model selection for specific tasks
- Context window sizing
- Temperature settings
- **Agents:** Hermes + Lead approval

#### Level 2 — Medium Decisions (Short-term)

- Model swapping strategies
- Resource allocation changes
- Quantization level adjustments
- **Agents:** Research + Benchmark + Lead approval

#### Level 3 — Major Decisions (Long-term)

- Backend selection (llama.cpp vs vLLM)
- Architecture changes
- Significant resource reallocation
- **Agents:** All agents + Lead decision

______________________________________________________________________

## 📊 Performance Tracking

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Model Swap Time | < 2s | TBD | ⏳ |
| Generation Speed (7B) | > 10 t/s | TBD | ⏳ |
| VRAM Utilization | < 70% | TBD | ⏳ |
| Context Efficiency | > 80% | TBD | ⏳ |

______________________________________________________________________

## 🎓 Knowledge Management

### Documentation Categories

1. **Configuration Guides**
   - llama-swap setup
   - Nix flake configuration
   - Model loading strategies
1. **Performance Analysis**
   - Benchmark results
   - Model comparisons
   - Optimization tips
1. **Troubleshooting**
   - Common issues
   - Error resolutions
   - Debugging guides
1. **Best Practices**
   - Resource management
   - Model selection
   - Performance tuning

### Knowledge Sources

- Primary: This project documentation
- Secondary: llama-swap docs, Nix docs
- Tertiary: llama.cpp documentation, community forums

______________________________________________________________________

## 🔄 Iteration Protocol

### Session Structure

**Pre-Session:**

1. Review previous iteration logs
1. Check performance benchmarks
1. Identify optimization opportunities

**During Session:**

1. Execute planned experiments
1. Collect performance data
1. Document findings immediately

**Post-Session:**

1. Update documentation
1. Write iteration log entry
1. Plan next session

### Documentation Standards

**Iteration Log Entries Must Include:**

- Date and session number
- Objective of this iteration
- Configuration changes made
- Performance metrics collected
- Issues encountered
- Lessons learned
- Next steps planned

**Technical Deep-Dive Requirements:**

- Clear problem statement
- Configuration details
- Expected vs actual results
- Analysis of findings
- Recommendations

**Benchmark Report Requirements:**

- Test setup description
- Models tested
- Metrics collected
- Comparison tables
- Performance rankings

______________________________________________________________________

## ✅ Success Criteria

### Individual Agent Success

| Agent | Criteria |
|-------|----------|
| **Hermes Agent** | ✅ System configured and operational; ✅ Performance meets targets; ✅ Documentation comprehensive; ✅ Iteration process effective |
| **Lead Developer** | ✅ Configuration architecture sound; ✅ Benchmarks reviewed before decisions; ✅ Practical constraints respected |
| **Research Assistant** | ✅ Configuration options explored; ✅ Best practices documented; ✅ Performance analysis complete; ✅ Recommendations actionable |

**All Agents:**

- ✅ Clear communication maintained
- ✅ Documentation up-to-date
- ✅ Performance tracked
- ✅ Lessons captured

______________________________________________________________________

## 📈 Evolution Path

### Phase 1: Foundation (Complete)

- ✅ Basic configuration established
- ✅ Documentation comprehensive
- ✅ Nix flake simplified (x86_64-linux only)

### Phase 2: Optimization (In Progress)

- 🔄 Refine model swapping strategy
- 🔄 Optimize resource utilization
- 🔄 Improve performance metrics

### Phase 3: Advanced

- 🔄 Implement intelligent model selection
- 🔄 Add multi-model support
- 🔄 Enhance C/C++ optimizations

### Phase 4: Production

- 🔄 Achieve production-ready configuration
- 🔄 Document best practices
- 🔄 Create deployment guides

______________________________________________________________________

## ⚙️ Configuration Files

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
| SKILL.md | Agent commands and capabilities |

______________________________________________________________________

## 🔄 Continuous Improvement

### Regular Review Cadence

**Daily:**

- Check performance metrics
- Update iteration logs
- Address immediate issues

**Weekly:**

- Review benchmark results
- Plan next experiments
- Update documentation

**Monthly:**

- Evaluate overall progress
- Review success criteria
- Plan major improvements

### Feedback Loops

**From Benchmarks → Configuration:**

- Performance data informs model selection
- Latency metrics guide optimization
- Memory usage patterns reveal bottlenecks

**From Documentation → Knowledge:**

- Iteration logs build expertise
- Deep-dives create reference material
- Troubleshooting guides help future sessions
