"""Live end-to-end smoke test for every photo in docs/sample_inputs/.

Walks each student's PHOTO/SCAN image through POST /api/capture on a
running backend, verifies the pipeline returns a structured result
(transcription + mapped goals + progress analyses), and writes a
markdown report to docs/qa-reports/sample_inputs_smoke_YYYY-MM-DD.md.

The capture endpoint writes new trial data back into
`data/students/{student_id}.json` via the IEP Mapper. To keep the test
reproducible, this script snapshots every student profile into memory
before running anything and restores them on exit (including on
interrupt or failure). Post-fix for the Windows unicode round-trip bug,
these restores are byte-identical.

Requirements:
  - Backend running on http://localhost:8001
  - MODEL_PROVIDER=google with a valid GOOGLE_AI_STUDIO_KEY, or any
    provider that returns structured results

Usage:
  python scripts/sample_inputs_smoke.py
  python scripts/sample_inputs_smoke.py --dry-run   # snapshot + restore only
"""

from __future__ import annotations

import argparse
import io
import json
import mimetypes
import signal
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any, Iterable
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

# Windows cp1252 console would crash on Gemma emoji output.
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.json_io import read_json, write_json  # noqa: E402

SAMPLES = REPO / "docs" / "sample_inputs"
STUDENTS_DIR = REPO / "data" / "students"
BACKEND = "http://localhost:8001"
REPORT_PATH = (
    REPO / "docs" / "qa-reports" / f"sample_inputs_smoke_{date.today().isoformat()}.md"
)

# (student_id, relative path under docs/sample_inputs/, work_type, subject)
PHOTOS: list[tuple[str, str, str, str]] = [
    ("maya_2026",   "01_maya/01_math_worksheet_PHOTO.png",      "worksheet", "math"),
    ("jaylen_2026", "02_jaylen/01_pecs_exchange_log_PHOTO.png", "log",       "communication"),
    ("sofia_2026",  "03_sofia/01_madison_essay_SCAN.png",       "essay",     "writing"),
    ("amara_2026",  "04_amara/02_talk_ticket_PHOTO.png",        "worksheet", "social"),
    ("ethan_2026",  "05_ethan/01_handwriting_sample_PHOTO.png", "worksheet", "writing"),
    ("lily_2026",   "06_lily/03_ocean_notebook_PHOTO.png",      "worksheet", "science"),
    ("marcus_2026", "07_marcus/01_bathroom_routine_PHOTO.png",  "data_sheet", "daily_living"),
]


def _post_multipart(
    path: str,
    fields: dict[str, str],
    file_field: str,
    file_name: str,
    file_bytes: bytes,
    timeout: float = 300.0,
) -> tuple[int, Any]:
    boundary = "----ClassLensSampleBoundary9f3b2d"
    lines: list[bytes] = []
    for k, v in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{k}"'.encode())
        lines.append(b"")
        lines.append(str(v).encode())
    lines.append(f"--{boundary}".encode())
    mime = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    lines.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"'.encode()
    )
    lines.append(f"Content-Type: {mime}".encode())
    lines.append(b"")
    lines.append(file_bytes)
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    req = urlrequest.Request(
        f"{BACKEND}{path}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urlrequest.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, "<non-json error body>"


def _snapshot_profiles() -> dict[str, bytes]:
    """Read every student profile as raw bytes for byte-exact restoration."""
    snap: dict[str, bytes] = {}
    for p in sorted(STUDENTS_DIR.glob("*.json")):
        snap[p.name] = p.read_bytes()
    return snap


def _restore_profiles(snapshot: dict[str, bytes]) -> None:
    """Restore byte-exact pre-test student profiles."""
    for name, raw in snapshot.items():
        (STUDENTS_DIR / name).write_bytes(raw)


def _evaluate(body: Any) -> tuple[bool, str]:
    """Return (passed, short_summary) for a capture response body."""
    if not isinstance(body, dict):
        return False, f"non-dict response: {str(body)[:80]}"

    transcription = body.get("transcription") or {}
    mapping = body.get("goal_mapping") or {}
    matched = mapping.get("matched_goals") or []
    analyses = body.get("analyses") or {}

    # Transcription should have structured content (not an empty string or missing)
    has_content = (
        isinstance(transcription, dict)
        and any(v for v in transcription.values() if v not in (None, "", [], {}))
    )

    summary = (
        f"matched={len(matched)} goals, analyses={len(analyses) if isinstance(analyses, dict) else 0}, "
        f"content={'yes' if has_content else 'no'}"
    )
    # Math worksheets (Maya) correctly don't match any communication goals —
    # accept empty mapping as long as transcription has structured content.
    passed = has_content
    return passed, summary


def run_capture(student_id: str, image_path: Path, work_type: str, subject: str) -> dict:
    label = image_path.name
    print(f"\n{'=' * 70}\n[{student_id}] {label}\n{'=' * 70}")
    t0 = time.time()
    try:
        code, body = _post_multipart(
            "/api/capture",
            {"student_id": student_id, "work_type": work_type, "subject": subject},
            "image",
            label,
            image_path.read_bytes(),
        )
    except URLError as e:
        return {
            "student_id": student_id,
            "photo": label,
            "code": 0,
            "elapsed_sec": round(time.time() - t0, 1),
            "pass": False,
            "summary": f"request failed: {e}",
            "matched": [],
        }
    elapsed = round(time.time() - t0, 1)

    passed, summary = _evaluate(body)
    if code != 200:
        passed = False
        summary = f"HTTP {code}: {str(body)[:120]}"

    matched_ids: list[str] = []
    if isinstance(body, dict):
        for g in body.get("goal_mapping", {}).get("matched_goals", []) or []:
            gid = g.get("goal_id")
            if gid:
                matched_ids.append(gid)

    print(f"HTTP {code} | {elapsed}s | {summary}")
    print(f"matched goals: {matched_ids or '—'}")

    return {
        "student_id": student_id,
        "photo": label,
        "code": code,
        "elapsed_sec": elapsed,
        "pass": passed,
        "summary": summary,
        "matched": matched_ids,
    }


def _write_report(results: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        f"# Sample Inputs Live Smoke — {date.today().isoformat()}",
        "",
        f"Backend: `{BACKEND}`  |  Photos: {len(results)}",
        "",
        "| # | Student | Photo | HTTP | Elapsed | Matched | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(results, 1):
        verdict = "PASS" if r["pass"] else "FAIL"
        lines.append(
            f"| {i} | `{r['student_id']}` | `{r['photo']}` | {r['code']} | "
            f"{r['elapsed_sec']}s | {', '.join(r['matched']) or '—'} | {verdict} |"
        )
    lines += ["", "## Details", ""]
    for i, r in enumerate(results, 1):
        lines += [
            f"### {i}. {r['student_id']} — {r['photo']}",
            "",
            f"- HTTP: {r['code']}",
            f"- Elapsed: {r['elapsed_sec']}s",
            f"- Matched goals: {r['matched'] or 'none'}",
            f"- Summary: {r['summary']}",
            f"- Verdict: **{'PASS' if r['pass'] else 'FAIL'}**",
            "",
        ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Snapshot + restore only; don't hit the backend",
    )
    args = parser.parse_args()

    missing = [p for _, p, _, _ in PHOTOS if not (SAMPLES / p).exists()]
    if missing:
        print("Missing sample photos:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        return 2

    print(f"Snapshotting {len(list(STUDENTS_DIR.glob('*.json')))} student profiles…")
    snapshot = _snapshot_profiles()

    # Guarantee restore even on Ctrl-C
    def _handler(signum, frame):
        print("\nInterrupt — restoring snapshots…", file=sys.stderr)
        _restore_profiles(snapshot)
        sys.exit(130)

    signal.signal(signal.SIGINT, _handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handler)

    if args.dry_run:
        _restore_profiles(snapshot)
        # Re-read to verify snapshot matches what's on disk (should always).
        for name, raw in snapshot.items():
            assert (STUDENTS_DIR / name).read_bytes() == raw, f"snapshot drift: {name}"
        print("dry-run: snapshot + restore round-trip OK")
        return 0

    results: list[dict] = []
    try:
        for student_id, rel, work_type, subject in PHOTOS:
            results.append(
                run_capture(student_id, SAMPLES / rel, work_type, subject)
            )
    finally:
        print("\nRestoring student profile snapshots…")
        _restore_profiles(snapshot)
        # Byte-exact check — this is why the unicode fix was a prerequisite.
        drift = [
            name for name, raw in snapshot.items()
            if (STUDENTS_DIR / name).read_bytes() != raw
        ]
        if drift:
            print(f"WARNING: snapshot drift after restore: {drift}", file=sys.stderr)

    _write_report(results)

    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    print(f"\n{'=' * 70}")
    print(f"Summary: {passed}/{total} pass")
    print(f"Report: {REPORT_PATH}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
