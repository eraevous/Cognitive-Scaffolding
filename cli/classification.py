"""
Module: cli/classification.py 

- @ai-path: cli.classification 
- @ai-source-file: combined_cli.py 
- @ai-module: classification_cli 
- @ai-role: cli_entrypoint 
- @ai-entrypoint: classify(), classify_large() 
- @ai-intent: "Expose classification and summarization routines as Typer CLI commands."

🔍 Summary:
These CLI commands run document classification via Claude summarization Lambda. The `classify` command is for individual documents, while `classify_large` automatically chunks large documents and merges metadata.

📦 Inputs:
- name (str): Filename (raw or parsed) to classify

📤 Outputs:
- S3 `.meta.json` file (via internal `save_metadata_s3`)
- Printed feedback from classification or chunk merge

🔗 Related Modules:
- main_commands → executes actual logic
- lambda_summary → sends content to Claude
- metadata.schema → used to validate and upload metadata

🧠 For AI Agents:
- @ai-dependencies: typer
- @ai-calls: main_commands.classify, main_commands.classify_large
- @ai-uses: name, str, @app.command
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
- @notes: 
"""


import typer
from cli import clustering, utility
from core_lib.workflows import main_commands

app = typer.Typer()

# Register command groups
app.add_typer(clustering.app, name="cluster")
app.add_typer(utility.app, name="utils")

@app.command()
def classify(name: str):
    """Classify a single document."""
    main_commands.classify(name)

@app.command()
def classify_large(name: str):
    """Classify a large document in chunks."""
    main_commands.classify_large(name)