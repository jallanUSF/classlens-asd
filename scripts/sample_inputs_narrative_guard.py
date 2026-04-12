"""Narrative/qualitative guard for sample_inputs chat path.

Feeds three qualitative scenarios through POST /api/chat and dumps the
raw Gemma responses to stdout and a markdown report. The point is to
eyeball whether the Progress Analyst persona fabricates numeric trial
percentages from prose observations, or correctly surfaces them as
qualitative notes / candidate alerts.

Scenarios:
  1. Amara cafeteria observation (04_amara/03_cafeteria_observation.md)
     + Marcus slide milestone (07_marcus/03_slide_milestone_note.md).
     Posted individually with generic "what do you see?" framing.
  2. Amara G2 "Why?" re-run with cafeteria observation in context.
     Should name the sketchbook-as-recharge pattern.
  3. Ethan plateau saturation: handwriting sample + speech transcript +
     weather chart as one combined context. Should detect saturation
     across fine-motor AND echolalia.

Requires the backend to be running on http://localhost:8001. Dumps a
report to docs/qa-reports/sample_inputs_narrative_guard_YYYY-MM-DD.md.
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

# Force UTF-8 stdout on Windows so Gemma emoji responses don't crash the
# default cp1252 console codec.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
SAMPLES = REPO / "docs" / "sample_inputs"
BACKEND = "http://localhost:8001"
REPORT_PATH = REPO / "docs" / "qa-reports" / f"sample_inputs_narrative_guard_{date.today().isoformat()}.md"

# Regex used to scan the response for numeric trial-data tokens: standalone
# percentages and fraction scores like "3/10". These are only counted as
# *fabrications* if they don't appear in the student's real profile AND
# don't appear verbatim in the source observation text.
_PCT_RE = re.compile(r"\b\d{1,3}\s*%|\b\d+\s*/\s*\d+\b")


def _normalize_token(tok: str) -> str:
    return re.sub(r"\s+", "", tok)


def _load_profile_pct_tokens(student_id: str) -> set[str]:
    """All percentage tokens that legitimately appear in a student's profile.

    Any token Gemma emits that matches one of these is recall, not
    fabrication. Covers integer percentages from trial_history and any
    target_criteria strings on the goal.
    """
    path = REPO / "data" / "students" / f"{student_id}.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for goal in data.get("iep_goals", []):
        for trial in goal.get("trial_history", []):
            pct = trial.get("pct")
            if pct is None:
                continue
            # Gemma may emit "40%" or "40.0%". Normalize to the integer form.
            out.add(f"{int(round(float(pct)))}%")
        # Grab any raw tokens in the description/target_criteria.
        for field in ("description", "target_criteria", "title"):
            val = goal.get(field) or ""
            for m in _PCT_RE.findall(str(val)):
                out.add(_normalize_token(m))
    return out


def _tokens_in_source(source: str) -> set[str]:
    return {_normalize_token(m) for m in _PCT_RE.findall(source)}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _chat(message: str, student_id: str | None) -> str:
    body = json.dumps(
        {"message": message, "student_id": student_id, "conversation_history": []}
    ).encode("utf-8")
    req = urlrequest.Request(
        f"{BACKEND}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=180) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("content", "")


def _check_fabrication(text: str, allowlist: set[str]) -> list[str]:
    """Return percentage/fraction tokens that aren't in the allowlist.

    The allowlist contains tokens from the student's real profile trial
    history AND tokens copied verbatim from the source observation. Anything
    outside that set is a fabrication — Gemma invented a number that has no
    basis in either data source.
    """
    fab: list[str] = []
    for raw in _PCT_RE.findall(text):
        norm = _normalize_token(raw)
        if norm in allowlist:
            continue
        # Allow both "40%" and "40.0%" style matches for float rounding.
        m = re.match(r"(\d+)\s*%", norm)
        if m and f"{int(m.group(1))}%" in allowlist:
            continue
        fab.append(raw)
    return fab


def run_scenario(
    label: str,
    student_id: str,
    message: str,
    source_text: str,
    expect_keywords: list[str],
    expect_no_pct: bool,
) -> dict:
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    print(f"Student: {student_id}")
    print(f"Message length: {len(message)} chars")
    t0 = time.time()
    try:
        response = _chat(message, student_id)
    except (HTTPError, URLError) as e:
        print(f"REQUEST FAILED: {e}")
        return {
            "label": label,
            "student_id": student_id,
            "error": str(e),
            "response": "",
            "keywords_hit": [],
            "fabricated_pcts": [],
            "expect_no_pct": expect_no_pct,
            "pass": False,
            "elapsed_sec": 0.0,
        }
    elapsed = time.time() - t0

    allowlist = _load_profile_pct_tokens(student_id) | _tokens_in_source(source_text)
    low = response.lower()
    hits = [k for k in expect_keywords if k.lower() in low]
    pcts = _check_fabrication(response, allowlist)

    pct_ok = (not expect_no_pct) or len(pcts) == 0
    kw_ok = len(hits) >= max(1, len(expect_keywords) // 2)
    passed = pct_ok and kw_ok

    print(f"\nElapsed: {elapsed:.1f}s")
    print(f"Response ({len(response)} chars):")
    print("-" * 70)
    print(response)
    print("-" * 70)
    print(f"Keyword hits ({len(hits)}/{len(expect_keywords)}): {hits}")
    print(f"Fabricated percentages found: {pcts or 'none'}")
    print(f"Verdict: {'PASS' if passed else 'FAIL'}")

    return {
        "label": label,
        "student_id": student_id,
        "response": response,
        "keywords_hit": hits,
        "keywords_expected": expect_keywords,
        "fabricated_pcts": pcts,
        "expect_no_pct": expect_no_pct,
        "pass": passed,
        "elapsed_sec": round(elapsed, 1),
    }


def main() -> int:
    amara_obs = _read(SAMPLES / "04_amara" / "03_cafeteria_observation.md")
    marcus_note = _read(SAMPLES / "07_marcus" / "03_slide_milestone_note.md")
    ethan_handwriting = _read(SAMPLES / "05_ethan" / "01_handwriting_sample.md")
    ethan_speech = _read(SAMPLES / "05_ethan" / "02_speech_transcript.md")
    ethan_weather = _read(SAMPLES / "05_ethan" / "03_weather_chart.md")

    scenarios: list[dict] = []

    ethan_combined_source = (
        "### Source 1 — Handwriting sample (G2, fine motor)\n\n"
        + ethan_handwriting
        + "\n\n### Source 2 — Speech transcript (G1, functional communication)\n\n"
        + ethan_speech
        + "\n\n### Source 3 — Weather journal (strength / regulation)\n\n"
        + ethan_weather
    )

    # Scenario 1a — Amara cafeteria observation, generic framing.
    scenarios.append(
        run_scenario(
            label="S1a — Amara cafeteria observation (narrative guard)",
            student_id="amara_2026",
            message=(
                "Mr. Chen dropped off qualitative observation notes from Friday's "
                "lunch. These are direct observations, not probed trial data — "
                "please treat them as a note rather than a numeric data point, "
                "and tell me what patterns you see.\n\n"
                + amara_obs
            ),
            source_text=amara_obs,
            expect_keywords=["qualitative", "observation", "pattern", "withdraw", "mask", "capacity"],
            expect_no_pct=True,
        )
    )

    # Scenario 1b — Marcus slide milestone, generic framing.
    scenarios.append(
        run_scenario(
            label="S1b — Marcus slide milestone (narrative guard)",
            student_id="marcus_2026",
            message=(
                "Ms. Tran sent over this anecdotal note from today's recess. "
                "This is not trial data — it's a milestone observation. Please "
                "give it back to me as a celebration / narrative rather than "
                "recording percentages.\n\n"
                + marcus_note
            ),
            source_text=marcus_note,
            expect_keywords=["milestone", "courage", "regulation", "peer", "celebrate"],
            expect_no_pct=True,
        )
    )

    # Scenario 2 — Amara G2 "Why?" with cafeteria observation in context.
    scenarios.append(
        run_scenario(
            label="S2 — Amara G2 Why? with cafeteria context",
            student_id="amara_2026",
            message=(
                "Amara's G2 (peer initiations) alert is flagged as DECLINING. "
                "Mr. Chen also dropped off this direct-observation note from "
                "Friday's lunch. Given the talk-ticket data AND this observation, "
                "can you explain what's driving the decline? What should I tell "
                "the IEP team on Monday?\n\n"
                + amara_obs
            ),
            source_text=amara_obs,
            expect_keywords=["sketchbook", "recharge", "mask", "capacity", "withdraw"],
            expect_no_pct=False,
        )
    )

    # Scenario 3 — Ethan plateau saturation across fine-motor + echolalia.
    scenarios.append(
        run_scenario(
            label="S3 — Ethan plateau multimodal saturation",
            student_id="ethan_2026",
            message=(
                "I want your read on Ethan's current plateau picture. Three "
                "data sources for you:\n\n"
                + ethan_combined_source
                + "\n\nLooking across all three, is this a saturation picture? "
                "Are there coping or regulation angles I should escalate with "
                "the OT and SLP before the annual IEP?"
            ),
            source_text=ethan_combined_source,
            expect_keywords=[
                "saturation",
                "plateau",
                "fatigue",
                "sensory",
                "echolalia",
                "regulation",
                "fine motor",
            ],
            expect_no_pct=False,
        )
    )

    # Write the markdown report.
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Sample Inputs Narrative Guard — {date.today().isoformat()}",
        "",
        f"Backend: `{BACKEND}`",
        "",
        "| # | Scenario | Student | Elapsed | Pct tokens | Verdict |",
        "|---|---|---|---|---|---|",
    ]
    for i, s in enumerate(scenarios, 1):
        verdict = "PASS" if s["pass"] else "FAIL"
        lines.append(
            f"| {i} | {s['label']} | {s['student_id']} | "
            f"{s['elapsed_sec']}s | {s['fabricated_pcts'] or '—'} | {verdict} |"
        )
    lines.append("")
    for i, s in enumerate(scenarios, 1):
        lines += [
            f"## {i}. {s['label']}",
            "",
            f"- Student: `{s['student_id']}`",
            f"- Elapsed: {s['elapsed_sec']}s",
            f"- Expected keywords: {s['keywords_expected']}",
            f"- Keywords hit: {s['keywords_hit']}",
            f"- Percentage tokens found: {s['fabricated_pcts'] or 'none'}",
            f"- Expect no percentages: **{s['expect_no_pct']}**",
            f"- Verdict: **{'PASS' if s['pass'] else 'FAIL'}**",
            "",
            "### Response",
            "",
            "```",
            s.get("response", "")[:4000],
            "```",
            "",
        ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    passed = sum(1 for s in scenarios if s["pass"])
    total = len(scenarios)
    print(f"\n{'=' * 70}")
    print(f"Summary: {passed}/{total} scenarios pass")
    print(f"Report: {REPORT_PATH}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
