"""T011 — `TodoService` 비즈니스 로직.

CLI는 이 서비스만 호출한다(헌법 원칙 1: 레이어 분리).
"""

from __future__ import annotations

from datetime import UTC, datetime

from services.due_date import parse_due_date
from services.models import Priority, ToDoItem
from storage.base import Storage

__all__ = ["TodoService"]


def _to_priority(value: str | None) -> Priority | None:
    if value is None:
        return None
    try:
        return Priority(value)
    except ValueError as e:
        raise ValueError(
            f"우선순위는 {[p.value for p in Priority]} 중 하나여야 합니다 (입력: {value!r})"
        ) from e


class TodoService:
    """Storage 어댑터 위에서 도메인 규칙을 강제한다."""

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    def add(
        self,
        title: str,
        due: str | None = None,
        priority: str | None = None,
    ) -> ToDoItem:
        if not title or not title.strip():
            raise ValueError("title은 비어있을 수 없습니다")

        item = ToDoItem(
            id=0,  # storage가 부여
            title=title,
            created_at=datetime.now(tz=UTC),
            due_date=parse_due_date(due),
            priority=_to_priority(priority),
        )
        return self._storage.add(item)

    def list(
        self,
        completed: bool | None = None,
        priority: str | None = None,
    ) -> list[ToDoItem]:
        items = self._storage.list()
        if completed is not None:
            items = [it for it in items if it.completed is completed]
        if priority is not None:
            target = _to_priority(priority)
            items = [it for it in items if it.priority is target]
        return items

    def get(self, item_id: int) -> ToDoItem:
        return self._storage.get(item_id)

    def complete(self, item_id: int) -> ToDoItem:
        item = self._storage.get(item_id)
        item.completed = True
        self._storage.update(item)
        return item

    def delete(self, item_id: int) -> None:
        self._storage.delete(item_id)
