"""
Inline smoke test for the 4 new judge-appeal features.
Runs against real Gemma via OpenRouter through TestClient.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []

def check(name, cond, detail=""):
    tag = PASS if cond else FAIL
    results.append((tag, name, detail))
    print(f"{tag} {name}" + (f" — {detail}" if detail else ""))

print("=" * 70)
print("FEATURE SMOKE — 4 new judge-appeal features, live Gemma")
print("=" * 70)

# ─────────────────────────────────────────────────────────────
# #2 Chat SSE streaming
# ─────────────────────────────────────────────────────────────
print("\n#2 Chat SSE streaming")
try:
    with client.stream(
        "POST",
        "/api/chat/stream",
        json={"message": "Say hello in one short sentence.", "student_id": None, "conversation_history": []},
    ) as resp:
        ctype = resp.headers.get("content-type", "")
        check("content-type is text/event-stream", "text/event-stream" in ctype, ctype)
        frames = []
        for line in resp.iter_lines():
            if line.startswith("data: "):
                frames.append(line[6:])
        delta_frames = [f for f in frames if '"delta"' in f]
        done_frames = [f for f in frames if '"done"' in f]
        check("received >=1 delta frame", len(delta_frames) >= 1, f"{len(delta_frames)} deltas")
        check("received terminal done frame", len(done_frames) >= 1)
        accumulated = ""
        for f in delta_frames:
            try:
                accumulated += json.loads(f).get("delta", "")
            except Exception:
                pass
        check("accumulated content non-empty", len(accumulated.strip()) > 0, f"len={len(accumulated)}")
except Exception as e:
    check("streaming endpoint reachable", False, str(e)[:100])

# ─────────────────────────────────────────────────────────────
# #3 Thinking-trace alert analysis
# ─────────────────────────────────────────────────────────────
print("\n#3 Thinking-trace alert analysis")
try:
    alerts_resp = client.get("/api/alerts")
    check("GET /api/alerts succeeds", alerts_resp.status_code == 200)
    alerts = alerts_resp.json()
    check("have >=1 alert to analyze", len(alerts) >= 1, f"{len(alerts)} alerts")
    if alerts:
        aid = alerts[0]["id"]
        analyze = client.post(f"/api/alerts/{aid}/analyze")
        check("POST /api/alerts/{id}/analyze succeeds", analyze.status_code == 200, f"code={analyze.status_code}")
        if analyze.status_code == 200:
            data = analyze.json()
            check("response has 'output' key", "output" in data)
            check("output is non-empty", len(data.get("output", "").strip()) > 0, f"len={len(data.get('output',''))}")
            check("response has 'thinking' key", "thinking" in data)
            # thinking is populated on MODEL_PROVIDER=google (native ThinkingConfig)
            # and empty on openrouter/ollama (no code path in gemma_client.py yet)
            print(f"       (thinking len={len(data.get('thinking','') or '')}, non-empty on google, empty on openrouter/ollama)")
            print(f"       output preview: {data.get('output','')[:120]}...")
except Exception as e:
    check("thinking-trace reachable", False, str(e)[:100])

# ─────────────────────────────────────────────────────────────
# #5 Bilingual parent communication (Spanish)
# ─────────────────────────────────────────────────────────────
print("\n#5 Bilingual parent communication")
try:
    resp = client.post(
        "/api/materials/generate",
        json={"student_id": "maya_2026", "goal_id": "G2", "material_type": "parent_comm", "language": "es"},
    )
    check("POST materials/generate (es) succeeds", resp.status_code == 200, f"code={resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        check("record has language='es'", data.get("language") == "es", str(data.get("language")))
        content = data.get("content", {})
        body_text = json.dumps(content, ensure_ascii=False).lower()
        # Spanish indicators: common short words that should appear in a Spanish letter
        spanish_markers = ["estimad", "querid", "saludo", "gracias", "hijo", "hija", "familia", "aprend", "progres", "esta semana", "esta", "del "]
        hits = sum(1 for m in spanish_markers if m in body_text)
        check(
            "content reads as Spanish (>=2 markers)",
            hits >= 2,
            f"{hits} markers found, preview: {body_text[:200]}"
        )
except Exception as e:
    check("bilingual endpoint reachable", False, str(e)[:100])

# ─────────────────────────────────────────────────────────────
# #1 IEP PDF extraction
# ─────────────────────────────────────────────────────────────
print("\n#1 IEP PDF extraction")
try:
    iep_dir = Path("data/sample_iep")
    pdfs = list(iep_dir.glob("*.pdf"))
    check("mock IEP PDFs exist", len(pdfs) >= 1, f"{len(pdfs)} PDFs found")
    if pdfs:
        pdf_path = pdfs[0]
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            data = {"student_id": "test_smoke", "doc_type": "iep_pdf"}
            resp = client.post("/api/documents/upload", files=files, data=data)
        check("POST documents/upload succeeds", resp.status_code == 200, f"code={resp.status_code}")
        if resp.status_code == 200:
            body = resp.json()
            check("response has 'extraction' key", "extraction" in body)
            extraction = body.get("extraction", {})
            goals = extraction.get("iep_goals", [])
            accoms = extraction.get("accommodations", [])
            check(
                "extraction returned goals OR notes (not silent-empty)",
                len(goals) > 0 or len(accoms) > 0 or "notes" in extraction,
                f"goals={len(goals)} accoms={len(accoms)} notes={'yes' if 'notes' in extraction else 'no'}"
            )
            if goals:
                print(f"       first goal: {json.dumps(goals[0], ensure_ascii=False)[:200]}")
            if "notes" in extraction:
                print(f"       notes: {extraction['notes'][:200]}")
except Exception as e:
    check("IEP upload reachable", False, str(e)[:100])

# ─────────────────────────────────────────────────────────────
# #4 First-Then material type
# ─────────────────────────────────────────────────────────────
print("\n#4 First-Then board")
try:
    resp = client.post(
        "/api/materials/generate",
        json={"student_id": "maya_2026", "goal_id": "G1", "material_type": "first_then"},
    )
    check("POST materials/generate (first_then) succeeds", resp.status_code == 200, f"code={resp.status_code}")
    if resp.status_code == 200:
        content = resp.json().get("content", "")
        check("first_then content non-empty", len(str(content)) > 0, f"len={len(str(content))}")
except Exception as e:
    check("first_then reachable", False, str(e)[:100])

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
print(f"SUMMARY: {passed} passed, {failed} failed")
print("=" * 70)
if failed:
    print("\nFailures:")
    for tag, name, detail in results:
        if tag == FAIL:
            print(f"  - {name}: {detail}")
sys.exit(0 if failed == 0 else 1)
