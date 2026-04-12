#!/usr/bin/env python3
"""
Generate precomputed trajectory reports for the 3 demo students.

Writes to data/precomputed/trajectory_{student_id}.json. The demo page
loads these instantly — no live Gemma call.

Usage:
    python scripts/generate_trajectory_cache.py              # all 3 demo students
    python scripts/generate_trajectory_cache.py maya_2026    # single student
    python scripts/generate_trajectory_cache.py --mock       # force mock client
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.sanitize import has_real_model_credentials, sanitize_model_text
from core.json_io import write_json

DEMO_STUDENTS = ["maya_2026", "jaylen_2026", "amara_2026"]
PRECOMPUTED_DIR = PROJECT_ROOT / "data" / "precomputed"


def _get_analyst(force_mock: bool):
    from agents.trajectory_analyst import TrajectoryAnalyst

    if force_mock or not has_real_model_credentials():
        from tests.mock_api_responses import MockGemmaClient
        print("[info] Using MockGemmaClient")
        return TrajectoryAnalyst(MockGemmaClient(), data_dir=str(PROJECT_ROOT / "data"))
    from core.gemma_client import GemmaClient
    print("[info] Using real GemmaClient (Google AI Studio)")
    return TrajectoryAnalyst(GemmaClient(), data_dir=str(PROJECT_ROOT / "data"))


def generate_one(student_id: str, analyst) -> None:
    print(f"\n--- {student_id} ---")
    print("  Analyzing trajectory (long-context + thinking mode)...")
    result = analyst.analyze_trajectory(student_id)

    # Match router sanitization so cached content is immediately servable
    result["thinking"] = sanitize_model_text(result.get("thinking", "") or "")
    if result.get("summary"):
        result["summary"] = sanitize_model_text(result["summary"])
    for goal in result.get("goals", []):
        if goal.get("trend_summary"):
            goal["trend_summary"] = sanitize_model_text(goal["trend_summary"])
        if goal.get("iep_meeting_note"):
            goal["iep_meeting_note"] = sanitize_model_text(goal["iep_meeting_note"])

    goals = result.get("goals", [])
    summary_preview = (result.get("summary") or "")[:120]
    print(f"  Goals analyzed: {len(goals)}")
    print(f"  Summary: {summary_preview}...")
    print(f"  Thinking trace: {len(result.get('thinking') or '')} chars")

    PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PRECOMPUTED_DIR / f"trajectory_{student_id}.json"
    write_json(out_path, result)
    size = out_path.stat().st_size
    print(f"  [ok] Written to data/precomputed/trajectory_{student_id}.json ({size} bytes)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("student", nargs="?", help="Specific student_id, or omit for all demo students")
    ap.add_argument("--mock", action="store_true", help="Force mock Gemma client")
    args = ap.parse_args()

    analyst = _get_analyst(force_mock=args.mock)
    students = [args.student] if args.student else DEMO_STUDENTS

    for sid in students:
        try:
            generate_one(sid, analyst)
        except Exception as exc:  # noqa: BLE001 — surface and continue
            print(f"  [fail] Failed: {exc}")

    print("\nDone.")


if __name__ == "__main__":
    main()
