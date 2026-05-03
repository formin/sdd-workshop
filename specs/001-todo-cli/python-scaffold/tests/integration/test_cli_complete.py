"""T016 — `cli complete` 통합 테스트."""

from __future__ import annotations

import json
from pathlib import Path

from cli.main import main


def _db(tmp_path: Path) -> str:
    return str(tmp_path / "todo.json")


def test_complete_marks_item_done(tmp_path, capsys):
    db = _db(tmp_path)
    main(["--db", db, "add", "A"])
    capsys.readouterr()

    rc = main(["--db", db, "complete", "1"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Marked 1" in out

    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert payload[0]["completed"] is True


def test_complete_nonexistent_id_emits_error(tmp_path, capsys):
    db = _db(tmp_path)
    main(["--db", db, "add", "A"])
    capsys.readouterr()

    rc = main(["--db", db, "complete", "999"])
    captured = capsys.readouterr()
    assert rc != 0
    assert "999" in captured.err
