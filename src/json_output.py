"""Write JSON atomically so a failed translation preserves the old file."""

import json
import os
from tempfile import NamedTemporaryFile


def write_json(path, value):
    """Serialize UTF-8 JSON and replace the destination after a full write."""
    document = json.dumps(
        value, ensure_ascii=False, indent=2, allow_nan=False,
    ) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = stream.name
            stream.write(document)
        os.replace(temporary, path)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
