"""
Podcast briefing endpoints — Gemma writes a Host/Guest dialogue script,
Edge TTS synthesizes it to MP3, frontend plays it back.

Three endpoints:
  POST /api/students/{id}/podcast/stream  — SSE generation with heartbeats
  GET  /api/students/{id}/podcast         — cached script JSON + audio URL
  GET  /api/podcast/audio/{id}.mp3        — serves the MP3 bytes
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from backend.routers._sse import SSE_HEADERS, run_streaming_job
from backend.sanitize import has_real_model_credentials, sanitize_model_text
from backend.upload_utils import validate_student_id
from core.json_io import read_json, write_json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["podcast"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
PRECOMPUTED_DIR = DATA_DIR / "precomputed"


def _script_path(student_id: str) -> Path:
    return PRECOMPUTED_DIR / f"podcast_{student_id}.json"


def _audio_path(student_id: str) -> Path:
    return PRECOMPUTED_DIR / f"podcast_{student_id}.mp3"


def _get_producer():
    from agents.podcast_producer import PodcastProducer

    if has_real_model_credentials():
        from core.gemma_client import GemmaClient
        return PodcastProducer(GemmaClient(), data_dir=str(DATA_DIR))
    from tests.mock_api_responses import MockGemmaClient
    return PodcastProducer(MockGemmaClient(), data_dir=str(DATA_DIR))


def _build_response_payload(student_id: str, script_data: dict) -> dict[str, Any]:
    """Attach audio_url to a cached script record for frontend consumption."""
    payload = dict(script_data)
    payload["audio_url"] = f"/api/podcast/audio/{student_id}.mp3"
    return payload


def _run_generation(student_id: str, language: str = "en") -> dict[str, Any]:
    """Blocking helper — produces script + MP3 and writes both to precomputed/."""
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise LookupError(f"Student {student_id} not found")

    producer = _get_producer()
    result = producer.produce_script(student_id, language=language)

    # Sanitize free-form model text before persisting
    result["thinking"] = sanitize_model_text(result.get("thinking", "") or "")
    for line in result.get("script", []):
        if isinstance(line, dict) and line.get("text"):
            line["text"] = sanitize_model_text(line["text"])

    # Synthesize MP3 via Edge TTS
    from core import tts_client

    mp3_bytes = tts_client.synthesize_script(result.get("script", []), language=language)

    PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)
    _audio_path(student_id).write_bytes(mp3_bytes)
    write_json(_script_path(student_id), result)

    return _build_response_payload(student_id, result)


@router.post("/students/{student_id}/podcast/stream")
async def generate_podcast_stream(student_id: str) -> StreamingResponse:
    """Generate a fresh podcast for this student, streamed with SSE heartbeats."""
    student_id = validate_student_id(student_id)
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    heartbeats = [
        "Analyzing student data…",
        "Writing script…",
        "Synthesizing audio…",
        "Finalizing…",
    ]
    # Single heartbeat message is fine — the skill spec listed the phases for UX
    # copy, not as separate stream messages. We rotate through them via the
    # ``heartbeat_message`` so users see progress evolve.
    async def event_source():
        async for frame in run_streaming_job(
            lambda: _run_generation(student_id),
            heartbeat_interval=4.0,
            heartbeat_message=heartbeats[0],
        ):
            yield frame

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.get("/students/{student_id}/podcast")
async def get_podcast(student_id: str) -> dict[str, Any]:
    """Return the cached podcast script + audio URL for this student."""
    student_id = validate_student_id(student_id)
    path = _script_path(student_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="No podcast generated for this student yet.")
    data = read_json(path)
    return _build_response_payload(student_id, data)


@router.get("/podcast/audio/{filename}")
async def get_podcast_audio(filename: str):
    """Serve the cached MP3. Filename must be <student_id>.mp3 — validated."""
    # Expect exactly "<student_id>.mp3" — strip and validate the student_id half
    if not filename.endswith(".mp3"):
        raise HTTPException(status_code=404, detail="Not found")
    student_id = filename[:-4]
    student_id = validate_student_id(student_id)  # path-traversal guard

    path = _audio_path(student_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio not generated yet.")
    # Serve inline (no Content-Disposition: attachment) so <audio> elements
    # play it directly. The frontend sets a download filename via <a download>
    # when the user clicks Download.
    return FileResponse(
        path,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-cache"},
    )
