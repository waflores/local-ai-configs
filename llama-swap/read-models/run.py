from llama_cpp import Llama
from pprint import pprint

import copy

MODEL = "/home/waflores/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf"

llm = Llama(model_path=MODEL, verbose=False)

print("*" * 80)
pprint(llm.__getstate__())
metadata_printer = copy.deepcopy(llm.metadata)
metadata_printer.pop("tokenizer.chat_template", "")
print("*" * 80)
pprint(metadata_printer)


# ---- the data you supplied ----
data = metadata_printer
vrams = 7374  # available VRAM in MiB

# convert the dict values to integers
emb_len = int(data["qwen35.embedding_length"])
ctx_len = int(data["qwen35.context_length"])
key_len = int(data["qwen35.attention.key_length"])
# More about the scaling
rope_scaling_factor = float(data["qwen35.rope.scaling.factor"])
original_context_length = int(data["qwen35.rope.scaling.original_context_length"])


# 1️⃣ Size of the embedding matrix (MiB)
# embedding = emb_len × ctx_len bytes  →  embed_mib = bytes / 1024²
embed_mib = (emb_len * ctx_len) / (1024 * 1024)  # = emb_len / 1024

# 2️⃣ VRAM left for the KV tables (MiB)
remaining = vrams - embed_mib

# 3️⃣ KV cost per token (MiB)
# KV = 2 * key_len bytes  →  kv_mib_per_tok = bytes / 1024²
kv_mib_per_tok = (2 * key_len) / (1024 * 1024)  # = 0.5 KiB = 0.00048828125 MiB

# 4️⃣ Maximum number of tokens we can keep
max_ctx = int(remaining / kv_mib_per_tok)

print(f"Maximum context length = {max_ctx:,} tokens")

original_ctx = int(rope_scaling_factor * original_context_length)
n_ctx = min(original_ctx, ctx_len)
print(f"Calculated n_ctx: {original_ctx}, max_ctx: {n_ctx}")
