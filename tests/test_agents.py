"""
Tests for the four ClassLens agents using MockGemmaClient.
Validates each agent produces well-structured output from mock responses.
"""

import json
import shutil
from pathlib import Path

import pytest

from tests.mock_api_responses import MockGemmaClient
from agents.vision_reader import VisionReader
from agents.iep_mapper import IEPMapper
from agents.progress_analyst import ProgressAnalyst
from agents.material_forge import MaterialForge


DATA_DIR = str(Path(__file__).parent.parent / "data")
SAMPLE_WORK = Path(__file__).parent.parent / "data" / "sample_work"


@pytest.fixture
def client():
    return MockGemmaClient()


@pytest.fixture
def data_dir(tmp_path):
    """Copy student data to a temp dir so tests don't mutate real data."""
    src = Path(DATA_DIR) / "students"
    dst = tmp_path / "students"
    shutil.copytree(src, dst)
    return str(tmp_path)


# ── Vision Reader ────────────────────────────────────────────

class TestVisionReader:
    def test_transcribe_maya_math(self, client):
        reader = VisionReader(client)
        result = reader.transcribe(
            image_path=str(SAMPLE_WORK / "maya_math_worksheet.png"),
            student_name="Maya",
            grade=3,
            asd_level=2,
            work_type="worksheet",
        )
        assert isinstance(result, dict)
        assert result["student_name"] == "Maya"
        assert result["work_type"] == "worksheet"
        assert result["accuracy_pct"] == 100
        assert len(result["task_items"]) == 3

    def test_transcribe_jaylen_checklist(self, client):
        reader = VisionReader(client)
        result = reader.transcribe(
            image_path=str(SAMPLE_WORK / "jaylen_task_checklist.png"),
            student_name="Jaylen",
            grade=1,
            asd_level=3,
            work_type="checklist",
        )
        assert result["student_name"] == "Jaylen"
        assert result["total_items"] == 5
        assert result["correct_items"] == 5

    def test_transcribe_sofia_writing(self, client):
        reader = VisionReader(client)
        result = reader.transcribe(
            image_path=str(SAMPLE_WORK / "sofia_writing_sample.png"),
            student_name="Sofia",
            grade=5,
            asd_level=1,
            work_type="free_response",
        )
        assert result["student_name"] == "Sofia"
        assert result["subject"] == "writing"

    def test_transcribe_unknown_image(self, client):
        reader = VisionReader(client)
        result = reader.transcribe(
            image_path="fake_image.png",
            student_name="Test",
            grade=1,
            asd_level=1,
            work_type="worksheet",
        )
        assert isinstance(result, dict)
        assert "raw_text" in result


# ── IEP Mapper ───────────────────────────────────────────────

class TestIEPMapper:
    def test_map_maya_goals(self, client, data_dir):
        mapper = IEPMapper(client, data_dir=data_dir)
        transcription = {"raw_text": "Maya's math worksheet", "accuracy_pct": 100}
        result = mapper.map_to_goals(
            student_id="maya_2026",
            transcription=transcription,
            work_type="worksheet",
        )
        assert "matched_goals" in result
        assert len(result["matched_goals"]) >= 1
        # Check goals have required fields
        for goal in result["matched_goals"]:
            assert "goal_id" in goal
            assert "percentage" in goal

    def test_map_jaylen_goals(self, client, data_dir):
        mapper = IEPMapper(client, data_dir=data_dir)
        result = mapper.map_to_goals(
            student_id="jaylen_2026",
            transcription={"raw_text": "Jaylen's checklist"},
            work_type="checklist",
        )
        assert "matched_goals" in result
        matched_ids = [g["goal_id"] for g in result["matched_goals"]]
        assert "G1" in matched_ids

    def test_trial_data_recorded(self, client, data_dir):
        """IEP Mapper should append trial data to student JSON."""
        mapper = IEPMapper(client, data_dir=data_dir)

        # Load original trial count
        student_path = Path(data_dir) / "students" / "maya_2026.json"
        with open(student_path) as f:
            original = json.load(f)
        original_g1_trials = len(original["iep_goals"][0]["trial_history"])

        mapper.map_to_goals(
            student_id="maya_2026",
            transcription={"raw_text": "Maya's behavior tally"},
            work_type="tally_sheet",
        )

        # Reload and check trial was appended
        with open(student_path) as f:
            updated = json.load(f)
        new_g1_trials = len(updated["iep_goals"][0]["trial_history"])
        assert new_g1_trials == original_g1_trials + 1


# ── Progress Analyst ─────────────────────────────────────────

class TestProgressAnalyst:
    def test_analyze_maya_g1(self, client, data_dir):
        analyst = ProgressAnalyst(client, data_dir=data_dir)
        result = analyst.analyze(student_id="maya_2026", goal_id="G1")
        assert result["goal_id"] == "G1"
        assert result["student_id"] == "maya_2026"
        assert "thinking" in result
        assert len(result["thinking"]) > 0
        assert "trend" in result

    def test_analyze_all_goals(self, client, data_dir):
        analyst = ProgressAnalyst(client, data_dir=data_dir)
        results = analyst.analyze_all_goals(student_id="maya_2026")
        assert len(results) == 3  # Maya has 3 IEP goals
        goal_ids = [r["goal_id"] for r in results]
        assert "G1" in goal_ids
        assert "G2" in goal_ids
        assert "G3" in goal_ids

    def test_analyze_invalid_goal(self, client, data_dir):
        analyst = ProgressAnalyst(client, data_dir=data_dir)
        with pytest.raises(ValueError, match="not found"):
            analyst.analyze(student_id="maya_2026", goal_id="G99")


# ── Material Forge ───────────────────────────────────────────

class TestMaterialForge:
    def test_generate_lesson_plan(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_lesson_plan(student_id="maya_2026", goal_id="G1")
        assert isinstance(result, dict)
        assert "title" in result
        assert "materials" in result or "activities" in result

    def test_generate_tracking_sheet(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_tracking_sheet(student_id="maya_2026", goal_id="G1")
        assert isinstance(result, dict)

    def test_generate_social_story(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_social_story(
            student_id="maya_2026",
            scenario="greeting peers at school arrival",
        )
        assert isinstance(result, dict)

    def test_generate_visual_schedule(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_visual_schedule(
            student_id="maya_2026",
            routine="Morning arrival",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_first_then(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_first_then(student_id="maya_2026", goal_id="G1")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_parent_comm(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_parent_comm(student_id="maya_2026", goal_id="G1")
        assert isinstance(result, dict)

    def test_generate_admin_report(self, client, data_dir):
        forge = MaterialForge(client, data_dir=data_dir)
        result = forge.generate_admin_report(student_id="maya_2026")
        assert isinstance(result, dict)
