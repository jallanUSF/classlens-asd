"""
Clean-slate solo test of Ollama gemma4:e4b on this machine.
Compare directly to the Google numbers from the earlier A/B.
"""
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from core.gemma_client import GemmaClient
from agents.iep_extractor import IEPExtractor
from agents.progress_analyst import ProgressAnalyst
from agents.material_forge import MaterialForge

PROVIDER = "ollama"
MODEL = "gemma4:e4b"
SEP = "=" * 78


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    try:
        return fn(*args, **kwargs), time.perf_counter() - t0, None
    except Exception as e:
        return None, time.perf_counter() - t0, f"{type(e).__name__}: {e}"


def new_client():
    return GemmaClient(provider=PROVIDER, model=MODEL)


print(SEP)
print(f"  Ollama / {MODEL}  —  SOLO (no contention)")
print(SEP)

# ─── Chat streaming latency ───────────────────────────────────────
print("\n[chat latency]", flush=True)
try:
    client = new_client()
    prompt = "In one short sentence, say hello to a teacher."
    t0 = time.perf_counter()
    first = None
    chars = 0
    for chunk in client.generate_stream(prompt):
        if first is None:
            first = time.perf_counter() - t0
        chars += len(chunk)
    total = time.perf_counter() - t0
    print(f"  time to first chunk: {first:.2f}s", flush=True)
    print(f"  total stream time:   {total:.2f}s", flush=True)
    print(f"  chars streamed:      {chars}", flush=True)
    print(f"  chars/sec:           {chars/total:.1f}", flush=True)
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}", flush=True)

# ─── #1 IEP extraction ─────────────────────────────────────────────
print("\n[#1 IEP extraction  —  amara_iep_2025.pdf]", flush=True)
try:
    pdf = next(Path("data/sample_iep").glob("*.pdf"))
    client = new_client()
    extractor = IEPExtractor(client)
    r, t, e = timed(extractor.extract, str(pdf), max_pages=2)
    print(f"  elapsed: {t:.1f}s", flush=True)
    if e:
        print(f"  ERROR: {e}", flush=True)
    elif r:
        goals = r.get("iep_goals", [])
        accoms = r.get("accommodations", [])
        print(f"  goals: {len(goals)}", flush=True)
        print(f"  accommodations: {len(accoms)}", flush=True)
        print(f"  student_name: {r.get('student_name') or '(empty)'}", flush=True)
        print(f"  grade: {r.get('grade', '(empty)')}", flush=True)
        print(f"  asd_level: {r.get('asd_level', '(empty)')}", flush=True)
        if goals:
            print(f"  first goal: {goals[0].get('goal_id', '?')} / {(goals[0].get('description','') or '')[:100]}...", flush=True)
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

# ─── #3 Alert analysis ─────────────────────────────────────────────
print("\n[#3 alert analysis  —  amara_2026 / G2]", flush=True)
try:
    client = new_client()
    analyst = ProgressAnalyst(client)
    method = getattr(analyst, "analyze", None) or getattr(analyst, "analyze_goal", None)
    r, t, e = timed(method, "amara_2026", "G2")
    print(f"  elapsed: {t:.1f}s", flush=True)
    if e:
        print(f"  ERROR: {e}", flush=True)
    elif isinstance(r, dict):
        thinking = r.get("thinking", "") or ""
        output = r.get("output", "") or r.get("progress_note", "") or ""
        print(f"  thinking chars: {len(thinking)}", flush=True)
        print(f"  output chars:   {len(output)}", flush=True)
        print(f"  output preview: {output[:250].strip()}...", flush=True)
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

# ─── #5 Spanish parent comm ────────────────────────────────────────
print("\n[#5 Spanish parent comm  —  maya_2026 / G2]", flush=True)
try:
    client = new_client()
    forge = MaterialForge(client)
    r, t, e = timed(forge.generate_parent_comm, "maya_2026", "G2", language="es")
    print(f"  elapsed: {t:.1f}s", flush=True)
    if e:
        print(f"  ERROR: {e}", flush=True)
    elif isinstance(r, dict):
        flat = json.dumps(r, ensure_ascii=False)
        markers = ["estimad","querid","gracias","hijo","hija","familia","aprend","progres","esta semana","padres"]
        hits = sum(1 for m in markers if m in flat.lower())
        greeting = ""
        if isinstance(r.get("letter"), dict):
            greeting = r["letter"].get("greeting", "")
        elif isinstance(r.get("greeting"), str):
            greeting = r["greeting"]
        print(f"  spanish markers: {hits}/10", flush=True)
        print(f"  greeting: {greeting[:120] or '(no greeting field)'}", flush=True)
        print(f"  total chars: {len(flat)}", flush=True)
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()

print("\n" + SEP)
print("  e4b solo complete")
print(SEP)
