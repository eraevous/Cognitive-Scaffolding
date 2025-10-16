from zen_of_spite import spite_verses
from core.logger import get_logger

logger = get_logger(__name__)


@app.command("spite")
def recite():   
    verses = "\n".join(f"• {v}" for v in spite_verses)
    logger.info("%s", verses)