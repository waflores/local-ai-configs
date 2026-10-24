# inference-tuning.md

How to tune llama.cpp inference parameters for hardware-aware context windows, and why OOM
happens at runtime despite correct RAM + VRAM estimates.

## Why this exists

The model registry records a "memory-safe context" per model, but the actual GPU allocation
at runtime includes CUDA context, allocator fragmentation, and KV-cache growth — none of
which the estimators account for. This doc explains the math, the failure modes, and the
safety margins to apply.

## Hardware context

- **RTX 5070 Max-Q:** 8 GB VRAM total, ~7.6 GB free
- **System RAM:** 30.8 GB
- Inference uses both VRAM (weights + GPU KV cache) and system RAM (weights + spilled KV).

## VRAM / RAM estimation

`estimate_vram_gb(model, ctx_size, kv_bits=8)`:

```
vram = model.size_gb * 1.1 + (ctx_size * kv_bytes_per_token / (1024**3)) * (kv_bits / 8)
```

- `model.size_gb * 1.1` — ~10% runtime overhead
- `kv_bytes_per_token` — estimated KV-cache bytes/token at Q8_0 (~4 bytes), scaled by
  precision (Q4_0 = 4 bits, Q8_0 = 8 bits)
- Default KV bytes/token: 190 KB (3B), 230 KB (4–12B), 250 KB (>12B), else 280 KB

`_estimate_ram_gb` mirrors this for system RAM.

## Context window sizing

`optimize_context` starts at the hardware-tier cap and reduces ~15% per step until VRAM
fits:

```
ctx = max_ctx (tier-capped)
while ctx > 256:
    if vram(ctx) <= vram_limit: return ctx
    ctx = int(ctx * 0.85)
```

Reduction ladder after dropping below 256: `8192 → 1024 → 256`.

`TIER_OVERRIDES` maps VRAM tiers to context caps:

| VRAM free | ctxSize |
|-----------|---------|
| ~10 GB | 16384 |
| ~15 GB | 32768 |
| ~20 GB | 65536 |

## Why OOM happens at runtime

1. **KV cache estimates are approximate** — real `layers × hidden_size` may exceed the
   assumed value.
1. **Context auto-growth** — `-c` is a soft allocation; llama.cpp can grow the KV cache
   beyond it, risking OOM near the limit.
1. **CUDA context overhead** — CUDA runtime + cuDNN + CUDA graphs allocate ~0.5–1 GB
   independently and are never counted.
1. **Process memory overhead** — Python + llama-cpp-python bindings + other modules.
1. **VRAM fragmentation** — non-contiguous allocations can fail even with enough free.

## Recommended safety margins

Add a 30% margin to the VRAM estimate:

```python
def estimate_vram_gb(model, ctx_size, kv_bits=8, margin=1.3) -> float:
    vram = model.size_gb * 1.1
    vram += (ctx_size * model.kv_bytes_per_token * (kv_bits / 8.0)) / 1024**3
    return vram * margin
```

Practical tips:

- Reduce context by 20–30% below the estimated limit.
- Use `-ngl` to keep layers on GPU; offloading to CPU reduces VRAM but increases RAM.
- Monitor `nvidia-smi` + `free -h` during inference.
- Disable flash attention (`-fa off`) if OOM; it's less predictable than `on`.
- Set `-c` explicitly to cap KV-cache growth.

## File map

| Concern | File |
|---------|------|
| `estimate_vram_gb`, `generate_profiles`, `optimize_context` | `llm_manager/configurator.py` |
| `Model.kv_bytes_per_token` | `llm_manager/models.py` |
| `HardwareSpec` | `llm_manager/hardware_spec.py` |
| Model registry & discovery | `llm_manager/loader.py` |
