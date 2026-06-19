# Figuring out what our models are doing under the hood

## Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf

0.00.594.565 I llama_model_loader: - kv 0: general.architecture str = qwen35
0.00.594.566 I llama_model_loader: - kv 1: general.type str = model
0.00.594.566 I llama_model_loader: - kv 2: general.name str = Qwen_Qwen3.5 9B
0.00.594.566 I llama_model_loader: - kv 3: general.basename str = Qwen_Qwen3.5
0.00.594.566 I llama_model_loader: - kv 4: general.size_label str = 9B
0.00.594.567 I llama_model_loader: - kv 5: qwen35.block_count u32 = 32
0.00.594.567 I llama_model_loader: - kv 6: qwen35.context_length u32 = 262144
0.00.594.568 I llama_model_loader: - kv 7: qwen35.embedding_length u32 = 4096
0.00.594.568 I llama_model_loader: - kv 8: qwen35.feed_forward_length u32 = 12288
0.00.594.568 I llama_model_loader: - kv 9: qwen35.attention.head_count u32 = 16
0.00.594.568 I llama_model_loader: - kv 10: qwen35.attention.head_count_kv u32 = 4
0.00.594.575 I llama_model_loader: - kv 11: qwen35.rope.dimension_sections arr[i32,4] = [11, 11, 10, 0]
0.00.594.578 I llama_model_loader: - kv 12: qwen35.rope.freq_base f32 = 10000000.000000
0.00.594.578 I llama_model_loader: - kv 13: qwen35.attention.layer_norm_rms_epsilon f32 = 0.000001
0.00.594.578 I llama_model_loader: - kv 14: qwen35.attention.key_length u32 = 256
0.00.594.579 I llama_model_loader: - kv 15: qwen35.attention.value_length u32 = 256
0.00.594.579 I llama_model_loader: - kv 16: qwen35.ssm.conv_kernel u32 = 4
0.00.594.579 I llama_model_loader: - kv 17: qwen35.ssm.state_size u32 = 128
0.00.594.579 I llama_model_loader: - kv 18: qwen35.ssm.group_count u32 = 16
0.00.594.579 I llama_model_loader: - kv 19: qwen35.ssm.time_step_rank u32 = 32
0.00.594.580 I llama_model_loader: - kv 20: qwen35.ssm.inner_size u32 = 4096
0.00.594.580 I llama_model_loader: - kv 21: qwen35.full_attention_interval u32 = 4
0.00.594.580 I llama_model_loader: - kv 22: qwen35.rope.dimension_count u32 = 64
0.00.594.580 I llama_model_loader: - kv 23: tokenizer.ggml.model str = gpt2
0.00.594.581 I llama_model_loader: - kv 24: tokenizer.ggml.pre str = qwen35
0.00.607.359 I llama_model_loader: - kv 25: tokenizer.ggml.tokens arr[str,248320] = \["!", """, "#", "$", "%", "&", "'", ...
0.00.611.011 I llama_model_loader: - kv 26: tokenizer.ggml.token_type arr[i32,248320] = \[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ...
0.00.623.832 I llama_model_loader: - kv 27: tokenizer.ggml.merges arr[str,247587] = \["Ġ Ġ", "ĠĠ ĠĠ", "i n", "Ġ t",...
0.00.623.834 I llama_model_loader: - kv 28: tokenizer.ggml.eos_token_id u32 = 248046
0.00.623.834 I llama_model_loader: - kv 29: tokenizer.ggml.padding_token_id u32 = 248044
0.00.623.835 I llama_model_loader: - kv 30: tokenizer.ggml.add_bos_token bool = false
0.00.623.836 I llama_model_loader: - kv 31: tokenizer.chat_template str = {%- set image_count = namespace(value...
0.00.623.837 I llama_model_loader: - kv 32: general.quantization_version u32 = 2
0.00.623.837 I llama_model_loader: - kv 33: general.file_type u32 = 15
0.00.623.838 I llama_model_loader: - type f32: 177 tensors
0.00.623.838 I llama_model_loader: - type q4_K: 204 tensors
0.00.623.839 I llama_model_loader: - type q5_K: 24 tensors
0.00.623.839 I llama_model_loader: - type q6_K: 22 tensors

0.00.623.840 I print_info: file format = GGUF V3 (latest)
0.00.623.841 I print_info: file type = Q4_K - Medium
0.00.623.842 I print_info: file size = 5.23 GiB (5.02 BPW)
0.00.783.385 I print_info: arch = qwen35
0.00.783.385 I print_info: vocab_only = 0
0.00.783.385 I print_info: no_alloc = 0
0.00.783.385 I print_info: n_ctx_train = 262144
0.00.783.385 I print_info: n_embd = 4096
0.00.783.385 I print_info: n_embd_inp = 4096
0.00.783.386 I print_info: n_layer = 32
0.00.783.391 I print_info: n_head = 16
0.00.783.392 I print_info: n_head_kv = 4
0.00.783.392 I print_info: n_rot = 64
0.00.783.392 I print_info: n_swa = 0
0.00.783.392 I print_info: is_swa_any = 0
0.00.783.393 I print_info: n_embd_head_k = 256
0.00.783.393 I print_info: n_embd_head_v = 256
0.00.783.393 I print_info: n_gqa = 4
0.00.783.394 I print_info: n_embd_k_gqa = 1024
0.00.783.395 I print_info: n_embd_v_gqa = 1024
0.00.783.395 I print_info: f_norm_eps = 0.0e+00
0.00.783.396 I print_info: f_norm_rms_eps = 1.0e-06
0.00.783.396 I print_info: f_clamp_kqv = 0.0e+00
0.00.783.396 I print_info: f_max_alibi_bias = 0.0e+00
0.00.783.397 I print_info: f_logit_scale = 0.0e+00
0.00.783.397 I print_info: f_attn_scale = 0.0e+00
0.00.783.397 I print_info: f_attn_value_scale = 0.0000
0.00.783.397 I print_info: n_ff = 12288
0.00.783.397 I print_info: n_expert = 0
0.00.783.398 I print_info: n_expert_used = 0
0.00.783.398 I print_info: n_expert_groups = 0
0.00.783.398 I print_info: n_group_used = 0
0.00.783.398 I print_info: causal attn = 1
0.00.783.398 I print_info: pooling type = -1
0.00.783.398 I print_info: rope type = 40
0.00.783.398 I print_info: rope scaling = linear
0.00.783.399 I print_info: freq_base_train = 10000000.0
0.00.783.399 I print_info: freq_scale_train = 1
0.00.783.399 I print_info: n_ctx_orig_yarn = 262144
0.00.783.399 I print_info: rope_yarn_log_mul = 0.0000
0.00.783.399 I print_info: rope_finetuned = unknown
0.00.783.400 I print_info: mrope sections = [11, 11, 10, 0]
0.00.783.400 I print_info: ssm_d_conv = 4
0.00.783.400 I print_info: ssm_d_inner = 4096
0.00.783.400 I print_info: ssm_d_state = 128
0.00.783.400 I print_info: ssm_dt_rank = 32
0.00.783.400 I print_info: ssm_n_group = 16
0.00.783.400 I print_info: ssm_dt_b_c_rms = 0
0.00.783.401 I print_info: model type = 9B
0.00.783.402 I print_info: model params = 8.95 B
0.00.783.402 I print_info: general.name = Qwen_Qwen3.5 9B
0.00.783.402 I print_info: vocab type = BPE
0.00.783.403 I print_info: n_vocab = 248320
0.00.783.403 I print_info: n_merges = 247587
0.00.783.403 I print_info: BOS token = 11 ','
0.00.783.403 I print_info: EOS token = 248046 '\<|im_end|>'
0.00.783.403 I print_info: EOT token = 248046 '\<|im_end|>'
0.00.783.403 I print_info: PAD token = 248044 '\<|endoftext|>'
0.00.783.403 I print_info: LF token = 198 'Ċ'
0.00.783.403 I print_info: FIM PRE token = 248060 '\<|fim_prefix|>'
0.00.783.403 I print_info: FIM SUF token = 248062 '\<|fim_suffix|>'

We can test stuff with this command:

```bash
llama-fit': GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 llama-fit-params -v --model /home/waflores/.lmstudio/models/lmstudio-community/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf --n-gpu-layers all --flash-attn auto -dev CUDA0
```

# llm-checker

```bash
# We did some checking
OLLAMA CAPACITY PLAN
Hardware: NVIDIA CUDA (cuda)
Memory budget: 6GB usable (reserve 2GB)

Selected models:
  - lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m:latest (26.9B, ~16.1GB base)

Recommended envelope:
  Context: 2048 (requested 8192)
  Parallel: 1 (requested 2)
  Loaded models: 1 (requested 2)
  Estimated memory: 17.18GB / 6GB (286%)
  Risk: CRITICAL (100/100)

Notes:
  - Requested settings exceed available memory budget; reduced settings are recommended.
  - Context reduced from 8192 to 2048 to avoid memory pressure.
  - Parallelism reduced from 2 to 1 to keep memory stable.
  - Loaded models capped at 1 for this objective and memory budget.

Recommended env vars:
  export OLLAMA_NUM_CTX=2048
  export OLLAMA_NUM_PARALLEL=1
  export OLLAMA_MAX_LOADED_MODELS=1
  export OLLAMA_MAX_QUEUE=4
  export OLLAMA_KEEP_ALIVE=15m
  export OLLAMA_FLASH_ATTENTION=1

Fallback profile:
  OLLAMA_NUM_CTX=2048 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1
```

We asked about ranking:

```md
│ Sorted by: score | Hardware: 31GB RAM
├───────────────────────────────────────────────────────────────────────────
╔═════╤═══════════════════════════╤════════╤═════════╤════════════╤═════════════════════════════════════════════════════════════════════════════════════════════╗
║ # │ Model │ Size │ Score │ Use Case │ Command ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 🥇 │ lms-lmstudio-community... │ 4.4GB │ 90/100 │ general │ ollama run lms-lmstudio-community-olmocr-2-7b-1025-gguf-olmocr-2-7b-1025-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 🥈 │ lms-lmstudio-community... │ 1.3GB │ 90/100 │ general │ ollama run lms-lmstudio-community-olmocr-2-7b-1025-gguf-mmproj-olmocr-2-7b-1025-f16 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 🥉 │ lms-lmstudio-community... │ 3.9GB │ 90/100 │ general │ ollama run lms-lmstudio-community-granite-4-0-h-tiny-gguf-granite-4-0-h-tiny-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 4. │ lms-lmstudio-community... │ 2.6GB │ 90/100 │ general │ ollama run lms-lmstudio-community-nvidia-nemotron-3-nano-4b-gguf-nvidia-nemotron-3-5dad6c34 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 5. │ lms-lmstudio-community... │ 2.3GB │ 83/100 │ reasoning │ ollama run lms-lmstudio-community-phi-4-mini-reasoning-gguf-phi-4-mini-reasoning-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 6. │ lms-lmstudio-community... │ 6.1GB │ 82/100 │ chat │ ollama run lms-lmstudio-community-mistral-nemo-instruct-2407-gguf-mistral-nemo-ins-0972fd65 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 7. │ lms-lmstudio-community... │ 4.6GB │ 82/100 │ chat │ ollama run lms-lmstudio-community-meta-llama-3-1-8b-instruct-gguf-meta-llama-3-1-8-58b4f9bd ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 8. │ lms-lmstudio-community... │ 3.8GB │ 82/100 │ coding │ ollama run lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 9. │ lms-mradermacher-zeran... │ 2.2GB │ 80/100 │ general │ ollama run lms-mradermacher-zerank-2-gguf-zerank-2-q4-k-s ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 10. │ lms-mradermacher-zeran... │ 1.7GB │ 80/100 │ general │ ollama run lms-mradermacher-zerank-1-small-gguf-zerank-1-small-q8-0 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 11. │ lms-lmstudio-community... │ 0.9GB │ 80/100 │ general │ ollama run lms-lmstudio-community-gemma-4-e4b-it-gguf-mmproj-gemma-4-e4b-it-bf16 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 12. │ lms-lmstudio-community... │ 5GB │ 80/100 │ general │ ollama run lms-lmstudio-community-gemma-4-e4b-it-gguf-gemma-4-e4b-it-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 13. │ lms-lmstudio-community... │ 0.9GB │ 80/100 │ general │ ollama run lms-lmstudio-community-qwen3-6-27b-gguf-mmproj-qwen3-6-27b-bf16 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 14. │ lms-lmstudio-community... │ 0.9GB │ 80/100 │ general │ ollama run lms-lmstudio-community-qwen3-5-9b-gguf-mmproj-qwen3-5-9b-bf16 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 15. │ lms-lmstudio-community... │ 5.2GB │ 80/100 │ general │ ollama run lms-lmstudio-community-qwen3-5-9b-gguf-qwen3-5-9b-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 16. │ lms-lmstudio-community... │ 1.1GB │ 80/100 │ chat │ ollama run lms-lmstudio-community-qwen3-vl-8b-instruct-gguf-mmproj-qwen3-vl-8b-instruct-f16 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 17. │ lms-lmstudio-community... │ 4.7GB │ 80/100 │ chat │ ollama run lms-lmstudio-community-qwen3-vl-8b-instruct-gguf-qwen3-vl-8b-instruct-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 18. │ lms-lmstudio-community... │ 2.3GB │ 80/100 │ general │ ollama run lms-lmstudio-community-qwen3-4b-thinking-2507-gguf-qwen3-4b-thinking-2507-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 19. │ lms-lmstudio-community... │ 4.7GB │ 80/100 │ reasoning │ ollama run lms-lmstudio-community-deepseek-r1-0528-qwen3-8b-gguf-deepseek-r1-0528-974d9efc ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 20. │ lms-lmstudio-community... │ 4.8GB │ 79/100 │ chat │ ollama run lms-lmstudio-community-rnj-1-instruct-gguf-rnj-1-instruct-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 21. │ lms-lmstudio-community... │ 8.4GB │ 78/100 │ reasoning │ ollama run lms-lmstudio-community-phi-4-reasoning-plus-gguf-phi-4-reasoning-plus-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 22. │ lms-lmstudio-community... │ 0.8GB │ 77/100 │ chat │ ollama run lms-lmstudio-community-ministral-3-3b-instruct-2512-gguf-mmproj-ministr-af8d4cc3 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 23. │ lms-lmstudio-community... │ 2GB │ 77/100 │ chat │ ollama run lms-lmstudio-community-ministral-3-3b-instruct-2512-gguf-ministral-3-3b-3e58ecf4 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 24. │ lms-lmstudio-community... │ 0.8GB │ 77/100 │ reasoning │ ollama run lms-lmstudio-community-ministral-3-14b-reasoning-2512-gguf-mmproj-minis-55d191c3 ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 25. │ lms-lmstudio-community... │ 0.8GB │ 77/100 │ chat │ ollama run lms-lmstudio-community-devstral-small-2-24b-instruct-2512-gguf-mmproj-d-338af3fb ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 26. │ lms-lmstudio-community... │ 7.7GB │ 72/100 │ reasoning │ ollama run lms-lmstudio-community-ministral-3-14b-reasoning-2512-gguf-ministral-3-f2aa5b6f ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 27. │ lms-lmstudio-community... │ 15.4GB │ 70/100 │ general │ ollama run lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 28. │ lms-lmstudio-community... │ 13.4GB │ 67/100 │ general │ ollama run lms-lmstudio-community-lfm2-24b-a2b-gguf-lfm2-24b-a2b-q4-k-m ║
╟─────┼───────────────────────────┼────────┼─────────┼────────────┼─────────────────────────────────────────────────────────────────────────────────────────────╢
║ 29. │ lms-lmstudio-community... │ 13.3GB │ 67/100 │ chat │ ollama run lms-lmstudio-community-devstral-small-2-24b-instruct-2512-gguf-devstral-d8fc31ec ║
╚═════╧═══════════════════════════╧════════╧═════════╧════════════╧═════════════════════════════════════════════════════════════════════════════════════════════╝
```

We can run `/ai-check` to perform evaluations.

```
llm-checker | AI Check
--------------------------------
│ Found 236 models in Ollama database
│ 236 models match general category

 AI-CHECK MODE
╭─────────────────────────────────────────────────────────────────
│ Category: GENERAL
│ AI Weight: 30% + Deterministic: 70%
│ Candidates Found: 12
│ Hardware: 24 cores, 30.8GB RAM, cpu_only
╰

 AI EVALUATOR STATUS
╭──────────────────────────────────────────────────
│ Model: lms-lmstudio-community-mistral-nemo-instruct-2407-gguf-mistral-nemo-ins-0972fd65:latest
│ 🔬 Evaluating: 36 models (showing top 12)
│ 🔬 Status: Running AI evaluation...
╰

 ❌ AI EVALUATION FAILED
╭──────────────────────────────────────────────────
│ Error: Failed to run chat request: This operation was aborted
│ Falling back to deterministic results
╰

 AI-CHECK RESULTS
╭─────────────────────────────────────────────────────────────────
│ Evaluator: lms-lmstudio-community-mistral-nemo-instruct-2407-gguf-mistral-nemo-ins-0972fd65:latest

│ Models Evaluated: 12
│ 📝 Note: AI evaluation failed (Failed to run chat request: This operation was aborted); showing deterministic results.
╰
╔═══════════════╤════════╤═════════════╤════════════╤═════════╤═════════════╤══════════╤═════════╤══════════════╗
║  Model        │  Size  │  Det Score  │  AI Score  │  Final  │  Fine-tune  │  RAM     │  Speed  │  Status      ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen2.5-coder │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ llama3.1      │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ llama3.2      │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen2.5       │ 7B     │ 62/100      │ N/A        │ 62/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma3        │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ mistral       │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma2        │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen3-coder   │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ codegemma     │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ qwen3         │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma4        │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╟───────────────┼────────┼─────────────┼────────────┼─────────┼─────────────┼──────────┼─────────┼──────────────╢
║ gemma         │ 7B     │ 61/100      │ N/A        │ 61/100  │ No accel    │ 8.3/25GB │ 9t/s    │ 🌐 Available ║
╚═══════════════╧════════╧═════════════╧════════════╧═════════╧═════════════╧══════════╧═════════╧══════════════╝


 AI-POWERED RECOMMENDATION
╭──────────────────────────────────────────────────
│ Best Model: qwen2.5-coder
│ Final Score: 62/100
│ ⚖️  Det: 62 + AI: N/A
│ Fine-tuning: No accel
│
│ 📥 Install command:
│   ollama pull qwen2.5-coder
│
│ Why this model?
│   • fits in 8.308752/24.64GB, Q8_0, coder-tuned, 7B is sweet spot
│   • AI: evaluation failed
```

Doing `/gpu-plan`:

```
llm-checker | Hardware Detection
------------------------------------------
✔ GPU placement plan ready

=== Multi-GPU Placement Plan ===
Backend: CUDA
Detected GPUs: 5
Total VRAM/Unified: 32GB
Single-GPU safe envelope: 14GB
Pooled safe envelope: 30GB
Strategy: distributed (5 GPUs detected; use spread scheduling and keep one model shard per device class.)

╔═══╤═════════╤══════════════════════════════════════════════════════════════════════════╤══════════════╤════════════╗
║ # │ Backend │ GPU                                                                      │ VRAM/Unified │ Speed Coef ║
╟───┼─────────┼──────────────────────────────────────────────────────────────────────────┼──────────────┼────────────╢
║ 1 │ GENERIC │ Arrow Lake-S [Intel Graphics]                                            │ 16GB         │ 0          ║
╟───┼─────────┼──────────────────────────────────────────────────────────────────────────┼──────────────┼────────────╢
║ 2 │ CUDA    │ NVIDIA GeForce RTX 5070 Laptop GPU                                       │ 8GB          │ 210        ║
╟───┼─────────┼──────────────────────────────────────────────────────────────────────────┼──────────────┼────────────╢
║ 3 │ GENERIC │ NVIDIA GeForce RTX 5070 Laptop GPU                                       │ 8GB          │ 0          ║
╟───┼─────────┼──────────────────────────────────────────────────────────────────────────┼──────────────┼────────────╢
║ 4 │ GENERIC │ Intel Graphics                                                           │ 0GB          │ 0          ║
╟───┼─────────┼──────────────────────────────────────────────────────────────────────────┼──────────────┼────────────╢
║ 5 │ GENERIC │ Non-VGA unclassified device [0000]: Intel Corporation Device [8086:7f2f] │ 0GB          │ 0          ║
╚═══╧═════════╧══════════════════════════════════════════════════════════════════════════╧══════════════╧════════════╝


Recommended env:
  export OLLAMA_SCHED_SPREAD="1"
  export OLLAMA_NUM_PARALLEL="4"
  export OLLAMA_MAX_LOADED_MODELS="3"

Recommendations:
  - Prefer model sizes <= 14GB for deterministic single-GPU residency.
  - Pooled envelope is ~30GB if scheduling spreads the load.
```

`/smart-recommend` run

```
llm-checker | Smart Recommend
---------------------------------------
✔ Analysis complete!

=== Hardware Analysis ===
  NVIDIA GeForce RTX 5070 Laptop GPU + Arrow Lake-S [Intel Graphics] + Intel Graphics + Non-VGA unclassified device [0000]: Intel Corporation Device [8086:7f2f] (8GB VRAM) + Intel(R) Core(TM) Ultra 9 275HX
  Tier: MEDIUM LOW
  Backend: cuda
  Max model size: 6GB

=== Top Recommendations ===

[BEST] Best Overall:
  qwen2.5-coder:1.5b-base-q8_0
  1.5B params | 1.5GB | Q8_0
  Score: 98/100 (Q:94 S:100 F:100)
  ~42 tokens/sec
  ollama pull qwen2.5-coder:1.5b-base-q8_0

Highest Quality:
  qwen2.5-coder:7b-base-q6_K
  7B | 5.3GB | Quality: 97/100
  ollama pull qwen2.5-coder:7b-base-q6_K

=== Other Good Options ===
[98] qwen2.5-coder:1.5b-instruct-q8_0 - 1.5B, 1.5GB
[98] qwen2.5-coder:0.5b-base-q8_0 - 0.5B, 0.5GB
[98] qwen2.5-coder:0.5b-instruct-q8_0 - 0.5B, 0.5GB
[97] qwen2.5:1.5b-instruct-q8_0 - 1.5B, 1.5GB

=== Insights ===
  [OK] Excellent match found! qwen2.5-coder:1.5b-base-q8_0 scores 98/100.
  [TIP] High-quality quantization selected. Good balance of quality and performance.
```

Doing some tool checks:

```
waflores@wills-legion-5i:~$ llm-checker toolcheck --all

llm-checker | Ollama Integration
------------------------------------------
✔ Toolcheck completed (29 models)

╔═════════════════════════════════════════════════════════════════════════════════════════╤═════════════╤═══════╤═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ Model                                                                                   │ Status      │ Score │ Reason                                                                                                                                                                                                  ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-mradermacher-zerank-2-gguf-zerank-2-q4-k-s:latest                                   │ UNSUPPORTED │ 10    │ No tool-calling markers found in response.                                                                                                                                                              ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-mradermacher-zerank-1-small-gguf-zerank-1-small-q8-0:latest                         │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-rnj-1-instruct-gguf-rnj-1-instruct-q4-k-m:latest                 │ PARTIAL     │ 50    │ Model responded but did not emit structured tool_calls.                                                                                                                                                 ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-olmocr-2-7b-1025-gguf-olmocr-2-7b-1025-q4-k-m:latest             │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"registry.ollama.ai/library/lms-lmstudio-community-olmocr-2-7b-1025-gguf-olmocr-2-7b-1025-q4-k-m:latest does not support tools"}           ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-olmocr-2-7b-1025-gguf-mmproj-olmocr-2-7b-1025-f16:latest         │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-olmocr-2-7b-1025-gguf-mmproj-olmocr-2-7b-1025-f16:latest\" does not support chat"}                               ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-granite-4-0-h-tiny-gguf-granite-4-0-h-tiny-q4-k-m:latest         │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-gemma-4-e4b-it-gguf-mmproj-gemma-4-e4b-it-bf16:latest            │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-gemma-4-e4b-it-gguf-mmproj-gemma-4-e4b-it-bf16:latest\" does not support chat"}                                  ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-gemma-4-e4b-it-gguf-gemma-4-e4b-it-q4-k-m:latest                 │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-6-27b-gguf-mmproj-qwen3-6-27b-bf16:latest                  │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-qwen3-6-27b-gguf-mmproj-qwen3-6-27b-bf16:latest\" does not support chat"}                                        ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m:latest                       │ UNSUPPORTED │ 0     │ Failed to run chat request: This operation was aborted                                                                                                                                                  ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-5-9b-gguf-mmproj-qwen3-5-9b-bf16:latest                    │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-qwen3-5-9b-gguf-mmproj-qwen3-5-9b-bf16:latest\" does not support chat"}                                          ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-5-9b-gguf-qwen3-5-9b-q4-k-m:latest                         │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 500: Internal Server Error - {"error":"llama-server returned invalid tool call arguments for \"add_numbers\": unexpected end of JSON input"}                           ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-vl-8b-instruct-gguf-mmproj-qwen3-vl-8b-instruct-f16:latest │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-qwen3-vl-8b-instruct-gguf-mmproj-qwen3-vl-8b-instruct-f16:latest\" does not support chat"}                       ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-vl-8b-instruct-gguf-qwen3-vl-8b-instruct-q4-k-m:latest     │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-qwen3-4b-thinking-2507-gguf-qwen3-4b-thinking-2507-q4-k-m:latest │ UNSUPPORTED │ 10    │ No tool-calling markers found in response.                                                                                                                                                              ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-phi-4-reasoning-plus-gguf-phi-4-reasoning-plus-q4-k-m:latest     │ UNSUPPORTED │ 0     │ Failed to run chat request: This operation was aborted                                                                                                                                                  ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-phi-4-mini-reasoning-gguf-phi-4-mini-reasoning-q4-k-m:latest     │ PARTIAL     │ 50    │ Model responded but did not emit structured tool_calls.                                                                                                                                                 ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-nvidia-nemotron-3-nano-4b-gguf-nvidia-nemotron-3-5dad6c34:latest │ UNSUPPORTED │ 10    │ No tool-calling markers found in response.                                                                                                                                                              ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-mistral-nemo-instruct-2407-gguf-mistral-nemo-ins-0972fd65:latest │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-ministral-3-3b-instruct-2512-gguf-mmproj-ministr-af8d4cc3:latest │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-ministral-3-3b-instruct-2512-gguf-mmproj-ministr-af8d4cc3:latest\" does not support chat"}                       ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-ministral-3-3b-instruct-2512-gguf-ministral-3-3b-3e58ecf4:latest │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-ministral-3-14b-reasoning-2512-gguf-mmproj-minis-55d191c3:latest │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-ministral-3-14b-reasoning-2512-gguf-mmproj-minis-55d191c3:latest\" does not support chat"}                       ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-ministral-3-14b-reasoning-2512-gguf-ministral-3-f2aa5b6f:latest  │ UNSUPPORTED │ 10    │ No tool-calling markers found in response.                                                                                                                                                              ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-meta-llama-3-1-8b-instruct-gguf-meta-llama-3-1-8-58b4f9bd:latest │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-lfm2-24b-a2b-gguf-lfm2-24b-a2b-q4-k-m:latest                     │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-devstral-small-2-24b-instruct-2512-gguf-mmproj-d-338af3fb:latest │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"\"lms-lmstudio-community-devstral-small-2-24b-instruct-2512-gguf-mmproj-d-338af3fb:latest\" does not support chat"}                       ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-devstral-small-2-24b-instruct-2512-gguf-devstral-d8fc31ec:latest │ SUPPORTED   │ 100   │ Model emitted structured tool_calls.                                                                                                                                                                    ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-deepseek-r1-0528-qwen3-8b-gguf-deepseek-r1-0528-974d9efc:latest  │ UNSUPPORTED │ 10    │ No tool-calling markers found in response.                                                                                                                                                              ║
╟─────────────────────────────────────────────────────────────────────────────────────────┼─────────────┼───────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m:latest   │ UNSUPPORTED │ 0     │ Failed to run chat request: HTTP 400: Bad Request - {"error":"registry.ollama.ai/library/lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m:latest does not support tools"} ║
╚═════════════════════════════════════════════════════════════════════════════════════════╧═════════════╧═══════╧═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

Summary:
  Supported: 9
  Partial: 2
  Unsupported: 18
```

```
waflores@wills-legion-5i:~$ llm-checker ollama-plan --models $(ollama list | cut -d' ' -f 1 | tail -n +2 | tr '\n' ' ') --objective throughput
✔ Capacity plan generated

 OLLAMA CAPACITY PLAN
Hardware: NVIDIA CUDA (cuda)
Memory budget: 6GB usable (reserve 2GB)

Selected models:
  - lms-lmstudio-community-qwen3-6-27b-gguf-qwen3-6-27b-q4-k-m:latest (26.9B, ~16.1GB base)

Recommended envelope:
  Context: 2048 (requested 8192)
  Parallel: 1 (requested 2)
  Loaded models: 1 (requested 3)
  Estimated memory: 17.18GB / 6GB (286%)
  Risk: CRITICAL (100/100)

Notes:
  - Requested settings exceed available memory budget; reduced settings are recommended.
  - Context reduced from 8192 to 2048 to avoid memory pressure.
  - Parallelism reduced from 2 to 1 to keep memory stable.
  - Loaded models capped at 1 for this objective and memory budget.

Recommended env vars:
  export OLLAMA_NUM_CTX=2048
  export OLLAMA_NUM_PARALLEL=1
  export OLLAMA_MAX_LOADED_MODELS=1
  export OLLAMA_MAX_QUEUE=4
  export OLLAMA_KEEP_ALIVE=10m
  export OLLAMA_FLASH_ATTENTION=1

Fallback profile:
  OLLAMA_NUM_CTX=2048 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1
```

We do a context verification test: `reset; for i in $(ollama list | cut -d' ' -f 1 | tail -n +2 | tr '\n' ' '); do llm-checker verify-context -m $i -t 200000; done`
Let's dump this to a json file for our project to digest.

```bash

# We can get 1 to dump to a file:
llm-checker verify-context -m lms-lmstudio-community-codellama-7b-instruct-gguf-codellama-7b-instruct-q4-k-m -t 200000 --json | minify --type json --output /tmp/context-verification.json


# Let's dump all of them to files of their own (we can't append):
for i in $(ollama list | cut -d' ' -f 1 | tail -n +2 | tr '\n' ' '); do llm-checker verify-context -m $i -t 200000 --json | minify --type json --output "/tmp/context-verification/${i%:*}.json"; done
```

So the files in `/tmp/context-verification/` actually does dump things into json format - we should be able to analyze these files now!

Example of a good bad run:

```bash
jq . /tmp/context-verification/llama2.json
{
  "model": "llama2:latest",
  "targetTokens": 2E+5,
  "declaredContext": 4096,
  "modelSizeGB": 3.6,
  "verification": {
    "modelName": "llama2:latest",
    "targetTokens": 2E+5,
    "declaredContext": 4096,
    "modelSizeGB": 3.6,
    "effectiveMemoryGB": 8,
    "memoryLimitedContext": 6E+4,
    "recommendedContext": 4096,
    "status": "fail",
    "checks": [
      {
        "id": "declared_context",
        "status": "fail",
        "message": "Model-declared context window: 4096 tokens"
      },
      {
        "id": "memory_budget",
        "status": "warn",
        "message": "Estimated memory-safe context: ~60000 tokens on this hardware"
      }
    ],
    "suggestions": [
      "Reduce target context to <= 4096 tokens."
    ]
  }
}
```

We can do a check for things:

```bash
jq '.verification | .modelName, .recommendedContext'  /tmp/context-verification/*.json
```
