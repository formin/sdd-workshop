"""T020 — SC-001 성능 회귀: `todo add` 95% 사례 1초 이내.

`list`/`complete`/`delete`도 동일 임계로 강화 검증한다 (plan에 명시).
"""

from __future__ import annotations

import time
from statistics import quantiles

import pytest

from cli.main import main

THRESHOLD_S = 1.0
SAMPLE_SIZE = 100


def _p95(durations: list[float]) -> float:
    # 100개 샘플 → percentile=100 분할의 95번째 컷
    return quantiles(durations, n=100)[94]


@pytest.mark.parametrize("argv_factory_name", ["add", "list", "complete", "delete"])
def test_command_p95_under_one_second(tmp_path, capsys, argv_factory_name):
    db = str(tmp_path / "todo.json")
    durations: list[float] = []

    if argv_factory_name == "add":
        for i in range(SAMPLE_SIZE):
            t0 = time.perf_counter()
            main(["--db", db, "add", f"item-{i}"])
            durations.append(time.perf_counter() - t0)
    elif argv_factory_name == "list":
        for i in range(SAMPLE_SIZE):
            main(["--db", db, "add", f"item-{i}"])
        for _ in range(SAMPLE_SIZE):
            t0 = time.perf_counter()
            main(["--db", db, "list"])
            durations.append(time.perf_counter() - t0)
    elif argv_factory_name == "complete":
        for i in range(SAMPLE_SIZE):
            main(["--db", db, "add", f"item-{i}"])
        for i in range(1, SAMPLE_SIZE + 1):
            t0 = time.perf_counter()
            main(["--db", db, "complete", str(i)])
            durations.append(time.perf_counter() - t0)
    elif argv_factory_name == "delete":
        for i in range(SAMPLE_SIZE):
            main(["--db", db, "add", f"item-{i}"])
        for i in range(1, SAMPLE_SIZE + 1):
            t0 = time.perf_counter()
            main(["--db", db, "delete", str(i)])
            durations.append(time.perf_counter() - t0)

    capsys.readouterr()
    p95 = _p95(durations)
    assert p95 < THRESHOLD_S, f"{argv_factory_name} p95={p95:.3f}s 가 임계 {THRESHOLD_S}s 를 초과"


# --- T020a: 002-tags SC-102 perf — list --tag p95 < 1s + 정확도 5/5 ---


def test_list_tag_p95_under_one_second(tmp_path, capsys):
    """100개 항목 중 5개만 'urgent' 태그를 갖도록 분포한 뒤
    `list --tag urgent`의 p95 < 1초이며 정확히 5개를 반환하는지 검증."""
    db = str(tmp_path / "todo.json")
    urgent_indices = {7, 23, 41, 68, 92}  # 5개 (SC-102 명시)

    for i in range(SAMPLE_SIZE):
        if i in urgent_indices:
            main(["--db", db, "add", f"item-{i}", "--tag", "urgent"])
        else:
            main(["--db", db, "add", f"item-{i}", "--tag", "other"])

    capsys.readouterr()  # 사전 추가 출력 비우기

    durations: list[float] = []
    for _ in range(SAMPLE_SIZE):
        t0 = time.perf_counter()
        main(["--db", db, "list", "--tag", "urgent"])
        durations.append(time.perf_counter() - t0)

    out = capsys.readouterr().out
    # 정확도: 5개 매칭 라인 (각 호출마다 5개씩 반복 출력)
    matching_lines_per_call = sum(1 for line in out.splitlines() if "urgent" in line) // SAMPLE_SIZE
    assert matching_lines_per_call == 5, (
        f"매칭 항목 수가 5개가 아님 (호출당 {matching_lines_per_call}개)"
    )

    p95 = _p95(durations)
    assert p95 < THRESHOLD_S, f"list --tag p95={p95:.3f}s 가 임계 {THRESHOLD_S}s 를 초과"
