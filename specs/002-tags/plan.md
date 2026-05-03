# Implementation Plan: 002-tags — ToDo 항목 태그 부여 및 태그 기반 필터

**Branch**: `002-tags` | **Date**: 2026-05-03 | **Spec**: [`specs/002-tags/spec.md`](./spec.md)
**Issues**: #1, #2

## Stack Reality Note (사용자 입력과의 차이)

`/speckit-plan` 호출 시 사용자가 "기존 todo_lib/, service.py, commands.py, Typer, SQLite+SQLAlchemy" 통합을 요청했으나, **현재 main 브랜치(`c2709a5 feat(cli): ToDo CLI v0.1`)의 실제 스택**은 다릅니다(001-todo-cli에서 typer/SQLAlchemy 스캐폴드를 제거하고 plan.md 결정에 맞춰 재작성했습니다).

| 사용자 입력에 명시 | 실제 main 코드 (권위 출처) |
|---|---|
| `todo_lib/` 패키지 | `src/services/`, `src/storage/`, `src/cli/` (3-레이어) |
| `todo_lib/service.py` | `src/services/todo_service.py` |
| `cli/commands.py` (Typer) | `src/cli/main.py` (argparse) |
| `Todo` (SQLAlchemy 모델) | `ToDoItem` (dataclass, `services/models.py`) |
| SQLite + SQLAlchemy 저장소 | 단일 JSON 파일 (`storage/json_store.py`) |
| `pytest`, Typer | `pytest`, `ruff`, 표준 라이브러리만 |

본 plan은 **사용자 의도의 본질**(기존 코드와 통합, 기존 테스트 회귀 0, "JSON 컬럼 = 단순함 우선")을 그대로 보존하며 실제 스택에 매핑합니다. "JSON 컬럼" 의미는 SQLite의 JSON1과 동일한 효과를 갖는 **JSON 파일 항목 레코드 내 `tags` 배열 필드**로 실현합니다(설계 변경 0, 헌법 원칙 4 단순함 일치).

## Summary

기존 ToDo CLI(001-todo-cli)에 항목당 0~5개 태그 부여 및 태그 기반 필터링을 추가한다. spec의 결정사항을 그대로 반영:

- **태그 모델**: `ToDoItem`에 `tags: frozenset[str]` 필드 추가 (집합·중복 없음·순서 무의미; 출력 시 사전식 정렬)
- **정규화**: `NFKC → trim → lowercase` 순 (FR-104, services 계층 책임)
- **검증**: 1~20자, 허용 문자(영문/숫자/한글/`-`/`_`), 최대 5개, 빈/공백·금지문자 거부
- **저장**: 기존 JSON 파일에 항목 레코드 안에 `tags: []` 키 추가, **태그 필드 없는 기존 데이터는 빈 배열로 해석**(FR-109/SC-104)
- **CLI 확장**: `add --tag <name>` 반복 옵션, `list --tag <name>` 단일 값 필터, 출력 라인에 항상 `tags:[t1,t2]` 표시(FR-110)
- **기존 테스트 회귀 0**: 001-todo-cli의 56개 통과 테스트가 전부 그대로 통과해야 함 (SC-103)

## Technical Context

- **언어/버전**: Python 3.11 (기존)
- **Primary Dependencies**: 표준 라이브러리만 (argparse, json, dataclasses, pathlib, **unicodedata**, re). 신규 외부 의존성 0건.
- **Storage**: 기존 JSON 파일(`todo.json`). 항목 레코드에 `tags` 배열 키 추가. 후방 호환은 역직렬화 시 `d.get("tags", [])` 한 줄로 처리.
- **Testing**: 기존 `pytest` 스위트 + 신규 단위/통합 테스트(아래 목록).
- **품질 도구**: 기존 `ruff` lint+format을 신규 코드에도 적용.
- **Target Platform**: 기존 동일 (Windows/macOS/Linux 로컬 CLI).
- **Project Type**: 단일 CLI 애플리케이션(추가 프로젝트 없음).
- **Performance Goals**: SC-101 `add` 95퍼센타일 < 1초, SC-102 `list --tag` 100개 항목 95퍼센타일 < 1초.
- **Constraints**: 기존 `todo.json` 무중단 호환, 신규 외부 의존성 추가 금지.
- **Scale/Scope**: 단일 사용자·로컬 파일 기준; 100~1,000 항목 규모에서 정상 동작.

## Constitution Check

*GATE: 모든 게이트는 Phase 0 진입 전 PASS여야 한다. Phase 1 후 재검증.*

- **원칙 1 — 레이어 분리**: PASS — 태그 정규화·검증은 `services/tags.py`(신규)와 `services/models.py` 확장에 두고, `cli/main.py`는 입력 수집·메시지 출력만 담당. `storage/json_store.py`는 직렬화/역직렬화만 책임.
- **원칙 2 — 테스트 우선 (NON-NEGOTIABLE)**: PASS — 모든 신규 시나리오에 RED 테스트를 먼저 작성하여 GREEN 페어 커밋 (자세한 테스트 목록은 본 plan의 *Test Strategy* 섹션).
- **원칙 3 — 최소 의존성**: PASS — 표준 라이브러리(`unicodedata`, `re`)만 사용. Dependency Justification 표 변경 없음(추가 행 불필요).
- **원칙 4 — 단순함 우선**: PASS — JSON 파일 단일 저장소·dataclass 유지. 별도 `Tag` 엔티티/테이블 도입 없음. "JSON 컬럼" 의미를 JSON 파일 내 배열 필드로 등치.
- **범위 확인 (원칙 5 — CLI 전용)**: PASS — 표준 입출력만 사용, REST/GUI 없음.

**게이트 결과: 5/5 PASS, 위반 없음.** 따라서 `## Complexity Tracking` 섹션은 비워둡니다.

## Project Structure

### Documentation (this feature)

```text
specs/002-tags/
├── plan.md                       # 본 파일
├── research.md                   # Phase 0 산출물
├── data-model.md                 # Phase 1 산출물
├── contracts/
│   └── cli-commands.md           # CLI 명령 계약 (입력/출력/오류 종료 코드)
├── quickstart.md                 # Phase 1 산출물 (사용 예시)
├── checklists/
│   └── requirements.md           # 명세 품질 체크리스트(이미 작성됨)
└── tasks.md                      # Phase 2 — `/speckit-tasks`가 생성
```

### Source Code (실제 main 코드 — 본 feature가 수정하는 위치)

```text
specs/001-todo-cli/python-scaffold/
├── pyproject.toml                # 변경 없음 (의존성 추가 0)
├── src/
│   ├── cli/
│   │   └── main.py               # 변경 — `add --tag`, `list --tag` 옵션 추가
│   ├── services/
│   │   ├── models.py             # 변경 — ToDoItem 에 tags: frozenset[str] 필드
│   │   ├── tags.py               # 신규 — normalize_tag, validate_tags
│   │   ├── todo_service.py       # 변경 — add(tags=...), list(tag=...) 시그니처 확장
│   │   └── due_date.py           # 변경 없음
│   └── storage/
│       ├── base.py               # 변경 없음 (인터페이스 동일)
│       └── json_store.py         # 변경 — _serialize/_deserialize 에 tags 추가, 후방 호환
└── tests/
    ├── unit/
    │   ├── test_tags.py          # 신규 — 정규화·검증
    │   ├── test_models.py        # 변경 — tags 필드 단위 테스트 추가
    │   ├── test_storage_json.py  # 변경 — tags 직렬화/역직렬화, 기존 파일 후방 호환
    │   ├── test_storage_contract.py  # 변경 없음 (계약 동일)
    │   └── test_service.py       # 변경 — add/list 태그 인자 처리
    └── integration/
        ├── test_cli_add.py       # 변경 — --tag 반복, 한도/길이/문자 오류
        ├── test_cli_list.py      # 변경 — --tag 단독·결합 필터, tags:[] 출력
        ├── test_cli_complete.py  # 변경 없음
        ├── test_cli_delete.py    # 변경 없음
        ├── test_cli_help.py      # 변경 — --tag 도움말 검증
        └── test_performance.py   # 변경 없음 (SC-101/102 동일 임계 유지)
```

**Structure Decision**: 기존 src-layout과 3-레이어를 그대로 유지. 태그 정규화·검증을 위한 신규 모듈 `services/tags.py` 1개만 추가하고, 나머지는 기존 파일에 인서트. 새 폴더/패키지 도입 없음.

## Test Strategy (헌법 원칙 2 강제)

각 GREEN 구현 태스크는 직전 RED 테스트가 커밋된 이후에만 시작한다. 신규 RED 테스트 핵심 셋:

| 테스트 파일 | 책임 | 매핑 FR/SC |
|---|---|---|
| `tests/unit/test_tags.py` | NFKC 정규화, trim, lowercase, 길이/문자 검증, 중복 제거 | FR-103/104/105, Edge Cases |
| `tests/unit/test_models.py` (확장) | `ToDoItem.tags` 기본값 빈 집합, dataclass 동작 | FR-101 |
| `tests/unit/test_storage_json.py` (확장) | tags 배열 직렬화, 정렬된 출력, **태그 필드 없는 기존 JSON 후방 호환** | FR-109, SC-104 |
| `tests/unit/test_service.py` (확장) | `add(tags=...)`/`list(tag=...)` 인자, 한도 위반·잘못된 문자·빈 태그 거부 | FR-101~108 |
| `tests/integration/test_cli_add.py` (확장) | `--tag` 반복, 6개째 거부, 21자 거부, 빈 `--tag ""` 거부, 중복 합치기 | US1 AC1~AC5 |
| `tests/integration/test_cli_list.py` (확장) | `--tag work`, `--tag urgent`(빈 결과), `--tag work --completed`, `tags:[]` 표시, 정렬 | US2 AC1~AC4, FR-110 |
| `tests/integration/test_cli_help.py` (확장) | `add --help`/`list --help`에 `--tag` 문구 등장 | SC-103 회귀 안전망 |

**기존 56개 테스트는 변경하지 않는다**. ToDoItem dataclass에 기본값 있는 신규 필드만 추가하므로 기존 인스턴스 생성·조회·완료·삭제 단언이 그대로 통과해야 한다(SC-103/SC-104 검증 포인트).

## Phase Breakdown (요약 — 자세한 분해는 `/speckit-tasks`)

1. **Phase 1 — 도메인 (RED→GREEN)**
   - `services/tags.py` 정규화·검증 함수 + `tests/unit/test_tags.py`
   - `ToDoItem.tags` 필드 추가 + `test_models.py` 보강
2. **Phase 2 — 저장소 (RED→GREEN)**
   - `JsonStorage._serialize/_deserialize` 확장 (정렬된 배열, 후방 호환) + `test_storage_json.py` 보강
3. **Phase 3 — 서비스 (RED→GREEN)**
   - `TodoService.add(tags=...)`, `TodoService.list(tag=...)` + `test_service.py` 보강
4. **Phase 4 — CLI (RED→GREEN)**
   - `cli/main.py`에 `add --tag` 반복 옵션, `list --tag` 단일 옵션, `_format_item`에 `tags:[...]` 추가
   - 통합 테스트(`test_cli_add.py`, `test_cli_list.py`, `test_cli_help.py`) 보강
5. **Phase 5 — 회귀 검증**
   - `pytest -q` → 56 baseline + 신규 케이스 모두 통과
   - `ruff check . && ruff format --check .` 0 issues
   - 스모크: 기존 `todo.json`(태그 필드 없음) 파일을 새 코드로 열어 `list`·`complete`·`delete` 정상 동작 확인

## Performance & Compatibility Notes

- **NFKC 비용**: 항목당 평균 2~3개 태그 가정 시 `unicodedata.normalize("NFKC", s)`는 µs 수준. SC-101/102 임계(1초) 영향 무시 가능.
- **후방 호환**: `_deserialize`에서 `frozenset(d.get("tags", []))` 한 줄로 충족. 별도 마이그레이션 명령 도입 안 함(spec Assumption 일치).
- **정렬**: 출력 시 사전식 정렬은 정규화된 문자열의 `sorted()`로 충분(NFKC 결과는 재현 가능).
- **GitHub Actions**: 기존 `.github/workflows/ci.yml`의 ruff+pytest 단일 잡으로 충분. 변경 없음.

## Out of Scope (spec과 일치)

- 항목 사후 태그 편집(`todo edit-tags` 등) — Clarifications Q1
- 다중 태그 AND/OR 조회 — `--tag` 반복은 argparse 마지막 값 사용, 의도된 단일 태그 의미
- 태그 자동완성·통계·그룹화·색상 표시 — 후속 명세

## Deliverables

- `specs/002-tags/plan.md` (본 파일)
- `specs/002-tags/research.md` (Phase 0)
- `specs/002-tags/data-model.md` (Phase 1)
- `specs/002-tags/contracts/cli-commands.md` (Phase 1)
- `specs/002-tags/quickstart.md` (Phase 1)
- `CLAUDE.md` 내 SPECKIT 마커 갱신(현재 활성 plan 참조)

## Next Steps

1. `/speckit-tasks` — 본 plan과 spec 결정사항을 RED→GREEN paired 태스크로 분해.
2. `/speckit-analyze` — 일관성 검증.
3. `/speckit-implement` — Phase 1부터 진행.
