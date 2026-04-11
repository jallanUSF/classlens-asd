"""
3-way A/B: Google AI Studio (gemma-4-31b-it) vs Ollama gemma4:e4b vs Ollama gemma4:26b

Measures on each provider:
  - #1 IEP PDF extraction — tool use + vision + nested structured output
  - #3 Alert analysis — thinking mode + reasoning depth
  - #5 Spanish parent comm — multilingual text generation + tool use
  - Chat latency — rough tok/s for streaming UX assessment
"""
import json
import sys
import textwrap
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


PROVIDERS = [
    ("google",          None,          "Google AI Studio / gemma-4-31b-it"),
    ("ollama",          "gemma4:e4b",  "Ollama / gemma4:e4b (fast)"),
    ("ollama",          "gemma4:26b",  "Ollama / gemma4:26b (full)"),
]

SEP = "=" * 78
SUB = "-" * 78


def make_client(provider, model):
    if model is None:
        return GemmaClient(provider=provider)
    return GemmaClient(provider=provider, model=model)


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
        return result, time.perf_counter() - t0, None
    except Exception as e:
        return None, time.perf_counter() - t0, f"{type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────────
def run_extraction(provider, model):
    pdf = Path("data/sample_iep/amara_iep_2025.pdf")
    if not pdf.exists():
        pdf = next(Path("data/sample_iep").glob("*.pdf"), None)
    if pdf is None:
        return None, 0, "no IEP PDFs found"
    try:
        client = make_client(provider, model)
        extractor = IEPExtractor(client)
        return timed(extractor.extract, str(pdf), max_pages=2)
    except Exception as e:
        return None, 0, f"client init: {type(e).__name__}: {e}"


def run_alert_analysis(provider, model, student_id, goal_id):
    try:
        client = make_client(provider, model)
        analyst = ProgressAnalyst(client)
        method = getattr(analyst, "analyze", None) or getattr(analyst, "analyze_goal", None)
        if method is None:
            return None, 0, "no analyze method"
        return timed(method, student_id, goal_id)
    except Exception as e:
        return None, 0, f"client init: {type(e).__name__}: {e}"


def run_spanish_comm(provider, model, student_id, goal_id):
    try:
        client = make_client(provider, model)
        forge = MaterialForge(client)
        return timed(forge.generate_parent_comm, student_id, goal_id, language="es")
    except Exception as e:
        return None, 0, f"client init: {type(e).__name__}: {e}"


def run_chat_latency(provider, model):
    """Measure tokens/sec on a short streaming request."""
    try:
        client = make_client(provider, model)
        prompt = "In one short sentence, say hello to a teacher."
        t0 = time.perf_counter()
        first_chunk_time = None
        char_count = 0
        for chunk in client.generate_stream(prompt):
            if first_chunk_time is None:
                first_chunk_time = time.perf_counter() - t0
            char_count += len(chunk)
        total = time.perf_counter() - t0
        return {
            "time_to_first_chunk": first_chunk_time,
            "total_time": total,
            "chars": char_count,
            "chars_per_sec": char_count / total if total > 0 else 0,
        }, total, None
    except Exception as e:
        return None, 0, f"{type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────────
def summarize_extraction(r):
    if not isinstance(r, dict):
        return "  (no result)"
    goals = r.get("iep_goals", [])
    accoms = r.get("accommodations", [])
    out = [
        f"  goals: {len(goals)}",
        f"  accommodations: {len(accoms)}",
        f"  student_name: {r.get('student_name') or '(empty)'}",
        f"  grade: {r.get('grade', '(empty)')}",
        f"  asd_level: {r.get('asd_level', '(empty)')}",
    ]
    if goals:
        first = goals[0]
        desc = (first.get("description", "") or "")[:110]
        out.append(f"  first goal: {first.get('goal_id', '?')} / {desc}...")
    return "\n".join(out)


def summarize_analysis(r):
    if not isinstance(r, dict):
        return f"  (got {type(r).__name__}: {str(r)[:200]})"
    thinking = r.get("thinking", "") or ""
    output = r.get("output", "") or r.get("progress_note", "") or ""
    return (
        f"  thinking chars: {len(thinking)}\n"
        f"  output chars:   {len(output)}\n"
        f"  output preview: {output[:200].strip()}..."
    )


def summarize_es(r):
    if not isinstance(r, dict):
        return "  (no result)"
    flat = json.dumps(r, ensure_ascii=False)
    markers = ["estimad", "querid", "gracias", "hijo", "hija", "familia", "aprend", "progres", "esta semana", "padres"]
    hits = sum(1 for m in markers if m in flat.lower())
    greeting = ""
    if isinstance(r.get("letter"), dict):
        greeting = r["letter"].get("greeting", "")
    elif isinstance(r.get("greeting"), str):
        greeting = r["greeting"]
    return (
        f"  spanish markers: {hits}/10\n"
        f"  greeting: {greeting[:120] or '(no greeting field)'}\n"
        f"  total chars: {len(flat)}"
    )


def summarize_latency(r, elapsed, err):
    if err:
        return f"  ERROR: {err[:200]}"
    if not isinstance(r, dict):
        return "  (no latency data)"
    return (
        f"  time to first chunk: {r['time_to_first_chunk']:.2f}s\n"
        f"  total stream time:   {r['total_time']:.2f}s\n"
        f"  chars streamed:      {r['chars']}\n"
        f"  chars/sec:           {r['chars_per_sec']:.1f}"
    )


# ─────────────────────────────────────────────────────────────
# Run all 3 providers
# ─────────────────────────────────────────────────────────────
all_results = {}

for provider, model, label in PROVIDERS:
    print("\n" + SEP)
    print(f"  {label}")
    print(SEP)
    results = {}

    print("\n[chat latency]")
    r, t, e = run_chat_latency(provider, model)
    results["latency"] = (r, t, e)
    print(summarize_latency(r, t, e))

    print("\n[#1 IEP extraction]")
    r, t, e = run_extraction(provider, model)
    results["extraction"] = (r, t, e)
    if e:
        print(f"  ERROR: {e[:300]}")
    else:
        print(f"  elapsed: {t:.1f}s")
        print(summarize_extraction(r))

    print("\n[#3 alert analysis  —  amara_2026 / G2]")
    r, t, e = run_alert_analysis(provider, model, "amara_2026", "G2")
    results["analysis"] = (r, t, e)
    if e:
        print(f"  ERROR: {e[:300]}")
    else:
        print(f"  elapsed: {t:.1f}s")
        print(summarize_analysis(r))

    print("\n[#5 Spanish parent comm  —  maya_2026 / G2]")
    r, t, e = run_spanish_comm(provider, model, "maya_2026", "G2")
    results["spanish"] = (r, t, e)
    if e:
        print(f"  ERROR: {e[:300]}")
    else:
        print(f"  elapsed: {t:.1f}s")
        print(summarize_es(r))

    all_results[label] = results


# ─────────────────────────────────────────────────────────────
# Compact side-by-side summary
# ─────────────────────────────────────────────────────────────
print("\n\n" + SEP)
print("  SIDE-BY-SIDE SUMMARY")
print(SEP)

headers = [lbl for _, _, lbl in PROVIDERS]
print(f"\n{'metric':<30}" + "".join(f"{h[:24]:<26}" for h in headers))
print("-" * (30 + 26 * len(headers)))


def cell(provider_label, key, accessor):
    r, t, e = all_results[provider_label].get(key, (None, 0, "missing"))
    if e:
        return "ERR"
    try:
        return accessor(r, t)
    except Exception:
        return "?"


rows = [
    ("latency: first chunk (s)", "latency", lambda r, t: f"{r['time_to_first_chunk']:.2f}"),
    ("latency: chars/sec",       "latency", lambda r, t: f"{r['chars_per_sec']:.1f}"),
    ("#1 goals extracted",       "extraction", lambda r, t: str(len(r.get('iep_goals', [])))),
    ("#1 accommodations",        "extraction", lambda r, t: str(len(r.get('accommodations', [])))),
    ("#1 demographics filled",   "extraction", lambda r, t: "y" if r.get("student_name") else "n"),
    ("#1 elapsed (s)",           "extraction", lambda r, t: f"{t:.1f}"),
    ("#3 thinking chars",        "analysis", lambda r, t: str(len(r.get('thinking', '') or ''))),
    ("#3 output chars",          "analysis", lambda r, t: str(len(r.get('output', '') or r.get('progress_note', '') or ''))),
    ("#3 elapsed (s)",           "analysis", lambda r, t: f"{t:.1f}"),
    ("#5 spanish markers /10",   "spanish", lambda r, t: str(sum(1 for m in ['estimad','querid','gracias','hijo','hija','familia','aprend','progres','esta semana','padres'] if m in json.dumps(r, ensure_ascii=False).lower()))),
    ("#5 elapsed (s)",           "spanish", lambda r, t: f"{t:.1f}"),
]

for name, key, accessor in rows:
    print(f"{name:<30}" + "".join(f"{cell(h, key, accessor):<26}" for h in headers))

print("\n" + SEP)
print("  A/B complete")
print(SEP)
