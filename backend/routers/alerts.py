"""
Alerts endpoint — surfaces students needing attention.
Analyzes trial data to detect plateaus, regressions, and upcoming reviews.
"""

import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["alerts"])

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
ALERTS_FILE = DATA_DIR / "alerts" / "active_alerts.json"


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
