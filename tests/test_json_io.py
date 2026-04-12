"""Round-trip tests for core.json_io.

Regression coverage for the Windows cp1252 mojibake bug described in
HANDOFF.md ("Pipeline-writeback gotcha"). The buggy path was:
  open(path, "r")  -> cp1252 on Windows -> decodes UTF-8 bytes as Latin-1
  open(path, "w")  -> cp1252 on Windows -> re-encodes mojibake back out
  json.dump(indent=2)  -> ensure_ascii=True by default -> \\uXXXX escapes

The fix centralizes read/write through core.json_io so every caller gets
UTF-8 + ensure_ascii=False + indent=2 for free. These tests lock the contract.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.json_io import read_json, write_json


UNICODE_SAMPLES = {
    "less_or_equal": "≤1 prompt per trip",
    "greater_or_equal": "≥80% target",
    "arrow": "first → then",
    "accented": "café — résumé",
    "emoji": "celebration 🌟",
    "mixed": "Maya scored ≤45% on G2 (baseline was ≈50%) 📉",
}


def test_round_trip_preserves_unicode_characters(tmp_path: Path) -> None:
    """Unicode characters survive a write -> read cycle unchanged."""
    target = tmp_path / "student.json"
    write_json(target, UNICODE_SAMPLES)
    restored = read_json(target)
    assert restored == UNICODE_SAMPLES


def test_round_trip_preserves_unicode_across_multiple_writes(tmp_path: Path) -> None:
    """Repeated read -> write cycles remain idempotent (no mojibake buildup)."""
    target = tmp_path / "student.json"
    write_json(target, UNICODE_SAMPLES)
    for _ in range(3):
        data = read_json(target)
        write_json(target, data)
    restored = read_json(target)
    assert restored == UNICODE_SAMPLES


def test_writes_literal_utf8_bytes_not_escape_sequences(tmp_path: Path) -> None:
    """ensure_ascii=False: file holds literal ≤ bytes, not \\u2264 escapes."""
    target = tmp_path / "student.json"
    write_json(target, {"note": "≤1 prompt"})
    raw = target.read_bytes()
    assert "≤".encode("utf-8") in raw
    assert b"\\u2264" not in raw


def test_writes_indented_two_space_json(tmp_path: Path) -> None:
    """indent=2 for human-friendly diffs."""
    target = tmp_path / "student.json"
    write_json(target, {"key": {"nested": "value"}})
    text = target.read_text(encoding="utf-8")
    assert '  "key":' in text
    assert '    "nested":' in text


def test_read_rejects_non_utf8_with_clear_error(tmp_path: Path) -> None:
    """If a caller hands us a cp1252 file, fail loudly instead of silently mojibaking."""
    target = tmp_path / "legacy.json"
    # Classic cp1252-encoded JSON containing a Windows-1252-only char (smart quote)
    target.write_bytes(b'{"note": "\x93smart quote\x94"}')
    with pytest.raises(UnicodeDecodeError):
        read_json(target)


def test_base_agent_writeback_is_byte_idempotent(tmp_path: Path) -> None:
    """BaseAgent._load_student_raw + _save_student_raw on unchanged data
    produces a byte-identical file. This is the specific failure mode
    flagged in HANDOFF.md "Pipeline-writeback gotcha" — an IEP Mapper
    writeback after a live /api/capture used to reformat inline objects
    and mojibake pre-existing unicode. Locking it here.
    """
    import shutil
    from agents.base import BaseAgent

    repo_root = Path(__file__).resolve().parent.parent
    source = repo_root / "data" / "students" / "marcus_2026.json"
    if not source.exists():
        pytest.skip("marcus_2026.json not present")

    students_dir = tmp_path / "students"
    students_dir.mkdir(parents=True)
    target = students_dir / "marcus_2026.json"
    shutil.copy2(source, target)

    before = target.read_bytes()
    agent = BaseAgent(client=None)
    data = agent._load_student_raw("marcus_2026", str(tmp_path))
    agent._save_student_raw("marcus_2026", data, str(tmp_path))
    after = target.read_bytes()

    assert before == after, (
        f"writeback drifted: {len(before)} -> {len(after)} bytes"
    )


def test_base_agent_writeback_preserves_existing_unicode_on_mutation(tmp_path: Path) -> None:
    """Append a new trial and verify pre-existing '≤' characters survive."""
    import shutil
    from agents.base import BaseAgent

    repo_root = Path(__file__).resolve().parent.parent
    source = repo_root / "data" / "students" / "marcus_2026.json"
    if not source.exists():
        pytest.skip("marcus_2026.json not present")

    students_dir = tmp_path / "students"
    students_dir.mkdir(parents=True)
    shutil.copy2(source, students_dir / "marcus_2026.json")

    agent = BaseAgent(client=None)
    data = agent._load_student_raw("marcus_2026", str(tmp_path))
    toileting = data["iep_goals"][1]
    toileting["trial_history"].append({
        "date": "2026-04-11",
        "trials": 5,
        "successes": 4,
        "pct": 80,
        "notes": "Test append ≤1 prompt",
    })
    agent._save_student_raw("marcus_2026", data, str(tmp_path))

    reread = agent._load_student_raw("marcus_2026", str(tmp_path))
    all_notes = " ".join(
        t.get("notes", "") for t in reread["iep_goals"][1]["trial_history"]
    )
    assert "≤" in all_notes
    assert "â‰¤" not in all_notes, "mojibake in writeback"


def test_marcus_profile_round_trips_without_mojibake() -> None:
    """Integration: the real marcus profile (contains '≤') survives a round-trip."""
    repo_root = Path(__file__).resolve().parent.parent
    source = repo_root / "data" / "students" / "marcus_2026.json"
    if not source.exists():
        pytest.skip("marcus_2026.json not present")
    data = read_json(source)

    def _find_note(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                hit = _find_note(v)
                if hit:
                    return hit
        elif isinstance(obj, list):
            for v in obj:
                hit = _find_note(v)
                if hit:
                    return hit
        elif isinstance(obj, str) and "≤" in obj:
            return obj
        return None

    note = _find_note(data)
    assert note is not None, "marcus profile should contain the '≤' canary character"
    assert "â‰¤" not in note, f"mojibake detected in marcus profile: {note!r}"
