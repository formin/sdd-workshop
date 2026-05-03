from typing import Optional

import typer

from todo_lib import TodoService
from todo_lib.init_db import init_db

app = typer.Typer(help="ToDo CLI (Typer)")


def get_service(db: str = "todo.db") -> TodoService:
    return TodoService(db)


@app.command()
def add(
    title: str = typer.Argument(..., help="할 일 제목"),
    due: Optional[str] = typer.Option(None, help="마감일 YYYY-MM-DD"),
    priority: Optional[str] = typer.Option(None, help="우선순위: high|medium|low"),
    db: str = typer.Option("todo.db", help="SQLite DB 파일 경로"),
):
    """항목 추가"""
    svc = get_service(db)
    tid = svc.add(title, due=due, priority=priority)
    typer.echo(f"Created ID {tid}")


@app.command()
def list(
    filter: Optional[str] = typer.Option(None, help="필터: done|pending"),
    priority: Optional[str] = typer.Option(None, help="우선순위 필터: high|medium|low"),
    db: str = typer.Option("todo.db", help="SQLite DB 파일 경로"),
):
    """목록 조회"""
    svc = get_service(db)
    items = svc.list()
    def keep(it):
        if filter == "done" and not it.completed:
            return False
        if filter == "pending" and it.completed:
            return False
        if priority and it.priority != priority:
            return False
        return True

    for it in filter(lambda x: keep(x), items):
        status = "x" if it.completed else " "
        typer.echo(f"{it.id}. [{status}] {it.title} (prio:{it.priority}) due:{it.due_date}")


@app.command()
def done(id: int = typer.Argument(..., help="완료 처리할 항목 ID"), db: str = typer.Option("todo.db", help="SQLite DB 파일 경로")):
    """항목 완료 처리"""
    svc = get_service(db)
    svc.complete(id)
    typer.echo(f"Marked {id} as completed")


@app.command()
def delete(id: int = typer.Argument(..., help="삭제할 항목 ID"), db: str = typer.Option("todo.db", help="SQLite DB 파일 경로")):
    """항목 삭제"""
    svc = get_service(db)
    svc.delete(id)
    typer.echo(f"Deleted {id}")


@app.command("init-db")
def initdb(db: str = typer.Option("todo.db", help="SQLite DB 파일 경로")):
    """데이터베이스 파일과 테이블을 초기화합니다."""
    init_db(db)
    typer.echo(f"Initialized DB: {db}")


if __name__ == "__main__":
    app()
