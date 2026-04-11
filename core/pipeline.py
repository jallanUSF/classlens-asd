"""
Full pipeline: image -> transcription -> goal mapping -> analysis.
Single function call that runs the first three agents in sequence.
Material Forge (Agent 4) is invoked separately from the UI layer.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional

from core.gemma_client import GemmaClient
from agents.vision_reader import VisionReader
from agents.iep_mapper import IEPMapper
from agents.progress_analyst import ProgressAnalyst


class ClassLensPipeline:
    """End-to-end orchestration of the ClassLens agent chain."""

    def __init__(self, client: Optional[GemmaClient] = None, data_dir: str = "data"):
        """
        Args:
            client: GemmaClient or MockGemmaClient. If None, creates a real GemmaClient.
            data_dir: Path to data directory containing students/ and precomputed/.
        """
        self.client = client or GemmaClient()
        self.data_dir = data_dir
        self.vision = VisionReader(self.client)
        self.mapper = IEPMapper(self.client, data_dir=data_dir)
        self.analyst = ProgressAnalyst(self.client, data_dir=data_dir)

        # Precomputed results directory
        self.precomputed_dir = Path(data_dir) / "precomputed"

    def process_work_artifact(
        self,
        student_id: str,
        image_path: str,
        work_type: str,
        subject: str,
        date: str,
    ) -> dict:
        """
        Full pipeline: photo -> transcription -> goal mapping -> analysis.

        Critical Rule #1: check precomputed results first.
        Demo NEVER waits for API if we have cached results.

        Args:
            student_id: Student identifier (e.g., "maya_2026")
            image_path: Path to the work artifact photo
            work_type: worksheet|tally_sheet|checklist|visual_schedule|free_response
            subject: Subject area (math, reading, etc.)
            date: Date of the work (YYYY-MM-DD)

        Returns:
            dict with transcription, goal_mapping, analyses, and alerts
        """
        # Check for precomputed results first (demo mode)
        precomputed = self._load_precomputed(image_path)
        if precomputed:
            return precomputed

        # Load student profile for context
        profile = self._load_profile(student_id)

        # Step 1: Vision Reader
        transcription = self.vision.transcribe(
            image_path=image_path,
            student_name=profile["name"],
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            work_type=work_type,
            task_description=f"{subject} {work_type}",
        )

        # Step 2: IEP Mapper
        mapping = self.mapper.map_to_goals(
            student_id=student_id,
            transcription=transcription,
            work_type=work_type,
        )

        # Step 3: Progress Analyst (for each matched goal)
        analyses = []
        alerts = []
        for goal_match in mapping.get("matched_goals", []):
            analysis = self.analyst.analyze(
                student_id=student_id,
                goal_id=goal_match["goal_id"],
            )
            analyses.append(analysis)
            if analysis.get("alert"):
                alerts.append(analysis)

        result = {
            "student_id": student_id,
            "image_path": image_path,
            "date": date,
            "transcription": transcription,
            "goal_mapping": mapping,
            "analyses": analyses,
            "alerts": alerts,
        }

        # Cache for future demo use
        self._save_precomputed(image_path, result)

        return result

    def _load_profile(self, student_id: str) -> dict:
        """Load student profile as raw dict."""
        student_path = Path(self.data_dir) / "students" / f"{student_id}.json"
        with open(student_path, "r") as f:
            return json.load(f)

    def _load_precomputed(self, image_path: str) -> Optional[dict]:
        """Check if we have precomputed results for this image.

        Tries the full stem first, then strips date/type prefixes to match
        original filenames (e.g., '2026-04-06_worksheet_maya_math' -> 'maya_math').
        """
        cache_key = self._cache_key(image_path)
        cache_path = self.precomputed_dir / f"{cache_key}.json"
        if cache_path.exists():
            with open(cache_path, "r") as f:
                return json.load(f)
        # Fallback: strip date_worktype_ prefix from uploaded filenames
        stem = Path(image_path).stem
        parts = stem.split("_", 2)  # e.g., ["2026-04-06", "worksheet", "maya_math_worksheet"]
        if len(parts) == 3:
            fallback_path = self.precomputed_dir / f"{parts[2]}.json"
            if fallback_path.exists():
                with open(fallback_path, "r") as f:
                    return json.load(f)
        return None

    def _save_precomputed(self, image_path: str, result: dict):
        """Save pipeline result for demo mode caching."""
        self.precomputed_dir.mkdir(parents=True, exist_ok=True)
        cache_key = self._cache_key(image_path)
        cache_path = self.precomputed_dir / f"{cache_key}.json"
        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)

    def _cache_key(self, image_path: str) -> str:
        """Generate a stable cache key from the image filename."""
        return Path(image_path).stem
