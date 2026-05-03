"""T014 — `cli list` 통합 테스트 (필터 포함)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.main import main


def _db(tmp_path: Path) -> str:
    return str(tmp_path / "todo.json")


@pytest.fixture()
def populated(tmp_path):
    db = _db(tmp_path)
    main(["--db", db, "add", "낮은 우선", "--priority", "low"])
    main(["--db", db, "add", "높은 우선", "--priority", "high"])
    main(["--db", db, "add", "필터없음"])
    main(["--db", db, "complete", "2"])
    return db


def test_list_all(populated, capsys):
    capsys.readouterr()  # drain fixture output
    rc = main(["--db", populated, "list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "낮은 우선" in out
    assert "높은 우선" in out
    assert "필터없음" in out


def test_list_completed_filter(populated, capsys):
    capsys.readouterr()
    rc = main(["--db", populated, "list", "--completed"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "높은 우선" in out
    assert "낮은 우선" not in out
    assert "필터없음" not in out


def test_list_pending_filter(populated, capsys):
    capsys.readouterr()
    rc = main(["--db", populated, "list", "--pending"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "낮은 우선" in out
    assert "필터없음" in out
    assert "높은 우선" not in out


def test_list_priority_filter(populated, capsys):
    capsys.readouterr()
    rc = main(["--db", populated, "list", "--priority", "high"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "높은 우선" in out
    assert "낮은 우선" not in out


def test_list_empty(tmp_path, capsys):
    rc = main(["--db", _db(tmp_path), "list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "항목이 없습니다" in out


def test_list_completed_and_pending_mutually_exclusive(tmp_path):
    with pytest.raises(SystemExit):
        main(["--db", _db(tmp_path), "list", "--completed", "--pending"])
