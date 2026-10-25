# context-verification

Source-of-truth JSON metadata for the 22 models in `llama-swap/config.yaml`.
The Python app (`llm_manager/loader.py`) reads these files at runtime to enrich
model definitions with verified context sizes, memory-safe context, and
quantization tags.

## File naming convention

```
<site-prefix>-<model-identifier>-gguf-<display-name>-<quant-tag>.json
```

Examples:
- `lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m.json`
- `lms-mradermacher-zerank-2-gguf-zerank-2-q4-k-s.json`

**Model identifier** (after the site prefix, before `-gguf-`) is the canonical
key used in the Python app. The display name is a human-readable form of the
identifier; the quant tag is the quantization suffix.

## Model mapping

| Model | JSON file |
|-------|-----------|
| CodeLlama-7B-Instruct | `lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m.json` |
| DeepSeek-R1-0528-Qwen3-8B | `lms-lmstudio-community-deepseek-r1-0528-qwen3-8b-gguf-deepseek-r1-0528-974d9efc.json` |
| Devstral-Small-2-24B-Instruct-2512 | `lms-lmstudio-community-devstral-small-2-24b-instruct-2512-gguf-devstral-d8fc31ec.json` |
| Gemma-4-E4B-it | `lms-lmstudio-community-gemma-4-e4b-it-gguf-gemma-4-e4b-it-q4-k-m.json` |
| Granite-4.0-h-tiny | `lms-lmstudio-community-granite-4-0-h-tiny-gguf-granite-4-0-h-tiny-q4-k-m.json` |
| LFM2-24B-A2B | `lms-lmstudio-community-lfm2-24b-a2b-gguf-lfm2-24b-a2b-q4-k-m.json` |
| Meta-Llama-3.1-8B-Instruct | `lms-lmstudio-community-meta-llama-3-1-8b-instruct-gguf-meta-llama-3-1-8-58b4f9bd.json` |
| Ministral-3-14B-Reasoning-2512 | `lms-lmstudio-community-ministral-3-14b-reasoning-2512-gguf-ministral-3-f2aa5b6f.json` |
| Ministral-3-3B-Instruct-2512 | `lms-lmstudio-community-ministral-3-3b-instruct-2512-gguf-ministral-3-3b-3e58ecf4.json` |
| Mistral-Nemo-Instruct-2407 | `lms-lmstudio-community-mistral-nemo-instruct-2407-gguf-mistral-nemo-ins-0972fd65.json` |
| NVIDIA-Nemotron-3-Nano-4B | `lms-lmstudio-community-nvidia-nemotron-3-nano-4b-gguf-nvidia-nemotron-3-5dad6c34.json` |
| olmOCR-2-7B-1025 | `lms-lmstudio-community-olmocr-2-7b-1025-gguf-olmocr-2-7b-1025-q4-k-m.json` |
| Phi-4-mini-reasoning | `lms-lmstudio-community-phi-4-mini-reasoning-gguf-phi-4-mini-reasoning-q4-k-m.json` |
| Phi-4-reasoning-plus | `lms-lmstudio-community-phi-4-reasoning-plus-gguf-phi-4-reasoning-plus-q4-k-m.json` |
| Qwen3-4B-Thinking-2507 | `lms-lmstudio-community-qwen3-4b-thinking-2507-gguf-qwen3-4b-thinking-2507-q4-k-m.json` |
| Qwen3.5-9B | `lms-lmstudio-community-qwen3-5-9b-gguf-qwen3-5-9b-q4-k-m.json` |
| Qwen3.6-27B | `lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m.json` |
| Qwen3-VL-8B-Instruct | `lms-lmstudio-community-qwen3-vl-8b-instruct-gguf-qwen3-vl-8b-instruct-q4-k-m.json` |
| rnj-1-instruct | `lms-lmstudio-community-rnj-1-instruct-gguf-rnj-1-instruct-q4-k-m.json` |
| zerank-1-small | `lms-mradermacher-zerank-1-small-gguf-zerank-1-small-q8-0.json` |
| zerank-2 | `lms-mradermacher-zerank-2-gguf-zerank-2-q4-k-s.json` |

Plus auxiliary MMProj sidecar files (not standalone models) and `llama2.json`.

## JSON fields

| Field | Meaning |
|-------|---------|
| `modelSizeGB` | Model size on disk (GB) |
| `declaredContext` | Context size requested in config |
| `memoryLimitedContext` | Memory-safe context (max tokens the model fits in VRAM) |
| `recommendedContext` | Recommended context for VRAM efficiency |
| `status` | Verification status (e.g. "verified") |

See `llm_manager/loader.py` for how these fields are parsed and merged.
