"""T004 — `ToDoItem` 데이터 모델 단위 테스트."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from services.models import Priority, ToDoItem


def test_todo_item_with_all_fields():
    item = ToDoItem(
        id=1,
        title="보고서 작성",
        due_date=datetime(2026, 6, 1, tzinfo=UTC),
        priority=Priority.HIGH,
        completed=False,
        created_at=datetime(2026, 5, 3, 10, 0, tzinfo=UTC),
    )
    assert item.id == 1
    assert item.title == "보고서 작성"
    assert item.due_date.tzinfo is not None
    assert item.priority is Priority.HIGH
    assert item.completed is False


def test_todo_item_optional_fields_default_to_none_or_false():
    item = ToDoItem(
        id=2,
        title="청소",
        created_at=datetime(2026, 5, 3, 10, 0, tzinfo=UTC),
    )
    assert item.due_date is None
    assert item.priority is None
    assert item.completed is False


def test_todo_item_requires_title():
    # 필수 필드 누락은 dataclass 시그니처에서 TypeError로 잡힘
    with pytest.raises(TypeError):
        ToDoItem(id=3)  # type: ignore[call-arg]


def test_priority_values_are_low_medium_high():
    assert {p.value for p in Priority} == {"low", "medium", "high"}


# --- T006: 002-tags 확장 — tags 필드 ---


def test_todo_item_tags_default_to_empty_frozenset():
    item = ToDoItem(
        id=10,
        title="기본 태그",
        created_at=datetime(2026, 5, 3, tzinfo=UTC),
    )
    assert item.tags == frozenset()
    assert isinstance(item.tags, frozenset)


def test_todo_item_accepts_explicit_tags():
    item = ToDoItem(
        id=11,
        title="태그 부여",
        created_at=datetime(2026, 5, 3, tzinfo=UTC),
        tags=frozenset({"work", "2026q2"}),
    )
    assert item.tags == frozenset({"work", "2026q2"})


def test_todo_item_required_signature_unchanged():
    """기존 ToDoItem(id=, title=, created_at=) 시그니처가 그대로 동작해야 한다."""
    item = ToDoItem(
        id=12,
        title="기존 흐름",
        created_at=datetime(2026, 5, 3, tzinfo=UTC),
    )
    assert item.tags == frozenset()
    assert item.due_date is None
    assert item.priority is None
    assert item.completed is False
