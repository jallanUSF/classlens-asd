"""
Agent 6: Podcast Producer
Generates a ~2-minute Host/Guest dialogue briefing on a student's IEP progress.

Gemma 4 does all the reasoning (thinking mode → dialogue script). Edge TTS is
commodity plumbing that turns the script into MP3. See
`docs/plans/2026-04-12-podcast-briefing-design.md` for full design rationale.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from agents.base import BaseAgent
from agents.trajectory_analyst import TrajectoryAnalyst
from core.json_io import read_json
from prompts.templates import PODCAST_PRODUCER_SYSTEM, PODCAST_PRODUCER_USER


class PodcastProducer(BaseAgent):
    """Writes a Host/Guest dialogue script from a student's full IEP data."""

    def __init__(self, client, data_dir: str = "data"):
        super().__init__(client)
        self.data_dir = data_dir
        # Reuse the trajectory analyst's context-gathering — identical shape.
        self._traj = TrajectoryAnalyst(client, data_dir=data_dir)

    def produce_script(self, student_id: str, language: str = "en") -> dict:
        """Call Gemma (thinking mode) to write the dialogue script.

        Returns a dict with: title, script (list of {speaker,text}), language,
        student_id, generated_date, thinking (Gemma's reasoning chain).
        """
        profile = self._load_student_raw(student_id, self.data_dir)

        goals_block = self._traj._format_goals_block(profile)
        alerts_block = self._traj._format_alerts_block(student_id)
        trajectory_summary = self._load_trajectory_summary(student_id)

        prompt = PODCAST_PRODUCER_USER.format(
            student_name=profile.get("name", student_id),
            grade=profile.get("grade", ""),
            asd_level=profile.get("asd_level", ""),
            communication_level=profile.get("communication_level", "verbal"),
            interests=", ".join(profile.get("interests", [])) or "none listed",
            goals_block=goals_block,
            alerts_block=alerts_block,
            trajectory_summary=trajectory_summary,
            today=date.today().isoformat(),
        )

        result = self.client.generate_with_thinking(
            prompt=prompt,
            system=PODCAST_PRODUCER_SYSTEM,
        )

        parsed = self._parse_script(result.get("output", ""))
        parsed["student_id"] = student_id
        parsed["language"] = language
        parsed["generated_date"] = date.today().isoformat()
        parsed["thinking"] = result.get("thinking", "") or ""
        return parsed

    def _load_trajectory_summary(self, student_id: str) -> str:
        """Pull a one-paragraph trajectory summary from the precomputed cache if present."""
        traj_path = Path(self.data_dir) / "precomputed" / f"trajectory_{student_id}.json"
        if not traj_path.exists():
            return "No precomputed trajectory available."
        try:
            data = read_json(traj_path)
            summary = data.get("summary") or ""
            priority = data.get("recommended_priority") or ""
            bits = [s for s in (summary, priority and f"Priority: {priority}") if s]
            return "\n".join(bits) or "No trajectory summary available."
        except Exception:
            return "No trajectory summary available."

    def _parse_script(self, text: str) -> dict:
        """Parse Gemma's JSON output into a {title, script:[...]} dict."""
        parsed = self._parse_fallback(text)
        script = parsed.get("script")
        if isinstance(script, list) and all(
            isinstance(line, dict) and "speaker" in line and "text" in line
            for line in script
        ):
            return {
                "title": parsed.get("title", "Progress Briefing"),
                "script": script,
            }

        # Fallback: wrap the whole text as a single Host line so the UI still works
        return {
            "title": "Progress Briefing",
            "script": [{"speaker": "host", "text": (text or "").strip()[:600]}],
        }
