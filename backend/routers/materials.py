"""
Material generation and management endpoints.
"""

import os
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.routers._sse import SSE_HEADERS, run_streaming_job
from core.json_io import read_json, write_json

router = APIRouter(tags=["materials"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
MATERIALS_DIR = DATA_DIR / "materials"


class GenerateRequest(BaseModel):
    student_id: str
    goal_id: str = ""
    material_type: str  # lesson_plan, tracking_sheet, social_story, visual_schedule, first_then, parent_comm, admin_report
    scenario: str = ""  # for social stories
    routine: str = ""  # for visual schedules
    language: str = "en"  # ISO-639 code for parent_comm (en, es, vi, zh)
    approved_content: str = ""  # approved EN letter text — triggers translate mode for parent_comm


def _get_forge():
    """Create a MaterialForge instance with available client."""
    from agents.material_forge import MaterialForge

    if os.getenv("OPENROUTER_API_KEY") or (
        os.getenv("GOOGLE_AI_STUDIO_KEY")
        and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
    ):
        from core.gemma_client import GemmaClient
        return MaterialForge(GemmaClient())
    else:
        from tests.mock_api_responses import MockGemmaClient
        return MaterialForge(MockGemmaClient())


def _generate_material_sync(req: GenerateRequest) -> dict[str, Any]:
    """Blocking helper shared by the JSON and SSE material endpoints."""
    student_path = DATA_DIR / "students" / f"{req.student_id}.json"
    if not student_path.exists():
        raise LookupError(f"Student {req.student_id} not found")

    forge = _get_forge()
    today = date.today().isoformat()

    if req.material_type == "lesson_plan":
        result = forge.generate_lesson_plan(req.student_id, req.goal_id)
    elif req.material_type == "tracking_sheet":
        result = forge.generate_tracking_sheet(req.student_id, req.goal_id)
    elif req.material_type == "social_story":
        result = forge.generate_social_story(req.student_id, req.scenario or "classroom routine")
    elif req.material_type == "visual_schedule":
        result = forge.generate_visual_schedule(req.student_id, req.routine or "morning arrival")
    elif req.material_type == "first_then":
        if not req.goal_id:
            raise ValueError("first_then requires goal_id")
        result = forge.generate_first_then(req.student_id, req.goal_id)
    elif req.material_type == "parent_comm":
        if req.approved_content and req.language != "en":
            result = forge.translate_parent_comm(
                approved_content=req.approved_content, language=req.language,
            )
        else:
            result = forge.generate_parent_comm(
                req.student_id, req.goal_id, language=req.language
            )
    elif req.material_type == "admin_report":
        result = forge.generate_admin_report(req.student_id)
    else:
        raise ValueError(f"Unknown material type: {req.material_type}")

    mat_dir = MATERIALS_DIR / req.student_id
    mat_dir.mkdir(parents=True, exist_ok=True)

    material_record = {
        "student_id": req.student_id,
        "goal_id": req.goal_id,
        "material_type": req.material_type,
        "created_date": today,
        "status": "draft",
        "content": result,
        "language": req.language if req.material_type == "parent_comm" else "en",
    }
    filename = f"{req.material_type}_{req.goal_id or 'all'}_{today}.json"
    write_json(mat_dir / filename, material_record)

    return material_record


@router.post("/materials/generate")
async def generate_material(req: GenerateRequest) -> dict[str, Any]:
    """Generate a material for a student + goal (non-streaming)."""
    try:
        return _generate_material_sync(req)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/materials/generate/stream")
async def generate_material_stream(req: GenerateRequest) -> StreamingResponse:
    """Streaming variant of /materials/generate.

    Emits SSE heartbeat frames while Material Forge runs its 30-75s Gemma
    call in a worker thread, then the final ``result`` frame with the same
    material record the JSON endpoint returns. Required because the
    Turbopack dev proxy drops idle sockets at ~30s.
    """

    async def event_source():
        async for frame in run_streaming_job(
            lambda: _generate_material_sync(req),
            heartbeat_interval=4.0,
            heartbeat_message=f"Generating {req.material_type}…",
        ):
            yield frame

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


@router.get("/students/{student_id}/materials")
async def list_materials(student_id: str) -> list[dict[str, Any]]:
    """List all generated materials for a student."""
    mat_dir = MATERIALS_DIR / student_id
    if not mat_dir.exists():
        return []
    materials = []
    for json_file in sorted(mat_dir.glob("*.json"), reverse=True):
        data = read_json(json_file)
        data["id"] = json_file.stem
        materials.append(data)
    return materials


@router.put("/materials/{student_id}/{material_id}/approve")
async def approve_material(student_id: str, material_id: str) -> dict[str, str]:
    """Mark a material as approved."""
    mat_path = MATERIALS_DIR / student_id / f"{material_id}.json"
    if not mat_path.exists():
        raise HTTPException(status_code=404, detail="Material not found")
    data = read_json(mat_path)
    data["status"] = "approved"
    write_json(mat_path, data)
    return {"status": "approved", "id": material_id}
