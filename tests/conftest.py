"""
Pytest fixtures for ClassLens ASD testing.

Provides mock clients, state store, and student profile fixtures
for use in all test modules.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

from tests.mock_api_responses import MockGemmaClient
from core.state_store import StateStore
from schemas.student_profile import StudentProfile


@pytest.fixture
def mock_client() -> MockGemmaClient:
    """
    Fixture providing a mock Gemma 4 API client.

    Returns:
        MockGemmaClient instance for testing without rate limits.
    """
    return MockGemmaClient()


@pytest.fixture
def state_store(tmp_path) -> StateStore:
    """
    Fixture providing a StateStore with test student data.

    Creates a temporary directory and populates it with all three
    student profiles for testing data persistence and retrieval.

    Args:
        tmp_path: pytest's temporary directory fixture

    Returns:
        StateStore instance pointing to temporary test directory
    """
    store = StateStore(data_dir=str(tmp_path))

    # Load all student profiles and save them to the temp store
    for student_json in _get_student_json_files():
        with open(student_json, "r") as f:
            student_data = json.load(f)
        # Save to test store
        student_path = store.students_dir / student_json.name
        with open(student_path, "w") as f:
            json.dump(student_data, f, indent=2)

    return store


@pytest.fixture
def sample_students(state_store: StateStore) -> Dict[str, StudentProfile]:
    """
    Fixture providing all three student profiles.

    Loads all available student profiles from the state store.

    Args:
        state_store: The StateStore fixture

    Returns:
        Dictionary mapping student_id to StudentProfile objects
    """
    students = {}
    for student_id in state_store.get_all_students():
        student = state_store.load_student(student_id)
        if student:
            students[student_id] = student
    return students


@pytest.fixture
def maya_profile(state_store: StateStore) -> StudentProfile:
    """
    Fixture providing Maya's student profile.

    Args:
        state_store: The StateStore fixture

    Returns:
        Maya's StudentProfile object (Grade 3, ASD Level 2)
    """
    return state_store.load_student("maya_2026")


@pytest.fixture
def jaylen_profile(state_store: StateStore) -> StudentProfile:
    """
    Fixture providing Jaylen's student profile.

    Args:
        state_store: The StateStore fixture

    Returns:
        Jaylen's StudentProfile object (Grade 1, ASD Level 3, non-verbal)
    """
    return state_store.load_student("jaylen_2026")


@pytest.fixture
def sofia_profile(state_store: StateStore) -> StudentProfile:
    """
    Fixture providing Sofia's student profile.

    Args:
        state_store: The StateStore fixture

    Returns:
        Sofia's StudentProfile object (Grade 5, ASD Level 1)
    """
    return state_store.load_student("sofia_2026")


# ==================== Helper Functions ====================


def _get_student_json_files() -> list:
    """
    Get paths to all student JSON profile files.

    Returns:
        List of Path objects pointing to student JSON files
    """
    data_dir = Path(__file__).parent.parent / "data" / "students"
    return sorted(data_dir.glob("*.json"))


@pytest.fixture(scope="session")
def student_data_dir() -> Path:
    """
    Fixture providing the path to student data directory.

    Returns:
        Path to the data/students directory
    """
    return Path(__file__).parent.parent / "data" / "students"
