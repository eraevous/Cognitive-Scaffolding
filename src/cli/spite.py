import typer

from core.logger import get_logger
from zen_of_spite import spite_verses

logger = get_logger(__name__)

app = typer.Typer()


@app.command("spite")
def recite():
    verses = "\n".join(f"• {v}" for v in spite_verses)
    logger.info("%s", verses)
