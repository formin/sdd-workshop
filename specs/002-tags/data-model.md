# Data Model: 002-tags

## 변경 요약

기존 `ToDoItem` dataclass에 `tags` 필드 1개를 추가한다. 새로운 엔티티 도입 없음. 저장 포맷(JSON)에 `tags` 키만 추가되고 기존 키 의미는 모두 보존된다.

## ToDoItem (확장)

```text
class ToDoItem (dataclass):
    id: int                 # 기존
    title: str              # 기존
    created_at: datetime    # 기존
    due_date: datetime | None = None    # 기존
    priority: Priority | None = None    # 기존
    completed: bool = False             # 기존
    tags: frozenset[str] = frozenset()  # 신규 — 기본값 빈 집합
```

### 필드별 제약 (FR 매핑)

| 필드 | 제약 | 검증 위치 |
|---|---|---|
| `tags` 원소 길이 | NFKC 정규화 후 1자 ≤ len ≤ 20자 | `services/tags.py::validate_tag` |
| `tags` 원소 문자 | NFKC 정규화 후 `[\w가-힣\-]+`만 (`_`는 `\w`에 포함) | `services/tags.py::validate_tag` |
| `tags` 크기 | 0 ≤ len(tags) ≤ 5 | `services/tags.py::validate_tags` |
| `tags` 중복 | `frozenset`으로 자료형 차원에서 제거 | dataclass 필드 타입 |
| 정규화 순서 | `unicodedata.normalize("NFKC", s).strip().lower()` | `services/tags.py::normalize_tag` |

### 상태 전이

`tags`는 항목 생성 시에만 부여된다(spec Clarifications Q1 — 사후 편집 out-of-scope). `complete`, `delete`는 `tags`를 변경하지 않는다.

## Tag (값 객체)

별도 엔티티로 영속되지 않는다. `services/tags.py`의 함수들로만 표현한다.

```text
normalize_tag(raw: str) -> str
    NFKC → trim → lower 적용. 결과가 빈 문자열이면 ValueError.

validate_tag(normalized: str) -> None
    길이 1~20자, 허용 문자 집합 검증. 실패 시 ValueError.

validate_tags(items: Iterable[str]) -> frozenset[str]
    각 원소를 normalize_tag → validate_tag 한 뒤 frozenset 반환.
    결과 크기 > 5이면 ValueError.
```

## JSON 저장 포맷

### 신규 항목

```json
{
  "id": 3,
  "title": "보고서 작성",
  "created_at": "2026-05-03T10:00:00+00:00",
  "due_date": "2026-06-01T00:00:00+00:00",
  "priority": "high",
  "completed": false,
  "tags": ["2026q2", "work"]
}
```

- `tags`는 항상 배열로 직렬화되며, 사전식 오름차순으로 정렬된 정규화 문자열만 포함한다.
- 빈 태그는 `"tags": []`로 직렬화된다(생략하지 않는다).

### 기존 항목 (002-tags 도입 이전 저장됨)

```json
{
  "id": 1,
  "title": "이전 항목",
  "created_at": "2026-05-01T09:00:00+00:00",
  "completed": false
  // tags 키 없음
}
```

- 역직렬화 시 `tags: frozenset()`으로 해석한다 (`d.get("tags", [])`).
- 다음 쓰기 시점에 `"tags": []`가 자동으로 추가된다.

## 무결성 규칙

- **R-INT-1**: 저장 직전 모든 항목의 `tags`는 `validate_tags`를 통과해야 한다.
- **R-INT-2**: JSON 직렬화 결과의 `tags` 배열은 항상 정렬된 상태여야 한다(파일 diff 안정).
- **R-INT-3**: `JsonStorage.list()` 결과에서 `tags`는 모두 `frozenset[str]` 타입이며 정규화된 형태여야 한다.

## 관계도

```text
ToDoItem (1) ──contains──▶ Tag (0..5)  [값 객체, 비-식별]
```

본 사이클에서 `Tag`는 별도 인덱스/영속 엔티티가 아니므로 다른 ToDoItem과의 관계는 정의되지 않는다(공유 태그 통계는 후속 기능 영역).

## 마이그레이션

명시적 마이그레이션 단계 없음. 자연 후방 호환:
1. 기존 파일이 새 코드로 읽힐 때 → 빈 `tags` 집합으로 해석.
2. 모든 기존 명령(추가/조회/완료/삭제) 정상 동작.
3. 다음 항목 추가/완료/삭제로 파일이 재기록될 때 모든 항목에 `"tags": []` 키가 추가된다.
