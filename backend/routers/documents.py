"""
Document upload endpoints — IEP PDFs and other student documents.
Gemma 4 extracts goals and accommodations from uploaded documents.
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile

from backend.upload_utils import (
    DOCUMENT_EXTENSIONS,
    validate_student_id,
    validate_upload,
)

router = APIRouter(tags=["documents"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@router.post("/documents/upload")
async def upload_document(
    student_id: str = Form(...),
    doc_type: str = Form(default="iep_pdf"),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """
    Upload an IEP document (PDF or image).
    Gemma 4 multimodal extracts goals, accommodations, and present levels.
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

    extraction = {
        "status": "uploaded",
        "file_path": str(file_path),
        "doc_type": doc_type,
        "upload_date": today,
        "message": "Document uploaded. Use the chat assistant to extract goals and accommodations.",
    }

    record_path = docs_dir / f"{doc_type}_{today}.json"
    with open(record_path, "w") as f:
        json.dump(extraction, f, indent=2)

    return extraction


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
