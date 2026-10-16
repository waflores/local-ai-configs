# Inference Parameter Tuning & OOM Prevention

This document explains how to tune llama.cpp inference parameters for hardware-aware context windows, and why OOM (out of memory) happens at runtime despite correct RAM + VRAM estimates.

It covers:
- VRAM and RAM estimation formulas
- Context window sizing per model
- KV cache precision selection
- Why OOM happens at runtime
- Recommended safety margins

---

## Hardware Context

**RTX 5070 Max-Q:** 8 GB VRAM total, ~7.6 GB free
**System RAM:** 30.8 GB

The RTX 5070 Max-Q (laptop GPU) shares CPU RAM with the system. Inference uses both:
- **VRAM** holds model weights + KV cache for GPU layers
- **System RAM** holds model weights + any KV cache that overflows from VRAM

---

## VRAM Estimation

The configurator's `estimate_vram_gb` formula:

```
vram = model_size_gb * 1.1 + (ctx_size * kv_bytes_per_token / (1024**3)) * (kv_bits / 8)
```

Where:
- `model_size_gb` — model file size (e.g., 4.7 GB for Qwen3-8B)
- `1.1` — ~10% runtime overhead (allocation buffers, etc.)
- `ctx_size` — context window
- `kv_bytes_per_token` — estimated KV-cache bytes per token at Q8_0 (4 bytes)
- `kv_bits` — precision: 8 = Q8_0, 4 = Q4_0 (halves KV cache)

### KV Bytes Per Token

The `kv_bytes_per_token` property estimates per-token KV cache size:

```
kv_bytes_per_token = (size_gb * 1e9 * 0.30) / memory_safe_context
```

This uses ~30% of model size as the KV cache overhead at the memory-safe context. If the memory-safe context is unknown, it falls back to rough defaults by parameter range (e.g., 230 KB/ton for 4B–12B models).

---

## RAM Estimation

The `_estimate_ram_gb` formula mirrors VRAM:

```
ram = model_size_gb * 1.1 + (ctx_size * kv_bytes_per_token / (1024**3)) * (kv_bits / 8)
```

This is the same formula because the total memory is `weights + KV cache` — the KV cache is just split between VRAM and RAM based on allocation.

### RAM Constraint Fit Check

```
ram_for_weights = model_size_gb * 1.1
ram_for_overflow_kv = max(0, vram_for_model - free_vram)
ram_needed = ram_for_weights + ram_for_overflow_kv

if RAM limit set:
    fits = ram_needed <= ram_limit
else:
    fits = vram_for_model <= free_vram
```

---

## Context Window Sizing

The configurator's `optimize_context` finds the largest context that fits:

1. Start at `max_ctx` (from hardware tier override)
2. Estimate VRAM at that context
3. If it exceeds the VRAM limit, reduce by ~15% per step
4. Try reduction ladder: 8192 → 1024 → 256

The `TIER_OVERRIDES` table maps VRAM tiers to context caps:

| VRAM Free | ctxSize | n_gpu_layers |
|-----------|---------|--------------|
| ~10 GB    | 16384   | all          |
| ~15 GB    | 32768   | all          |
| ~20 GB    | 65536   | all          |

For the RTX 5070 Max-Q (7.6 GB free), models stay within the tier-10 cap.

---

## KV Cache Precision Selection

Q4_0 halves KV cache memory vs Q8_0:

| Precision | KV bytes/token | Memory Savings |
|-----------|----------------|----------------|
| Q8_0      | ~4 bytes       | —              |
| Q4_0      | ~2 bytes       | 50%            |

The sweep in `generate_profiles` tries both 8 and 4 bits, then applies context reductions (8192, 1024, 256) until the model fits in VRAM.

---

## Why OOM Happens at Runtime

### 1. KV cache estimates are approximate

The `kv_bytes_per_token` is derived from model size and memory-safe context — a rough inference, not the actual architecture. Real KV cache depends on `layers × hidden_size`:

```
Real KV = 2 × layers × hidden_size × 2 × (bit/8) × context
```

If the actual `layers × hidden_size` > assumed, the real KV cache exceeds the estimate.

### 2. Context auto-growth

`-c` is a soft allocation. When the model generates more tokens than the context allows, llama.cpp can dynamically grow the KV cache. This reallocation can OOM if you're near your memory limit.

### 3. CUDA context overhead

The CUDA runtime, cuDNN, and CUDA graphs allocate memory independently:

```
Total GPU memory = model weights + KV cache + CUDA context (~0.5–1 GB)
```

Your configurator only estimates `size_gb × 1.1 + KV_cache`. The CUDA context is never accounted for.

### 4. Process memory overhead

The Python process + llama.cpp bindings + other modules consume RAM not in your model estimates:

```
Total RAM = weights + KV cache + bindings + Python + OS + other processes
```

### 5. GPU VRAM fragmentation

Even with enough total VRAM, the allocation might not be contiguous. Large contiguous blocks can fail with OOM even if total free memory is sufficient. Flash attention (`-fa on`) can increase peak VRAM due to intermediate buffers.

---

## Recommended Safety Margins

Add a margin to the estimates so you have headroom for unknown factors:

```python
def estimate_vram_gb(model, ctx_size, kv_bits=8, margin=1.3) -> float:
    vram = model.size_gb * 1.1
    kv_bytes_per_token = model.kv_bytes_per_token * (kv_bits / 8.0)
    vram += (ctx_size * kv_bytes_per_token) / 1024**3
    return vram * margin  # 30% safety margin for CUDA context, fragmentation, overhead
```

A 30% margin accounts for:
- CUDA context (~0.5–1 GB)
- Allocator fragmentation
- Flash attention intermediate buffers
- Runtime overhead

---

## Practical Tuning Tips

1. **Reduce context by 20–30% below estimated limit** — leaves room for growth
2. **Use `-ngl` to keep layers on GPU** — offloading layers to CPU reduces VRAM but increases RAM
3. **Monitor `nvidia-smi` and `free -h`** during inference to see actual usage
4. **Disable flash attention if OOM**: `-fa off` is more predictable than `-fa on`
5. **Set `-c` explicitly** to cap KV cache growth

---

## File Reference

- `llm_manager/configurator.py` — `estimate_vram_gb`, `_estimate_ram_gb`, `generate_profiles`, `optimize_context`, `Config.ram_limit_gb`
- `llm_manager/models.py` — `Model.kv_bytes_per_token` property, `ConfigProfile.ram_gb`, `estimate_vram_gb`
- `llm_manager/hardware_spec.py` — `HardwareSpec` (includes `system_ram_gb`)
