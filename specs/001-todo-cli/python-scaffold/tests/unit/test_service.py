"""T010 — `TodoService` 단위 테스트."""

from __future__ import annotations

import pytest

from services.models import Priority
from services.todo_service import TodoService
from storage.json_store import JsonStorage


@pytest.fixture()
def service(tmp_path):
    return TodoService(JsonStorage(tmp_path / "todo.json"))


def test_add_creates_item_and_returns_id(service):
    a = service.add(title="A")
    assert a.id == 1
    assert a.title == "A"


def test_add_with_due_and_priority(service):
    item = service.add(title="발표 자료", due="2026-06-01", priority="high")
    assert item.due_date is not None
    assert item.due_date.tzinfo is not None
    assert item.priority is Priority.HIGH


def test_add_empty_title_rejected(service):
    with pytest.raises(ValueError):
        service.add(title="")


def test_add_invalid_priority_rejected(service):
    with pytest.raises(ValueError):
        service.add(title="A", priority="urgent")


def test_list_filters_by_completed_state(service):
    a = service.add(title="A")
    service.add(title="B")
    service.complete(a.id)

    assert {it.id for it in service.list(completed=True)} == {a.id}
    assert {it.title for it in service.list(completed=False)} == {"B"}


def test_list_filters_by_priority(service):
    service.add(title="High", priority="high")
    service.add(title="Low", priority="low")
    high = service.list(priority="high")
    assert [it.title for it in high] == ["High"]


def test_complete_marks_item_done(service):
    a = service.add(title="A")
    service.complete(a.id)
    assert service.get(a.id).completed is True


def test_complete_nonexistent_raises_keyerror(service):
    with pytest.raises(KeyError):
        service.complete(999)


def test_delete_removes_only_target(service):
    a = service.add(title="A")
    b = service.add(title="B")
    service.delete(a.id)
    assert {it.id for it in service.list()} == {b.id}


def test_delete_nonexistent_raises_keyerror(service):
    with pytest.raises(KeyError):
        service.delete(999)


def test_id_reference_with_duplicate_titles(service):
    """Edge Case 2 — 동일 제목 다중 항목에서 ID로 정확히 참조."""
    a = service.add(title="중복")
    b = service.add(title="중복")
    c = service.add(title="중복")
    assert {a.id, b.id, c.id} == {1, 2, 3}

    service.complete(b.id)
    assert service.get(a.id).completed is False
    assert service.get(b.id).completed is True
    assert service.get(c.id).completed is False

    service.delete(c.id)
    remaining = {it.id for it in service.list()}
    assert remaining == {a.id, b.id}
