import re
import sys
import json
from pathlib import Path


def clean_trace_line(line: str) -> str:
    if line.strip().startswith("```") or not line.strip():
        return ""
    root_match = re.search(r'root@[^:\s]+[:#]', line)
    if root_match:
        return line[:root_match.start()].rstrip()
    return line.strip()


def truncate_to_sentences(text: str, max_sentences: int = 3) -> str:
    # Split by punctuation followed by whitespace or end-of-line
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) > max_sentences:
        return " ".join(sentences[:max_sentences]).strip() + " ..."
    return " ".join(sentences).strip()


def extract_codex_reasoning(input_path: str, output_md: str, output_jsonl: str = None):
    input_path = Path(input_path)
    output_md = Path(output_md)

    try:
        lines = input_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = input_path.read_text(encoding="latin1").splitlines()

    prompt = None
    reasoning_steps = []
    current_step_lines = []
    step_id = 1

    step_start = re.compile(
        r"^(I['’]m|I am|Now I|Tests\s+|Let me|Next,|First,|Then,|To start|Time to|Hmm|Looks like|Looking for|I think|I meant|Here's the|There\s+|I see|I['’]ll|It looks|I suspect|I\s+|Trying the|The\s+|I'm going to|I'll|We can)\b",
        re.IGNORECASE,
    )

    for raw_line in lines:
        line = clean_trace_line(raw_line)
        if not line:
            continue

        if not prompt and line.lower().startswith("user:"):
            prompt = line[5:].strip()
            continue

        if step_start.match(line):
            if current_step_lines:
                combined = " ".join(current_step_lines).strip()
                reasoning_steps.append({
                    "step": step_id,
                    "text": truncate_to_sentences(combined)
                })
                step_id += 1
                current_step_lines = []
            current_step_lines.append(line)
        else:
            current_step_lines.append(line)

    if current_step_lines:
        combined = " ".join(current_step_lines).strip()
        reasoning_steps.append({
            "step": step_id,
            "text": truncate_to_sentences(combined)
        })

    with output_md.open("w", encoding="utf-8") as f:
        f.write("## 🧠 Codex Reasoning Chain\n\n")
        if prompt:
            f.write(f"> Prompt:\n> {prompt}\n\n---\n\n")
        for step in reasoning_steps:
            f.write(f"### 🪄 Step {step['step']}\n\n{step['text']}\n\n---\n\n")

    if output_jsonl:
        with Path(output_jsonl).open("w", encoding="utf-8") as jf:
            for step in reasoning_steps:
                jf.write(json.dumps(step) + "\n")

    print(f"✅ Extracted {len(reasoning_steps)} reasoning steps")
    print(f"📝 Markdown saved to: {output_md}")
    if output_jsonl:
        print(f"📦 JSONL saved to: {output_jsonl}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python clean_trace.py <input_trace> <output_md> [<output_jsonl>]")
        sys.exit(1)

    extract_codex_reasoning(
        input_path=sys.argv[1],
        output_md=sys.argv[2],
        output_jsonl=sys.argv[3] if len(sys.argv) > 3 else None
    )
