"""One-shot normalizer for data/students/*.json.

Reads every student profile with core.json_io (UTF-8) and writes it back
in the canonical format (UTF-8, ensure_ascii=False, indent=2). The effect
is cosmetic unless a file already contains mojibake, in which case the
read step fails loudly.

Run once after shipping core/json_io to eliminate diff noise from
IEP Mapper writebacks (inline baseline objects expand to multi-line on
json.dump re-serialization, so the source files must already match).

Usage:
    python scripts/normalize_student_profiles.py
    python scripts/normalize_student_profiles.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Repo root on sys.path so `core.json_io` resolves when run as a script.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.json_io import read_json, write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which files would change, don't write",
    )
    args = parser.parse_args()

    students_dir = REPO_ROOT / "data" / "students"
    if not students_dir.exists():
        print(f"no students dir at {students_dir}", file=sys.stderr)
        return 1

    changed = 0
    skipped = 0
    for path in sorted(students_dir.glob("*.json")):
        before = path.read_bytes()
        data = read_json(path)
        # Write to a temp path so we can compare without touching the original
        # in --dry-run mode.
        tmp = path.with_suffix(".json.normalized")
        write_json(tmp, data)
        after = tmp.read_bytes()

        if before == after:
            tmp.unlink()
            print(f"  ok    {path.name}")
            skipped += 1
            continue

        if args.dry_run:
            tmp.unlink()
            print(f"  WOULD {path.name}  ({len(before)} -> {len(after)} bytes)")
        else:
            tmp.replace(path)
            print(f"  fixed {path.name}  ({len(before)} -> {len(after)} bytes)")
        changed += 1

    print()
    print(f"normalized: {changed}, unchanged: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
