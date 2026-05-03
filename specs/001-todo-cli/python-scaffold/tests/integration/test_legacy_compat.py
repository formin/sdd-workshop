"""T020 — 002-tags 도입 이전 데이터(태그 필드 없음) 후방 호환 스모크.

FR-109 / SC-104: 추가 마이그레이션 없이 모든 명령이 동작하고, 다음
쓰기 시점에 모든 항목 레코드에 `"tags": []` 키가 자동 추가된다.
"""

from __future__ import annotations

import json
from pathlib import Path

from cli.main import main

LEGACY_PAYLOAD = [
    {
        "id": 1,
        "title": "기존-A",
        "created_at": "2026-05-01T09:00:00+00:00",
        "due_date": None,
        "priority": None,
        "completed": False,
        # tags 키 없음
    },
    {
        "id": 2,
        "title": "기존-B",
        "created_at": "2026-05-02T09:00:00+00:00",
        "due_date": "2026-06-01T00:00:00+00:00",
        "priority": "high",
        "completed": True,
    },
]


def _legacy_db(tmp_path: Path) -> Path:
    path = tmp_path / "legacy-todo.json"
    path.write_text(json.dumps(LEGACY_PAYLOAD), encoding="utf-8")
    return path


def test_legacy_list_renders_empty_tags(tmp_path, capsys):
    db = _legacy_db(tmp_path)
    rc = main(["--db", str(db), "list"])
    out = capsys.readouterr().out
    assert rc == 0
    # 두 기존 항목 모두 tags:[]로 표시
    for line in out.splitlines():
        assert "tags:[]" in line
    assert "기존-A" in out
    assert "기존-B" in out


def test_legacy_complete_and_delete_still_work(tmp_path, capsys):
    db = _legacy_db(tmp_path)
    rc = main(["--db", str(db), "complete", "1"])
    capsys.readouterr()
    assert rc == 0

    rc = main(["--db", str(db), "delete", "2"])
    capsys.readouterr()
    assert rc == 0

    payload = json.loads(db.read_text(encoding="utf-8"))
    assert len(payload) == 1
    assert payload[0]["id"] == 1
    assert payload[0]["completed"] is True


def test_legacy_file_gets_tags_key_after_write(tmp_path, capsys):
    """다음 쓰기 시점에 모든 기존 항목에 tags 키가 자동 추가된다."""
    db = _legacy_db(tmp_path)
    rc = main(["--db", str(db), "add", "신규", "--tag", "work"])
    capsys.readouterr()
    assert rc == 0

    payload = json.loads(db.read_text(encoding="utf-8"))
    assert len(payload) == 3
    for record in payload:
        assert "tags" in record
    # 기존 두 항목은 빈 태그
    assert payload[0]["tags"] == []
    assert payload[1]["tags"] == []
    # 신규 항목은 work
    assert payload[2]["tags"] == ["work"]
