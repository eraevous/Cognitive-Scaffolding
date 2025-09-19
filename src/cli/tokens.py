import json
from pathlib import Path

import typer

from core.analysis.token_stats import TokenStats

# 👇  absolute path to the repo-local default
DEFAULT_CFG = Path(__file__).parent.parent / "core" / "config" / "path_config.json"

app = typer.Typer(help="Token-count utilities")


@app.command("summary")
def summary(
    config_file: Path = typer.Option(
        DEFAULT_CFG,  # <- uses your repo file by default
        exists=True,
        help="path_config.json (root / parsed keys). "
        "Pass a different file to override.",
    ),
    tokenizer: str = typer.Option("tiktoken:gpt-4o-mini"),
    show_hist: bool = False,
):
    """
    Count tokens in every *.txt under  <root>/<parsed>/…  using the paths config.
    """
    cfg = json.loads(config_file.read_text())

    try:
        parsed_dir = Path(cfg["root"]) / cfg["parsed"]
    except KeyError as e:
        typer.echo(f"❌ config missing key {e}", err=True)
        raise typer.Exit(1)

    stats = TokenStats.from_dir(parsed_dir, "*.txt", tokenizer)
    typer.echo(stats.describe())

    if show_hist and stats.counts:
        import numpy as np

        hist, edges = np.histogram(stats.counts, bins=10)
        for h, (lo, hi) in zip(hist, zip(edges[:-1], edges[1:])):
            bar = "█" * int(h / hist.max() * 30)
            typer.echo(f"{int(lo):>6,}–{int(hi):>6,} | {bar} {h}")


@app.command("spite")
def recite():
    from zen_of_spite import spite_verses

    print("\n".join(f"• {v}" for v in spite_verses))
