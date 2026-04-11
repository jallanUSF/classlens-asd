"""
Security regression tests for backend upload validation and chat sanitization.

These tests cover the code paths that the mocked pipeline/agent tests
do NOT exercise: filename sanitization, upload size/extension limits,
student_id path-traversal blocking, and HTML tag stripping in chat responses.
"""

from __future__ import annotations

import io

import pytest
from fastapi import HTTPException, UploadFile

from backend.upload_utils import (
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    MAX_UPLOAD_BYTES,
    safe_filename,
    validate_student_id,
    validate_upload,
)
from backend.routers.chat import _sanitize_model_text
from backend.routers.students import _annotate_goal_target


def _make_upload(name: str, body: bytes) -> UploadFile:
    return UploadFile(filename=name, file=io.BytesIO(body))


class TestSafeFilename:
    def test_strips_posix_path_traversal(self):
        assert safe_filename("../../etc/passwd") == "passwd"

    def test_strips_windows_path_traversal(self):
        assert safe_filename("..\\..\\Windows\\System32\\cmd.exe") == "cmd.exe"

    def test_strips_absolute_path(self):
        assert safe_filename("/home/user/.ssh/id_rsa") == "id_rsa"

    def test_replaces_unsafe_chars(self):
        assert safe_filename("my photo (final)!.png") == "my_photo_final_.png"

    def test_preserves_safe_chars(self):
        assert safe_filename("maya_math_worksheet.png") == "maya_math_worksheet.png"

    def test_empty_name_fallback(self):
        assert safe_filename("") == "upload"

    def test_only_dots_fallback(self):
        assert safe_filename("...") == "upload"


class TestValidateStudentId:
    def test_accepts_valid(self):
        assert validate_student_id("maya_2026") == "maya_2026"

    def test_accepts_hyphens(self):
        assert validate_student_id("student-01") == "student-01"

    @pytest.mark.parametrize(
        "bad_id",
        ["", "../maya_2026", "maya/2026", "maya 2026", "maya;rm", ".env", "maya.."],
    )
    def test_rejects_traversal_and_unsafe(self, bad_id):
        with pytest.raises(HTTPException) as exc:
            validate_student_id(bad_id)
        assert exc.value.status_code == 400


class TestValidateUpload:
    def test_accepts_valid_png(self):
        upload = _make_upload("maya_work.png", b"\x89PNG\r\n" + b"0" * 100)
        name, data = validate_upload(upload, IMAGE_EXTENSIONS)
        assert name == "maya_work.png"
        assert len(data) == 106

    def test_sanitizes_filename_during_validation(self):
        upload = _make_upload("../../secret.png", b"\x89PNG\r\n")
        name, _ = validate_upload(upload, IMAGE_EXTENSIONS)
        assert name == "secret.png"

    def test_rejects_wrong_extension(self):
        upload = _make_upload("payload.exe", b"MZ" + b"\x00" * 50)
        with pytest.raises(HTTPException) as exc:
            validate_upload(upload, IMAGE_EXTENSIONS)
        assert exc.value.status_code == 400

    def test_rejects_pdf_in_image_only_endpoint(self):
        upload = _make_upload("iep.pdf", b"%PDF-1.4\n" + b"0" * 20)
        with pytest.raises(HTTPException) as exc:
            validate_upload(upload, IMAGE_EXTENSIONS)
        assert exc.value.status_code == 400

    def test_accepts_pdf_in_document_endpoint(self):
        upload = _make_upload("iep.pdf", b"%PDF-1.4\n" + b"0" * 20)
        name, _ = validate_upload(upload, DOCUMENT_EXTENSIONS)
        assert name == "iep.pdf"

    def test_rejects_empty_file(self):
        upload = _make_upload("empty.png", b"")
        with pytest.raises(HTTPException) as exc:
            validate_upload(upload, IMAGE_EXTENSIONS)
        assert exc.value.status_code == 422

    def test_rejects_oversized_file(self):
        upload = _make_upload("big.png", b"\x00" * (MAX_UPLOAD_BYTES + 10))
        with pytest.raises(HTTPException) as exc:
            validate_upload(upload, IMAGE_EXTENSIONS)
        assert exc.value.status_code == 413

    def test_rejects_missing_filename(self):
        upload = UploadFile(filename=None, file=io.BytesIO(b"\x89PNG\r\n"))
        with pytest.raises(HTTPException) as exc:
            validate_upload(upload, IMAGE_EXTENSIONS)
        assert exc.value.status_code == 422


class TestAnnotateGoalTarget:
    def test_percentage_goal(self):
        goal = {
            "goal_id": "G1",
            "target": 80,
            "description": "Maya will initiate peer greetings with 80% accuracy",
            "trial_history": [{"date": "2026-04-03", "pct": 60}],
        }
        _annotate_goal_target(goal)
        assert goal["target_pct"] == 80
        assert goal["target_unit"] == "percent"
        assert goal["target_display"] == "80%"
        assert goal["target_value"] == 80
        assert goal["current_pct"] == 60

    def test_count_based_outburst_goal(self):
        goal = {
            "goal_id": "G3",
            "target": 1,
            "description": "Maya will reduce outbursts to 1 or fewer per day",
            "trial_history": [{"date": "2026-04-03", "pct": 100}],
        }
        _annotate_goal_target(goal)
        assert goal["target_pct"] == 100, "progress bar should fill to 100 when count goal met"
        assert goal["target_unit"] == "count_per_day"
        assert goal["target_display"] == "≤1/day"
        assert goal["target_value"] == 1
        assert goal["current_pct"] == 100

    def test_small_target_without_count_hints_stays_percent(self):
        # Edge case: a low percentage target without "fewer/reduce/outburst" language
        # should stay as a percent, not be misclassified.
        goal = {
            "goal_id": "G1",
            "target": 5,
            "description": "Student will show 5% improvement in fine motor accuracy",
            "trial_history": [],
        }
        _annotate_goal_target(goal)
        assert goal["target_unit"] == "percent"
        assert goal["target_display"] == "5%"

    def test_uses_baseline_when_no_history(self):
        goal = {
            "goal_id": "G1",
            "target": 80,
            "description": "Initiate peer greetings",
            "baseline": {"value": 20, "date": "2025-10-15"},
            "trial_history": [],
        }
        _annotate_goal_target(goal)
        assert goal["current_pct"] == 20


class TestSanitizeModelText:
    def test_strips_table_fragments(self):
        assert _sanitize_model_text("Maya scored <td>80%</td> today.") == "Maya scored 80% today."

    def test_strips_script_block_with_body(self):
        dirty = "Hello<script>alert('xss')</script> world"
        assert _sanitize_model_text(dirty) == "Hello world"

    def test_strips_style_block_with_body(self):
        dirty = "Before<style>body{color:red}</style>after"
        assert _sanitize_model_text(dirty) == "Beforeafter"

    def test_strips_tags_with_attributes(self):
        dirty = '<div class="highlight" id="x">important</div>'
        assert _sanitize_model_text(dirty) == "important"

    def test_strips_self_closing_tags(self):
        assert _sanitize_model_text("line1<br/>line2") == "line1line2"

    def test_strips_headings_and_lists(self):
        dirty = "<h2>Progress</h2><ul><li>G1</li><li>G2</li></ul>"
        assert _sanitize_model_text(dirty) == "ProgressG1G2"

    def test_preserves_plain_text(self):
        plain = "Maya reached the 80% target on Goal G1."
        assert _sanitize_model_text(plain) == plain

    def test_handles_empty_input(self):
        assert _sanitize_model_text("") == ""
