"""T006a — ISO-8601 마감일 파싱·UTC 정규화.

날짜 전용(`YYYY-MM-DD`)은 UTC 자정으로 해석한다.
naive datetime을 받으면 UTC로 간주한다.
"""

from __future__ import annotations

from datetime import UTC, datetime


def parse_due_date(raw: str | None) -> datetime | None:
    """입력 문자열을 UTC tz-aware `datetime`으로 정규화한다.

    Args:
        raw: ISO-8601 문자열(`2026-06-01` 또는 `2026-06-01T09:00:00+09:00`) 또는 `None`.

    Returns:
        tz-aware UTC datetime, 또는 입력이 None이면 None.

    Raises:
        ValueError: 파싱할 수 없는 형식인 경우.
    """
    if raw is None:
        return None

    # `Z` suffix는 fromisoformat이 Python 3.11부터 지원.
    parsed = datetime.fromisoformat(raw)

    if parsed.tzinfo is None:
        # naive datetime은 UTC로 간주
        parsed = parsed.replace(tzinfo=UTC)
    else:
        parsed = parsed.astimezone(UTC)

    return parsed
