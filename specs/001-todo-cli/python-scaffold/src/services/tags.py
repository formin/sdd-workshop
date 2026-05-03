"""T005 — 태그 정규화·검증 도메인 모듈.

규칙:
- 정규화: Unicode NFKC → 앞뒤 공백 제거 → 소문자 변환
- 허용 문자: 영문/숫자/한글/`-`/`_` (정규화 후)
- 길이: 1자 이상 20자 이하 (정규화 후)
- 한도: 항목당 0~5개 (중복 제거 후)
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

__all__ = ["normalize_tag", "validate_tag", "validate_tags", "MAX_TAGS", "MAX_TAG_LEN"]


MAX_TAGS = 5
MAX_TAG_LEN = 20

# `\w`는 re.UNICODE에서 한글 자모/완성형 + 영문/숫자/언더스코어 포함.
# 하이픈은 별도 추가. 콤마·공백·기타 특수문자는 자연 거부.
_ALLOWED = re.compile(r"^[\w\-]+$", re.UNICODE)


def normalize_tag(raw: str) -> str:
    """Unicode NFKC 정규화 → trim → lowercase 순으로 적용.

    Raises:
        ValueError: 정규화 결과가 빈 문자열이면.
    """
    if raw is None:
        raise ValueError("태그는 비어 있을 수 없습니다")
    normalized = unicodedata.normalize("NFKC", raw).strip().lower()
    if not normalized:
        raise ValueError("태그는 비어 있을 수 없습니다")
    return normalized


def validate_tag(normalized: str) -> None:
    """정규화된 단일 태그의 길이·문자 집합 검증.

    `normalized`는 호출자가 이미 `normalize_tag` 결과를 넣어야 하나,
    방어적으로 빈 입력도 거부한다.

    Raises:
        ValueError: 길이 또는 문자 집합 위반 시.
    """
    if not normalized:
        raise ValueError("태그는 비어 있을 수 없습니다")
    if len(normalized) > MAX_TAG_LEN:
        raise ValueError(f"태그 길이는 1~{MAX_TAG_LEN}자여야 합니다 (입력: {normalized!r})")
    if not _ALLOWED.match(normalized):
        raise ValueError(f"태그에 허용되지 않는 문자가 포함되었습니다 (입력: {normalized!r})")


def validate_tags(items: Iterable[str] | None) -> frozenset[str]:
    """원시 태그 컬렉션을 정규화·검증·중복 제거하여 frozenset으로 반환.

    Raises:
        ValueError: 한도 초과·길이·문자·빈 태그 등 위반 시.
    """
    if items is None:
        return frozenset()

    raw_list = list(items)
    normalized: set[str] = set()
    for raw in raw_list:
        n = normalize_tag(raw)
        validate_tag(n)
        normalized.add(n)

    if len(normalized) > MAX_TAGS:
        raise ValueError(f"태그는 최대 {MAX_TAGS}개까지 허용됩니다 (입력: {len(normalized)}개)")
    return frozenset(normalized)
