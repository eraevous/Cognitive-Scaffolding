import typer

from core.agent_hub import run_agents

app = typer.Typer()


@app.command()
def run(prompt: str, roles: str = "synthesizer"):  # comma-separated
    """Run a simple multi-agent loop with given roles."""
    role_list = [r.strip() for r in roles.split(",") if r.strip()]
    run_agents(prompt, role_list)
