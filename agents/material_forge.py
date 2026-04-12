"""
Agent 4: Material Forge
Generates personalized materials for three audiences:
  Teacher: lesson plans, tracking sheets, social stories, visual schedules, first-then boards
  Parents: parent communications
  Admin:   progress reports

Uses Gemma 4 function calling with student profile as context.
"""

import json

from agents.base import BaseAgent
from schemas.tools import (
    GENERATE_LESSON_PLAN,
    GENERATE_TRACKING_SHEET,
    GENERATE_SOCIAL_STORY,
    GENERATE_PARENT_COMM,
    GENERATE_ADMIN_REPORT,
)
from prompts.templates import (
    LANGUAGE_CODE_TO_NAME,
    MATERIAL_FORGE_SYSTEM,
    MATERIAL_FORGE_LESSON_PLAN,
    MATERIAL_FORGE_TRACKING_SHEET,
    MATERIAL_FORGE_SOCIAL_STORY,
    MATERIAL_FORGE_VISUAL_SCHEDULE,
    MATERIAL_FORGE_FIRST_THEN_BOARD,
    MATERIAL_FORGE_PARENT_COMM,
    MATERIAL_FORGE_TRANSLATE_PARENT_COMM,
    MATERIAL_FORGE_ADMIN_REPORT,
)


class MaterialForge(BaseAgent):
    """Generates 7 output types for teachers, parents, and administrators."""

    def __init__(self, client, data_dir: str = "data"):
        super().__init__(client)
        self.data_dir = data_dir

    # ── Helpers ────────────────────────────────────────────────

    def _profile(self, student_id: str) -> dict:
        return self._load_student_raw(student_id, self.data_dir)

    def _get_goal(self, profile: dict, goal_id: str) -> dict:
        for g in profile["iep_goals"]:
            if g["goal_id"] == goal_id:
                return g
        raise ValueError(f"Goal {goal_id} not found")

    def _sensory(self, profile: dict, key: str) -> str:
        return ", ".join(profile.get("sensory_profile", {}).get(key, [])) or "Not specified"

    def _interests(self, profile: dict) -> str:
        return ", ".join(profile.get("interests", []))

    def _reinforcers(self, profile: dict) -> str:
        return ", ".join(profile.get("reinforcers", []))

    def _baseline_val(self, goal: dict):
        b = goal.get("baseline", {})
        return b.get("value", "N/A") if isinstance(b, dict) else b

    def _latest_trend(self, goal: dict) -> str:
        """Quick trend summary from trial history."""
        history = goal.get("trial_history", [])
        if len(history) < 2:
            return "Insufficient data for trend"
        recent = [h.get("pct", 0) for h in history[-3:]]
        older = [h.get("pct", 0) for h in history[-6:-3]] if len(history) >= 6 else [h.get("pct", 0) for h in history[:3]]
        recent_avg = sum(recent) / len(recent) if recent else 0
        older_avg = sum(older) / len(older) if older else 0
        if recent_avg > older_avg + 5:
            return f"Improving (recent avg {recent_avg:.0f}%)"
        elif recent_avg < older_avg - 5:
            return f"Declining (recent avg {recent_avg:.0f}%)"
        return f"Stable (recent avg {recent_avg:.0f}%)"

    def _call_with_fallback(self, prompt: str, tools: list, system: str) -> dict:
        """Call Gemma with function calling, fall back to text parsing."""
        result = self.client.generate_with_tools(
            prompt=prompt, tools=tools, system=system,
        )
        if "function" in result:
            return result["args"]
        return self._parse_fallback(result.get("text", ""))

    def _call_with_thinking(self, prompt: str, tools: list, system: str, student_id: str) -> dict:
        """Call Gemma with thinking mode for confidence scoring.

        Uses generate_with_thinking for the reasoning chain, then parses
        the output as structured content. Returns the content dict with
        'thinking' and 'confidence_score' fields added.
        """
        result = self.client.generate_with_thinking(
            prompt=prompt, system=system,
        )
        thinking = result.get("thinking", "")
        output = result.get("output", "")

        # Parse the output as structured content
        content = self._parse_fallback(output)

        # Add thinking trace and confidence score
        content["_thinking"] = thinking
        content["_confidence_score"] = self._compute_confidence(
            thinking, student_id,
        )
        return content

    def _compute_confidence(self, thinking: str, student_id: str) -> str:
        """Determine confidence level based on thinking trace and data availability.

        Returns: "high", "review_recommended", or "flag_for_expert"
        """
        # Check data richness — more trial data = higher confidence
        try:
            profile = self._profile(student_id)
            total_trials = sum(
                len(g.get("trial_history", []))
                for g in profile.get("iep_goals", [])
            )
        except Exception:
            total_trials = 0

        # Check thinking trace for hedge language
        hedge_terms = [
            "unclear", "limited data", "unable to determine",
            "not enough", "insufficient", "uncertain", "no data",
            "cannot determine", "unknown", "missing information",
            "no trial", "no history", "no prior",
        ]
        thinking_lower = thinking.lower()
        hedge_count = sum(1 for term in hedge_terms if term in thinking_lower)

        if total_trials < 3 or hedge_count >= 3:
            return "flag_for_expert"
        if total_trials < 6 or hedge_count >= 1:
            return "review_recommended"
        return "high"

    def _generate_text(self, prompt: str, system: str) -> str:
        """Plain text generation (for visual schedules and first-then boards)."""
        return self.client.generate(prompt=prompt, system=system)

    # ── 1. Lesson Plans (Sarah's #1 request) ──────────────────

    def generate_lesson_plan(self, student_id: str, goal_id: str) -> dict:
        """IEP goal -> scaffolded lesson plan incorporating student interests."""
        p = self._profile(student_id)
        g = self._get_goal(p, goal_id)
        prompt = MATERIAL_FORGE_LESSON_PLAN.format(
            student_name=p["name"],
            grade=p["grade"],
            asd_level=p["asd_level"],
            communication_level=p.get("communication_level", "verbal"),
            interests=self._interests(p),
            sensory_seeks=self._sensory(p, "seeks"),
            sensory_avoids=self._sensory(p, "avoids"),
            reinforcers=self._reinforcers(p),
            calming_strategies=self._sensory(p, "calming_strategies"),
            domain=g["domain"],
            goal_description=g["description"],
            baseline=self._baseline_val(g),
            target=g["target"],
            measurement_method=g.get("measurement_method", "N/A"),
            progress_summary=self._latest_trend(g),
        )
        return self._call_with_thinking(prompt, [GENERATE_LESSON_PLAN], MATERIAL_FORGE_SYSTEM, student_id)

    # ── 2. Tracking Sheets ────────────────────────────────────

    def generate_tracking_sheet(self, student_id: str, goal_id: str) -> dict:
        """Per-goal clipboard-ready tracking sheet."""
        p = self._profile(student_id)
        g = self._get_goal(p, goal_id)
        prompt = MATERIAL_FORGE_TRACKING_SHEET.format(
            student_name=p["name"],
            grade=p["grade"],
            goal_id=g["goal_id"],
            goal_description=g["description"],
            baseline=self._baseline_val(g),
            target=g["target"],
            measurement_method=g.get("measurement_method", "N/A"),
        )
        return self._call_with_thinking(prompt, [GENERATE_TRACKING_SHEET], MATERIAL_FORGE_SYSTEM, student_id)

    # ── 3. Social Stories (Carol Gray framework) ──────────────

    def generate_social_story(self, student_id: str, scenario: str, skill: str = "") -> dict:
        """Carol Gray framework social story with student interests."""
        p = self._profile(student_id)
        prompt = MATERIAL_FORGE_SOCIAL_STORY.format(
            student_name=p["name"],
            grade=p["grade"],
            asd_level=p["asd_level"],
            communication_level=p.get("communication_level", "verbal"),
            interests=self._interests(p),
            goal_description=scenario,
            situation_or_transition=scenario,
            skill_to_teach=skill or scenario,
        )
        return self._call_with_thinking(prompt, [GENERATE_SOCIAL_STORY], MATERIAL_FORGE_SYSTEM, student_id)

    # ── 4. Visual Schedules ───────────────────────────────────

    def generate_visual_schedule(
        self, student_id: str, routine: str, setting: str = "classroom", duration: str = "30 minutes",
    ) -> str:
        """Sequential visual schedule description."""
        p = self._profile(student_id)
        goal_desc = p["iep_goals"][0]["description"] if p["iep_goals"] else "General routine"
        prompt = MATERIAL_FORGE_VISUAL_SCHEDULE.format(
            student_name=p["name"],
            grade=p["grade"],
            asd_level=p["asd_level"],
            interests=self._interests(p),
            communication_level=p.get("communication_level", "verbal"),
            sensory_avoids=self._sensory(p, "avoids"),
            routine_name=routine,
            setting=setting,
            goal_description=goal_desc,
            duration=duration,
        )
        return self._generate_text(prompt, MATERIAL_FORGE_SYSTEM)

    # ── 5. First-Then Boards ──────────────────────────────────

    def generate_first_then(self, student_id: str, goal_id: str) -> str:
        """First-Then board text using student's reinforcers."""
        p = self._profile(student_id)
        g = self._get_goal(p, goal_id)
        prompt = MATERIAL_FORGE_FIRST_THEN_BOARD.format(
            student_name=p["name"],
            grade=p["grade"],
            asd_level=p["asd_level"],
            interests=self._interests(p),
            sensory_seeks=self._sensory(p, "seeks"),
            reinforcers=self._reinforcers(p),
            goal_description=g["description"],
            baseline=self._baseline_val(g),
        )
        return self._generate_text(prompt, MATERIAL_FORGE_SYSTEM)

    # ── 6. Parent Communications ──────────────────────────────

    def generate_parent_comm(
        self, student_id: str, goal_id: str, date: str = "", language: str = "en",
    ) -> dict:
        """Warm, jargon-free parent progress update.

        Args:
            language: ISO-639 code (en, es, vi, zh). Unknown codes fall back to English.
        """
        p = self._profile(student_id)
        g = self._get_goal(p, goal_id)
        history = g.get("trial_history", [])
        recent_pcts = [h.get("pct", 0) for h in history[-5:]]
        success_rate = sum(recent_pcts) / len(recent_pcts) if recent_pcts else 0

        language_name = LANGUAGE_CODE_TO_NAME.get(language, "English")

        prompt = MATERIAL_FORGE_PARENT_COMM.format(
            student_name=p["name"],
            grade=p["grade"],
            parent_email=p.get("parent_email", "parent@email.com"),
            parent_phone=p.get("parent_phone", ""),
            goal_description=g["description"],
            baseline=self._baseline_val(g),
            target=g["target"],
            measurement_method=g.get("measurement_method", "N/A"),
            trial_count=len(history),
            success_rate=f"{success_rate:.0f}",
            trend_direction=self._latest_trend(g),
            progress_summary=self._latest_trend(g),
            language_name=language_name,
            teacher_name=p.get("teacher", "Ms. Rodriguez"),
        )
        return self._call_with_thinking(prompt, [GENERATE_PARENT_COMM], MATERIAL_FORGE_SYSTEM, student_id)

    def translate_parent_comm(
        self, approved_content: str, language: str = "es",
    ) -> dict:
        """Translate an approved English parent letter to the target language.

        Unlike generate_parent_comm which regenerates from scratch (losing
        student-specific color like interest references), this method preserves
        every detail from the approved EN version by asking Gemma to translate
        it directly.
        """
        language_name = LANGUAGE_CODE_TO_NAME.get(language, "English")
        prompt = MATERIAL_FORGE_TRANSLATE_PARENT_COMM.format(
            language_name=language_name,
            approved_content=approved_content,
        )
        # Plain text generation — no function calling needed for translation.
        translated = self._generate_text(prompt, MATERIAL_FORGE_SYSTEM)
        return {"text": translated}

    # ── 7. Admin Reports ──────────────────────────────────────

    def generate_admin_report(
        self, student_id: str, period: str = "Monthly",
    ) -> dict:
        """Polished progress report for administrators."""
        p = self._profile(student_id)
        from datetime import date as dt_date
        today = dt_date.today().isoformat()

        prompt = MATERIAL_FORGE_ADMIN_REPORT.format(
            student_name=p["name"],
            student_id=student_id,
            grade=p["grade"],
            case_manager_name=p.get("teacher", "Case Manager"),
            goal_id="ALL",
            domain="All domains",
            goal_description="See individual goal summaries below",
            baseline="See per-goal data",
            target="See per-goal data",
            measurement_method="Mixed methods",
            status_date=today,
            period_start="See report period",
            period_end=today,
            trial_count=sum(len(g.get("trial_history", [])) for g in p["iep_goals"]),
            success_rate="See per-goal data",
            trend_direction="See per-goal data",
            days_active="See per-goal data",
            progress_summary=self._build_goals_summary(p),
            regression_info="None" if not self._has_regression(p) else "See goal details",
        )
        return self._call_with_thinking(prompt, [GENERATE_ADMIN_REPORT], MATERIAL_FORGE_SYSTEM, student_id)

    def _build_goals_summary(self, profile: dict) -> str:
        """Build a text summary of all goals for admin report context."""
        lines = []
        for g in profile["iep_goals"]:
            history = g.get("trial_history", [])
            if history:
                recent = [h.get("pct", 0) for h in history[-3:]]
                avg = sum(recent) / len(recent)
                lines.append(
                    f"[{g['goal_id']}] {g['domain']}: {g['description'][:80]}... "
                    f"Current avg: {avg:.0f}%, Target: {g['target']}%, "
                    f"Trend: {self._latest_trend(g)}"
                )
            else:
                lines.append(f"[{g['goal_id']}] {g['domain']}: No trial data yet")
        return "\n".join(lines)

    def _has_regression(self, profile: dict) -> bool:
        """Quick check for any goal showing regression."""
        for g in profile["iep_goals"]:
            trend = self._latest_trend(g).lower()
            if "declining" in trend:
                return True
        return False
