"""T021 — `--help` 텍스트 검증 (SC-003 buildable proxy)."""

from __future__ import annotations

import pytest

from cli.main import main


def _help(argv: list[str], capsys) -> str:
    with pytest.raises(SystemExit) as exc:
        main(argv)
    assert exc.value.code == 0
    return capsys.readouterr().out


def test_root_help_lists_subcommands(capsys):
    out = _help(["--help"], capsys)
    for cmd in ["add", "list", "complete", "delete"]:
        assert cmd in out


def test_add_help_documents_due_and_priority(capsys):
    out = _help(["add", "--help"], capsys)
    assert "--due" in out
    assert "--priority" in out
    assert "title" in out


def test_list_help_documents_filters(capsys):
    out = _help(["list", "--help"], capsys)
    assert "--completed" in out
    assert "--pending" in out
    assert "--priority" in out


def test_complete_help_documents_id(capsys):
    out = _help(["complete", "--help"], capsys)
    assert "id" in out.lower()


def test_delete_help_documents_id(capsys):
    out = _help(["delete", "--help"], capsys)
    assert "id" in out.lower()


# --- T013 / T017: 002-tags 확장 — --tag 도움말 ---


def test_add_help_documents_tag_option_with_limit(capsys):
    out = _help(["add", "--help"], capsys)
    assert "--tag" in out
    # FR-102: 한도 안내
    assert "5" in out


def test_list_help_documents_tag_filter(capsys):
    out = _help(["list", "--help"], capsys)
    assert "--tag" in out
