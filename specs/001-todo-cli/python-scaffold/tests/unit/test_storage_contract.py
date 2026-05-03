"""T007 — `Storage` 추상 인터페이스 계약 테스트."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from services.models import Priority, ToDoItem
from storage.json_store import JsonStorage


@pytest.fixture()
def store(tmp_path):
    return JsonStorage(tmp_path / "todo.json")


def _now() -> datetime:
    return datetime(2026, 5, 3, 10, 0, tzinfo=UTC)


def test_add_assigns_monotonic_id_and_persists(store):
    a = store.add(ToDoItem(id=0, title="A", created_at=_now()))
    b = store.add(ToDoItem(id=0, title="B", created_at=_now()))
    assert a.id == 1
    assert b.id == 2
    assert {it.id for it in store.list()} == {1, 2}


def test_get_returns_item_or_raises_for_missing(store):
    a = store.add(ToDoItem(id=0, title="A", created_at=_now()))
    assert store.get(a.id).title == "A"
    with pytest.raises(KeyError):
        store.get(999)


def test_update_modifies_existing(store):
    a = store.add(ToDoItem(id=0, title="A", created_at=_now()))
    a.completed = True
    a.priority = Priority.HIGH
    store.update(a)
    fetched = store.get(a.id)
    assert fetched.completed is True
    assert fetched.priority is Priority.HIGH


def test_update_nonexistent_raises(store):
    with pytest.raises(KeyError):
        store.update(ToDoItem(id=999, title="X", created_at=_now()))


def test_delete_removes_only_target(store):
    a = store.add(ToDoItem(id=0, title="A", created_at=_now()))
    b = store.add(ToDoItem(id=0, title="B", created_at=_now()))
    store.delete(a.id)
    assert {it.id for it in store.list()} == {b.id}


def test_delete_nonexistent_raises(store):
    with pytest.raises(KeyError):
        store.delete(999)


def test_persistence_survives_reopen(tmp_path):
    path = tmp_path / "todo.json"
    s1 = JsonStorage(path)
    s1.add(ToDoItem(id=0, title="A", created_at=_now()))
    s2 = JsonStorage(path)
    assert [it.title for it in s2.list()] == ["A"]
