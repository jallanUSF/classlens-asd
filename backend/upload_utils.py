"""
Shared upload validation for file-upload endpoints.

Enforces:
- Maximum file size (default 10 MB)
- Extension allowlist (images: png/jpg/jpeg/webp; documents: pdf + images)
- Safe filename construction (strips path traversal, control chars, and reserved names)
- Safe student_id (blocks path traversal into other students' directories)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".webp"})
DOCUMENT_EXTENSIONS = frozenset({".pdf", ".png", ".jpg", ".jpeg", ".webp"})

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
_SAFE_STUDENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_student_id(student_id: str) -> str:
    """Reject student IDs that could escape the students directory."""
    if not student_id or not _SAFE_STUDENT_ID_RE.match(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student_id: only letters, digits, underscore, and hyphen allowed.",
        )
    return student_id


def safe_filename(raw_name: str) -> str:
    """Return a filesystem-safe filename derived from a client-supplied name.

    Strips any path components, replaces unsafe characters with underscore,
    collapses to the basename only, and ensures a non-empty result.
    """
    if not raw_name:
        return "upload"
    # Strip any directory prefix (handles ../, absolute paths, Windows backslashes)
    base = Path(raw_name.replace("\\", "/")).name
    # Replace unsafe chars
    cleaned = _SAFE_FILENAME_RE.sub("_", base).strip("._")
    return cleaned or "upload"


def validate_upload(
    upload: UploadFile,
    allowed_extensions: Iterable[str],
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> tuple[str, bytes]:
    """Validate an UploadFile and return (safe_filename, file_bytes).

    Reads the full file into memory to enforce the byte limit — acceptable
    for a ~10 MB cap on a demo app. For larger uploads, switch to streaming
    with chunked size tracking.

    Raises HTTPException with 400 (bad extension), 413 (too large), or 422
    (missing filename / empty file).
    """
    if not upload.filename:
        raise HTTPException(status_code=422, detail="Upload is missing a filename.")

    name = safe_filename(upload.filename)
    ext = Path(name).suffix.lower()
    allowed = frozenset(e.lower() for e in allowed_extensions)
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(allowed)}",
        )

    # Read with a hard cap — if more bytes remain, reject.
    data = upload.file.read(max_bytes + 1)
    if not data:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {max_bytes // (1024 * 1024)} MB limit.",
        )

    return name, data
