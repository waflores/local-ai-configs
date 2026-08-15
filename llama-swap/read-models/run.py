from llama_cpp import Llama

MODEL = "/home/waflores/.lmstudio/models/empero-ai/Qwythos-9B-Claude-Mythos-5-1M-GGUF/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf"

llm = Llama(model_path=MODEL)
