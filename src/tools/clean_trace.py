import json
import re
import sys
from pathlib import Path

from src.core.logger import get_logger

logger = get_logger(__name__)

STRICT_DEBUG = False   # flip to False for normal behavior


def clean_trace_line(line: str) -> str:
    if line.strip().startswith("```") or not line.strip():
        return ""
    root_match = re.search(r"root@[^:\s]+[:#]", line)
    if root_match:
        return line[: root_match.start()].rstrip()
    return line.strip()


def truncate_to_sentences(text: str, max_sentences: int = 6, max_chars: int = 200) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+|(?<=[:;])\s+|(?<=\))\s+", text)
    truncated = " ".join(sentences[:max_sentences]).strip()
    truncated = truncated[:max_chars].rstrip()
    if len(text) > max_chars:
        truncated += " ..."
    return truncated


def extract_codex_reasoning(input_path: Path, output_md: Path, output_jsonl: Path = None):
    # --- Detect encoding
    try:
        raw_text = input_path.read_text(encoding="utf-8")
        encoding_used = "utf-8"
    except UnicodeDecodeError:
        raw_text = input_path.read_text(encoding="latin1")
        encoding_used = "latin1"

    lines = raw_text.splitlines()

    if STRICT_DEBUG:
        logger.info("[DEBUG] Processing %s", input_path)
        logger.info("[DEBUG] Encoding used: %s", encoding_used)
        logger.info("[DEBUG] First 5 raw lines:\n%s",
                    "\n".join(lines[:5]))

    prompt = None
    reasoning_steps = []
    current_step_lines = []
    step_id = 1

    step_start = re.compile(
        r"^(I['’]m|I am|Now I|Tests\s+|Let me|Next,|First,|Then,|To start|Time to|Hmm|Looks like|Looking for|I think|I meant|Here's the|There\s+|I see|I['’]ll|It looks|I suspect|I\s+|Trying the|The\s+|I'm going to|I'll|We can)\b",
        re.IGNORECASE,
    )

    for idx, raw_line in enumerate(lines, start=1):
        line = clean_trace_line(raw_line)
        if not line:
            continue

        if not prompt and line.lower().startswith("user:"):
            prompt = line[5:].strip()
            if STRICT_DEBUG:
                logger.info("[DEBUG] Found prompt at line %d: %s", idx, prompt)
            continue

        if step_start.match(line):
            if current_step_lines:
                combined = " ".join(current_step_lines).strip()
                reasoning_steps.append(
                    {"step": step_id, "text": truncate_to_sentences(combined)}
                )
                step_id += 1
                current_step_lines = []
            current_step_lines.append(line)
            if STRICT_DEBUG:
                logger.info("[DEBUG] Step start detected at line %d: %s", idx, line)
        else:
            current_step_lines.append(line)

    if current_step_lines:
        combined = " ".join(current_step_lines).strip()
        reasoning_steps.append(
            {"step": step_id, "text": truncate_to_sentences(combined)}
        )

    if STRICT_DEBUG:
        logger.info("[DEBUG] Total reasoning steps: %d", len(reasoning_steps))
        if not reasoning_steps:
            logger.warning("[DEBUG] No steps extracted from %s", input_path)

    # Save Markdown
    output_md.parent.mkdir(parents=True, exist_ok=True)
    with output_md.open("w", encoding="utf-8") as f:
        f.write("## 🧠 Codex Reasoning Chain\n\n")
        if prompt:
            f.write(f"> Prompt:\n> {prompt}\n\n---\n\n")
        for step in reasoning_steps:
            f.write(f"### 🪄 Step {step['step']}\n\n{step['text']}\n\n---\n\n")

    # Save JSONL if requested
    if output_jsonl:
        with output_jsonl.open("w", encoding="utf-8") as jf:
            for step in reasoning_steps:
                jf.write(json.dumps(step) + "\n")

    logger.info("Extracted %d reasoning steps", len(reasoning_steps))
    logger.info("Markdown: %s", output_md.name)
    if output_jsonl:
        logger.info("JSONL: %s", output_jsonl.name)


def bulk_process_dir(input_dir: Path, output_dir: Path):
    trace_files = (
        list(input_dir.rglob("*.trace.txt"))
        + list(input_dir.rglob("*.trace.md"))
        + list(input_dir.rglob("*.trace.jsonl"))
    )
    for trace in trace_files:
        rel_path = trace.relative_to(input_dir)
        out_md = output_dir / rel_path.with_suffix(".cleaned.md")
        out_jsonl = output_dir / rel_path.with_suffix(".cleaned.jsonl")
        extract_codex_reasoning(trace, out_md, out_jsonl)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage:")
        logger.error("  Single file : python clean_trace.py <input_file> <output_md> [<output_jsonl>]")
        logger.error("  Bulk mode   : python clean_trace.py <input_dir> <output_dir>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if input_path.is_dir():
        bulk_process_dir(input_path, output_path)
    else:
        extract_codex_reasoning(
            input_path=input_path,
            output_md=output_path,
            output_jsonl=Path(sys.argv[3]) if len(sys.argv) > 3 else None,
        )
