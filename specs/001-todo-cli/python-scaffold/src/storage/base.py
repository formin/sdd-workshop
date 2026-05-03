"""T009 — `Storage` 추상 인터페이스 + 공용 예외."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from services.models import ToDoItem


class StorageError(Exception):
    """저장소 I/O·무결성 오류를 사용자 친화적으로 표현한다."""


class Storage(ABC):
    """ToDo 항목 영속화 계약."""

    @abstractmethod
    def add(self, item: ToDoItem) -> ToDoItem:
        """항목을 저장하고 ID가 부여된 객체를 반환한다."""

    @abstractmethod
    def list(self) -> list[ToDoItem]:
        """전체 항목을 ID 오름차순으로 반환한다."""

    @abstractmethod
    def get(self, item_id: int) -> ToDoItem:
        """ID로 단일 항목을 조회한다.

        Raises:
            KeyError: 해당 ID가 없을 때.
        """

    @abstractmethod
    def update(self, item: ToDoItem) -> None:
        """기존 항목을 갱신한다.

        Raises:
            KeyError: 해당 ID가 없을 때.
        """

    @abstractmethod
    def delete(self, item_id: int) -> None:
        """ID로 단일 항목을 삭제한다.

        Raises:
            KeyError: 해당 ID가 없을 때.
        """


__all__: Iterable[str] = ["Storage", "StorageError"]
