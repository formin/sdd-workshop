"""T004 — 태그 정규화·검증 단위 테스트.

regulates services/tags.py contract: NFKC → trim → lowercase 순 정규화,
길이(1~20), 허용 문자(영문/숫자/한글/`-`/`_`), 한도(≤5), 중복 제거.
"""

from __future__ import annotations

import unicodedata

import pytest

from services.tags import normalize_tag, validate_tag, validate_tags

# --- normalize_tag ---


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("work", "work"),
        ("WORK", "work"),
        ("  Work  ", "work"),
        ("Work-2026", "work-2026"),
        ("한글_태그", "한글_태그"),
        # NFKC 호환 매핑
        ("①", "1"),
        # NFKC 합성 (precomposed café는 그대로, NFD `cafe´`도 동일 결과여야)
        (unicodedata.normalize("NFC", "café"), "café"),
        (unicodedata.normalize("NFD", "café"), "café"),
    ],
)
def test_normalize_tag_applies_nfkc_trim_lower(raw, expected):
    assert normalize_tag(raw) == expected


def test_normalize_tag_rejects_empty():
    with pytest.raises(ValueError):
        normalize_tag("")


def test_normalize_tag_rejects_whitespace_only():
    with pytest.raises(ValueError):
        normalize_tag("   ")


def test_normalize_tag_nfd_hangul_equivalent_to_nfc():
    nfc = unicodedata.normalize("NFC", "한글")
    nfd = unicodedata.normalize("NFD", "한글")
    assert normalize_tag(nfc) == normalize_tag(nfd)


# --- validate_tag (정규화된 입력 가정) ---


@pytest.mark.parametrize("ok", ["a", "work", "2026q2", "kebab-case", "snake_case", "한글"])
def test_validate_tag_accepts_allowed_chars(ok):
    validate_tag(ok)  # no raise


@pytest.mark.parametrize("bad", ["no spaces", "no,comma", "dot.test", "hash#tag", "slash/no"])
def test_validate_tag_rejects_disallowed_chars(bad):
    with pytest.raises(ValueError):
        validate_tag(bad)


def test_validate_tag_rejects_empty_after_normalize():
    with pytest.raises(ValueError):
        validate_tag("")


def test_validate_tag_rejects_too_long():
    with pytest.raises(ValueError):
        validate_tag("a" * 21)


def test_validate_tag_accepts_max_length():
    validate_tag("a" * 20)


# --- validate_tags (집합 차원: 한도/중복) ---


def test_validate_tags_returns_frozenset():
    result = validate_tags(["work", "2026Q2"])
    assert isinstance(result, frozenset)
    assert result == {"work", "2026q2"}


def test_validate_tags_dedupes_after_normalization():
    result = validate_tags(["Work", "work", "WORK", "  work  "])
    assert result == frozenset({"work"})


def test_validate_tags_accepts_empty_input():
    assert validate_tags([]) == frozenset()
    assert validate_tags(None) == frozenset()


def test_validate_tags_accepts_up_to_5():
    result = validate_tags(["a", "b", "c", "d", "e"])
    assert len(result) == 5


def test_validate_tags_rejects_more_than_5():
    with pytest.raises(ValueError):
        validate_tags(["a", "b", "c", "d", "e", "f"])


def test_validate_tags_rejects_invalid_member():
    with pytest.raises(ValueError):
        validate_tags(["ok", "no spaces"])


def test_validate_tags_rejects_empty_member():
    with pytest.raises(ValueError):
        validate_tags(["ok", ""])
