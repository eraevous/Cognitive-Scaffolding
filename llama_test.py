from llama_cpp import Llama

llm = Llama(
    model_path="C:/Users/Admin/.lmstudio/models/unsloth/gpt-oss-20b-GGUF/gpt-oss-20b-Q4_K_S.gguf",
    n_ctx=32000,
    verbose=True
)

response = llm(
    "Give me the first 100 words of Moby Dick in pirate voice.",
    max_tokens=200
)

print(response["choices"][0]["text"])
