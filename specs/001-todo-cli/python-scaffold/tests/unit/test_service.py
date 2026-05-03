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


# --- T010: 002-tags 확장 — 태그 인자 처리 및 필터 ---


def test_add_with_tags_normalizes_and_dedupes(service):
    item = service.add(title="A", tags=["Work", "work", "  WORK  "])
    assert item.tags == frozenset({"work"})


def test_add_rejects_more_than_5_tags(service):
    with pytest.raises(ValueError):
        service.add(title="A", tags=["a", "b", "c", "d", "e", "f"])


def test_add_rejects_tag_too_long(service):
    with pytest.raises(ValueError):
        service.add(title="A", tags=["a" * 21])


def test_add_rejects_empty_tag(service):
    with pytest.raises(ValueError):
        service.add(title="A", tags=[""])


def test_add_rejects_disallowed_chars(service):
    with pytest.raises(ValueError):
        service.add(title="A", tags=["no spaces"])


def test_add_with_no_tags_kwarg_keeps_legacy_behavior(service):
    item = service.add(title="기존 흐름")
    assert item.tags == frozenset()


def test_list_filters_by_single_tag_exact_match(service):
    service.add(title="A", tags=["work"])
    service.add(title="B", tags=["personal"])
    service.add(title="C", tags=["work", "urgent"])

    work_items = service.list(tag="work")
    assert {it.title for it in work_items} == {"A", "C"}


def test_list_tag_filter_normalizes_input(service):
    service.add(title="A", tags=["work"])
    # 사용자가 'Work'로 조회해도 정규화 후 매칭
    assert {it.title for it in service.list(tag="Work")} == {"A"}


def test_list_tag_filter_returns_empty_when_no_match(service):
    service.add(title="A", tags=["work"])
    assert service.list(tag="missing") == []


def test_list_tag_combines_with_completed_filter(service):
    a = service.add(title="A", tags=["work"])
    service.add(title="B", tags=["work"])
    service.add(title="C", tags=["personal"])
    service.complete(a.id)

    result = service.list(tag="work", completed=True)
    assert {it.title for it in result} == {"A"}


def test_list_tag_combines_with_priority_filter(service):
    service.add(title="A", tags=["work"], priority="high")
    service.add(title="B", tags=["work"], priority="low")

    result = service.list(tag="work", priority="high")
    assert [it.title for it in result] == ["A"]


def test_list_without_tag_arg_returns_all(service):
    service.add(title="A", tags=["work"])
    service.add(title="B")
    assert {it.title for it in service.list()} == {"A", "B"}
