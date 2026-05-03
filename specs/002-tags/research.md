# Research: 002-tags

본 문서는 `plan.md` 작성 과정에서 검토한 기술 결정과 그 근거를 통합 기록한다. spec.md의 `Clarifications`와 함께 권위 있는 의사결정 출처로 작동한다.

## R1: Unicode 정규화 라이브러리 선택

- **Decision**: 표준 라이브러리 `unicodedata.normalize("NFKC", s)`
- **Rationale**: Python 3.11 표준 모듈로 외부 의존성 0개. NFKC는 결합 문자(`café` vs `cafe´`)와 호환 매핑(`①`→`1`)을 모두 합성·정규화해 spec Q2 결정과 정확히 일치. `casefold()` 대신 `lower()`를 쓰는 한 비용은 µs 수준.
- **Alternatives considered**:
  - `regex` 패키지의 `\p{XID_Start}` 등 — 외부 의존성, 헌법 원칙 3 위반.
  - NFC만 적용 — 호환 매핑(`①`/`㈜` 등)을 정리하지 못해 결정 Q2(NFKC 채택)와 불일치.
  - 정규화 미적용 — Q2 답변(권장 옵션 A)으로 명시적 거부.

## R2: 태그 컬렉션 자료형

- **Decision**: 도메인 모델에서는 `frozenset[str]`, JSON 직렬화에서는 정렬된 `list[str]`
- **Rationale**: spec FR-104(중복 제거), FR-110(사전식 정렬 출력)을 자료형으로 강제. `frozenset`은 dataclass `eq` 비교에 안정, 이뮤터블이라 의도치 않은 변형 방지. JSON에는 `sorted(list(...))`로 직렬화하여 파일 diff가 안정적.
- **Alternatives considered**:
  - `list[str]` + 호출 시점 dedupe — 매번 정렬·중복 제거 호출 필요, 테스트 단언 깨지기 쉬움.
  - `set[str]` — 가변이라 의도치 않은 수정 가능성.

## R3: 허용 문자 집합 검증 정규식

- **Decision**: `re.compile(r"^[\w가-힣\-]+$", re.UNICODE)` 사용. 단, NFKC 정규화 **이후** 검증.
- **Rationale**: `\w`는 `[A-Za-z0-9_]`를 포함하고 `re.UNICODE`(Python 3에서 기본)에서 한글 자모도 포함. 하이픈은 별도 추가. 공백은 trim 후에도 검출되면 거부. 콤마 등은 `\w`에 포함되지 않아 자연 거부.
- **Alternatives considered**:
  - `unicodedata.category` 기반 화이트리스트 — 과한 일반화. spec 허용 집합이 명시되어 있어 정규식이 더 명료.
  - `str.isidentifier()` — 숫자 시작 거부 등 의도치 않은 제약.

## R4: 기존 데이터 후방 호환 전략 (FR-109 / SC-104)

- **Decision**: 역직렬화 시 `frozenset(d.get("tags", []))` 단일 라인. 별도 마이그레이션 명령 미도입.
- **Rationale**: spec Assumption과 일치. 기존 사용자 파일은 자연스럽게 빈 집합으로 해석되어 `list`/`complete`/`delete`가 그대로 동작. 다음 쓰기 시점에 자동으로 `tags: []` 키가 추가되며 데이터 손실 없음.
- **Alternatives considered**:
  - 기동 시 일괄 마이그레이션 — 사용자 환경에서 1회 실행 필요, 단순함 우선 위반.
  - 명시적 `todo migrate` 명령 — 헌법 원칙 4(YAGNI) 위반.

## R5: argparse 다중 옵션 표현 (`--tag` 반복)

- **Decision**:
  - `add` 서브커맨드: `--tag`를 `action="append"`로 정의 → 반복 호출 시 모두 수집.
  - `list` 서브커맨드: 기본 `action="store"`(=마지막 값) → 단일 태그 의미 강제.
- **Rationale**: spec Assumption("`list --tag`는 단일 값")과 정확히 일치. argparse 표준 동작이므로 추가 코드 0줄.
- **Alternatives considered**:
  - `nargs="*"`로 `--tag a b c` 형태 — 사용자 멘탈 모델("`--tag`를 반복")과 어긋남.
  - 콤마 구분 단일 값 `--tag a,b,c` — spec이 콤마를 거부 문자로 명시(허용문자 집합 외).

## R6: 정렬·표시 형식 안정성 (FR-110)

- **Decision**: `_format_item` 내부에서 `tags = ",".join(sorted(item.tags))`로 항상 사전식 정렬.
- **Rationale**: 통합 테스트 단언 안정성(spec Q3 결정 근거). `frozenset`은 순회 순서 비결정적이므로 출력 시점 정렬 필수.

## R7: 성능 검증 베이스라인

- **Decision**: 기존 `tests/integration/test_performance.py`의 임계(95퍼센타일 < 1초, 100개 항목)를 그대로 유지하되 본 사이클에서 추가 케이스는 추가하지 않음. 태그 추가의 비용이 µs 수준이라 기존 테스트가 회귀 신호 역할을 한다.
- **Rationale**: SC-101/102가 기존 임계와 같은 수치이며, 새로운 회귀가 발생하면 기존 성능 테스트가 자연스럽게 실패하므로 별도 케이스 작성은 단순함 우선 원칙에 어긋난다.
- **Alternatives considered**:
  - 태그 부착 항목으로만 따로 측정 — 신규 가치 없음, 테스트 비용만 증가.

## R8: 헌법 게이트 재확인 결과

| 게이트 | 사전 평가 | 사후 (Phase 1 설계 후) |
|---|---|---|
| 원칙 1 (레이어 분리) | PASS | PASS — `services/tags.py` 신규 모듈로 도메인 책임 명확 |
| 원칙 2 (테스트 우선) | REQUIRED | PASS — 7개 RED 테스트 셋 명시 |
| 원칙 3 (최소 의존성) | PASS | PASS — 표준 라이브러리만 추가 사용 |
| 원칙 4 (단순함) | PASS | PASS — 신규 폴더 0, 신규 모듈 1, 기존 인터페이스 보존 |
| 원칙 5 (CLI 전용) | PASS | PASS — 표준 입출력만 |

## 미해결 항목 (Outstanding)

없음. 모든 결정이 Decision/Rationale/Alternatives로 봉인되어 `/speckit-tasks` 진입 가능.
