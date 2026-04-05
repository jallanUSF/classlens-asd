"""
Document upload endpoints — IEP PDFs and other student documents.
Gemma 4 extracts goals and accommodations from uploaded documents.
"""

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

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
    docs_dir = DATA_DIR / "documents" / student_id
    docs_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filename = f"{doc_type}_{today}_{file.filename}"
    file_path = docs_dir / filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # TODO: Send to Gemma 4 multimodal for extraction
    # For now, return a stub extraction that the chat service will handle
    extraction = {
        "status": "uploaded",
        "file_path": str(file_path),
        "doc_type": doc_type,
        "upload_date": today,
        "message": "Document uploaded. Use the chat assistant to extract goals and accommodations.",
    }

    # Save record
    record_path = docs_dir / f"{doc_type}_{today}.json"
    with open(record_path, "w") as f:
        json.dump(extraction, f, indent=2)

    return extraction


@router.get("/students/{student_id}/documents")
async def list_documents(student_id: str) -> list[dict[str, Any]]:
    """List all uploaded documents for a student."""
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
