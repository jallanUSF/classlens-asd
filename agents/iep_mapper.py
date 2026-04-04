"""
Agent 2: IEP Mapper
Transcribed work -> matched to student's IEP goals -> trial data recorded.
Uses Gemma 4 function calling.
"""

import json

from agents.base import BaseAgent
from schemas.tools import MAP_WORK_TO_GOALS
from prompts.templates import IEP_MAPPER_SYSTEM, IEP_MAPPER_USER


class IEPMapper(BaseAgent):
    """Maps transcribed student work to IEP goals and records trial data."""

    def __init__(self, client, data_dir: str = "data"):
        super().__init__(client)
        self.data_dir = data_dir

    def map_to_goals(
        self,
        student_id: str,
        transcription: dict,
        work_type: str = "worksheet",
    ) -> dict:
        """
        Map transcribed work to the student's IEP goals.

        Args:
            student_id: Student identifier
            transcription: Output from VisionReader.transcribe()
            work_type: Type of work artifact

        Returns:
            dict with matched_goals and trial data
        """
        profile = self._load_student_raw(student_id, self.data_dir)

        # Format IEP goals as context string
        goals_context = self._format_goals(profile["iep_goals"])

        # Build the sensory profile strings
        sensory = profile.get("sensory_profile", {})
        sensory_seeks = ", ".join(sensory.get("seeks", []))
        sensory_avoids = ", ".join(sensory.get("avoids", []))

        prompt = IEP_MAPPER_USER.format(
            student_id=student_id,
            student_name=profile["name"],
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            communication_level=profile.get("communication_level", "verbal"),
            interests=", ".join(profile.get("interests", [])),
            sensory_seeks=sensory_seeks or "Not specified",
            sensory_avoids=sensory_avoids or "Not specified",
            reinforcers=", ".join(profile.get("reinforcers", [])),
            iep_goals_list=goals_context,
            transcription_json=json.dumps(transcription, indent=2),
            work_type=work_type,
        )

        result = self.client.generate_with_tools(
            prompt=prompt,
            tools=[MAP_WORK_TO_GOALS],
            system=IEP_MAPPER_SYSTEM,
        )

        if "function" in result:
            mapping = result["args"]
        else:
            mapping = self._parse_fallback(result.get("text", ""))

        # Record trial data to student's goal history
        self._record_trials(student_id, profile, mapping)

        return mapping

    def _format_goals(self, goals: list) -> str:
        """Format IEP goals as context string for the prompt."""
        lines = []
        for g in goals:
            baseline = g.get("baseline", {})
            baseline_val = baseline.get("value", "N/A") if isinstance(baseline, dict) else baseline
            lines.append(
                f"[{g['goal_id']}] {g['domain']}: {g['description']} "
                f"(baseline: {baseline_val}%, target: {g['target']}%, "
                f"measurement: {g.get('measurement_method', 'N/A')})"
            )
        return "\n".join(lines)

    def _record_trials(self, student_id: str, profile: dict, mapping: dict):
        """
        Write trial data from the mapping back into the student's JSON.
        Appends to each goal's trial_history.
        """
        from datetime import date

        matched = mapping.get("matched_goals", [])
        if not matched:
            return

        today = date.today().isoformat()

        for goal_match in matched:
            goal_id = goal_match.get("goal_id")
            if not goal_id:
                continue

            # Find the goal in the profile
            for goal in profile["iep_goals"]:
                if goal["goal_id"] == goal_id:
                    trial_entry = {
                        "date": today,
                        "trials": goal_match.get("trials", 0),
                        "successes": goal_match.get("successes", 0),
                        "pct": goal_match.get("percentage", 0),
                        "notes": goal_match.get("reasoning", ""),
                    }
                    if "trial_history" not in goal:
                        goal["trial_history"] = []
                    goal["trial_history"].append(trial_entry)
                    break

        self._save_student_raw(student_id, profile, self.data_dir)
