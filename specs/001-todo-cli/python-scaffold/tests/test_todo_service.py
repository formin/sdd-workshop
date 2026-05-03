import os
from pathlib import Path

import pytest


def test_add_list_complete_delete(tmp_path):
    """TDD: 서비스 동작 검증 테스트(추가/조회/완료/삭제).

    현재는 테스트 우선으로 작성되며, 이후 `todo_lib`의 구현을 통해 통과시킵니다.
    """
    db_path = tmp_path / "test.db"

    # 구현 대상: todo_lib.service.TodoService
    from todo_lib import service  # noqa: WPS305 (TDD 단계에서 import 에러가 발생함)

    svc = service.TodoService(db_path.as_posix())

    tid = svc.add("테스트 항목", due=None, priority="high")
    assert tid > 0

    items = svc.list()
    assert any(i.id == tid for i in items)

    svc.complete(tid)
    items = svc.list()
    it = next(i for i in items if i.id == tid)
    assert it.completed

    svc.delete(tid)
    items = svc.list()
    assert all(i.id != tid for i in items)
