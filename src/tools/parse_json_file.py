import argparse
import json
from pathlib import Path

from core.logger import get_logger


def extract_and_parse_text(json_path):
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_text = data.get("text", "")
    return raw_text  # Already decoded correctly by json.load


def main():
    logger = get_logger(__name__)
    parser = argparse.ArgumentParser(
        description="Extract and print the 'text' field from a JSON file."
    )
    parser.add_argument("file", help="Path to JSON file containing a 'text' field.")
    args = parser.parse_args()

    try:
        parsed_text = extract_and_parse_text(args.file)
        logger.info("%s", parsed_text)
    except Exception as e:
        logger.error("Error: %s", e)


if __name__ == "__main__":
    main()
