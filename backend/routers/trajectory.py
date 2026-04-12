"""
Trajectory endpoint — long-context semester analysis for IEP meeting prep.
Uses Gemma 4's 256K context window to analyze all trial data in one call.
"""

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.routers._sse import SSE_HEADERS, run_streaming_job
from backend.sanitize import has_real_model_credentials, sanitize_model_text as _sanitize_model_text
from backend.upload_utils import validate_student_id
from core.json_io import read_json, write_json

load_dotenv()

router = APIRouter(tags=["trajectory"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _get_trajectory_analyst():
    """Create a TrajectoryAnalyst instance with a real or mock client."""
    from agents.trajectory_analyst import TrajectoryAnalyst

    if has_real_model_credentials():
        from core.gemma_client import GemmaClient
        return TrajectoryAnalyst(GemmaClient(), data_dir=str(DATA_DIR))
    else:
        from tests.mock_api_responses import MockGemmaClient
        return TrajectoryAnalyst(MockGemmaClient(), data_dir=str(DATA_DIR))


def _check_precomputed(student_id: str) -> dict | None:
    """Check for a precomputed trajectory result."""
    precomputed_path = DATA_DIR / "precomputed" / f"trajectory_{student_id}.json"
    if precomputed_path.exists():
        return read_json(precomputed_path)
    return None


def _run_trajectory(student_id: str) -> dict[str, Any]:
    """Blocking helper for trajectory analysis — used by both endpoints."""
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise LookupError(f"Student {student_id} not found")

    # Check precomputed cache first (demo never waits for API)
    precomputed = _check_precomputed(student_id)
    if precomputed:
        return precomputed

    analyst = _get_trajectory_analyst()
    result = analyst.analyze_trajectory(student_id)

    # Sanitize model text
    result["thinking"] = _sanitize_model_text(result.get("thinking", "") or "")
    if result.get("summary"):
        result["summary"] = _sanitize_model_text(result["summary"])
    for goal in result.get("goals", []):
        if goal.get("trend_summary"):
            goal["trend_summary"] = _sanitize_model_text(goal["trend_summary"])
        if goal.get("iep_meeting_note"):
            goal["iep_meeting_note"] = _sanitize_model_text(goal["iep_meeting_note"])

    # Cache the result for future requests
    cache_path = DATA_DIR / "precomputed" / f"trajectory_{student_id}.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(cache_path, result)

    return result


@router.post("/students/{student_id}/trajectory")
async def generate_trajectory(student_id: str) -> dict[str, Any]:
    """Generate a full-semester trajectory report for a student.

    Uses precomputed cache if available, otherwise runs live Gemma analysis.
    """
    student_id = validate_student_id(student_id)
    try:
        return _run_trajectory(student_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.exception("Trajectory analysis failed for student %s", student_id)
        raise HTTPException(status_code=502, detail="Trajectory analysis failed. Please try again later.")


@router.post("/students/{student_id}/trajectory/stream")
async def generate_trajectory_stream(student_id: str) -> StreamingResponse:
    """Streaming variant with SSE heartbeats for the Next.js dev proxy."""
    student_id = validate_student_id(student_id)
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    async def event_source():
        async for frame in run_streaming_job(
            lambda: _run_trajectory(student_id),
            heartbeat_interval=4.0,
            heartbeat_message="Analyzing semester trajectory…",
        ):
            yield frame

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
