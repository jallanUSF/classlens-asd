"""
Student CRUD endpoints.
Reads/writes the same data/students/*.json files the agents use.
"""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.upload_utils import validate_student_id
from core.json_io import read_json, write_json

router = APIRouter(tags=["students"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STUDENTS_DIR = DATA_DIR / "students"


def _read_profile(student_id: str) -> dict:
    """Read a student JSON file. Raises HTTPException if not found."""
    path = STUDENTS_DIR / f"{student_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return read_json(path)


def _write_profile(student_id: str, data: dict):
    """Write a student JSON file."""
    STUDENTS_DIR.mkdir(parents=True, exist_ok=True)
    path = STUDENTS_DIR / f"{student_id}.json"
    write_json(path, data)


def _student_summary(data: dict) -> dict:
    """Extract sidebar-friendly summary from full profile."""
    goals = data.get("iep_goals", [])
    total_sessions = sum(len(g.get("trial_history", [])) for g in goals)
    return {
        "student_id": data.get("student_id", ""),
        "name": data.get("name", ""),
        "grade": data.get("grade", 0),
        "asd_level": data.get("asd_level", 1),
        "communication_level": data.get("communication_level", "verbal"),
        "interests": data.get("interests", []),
        "goal_count": len(goals),
        "session_count": total_sessions,
        "last_session_date": data.get("last_session_date"),
    }


@router.get("/students")
async def list_students() -> list[dict[str, Any]]:
    """List all students with sidebar-friendly summaries."""
    if not STUDENTS_DIR.exists():
        return []
    students = []
    for json_file in sorted(STUDENTS_DIR.glob("*.json")):
        data = read_json(json_file)
        students.append(_student_summary(data))
    return students


_COUNT_BASED_HINTS = ("fewer", "reduce", "outburst", "incident", "per day")


def _annotate_goal_target(goal: dict) -> None:
    """Annotate a goal with frontend-friendly target fields.

    Distinguishes percentage-based goals ("80% across 10 trials") from
    count-based goals ("1 or fewer outbursts per day"). Count-based goals
    have small raw targets and the trial_history.pct already represents
    percent of sessions meeting the target, so the progress bar fills to
    target_pct=100 when current_pct reaches 100.
    """
    raw_target = goal.get("target", 0)
    description = str(goal.get("description", "")).lower()

    is_count_based = (
        isinstance(raw_target, (int, float))
        and raw_target <= 10
        and any(hint in description for hint in _COUNT_BASED_HINTS)
    )

    if is_count_based:
        goal["target_pct"] = 100
        goal["target_unit"] = "count_per_day"
        goal["target_value"] = raw_target
        goal["target_display"] = f"≤{raw_target}/day"
    else:
        goal["target_pct"] = goal.get("target_pct", raw_target)
        goal["target_unit"] = "percent"
        goal["target_value"] = raw_target
        goal["target_display"] = f"{raw_target}%"

    history = goal.get("trial_history", [])
    if "current_pct" not in goal and history:
        goal["current_pct"] = history[-1].get("pct", 0)
    elif "current_pct" not in goal:
        goal["current_pct"] = goal.get("baseline", {}).get("value", 0)


@router.get("/students/{student_id}")
async def get_student(student_id: str) -> dict[str, Any]:
    """Get full student profile including goals and trial history."""
    student_id = validate_student_id(student_id)
    data = _read_profile(student_id)
    for goal in data.get("iep_goals", []):
        _annotate_goal_target(goal)
    return data


class CreateStudentRequest(BaseModel):
    student_id: str
    name: str
    grade: int
    asd_level: int = 1
    communication_level: str = "verbal"
    interests: list[str] = []
    sensory_profile: dict = {}
    iep_goals: list[dict] = []


@router.post("/students", status_code=201)
async def create_student(req: CreateStudentRequest) -> dict[str, Any]:
    """Create a new student profile."""
    validate_student_id(req.student_id)
    path = STUDENTS_DIR / f"{req.student_id}.json"
    if path.exists():
        raise HTTPException(status_code=409, detail=f"Student {req.student_id} already exists")
    data = req.model_dump()
    _write_profile(req.student_id, data)
    return data


@router.put("/students/{student_id}")
async def update_student(student_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Update an existing student profile. Merges updates into existing data."""
    student_id = validate_student_id(student_id)
    data = _read_profile(student_id)
    data.update(updates)
    _write_profile(student_id, data)
    return data


@router.delete("/students/{student_id}")
async def delete_student(student_id: str) -> dict[str, str]:
    """Delete a student profile."""
    student_id = validate_student_id(student_id)
    path = STUDENTS_DIR / f"{student_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    path.unlink()
    return {"status": "deleted", "student_id": student_id}
