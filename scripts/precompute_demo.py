#!/usr/bin/env python3
"""
Generate precomputed demo results for ClassLens ASD.

Runs the full pipeline against all sample work images using either:
  - Real Gemma 4 API (if GOOGLE_AI_STUDIO_KEY is set)
  - MockGemmaClient (fallback for offline generation)

Saves results to data/precomputed/ so the demo NEVER waits for API.

Usage:
    python scripts/precompute_demo.py          # uses mock if no API key
    python scripts/precompute_demo.py --mock    # force mock mode
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.mock_api_responses import MockGemmaClient
from core.pipeline import ClassLensPipeline

DATA_DIR = Path(__file__).parent.parent / "data"
SAMPLE_WORK = DATA_DIR / "sample_work"

# Map each sample image to its student + metadata
DEMO_ARTIFACTS = [
    {
        "student_id": "maya_2026",
        "image": "maya_math_worksheet.png",
        "work_type": "worksheet",
        "subject": "math",
        "date": "2026-04-03",
    },
    {
        "student_id": "maya_2026",
        "image": "maya_behavior_tally.png",
        "work_type": "tally_sheet",
        "subject": "communication",
        "date": "2026-04-03",
    },
    {
        "student_id": "jaylen_2026",
        "image": "jaylen_task_checklist.png",
        "work_type": "checklist",
        "subject": "daily_living",
        "date": "2026-04-03",
    },
    {
        "student_id": "sofia_2026",
        "image": "sofia_writing_sample.png",
        "work_type": "free_response",
        "subject": "writing",
        "date": "2026-04-03",
    },
]


def get_client(force_mock: bool):
    """Get API client — real if possible, mock as fallback."""
    if force_mock:
        print("Using MockGemmaClient (--mock flag)")
        return MockGemmaClient()

    import os
    from dotenv import load_dotenv
    load_dotenv()

    if os.getenv("GOOGLE_AI_STUDIO_KEY"):
        try:
            from core.gemma_client import GemmaClient
            client = GemmaClient()
            print("Using real Gemma 4 API")
            return client
        except Exception as e:
            print(f"API key found but client failed: {e}")
            print("Falling back to MockGemmaClient")
            return MockGemmaClient()
    else:
        print("No GOOGLE_AI_STUDIO_KEY — using MockGemmaClient")
        return MockGemmaClient()


def main():
    parser = argparse.ArgumentParser(description="Generate precomputed demo results")
    parser.add_argument("--mock", action="store_true", help="Force mock mode")
    args = parser.parse_args()

    client = get_client(args.mock)
    pipeline = ClassLensPipeline(client=client, data_dir=str(DATA_DIR))

    # Ensure precomputed dir exists
    precomputed_dir = DATA_DIR / "precomputed"
    precomputed_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {len(DEMO_ARTIFACTS)} precomputed results...")
    print("=" * 60)

    for artifact in DEMO_ARTIFACTS:
        image_path = str(SAMPLE_WORK / artifact["image"])
        print(f"\n  Processing: {artifact['image']}")
        print(f"    Student:  {artifact['student_id']}")
        print(f"    Type:     {artifact['work_type']}")

        try:
            result = pipeline.process_work_artifact(
                student_id=artifact["student_id"],
                image_path=image_path,
                work_type=artifact["work_type"],
                subject=artifact["subject"],
                date=artifact["date"],
            )

            # Pipeline caches automatically, but verify
            cache_key = Path(image_path).stem
            cache_path = precomputed_dir / f"{cache_key}.json"
            assert cache_path.exists(), f"Cache file not created: {cache_path}"

            # Print summary
            n_goals = len(result.get("goal_mapping", {}).get("matched_goals", []))
            n_analyses = len(result.get("analyses", []))
            n_alerts = len(result.get("alerts", []))
            print(f"    Result:   {n_goals} goals matched, {n_analyses} analyses, {n_alerts} alerts")
            print(f"    Cached:   {cache_path.name}")

        except Exception as e:
            print(f"    ERROR:    {e}")

    # Summary
    cached_files = list(precomputed_dir.glob("*.json"))
    print("\n" + "=" * 60)
    print(f"Done! {len(cached_files)} precomputed results in {precomputed_dir}")
    for f in sorted(cached_files):
        size = f.stat().st_size
        print(f"  {f.name} ({size:,} bytes)")


if __name__ == "__main__":
    main()
