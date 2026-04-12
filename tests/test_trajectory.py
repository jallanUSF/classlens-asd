"""Tests for the Trajectory Analyst agent and endpoint."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


class TestTrajectoryEndpoint:
    """Test the trajectory API endpoint."""

    def test_trajectory_returns_precomputed_for_maya(self):
        """Maya has precomputed data — should return instantly."""
        resp = client.post("/api/students/maya_2026/trajectory")
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == "maya_2026"
        assert "summary" in data
        assert "goals" in data
        assert len(data["goals"]) == 3  # Maya has 3 IEP goals

    def test_trajectory_goal_fields(self):
        """Each goal in the trajectory should have required fields."""
        resp = client.post("/api/students/maya_2026/trajectory")
        data = resp.json()
        for goal in data["goals"]:
            assert "goal_id" in goal
            assert "domain" in goal
            assert goal["status"] in ("on_track", "at_risk", "stalled", "met")
            assert "current_pct" in goal
            assert "target_pct" in goal
            assert "baseline_pct" in goal
            assert "trend_summary" in goal
            assert goal["confidence"] in ("high", "moderate", "low")
            assert "iep_meeting_note" in goal

    def test_trajectory_amara_has_at_risk_goal(self):
        """Amara's G2 social communication should be flagged as at_risk."""
        resp = client.post("/api/students/amara_2026/trajectory")
        data = resp.json()
        g2 = next((g for g in data["goals"] if g["goal_id"] == "G2"), None)
        assert g2 is not None
        assert g2["status"] == "at_risk"

    def test_trajectory_jaylen_precomputed(self):
        """Jaylen has precomputed data — should return his trajectory."""
        resp = client.post("/api/students/jaylen_2026/trajectory")
        data = resp.json()
        assert data["student_id"] == "jaylen_2026"
        assert len(data["goals"]) == 3

    def test_trajectory_404_for_unknown_student(self):
        """Unknown student should return 404."""
        resp = client.post("/api/students/nonexistent_student/trajectory")
        assert resp.status_code == 404

    def test_trajectory_stream_endpoint(self):
        """Streaming endpoint should return SSE frames with the result."""
        resp = client.post(
            "/api/students/maya_2026/trajectory/stream",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        # SSE response contains data frames
        body = resp.text
        assert "data:" in body

    def test_trajectory_has_thinking_trace(self):
        """Precomputed data includes the thinking trace."""
        resp = client.post("/api/students/maya_2026/trajectory")
        data = resp.json()
        assert "thinking" in data
        assert len(data["thinking"]) > 0

    def test_trajectory_has_cross_goal_patterns(self):
        """Report should include cross-goal analysis."""
        resp = client.post("/api/students/amara_2026/trajectory")
        data = resp.json()
        assert data.get("cross_goal_patterns") is not None
        assert len(data["cross_goal_patterns"]) > 0

    def test_trajectory_has_recommended_priority(self):
        """Report should include a recommended priority."""
        resp = client.post("/api/students/maya_2026/trajectory")
        data = resp.json()
        assert "recommended_priority" in data
        assert len(data["recommended_priority"]) > 0


class TestTrajectoryAnalystAgent:
    """Test the TrajectoryAnalyst agent directly."""

    def test_agent_formats_goals_block(self):
        """Goals block formatter should produce readable output."""
        from tests.mock_api_responses import MockGemmaClient
        from agents.trajectory_analyst import TrajectoryAnalyst

        analyst = TrajectoryAnalyst(MockGemmaClient(), data_dir="data")
        profile = analyst._load_student_raw("maya_2026", "data")
        block = analyst._format_goals_block(profile)

        assert "G1" in block
        assert "G2" in block
        assert "G3" in block
        assert "communication" in block
        assert "Date" in block  # trial table header

    def test_agent_formats_alerts_block(self):
        """Alerts block should return a string (empty or populated)."""
        from tests.mock_api_responses import MockGemmaClient
        from agents.trajectory_analyst import TrajectoryAnalyst

        analyst = TrajectoryAnalyst(MockGemmaClient(), data_dir="data")
        block = analyst._format_alerts_block("maya_2026")
        assert isinstance(block, str)
