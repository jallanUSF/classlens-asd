"""
Agent: Voice Reader
Teacher voice observation -> structured trial data via Gemma audio input.
Output schema matches Vision Reader so the IEP Mapper receives identical input.
"""

import json
import logging
from typing import Optional

from agents.base import BaseAgent
from prompts.templates import VOICE_READER_SYSTEM, VOICE_READER_USER

logger = logging.getLogger(__name__)


class VoiceReader(BaseAgent):
    """Extracts structured trial data from teacher voice observations."""

    def __init__(self, client, data_dir: str = "data"):
        super().__init__(client)
        self.data_dir = data_dir

    def transcribe_and_extract(
        self,
        audio_bytes: bytes,
        mime_type: str,
        student_id: str,
    ) -> dict:
        """
        Send audio to Gemma via Google AI Studio audio input.
        Returns the same schema as vision_reader output so the IEP Mapper
        receives identical input regardless of capture method.

        Args:
            audio_bytes: Raw audio bytes
            mime_type: MIME type (e.g., "audio/webm", "audio/wav")
            student_id: Student ID for context loading

        Returns:
            dict with transcription, work_type, student_work, confidence
        """
        profile = self._load_student_raw(student_id, self.data_dir)

        # Build goals summary for context
        goals_summary = "; ".join(
            f"{g['goal_id']} ({g['domain']}): {g['description'][:80]}"
            for g in profile.get("iep_goals", [])
        )

        prompt = VOICE_READER_USER.format(
            student_name=profile["name"],
            student_id=student_id,
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            communication_level=profile.get("communication_level", "verbal"),
            goals_summary=goals_summary,
        )

        # Use audio multimodal input
        raw_output = self.client.generate_with_audio(
            audio_bytes=audio_bytes,
            mime_type=mime_type,
            prompt=prompt,
            system=VOICE_READER_SYSTEM,
        )

        # Parse the structured output
        result = self._parse_result(raw_output)
        result["student_id"] = student_id
        result["work_type"] = "voice_observation"
        return result

    def transcribe_from_text(self, text: str, student_id: str) -> dict:
        """
        Fallback for non-Google providers: accept typed text instead of audio.
        Parses the teacher's typed observation the same way.
        """
        profile = self._load_student_raw(student_id, self.data_dir)

        goals_summary = "; ".join(
            f"{g['goal_id']} ({g['domain']}): {g['description'][:80]}"
            for g in profile.get("iep_goals", [])
        )

        prompt = VOICE_READER_USER.format(
            student_name=profile["name"],
            student_id=student_id,
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            communication_level=profile.get("communication_level", "verbal"),
            goals_summary=goals_summary,
        )

        # Add the teacher's typed observation to the prompt
        full_prompt = f"{prompt}\n\nTeacher's observation (typed):\n{text}"

        raw_output = self.client.generate(
            prompt=full_prompt,
            system=VOICE_READER_SYSTEM,
        )

        result = self._parse_result(raw_output)
        result["student_id"] = student_id
        result["work_type"] = "voice_observation"
        result["transcription"] = text  # Use original text as transcription
        return result

    def _parse_result(self, text: str) -> dict:
        """Parse the voice reader output, with fallback."""
        parsed = self._parse_fallback(text)

        # Ensure required fields exist
        parsed.setdefault("transcription", text[:500] if text else "")
        parsed.setdefault("work_type", "voice_observation")
        parsed.setdefault("subject", "")
        parsed.setdefault("student_work", {})
        parsed.setdefault("confidence", 0.7)

        return parsed
