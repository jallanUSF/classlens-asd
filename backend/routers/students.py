"""
Student CRUD endpoints.
Reads/writes the same data/students/*.json files the agents use.
"""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["students"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STUDENTS_DIR = DATA_DIR / "students"


def _read_profile(student_id: str) -> dict:
    """Read a student JSON file. Raises HTTPException if not found."""
    path = STUDENTS_DIR / f"{student_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    with open(path, "r") as f:
        return json.load(f)


def _write_profile(student_id: str, data: dict):
    """Write a student JSON file."""
    STUDENTS_DIR.mkdir(parents=True, exist_ok=True)
    path = STUDENTS_DIR / f"{student_id}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


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
        with open(json_file, "r") as f:
            data = json.load(f)
        students.append(_student_summary(data))
    return students


@router.get("/students/{student_id}")
async def get_student(student_id: str) -> dict[str, Any]:
    """Get full student profile including goals and trial history."""
    return _read_profile(student_id)


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
    path = STUDENTS_DIR / f"{req.student_id}.json"
    if path.exists():
        raise HTTPException(status_code=409, detail=f"Student {req.student_id} already exists")
    data = req.model_dump()
    _write_profile(req.student_id, data)
    return data


@router.put("/students/{student_id}")
async def update_student(student_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    """Update an existing student profile. Merges updates into existing data."""
    data = _read_profile(student_id)
    data.update(updates)
    _write_profile(student_id, data)
    return data


@router.delete("/students/{student_id}")
async def delete_student(student_id: str) -> dict[str, str]:
    """Delete a student profile."""
    path = STUDENTS_DIR / f"{student_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    path.unlink()
    return {"status": "deleted", "student_id": student_id}
