"""
Browser-path smoke test — drives the real Next.js frontend via Playwright so
it catches proxy / SSE / client-render regressions that TestClient-based tests
cannot (see MISTAKES.md #5).

Preconditions:
    1. Backend on http://127.0.0.1:8001  (python -m uvicorn backend.main:app --port 8001)
    2. Frontend on http://localhost:3000 (cd frontend && npm run dev)
    3. playwright installed:  pip install playwright && playwright install chromium

Usage:
    python scripts/browser_smoke.py                 # all 3 core students
    python scripts/browser_smoke.py maya_2026       # single student
    python scripts/browser_smoke.py --headed        # show browser window

Exits 0 on all-pass, 1 on any failure. Designed for CI + pre-demo sanity.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

FRONTEND = "http://localhost:3000"
DEFAULT_STUDENTS = ["maya_2026", "jaylen_2026", "amara_2026"]

# Regexes allow transient dev-server noise we deliberately ignore.
CONSOLE_IGNORES = (
    "Download the React DevTools",
    "[Fast Refresh]",
    "[HMR]",
)


@dataclass
class StudentResult:
    student_id: str
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, ok, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.checks)


def _filter_console(messages) -> list[str]:
    noisy = []
    for m in messages:
        text = m.text if hasattr(m, "text") else str(m)
        if m.type not in {"error", "warning"}:
            continue
        if any(ig in text for ig in CONSOLE_IGNORES):
            continue
        noisy.append(f"[{m.type}] {text}")
    return noisy


def check_student(page, student_id: str) -> StudentResult:
    result = StudentResult(student_id)
    console_msgs = []
    page.on("console", lambda msg: console_msgs.append(msg))

    # 1. Page loads
    resp = page.goto(f"{FRONTEND}/student/{student_id}", wait_until="domcontentloaded", timeout=20_000)
    result.add("page_load", resp is not None and resp.ok, f"status={resp.status if resp else 'none'}")

    # 2. Student name renders (hydration)
    try:
        page.wait_for_selector("h1, h2", timeout=10_000)
        result.add("heading_rendered", True)
    except Exception as exc:
        result.add("heading_rendered", False, str(exc))

    # 3. Trajectory section present
    try:
        page.get_by_text("Trajectory", exact=False).first.wait_for(timeout=10_000)
        result.add("trajectory_section", True)
    except Exception as exc:
        result.add("trajectory_section", False, str(exc))

    # 4. Progress Briefing podcast section present
    try:
        page.get_by_text("Progress Briefing", exact=False).first.wait_for(timeout=10_000)
        result.add("podcast_section", True)
    except Exception as exc:
        result.add("podcast_section", False, str(exc))

    # 5. Materials / confidence surface
    try:
        page.get_by_text("Materials", exact=False).first.wait_for(timeout=10_000)
        result.add("materials_section", True)
    except Exception as exc:
        result.add("materials_section", False, str(exc))

    # 6. No unexpected console errors
    noisy = _filter_console(console_msgs)
    result.add("console_clean", not noisy, "; ".join(noisy[:3]))

    page.remove_listener("console", lambda msg: console_msgs.append(msg))  # best-effort
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("student", nargs="?", help="single student id, or omit for defaults")
    ap.add_argument("--headed", action="store_true", help="show browser window")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[fail] playwright not installed. Run: pip install playwright && playwright install chromium")
        return 1

    students = [args.student] if args.student else DEFAULT_STUDENTS
    all_results: list[StudentResult] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context()
        page = context.new_page()

        for sid in students:
            print(f"\n--- {sid} ---")
            try:
                res = check_student(page, sid)
            except Exception as exc:
                res = StudentResult(sid)
                res.add("exception", False, str(exc))
            all_results.append(res)
            for name, ok, detail in res.checks:
                tag = "PASS" if ok else "FAIL"
                suffix = f"  ({detail})" if detail and not ok else ""
                print(f"  [{tag}] {name}{suffix}")

        browser.close()

    total = sum(len(r.checks) for r in all_results)
    passed = sum(1 for r in all_results for _, ok, _ in r.checks if ok)
    failed_students = [r.student_id for r in all_results if not r.passed]

    print(f"\n{passed}/{total} checks passed across {len(all_results)} students")
    if failed_students:
        print(f"Failed: {', '.join(failed_students)}")
        return 1
    print("All browser-path smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
