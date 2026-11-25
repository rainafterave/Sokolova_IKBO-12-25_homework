"""Translate standard input from variant 23 syntax to a JSON file."""

import argparse
import json
import sys
from pathlib import Path

from language import LanguageError, parse


def main(argv=None):
    """Read UTF-8 source and write its translated value to --output."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.buffer.read().decode("utf-8-sig")
        result = parse(source)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False),
            encoding="utf-8",
        )
    except (LanguageError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
