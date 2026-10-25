# llm_manager.md

The Python Flask application: model registry, hardware-aware config generation, and the web UI.

## Why this exists

`llm_manager` is the web-facing layer. It turns the 22-model registry (from `context-verification/*.json` + `llama-swap/config.yaml`) plus live hardware detection into hardware-aware "profiles" — quantized, context-capped configurations that tell the user which models fit in the RTX 5070 Max-Q VRAM and what llama.cpp parameters to use.

## Architecture

```
llm_manager/
├── config.py           # Domain dataclasses (ModelConfig, HardwareSpec, SwapConfig, ...)
├── models.py           # Model dataclass (size, context, quantization, paths) + helpers
├── configurator.py     # Hardware-aware profile generation (estimate_vram, optimize, tiers)
├── loader.py           # Model discovery: JSON metadata + config.yaml + on-disk scan
├── model_paths.py      # Path resolution: directory mapping + GGUF file scanning
├── hardware.py         # nvidia-smi / free / nproc detection
├── database.py         # SQLite ORM: persist + reload config snapshots
├── config_store.py     # Persist/reload/import/export configs to the DB
├── tuning_store.py     # Tuning profiles (per-model llama.cpp params)
├── api_docs.py         # FastAPI app: auto-generated OpenAPI + Swagger/ReDoc
├── webapp.py           # Flask app: routes (/ /models /hardware /configs /tuning /admin)
├── templates/          # Flask Jinja templates (admin, api_docs, base, configs, hardware, index, models, tuning)
└── tests/              # pytest suite (discovery edge cases, configurator, web app, ORM)
```

## Model discovery pipeline

`discover_models()` runs three passes:

1. **Parse JSON metadata** — every `context-verification/*.json` becomes a `Model`.
1. **Enrich from config.yaml** — name/path overrides and config key → directory alias mapping.
1. **Drop MMProj auxiliary files** — the vision-encoder sidecar files are not standalone models.

Path resolution order for each model:

1. config.yaml `model_path` override (if declared)
1. directory mapping (`model_directory_mapping()`)
1. recursive directory scan for matching `.gguf` file

## Hardware-aware profile generation

`generate_profiles()` walks every model and produces a `ConfigProfile`:

- Picks the right **quantization** (Q4_K_M / Q5_K_M / Q8_0 / FP8…) and **KV-cache precision**.
- **Capping context** to the hardware tier (`TIER_OVERRIDES`) so models fit in VRAM.
- Runs an **industrial-strength fit sweep**: KV-bit toggles + context reductions until the
  model fits, or marks it `over_vram`.
- Produces `fit_status`: `fits`, `fits_with_capping`, or `over_vram`.

## Web UI routes

| Route | Description |
|-------|-------------|
| `GET /` | Front page: hardware + config summary |
| `GET /models` | Model registry |
| `GET /hardware` | Detected hardware |
| `GET /configs` | Generated profiles + export |
| `GET /configs/export.json` | Config as JSON |
| `GET /configs/export.yaml` | Config as YAML download |
| `POST /tuning` | Save a per-model llama.cpp tuning profile |
| `GET /admin` | Admin portal: directories + model counts |
| `POST /dirs` | Add/delete a model directory |
| `GET /api-docs` | Swagger UI / ReDoc (proxied from the FastAPI app on 5001) |

## Running

```bash
nix develop .#default
uv run python -m llm_manager.webapp      # Flask on 127.0.0.1:5000
uv run uvicorn llm_manager.api_docs:app --port 5001   # FastAPI docs on 5001
```

## Development

```bash
uv run pytest                          # run tests
uv run ruff check                      # lint
uv run ruff format --check             # format check
```

Tests are in `llm_manager/tests/` and cover discovery edge cases, configurator branches,
ORM persistence, and the Flask routes.
