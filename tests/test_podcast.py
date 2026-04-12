"""Tests for the Progress Briefing podcast feature.

Mocks `core.tts_client.synthesize_script` so no network call hits Edge TTS
during CI. The mock returns a deterministic ~1KB "silence" payload.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

# Minimal MP3 header + silence padding, enough for Content-Type/length assertions
FAKE_MP3 = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\x00" * 1024

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PRECOMPUTED_DIR = DATA_DIR / "precomputed"


@pytest.fixture
def mock_tts():
    """Patch Edge TTS to return deterministic fake MP3 bytes."""
    with patch("core.tts_client.synthesize_script", return_value=FAKE_MP3) as mock:
        yield mock


class TestPodcastEndpoints:
    def test_get_cached_podcast_ok(self):
        """Cached podcast JSON returns with audio_url attached."""
        resp = client.get("/api/students/maya_2026/podcast")
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_id"] == "maya_2026"
        assert "script" in data and isinstance(data["script"], list)
        assert data["audio_url"] == "/api/podcast/audio/maya_2026.mp3"

    def test_get_podcast_nonexistent_student(self):
        """Nonexistent student returns 404 on GET."""
        resp = client.get("/api/students/fake_student_xyz/podcast")
        assert resp.status_code == 404

    def test_get_audio_mp3_content_type(self):
        """Serves the cached MP3 with audio/mpeg Content-Type."""
        resp = client.get("/api/podcast/audio/maya_2026.mp3")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("audio/mpeg")
        assert len(resp.content) > 0

    def test_get_audio_missing_student_404(self):
        """Audio request for a student with no cache returns 404."""
        resp = client.get("/api/podcast/audio/fake_student_xyz.mp3")
        assert resp.status_code == 404

    def test_get_audio_rejects_non_mp3_filename(self):
        """Non-mp3 filenames should 404 or 400, never serve content."""
        resp = client.get("/api/podcast/audio/maya_2026.wav")
        assert resp.status_code == 404

    def test_path_traversal_rejected_on_audio(self):
        """validate_student_id blocks path traversal via filename field."""
        # FastAPI routes don't allow "/" in path-param, but the validator
        # must still reject ".." and other disallowed chars.
        resp = client.get("/api/podcast/audio/..maya.mp3")
        assert resp.status_code in (400, 404)

    def test_path_traversal_rejected_on_get(self):
        resp = client.get("/api/students/..maya/podcast")
        assert resp.status_code in (400, 404)

    def test_path_traversal_rejected_on_stream(self):
        resp = client.post("/api/students/..maya/podcast/stream")
        assert resp.status_code in (400, 404)


class TestPodcastGeneration:
    """Covers the live generation path (SSE stream) with TTS mocked."""

    def test_stream_regenerates_and_overwrites_cache(self, mock_tts):
        """Posting to /stream should overwrite the cached MP3."""
        original_audio = (PRECOMPUTED_DIR / "podcast_maya_2026.mp3").read_bytes()

        with client.stream(
            "POST", "/api/students/maya_2026/podcast/stream"
        ) as resp:
            assert resp.status_code == 200
            frames = [chunk for chunk in resp.iter_text() if chunk.strip()]

        # Final frame should carry the result or done marker
        joined = "".join(frames)
        assert "result" in joined or "done" in joined

        # Cache overwritten with our fake MP3
        new_audio = (PRECOMPUTED_DIR / "podcast_maya_2026.mp3").read_bytes()
        assert new_audio == FAKE_MP3
        # Restore the real precomputed MP3 so other tests aren't affected
        (PRECOMPUTED_DIR / "podcast_maya_2026.mp3").write_bytes(original_audio)

    def test_stream_nonexistent_student_404(self):
        resp = client.post("/api/students/fake_student_xyz/podcast/stream")
        assert resp.status_code == 404
