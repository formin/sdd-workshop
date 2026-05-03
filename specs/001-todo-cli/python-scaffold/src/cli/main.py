"""T013/T015/T017/T019 — CLI 진입점 (argparse 기반).

`cli/` 계층은 `services/` 만 호출하고 직접 `storage/`에 접근하지 않는다 (원칙 1).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from services.todo_service import TodoService
from storage.base import StorageError
from storage.json_store import JsonStorage

DEFAULT_DB = "todo.json"


def _format_item(it) -> str:
    mark = "x" if it.completed else " "
    due = it.due_date.date().isoformat() if it.due_date else "-"
    pri = it.priority.value if it.priority else "-"
    return f"{it.id}. [{mark}] {it.title} (priority:{pri}, due:{due})"


def _build_service(db_path: str) -> TodoService:
    return TodoService(JsonStorage(Path(db_path)))


def _cmd_add(args: argparse.Namespace) -> int:
    svc = _build_service(args.db)
    item = svc.add(title=args.title, due=args.due, priority=args.priority)
    print(f"Created ID {item.id}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    svc = _build_service(args.db)
    completed: bool | None = None
    if args.completed:
        completed = True
    elif args.pending:
        completed = False

    items = svc.list(completed=completed, priority=args.priority)
    if not items:
        print("(항목이 없습니다)")
        return 0
    for it in items:
        print(_format_item(it))
    return 0


def _cmd_complete(args: argparse.Namespace) -> int:
    svc = _build_service(args.db)
    item = svc.complete(args.id)
    print(f"Marked {item.id} as completed")
    return 0


def _cmd_delete(args: argparse.Namespace) -> int:
    svc = _build_service(args.db)
    svc.delete(args.id)
    print(f"Deleted {args.id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="ToDo CLI — 로컬 JSON 저장소 기반 단일 사용자 도구",
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help="JSON 저장소 파일 경로 (기본: todo.json)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="새 ToDo 항목 추가")
    p_add.add_argument("title", help="할 일 제목 (필수)")
    p_add.add_argument("--due", help="마감일 (ISO-8601, 예: 2026-06-01)")
    p_add.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        help="우선순위",
    )
    p_add.set_defaults(func=_cmd_add)

    p_list = sub.add_parser("list", help="ToDo 항목 목록 조회")
    flag = p_list.add_mutually_exclusive_group()
    flag.add_argument("--completed", action="store_true", help="완료된 항목만 표시")
    flag.add_argument("--pending", action="store_true", help="미완료 항목만 표시")
    p_list.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        help="우선순위로 필터",
    )
    p_list.set_defaults(func=_cmd_list)

    p_complete = sub.add_parser("complete", help="ID로 항목을 완료 처리")
    p_complete.add_argument("id", type=int, help="완료할 항목 ID")
    p_complete.set_defaults(func=_cmd_complete)

    p_delete = sub.add_parser("delete", help="ID로 항목을 삭제")
    p_delete.add_argument("id", type=int, help="삭제할 항목 ID")
    p_delete.set_defaults(func=_cmd_delete)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 2
    except KeyError as e:
        # KeyError는 메시지가 따옴표로 감싸지므로 args[0] 사용
        msg = e.args[0] if e.args else str(e)
        print(f"오류: {msg}", file=sys.stderr)
        return 3
    except StorageError as e:
        print(f"저장소 오류: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
