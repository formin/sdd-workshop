from sqlalchemy import create_engine

from .models import Base


def init_db(db_path: str = "todo.db") -> None:
    """초기화: SQLite 파일을 만들고 테이블을 생성합니다."""
    url = f"sqlite:///{db_path}"
    engine = create_engine(url, echo=False, future=True)
    Base.metadata.create_all(engine)


__all__ = ["init_db"]
