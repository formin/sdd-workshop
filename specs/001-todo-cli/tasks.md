# ToDo CLI — 실행 가능한 태스크 목록

본 태스크는 `specs/001-todo-cli/plan.md`(Python 3.11 + pytest + JSON 저장소, `src/cli` → `src/services` → `src/storage` 3-레이어)를 기반으로 분해한 커밋 단위 작업입니다. 각 항목은 하나의 커밋으로 적용 가능해야 합니다. 병렬 실행 가능한 작업에는 `[P]` 마커가 붙어 있습니다.

**경로 규약**: 모든 구현·테스트 자산은 `specs/001-todo-cli/python-scaffold/` 하위에 위치합니다. 이하 표기에서는 이 prefix를 생략하고 `src/...`, `tests/...`로 적습니다.

**TDD 게이트**: 각 "구현" 태스크는 직전의 "테스트" 태스크가 RED 상태(실패 확인)로 커밋된 이후에만 시작합니다.

## Phase 1 — Setup

- [X] T001 [P] 디렉터리 구조 생성: `src/cli/`, `src/services/`, `src/storage/`, `tests/unit/`, `tests/integration/` 와 각 패키지의 `__init__.py` (`specs/001-todo-cli/python-scaffold/`)
- [X] T002 패키지 초기화: `pyproject.toml` 작성 — Python 3.11, 진입점 `todo = cli.main:main`, 개발 의존성 `pytest`, `ruff` 등록 (`specs/001-todo-cli/python-scaffold/pyproject.toml`)
- [X] T003 [P] `.gitignore` 정비 및 CI 워크플로 갱신 — Python 3.11, `ruff check`, `ruff format --check`, `pytest -q` 실행 (`specs/001-todo-cli/python-scaffold/.gitignore`, `.github/workflows/ci.yml`)

## Phase 2 — Foundational (blocking)

- [X] T004 [데이터모델 RED] `ToDoItem` 단위 테스트: `id`/`title`/`due_date`/`priority`/`completed`/`created_at` 속성, 필수/선택 필드 검증 (`tests/unit/test_models.py`)
- [X] T005 [데이터모델 GREEN] `ToDoItem` dataclass + `Priority` StrEnum 구현 (`src/services/models.py`)
- [X] T006 [P] [Edge: 시간대 RED] ISO-8601 마감일 파싱 단위 테스트: 다른 시스템 시간대에서도 동일 결과(UTC 정규화) 보장 (`tests/unit/test_due_date.py`)
- [X] T006a [Edge: 시간대 GREEN] `parse_due_date()` 구현 — ISO-8601 파싱 후 UTC 정규화 (`src/services/due_date.py`)
- [X] T007 [P] [저장소 RED] `Storage` 추상 인터페이스 단위 테스트: `add/list/get/update/delete` 계약 (`tests/unit/test_storage_contract.py`)
- [X] T008 [P] [Edge: 파일권한 RED] JSON 저장소 I/O 오류 단위 테스트: 읽기/쓰기 권한 부재·손상 파일 시 `StorageError` 검증 (`tests/unit/test_storage_json.py`)
- [X] T009 [저장소 GREEN] `Storage` 추상 클래스 + `JsonStorage` 구현 (T007·T008 통과) (`src/storage/base.py`, `src/storage/json_store.py`)
- [X] T010 [서비스 RED] `TodoService` 단위 테스트: 추가/조회(필터)/완료/삭제, 비존재 ID 예외, 빈 제목 거부, **동일 제목·다중 항목에서 ID로 정확 참조(Edge 2)** (`tests/unit/test_service.py`)
- [X] T011 [서비스 GREEN] `TodoService` 구현, storage 의존성 주입 (`src/services/todo_service.py`)

## Phase 3 — User Story P1 (MVP: add, list)

- [X] T012 [US1] [add RED] `cli add` 통합 테스트: 정상 추가, 빈 제목 오류(US1.AC2), `--due`/`--priority` 옵션 파싱 (`tests/integration/test_cli_add.py`)
- [X] T013 [P] [US1] [add GREEN] `cli add` 명령 구현 (`src/cli/main.py`)
- [X] T014 [US1] [list RED] `cli list` 통합 테스트: 전체 조회, `--completed`/`--pending`/`--priority` 필터 (US2.AC1, AC2) (`tests/integration/test_cli_list.py`)
- [X] T015 [P] [US1] [list GREEN] `cli list` 명령 구현 (`src/cli/main.py`)

## Phase 4 — User Story P2 (complete, delete)

- [X] T016 [US2] [complete RED] `cli complete` 통합 테스트: 정상(US3.AC1) 및 비존재 ID(US3.AC2) 케이스 (`tests/integration/test_cli_complete.py`)
- [X] T017 [P] [US2] [complete GREEN] `cli complete` 명령 구현 (`src/cli/main.py`)
- [X] T018 [US2] [delete RED] `cli delete` 통합 테스트: 정상(US4.AC1) 및 비존재 ID(US4.AC2) 케이스 (`tests/integration/test_cli_delete.py`)
- [X] T019 [P] [US2] [delete GREEN] `cli delete` 명령 구현 (`src/cli/main.py`)

## Phase 5 — Polish & Cross-cutting

- [X] T020 [SC-001] 성능 회귀 테스트: `add`/`list`/`complete`/`delete` 100개 샘플 95퍼센타일 < 1초 (`tests/integration/test_performance.py`)
- [X] T021 [P] 사용성 도움말 (SC-003 buildable proxy): `todo --help` 및 각 서브커맨드 도움말 텍스트 검증 통합 테스트 (`tests/integration/test_cli_help.py`)
- [X] T022 [P] 문서화: `README.md` 빠른 시작·예시 명령·CI 배지 (`specs/001-todo-cli/python-scaffold/README.md`)
- [X] T023 [P] 린트·포맷: `ruff` 설정(`[tool.ruff]`/`[tool.ruff.format]` 추가) 및 CI에 `ruff check`/`ruff format --check` 단계 통합 (`pyproject.toml`, `.github/workflows/ci.yml`)

## Dependencies (실행 순서)

- Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5
- Phase 2 내부: T004→T005, T006→T006a, (T007‖T008)→T009, T010→T011. T006a·T009는 T010 시작 전 완료 필요.
- Phase 3·4 내부: 각 RED 테스트 태스크는 동일 phase의 GREEN 구현 태스크 직전에 RED 상태로 커밋되어야 한다(헌법 원칙 2).
- T013, T015, T017, T019는 모두 `src/cli/main.py`를 수정하므로 직렬 병합 권장(병렬 실행 시 충돌 주의).

## 독립 검증 기준 (User Story별)

- **US1 (add/list)**: `tests/integration/test_cli_add.py`, `test_cli_list.py` 모두 통과 + `pytest -q` 0 failure. ✅
- **US2 (complete/delete)**: `tests/integration/test_cli_complete.py`, `test_cli_delete.py` 모두 통과. ✅
- **SC-001 검증**: `tests/integration/test_performance.py` 100개 항목 기준 95퍼센타일 < 1초. ✅
- **SC-003 buildable proxy**: `tests/integration/test_cli_help.py` 통과. ✅

## 요구사항 ↔ 태스크 추적

| Requirement | Tasks |
|-------------|-------|
| FR-001 (add) | T012, T013 |
| FR-002 (list + 필터) | T014, T015 |
| FR-003 (complete) | T016, T017 |
| FR-004 (delete) | T018, T019 |
| FR-005 (stdio 전용) | T012~T019 (통합 테스트가 stdout/stderr 검증) |
| SC-001 (1초/95%) | T020 |
| SC-002 (필터 100% 통과) | T014, T015 |
| SC-003 (사용성 90%) — buildable proxy | T021 |
| Edge: 시간대 파싱 | T006 (RED), T006a (GREEN) |
| Edge: 파일 권한 오류 | T008 (RED), T009 (GREEN) |
| Edge: 동일 제목 ID 참조 | T010 (명시 케이스 포함), T016, T018 |

## 최종 검증 결과

- `pytest -q` → **56 passed, 1 skipped** (skip은 Windows에서 POSIX 권한 시맨틱 필요한 테스트)
- `ruff check .` → **All checks passed**
- `ruff format --check .` → **23 files already formatted**
- 스모크 테스트(`todo add`/`list`/`complete`/`delete`) → 정상 동작
