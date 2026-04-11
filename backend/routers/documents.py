"""
Document upload endpoints — IEP PDFs and other student documents.

On upload, Gemma 4 multimodal + function calling reads the document page(s)
and extracts IEP goals, accommodations, and any student demographic fields
that are visible. The extracted content is returned to the client and saved
alongside the raw file so it can be displayed in the Add Student flow and
reused by the chat assistant.
"""

import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from backend.upload_utils import (
    DOCUMENT_EXTENSIONS,
    validate_student_id,
    validate_upload,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["documents"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _get_extractor():
    """Build an IEPExtractor with whichever client the environment allows."""
    from agents.iep_extractor import IEPExtractor

    if os.getenv("OPENROUTER_API_KEY") or (
        os.getenv("GOOGLE_AI_STUDIO_KEY")
        and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
    ):
        from core.gemma_client import GemmaClient
        return IEPExtractor(GemmaClient())

    from tests.mock_api_responses import MockGemmaClient
    return IEPExtractor(MockGemmaClient())


@router.post("/documents/upload")
async def upload_document(
    student_id: str = Form(...),
    doc_type: str = Form(default="iep_pdf"),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """
    Upload an IEP document (PDF or image) and extract its contents.

    The uploaded file is persisted under data/documents/<student_id>/. After
    the file is saved, Gemma 4 multimodal extracts IEP goals, accommodations,
    and any student demographic fields that appear on the first two pages.
    The extracted content is returned in the ``extraction`` field and cached
    to disk as a sidecar JSON.
    """
    student_id = validate_student_id(student_id)
    safe_name, file_bytes = validate_upload(file, DOCUMENT_EXTENSIONS)

    docs_dir = DATA_DIR / "documents" / student_id
    docs_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filename = f"{doc_type}_{today}_{safe_name}"
    file_path = docs_dir / filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Run the real extraction. Never raise — degrade to an empty extraction
    # so the upload flow still succeeds if the model is unreachable.
    extraction: dict[str, Any]
    try:
        extractor = _get_extractor()
        extraction = extractor.extract(
            document_path=str(file_path),
            source_filename=safe_name,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("IEP extraction failed for %s: %s", file_path, exc)
        extraction = {
            "student_name": "",
            "grade": None,
            "asd_level": None,
            "communication_level": "",
            "interests": [],
            "iep_goals": [],
            "accommodations": [],
            "notes": f"Extraction failed: {exc}",
        }

    goal_count = len(extraction.get("iep_goals") or [])
    accom_count = len(extraction.get("accommodations") or [])

    response: dict[str, Any] = {
        "status": "uploaded",
        "file_path": str(file_path),
        "doc_type": doc_type,
        "upload_date": today,
        "extraction": extraction,
        "message": (
            f"Extracted {goal_count} IEP goal(s) and {accom_count} "
            f"accommodation(s) from {safe_name}."
        ),
    }

    record_path = docs_dir / f"{doc_type}_{today}.json"
    with open(record_path, "w") as f:
        json.dump(response, f, indent=2)

    return response


@router.get("/students/{student_id}/documents")
async def list_documents(student_id: str) -> list[dict[str, Any]]:
    """List all uploaded documents for a student."""
    student_id = validate_student_id(student_id)
    docs_dir = DATA_DIR / "documents" / student_id
    if not docs_dir.exists():
        return []

    documents = []
    for json_file in sorted(docs_dir.glob("*.json"), reverse=True):
        with open(json_file, "r") as f:
            data = json.load(f)
        data["id"] = json_file.stem
        documents.append(data)
    return documents
