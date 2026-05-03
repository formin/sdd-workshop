from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Todo


class TodoService:
    def __init__(self, db_path: str = "todo.db") -> None:
        # db_path can be a file path; use sqlite url
        url = f"sqlite:///{db_path}"
        self._engine = create_engine(url, echo=False, future=True)
        Base.metadata.create_all(self._engine)
        self._Session = sessionmaker(bind=self._engine, expire_on_commit=False)

    def add(self, title: str, due: Optional[str] = None, priority: Optional[str] = None) -> int:
        if not title:
            raise ValueError("title required")
        sess = self._Session()
        item = Todo(title=title, due_date=due, priority=priority, completed=False, created_at=datetime.utcnow())
        sess.add(item)
        sess.commit()
        sess.refresh(item)
        sess.close()
        return int(item.id)

    def list(self) -> List[Todo]:
        sess = self._Session()
        items = sess.query(Todo).order_by(Todo.id).all()
        sess.close()
        return items

    def complete(self, id: int) -> None:
        sess = self._Session()
        item = sess.get(Todo, id)
        if item is None:
            sess.close()
            raise ValueError("id not found")
        item.completed = True
        sess.add(item)
        sess.commit()
        sess.close()

    def delete(self, id: int) -> None:
        sess = self._Session()
        item = sess.get(Todo, id)
        if item is None:
            sess.close()
            raise ValueError("id not found")
        sess.delete(item)
        sess.commit()
        sess.close()
