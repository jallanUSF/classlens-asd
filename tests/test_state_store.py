"""
Tests for StateStore — CRUD operations on student JSON files.

Note: StateStore.load_student() uses Pydantic models that don't match
the actual JSON shape (known issue). These tests focus on the raw file
operations and the methods that do work correctly.
"""

import json
from pathlib import Path

import pytest

from core.state_store import StateStore


@pytest.fixture
def store(tmp_path):
    """Fresh StateStore in a temp directory."""
    return StateStore(data_dir=str(tmp_path))


@pytest.fixture
def store_with_data(tmp_path):
    """StateStore pre-populated with the three demo students."""
    src = Path(__file__).parent.parent / "data" / "students"
    dst = tmp_path / "students"
    dst.mkdir()
    for f in src.glob("*.json"):
        (dst / f.name).write_text(f.read_text())
    return StateStore(data_dir=str(tmp_path))


class TestDirectorySetup:
    def test_creates_directories(self, tmp_path):
        store = StateStore(data_dir=str(tmp_path / "new_dir"))
        assert store.data_dir.exists()
        assert store.students_dir.exists()


class TestGetAllStudents:
    def test_empty_store(self, store):
        assert store.get_all_students() == []

    def test_lists_students(self, store_with_data):
        students = store_with_data.get_all_students()
        assert sorted(students) == ["amara_2026", "ethan_2026", "jaylen_2026", "lily_2026", "marcus_2026", "maya_2026", "sofia_2026"]

    def test_sorted_alphabetically(self, store_with_data):
        students = store_with_data.get_all_students()
        assert students == sorted(students)


class TestRawFileOperations:
    """Test file-level operations without Pydantic serialization."""

    def test_student_file_exists(self, store_with_data):
        path = store_with_data._get_student_path("maya_2026")
        assert path.exists()

    def test_student_json_loadable(self, store_with_data):
        path = store_with_data._get_student_path("maya_2026")
        with open(path) as f:
            data = json.load(f)
        assert data["name"] == "Maya"
        assert data["grade"] == 3
        assert data["asd_level"] == 2
        assert len(data["iep_goals"]) == 3

    def test_delete_student(self, store_with_data):
        assert store_with_data.delete_student("maya_2026") is True
        assert "maya_2026" not in store_with_data.get_all_students()

    def test_delete_nonexistent(self, store_with_data):
        assert store_with_data.delete_student("nonexistent") is False

    def test_student_path(self, store):
        path = store._get_student_path("test_student")
        assert path.name == "test_student.json"
        assert path.parent == store.students_dir


class TestStudentDataIntegrity:
    """Verify the demo student JSON files have the expected structure."""

    def test_maya_profile(self, store_with_data):
        path = store_with_data._get_student_path("maya_2026")
        with open(path) as f:
            maya = json.load(f)
        assert maya["student_id"] == "maya_2026"
        assert maya["name"] == "Maya"
        assert maya["grade"] == 3
        assert maya["asd_level"] == 2
        assert len(maya["interests"]) > 0
        assert len(maya["reinforcers"]) > 0
        assert "sensory_profile" in maya
        # G1 should have trial history
        g1 = maya["iep_goals"][0]
        assert g1["goal_id"] == "G1"
        assert len(g1["trial_history"]) >= 5

    def test_jaylen_profile(self, store_with_data):
        path = store_with_data._get_student_path("jaylen_2026")
        with open(path) as f:
            jaylen = json.load(f)
        assert jaylen["student_id"] == "jaylen_2026"
        assert jaylen["asd_level"] == 3

    def test_sofia_profile(self, store_with_data):
        path = store_with_data._get_student_path("sofia_2026")
        with open(path) as f:
            sofia = json.load(f)
        assert sofia["student_id"] == "sofia_2026"
        assert sofia["asd_level"] == 1
