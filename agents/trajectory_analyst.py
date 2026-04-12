"""
Agent 5: Trajectory Analyst
Full-semester long-context analysis — all goals, all trial history, one Gemma call.
Uses thinking mode + 256K context window for comprehensive IEP meeting prep.
"""

import json
from pathlib import Path

from agents.base import BaseAgent
from core.json_io import read_json
from prompts.templates import TRAJECTORY_ANALYST_SYSTEM, TRAJECTORY_ANALYST_USER


class TrajectoryAnalyst(BaseAgent):
    """Analyzes full-semester IEP trajectory using Gemma's long context window."""

    def __init__(self, client, data_dir: str = "data"):
        super().__init__(client)
        self.data_dir = data_dir

    def analyze_trajectory(self, student_id: str) -> dict:
        """
        Build a long-context prompt from all trial data and alert history
        for one student. Calls Gemma 31B with thinking mode.

        Returns:
            dict with summary, per-goal trajectories, cross-goal patterns,
            and recommended priority, plus 'thinking' key with reasoning chain.
        """
        profile = self._load_student_raw(student_id, self.data_dir)

        # Build the goals block — full trial history for every goal
        goals_block = self._format_goals_block(profile)

        # Build the alerts block from any existing alert data
        alerts_block = self._format_alerts_block(student_id)

        prompt = TRAJECTORY_ANALYST_USER.format(
            student_name=profile["name"],
            grade=profile["grade"],
            asd_level=profile["asd_level"],
            communication_level=profile.get("communication_level", "verbal"),
            interests=", ".join(profile.get("interests", [])),
            sensory_seeks=", ".join(
                profile.get("sensory_profile", {}).get("seeks", [])
            ),
            sensory_avoids=", ".join(
                profile.get("sensory_profile", {}).get("avoids", [])
            ),
            goals_block=goals_block,
            alerts_block=alerts_block,
        )

        # Use thinking mode — the reasoning chain is part of the output
        result = self.client.generate_with_thinking(
            prompt=prompt,
            system=TRAJECTORY_ANALYST_SYSTEM,
        )

        # Parse the structured trajectory from the output
        trajectory = self._parse_trajectory(result["output"])
        trajectory["thinking"] = result["thinking"]
        trajectory["student_id"] = student_id

        return trajectory

    def _format_goals_block(self, profile: dict) -> str:
        """Format all goals with full trial history into a readable block."""
        blocks = []
        for goal in profile.get("iep_goals", []):
            goal_id = goal.get("goal_id", "?")
            domain = goal.get("domain", "unknown")
            description = goal.get("description", "")
            baseline = goal.get("baseline", {})
            baseline_val = baseline.get("value", "N/A") if isinstance(baseline, dict) else baseline
            target = goal.get("target", "N/A")
            method = goal.get("measurement_method", "N/A")
            review_date = goal.get("iep_review_date", "N/A")

            header = (
                f"--- Goal {goal_id} ({domain}) ---\n"
                f"Description: {description}\n"
                f"Baseline: {baseline_val}% | Target: {target}% | Method: {method}\n"
                f"IEP Review Date: {review_date}\n"
            )

            history = goal.get("trial_history", [])
            if history:
                lines = ["Date       | Trials | Successes | Pct  | Notes"]
                lines.append("-" * 70)
                for entry in history:
                    lines.append(
                        f"{entry.get('date', 'N/A'):10s} | "
                        f"{entry.get('trials', 0):6d} | "
                        f"{entry.get('successes', 0):9d} | "
                        f"{entry.get('pct', 0):4.0f}% | "
                        f"{entry.get('notes', '')}"
                    )
                trial_table = "\n".join(lines)
            else:
                trial_table = "No trial data available."

            blocks.append(f"{header}\nTrial History ({len(history)} sessions):\n{trial_table}")

        return "\n\n".join(blocks) if blocks else "No IEP goals found."

    def _format_alerts_block(self, student_id: str) -> str:
        """Load and format any existing alerts for this student."""
        alerts_file = Path(self.data_dir) / "alerts" / "active_alerts.json"
        if not alerts_file.exists():
            return "No prior alerts."

        all_alerts = read_json(alerts_file)
        student_alerts = [
            a for a in all_alerts
            if a.get("student_id") == student_id and not a.get("dismissed")
        ]

        if not student_alerts:
            return "No prior alerts."

        lines = []
        for a in student_alerts:
            lines.append(
                f"- [{a.get('severity', 'unknown').upper()}] {a.get('title', 'Alert')} "
                f"(Goal {a.get('goal_id', '?')}, {a.get('label', 'unknown')}): "
                f"{a.get('detail', '')}"
            )
        return "\n".join(lines)

    def _parse_trajectory(self, text: str) -> dict:
        """
        Parse the trajectory report from thinking mode output.
        Tries structured JSON first, then falls back to text extraction.
        """
        # Try JSON extraction first
        parsed = self._parse_fallback(text)

        # Check if we got a proper trajectory structure
        if "goals" in parsed and isinstance(parsed["goals"], list):
            return parsed

        # If we got partial data, fill in defaults
        if "summary" in parsed:
            parsed.setdefault("goals", [])
            parsed.setdefault("cross_goal_patterns", None)
            parsed.setdefault("recommended_priority", "")
            return parsed

        # Complete fallback — wrap the text output
        return {
            "summary": text[:500] if text else "Trajectory analysis not available.",
            "goals": [],
            "cross_goal_patterns": None,
            "recommended_priority": "",
        }
