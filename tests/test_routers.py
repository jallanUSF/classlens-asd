"""
TestClient-based endpoint tests for untested FastAPI routers:
  - Students CRUD
  - Chat (non-streaming + SSE)
  - Alerts
  - Documents
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tmp_students_dir(tmp_path: Path) -> Path:
    """Create a temporary students directory and return its path."""
    d = tmp_path / "students"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_student(directory: Path, student_id: str, data: dict | None = None):
    """Write a minimal student JSON file into the given directory."""
    if data is None:
        data = {
            "student_id": student_id,
            "name": f"Test {student_id}",
            "grade": 3,
            "asd_level": 1,
            "communication_level": "verbal",
            "interests": ["trains"],
            "sensory_profile": {},
            "iep_goals": [],
        }
    path = directory / f"{student_id}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ===================================================================
# 1. Students router
# ===================================================================


class TestStudentsListAndGet:
    """GET /api/students and GET /api/students/{id}."""

    def test_list_students(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        _write_student(students_dir, "stu_a")
        _write_student(students_dir, "stu_b")
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.get("/api/students")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2
        ids = {s["student_id"] for s in data}
        assert ids == {"stu_a", "stu_b"}

    def test_list_students_empty(self, tmp_path):
        empty_dir = tmp_path / "empty_students"
        # Don't create the directory — simulates fresh install
        with patch("backend.routers.students.STUDENTS_DIR", empty_dir):
            resp = client.get("/api/students")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_student_found(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        _write_student(students_dir, "maya_test", {
            "student_id": "maya_test",
            "name": "Maya Test",
            "grade": 3,
            "asd_level": 2,
            "communication_level": "verbal",
            "interests": ["dinosaurs"],
            "sensory_profile": {},
            "iep_goals": [
                {
                    "goal_id": "G1",
                    "target": 80,
                    "description": "Initiate peer greetings with 80% accuracy",
                    "trial_history": [{"date": "2026-04-01", "pct": 60}],
                }
            ],
        })
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.get("/api/students/maya_test")
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == "maya_test"
        # Should have annotated goal target fields
        goal = data["iep_goals"][0]
        assert "target_pct" in goal
        assert "target_display" in goal

    def test_get_student_not_found(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.get("/api/students/nonexistent")
        assert resp.status_code == 404

    def test_get_student_path_traversal_rejected(self):
        """validate_student_id should block path-traversal-style IDs."""
        # ../etc gets normalized by the URL layer, so use an ID with dots
        # that validate_student_id still catches (e.g., contains '..')
        resp = client.get("/api/students/maya..2026")
        assert resp.status_code == 400


class TestStudentsCreate:
    """POST /api/students."""

    def test_create_student_success(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.post("/api/students", json={
                "student_id": "new_kid",
                "name": "New Kid",
                "grade": 2,
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data["student_id"] == "new_kid"
        assert data["name"] == "New Kid"
        # File should exist on disk
        assert (students_dir / "new_kid.json").exists()

    def test_create_student_conflict(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        _write_student(students_dir, "existing")
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.post("/api/students", json={
                "student_id": "existing",
                "name": "Existing",
                "grade": 1,
            })
        assert resp.status_code == 409

    def test_create_student_bad_id(self):
        resp = client.post("/api/students", json={
            "student_id": "../hack",
            "name": "Hack",
            "grade": 1,
        })
        assert resp.status_code == 400


class TestStudentsUpdateAndDelete:
    """PUT and DELETE /api/students/{id}."""

    def test_update_student(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        _write_student(students_dir, "upd_kid")
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.put("/api/students/upd_kid", json={
                "name": "Updated Name",
                "grade": 5,
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Name"
        assert data["grade"] == 5

    def test_update_student_not_found(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.put("/api/students/ghost", json={"name": "Ghost"})
        assert resp.status_code == 404

    def test_delete_student(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        _write_student(students_dir, "del_kid")
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.delete("/api/students/del_kid")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"
        assert not (students_dir / "del_kid.json").exists()

    def test_delete_student_not_found(self, tmp_path):
        students_dir = _tmp_students_dir(tmp_path)
        with patch("backend.routers.students.STUDENTS_DIR", students_dir):
            resp = client.delete("/api/students/ghost")
        assert resp.status_code == 404

    def test_delete_student_path_traversal(self):
        resp = client.delete("/api/students/maya..hack")
        assert resp.status_code == 400


# ===================================================================
# 2. Chat router
# ===================================================================


class TestChatEndpoint:
    """POST /api/chat — non-streaming."""

    def test_chat_returns_response(self):
        """Without API keys, the mock path should still return a response."""
        with patch("backend.routers.chat._has_live_api_key", return_value=False):
            resp = client.post("/api/chat", json={
                "message": "Hello, how can you help?",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "assistant"
        assert isinstance(data["content"], str)
        assert len(data["content"]) > 0

    def test_chat_with_student_context(self):
        """Chat referencing a student should include student context."""
        with patch("backend.routers.chat._has_live_api_key", return_value=False):
            resp = client.post("/api/chat", json={
                "message": "How is Maya doing?",
                "student_id": "maya_2026",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == "maya_2026"
        assert len(data["content"]) > 0

    def test_chat_with_history(self):
        with patch("backend.routers.chat._has_live_api_key", return_value=False):
            resp = client.post("/api/chat", json={
                "message": "Tell me more.",
                "conversation_history": [
                    {"role": "user", "content": "How is Maya?"},
                    {"role": "assistant", "content": "Maya is doing well."},
                ],
            })
        assert resp.status_code == 200
        assert resp.json()["role"] == "assistant"


class TestChatStreamEndpoint:
    """POST /api/chat/stream — SSE streaming."""

    def test_stream_returns_sse(self):
        with patch("backend.routers.chat._has_live_api_key", return_value=False):
            resp = client.post("/api/chat/stream", json={
                "message": "Hello",
            })
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

        # Parse SSE frames
        body = resp.text
        frames = [
            line.removeprefix("data: ")
            for line in body.strip().splitlines()
            if line.startswith("data: ")
        ]
        assert len(frames) >= 1
        # Last frame should be the done marker
        last = json.loads(frames[-1])
        assert last.get("done") is True

    def test_stream_contains_delta(self):
        with patch("backend.routers.chat._has_live_api_key", return_value=False):
            resp = client.post("/api/chat/stream", json={
                "message": "Hello",
            })
        body = resp.text
        frames = [
            line.removeprefix("data: ")
            for line in body.strip().splitlines()
            if line.startswith("data: ")
        ]
        # At least one delta frame before the done frame
        deltas = [json.loads(f) for f in frames if "delta" in f]
        assert len(deltas) >= 1
        assert isinstance(deltas[0]["delta"], str)


# ===================================================================
# 3. Alerts router
# ===================================================================


class TestAlertsEndpoint:
    """GET /api/alerts and PUT /api/alerts/{id}/dismiss."""

    def test_get_alerts_returns_list(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        alerts_dir = data_dir / "alerts"
        students_dir.mkdir(parents=True)
        alerts_dir.mkdir(parents=True)

        # Write a student with declining trial data to trigger an alert
        student_data = {
            "student_id": "alert_kid",
            "name": "Alert Kid",
            "grade": 3,
            "asd_level": 2,
            "iep_goals": [
                {
                    "goal_id": "G1",
                    "domain": "communication",
                    "target": 80,
                    "description": "Peer greetings",
                    "trial_history": [
                        {"date": "2026-03-01", "pct": 70},
                        {"date": "2026-03-08", "pct": 65},
                        {"date": "2026-03-15", "pct": 60},
                    ],
                }
            ],
        }
        (students_dir / "alert_kid.json").write_text(
            json.dumps(student_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        alerts_file = alerts_dir / "active_alerts.json"

        with (
            patch("backend.routers.alerts.DATA_DIR", data_dir),
            patch("backend.routers.alerts.ALERTS_FILE", alerts_file),
        ):
            resp = client.get("/api/alerts")
        assert resp.status_code == 200
        alerts = resp.json()
        assert isinstance(alerts, list)
        assert len(alerts) >= 1
        assert alerts[0]["student_id"] == "alert_kid"
        assert alerts[0]["alert_type"] == "regression"

    def test_get_alerts_empty(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        alerts_dir = data_dir / "alerts"
        students_dir.mkdir(parents=True)
        alerts_dir.mkdir(parents=True)
        alerts_file = alerts_dir / "active_alerts.json"

        with (
            patch("backend.routers.alerts.DATA_DIR", data_dir),
            patch("backend.routers.alerts.ALERTS_FILE", alerts_file),
        ):
            resp = client.get("/api/alerts")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_dismiss_alert(self, tmp_path):
        data_dir = tmp_path / "data"
        alerts_dir = data_dir / "alerts"
        alerts_dir.mkdir(parents=True)
        alerts_file = alerts_dir / "active_alerts.json"

        # Pre-populate an alert
        alert = {
            "id": "abc12345",
            "student_id": "maya_2026",
            "alert_type": "regression",
            "label": "declining",
            "severity": "high",
            "goal_id": "G1",
            "title": "Maya declining",
            "detail": "Scores dropping",
            "suggested_action": "Review",
            "created_date": "2026-04-12",
            "dismissed": False,
        }
        alerts_file.write_text(json.dumps([alert]), encoding="utf-8")

        with patch("backend.routers.alerts.ALERTS_FILE", alerts_file):
            resp = client.put("/api/alerts/abc12345/dismiss")
        assert resp.status_code == 200
        assert resp.json()["status"] == "dismissed"

        # Verify the file was updated
        saved = json.loads(alerts_file.read_text(encoding="utf-8"))
        assert saved[0]["dismissed"] is True

    def test_dismiss_alert_not_found(self, tmp_path):
        alerts_dir = tmp_path / "alerts"
        alerts_dir.mkdir(parents=True)
        alerts_file = alerts_dir / "active_alerts.json"
        alerts_file.write_text("[]", encoding="utf-8")

        with patch("backend.routers.alerts.ALERTS_FILE", alerts_file):
            resp = client.put("/api/alerts/nonexistent/dismiss")
        assert resp.status_code == 404

    def test_analyze_alert_validates_student_id(self, tmp_path):
        """The analyze endpoint should reject alerts with invalid student_id."""
        data_dir = tmp_path / "data"
        alerts_dir = data_dir / "alerts"
        students_dir = data_dir / "students"
        alerts_dir.mkdir(parents=True)
        students_dir.mkdir(parents=True)
        alerts_file = alerts_dir / "active_alerts.json"

        # Pinned alert with a bad student_id to test validate_student_id
        alert = {
            "id": "bad_id_alert",
            "student_id": "../etc",
            "alert_type": "regression",
            "label": "declining",
            "severity": "high",
            "goal_id": "G1",
            "title": "Bad",
            "detail": "Bad",
            "suggested_action": "Bad",
            "created_date": "2026-04-12",
            "dismissed": False,
            "pinned": True,
        }
        alerts_file.write_text(json.dumps([alert]), encoding="utf-8")

        with (
            patch("backend.routers.alerts.DATA_DIR", data_dir),
            patch("backend.routers.alerts.ALERTS_FILE", alerts_file),
        ):
            resp = client.post("/api/alerts/bad_id_alert/analyze")
        assert resp.status_code == 400


# ===================================================================
# 4. Documents router
# ===================================================================


class TestDocumentsEndpoint:
    """GET /api/students/{id}/documents and POST /api/documents/upload."""

    def test_list_documents_empty(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)

        with patch("backend.routers.documents.DATA_DIR", data_dir):
            resp = client.get("/api/students/maya_2026/documents")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_documents_with_data(self, tmp_path):
        data_dir = tmp_path / "data"
        docs_dir = data_dir / "documents" / "maya_2026"
        docs_dir.mkdir(parents=True)

        doc_record = {
            "status": "uploaded",
            "file_path": "/some/path",
            "doc_type": "iep_pdf",
            "upload_date": "2026-04-12",
            "extraction": {"iep_goals": [], "accommodations": []},
            "message": "Extracted 0 goals.",
        }
        (docs_dir / "iep_pdf_2026-04-12.json").write_text(
            json.dumps(doc_record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        with patch("backend.routers.documents.DATA_DIR", data_dir):
            resp = client.get("/api/students/maya_2026/documents")
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) == 1
        assert docs[0]["status"] == "uploaded"
        assert "id" in docs[0]

    def test_list_documents_path_traversal(self):
        resp = client.get("/api/students/maya..hack/documents")
        assert resp.status_code == 400

    def test_upload_document(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)

        # Mock the IEP extractor so we don't need a real model
        mock_extraction = {
            "student_name": "Test Student",
            "grade": 3,
            "asd_level": 2,
            "communication_level": "verbal",
            "interests": [],
            "iep_goals": [{"goal_id": "G1", "description": "Test goal"}],
            "accommodations": ["Extended time"],
            "notes": "",
        }

        with (
            patch("backend.routers.documents.DATA_DIR", data_dir),
            patch("backend.routers.documents._run_extraction", return_value=mock_extraction),
        ):
            fake_pdf = io.BytesIO(b"%PDF-1.4 fake content here")
            resp = client.post(
                "/api/documents/upload",
                data={
                    "student_id": "test_stu",
                    "doc_type": "iep_pdf",
                },
                files={"file": ("iep_document.pdf", fake_pdf, "application/pdf")},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "uploaded"
        assert "1 IEP goal" in data["message"]
        assert "1 accommodation" in data["message"]

    def test_upload_document_bad_extension(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)

        with patch("backend.routers.documents.DATA_DIR", data_dir):
            fake_exe = io.BytesIO(b"MZ" + b"\x00" * 50)
            resp = client.post(
                "/api/documents/upload",
                data={
                    "student_id": "test_stu",
                    "doc_type": "iep_pdf",
                },
                files={"file": ("malware.exe", fake_exe, "application/octet-stream")},
            )
        assert resp.status_code == 400

    def test_upload_document_bad_student_id(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir(parents=True)

        with patch("backend.routers.documents.DATA_DIR", data_dir):
            fake_pdf = io.BytesIO(b"%PDF-1.4 content")
            resp = client.post(
                "/api/documents/upload",
                data={
                    "student_id": "../hack",
                    "doc_type": "iep_pdf",
                },
                files={"file": ("iep.pdf", fake_pdf, "application/pdf")},
            )
        assert resp.status_code == 400


# ===================================================================
# 6. Materials router
# ===================================================================


class TestMaterialsEndpoint:
    """Tests for /api/materials/* endpoints."""

    def test_list_materials_empty(self, tmp_path):
        mat_dir = tmp_path / "materials"
        mat_dir.mkdir(parents=True)

        with patch("backend.routers.materials.MATERIALS_DIR", mat_dir):
            resp = client.get("/api/students/maya_2026/materials")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_materials_with_data(self, tmp_path):
        mat_dir = tmp_path / "materials" / "maya_2026"
        mat_dir.mkdir(parents=True)
        record = {
            "student_id": "maya_2026",
            "goal_id": "G1",
            "material_type": "lesson_plan",
            "status": "draft",
            "content": {"title": "Test Lesson"},
        }
        (mat_dir / "lesson_plan_G1_2026-04-12.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        with patch("backend.routers.materials.MATERIALS_DIR", mat_dir.parent):
            resp = client.get("/api/students/maya_2026/materials")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["material_type"] == "lesson_plan"
        assert "id" in data[0]

    def test_list_materials_path_traversal(self):
        resp = client.get("/api/students/../hack/materials")
        assert resp.status_code in (400, 404)

    def test_approve_material(self, tmp_path):
        mat_dir = tmp_path / "materials" / "maya_2026"
        mat_dir.mkdir(parents=True)
        record = {"student_id": "maya_2026", "status": "draft", "content": {}}
        (mat_dir / "lesson_G1.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        with patch("backend.routers.materials.MATERIALS_DIR", mat_dir.parent):
            resp = client.put("/api/materials/maya_2026/lesson_G1/approve")
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    def test_approve_material_not_found(self, tmp_path):
        mat_dir = tmp_path / "materials" / "maya_2026"
        mat_dir.mkdir(parents=True)

        with patch("backend.routers.materials.MATERIALS_DIR", mat_dir.parent):
            resp = client.put("/api/materials/maya_2026/nonexistent/approve")
        assert resp.status_code == 404

    def test_flag_material(self, tmp_path):
        mat_dir = tmp_path / "materials" / "maya_2026"
        mat_dir.mkdir(parents=True)
        record = {"student_id": "maya_2026", "status": "draft", "content": {}}
        (mat_dir / "lesson_G1.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        flags_dir = tmp_path / "flags"
        flags_dir.mkdir(parents=True)

        with (
            patch("backend.routers.materials.MATERIALS_DIR", mat_dir.parent),
            patch("backend.routers.materials.DATA_DIR", tmp_path),
        ):
            resp = client.post(
                "/api/materials/maya_2026/lesson_G1/flag",
                json={"reason": "Inaccurate content"},
            )
        assert resp.status_code == 200
        assert resp.json()["status"] == "flagged"
        flags_path = flags_dir / "maya_2026.json"
        assert flags_path.exists()
        flags = json.loads(flags_path.read_text(encoding="utf-8"))
        assert len(flags) == 1
        assert flags[0]["reason"] == "Inaccurate content"

    def test_flag_material_not_found(self, tmp_path):
        mat_dir = tmp_path / "materials" / "maya_2026"
        mat_dir.mkdir(parents=True)

        with patch("backend.routers.materials.MATERIALS_DIR", mat_dir.parent):
            resp = client.post(
                "/api/materials/maya_2026/nonexistent/flag",
                json={"reason": "test"},
            )
        assert resp.status_code == 404

    def test_flag_material_path_traversal(self):
        resp = client.post(
            "/api/materials/../hack/lesson_G1/flag",
            json={"reason": "test"},
        )
        assert resp.status_code in (400, 404)

    def test_generate_unknown_type(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        students_dir.mkdir(parents=True)
        _write_student(students_dir, "maya_2026")

        with patch("backend.routers.materials.DATA_DIR", data_dir):
            resp = client.post(
                "/api/materials/generate",
                json={
                    "student_id": "maya_2026",
                    "material_type": "invalid_type",
                },
            )
        assert resp.status_code == 400

    def test_generate_student_not_found(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        students_dir.mkdir(parents=True)

        with patch("backend.routers.materials.DATA_DIR", data_dir):
            resp = client.post(
                "/api/materials/generate",
                json={
                    "student_id": "nonexistent",
                    "material_type": "lesson_plan",
                },
            )
        assert resp.status_code == 404


# ===================================================================
# 7. Capture router
# ===================================================================


class TestCaptureEndpoint:
    """Tests for /api/capture and /api/capture/voice/* endpoints."""

    def test_capture_student_not_found(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        students_dir.mkdir(parents=True)

        with patch("backend.routers.capture.DATA_DIR", data_dir):
            fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
            resp = client.post(
                "/api/capture",
                data={"student_id": "nonexistent", "work_type": "worksheet"},
                files={"image": ("test.png", fake_img, "image/png")},
            )
        assert resp.status_code == 404

    def test_capture_path_traversal(self):
        fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        resp = client.post(
            "/api/capture",
            data={"student_id": "../hack", "work_type": "worksheet"},
            files={"image": ("test.png", fake_img, "image/png")},
        )
        assert resp.status_code == 400

    def test_capture_bad_extension(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        students_dir.mkdir(parents=True)
        _write_student(students_dir, "maya_2026")

        with patch("backend.routers.capture.DATA_DIR", data_dir):
            fake_exe = io.BytesIO(b"MZ" + b"\x00" * 100)
            resp = client.post(
                "/api/capture",
                data={"student_id": "maya_2026", "work_type": "worksheet"},
                files={"image": ("malware.exe", fake_exe, "application/octet-stream")},
            )
        assert resp.status_code == 400

    def test_voice_supported_endpoint(self):
        resp = client.get("/api/capture/voice/supported")
        assert resp.status_code == 200
        data = resp.json()
        assert "supported" in data
        assert "provider" in data

    def test_voice_capture_student_not_found(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        students_dir.mkdir(parents=True)

        with patch("backend.routers.capture.DATA_DIR", data_dir):
            resp = client.post(
                "/api/capture/voice",
                json={
                    "student_id": "nonexistent",
                    "audio_b64": "",
                    "text_fallback": "Maya got 4 out of 5 on coin sorting",
                },
            )
        assert resp.status_code == 404

    def test_voice_capture_path_traversal(self):
        resp = client.post(
            "/api/capture/voice",
            json={
                "student_id": "../hack",
                "audio_b64": "",
                "text_fallback": "test",
            },
        )
        assert resp.status_code == 400

    def test_voice_capture_bad_audio_type(self, tmp_path):
        data_dir = tmp_path / "data"
        students_dir = data_dir / "students"
        students_dir.mkdir(parents=True)
        _write_student(students_dir, "maya_2026")

        import base64
        with (
            patch("backend.routers.capture.DATA_DIR", data_dir),
            patch("backend.routers.capture._is_google_provider", return_value=True),
        ):
            resp = client.post(
                "/api/capture/voice",
                json={
                    "student_id": "maya_2026",
                    "audio_b64": base64.b64encode(b"fake audio").decode(),
                    "media_type": "video/mp4",
                },
            )
        assert resp.status_code == 400
