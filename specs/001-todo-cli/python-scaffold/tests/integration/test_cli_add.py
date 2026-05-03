"""T012 — `cli add` 통합 테스트."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli.main import main


def _db(tmp_path: Path) -> str:
    return str(tmp_path / "todo.json")


def test_add_normal_creates_item_and_prints_id(tmp_path, capsys):
    rc = main(["--db", _db(tmp_path), "add", "보고서 작성"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Created ID 1" in captured.out

    payload = json.loads(Path(_db(tmp_path)).read_text(encoding="utf-8"))
    assert payload[0]["title"] == "보고서 작성"


def test_add_with_due_and_priority(tmp_path, capsys):
    rc = main(
        [
            "--db",
            _db(tmp_path),
            "add",
            "발표",
            "--due",
            "2026-06-01",
            "--priority",
            "high",
        ]
    )
    assert rc == 0

    payload = json.loads(Path(_db(tmp_path)).read_text(encoding="utf-8"))
    assert payload[0]["priority"] == "high"
    assert payload[0]["due_date"].startswith("2026-06-01")


def test_add_empty_title_returns_error(tmp_path, capsys):
    rc = main(["--db", _db(tmp_path), "add", ""])
    captured = capsys.readouterr()
    assert rc != 0
    assert "title" in captured.err.lower() or "비어" in captured.err


def test_add_invalid_priority_rejected_by_argparse(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["--db", _db(tmp_path), "add", "x", "--priority", "urgent"])
    assert exc.value.code != 0
