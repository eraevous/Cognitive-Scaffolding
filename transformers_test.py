# Use a pipeline as a high-level helper
def helper():
    from transformers import pipeline
    pipe = pipeline("text-generation", model="Qwen/Qwen1.5-7B-Chat")
    messages = [
        {"role": "user", "content": "Who are you?"},
    ]
    return pipe(messages)

def direct():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-7B-Chat")
    model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen1.5-7B-Chat")
    messages = [
        {"role": "user", "content": "Who are you?"},
    ]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(**inputs, max_new_tokens=40)
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])

if __name__ == "__main__":
    print(helper())
    #print(direct())