#!/usr/bin/env python3
"""
Generate precomputed podcast briefings for the 3 demo students.

Writes to data/precomputed/podcast_{student_id}.{json,mp3}. The demo page
loads these instantly — no live Gemma call, no live TTS synthesis.

Usage:
    python scripts/generate_podcast_cache.py              # all 3 demo students
    python scripts/generate_podcast_cache.py maya_2026    # single student
    python scripts/generate_podcast_cache.py --mock       # force mock client
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.sanitize import has_real_model_credentials
from core import tts_client
from core.json_io import write_json

DEMO_STUDENTS = ["maya_2026", "jaylen_2026", "amara_2026"]
PRECOMPUTED_DIR = PROJECT_ROOT / "data" / "precomputed"


def _get_producer(force_mock: bool):
    from agents.podcast_producer import PodcastProducer

    if force_mock or not has_real_model_credentials():
        from tests.mock_api_responses import MockGemmaClient
        print("[info] Using MockGemmaClient")
        return PodcastProducer(MockGemmaClient(), data_dir=str(PROJECT_ROOT / "data"))
    from core.gemma_client import GemmaClient
    print("[info] Using real GemmaClient (Google AI Studio)")
    return PodcastProducer(GemmaClient(), data_dir=str(PROJECT_ROOT / "data"))


def generate_one(student_id: str, producer) -> None:
    print(f"\n--- {student_id} ---")
    print("  Writing script...")
    result = producer.produce_script(student_id, language="en")

    script = result.get("script", [])
    print(f"  Script: {len(script)} lines")
    for i, line in enumerate(script[:3]):
        preview = (line.get("text") or "")[:80]
        print(f"    {i}. [{line.get('speaker')}] {preview}...")

    print("  Synthesizing MP3 (Edge TTS)...")
    mp3 = tts_client.synthesize_script(script, language="en")
    print(f"  MP3: {len(mp3)} bytes")

    PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)
    (PRECOMPUTED_DIR / f"podcast_{student_id}.mp3").write_bytes(mp3)
    write_json(PRECOMPUTED_DIR / f"podcast_{student_id}.json", result)
    print(f"  [ok] Written to data/precomputed/podcast_{student_id}.{{json,mp3}}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("student", nargs="?", help="Specific student_id, or omit for all demo students")
    ap.add_argument("--mock", action="store_true", help="Force mock Gemma client")
    args = ap.parse_args()

    producer = _get_producer(force_mock=args.mock)
    students = [args.student] if args.student else DEMO_STUDENTS

    for sid in students:
        try:
            generate_one(sid, producer)
        except Exception as exc:  # noqa: BLE001 — surface and continue
            print(f"  [fail] Failed: {exc}")

    print("\nDone.")


if __name__ == "__main__":
    main()
