# Monorepo Reorganization Plan — llama-swap + LLM Manager

## Current state

The project has grown organically over several sessions with no clear structure:

```
local-config/
├── .agents/         # Generic AI agent definitions (renamed from .continue)
├── .direnv/         # direnv state (not tracked)
├── .venv/           # Python venv (3,741 files — do not track)
├── .ruff_cache/     # Ruff caches from multiple runs
├── llama-swap/      # llama-swap config + benchmark scripts
├── llm_manager/     # Python package (Flask web app)
├── other_experiments/  # Experimental: inferhost, llamastash
├── context-verification/# Model verification JSON metadata
├── nix/             # treefmt-nix module + formatter bridge
├── pyproject.toml   # Python project config
├── uv.lock
├── .python-version
├── .envrc
├── flake.nix / flake.lock
├── main.py, tests/, templates/
└── other telemetry files (*.pyc, __pycache__)
```

## Recommended final structure

```
local-config/
├── flake.nix                          # Single flake entry point
├── flake.lock
├── .gitignore
├── README.md
├── docs/
│   ├── nix-formatting.md              # (existing) Nix formatting docs
│   └── monorepo.md                    # (new) Monorepo structure guide
├── src/
│   └── llm_manager/                   # Renamed from llm_manager/
│       ├── __init__.py
│       ├── configurator.py
│       ├── hardware.py
│       ├── hardware_spec.py
│       ├── loader.py
│       ├── model_paths.py
│       ├── models.py
│       ├── quantization.py
│       ├── webapp.py
│       └── pyproject.toml
├── llama-swap/                        # Keep as-is (top-level)
│   ├── config.yaml
│   ├── run_benchmarks.py
│   ├── run_llama_bench.sh
│   ├── README.md
│   └── parameter-optimizer/
│       ├── batch-analyzer.py
│       ├── parameter-optimizer.py
│       └── README.md
├── other_experiments/                 # Keep as "experimental" subdir
│   ├── inferhost/
│   └── llamastash/
├── context-verification/              # Moved to top level (already there)
│   └── *.json
├── nix/
│   ├── treefmt.nix                    # (existing)
│   ├── formatter.nix                  # (existing)
│   └── checks/
│       └── pre-commit-check.nix       # (existing)
├── pyproject.toml                     # Root Python project config
├── uv.lock
├── .python-version
├── .envrc
├── .gitignore
└── tests/                             # Move from root to src/tests/
```

## Files to act on

| File | Action |
|---|---|
| `.continue/` | Delete |
| `.trunk/` | Delete (or repurpose as a docs directory if you want to keep trunk configs) |
| `.venv/` | Add to `.gitignore` — do not track |
| `nix/treefmt.nix` | Keep (blueprint requires separate module file) |
| `nix/formatter.nix` | Keep (blueprint requires separate bridge file) |
| `nix/checks/pre-commit-check.nix` | Keep (for flake checks) |
| `flake.nix` | Minor update to add new outputs |
| `pyproject.toml` | Keep at root, add `[project]` config for nix |
| `uv.lock` | Keep at root |
| `llama-swap/` | Keep as-is |
| `llm_manager/` | **Rename to `src/llm_manager/`** |
| `main.py` | Move to `src/main.py` |
| `tests/` | Move to `src/tests/` |
| `templates/` | Move to `src/templates/` |
| `config.py`, `models.py` | These are root-level — move to `src/` |
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

### Phase 2 — Directory moves

1. Rename `llm_manager/` → `src/llm_manager/`
1. Move `main.py`, `tests/`, `templates/` into `src/`
1. Move `config.py`, `models.py` into `src/`

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
1. **Should the `src/` rename be a rename or a move?** A git rename preserves history. I recommend `git mv llm_manager src/llm_manager`.
1. **Do you want to drop `other_experiments/` entirely?** It's experimental and not part of the core stack. Keeping it is fine, but it adds noise.

## Recommendation

The cleanest approach:

- Delete `.continue/` and `.trunk/`
- Add `.venv/` to `.gitignore`
- Rename `llm_manager/` → `src/llm_manager/`
- Move `main.py`, `tests/`, `templates/` into `src/`
- Keep `llama-swap/`, `other_experiments/`, `context-verification/` as-is
- Update `flake.nix` and `docs/nix-formatting.md`
- Keep `other_experiments/` but mark it as experimental
