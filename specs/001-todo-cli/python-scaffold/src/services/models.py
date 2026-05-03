"""T005 — `ToDoItem` 도메인 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Priority(StrEnum):
    """항목 우선순위."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ToDoItem:
    """ToDo 항목 도메인 모델.

    `id`/`title`/`created_at`은 필수. 나머지는 선택.
    """

    id: int
    title: str
    created_at: datetime
    due_date: datetime | None = None
    priority: Priority | None = None
    completed: bool = False
