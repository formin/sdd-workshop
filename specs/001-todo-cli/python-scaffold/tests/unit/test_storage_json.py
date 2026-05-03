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
