# projdoc/

The project corpus index: a file map, a domain map, and a recommended reading order.
Use this to navigate the repository without reading everything.

## File map

| Path | Role |
|------|------|
| `llama-swap/config.yaml` | Model config (6 models) + benchmark scripts |
| `llama-swap/run_benchmarks.py` | Benchmark harness — placeholder to be retired or replaced |
| `llama-swap/run_llama_bench.sh` | Shell wrapper around benchmarks — not a real pipeline |
| `llm_manager/` | Python package: registry, hardware, profiles, web UI, tests |
| `nix/treefmt.nix` | treefmt-nix module: declares formatters |
| `nix/formatter.nix` | Bridge: extracts the treefmt wrapper binary |
| `nix/packages/default.nix` | Blueprint packages output |
| `nix/devshells/default.nix` | Blueprint devShell output |
| `nix/checks/pre-commit-check.nix` | Pre-commit check wired to treefmt |
| `context-verification/*.json` | Source-of-truth model metadata (22 files) |
| `.agents/config.json` | Machine-readable project authority |
| `.agents/README.md` | Intent layer |
| `.agents/agents/*.md` | Agent instructions (PROJECT-CONTRACT, etc.) |
| `flake.nix` | Single flake entry point (x86_64-linux only) |
| `pyproject.toml` | Python metadata (uv) + Ruff config |

## Domain map

| Domain | Files | Questions it answers |
|--------|-------|----------------------|
| Model registry | `llama-swap/config.yaml`, `context-verification/*.json`, `llm_manager/loader.py` | What models exist, where they live, their sizes/contexts |
| Model discovery | `llm_manager/loader.py`, `llm_manager/model_paths.py` | How paths are resolved at runtime |
| Hardware | `llm_manager/hardware.py`, `hardware_spec.py` | What the machine reports (VRAM, RAM, CPU) |
| Profiles | `llm_manager/configurator.py`, `models.py`, `config_store.py` | How configs are generated, persisted, exported |
| Web UI | `llm_manager/webapp.py`, `templates/` | What the user sees and does |
| API docs | `llm_manager/api_docs.py` | The FastAPI OpenAPI spec |
| Nix packaging | `nix/*.nix`, `flake.nix` | Reproducible build, dev shell, formatting |
| Model registry | `llama-swap/config.yaml` (6 models) + `context-verification/*.json` (22 source-of-truth files) |
| Model discovery | `llm_manager/loader.py`, `llm_manager/model_paths.py` | How paths are resolved at runtime |
| Benchmarking | `llama-swap/run_benchmarks.py`, `run_llama_bench.sh` | Performance measurement — placeholder/wrapper, see note below |

The key facts: `config.yaml` defines 6 models; `context-verification/*.json` is the 22-file source of truth for `llm_manager`.

## Note on benchmarking

`llama-swap/run_benchmarks.py` and `run_llama_bench.sh` are **placeholder/wrapper**, not a real benchmark pipeline yet. The performance targets (`docs/llama-swap.md`) are the contract; the pipeline is the first item in the re-scoped CMMI roadmap. See `.hermes/plans/2026-09-24_133545-cmmi-5-roadmap.md` and `.hermes/plans/2026-09-24_134500-benchmarking-infrastructure-report.md` for the current implementation plan.

## Reading order

1. `docs/README.md` — where to look
1. `llama-swap/README.md` — the user-facing llama-swap docs
1. `docs/llm_manager.md` — the Python app
1. `docs/nix-formatting.md` — Nix + formatting
1. `docs/monorepo.md` — structure and phase plan
1. `docs/inference-tuning.md` — performance math
