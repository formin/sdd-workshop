# Tasks: 002-tags — ToDo 항목 태그 부여 및 태그 기반 필터

**Input**: 설계 문서 — `specs/002-tags/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/cli-commands.md](./contracts/cli-commands.md), [quickstart.md](./quickstart.md)

**Tests**: 헌법 원칙 2(NON-NEGOTIABLE)에 따라 모든 신규 기능은 RED 테스트를 먼저 작성한 뒤 GREEN 구현으로 짝을 짓는다.

**Organization**: 사용자 스토리별 phase로 그룹화. US1과 US2는 모두 P1이지만 US1(태그 부여)이 US2(태그 필터)의 전제이므로 순차 진행한다.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 다른 파일을 수정하므로 병렬 가능
- **[Story]**: 해당 태스크가 속한 사용자 스토리 (US1/US2)
- 모든 경로는 `specs/001-todo-cli/python-scaffold/` 기준 (이하 본 prefix 생략)
- TDD 게이트: 각 GREEN 태스크는 직전 RED 태스크가 RED 상태로 커밋된 이후에만 시작

---

## Phase 1: Setup (회귀 안전망 확립)

**Purpose**: 본 사이클 작업 전에 **기존 테스트 전부 통과**를 첫 번째 확인 기준으로 설정. 이 phase가 PASS하지 않으면 어떤 신규 작업도 시작하지 않는다.

- [X] T001 회귀 베이스라인 캡처: `pytest -q` 실행해 **56 passed, 1 skipped**(Windows에서 POSIX 권한 테스트) 확인 — 결과를 `specs/002-tags/baseline.txt`로 저장(커밋하지 않음, gitignored)
- [X] T002 [P] 품질 베이스라인 캡처: `ruff check .` / `ruff format --check .` 모두 0 issues 확인
- [X] T003 [P] 환경 정합성 점검: Python 3.11 venv 활성, `pip install -e ".[dev]"` 재실행해 의존성 누락 없음 확인 (`specs/001-todo-cli/python-scaffold/`)

**Checkpoint 1**: 기존 테스트 56/1 + ruff 0/0 통과 — 이 시점이 본 feature의 회귀 0건 기준점이다.

---

## Phase 2: Foundational (US1·US2 공통 도메인 계층)

**Purpose**: 태그 정규화·검증·모델 확장은 US1과 US2 모두의 전제. 이 phase 완료 전에는 어떤 user story phase도 진입할 수 없다.

- [X] T004 [P] [태그 도메인 RED] 태그 정규화·검증 단위 테스트 작성 — NFKC + trim + lowercase, 길이(1~20), 허용 문자(`[\w가-힣\-]+`), 한도(≤5), 중복 제거, 빈 태그 거부, 호환 매핑(`①`→`1`), NFD↔NFC 등가 (`tests/unit/test_tags.py`)
- [X] T005 [태그 도메인 GREEN] `services/tags.py` 신규 모듈 구현 — `normalize_tag`, `validate_tag`, `validate_tags` (`src/services/tags.py`)
- [X] T006 [모델 RED] `ToDoItem.tags: frozenset[str]` 필드 단위 테스트 추가 — 기본값 빈 집합, 명시 부여, 기존 시그니처(필수 인자 변동 없음) 단언 (`tests/unit/test_models.py` 확장)
- [X] T007 [모델 GREEN] `ToDoItem`에 `tags: frozenset[str] = frozenset()` 필드 추가 (`src/services/models.py`)
- [X] T008 [저장소 RED] JSON 직렬화/역직렬화 단위 테스트 확장 — tags 배열은 사전식 정렬, 빈 태그는 `[]`로 직렬화, **태그 필드 없는 기존 JSON(`get("tags", [])`)을 빈 frozenset으로 해석**, 라운드트립 보존 (`tests/unit/test_storage_json.py` 확장)
- [X] T009 [저장소 GREEN] `_serialize`/`_deserialize`에 tags 처리 추가 — 직렬화 시 `sorted(list(item.tags))`, 역직렬화 시 `frozenset(d.get("tags", []))` (`src/storage/json_store.py`)
- [X] T010 [서비스 RED] `TodoService` 단위 테스트 확장 — `add(title, tags=...)` 정상/한도/길이/문자/빈/중복, `list(tag=...)` 단일 태그 정확 일치(정규화 후), 비존재 태그 빈 결과, `--tag` + `--completed`/`--priority` AND 결합 (`tests/unit/test_service.py` 확장)
- [X] T011 [서비스 GREEN] `TodoService.add` 시그니처에 `tags: Iterable[str] | None = None` 추가, `validate_tags`로 정규화·검증 후 ToDoItem에 부여; `TodoService.list` 시그니처에 `tag: str | None = None` 추가, `normalize_tag` 후 정확 일치 필터 (`src/services/todo_service.py`)

**Checkpoint 2**: `pytest tests/unit -q` 전 통과 + 회귀 0건. **계약 테스트(`test_storage_contract.py`) 변경 없이도 통과해야 함**.

---

## Phase 3: User Story 1 — 항목 생성 시 태그 부여 (Priority: P1) 🎯 MVP

**Goal**: 사용자가 `todo add ... --tag <name> --tag <name2>`로 0~5개 태그를 부여하며, 입력 검증·기존 흐름 보존·중복 합치기가 작동한다.

**Independent Test**: 새 빈 DB에서 태그 0/1/N개 추가, 한도/길이/문자 위반 거부, 빈 태그 거부, 중복 합치기를 통합 테스트로 검증할 수 있다 (`tests/integration/test_cli_add.py` 단독 통과).

- [X] T012 [US1] [add CLI RED] `cli add --tag` 통합 테스트 확장 — 정상(0개/1개/5개), 6개째 거부, 21자 거부, 빈 `--tag ""` 거부, 금지 문자 거부, 동일 태그 중복 → 1개 합치기, 기존 무태그 흐름(`Created ID 1`) 보존, NFKC 정규화 케이스(`Work` → `work`) (`tests/integration/test_cli_add.py` 확장)
- [X] T013 [P] [US1] [help RED] `todo add --help` 출력에 `--tag` 옵션 행과 한도(5) 안내 문구가 포함되는지 단언 (`tests/integration/test_cli_help.py` 확장)
- [X] T014 [US1] [add CLI GREEN] `cli/main.py`의 `add` 서브파서에 `--tag <name>` 옵션을 `action="append"`로 추가, 도움말 텍스트에 한도 안내, `_cmd_add`가 `args.tag` 또는 `[]`를 서비스에 전달, 도메인 `ValueError`는 종료 코드 2로 stderr 친화적 메시지 출력 (`src/cli/main.py`)

**Checkpoint 3 (US1 MVP)**: `pytest tests/integration/test_cli_add.py tests/integration/test_cli_help.py -q` 통과 + 전 회귀 0건. 이 시점에서 US1만으로도 사용자가 태그 부여를 활용 가능.

---

## Phase 4: User Story 2 — 태그로 목록 필터링 (Priority: P1)

**Goal**: 사용자가 `todo list --tag <name>`으로 특정 태그 항목만 추리며, 다른 필터와 AND 결합 가능, 빈 결과는 정상 처리, list 출력에는 `tags:[t1,t2]`가 항상 표시된다.

**Independent Test**: US1로 다양한 태그 조합을 가진 항목들을 추가한 뒤 `--tag` 단독·결합 필터 결과의 정확성·정렬·빈 결과 처리·`tags:[]` 표시를 통합 테스트로 검증.

- [X] T015 [US2] [list 출력 RED] `cli list` 출력에 `tags:[t1,t2,...]` 표시 단언 추가 — 항상 표시, 사전식 오름차순, 빈 태그는 `tags:[]`, 콤마 구분(공백 없음). 기존 출력 단언이 깨지지 않도록 부분 문자열 단언 보강 (`tests/integration/test_cli_list.py` 확장)
- [X] T016 [US2] [list 필터 RED] `cli list --tag` 통합 테스트 — 단독 필터(매칭/비매칭/빈 결과), `--completed`·`--priority`와 AND 결합, NFKC 정규화 일관성(`Work` 입력 = `work` 매칭) (`tests/integration/test_cli_list.py` 확장)
- [X] T017 [P] [US2] [help RED] `todo list --help` 출력에 `--tag` 옵션 행이 포함되는지 단언 (`tests/integration/test_cli_help.py` 확장)
- [X] T018 [US2] [list GREEN] `cli/main.py`의 `list` 서브파서에 `--tag <name>` 단일 옵션 추가(`action="store"`, 기본 None), `_cmd_list`가 `args.tag`를 서비스에 전달, `_format_item`에 `tags:[<sorted,joined>]` 추가 (`src/cli/main.py`)
- [X] T019 [P] [US2] [회귀 단언 RED→FIX] 기존 `test_cli_list.py`의 출력 단언이 새 `tags:[]` 토큰 추가로 깨지면 부분 문자열 비교로 보강(추가만, 제거 금지) (`tests/integration/test_cli_list.py`)

**Checkpoint 4 (US2 완료)**: `pytest -q` 전체 통과. US1+US2 결합으로 spec의 두 P1 모두 달성.

---

## Phase 5: Polish & Cross-cutting

**Purpose**: 회귀 검증, 문서, 호환성 스모크.

- [X] T020 [P] 데이터 후방 호환 스모크 — `tags` 필드 없는 샘플 `legacy-todo.json`(2개 항목)을 임시 디렉터리에 생성한 뒤 `--db`로 지정해 `list`/`complete`/`delete` 모두 정상 동작 + 다음 쓰기 후 `"tags": []` 키가 추가되는지 단언 (`tests/integration/test_legacy_compat.py` 신규)
- [X] T020a [P] [SC-102 perf RED+GREEN] `list --tag` 성능 회귀 — 100개 항목(태그 다양 분포, 그 중 5개만 `urgent`) 사전 추가 후 `main(["--db", db, "list", "--tag", "urgent"])`를 SAMPLE_SIZE(=100)회 호출. `quantiles(durations, n=100)[94]`가 `THRESHOLD_S(=1.0)` 미만임을 단언하고, 결과의 정확도(매칭 항목 수=5)도 함께 검증. spec SC-102 직접 측정 (`tests/integration/test_performance.py` 확장 — 신규 `test_list_tag_p95_under_one_second` 함수 추가, 기존 함수 변경 금지)
- [X] T021 [P] tasks.md의 모든 [X] 마킹 + 회귀 결과 기록 — `pytest -q` 최종 결과(예: 65 passed, 1 skipped), `ruff check`/`format --check` 결과를 본 파일 하단의 검증 결과 섹션에 기록
- [X] T022 [P] quickstart 검증 — `specs/002-tags/quickstart.md`의 예시 명령들을 손으로 따라가 출력이 일치하는지 확인(스크린샷·로그 불필요, 사용자 시나리오 점검)
- [X] T023 README 갱신 — `specs/001-todo-cli/python-scaffold/README.md`의 사용 예시에 `--tag` 사용 문구 추가 (`specs/001-todo-cli/python-scaffold/README.md`)

**Checkpoint 5 (최종)**: 전체 `pytest -q` + `ruff` 통과, 후방 호환 스모크(T020) PASS, **SC-102 perf 단언(T020a) PASS**, 문서 갱신 완료.

---

## Dependencies (실행 순서)

1. **Phase 1 → 모든 phase 시작 전 필수.** 회귀 베이스라인이 깨지면 진행 금지.
2. **Phase 2 → Phase 3, 4 모두의 전제.** 도메인·저장소·서비스가 안정되어야 CLI 통합 테스트 작성 가능.
3. **Phase 3 (US1)** → **Phase 4 (US2)**. US2는 US1로 부여된 태그가 있어야 필터 검증이 의미 있음.
4. **Phase 5**는 Phase 4 완료 후.

### Phase 내부 순서

- Phase 2: T004→T005, T006→T007, T008→T009, T010→T011 (각 RED→GREEN). T004/T006/T008/T010은 서로 다른 파일이라 병렬 가능 (`[P]` 표시는 phase-내 RED 테스트 작성 단계만 해당).
- Phase 3: T012→T014, T013은 T014와 병행 가능.
- Phase 4: T015·T016·T017은 병렬, 모두 끝나면 T018 → T019.
- Phase 5: T020·T020a·T021·T022 병렬, T023은 마지막.

---

## 병렬 실행 예시

- 팀원 A: T004 (`tests/unit/test_tags.py`)
- 팀원 B: T006 (`tests/unit/test_models.py` 확장 부분)
- 팀원 C: T008 (`tests/unit/test_storage_json.py` 확장 부분)
- 팀원 D: T010 (`tests/unit/test_service.py` 확장 부분)

위 4명이 병렬로 RED 테스트를 작성한 뒤 각자의 GREEN 짝(T005/T007/T009/T011)을 직렬화해 진행.

---

## 요구사항 ↔ 태스크 추적

| Requirement / Story | Tasks |
|---|---|
| FR-101 (`--tag` 0회 이상) | T012, T014 |
| FR-102 (≤5개) | T004, T005, T012 |
| FR-103 (1~20자) | T004, T005, T012 |
| FR-104 (NFKC→trim→lower→dedupe) | T004, T005 |
| FR-105 (허용 문자) | T004, T005, T012 |
| FR-106 (무태그 기존 흐름 보존) | T012, T014 (회귀 단언) |
| FR-107 (`list --tag` 정확 일치) | T010, T011, T016, T018 |
| FR-108 (다른 필터와 AND 결합) | T010, T011, T016, T018 |
| FR-109 (기존 데이터 빈 태그 해석) | T008, T009, T020 |
| FR-110 (항상 표시, `tags:[]`) | T015, T018 |
| US1 AC1~AC5 | T012, T014 |
| US2 AC1~AC4 | T015, T016, T018 |
| SC-101 (95%/1초 add) | 기존 `test_performance.py` (변경 없음) |
| SC-102 (95%/1초 `list --tag`, 100/5) | T020a (신규 perf 케이스, 정확도 5/5 단언 포함) |
| SC-103 (회귀 0건) | T001, T019, Phase 5 전체 |
| SC-104 (기존 파일 호환) | T008, T009, T020 |
| Edge: 정규화/빈/문자/기존 데이터/다중 태그 매칭 | T004, T008, T012, T016, T020 |

---

## MVP 제안

T001~T011(Phase 1·2)을 완료해 도메인·저장소·서비스가 안정된 후 **Phase 3(US1)을 먼저 머지하면 사용자에게 "태그 부여" 기능만으로도 가치가 전달**된다(회귀 0). 이후 Phase 4(US2)·Phase 5를 차례로 통합.

---

## 검증 결과 (Phase 5 완료 후 기록)

- 회귀 베이스라인 (Phase 1):
  - `pytest -q`: 56 passed, 1 skipped
  - `ruff check .`: All checks passed
  - `ruff format --check .`: 23 files already formatted
- 최종 (Phase 5 완료):
  - `pytest -q`: **131 passed, 1 skipped** (기존 56 + 신규 75)
  - `ruff check .`: All checks passed (0 issues)
  - `ruff format --check .`: 26 files already formatted
  - 후방 호환 스모크 (T020): PASS — 태그 필드 없는 legacy `todo.json`에서 list/complete/delete 정상, 다음 쓰기 시 `"tags": []` 자동 추가
  - SC-102 perf (T020a): PASS — 100개 항목 중 5개 매칭 `list --tag urgent`의 95퍼센타일 < 1초, 정확도 5/5
  - 스모크 (CLI 진입점): PASS — `todo add ... --tag work --tag 2026Q2`, `todo list --tag work`, `todo list` 모두 정상
