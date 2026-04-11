"""
Capture endpoint — upload student work image and run the analysis pipeline.
"""

import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.upload_utils import (
    IMAGE_EXTENSIONS,
    validate_student_id,
    validate_upload,
)

load_dotenv()

router = APIRouter(tags=["capture"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _has_real_model_credentials() -> bool:
    if os.getenv("OPENROUTER_API_KEY"):
        return True
    google_key = os.getenv("GOOGLE_AI_STUDIO_KEY")
    return bool(google_key) and google_key != "your_api_key_here"


def _build_pipeline():
    """Construct the pipeline with a real client when credentials exist, mock otherwise."""
    from core.pipeline import ClassLensPipeline
    if _has_real_model_credentials():
        return ClassLensPipeline()
    # Dev/offline fallback — keep the test mock isolated from the production import path
    from tests.mock_api_responses import MockGemmaClient
    return ClassLensPipeline(client=MockGemmaClient())


@router.post("/capture")
async def capture_work(
    student_id: str = Form(...),
    work_type: str = Form(default="worksheet"),
    subject: str = Form(default="general"),
    image: UploadFile = File(...),
) -> dict:
    """
    Upload a student work image and run Vision Reader → IEP Mapper → Progress Analyst.
    Uses precomputed cache when available (demo mode).
    """
    student_id = validate_student_id(student_id)

    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    safe_name, image_bytes = validate_upload(image, IMAGE_EXTENSIONS)

    docs_dir = DATA_DIR / "documents" / student_id
    docs_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filename = f"{today}_{work_type}_{safe_name}"
    image_path = docs_dir / filename

    with open(image_path, "wb") as f:
        f.write(image_bytes)

    pipeline = _build_pipeline()
    result = pipeline.process_work_artifact(
        student_id=student_id,
        image_path=str(image_path),
        work_type=work_type,
        subject=subject,
        date=today,
    )

    record = {
        "student_id": student_id,
        "filename": filename,
        "doc_type": work_type,
        "upload_date": today,
        "subject": subject,
        "extraction": result.get("transcription", {}),
        "mapped_goals": [
            g["goal_id"] for g in result.get("goal_mapping", {}).get("matched_goals", [])
        ],
        "image_path": str(image_path),
    }
    record_path = docs_dir / f"{today}_{work_type}_{Path(safe_name).stem}.json"
    with open(record_path, "w") as f:
        json.dump(record, f, indent=2)

    return result
