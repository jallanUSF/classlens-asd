"""
Capture endpoint — upload student work image and run the analysis pipeline.
"""

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

router = APIRouter(tags=["capture"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


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
    # Verify student exists
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    # Save uploaded image to documents folder
    docs_dir = DATA_DIR / "documents" / student_id
    docs_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    filename = f"{today}_{work_type}_{image.filename}"
    image_path = docs_dir / filename

    with open(image_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Run pipeline (reuses existing ClassLensPipeline)
    from core.pipeline import ClassLensPipeline
    from tests.mock_api_responses import MockGemmaClient
    import os

    if os.getenv("OPENROUTER_API_KEY") or (
        os.getenv("GOOGLE_AI_STUDIO_KEY")
        and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
    ):
        pipeline = ClassLensPipeline()
    else:
        pipeline = ClassLensPipeline(client=MockGemmaClient())

    result = pipeline.process_work_artifact(
        student_id=student_id,
        image_path=str(image_path),
        work_type=work_type,
        subject=subject,
        date=today,
    )

    # Save document record alongside the image
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
    record_path = docs_dir / f"{today}_{work_type}_{Path(image.filename).stem}.json"
    with open(record_path, "w") as f:
        json.dump(record, f, indent=2)

    return result
