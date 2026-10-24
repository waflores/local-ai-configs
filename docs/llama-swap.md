# llama-swap.md

What llama-swap is, its config format, its REST API, the 22-model inventory, and the
performance targets.

## Why this exists

`l Lama-swap` is the model-management layer on top of `llama-server`. It loads and unloads
GGUF models on demand, swapping between CUDA0 (active inference) and Vulkan0/Vulkan1
(storage/fallback). All agent interaction with models goes through this daemon.

## Artifacts

| Artifact | Purpose |
|----------|---------|
| `config.yaml` | 22 model definitions (name, roles, context, paths) |
| `run_benchmarks.py` | Benchmark harness (placeholder — redesign in progress) |
| `run_llama_bench.sh` | Shell wrapper that runs all benchmarks |

## REST API (daemon on 127.0.0.1:10001)

```bash
# Health + model list
curl http://127.0.0.1:10001/health
curl http://127.0.0.1:10001/v1/models

# Load / unload
curl -X POST http://127.0.0.1:10001/v1/models \
  -H "Content-Type: application/json" \
  -d '{"name": "...", "path": "/path/to/model.gguf", "ttl": 600}'

curl -X DELETE http://127.0.0.1:10001/v1/models/<name>

# Chat completion
curl -X POST http://127.0.0.1:10001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "...", "messages": [{"role": "user", "content": "..."}]}'
```

## Model inventory (22)

The registry is defined in `context-verification/*.json` and matched to `config.yaml`
keys by a string alias map. Each model is discovered by:

1. **Static metadata** (*context-verification/*.json) — name, size, context, quantization.
1. **On-disk scan** (`loader.discover_models_on_disk()`) — live `.gguf` paths.
1. **config.yaml path override** — if a `model_path` is declared.
1. **Directory mapping** — case-insensitive dir name → canonical path.
1. **Directory scan** — recursive walk for matching `.gguf` files.

| Model | Params | Size (Q4_K_M) |
|-------|--------|---------------|
| CodeLlama-7B-Instruct | 7B | ~4 GB |
| DeepSeek-R1-0528-Qwen3-8B | 8B | ~5 GB |
| Devstral-Small-2-24B-Instruct-2512 | 24B | ~14 GB |
| Gemma-4-E4B-it | 8B | ~5.3 GB |
| Granite-4.0-h-tiny | 7B | ~4 GB |
| LFM2-24B-A2B | 24B | ~14.4 GB |
| Meta-Llama-3.1-8B-Instruct | 8B | ~5 GB |
| Ministral-3-14B-Reasoning-2512 | 14B | ~8 GB |
| Ministral-3-3B-Instruct-2512 | 3B | ~2 GB |
| Mistral-Nemo-Instruct-2407 | 13B | ~6.5 GB |
| NVIDIA-Nemotron-3-Nano-4B | 4B | ~2.8 GB |
| olmOCR-2-7B-1025 | 8B | ~4.7 GB |
| Phi-4-mini-reasoning | 3B | ~2.5 GB |
| Phi-4-reasoning-plus | 13B | ~9 GB |
| Qwen3-4B-Thinking-2507 | 4B | ~4 GB |
| Qwen3.5-9B | 9B | ~5.6 GB |
| Qwen3.6-27B | 27B | ~16.5 GB |
| Qwen3-VL-8B-Instruct | 8B | ~5 GB |
| rnj-1-instruct | — | — |
| zerank-1-small | — | — |
| zerank-2 | — | — |
| llama2:latest | 7B | ~3.6 GB (reference only, no disk path) |

## Performance targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Model load time | < 5s | < 10s |
| Model swap time | < 2s | < 5s |
| Generation speed (7B) | > 10 t/s | > 5 t/s |
| VRAM utilization | < 70% | < 90% |
| Context efficiency | > 80% | > 50% |

## Configuration highlights

- `globalTTL: 0` — keep models loaded indefinitely.
- `groups.swappable.exclusive: true` + `swap: true` — only one model per swap group at a time.
- `macros.device: "CUDA0"` — active inference; `Vulkan0` for storage/fallback.
- `macros.ctxSize` per model — tuned to the model's memory-safe context.
- `models.<name>.cmd` — the full llama-server command per model (includes paths, GPUs, context).

## Notes

- `run_benchmarks.py` and `run_llama_bench.sh` are **placeholders/wrappers** — not yet
  wired into a real benchmark pipeline. Benchmarks are tracked in `docs/monorepo.md`.
- `my-config.yaml`, `tweaking-config.yaml`, and `profiles_generated.yaml` are duplicates/
  working files; they are not part of the canonical config. See `docs/monorepo.md`.
