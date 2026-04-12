"""
Capture endpoint — upload student work image or voice note and run the pipeline.
"""

import base64
import os
from datetime import date
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from core.json_io import read_json, write_json
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.routers._sse import SSE_HEADERS, run_streaming_job
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
    write_json(record_path, record)

    return result


# ── Voice Capture ─────────────────────────────────────────────

AUDIO_MIME_TYPES = {
    "audio/webm", "audio/wav", "audio/mp3", "audio/mpeg",
    "audio/ogg", "audio/m4a", "audio/mp4",
}


class VoiceCaptureRequest(BaseModel):
    student_id: str
    audio_b64: str  # base64-encoded audio
    media_type: str = "audio/webm"
    text_fallback: str = ""  # For non-google providers: typed observation


def _get_voice_reader():
    """Create a VoiceReader with real or mock client."""
    from agents.voice_reader import VoiceReader

    if _has_real_model_credentials():
        from core.gemma_client import GemmaClient
        return VoiceReader(GemmaClient(), data_dir=str(DATA_DIR))
    else:
        from tests.mock_api_responses import MockGemmaClient
        return VoiceReader(MockGemmaClient(), data_dir=str(DATA_DIR))


def _is_google_provider() -> bool:
    """Check if the current provider supports audio."""
    provider = os.getenv("MODEL_PROVIDER", "google").lower()
    return provider == "google"


def _run_voice_capture(req: VoiceCaptureRequest) -> dict:
    """Blocking helper for voice capture — used by both endpoints."""
    student_id = validate_student_id(req.student_id)
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise LookupError(f"Student {student_id} not found")

    # Check precomputed cache
    precomputed = DATA_DIR / "precomputed" / f"voice_{student_id}.json"
    if precomputed.exists():
        return read_json(precomputed)

    reader = _get_voice_reader()

    # If non-google provider or text fallback provided, use text mode
    if not _is_google_provider() or (req.text_fallback and not req.audio_b64):
        if not req.text_fallback:
            return {
                "error": "audio_not_supported",
                "fallback": "text_input",
                "message": "Audio input requires Google AI Studio provider. Please type your observation instead.",
            }
        return reader.transcribe_from_text(req.text_fallback, student_id)

    # Decode audio and process
    if req.media_type not in AUDIO_MIME_TYPES:
        raise ValueError(f"Unsupported audio type: {req.media_type}. Supported: {', '.join(sorted(AUDIO_MIME_TYPES))}")

    audio_bytes = base64.b64decode(req.audio_b64)
    if len(audio_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError("Audio file too large (max 10MB)")

    return reader.transcribe_and_extract(
        audio_bytes=audio_bytes,
        mime_type=req.media_type,
        student_id=student_id,
    )


@router.post("/capture/voice")
async def capture_voice(req: VoiceCaptureRequest) -> dict:
    """
    Capture a teacher voice observation and extract structured trial data.

    Requires Google AI Studio provider for audio processing.
    Falls back to text mode on other providers.
    """
    try:
        return _run_voice_capture(req)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Voice capture failed: {e}")


@router.post("/capture/voice/stream")
async def capture_voice_stream(req: VoiceCaptureRequest) -> StreamingResponse:
    """Streaming variant with SSE heartbeats for voice capture."""
    student_id = validate_student_id(req.student_id)
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    async def event_source():
        async for frame in run_streaming_job(
            lambda: _run_voice_capture(req),
            heartbeat_interval=4.0,
            heartbeat_message="Processing voice observation…",
        ):
            yield frame

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.get("/capture/voice/supported")
async def voice_supported() -> dict:
    """Check if voice capture is supported with the current provider."""
    return {
        "supported": _is_google_provider(),
        "provider": os.getenv("MODEL_PROVIDER", "google").lower(),
        "fallback": "text_input" if not _is_google_provider() else None,
    }
