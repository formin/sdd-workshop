"""T006 — Edge Case 1: 시간대 안전한 ISO-8601 마감일 파싱.

서로 다른 시스템 시간대에서 호출되어도 동일한 UTC 정규화 결과를 보장해야 한다.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

import pytest

from services.due_date import parse_due_date


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("2026-06-01", datetime(2026, 6, 1, 0, 0, tzinfo=UTC)),
        ("2026-06-01T09:00:00+09:00", datetime(2026, 6, 1, 0, 0, tzinfo=UTC)),
        ("2026-06-01T00:00:00Z", datetime(2026, 6, 1, 0, 0, tzinfo=UTC)),
    ],
)
def test_parse_due_date_normalizes_to_utc(raw: str, expected: datetime):
    assert parse_due_date(raw) == expected


def test_parse_due_date_returns_none_for_none():
    assert parse_due_date(None) is None


def test_parse_due_date_invalid_format_raises():
    with pytest.raises(ValueError):
        parse_due_date("not-a-date")


def test_parse_due_date_consistent_across_local_tz(monkeypatch):
    """TZ 환경 변수를 바꿔도 동일한 UTC 결과를 반환해야 한다."""
    raw = "2026-06-01"
    expected = datetime(2026, 6, 1, 0, 0, tzinfo=UTC)

    # Asia/Seoul 가정
    monkeypatch.setenv("TZ", "Asia/Seoul")
    if hasattr(time, "tzset"):
        time.tzset()
    result_kst = parse_due_date(raw)

    # America/New_York 가정
    monkeypatch.setenv("TZ", "America/New_York")
    if hasattr(time, "tzset"):
        time.tzset()
    result_nyc = parse_due_date(raw)

    assert result_kst == result_nyc == expected
