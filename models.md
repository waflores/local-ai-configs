# Figuring out what our models are doing under the hood

## Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf

0.00.594.565 I llama_model_loader: - kv   0:                       general.architecture str              = qwen35
0.00.594.566 I llama_model_loader: - kv   1:                               general.type str              = model
0.00.594.566 I llama_model_loader: - kv   2:                               general.name str              = Qwen_Qwen3.5 9B
0.00.594.566 I llama_model_loader: - kv   3:                           general.basename str              = Qwen_Qwen3.5
0.00.594.566 I llama_model_loader: - kv   4:                         general.size_label str              = 9B
0.00.594.567 I llama_model_loader: - kv   5:                         qwen35.block_count u32              = 32
0.00.594.567 I llama_model_loader: - kv   6:                      qwen35.context_length u32              = 262144
0.00.594.568 I llama_model_loader: - kv   7:                    qwen35.embedding_length u32              = 4096
0.00.594.568 I llama_model_loader: - kv   8:                 qwen35.feed_forward_length u32              = 12288
0.00.594.568 I llama_model_loader: - kv   9:                qwen35.attention.head_count u32              = 16
0.00.594.568 I llama_model_loader: - kv  10:             qwen35.attention.head_count_kv u32              = 4
0.00.594.575 I llama_model_loader: - kv  11:             qwen35.rope.dimension_sections arr[i32,4]       = [11, 11, 10, 0]
0.00.594.578 I llama_model_loader: - kv  12:                      qwen35.rope.freq_base f32              = 10000000.000000
0.00.594.578 I llama_model_loader: - kv  13:    qwen35.attention.layer_norm_rms_epsilon f32              = 0.000001
0.00.594.578 I llama_model_loader: - kv  14:                qwen35.attention.key_length u32              = 256
0.00.594.579 I llama_model_loader: - kv  15:              qwen35.attention.value_length u32              = 256
0.00.594.579 I llama_model_loader: - kv  16:                     qwen35.ssm.conv_kernel u32              = 4
0.00.594.579 I llama_model_loader: - kv  17:                      qwen35.ssm.state_size u32              = 128
0.00.594.579 I llama_model_loader: - kv  18:                     qwen35.ssm.group_count u32              = 16
0.00.594.579 I llama_model_loader: - kv  19:                  qwen35.ssm.time_step_rank u32              = 32
0.00.594.580 I llama_model_loader: - kv  20:                      qwen35.ssm.inner_size u32              = 4096
0.00.594.580 I llama_model_loader: - kv  21:             qwen35.full_attention_interval u32              = 4
0.00.594.580 I llama_model_loader: - kv  22:                qwen35.rope.dimension_count u32              = 64
0.00.594.580 I llama_model_loader: - kv  23:                       tokenizer.ggml.model str              = gpt2
0.00.594.581 I llama_model_loader: - kv  24:                         tokenizer.ggml.pre str              = qwen35
0.00.607.359 I llama_model_loader: - kv  25:                      tokenizer.ggml.tokens arr[str,248320]  = ["!", "\"", "#", "$", "%", "&", "'", ...
0.00.611.011 I llama_model_loader: - kv  26:                  tokenizer.ggml.token_type arr[i32,248320]  = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, ...
0.00.623.832 I llama_model_loader: - kv  27:                      tokenizer.ggml.merges arr[str,247587]  = ["Ġ Ġ", "ĠĠ ĠĠ", "i n", "Ġ t",...
0.00.623.834 I llama_model_loader: - kv  28:                tokenizer.ggml.eos_token_id u32              = 248046
0.00.623.834 I llama_model_loader: - kv  29:            tokenizer.ggml.padding_token_id u32              = 248044
0.00.623.835 I llama_model_loader: - kv  30:               tokenizer.ggml.add_bos_token bool             = false
0.00.623.836 I llama_model_loader: - kv  31:                    tokenizer.chat_template str              = {%- set image_count = namespace(value...
0.00.623.837 I llama_model_loader: - kv  32:               general.quantization_version u32              = 2
0.00.623.837 I llama_model_loader: - kv  33:                          general.file_type u32              = 15
0.00.623.838 I llama_model_loader: - type  f32:  177 tensors
0.00.623.838 I llama_model_loader: - type q4_K:  204 tensors
0.00.623.839 I llama_model_loader: - type q5_K:   24 tensors
0.00.623.839 I llama_model_loader: - type q6_K:   22 tensors

0.00.623.840 I print_info: file format = GGUF V3 (latest)
0.00.623.841 I print_info: file type   = Q4_K - Medium
0.00.623.842 I print_info: file size   = 5.23 GiB (5.02 BPW) 
0.00.783.385 I print_info: arch                  = qwen35
0.00.783.385 I print_info: vocab_only            = 0
0.00.783.385 I print_info: no_alloc              = 0
0.00.783.385 I print_info: n_ctx_train           = 262144
0.00.783.385 I print_info: n_embd                = 4096
0.00.783.385 I print_info: n_embd_inp            = 4096
0.00.783.386 I print_info: n_layer               = 32
0.00.783.391 I print_info: n_head                = 16
0.00.783.392 I print_info: n_head_kv             = 4
0.00.783.392 I print_info: n_rot                 = 64
0.00.783.392 I print_info: n_swa                 = 0
0.00.783.392 I print_info: is_swa_any            = 0
0.00.783.393 I print_info: n_embd_head_k         = 256
0.00.783.393 I print_info: n_embd_head_v         = 256
0.00.783.393 I print_info: n_gqa                 = 4
0.00.783.394 I print_info: n_embd_k_gqa          = 1024
0.00.783.395 I print_info: n_embd_v_gqa          = 1024
0.00.783.395 I print_info: f_norm_eps            = 0.0e+00
0.00.783.396 I print_info: f_norm_rms_eps        = 1.0e-06
0.00.783.396 I print_info: f_clamp_kqv           = 0.0e+00
0.00.783.396 I print_info: f_max_alibi_bias      = 0.0e+00
0.00.783.397 I print_info: f_logit_scale         = 0.0e+00
0.00.783.397 I print_info: f_attn_scale          = 0.0e+00
0.00.783.397 I print_info: f_attn_value_scale    = 0.0000
0.00.783.397 I print_info: n_ff                  = 12288
0.00.783.397 I print_info: n_expert              = 0
0.00.783.398 I print_info: n_expert_used         = 0
0.00.783.398 I print_info: n_expert_groups       = 0
0.00.783.398 I print_info: n_group_used          = 0
0.00.783.398 I print_info: causal attn           = 1
0.00.783.398 I print_info: pooling type          = -1
0.00.783.398 I print_info: rope type             = 40
0.00.783.398 I print_info: rope scaling          = linear
0.00.783.399 I print_info: freq_base_train       = 10000000.0
0.00.783.399 I print_info: freq_scale_train      = 1
0.00.783.399 I print_info: n_ctx_orig_yarn       = 262144
0.00.783.399 I print_info: rope_yarn_log_mul     = 0.0000
0.00.783.399 I print_info: rope_finetuned        = unknown
0.00.783.400 I print_info: mrope sections        = [11, 11, 10, 0]
0.00.783.400 I print_info: ssm_d_conv            = 4
0.00.783.400 I print_info: ssm_d_inner           = 4096
0.00.783.400 I print_info: ssm_d_state           = 128
0.00.783.400 I print_info: ssm_dt_rank           = 32
0.00.783.400 I print_info: ssm_n_group           = 16
0.00.783.400 I print_info: ssm_dt_b_c_rms        = 0
0.00.783.401 I print_info: model type            = 9B
0.00.783.402 I print_info: model params          = 8.95 B
0.00.783.402 I print_info: general.name          = Qwen_Qwen3.5 9B
0.00.783.402 I print_info: vocab type            = BPE
0.00.783.403 I print_info: n_vocab               = 248320
0.00.783.403 I print_info: n_merges              = 247587
0.00.783.403 I print_info: BOS token             = 11 ','
0.00.783.403 I print_info: EOS token             = 248046 '<|im_end|>'
0.00.783.403 I print_info: EOT token             = 248046 '<|im_end|>'
0.00.783.403 I print_info: PAD token             = 248044 '<|endoftext|>'
0.00.783.403 I print_info: LF token              = 198 'Ċ'
0.00.783.403 I print_info: FIM PRE token         = 248060 '<|fim_prefix|>'
0.00.783.403 I print_info: FIM SUF token         = 248062 '<|fim_suffix|>'

We can test stuff with this command:

```bash
llama-fit': GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 llama-fit-params -v --model /home/waflores/.lmstudio/models/lmstudio-community/Qwen3.5-9B-GGUF/Qwen3.5-9B-Q4_K_M.gguf --n-gpu-layers all --flash-attn auto -dev CUDA0
```