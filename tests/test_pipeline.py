"""
Tests for the ClassLens pipeline (end-to-end with MockGemmaClient).
"""

import json
import shutil
from pathlib import Path

import pytest

from tests.mock_api_responses import MockGemmaClient
from core.pipeline import ClassLensPipeline


DATA_DIR = Path(__file__).parent.parent / "data"
SAMPLE_WORK = DATA_DIR / "sample_work"


@pytest.fixture
def data_dir(tmp_path):
    """Copy student data to temp dir; create empty precomputed dir."""
    src = DATA_DIR / "students"
    dst = tmp_path / "students"
    shutil.copytree(src, dst)
    (tmp_path / "precomputed").mkdir()
    return str(tmp_path)


@pytest.fixture
def pipeline(data_dir):
    client = MockGemmaClient()
    return ClassLensPipeline(client=client, data_dir=data_dir)


class TestPipelineEndToEnd:
    def test_process_maya_math(self, pipeline):
        result = pipeline.process_work_artifact(
            student_id="maya_2026",
            image_path=str(SAMPLE_WORK / "maya_math_worksheet.png"),
            work_type="worksheet",
            subject="math",
            date="2026-04-03",
        )
        assert result["student_id"] == "maya_2026"
        assert "transcription" in result
        assert "goal_mapping" in result
        assert "analyses" in result
        assert isinstance(result["analyses"], list)

    def test_process_maya_tally(self, pipeline):
        result = pipeline.process_work_artifact(
            student_id="maya_2026",
            image_path=str(SAMPLE_WORK / "maya_behavior_tally.png"),
            work_type="tally_sheet",
            subject="communication",
            date="2026-04-03",
        )
        assert result["student_id"] == "maya_2026"
        assert "transcription" in result

    def test_process_jaylen(self, pipeline):
        result = pipeline.process_work_artifact(
            student_id="jaylen_2026",
            image_path=str(SAMPLE_WORK / "jaylen_task_checklist.png"),
            work_type="checklist",
            subject="daily_living",
            date="2026-04-03",
        )
        assert result["student_id"] == "jaylen_2026"

    def test_process_sofia(self, pipeline):
        result = pipeline.process_work_artifact(
            student_id="sofia_2026",
            image_path=str(SAMPLE_WORK / "sofia_writing_sample.png"),
            work_type="free_response",
            subject="writing",
            date="2026-04-03",
        )
        assert result["student_id"] == "sofia_2026"


class TestPrecomputedCaching:
    def test_results_cached_after_processing(self, pipeline, data_dir):
        image_path = str(SAMPLE_WORK / "maya_math_worksheet.png")
        result1 = pipeline.process_work_artifact(
            student_id="maya_2026",
            image_path=image_path,
            work_type="worksheet",
            subject="math",
            date="2026-04-03",
        )

        # Cache file should exist
        cache_path = Path(data_dir) / "precomputed" / "maya_math_worksheet.json"
        assert cache_path.exists()

        # Second call should return cached result
        result2 = pipeline.process_work_artifact(
            student_id="maya_2026",
            image_path=image_path,
            work_type="worksheet",
            subject="math",
            date="2026-04-03",
        )
        assert result1 == result2

    def test_precomputed_loads_from_disk(self, data_dir):
        """Pre-populated cache should be returned without calling agents."""
        precomputed = {
            "student_id": "maya_2026",
            "transcription": {"cached": True},
            "goal_mapping": {},
            "analyses": [],
            "alerts": [],
        }
        cache_path = Path(data_dir) / "precomputed" / "maya_math_worksheet.json"
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(precomputed, f)

        pipeline = ClassLensPipeline(client=MockGemmaClient(), data_dir=data_dir)
        result = pipeline.process_work_artifact(
            student_id="maya_2026",
            image_path=str(SAMPLE_WORK / "maya_math_worksheet.png"),
            work_type="worksheet",
            subject="math",
            date="2026-04-03",
        )
        assert result["transcription"] == {"cached": True}
