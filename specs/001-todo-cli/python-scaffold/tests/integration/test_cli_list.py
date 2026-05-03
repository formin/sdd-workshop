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


# --- T015 / T016: 002-tags 확장 — list 출력 표시 + --tag 필터 ---


@pytest.fixture()
def tagged(tmp_path):
    db = _db(tmp_path)
    main(["--db", db, "add", "보고서", "--tag", "work", "--tag", "2026Q2"])
    main(["--db", db, "add", "장보기", "--tag", "personal"])
    main(["--db", db, "add", "잡일"])  # 태그 없음
    main(["--db", db, "add", "복합", "--tag", "work", "--tag", "urgent"])
    return db


def test_list_always_shows_tags_field(tagged, capsys):
    capsys.readouterr()  # drain fixture output
    rc = main(["--db", tagged, "list"])
    out = capsys.readouterr().out
    assert rc == 0
    # 모든 라인에 tags:[...] 토큰 포함
    for line in out.strip().splitlines():
        assert "tags:[" in line


def test_list_empty_tags_render_as_empty_brackets(tagged, capsys):
    capsys.readouterr()
    main(["--db", tagged, "list"])
    out = capsys.readouterr().out
    assert "잡일" in out
    # 잡일 항목은 tags:[] 형태로 표시
    for line in out.splitlines():
        if "잡일" in line:
            assert "tags:[]" in line


def test_list_tags_sorted_alphabetically(tagged, capsys):
    capsys.readouterr()
    main(["--db", tagged, "list"])
    out = capsys.readouterr().out
    for line in out.splitlines():
        if "보고서" in line:
            # work, 2026Q2 입력 → 정규화·정렬 후 [2026q2,work]
            assert "tags:[2026q2,work]" in line


def test_list_filter_by_tag_returns_matching_items_only(tagged, capsys):
    capsys.readouterr()
    rc = main(["--db", tagged, "list", "--tag", "work"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "보고서" in out
    assert "복합" in out
    assert "장보기" not in out
    assert "잡일" not in out


def test_list_filter_by_tag_normalizes_input(tagged, capsys):
    """입력은 'Work'/' work '/'WORK' 어느 것이든 동일하게 매칭."""
    capsys.readouterr()
    rc = main(["--db", tagged, "list", "--tag", "Work"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "보고서" in out
    assert "복합" in out


def test_list_filter_by_tag_no_match_returns_empty_message(tagged, capsys):
    capsys.readouterr()
    rc = main(["--db", tagged, "list", "--tag", "missing"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "항목이 없습니다" in out


def test_list_tag_combined_with_completed_filter(tmp_path, capsys):
    db = _db(tmp_path)
    main(["--db", db, "add", "A", "--tag", "work"])
    main(["--db", db, "add", "B", "--tag", "work"])
    main(["--db", db, "add", "C", "--tag", "personal"])
    main(["--db", db, "complete", "1"])
    capsys.readouterr()

    rc = main(["--db", db, "list", "--tag", "work", "--completed"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "A" in out
    assert "B" not in out
    assert "C" not in out


def test_list_tag_combined_with_priority_filter(tmp_path, capsys):
    db = _db(tmp_path)
    main(["--db", db, "add", "A", "--tag", "work", "--priority", "high"])
    main(["--db", db, "add", "B", "--tag", "work", "--priority", "low"])
    capsys.readouterr()

    rc = main(["--db", db, "list", "--tag", "work", "--priority", "high"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "A" in out
    assert "B" not in out
