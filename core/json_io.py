"""UTF-8 safe JSON file I/O for student profiles and model output caches.

Every caller in this codebase that opens a JSON file containing student
profile data, Gemma output, or trial history must route through here.

The bug this prevents: on Windows, Python's default open() encoding is
cp1252. Reading a UTF-8 JSON file with `open(path, "r")` silently decodes
bytes like 0xE2 0x89 0xA4 (U+2264, "≤") as three cp1252 chars ("â‰¤").
Writing back through json.dump with ensure_ascii=True (the stdlib default)
then escapes each of those chars as \\u00e2\\u2030\\u00a4, visibly
corrupting the file. See HANDOFF.md "Pipeline-writeback gotcha" and
MISTAKES.md #3 (same pattern for upload filenames).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

PathLike = Union[str, Path]


def read_json(path: PathLike) -> Any:
    """Read a UTF-8 JSON file and return the parsed value.

    Raises UnicodeDecodeError if the file is not valid UTF-8 — loud failure
    is the point. Callers that need to tolerate legacy encodings must
    explicitly convert upstream.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: PathLike, data: Any) -> None:
    """Write a value as pretty-printed UTF-8 JSON with literal non-ASCII.

    - encoding="utf-8" keeps round-trips idempotent on Windows.
    - ensure_ascii=False stores "≤" as the literal UTF-8 byte sequence
      instead of "\\u2264" escapes, making diffs human-readable.
    - indent=2 matches the canonical on-disk format used across data/.
    - default=str serializes datetime/date objects from Pydantic dumps.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
