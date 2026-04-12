"""Tests for voice capture endpoint and VoiceReader agent."""

import base64

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestVoiceSupportedEndpoint:
    """Test the voice support check endpoint."""

    def test_voice_supported_returns_status(self):
        resp = client.get("/api/capture/voice/supported")
        assert resp.status_code == 200
        data = resp.json()
        assert "supported" in data
        assert "provider" in data


class TestVoiceCaptureEndpoint:
    """Test the voice capture endpoint."""

    def test_voice_capture_text_fallback(self):
        """Text fallback mode should work without audio."""
        resp = client.post(
            "/api/capture/voice",
            json={
                "student_id": "maya_2026",
                "audio_b64": "",
                "media_type": "audio/webm",
                "text_fallback": "Maya greeted 3 peers this morning during arrival.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("work_type") == "voice_observation"
        assert data.get("student_id") == "maya_2026"

    def test_voice_capture_with_audio_or_graceful_error(self):
        """Audio capture should process or return a graceful error (audio may not be supported on all models)."""
        fake_audio = base64.b64encode(b"fake audio data").decode()
        resp = client.post(
            "/api/capture/voice",
            json={
                "student_id": "marcus_2026",
                "audio_b64": fake_audio,
                "media_type": "audio/webm",
            },
        )
        # Three legitimate outcomes:
        #   200 + transcription     → audio path succeeded (mock or enabled provider)
        #   200 + audio_not_supported → provider gate kicked in; UI falls back to text
        #   502                     → live API failed gracefully
        assert resp.status_code in (200, 502)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("error") == "audio_not_supported":
                assert data.get("fallback") == "text_input"
            else:
                assert "transcription" in data
                assert "student_work" in data

    def test_voice_capture_invalid_student(self):
        """Unknown student should return 404."""
        resp = client.post(
            "/api/capture/voice",
            json={
                "student_id": "nonexistent",
                "audio_b64": "",
                "text_fallback": "test",
            },
        )
        assert resp.status_code == 404

    def test_voice_capture_stream(self):
        """Streaming endpoint should return SSE frames."""
        resp = client.post(
            "/api/capture/voice/stream",
            json={
                "student_id": "maya_2026",
                "audio_b64": "",
                "media_type": "audio/webm",
                "text_fallback": "Maya greeted peers today.",
            },
        )
        assert resp.status_code == 200
        assert "data:" in resp.text

    def test_voice_capture_rejects_oversized_audio(self):
        """Audio over 10MB should be rejected."""
        # 11MB of base64
        huge_audio = base64.b64encode(b"x" * (11 * 1024 * 1024)).decode()
        resp = client.post(
            "/api/capture/voice",
            json={
                "student_id": "maya_2026",
                "audio_b64": huge_audio,
                "media_type": "audio/webm",
            },
        )
        assert resp.status_code == 400
        assert "too large" in resp.json()["detail"]

    def test_voice_capture_rejects_bad_mime(self):
        """Invalid MIME type should be rejected."""
        fake_audio = base64.b64encode(b"test").decode()
        resp = client.post(
            "/api/capture/voice",
            json={
                "student_id": "maya_2026",
                "audio_b64": fake_audio,
                "media_type": "video/mp4",
            },
        )
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["detail"]


class TestVoiceReaderAgent:
    """Test the VoiceReader agent directly."""

    def test_text_fallback_extracts_data(self):
        from tests.mock_api_responses import MockGemmaClient
        from agents.voice_reader import VoiceReader

        reader = VoiceReader(MockGemmaClient(), data_dir="data")
        result = reader.transcribe_from_text(
            "Maya said hello to 3 friends during arrival today.",
            student_id="maya_2026",
        )
        assert result["work_type"] == "voice_observation"
        assert result["student_id"] == "maya_2026"
        assert "transcription" in result

    def test_audio_extracts_data(self):
        from tests.mock_api_responses import MockGemmaClient
        from agents.voice_reader import VoiceReader

        reader = VoiceReader(MockGemmaClient(), data_dir="data")
        result = reader.transcribe_and_extract(
            audio_bytes=b"fake audio",
            mime_type="audio/webm",
            student_id="marcus_2026",
        )
        assert result["work_type"] == "voice_observation"
        assert "student_work" in result
        assert result["student_work"]["correct_responses"] == 4
