"""T008 — Edge Case 3: JSON 저장소 I/O 오류 처리."""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime

import pytest

from services.models import ToDoItem
from storage.json_store import JsonStorage, StorageError


def _now() -> datetime:
    return datetime(2026, 5, 3, 10, 0, tzinfo=UTC)


def test_corrupt_file_raises_storage_error(tmp_path):
    path = tmp_path / "todo.json"
    path.write_text("{not valid json", encoding="utf-8")
    store = JsonStorage(path)
    with pytest.raises(StorageError) as exc:
        store.list()
    assert "손상" in str(exc.value) or "corrupt" in str(exc.value).lower()


@pytest.mark.skipif(sys.platform.startswith("win"), reason="POSIX 권한 시맨틱 필요")
def test_unwritable_path_raises_storage_error(tmp_path):
    path = tmp_path / "todo.json"
    path.write_text("[]", encoding="utf-8")
    os.chmod(path, 0o400)  # 읽기 전용
    try:
        store = JsonStorage(path)
        with pytest.raises(StorageError) as exc:
            store.add(ToDoItem(id=0, title="A", created_at=_now()))
        assert "권한" in str(exc.value) or "permission" in str(exc.value).lower()
    finally:
        os.chmod(path, 0o600)


def test_unreadable_path_raises_storage_error(tmp_path, monkeypatch):
    """플랫폼에 무관하게 읽기 실패를 친절한 메시지로 변환한다."""
    path = tmp_path / "todo.json"
    path.write_text("[]", encoding="utf-8")
    store = JsonStorage(path)

    def _raise(*_args, **_kwargs):
        raise PermissionError("denied")

    monkeypatch.setattr("pathlib.Path.read_text", _raise)
    with pytest.raises(StorageError) as exc:
        store.list()
    assert "권한" in str(exc.value) or "permission" in str(exc.value).lower()


# --- T008: 002-tags 확장 — tags 직렬화/역직렬화/후방 호환 ---


def test_tags_round_trip(tmp_path):
    """저장한 태그가 같은 frozenset으로 복원된다."""
    path = tmp_path / "todo.json"
    store = JsonStorage(path)
    item = ToDoItem(
        id=0,
        title="태그 항목",
        created_at=_now(),
        tags=frozenset({"work", "2026q2"}),
    )
    store.add(item)
    fetched = store.list()[0]
    assert fetched.tags == frozenset({"work", "2026q2"})
    assert isinstance(fetched.tags, frozenset)


def test_tags_serialized_as_sorted_list(tmp_path):
    """디스크의 JSON 배열은 사전식 오름차순으로 정렬되어야 한다(파일 diff 안정)."""
    import json

    path = tmp_path / "todo.json"
    store = JsonStorage(path)
    store.add(
        ToDoItem(
            id=0,
            title="순서 검증",
            created_at=_now(),
            tags=frozenset({"work", "2026q2", "urgent"}),
        )
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload[0]["tags"] == ["2026q2", "urgent", "work"]


def test_empty_tags_serialized_as_empty_array(tmp_path):
    import json

    path = tmp_path / "todo.json"
    store = JsonStorage(path)
    store.add(ToDoItem(id=0, title="빈 태그", created_at=_now()))
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload[0]["tags"] == []


def test_legacy_file_without_tags_field_is_treated_as_empty(tmp_path):
    """FR-109/SC-104: 태그 필드가 없는 기존 데이터를 빈 frozenset으로 해석."""
    import json

    path = tmp_path / "legacy.json"
    legacy_payload = [
        {
            "id": 1,
            "title": "기존 항목",
            "created_at": _now().isoformat(),
            "due_date": None,
            "priority": None,
            "completed": False,
            # tags 키 없음
        }
    ]
    path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    store = JsonStorage(path)
    items = store.list()
    assert len(items) == 1
    assert items[0].tags == frozenset()


def test_legacy_file_rewrite_adds_tags_key(tmp_path):
    """기존 파일에 새 항목을 추가하면 모든 항목에 tags 키가 채워진다."""
    import json

    path = tmp_path / "legacy.json"
    legacy_payload = [
        {
            "id": 1,
            "title": "기존",
            "created_at": _now().isoformat(),
            "due_date": None,
            "priority": None,
            "completed": False,
        }
    ]
    path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    store = JsonStorage(path)
    store.add(
        ToDoItem(
            id=0,
            title="신규",
            created_at=_now(),
            tags=frozenset({"work"}),
        )
    )

    rewritten = json.loads(path.read_text(encoding="utf-8"))
    assert rewritten[0]["tags"] == []  # 기존 항목도 채워졌어야 함
    assert rewritten[1]["tags"] == ["work"]
