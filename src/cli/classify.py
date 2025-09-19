"""
📦 Module: cli.classification
- @ai-path: cli.classification
- @ai-source-file: combined_cli.py
- @ai-role: CLI Entrypoint
- @ai-intent: "Expose classification and summarization routines as Typer CLI commands."

🔍 Module Summary:
This module provides Typer CLI commands to classify documents via Lambda-based Claude summarization. 
It supports both individual document classification and automated chunked classification for larger inputs. 
It is intended for fast integration into scalable document processing pipelines.

🗂️ Contents:

| Name           | Type     | Purpose                             |
|:---------------|:---------|:------------------------------------|
| classify       | CLI Command | Classify a single document using Claude summarization. |
| classify_large | CLI Command | Classify large documents by chunking and merging results. |

🧠 For AI Agents:
- @ai-dependencies: typer
- @ai-uses: main_commands.classify, main_commands.classify_large
- @ai-tags: cli, classification, summarization, Lambda, chunking

⚙️ Meta:
- @ai-version: 0.3.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add Typer commands for classification
- @change-summary: CLI passthrough to classify and classify_large workflows
- @notes: ""

👤 Human Overview:
    - Context: Classify new documents directly from the command line without needing manual uploads or processing.
    - Change Caution: Large document classification is chunk-based; be aware of chunking limits and recombination logic.
    - Future Hints: Allow manual override of chunk size or prompt template via CLI options.
"""


import typer

from core.workflows.main_commands import classify

app = typer.Typer()


@app.command()
def classify_one(
    name: str,
    chunked: bool = False,
    segmentation: str = "semantic",
):
    """Classify a single document (optionally in chunked mode)."""
    result = classify(name, chunked=chunked, segmentation=segmentation)
    print("✅ Metadata saved.")
    print(result)
