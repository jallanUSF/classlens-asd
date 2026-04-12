"""Post-capture verification: materials generation, alerts, and profile integrity.

Runs after sample_inputs_smoke.py to verify:
1. Alerts recalculate correctly from student data
2. Materials generate for each student with matched goals
3. Admin report generates for a student
4. Bilingual translate preserves content
5. Student profiles are intact (no mojibake)

Requires backend running on http://localhost:8001.
"""
import io, json, sys, time, requests

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8001/api"
PASS, FAIL = 0, 0

def check(name, ok, detail=""):
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    PASS += ok; FAIL += (not ok)
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 70)
print("POST-CAPTURE VERIFICATION")
print("=" * 70)

# 1. ALERTS — recalculate from current data
print("\n--- 1. ALERTS RECALCULATION ---")
r = requests.get(f"{BASE}/alerts", timeout=30)
check("alerts endpoint returns 200", r.status_code == 200)
alerts = r.json()
check(f"alerts count >= 4", len(alerts) >= 4, f"got {len(alerts)}")
# Check all alerts have required fields
for a in alerts:
    has_fields = all(k in a for k in ("id", "student_id", "severity", "title", "label"))
    if not has_fields:
        check(f"alert {a.get('id','?')} has required fields", False, str(a.keys()))
        break
else:
    check("all alerts have required fields", True)
# Check severity populated (Finding 8 regression check)
empty_sev = [a for a in alerts if not a.get("severity")]
check("all alerts have severity", len(empty_sev) == 0, f"{len(empty_sev)} missing")

# 2. MATERIALS GENERATION — lesson plan for Maya G1
print("\n--- 2. MATERIALS GENERATION ---")
t0 = time.time()
r = requests.post(f"{BASE}/materials/generate", json={
    "student_id": "maya_2026", "goal_id": "G1",
    "material_type": "lesson_plan"
}, timeout=180)
elapsed = round(time.time() - t0, 1)
check(f"lesson plan generates (maya G1)", r.status_code == 200, f"{elapsed}s")
if r.status_code == 200:
    content = r.json().get("content", {})
    check("lesson plan has content", bool(content))

# 3. PARENT COMM — EN generation
print("\n--- 3. PARENT LETTER (EN) ---")
t0 = time.time()
r = requests.post(f"{BASE}/materials/generate", json={
    "student_id": "amara_2026", "goal_id": "G2",
    "material_type": "parent_comm", "language": "en"
}, timeout=180)
elapsed = round(time.time() - t0, 1)
check(f"EN parent letter generates (amara G2)", r.status_code == 200, f"{elapsed}s")
en_content = {}
en_text = ""
if r.status_code == 200:
    en_content = r.json().get("content", {})
    # Extract text for translation test
    if isinstance(en_content, dict):
        en_text = en_content.get("text", "")
        if not en_text:
            parts = []
            if en_content.get("greeting"): parts.append(en_content["greeting"])
            if en_content.get("highlights"): parts.append("\n".join(en_content["highlights"]))
            if en_content.get("closing"): parts.append(en_content["closing"])
            if en_content.get("teacher_name"): parts.append(en_content["teacher_name"])
            en_text = "\n\n".join(parts)
    check("EN letter has content", len(en_text) > 50, f"{len(en_text)} chars")

# 4. BILINGUAL TRANSLATE — EN→ES with approved content
print("\n--- 4. BILINGUAL TRANSLATE (EN→ES) ---")
if en_text:
    t0 = time.time()
    r = requests.post(f"{BASE}/materials/generate", json={
        "student_id": "amara_2026", "goal_id": "G2",
        "material_type": "parent_comm", "language": "es",
        "approved_content": en_text,
    }, timeout=180)
    elapsed = round(time.time() - t0, 1)
    check(f"ES translate completes", r.status_code == 200, f"{elapsed}s")
    if r.status_code == 200:
        es_content = r.json().get("content", {})
        es_text = es_content.get("text", "") if isinstance(es_content, dict) else ""
        check("ES has content", len(es_text) > 50, f"{len(es_text)} chars")
        check("ES language field set", r.json().get("language") == "es")
        # Verify student name preserved in translation
        check("student name preserved in ES", "Amara" in es_text or "amara" in es_text.lower())
else:
    check("skipped ES translate (no EN content)", False)

# 5. ADMIN REPORT
print("\n--- 5. ADMIN REPORT ---")
t0 = time.time()
r = requests.post(f"{BASE}/materials/generate", json={
    "student_id": "ethan_2026", "goal_id": "",
    "material_type": "admin_report"
}, timeout=180)
elapsed = round(time.time() - t0, 1)
check(f"admin report generates (ethan)", r.status_code == 200, f"{elapsed}s")
if r.status_code == 200:
    content = r.json().get("content", {})
    check("admin report has content", bool(content))

# 6. STUDENT PROFILE INTEGRITY — check for mojibake
print("\n--- 6. PROFILE INTEGRITY ---")
from pathlib import Path
students_dir = Path("data/students")
for p in sorted(students_dir.glob("*.json")):
    raw = p.read_bytes()
    try:
        text = raw.decode("utf-8")
        has_mojibake = "\u00e2" in text or "â‰" in text
        check(f"{p.name} UTF-8 clean", not has_mojibake,
              "mojibake detected!" if has_mojibake else f"{len(raw)} bytes")
    except UnicodeDecodeError as e:
        check(f"{p.name} UTF-8 valid", False, str(e))

# 7. MATERIALS LIST — verify saved files can be read back
print("\n--- 7. SAVED MATERIALS READBACK ---")
for sid in ["maya_2026", "amara_2026", "ethan_2026"]:
    r = requests.get(f"{BASE}/students/{sid}/materials", timeout=30)
    check(f"{sid} materials list", r.status_code == 200, f"count={len(r.json())}")

print(f"\n{'=' * 70}")
print(f"TOTAL: {PASS + FAIL} checks | PASS: {PASS} | FAIL: {FAIL}")
print(f"{'=' * 70}")
sys.exit(0 if FAIL == 0 else 1)
