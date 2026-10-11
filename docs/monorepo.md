# Monorepo Reorganization Plan — llama-swap + LLM Manager

## How to read this document

This is a **living document** describing a proposed directory structure for iteration. The structure below is a starting point, not a final answer.

**Key principle from the monorepo community** (Luca Pette, "How to structure a monorepo"):

> The monorepo structure should **loosely reflect how teams/domains are organized** — not a rigid one-to-one mapping, but the structure should have organizational meaning. And **don't put technical choices at the top level** (e.g., grouping by language) — top-level folders should reflect product responsibilities.

That means: the top-level folders here reflect *what each subsystem does*, not the language it's written in. `src/` is the only technology-specific grouping, and it contains `llm_manager/` (the Python package).

## Current state (before Phase 2)

The project has grown organically over several sessions with no clear structure:

```text
local-config/
├── .agents/              # Generic AI agent definitions (renamed from .continue)
├── llama-swap/           # llama-swap config + benchmark scripts
├── llm_manager/          # Python package (Flask web app)
├── other_experiments/    # Experimental: inferhost, llamastash
├── context-verification/ # Model verification JSON metadata
├── nix/                  # treefmt-nix module + formatter bridge
├── pyproject.toml
├── uv.lock
├── .python-version
├── .envrc
├── flake.nix / flake.lock
├── main.py, tests/, templates/
└── other telemetry files (*.pyc, __pycache__)
```

## Recommended final structure (after moves)

```text
local-config/
├── flake.nix                          # Single flake entry point
├── flake.lock
├── .gitignore
├── README.md
├── docs/
│   ├── nix-formatting.md              # (existing) Nix formatting docs
│   └── monorepo.md                    # (new) Monorepo structure guide
├── .agents/                           # Generic AI agent definitions
│   ├── config.json
│   ├── environment.json
│   ├── README.md
│   └── agents/
│       ├── PROJECT-CONTRACT.md
│       ├── breaking-change-detector.md
│       ├── dependency-security-review.md
│       ├── error-message-quality.md
│       ├── input-validation.md
│       └── test-coverage.md
├── llama-swap/                        # Core: llama-swap config + benchmarks
│   ├── config.yaml                    # (moved from .continue-dev/)
│   ├── run_benchmarks.py
│   ├── run_llama_bench.sh
│   ├── README.md
│   ├── parameter-optimizer/
│   │   ├── batch-analyzer.py
│   │   ├── parameter-optimizer.py
│   │   └── README.md
│   └── read-models/
│       └── run.py
├── llm_manager/                       # Core: Python package (Flask web app)
│   ├── __init__.py
│   ├── config.py                      # Python config/constants module
│   ├── models.py                      # Python model definitions module
│   ├── main.py                        # Python CLI entry point
│   ├── configurator.py
│   ├── hardware.py
│   ├── hardware_spec.py
│   ├── loader.py
│   ├── model_paths.py
│   ├── quantization.py
│   ├── webapp.py
│   ├── templates/                     # Flask templates (package-local)
│   │   ├── base.html
│   │   ├── configs.html
│   │   ├── hardware.html
│   │   ├── index.html
│   │   └── models.html
│   └── tests/                         # Tests for the llm_manager package
│       └── test_llm_manager.py
├── other_experiments/                 # Experimental, not core stack
│   ├── inferhost/
│   │   ├── inferhost.env
│   │   ├── litellm.yaml
│   │   ├── llama-swap.yaml
│   │   └── models.toml
│   └── llamastash/
│       ├── AGENTS.md
│       ├── CONFIG-STRUCTURE.md
│       ├── INSTALL.md
│       ├── INTEGRATION-PATTERNS.md
│       ├── QUICK-START.md
│       ├── README.md
│       ├── llamastash-integration.md
│       ├── llamastash-integration.yaml
│       ├── llama-swap-integration.sh
│       ├── llamastash-integrate.sh
│       ├── update-yaml.py
│       └── logs/
│           └── models.md
├── context-verification/              # Model JSON metadata (verification)
│   └── *.json
└── nix/
    ├── treefmt.nix                    # Formatter declaration (blueprint)
    ├── formatter.nix                  # Bridge evaluator
    ├── devshell.nix                   # devShell definition
    └── checks/
        └── pre-commit-check.nix       # pre-commit check
```

## Key changes from previous proposal

1. **`templates/` is now inside `llm_manager/`** — package-local templates, no longer at the top level. `webapp.py` now points to `llm_manager/templates/` automatically.
1. **`config.py`, `models.py`, `main.py` are now inside `llm_manager/`** — all Python modules are part of the application. No orphaned root-level Python files remain.
1. **No `src/` rename** — the top-level `llm_manager/` package now holds everything (package modules + package-local templates + package tests). The `src/` rename proposed earlier is unnecessary because the package itself is the application.
1. **No root-level Python files left** — every `.py` file at the top level now lives inside a subdirectory (the `llm_manager/` package), except for the subdirectories with their own applications:
   - `llama-swap/` — its own application (config + benchmarks + optimizer scripts)
   - `other_experiments/` — subdirectory with its own applications (inferhost, llamastash)
1. **`.continue-dev/config.yaml` → `llama-swap/config.yaml`** — moved to the core llama-swap config location.

## Files to act on (remaining items)

| File | Action |
|---|---|
| `.continue/` | Delete (renamed to `.agents/`) |
| `.trunk/` | Delete (confirmed no longer used) |
| `.venv/` | Add to `.gitignore` — do not track |
| `nix/treefmt.nix` | Keep (blueprint requires separate module file) |
| `nix/formatter.nix` | Keep (blueprint requires separate bridge file) |
| `nix/checks/pre-commit-check.nix` | Keep (for flake checks) |
| `flake.nix` | Minor update to add new outputs |
| `pyproject.toml` | Keep at root, add `[project]` config for nix |
| `uv.lock` | Keep at root |
| `llama-swap/` | Keep as-is |
| `llm_manager/` | **All Python files consolidated inside** (no rename, just moves) |
| `main.py` | Moved into `llm_manager/` |
| `tests/` | Moved into `llm_manager/tests/` |
| `templates/` | Moved into `llm_manager/templates/` |
| `config.py` | Moved into `llm_manager/` |
| `models.py` | Moved into `llm_manager/` |
| `context-verification/` | Already at top level — keep |
| `other_experiments/` | Keep as "experimental" subdir |
| `docs/nix-formatting.md` | Keep + add `monorepo.md` |

## Nix dependency management

`llama-cpp-python` is available in nixpkgs. The plan:

1. **`nix/pyproject.nix`** — `buildPythonPackage` with `pyproject = true`
1. **`flake.nix`** — expose `packages`, `devShells`, `formatter`, `checks`
1. **`flake.nix`** uses `inputs.blueprint` to generate outputs

## Files that block this

None — the tree is fully reorganizable.

## Plan of action

### Phase 1 — Reposition (no file moves, just config)

1. Update `.gitignore` to exclude `.venv/`, `*.pyc`, `__pycache__/`, `.ruff_cache/`
1. Delete `.continue/` and `.trunk/` (they're dead/conflicting)
1. Update `docs/nix-formatting.md` to reference the new structure

### Phase 2 — Directory moves (current)

1. Move `templates/` → `llm_manager/templates/`
1. Move `main.py`, `config.py`, `models.py` → `llm_manager/`
1. Move `tests/` → `llm_manager/tests/`
1. Update `webapp.py` template path to `llm_manager/templates/`
1. Update `models.py` import from `config` → `from .config`
1. Update imports in `tests/` for the moved files

### Phase 3 — Nix module updates

1. Update `flake.nix` to add `packages`, `devShells`, `formatter`, `checks`
1. Create `nix/pyproject.nix` for Python package generation
1. Verify `nix fmt` still works

### Phase 4 — Documentation

1. Write `docs/monorepo.md` with the final structure
1. Update `README.md` top-level overview
1. Update `AGENTS.md` docs listing

## Risks

- `llama-cpp-python` is a source-build package — `nix develop` may take a long time
- `.venv/` must be removed before moving files (or files reference venv paths)
- `other_experiments/llamastash/` has hardcoded paths that won't work elsewhere

## Question for you

1. **Do you want to keep `other_experiments/llamastash/`?** It's not portable (hardcoded absolute paths). If you want a clean monorepo, I'd remove it or mark it clearly as experimental.
1. **Do you want to drop `other_experiments/` entirely?** It's experimental and not part of the core stack. Keeping it is fine, but it adds noise.

## Recommendation

The cleanest approach:

- Delete `.continue/` and `.trunk/`
- Add `.venv/` to `.gitignore`
- Keep `llm_manager/` as the single Python package (all modules + templates + tests inside)
- Move `main.py`, `config.py`, `models.py` into `llm_manager/`
- Move `.continue-dev/config.yaml` → `llama-swap/config.yaml`
- Keep `llama-swap/`, `other_experiments/`, `context-verification/` as-is
- Update `flake.nix` and `docs/nix-formatting.md`
- Keep `other_experiments/` but mark it as experimental
