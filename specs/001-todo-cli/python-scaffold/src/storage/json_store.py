"""T009 — 로컬 JSON 파일 기반 `Storage` 구현체."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from services.models import Priority, ToDoItem
from storage.base import Storage, StorageError

__all__ = ["JsonStorage", "StorageError"]


class JsonStorage(Storage):
    """단일 JSON 파일에 항목 목록을 직렬화한다."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._write_raw([])

    def add(self, item: ToDoItem) -> ToDoItem:
        items = self._load()
        next_id = (max((it.id for it in items), default=0)) + 1
        item.id = next_id
        items.append(item)
        self._save(items)
        return item

    def list(self) -> list[ToDoItem]:
        return sorted(self._load(), key=lambda it: it.id)

    def get(self, item_id: int) -> ToDoItem:
        for it in self._load():
            if it.id == item_id:
                return it
        raise KeyError(f"ID {item_id} 을(를) 찾을 수 없습니다")

    def update(self, item: ToDoItem) -> None:
        items = self._load()
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                self._save(items)
                return
        raise KeyError(f"ID {item.id} 을(를) 찾을 수 없습니다")

    def delete(self, item_id: int) -> None:
        items = self._load()
        for idx, existing in enumerate(items):
            if existing.id == item_id:
                del items[idx]
                self._save(items)
                return
        raise KeyError(f"ID {item_id} 을(를) 찾을 수 없습니다")

    # --- 내부 직렬화 헬퍼 ---

    def _load(self) -> list[ToDoItem]:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except PermissionError as e:
            raise StorageError(f"저장소 읽기 권한이 없습니다: {self._path}") from e
        except OSError as e:
            raise StorageError(f"저장소를 읽을 수 없습니다: {self._path} ({e})") from e

        if not raw.strip():
            return []

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            raise StorageError(f"저장소 파일이 손상되었습니다: {self._path} ({e})") from e

        return [_deserialize(d) for d in payload]

    def _save(self, items: list[ToDoItem]) -> None:
        payload = [_serialize(it) for it in items]
        self._write_raw(payload)

    def _write_raw(self, payload: list[dict]) -> None:
        try:
            self._path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except PermissionError as e:
            raise StorageError(f"저장소 쓰기 권한이 없습니다: {self._path}") from e
        except OSError as e:
            raise StorageError(f"저장소에 쓸 수 없습니다: {self._path} ({e})") from e


def _serialize(item: ToDoItem) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "created_at": item.created_at.isoformat(),
        "due_date": item.due_date.isoformat() if item.due_date else None,
        "priority": item.priority.value if item.priority else None,
        "completed": item.completed,
        # 002-tags: 항상 배열 키 부여, 사전식 정렬로 파일 diff 안정성 확보
        "tags": sorted(item.tags),
    }


def _deserialize(d: dict) -> ToDoItem:
    return ToDoItem(
        id=int(d["id"]),
        title=d["title"],
        created_at=datetime.fromisoformat(d["created_at"]),
        due_date=datetime.fromisoformat(d["due_date"]) if d.get("due_date") else None,
        priority=Priority(d["priority"]) if d.get("priority") else None,
        completed=bool(d["completed"]),
        # 002-tags: 태그 필드 없는 기존 파일은 빈 frozenset으로 해석 (FR-109)
        tags=frozenset(d.get("tags", [])),
    )
