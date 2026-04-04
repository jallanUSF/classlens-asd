"""
Agent 3: Progress Analyst
Trial history -> trend analysis, progress notes, regression alerts.
Uses Gemma 4 thinking mode for explainable reasoning.
"""

import json

from agents.base import BaseAgent
from prompts.templates import PROGRESS_ANALYST_SYSTEM, PROGRESS_ANALYST_USER


class ProgressAnalyst(BaseAgent):
    """Analyzes IEP goal progress with thinking mode for explainable reasoning."""

    def __init__(self, client, data_dir: str = "data"):
        super().__init__(client)
        self.data_dir = data_dir

    def analyze(self, student_id: str, goal_id: str) -> dict:
        """
        Analyze progress toward a specific IEP goal.

        Returns:
            dict with trend, alert, progress_note, recommendation,
            plus 'thinking' key showing the model's reasoning chain
        """
        profile = self._load_student_raw(student_id, self.data_dir)
        goal = self._get_goal(profile, goal_id)
        history = goal.get("trial_history", [])

        # Format trial history as a readable table
        trial_table = self._format_trial_history(history)

        # Get last trial date
        last_trial_date = history[-1]["date"] if history else "No trials"

        prompt = PROGRESS_ANALYST_USER.format(
            student_name=profile["name"],
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            communication_level=profile.get("communication_level", "verbal"),
            goal_id=goal_id,
            domain=goal["domain"],
            goal_description=goal["description"],
            baseline=goal.get("baseline", {}).get("value", "N/A"),
            target=goal["target"],
            measurement_method=goal.get("measurement_method", "N/A"),
            trial_history_table=trial_table,
            last_trial_date=last_trial_date,
            current_intervention="See IEP goal notes",
            recent_changes="None noted",
            trial_count=len(history),
        )

        # Use thinking mode — the reasoning chain is part of the output
        result = self.client.generate_with_thinking(
            prompt=prompt,
            system=PROGRESS_ANALYST_SYSTEM,
        )

        # Parse the structured analysis from the output
        analysis = self._parse_analysis(result["output"])
        analysis["thinking"] = result["thinking"]
        analysis["goal_id"] = goal_id
        analysis["student_id"] = student_id

        return analysis

    def analyze_all_goals(self, student_id: str) -> list:
        """Run analysis on every active goal for a student."""
        profile = self._load_student_raw(student_id, self.data_dir)
        results = []
        for goal in profile["iep_goals"]:
            analysis = self.analyze(student_id, goal["goal_id"])
            results.append(analysis)
        return results

    def _get_goal(self, profile: dict, goal_id: str) -> dict:
        """Find a specific goal in the profile."""
        for goal in profile["iep_goals"]:
            if goal["goal_id"] == goal_id:
                return goal
        raise ValueError(
            f"Goal {goal_id} not found for student {profile.get('name', 'unknown')}"
        )

    def _format_trial_history(self, history: list) -> str:
        """Format trial history as a readable table for the prompt."""
        if not history:
            return "No trial data available."

        lines = ["Date       | Trials | Successes | Pct  | Notes"]
        lines.append("-" * 70)
        for entry in history:
            lines.append(
                f"{entry['date']:10s} | {entry.get('trials', 0):6d} | "
                f"{entry.get('successes', 0):9d} | {entry.get('pct', 0):4.0f}% | "
                f"{entry.get('notes', '')}"
            )
        return "\n".join(lines)

    def _parse_analysis(self, text: str) -> dict:
        """
        Parse the progress analysis from thinking mode output.
        Tries structured JSON first, then extracts key fields from text.
        """
        # Try JSON extraction first
        try:
            return self._parse_fallback(text)
        except ValueError:
            pass

        # Fall back to extracting key fields from text
        analysis = {
            "trend": "stable",
            "current_average": 0.0,
            "sessions_analyzed": 0,
            "confidence": "low",
            "alert": False,
            "alert_message": "",
            "progress_note": text[:500] if text else "No analysis available.",
            "recommendation": "",
        }

        text_lower = text.lower()
        if "improving" in text_lower:
            analysis["trend"] = "improving"
        elif "declining" in text_lower or "regress" in text_lower:
            analysis["trend"] = "regressing"
            analysis["alert"] = True
            analysis["alert_message"] = "Possible regression detected"
        elif "plateau" in text_lower or "stall" in text_lower:
            analysis["trend"] = "plateaued"
            analysis["alert"] = True
            analysis["alert_message"] = "Progress may have plateaued"

        return analysis
