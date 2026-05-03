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


# --- T012: 002-tags 확장 — --tag 옵션 ---


def test_add_with_single_tag(tmp_path, capsys):
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "보고서", "--tag", "work"])
    capsys.readouterr()
    assert rc == 0
    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert payload[0]["tags"] == ["work"]


def test_add_with_multiple_tags_repeated_option(tmp_path, capsys):
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "보고서", "--tag", "work", "--tag", "2026Q2"])
    capsys.readouterr()
    assert rc == 0
    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    # 사전식 정렬 + 정규화(소문자)
    assert payload[0]["tags"] == ["2026q2", "work"]


def test_add_max_5_tags_accepted(tmp_path, capsys):
    db = _db(tmp_path)
    argv = ["--db", db, "add", "x"]
    for t in ["a", "b", "c", "d", "e"]:
        argv.extend(["--tag", t])
    rc = main(argv)
    capsys.readouterr()
    assert rc == 0
    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert payload[0]["tags"] == ["a", "b", "c", "d", "e"]


def test_add_rejects_6_tags(tmp_path, capsys):
    db = _db(tmp_path)
    argv = ["--db", db, "add", "x"]
    for t in ["a", "b", "c", "d", "e", "f"]:
        argv.extend(["--tag", t])
    rc = main(argv)
    captured = capsys.readouterr()
    assert rc != 0
    assert "최대" in captured.err or "5" in captured.err


def test_add_rejects_tag_too_long(tmp_path, capsys):
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "x", "--tag", "a" * 21])
    captured = capsys.readouterr()
    assert rc != 0
    assert "20" in captured.err or "길이" in captured.err


def test_add_rejects_empty_tag(tmp_path, capsys):
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "x", "--tag", ""])
    captured = capsys.readouterr()
    assert rc != 0
    assert "비어" in captured.err or "empty" in captured.err.lower()


@pytest.mark.parametrize("bad_tag", ["no spaces", "no,comma", "dot.test"])
def test_add_rejects_disallowed_chars(tmp_path, capsys, bad_tag):
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "x", "--tag", bad_tag])
    captured = capsys.readouterr()
    assert rc != 0
    assert "허용" in captured.err or "허용되지" in captured.err


def test_add_dedupes_repeated_same_tag(tmp_path, capsys):
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "x", "--tag", "work", "--tag", "WORK", "--tag", "  work  "])
    capsys.readouterr()
    assert rc == 0
    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert payload[0]["tags"] == ["work"]


def test_add_without_tag_legacy_flow_preserved(tmp_path, capsys):
    """FR-106: 태그 옵션 없이 추가하면 기존 흐름과 동일."""
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "기존 흐름"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Created ID 1" in captured.out
    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert payload[0]["tags"] == []


def test_add_tag_nfkc_normalization(tmp_path, capsys):
    """대소문자/공백 차이 입력은 동일 태그로 합쳐져야 함."""
    db = _db(tmp_path)
    rc = main(["--db", db, "add", "x", "--tag", "Work"])
    capsys.readouterr()
    assert rc == 0
    payload = json.loads(Path(db).read_text(encoding="utf-8"))
    assert payload[0]["tags"] == ["work"]
