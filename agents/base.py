"""
Base agent class for ClassLens ASD pipeline.
Shared GemmaClient instance and common fallback parsing.
"""

import json
import re
from typing import Optional


class BaseAgent:
    """Base class providing shared utilities for all agents."""

    def __init__(self, client):
        """
        Args:
            client: GemmaClient or MockGemmaClient instance.
        """
        self.client = client

    def _parse_fallback(self, text: str) -> dict:
        """
        If function calling fails, try to extract JSON from text response.
        Every agent must have this — Critical Rule #2.
        """
        # Try to find a JSON object in the text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Try to find a JSON array
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                return {"items": json.loads(json_match.group())}
            except json.JSONDecodeError:
                pass

        # If no JSON found, return the text as-is in a dict
        return {"text": text}

    def _load_student_raw(self, student_id: str, data_dir: str = "data") -> dict:
        """
        Load student profile as raw dict from JSON file.
        Works with the actual JSON shape (name, grade, asd_level, etc.)
        without going through the Pydantic model.
        """
        from pathlib import Path
        student_path = Path(data_dir) / "students" / f"{student_id}.json"
        if not student_path.exists():
            raise FileNotFoundError(f"Student profile not found: {student_path}")
        with open(student_path, "r") as f:
            return json.load(f)

    def _save_student_raw(self, student_id: str, data: dict, data_dir: str = "data"):
        """Save student profile dict back to JSON file."""
        from pathlib import Path
        student_path = Path(data_dir) / "students" / f"{student_id}.json"
        with open(student_path, "w") as f:
            json.dump(data, f, indent=2)
