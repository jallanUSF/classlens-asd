"""
Document upload endpoints — IEP PDFs and other student documents.

On upload, Gemma 4 multimodal + function calling reads the document page(s)
and extracts IEP goals, accommodations, and any student demographic fields
that are visible. The extracted content is returned to the client and saved
alongside the raw file so it can be displayed in the Add Student flow and
reused by the chat assistant.
"""

import logging
import os
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from backend.routers._sse import SSE_HEADERS, run_streaming_job
from core.json_io import read_json, write_json
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


def _run_extraction(file_path: Path, safe_name: str) -> dict[str, Any]:
    """Blocking Gemma call + graceful degrade — shared by JSON and SSE paths."""
    try:
        extractor = _get_extractor()
        return extractor.extract(
            document_path=str(file_path),
            source_filename=safe_name,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("IEP extraction failed for %s: %s", file_path, exc)
        return {
            "student_name": "",
            "grade": None,
            "asd_level": None,
            "communication_level": "",
            "interests": [],
            "iep_goals": [],
            "accommodations": [],
            "notes": f"Extraction failed: {exc}",
        }


def _build_upload_response(
    extraction: dict[str, Any],
    file_path: Path,
    doc_type: str,
    today: str,
    safe_name: str,
) -> dict[str, Any]:
    goal_count = len(extraction.get("iep_goals") or [])
    accom_count = len(extraction.get("accommodations") or [])
    return {
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


def _persist_upload_record(
    docs_dir: Path, doc_type: str, today: str, response: dict[str, Any]
) -> None:
    record_path = docs_dir / f"{doc_type}_{today}.json"
    write_json(record_path, response)


def _save_upload_to_disk(
    student_id: str, doc_type: str, safe_name: str, file_bytes: bytes
) -> tuple[Path, Path, str]:
    """Persist the uploaded file and return (docs_dir, file_path, today)."""
    docs_dir = DATA_DIR / "documents" / student_id
    docs_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    filename = f"{doc_type}_{today}_{safe_name}"
    file_path = docs_dir / filename
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return docs_dir, file_path, today


@router.post("/documents/upload")
async def upload_document(
    student_id: str = Form(...),
    doc_type: str = Form(default="iep_pdf"),
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """
    Upload an IEP document (PDF or image) and extract its contents (non-streaming).

    Prefer /documents/upload/stream in the browser — this endpoint is kept
    for TestClient-based smoke tests and simple clients.
    """
    student_id = validate_student_id(student_id)
    safe_name, file_bytes = validate_upload(file, DOCUMENT_EXTENSIONS)

    docs_dir, file_path, today = _save_upload_to_disk(
        student_id, doc_type, safe_name, file_bytes
    )
    extraction = _run_extraction(file_path, safe_name)
    response = _build_upload_response(extraction, file_path, doc_type, today, safe_name)
    _persist_upload_record(docs_dir, doc_type, today, response)
    return response


@router.post("/documents/upload/stream")
async def upload_document_stream(
    student_id: str = Form(...),
    doc_type: str = Form(default="iep_pdf"),
    file: UploadFile = File(...),
) -> StreamingResponse:
    """Streaming variant of /documents/upload.

    Multipart upload still happens in a single request, but the Gemma
    multimodal extraction (which can take 30-75s on Google AI Studio) runs
    in a worker thread with SSE heartbeats so the Turbopack dev proxy
    doesn't drop the socket.
    """
    student_id = validate_student_id(student_id)
    safe_name, file_bytes = validate_upload(file, DOCUMENT_EXTENSIONS)
    docs_dir, file_path, today = _save_upload_to_disk(
        student_id, doc_type, safe_name, file_bytes
    )

    def job() -> dict[str, Any]:
        extraction = _run_extraction(file_path, safe_name)
        response = _build_upload_response(
            extraction, file_path, doc_type, today, safe_name
        )
        _persist_upload_record(docs_dir, doc_type, today, response)
        return response

    async def event_source():
        async for frame in run_streaming_job(
            job,
            heartbeat_interval=4.0,
            heartbeat_message="Extracting IEP content…",
        ):
            yield frame

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.get("/students/{student_id}/documents")
async def list_documents(student_id: str) -> list[dict[str, Any]]:
    """List all uploaded documents for a student."""
    student_id = validate_student_id(student_id)
    docs_dir = DATA_DIR / "documents" / student_id
    if not docs_dir.exists():
        return []

    documents = []
    for json_file in sorted(docs_dir.glob("*.json"), reverse=True):
        data = read_json(json_file)
        data["id"] = json_file.stem
        documents.append(data)
    return documents
