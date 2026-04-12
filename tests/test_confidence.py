"""Tests for the confidence panel — Material Forge thinking mode + flag endpoint."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestConfidenceScoring:
    """Test that materials include confidence_score and thinking fields."""

    def test_generate_material_has_confidence(self):
        """Generated materials should include confidence_score."""
        resp = client.post(
            "/api/materials/generate",
            json={
                "student_id": "maya_2026",
                "goal_id": "G1",
                "material_type": "lesson_plan",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "confidence_score" in data
        assert data["confidence_score"] in ("high", "review_recommended", "flag_for_expert")

    def test_generate_material_has_thinking(self):
        """Generated materials should include thinking trace."""
        resp = client.post(
            "/api/materials/generate",
            json={
                "student_id": "maya_2026",
                "goal_id": "G1",
                "material_type": "lesson_plan",
            },
        )
        data = resp.json()
        assert "thinking" in data
        assert isinstance(data["thinking"], str)

    def test_existing_materials_have_confidence(self):
        """Migrated materials should have confidence_score."""
        resp = client.get("/api/students/maya_2026/materials")
        assert resp.status_code == 200
        materials = resp.json()
        assert len(materials) > 0
        for mat in materials:
            assert "confidence_score" in mat, f"Material {mat.get('id')} missing confidence_score"

    def test_confidence_not_in_content(self):
        """_thinking and _confidence_score should be extracted, not left in content."""
        resp = client.post(
            "/api/materials/generate",
            json={
                "student_id": "maya_2026",
                "goal_id": "G1",
                "material_type": "lesson_plan",
            },
        )
        data = resp.json()
        content = data.get("content", {})
        assert "_thinking" not in content
        assert "_confidence_score" not in content


class TestFlagEndpoint:
    """Test the flag-for-review endpoint."""

    def test_flag_material(self, tmp_path):
        """Flagging a material should update its status."""
        # First generate a material
        gen_resp = client.post(
            "/api/materials/generate",
            json={
                "student_id": "maya_2026",
                "goal_id": "G1",
                "material_type": "lesson_plan",
            },
        )
        assert gen_resp.status_code == 200

        # List materials to get the ID
        list_resp = client.get("/api/students/maya_2026/materials")
        materials = list_resp.json()
        assert len(materials) > 0
        mat_id = materials[0]["id"]

        # Flag it
        flag_resp = client.post(
            f"/api/materials/maya_2026/{mat_id}/flag",
            json={"reason": "Needs expert review"},
        )
        assert flag_resp.status_code == 200
        assert flag_resp.json()["status"] == "flagged"

    def test_flag_nonexistent_material(self):
        """Flagging a nonexistent material should 404."""
        resp = client.post(
            "/api/materials/maya_2026/nonexistent_material/flag",
            json={"reason": "test"},
        )
        assert resp.status_code == 404


class TestComputeConfidence:
    """Test the confidence scoring logic directly."""

    def test_high_confidence_with_data(self):
        """Student with >5 trials and no hedge terms should be high confidence."""
        from tests.mock_api_responses import MockGemmaClient
        from agents.material_forge import MaterialForge

        forge = MaterialForge(MockGemmaClient(), data_dir="data")
        # Maya has 7+ trials per goal
        score = forge._compute_confidence(
            thinking="Clear upward trajectory, consistent improvement noted.",
            student_id="maya_2026",
        )
        assert score == "high"

    def test_low_confidence_with_hedge_language(self):
        """Thinking trace with multiple hedge terms should flag for expert."""
        from tests.mock_api_responses import MockGemmaClient
        from agents.material_forge import MaterialForge

        forge = MaterialForge(MockGemmaClient(), data_dir="data")
        score = forge._compute_confidence(
            thinking="Limited data available. Unable to determine trend. Unclear whether this is sufficient. No prior observations found.",
            student_id="maya_2026",
        )
        assert score == "flag_for_expert"

    def test_medium_confidence_with_some_hedging(self):
        """Single hedge term should produce review_recommended."""
        from tests.mock_api_responses import MockGemmaClient
        from agents.material_forge import MaterialForge

        forge = MaterialForge(MockGemmaClient(), data_dir="data")
        score = forge._compute_confidence(
            thinking="Good progress overall. One area is unclear but the trend is positive.",
            student_id="maya_2026",
        )
        assert score == "review_recommended"
