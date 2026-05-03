"""T018 — `cli delete` 통합 테스트."""

from __future__ import annotations

import json
from pathlib import Path

from cli.main import main


def _db(tmp_path: Path) -> str:
    return str(tmp_path / "todo.json")


def test_delete_removes_item(tmp_path, capsys):
    db = _db(tmp_path)
    main(["--db", db, "add", "A"])
    main(["--db", db, "add", "B"])
    capsys.readouterr()

    rc = main(["--db", db, "delete", "1"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Deleted 1" in out

    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert [it["id"] for it in payload] == [2]


def test_delete_nonexistent_id_leaves_others_intact(tmp_path, capsys):
    db = _db(tmp_path)
    main(["--db", db, "add", "A"])
    main(["--db", db, "add", "B"])
    capsys.readouterr()

    rc = main(["--db", db, "delete", "999"])
    captured = capsys.readouterr()
    assert rc != 0
    assert "999" in captured.err

    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert {it["id"] for it in payload} == {1, 2}
