"""
Cold-boot smoke test — hits the live backend end-to-end without mocks.

Run against a freshly-started uvicorn instance. Verifies:
  1. /health responds
  2. /api/students returns profiles
  3. /api/chat returns a real response (mock or live based on env)
  4. /api/capture with a valid image returns precomputed pipeline result
  5. /api/capture rejects bad extensions, bad student_ids, oversize files
"""

from __future__ import annotations

import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

BASE = "http://127.0.0.1:8001"
ROOT = Path(__file__).resolve().parent.parent
SAMPLE_IMG = ROOT / "data" / "sample_work" / "maya_math_worksheet.png"

PASS = "PASS"
FAIL = "FAIL"


def _get(path: str) -> tuple[int, dict | list | str]:
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=15) as r:
            body = r.read().decode()
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _post_json(path: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _post_multipart(path: str, fields: dict[str, str], file_field: str,
                    file_name: str, file_bytes: bytes, file_type: str | None = None) -> tuple[int, dict | str]:
    boundary = "----ClassLensBoundary7f8a9c"
    lines = []
    for k, v in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{k}"'.encode())
        lines.append(b"")
        lines.append(str(v).encode())
    lines.append(f"--{boundary}".encode())
    mime = file_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    lines.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"'.encode()
    )
    lines.append(f"Content-Type: {mime}".encode())
    lines.append(b"")
    lines.append(file_bytes)
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, "<non-json error>"


def main() -> int:
    results: list[tuple[str, str, str]] = []  # (name, verdict, note)

    # 1. Health
    code, body = _get("/health")
    results.append((
        "health",
        PASS if code == 200 and isinstance(body, dict) and body.get("status") == "ok" else FAIL,
        f"{code} {body}",
    ))

    # 2. Students list
    code, body = _get("/api/students")
    n = len(body) if isinstance(body, list) else 0
    results.append((
        "students list",
        PASS if code == 200 and n >= 3 else FAIL,
        f"{code} count={n}",
    ))

    # 3. Chat — real API if key present, else mock. Keep prompt tiny to cap cost.
    code, body = _post_json("/api/chat", {
        "student_id": "maya_2026",
        "message": "In one sentence, name Maya's top IEP goal.",
        "conversation_history": [],
    })
    has_text = isinstance(body, dict) and len(body.get("content", "")) > 10
    results.append((
        "chat (Maya)",
        PASS if code == 200 and has_text else FAIL,
        f"{code} content_len={len(body.get('content','')) if isinstance(body, dict) else 0}",
    ))

    # 4. Capture — valid PNG, precomputed path
    if not SAMPLE_IMG.exists():
        results.append(("capture happy path", FAIL, "sample image missing"))
    else:
        img_bytes = SAMPLE_IMG.read_bytes()
        code, body = _post_multipart(
            "/api/capture",
            {"student_id": "maya_2026", "work_type": "worksheet", "subject": "math"},
            "image",
            "maya_math_worksheet.png",
            img_bytes,
        )
        has_matched = (
            isinstance(body, dict)
            and body.get("goal_mapping", {}).get("matched_goals")
        )
        results.append((
            "capture happy path",
            PASS if code == 200 and has_matched else FAIL,
            f"{code} matched={len(body.get('goal_mapping',{}).get('matched_goals',[])) if isinstance(body,dict) else 0}",
        ))

    # 4b. Capture — one of the newly-added precomputed entries
    new_img = ROOT / "data" / "sample_work" / "jaylen_choice_board.png"
    if not new_img.exists():
        results.append(("capture new cache entry", FAIL, "jaylen_choice_board.png missing"))
    else:
        img_bytes = new_img.read_bytes()
        code, body = _post_multipart(
            "/api/capture",
            {"student_id": "jaylen_2026", "work_type": "log", "subject": "communication"},
            "image",
            "jaylen_choice_board.png",
            img_bytes,
        )
        goals = (
            body.get("goal_mapping", {}).get("matched_goals", [])
            if isinstance(body, dict) else []
        )
        hit_g1 = any(g.get("goal_id") == "G1" for g in goals)
        results.append((
            "capture new cache entry",
            PASS if code == 200 and hit_g1 else FAIL,
            f"{code} goals={[g.get('goal_id') for g in goals]}",
        ))

    # 5. Capture rejects bad extension
    code, body = _post_multipart(
        "/api/capture",
        {"student_id": "maya_2026"},
        "image",
        "payload.exe",
        b"MZ" + b"\x00" * 50,
        file_type="application/octet-stream",
    )
    results.append((
        "reject .exe",
        PASS if code == 400 else FAIL,
        f"{code} {body if isinstance(body, dict) else str(body)[:80]}",
    ))

    # 6. Capture rejects path-traversal student_id
    code, body = _post_multipart(
        "/api/capture",
        {"student_id": "../etc"},
        "image",
        "ok.png",
        b"\x89PNG\r\n" + b"0" * 50,
    )
    results.append((
        "reject bad student_id",
        PASS if code == 400 else FAIL,
        f"{code} {body if isinstance(body, dict) else str(body)[:80]}",
    ))

    # 7. Capture rejects oversize
    big = b"\x89PNG\r\n" + b"0" * (11 * 1024 * 1024)
    code, body = _post_multipart(
        "/api/capture",
        {"student_id": "maya_2026"},
        "image",
        "big.png",
        big,
    )
    results.append((
        "reject >10MB",
        PASS if code == 413 else FAIL,
        f"{code}",
    ))

    # Print table
    width = max(len(n) for n, _, _ in results)
    print(f"\n{'Check':<{width}}  Verdict  Notes")
    print("-" * (width + 30))
    for name, verdict, note in results:
        print(f"{name:<{width}}  {verdict:<7}  {note}")

    failed = sum(1 for _, v, _ in results if v == FAIL)
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
