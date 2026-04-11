"""
Alerts endpoint — surfaces students needing attention.
Analyzes trial data to detect plateaus, regressions, and upcoming reviews.
"""

import json
import os
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["alerts"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
ALERTS_FILE = DATA_DIR / "alerts" / "active_alerts.json"

# Sanitization regexes — duplicated from chat.py to keep this router
# self-contained and avoid a cross-router import cycle.
_SCRIPT_STYLE_BLOCK_RE = re.compile(
    r"<(script|style)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL
)
_ANY_TAG_RE = re.compile(r"<[^>]+>")


def _sanitize_model_text(text: str) -> str:
    """Remove HTML tags and dangerous script/style blocks from model output."""
    if not text:
        return text
    text = _SCRIPT_STYLE_BLOCK_RE.sub("", text)
    text = _ANY_TAG_RE.sub("", text)
    return text.strip()


def _get_progress_analyst():
    """Create a ProgressAnalyst instance with a real or mock client.

    Mirrors the pattern in materials.py::_get_forge — real Gemma when an
    API key is present, MockGemmaClient otherwise so the demo path still
    works offline.
    """
    from agents.progress_analyst import ProgressAnalyst

    if os.getenv("OPENROUTER_API_KEY") or (
        os.getenv("GOOGLE_AI_STUDIO_KEY")
        and os.getenv("GOOGLE_AI_STUDIO_KEY") != "your_api_key_here"
    ):
        from core.gemma_client import GemmaClient
        return ProgressAnalyst(GemmaClient(), data_dir=str(DATA_DIR))
    else:
        from tests.mock_api_responses import MockGemmaClient
        return ProgressAnalyst(MockGemmaClient(), data_dir=str(DATA_DIR))


def _load_alerts() -> list[dict]:
    """Load active alerts from file."""
    if not ALERTS_FILE.exists():
        return []
    with open(ALERTS_FILE, "r") as f:
        return json.load(f)


def _save_alerts(alerts: list[dict]):
    """Save alerts to file."""
    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def _analyze_student_alerts(student_id: str, data: dict) -> list[dict]:
    """Analyze a student's data for alert conditions."""
    alerts = []
    today = date.today().isoformat()

    for goal in data.get("iep_goals", []):
        history = goal.get("trial_history", [])
        if len(history) < 3:
            continue

        # Get last 3 session percentages
        recent = [h.get("pct", 0) for h in history[-3:]]
        older = [h.get("pct", 0) for h in history[-6:-3]] if len(history) >= 6 else []

        recent_avg = sum(recent) / len(recent) if recent else 0

        # Plateau detection: last 3 sessions within 5% range
        if max(recent) - min(recent) <= 5 and len(history) >= 6:
            alerts.append({
                "id": str(uuid.uuid4())[:8],
                "student_id": student_id,
                "alert_type": "plateau",
                "goal_id": goal.get("goal_id", ""),
                "title": f"{data.get('name', student_id)} — {goal.get('domain', 'Goal').replace('_', ' ').title()} plateaued",
                "detail": f"Last 3 sessions: {', '.join(f'{p:.0f}%' for p in recent)}. No meaningful change.",
                "suggested_action": "Adjust prompting strategy or generate updated materials",
                "created_date": today,
                "dismissed": False,
            })

        # Regression detection: downward trend in last 3
        if older:
            older_avg = sum(older) / len(older)
            if recent_avg < older_avg - 10:
                alerts.append({
                    "id": str(uuid.uuid4())[:8],
                    "student_id": student_id,
                    "alert_type": "regression",
                    "goal_id": goal.get("goal_id", ""),
                    "title": f"{data.get('name', student_id)} — {goal.get('domain', 'Goal').replace('_', ' ').title()} regression",
                    "detail": f"Average dropped from {older_avg:.0f}% to {recent_avg:.0f}%.",
                    "suggested_action": "Review recent changes and consider reverting strategy",
                    "created_date": today,
                    "dismissed": False,
                })

    return alerts


@router.get("/alerts")
async def get_alerts() -> list[dict[str, Any]]:
    """
    Get all active alerts across all students.
    Regenerates alerts from current data, plus any pinned alerts from file.
    """
    students_dir = DATA_DIR / "students"
    if not students_dir.exists():
        return []

    all_alerts = []
    for json_file in students_dir.glob("*.json"):
        with open(json_file, "r") as f:
            data = json.load(f)
        student_id = json_file.stem
        all_alerts.extend(_analyze_student_alerts(student_id, data))

    # Merge with previously saved alerts
    existing = _load_alerts()
    dismissed_ids = {a["id"] for a in existing if a.get("dismissed")}

    # Include pinned alerts from file (manually-created demo alerts)
    pinned = [a for a in existing if a.get("pinned") and not a.get("dismissed")]
    auto_ids = {a["id"] for a in all_alerts}
    for p in pinned:
        if p["id"] not in auto_ids:
            all_alerts.append(p)

    # Filter out dismissed
    active = [a for a in all_alerts if a["id"] not in dismissed_ids]

    _save_alerts(active + [a for a in existing if a.get("dismissed")])
    return active


@router.put("/alerts/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str) -> dict[str, str]:
    """Dismiss an alert."""
    alerts = _load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            alert["dismissed"] = True
            _save_alerts(alerts)
            return {"status": "dismissed", "id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")


def _find_current_alert(alert_id: str) -> dict | None:
    """Find an alert by id across both regenerated and pinned alerts.

    Alerts are mostly ephemeral — get_alerts regenerates them on every call
    from student trial data. So we re-run the same logic here to resolve an
    alert_id back to its full record (student_id + goal_id).
    """
    # Regenerate from live student data
    students_dir = DATA_DIR / "students"
    if students_dir.exists():
        for json_file in students_dir.glob("*.json"):
            with open(json_file, "r") as f:
                data = json.load(f)
            for alert in _analyze_student_alerts(json_file.stem, data):
                if alert["id"] == alert_id:
                    return alert

    # Fall back to persisted alerts (pinned demo alerts, etc.)
    for alert in _load_alerts():
        if alert["id"] == alert_id and not alert.get("dismissed"):
            return alert

    return None


@router.post("/alerts/{alert_id}/analyze")
async def analyze_alert(alert_id: str) -> dict[str, Any]:
    """Run ProgressAnalyst on the goal behind this alert, returning the
    Gemma thinking trace and final analysis.

    Thinking mode only actually populates ``thinking`` on the Google AI
    Studio provider — OpenRouter and Ollama fall back to normal generation
    and return an empty thinking string (see GemmaClient.generate_with_thinking).
    """
    alert = _find_current_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    student_id = alert.get("student_id")
    goal_id = alert.get("goal_id")
    if not student_id or not goal_id:
        raise HTTPException(
            status_code=400,
            detail="Alert is missing student_id or goal_id — cannot analyze",
        )

    # Verify student/goal exist before burning an API call
    student_path = DATA_DIR / "students" / f"{student_id}.json"
    if not student_path.exists():
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    analyst = _get_progress_analyst()
    try:
        # ProgressAnalyst.analyze already calls generate_with_thinking
        # internally and returns a dict with 'thinking' + parsed fields.
        # The raw Gemma 'output' text is stored in progress_note on the
        # text-fallback path; we want the actual final text for display,
        # so we also build a human-readable summary from the parsed fields.
        result = analyst.analyze(student_id, goal_id)
    except Exception as e:  # pragma: no cover — network/provider errors
        raise HTTPException(
            status_code=502,
            detail=f"ProgressAnalyst failed: {e}",
        )

    thinking = _sanitize_model_text(result.get("thinking", "") or "")

    # Build the "Analysis" body. Prefer the progress_note (which on the
    # text-fallback path already holds the raw model output); otherwise
    # stitch together the structured fields.
    progress_note = result.get("progress_note", "") or ""
    recommendation = result.get("recommendation", "") or ""
    trend = result.get("trend", "") or ""
    alert_message = result.get("alert_message", "") or ""

    parts: list[str] = []
    if progress_note:
        parts.append(progress_note)
    if trend and trend not in progress_note:
        parts.append(f"Trend: {trend}.")
    if alert_message and alert_message not in progress_note:
        parts.append(f"Alert: {alert_message}.")
    if recommendation:
        parts.append(f"Recommendation: {recommendation}")
    output_text = _sanitize_model_text("\n\n".join(p for p in parts if p))

    return {
        "alert_id": alert_id,
        "goal_id": goal_id,
        "student_id": student_id,
        "thinking": thinking,
        "output": output_text,
    }
