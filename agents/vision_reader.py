"""
Agent 1: Vision Reader
Photo of student work -> structured JSON transcription.
Uses Gemma 4 multimodal (image + text -> function call).
"""

from agents.base import BaseAgent
from schemas.tools import TRANSCRIBE_STUDENT_WORK
from prompts.templates import VISION_READER_SYSTEM, VISION_READER_USER


class VisionReader(BaseAgent):
    """Reads photos of student work and produces structured transcriptions."""

    def transcribe(
        self,
        image_path: str,
        student_name: str,
        grade: int,
        asd_level: int,
        work_type: str,
        task_description: str = "",
        teacher_notes: str = "",
    ) -> dict:
        """
        Read a photo of student work and produce structured transcription.

        Args:
            image_path: Path to the photograph
            student_name: Student's first name
            grade: Grade level (for context)
            asd_level: ASD support level (1-3)
            work_type: worksheet|tally_sheet|checklist|visual_schedule|free_response
            task_description: What the assignment is about
            teacher_notes: Any teacher notes about the work

        Returns:
            dict with transcribed data matching TRANSCRIBE_STUDENT_WORK schema
        """
        prompt = VISION_READER_USER.format(
            student_name=student_name,
            grade=grade,
            asd_level=asd_level,
            work_type=work_type,
            task_description=task_description or "Not specified",
            teacher_notes=teacher_notes or "None provided",
        )

        result = self.client.generate_with_tools(
            prompt=prompt,
            tools=[TRANSCRIBE_STUDENT_WORK],
            system=VISION_READER_SYSTEM,
            image_path=image_path,
        )

        # If function calling worked, return args directly
        if "function" in result:
            return result["args"]

        # Fallback: parse JSON from text response
        return self._parse_fallback(result.get("text", ""))
