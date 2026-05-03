# ToDo CLI — 실행 가능한 태스크 목록

다음 태스크들은 `specs/001-todo-cli/plan.md`를 기반으로 분해한 커밋 단위 작업들입니다. 각 항목은 하나의 커밋으로 적용 가능해야 합니다. 병렬 실행 가능한 작업에는 `[P]` 마커가 붙어 있습니다.

**파일/경로 표기법**: 각 태스크 설명 끝에 구현할 파일 경로를 명시합니다.

Phase 1 — Setup
- [ ] T001 [P] 생성: 프로젝트 디렉터리 및 기본 폴더 구조 생성 (`specs/001-todo-cli/python-scaffold/src/`, `specs/001-todo-cli/python-scaffold/tests/unit/`, `docs/`) — 파일/디렉토리 생성
- [ ] T002 생성: `pyproject.toml` 초기화 및 개발 의존성 추가 (`specs/001-todo-cli/python-scaffold/pyproject.toml`) — 파일 추가/편집
- [ ] T003 생성: `.gitignore` 및 기본 CI 템플릿 복사 (`.gitignore`, `.github/workflows/ci.yml`) — 파일 추가

Phase 2 — Foundational (blocking)
- [ ] T004 데이터모델 테스트 작성: `ToDoItem` 데이터 모델 단위 테스트 추가 (`specs/001-todo-cli/python-scaffold/tests/unit/test_models.py`) — 테스트 추가
- [ ] T005 데이터모델 구현: `ToDoItem` 모델 구현 (`specs/001-todo-cli/python-scaffold/todo_lib/models.py`) — 코드 추가/수정
- [ ] T006 [P] 저장소 추상화 테스트 작성: 스토리지 인터페이스 단위 테스트 추가 (`specs/001-todo-cli/python-scaffold/tests/unit/test_storage.py`) — 테스트 추가
- [ ] T007 [P] 저장소 구현 (JSON): JSON 저장소 구현 및 테스트 통과 (`specs/001-todo-cli/python-scaffold/todo_lib/storage_json.py`, `specs/001-todo-cli/python-scaffold/todo_lib/storage.py`) — 코드 추가
- [ ] T008 서비스 계층 테스트 작성: 서비스 인터페이스(추가/조회/완료/삭제) 단위 테스트 추가 (`specs/001-todo-cli/python-scaffold/tests/unit/test_service.py`) — 테스트 추가
- [ ] T009 서비스 계층 구현: `TodoService` 구현 및 테스트 통과 (`specs/001-todo-cli/python-scaffold/todo_lib/service.py`) — 코드 추가/수정

Phase 3 — User Story P1 (MVP: add, list)
- [ ] T010 [US1] `add` 명세 테스트 작성 (실패하는 테스트 먼저) (`specs/001-todo-cli/python-scaffold/tests/integration/test_cli_add.py`) — 테스트 추가
- [ ] T011 [P] [US1] `cli add` 구현 및 단위/통합 테스트 통과 (`specs/001-todo-cli/python-scaffold/cli/main.py`) — 코드 수정
- [ ] T012 [US1] `list` 명세 테스트 작성 (필터·우선순위 포함) (`specs/001-todo-cli/python-scaffold/tests/integration/test_cli_list.py`) — 테스트 추가
- [ ] T013 [P] [US1] `cli list` 구현 및 통합 테스트 통과 (`specs/001-todo-cli/python-scaffold/cli/main.py`) — 코드 수정

Phase 4 — User Story P2 (complete, delete)
- [ ] T014 [US2] `complete` 명세 테스트 작성 (정상·존재하지 않는 ID 케이스) (`specs/001-todo-cli/python-scaffold/tests/integration/test_cli_complete.py`) — 테스트 추가
- [ ] T015 [P] [US2] `cli complete` 구현 및 테스트 통과 (`specs/001-todo-cli/python-scaffold/cli/main.py`) — 코드 수정
- [ ] T016 [US2] `delete` 명세 테스트 작성 (정상·존재하지 않는 ID 케이스) (`specs/001-todo-cli/python-scaffold/tests/integration/test_cli_delete.py`) — 테스트 추가
- [ ] T017 [P] [US2] `cli delete` 구현 및 테스트 통과 (`specs/001-todo-cli/python-scaffold/cli/main.py`) — 코드 수정

Phase 5 — Polish & Cross-cutting
- [ ] T018 문서화: `README.md` 업데이트(빠른 시작, 예시 명령, CI 배지) (`specs/001-todo-cli/python-scaffold/README.md`) — 문서 수정
- [ ] T019 린트·포맷: `pyproject.toml`에 포맷터/린터 설정 추가 및 자동 포맷 실행 (`.github/workflows/ci.yml`, `pyproject.toml`) — 구성 수정
- [ ] T020 패키징·릴리스: 패키지 메타데이터 정리 및 배포 스크립트 추가 (`specs/001-todo-cli/python-scaffold/pyproject.toml`, `scripts/release.sh`) — 파일 추가

Dependencies (스토리·태스크 순서)
- Phase 1 -> Phase 2 -> Phase 3 (US1) -> Phase 4 (US2) -> Phase 5
- `T006`(스토리지 테스트)과 `T007`(JSON 저장소 구현)은 병렬로 진행 가능합니다.
- `T011`(cli add) 와 `T013`(cli list)은 동일 서비스 인터페이스를 사용하기 때문에 `T009`(서비스 구현) 이후에 병렬로 구현할 수 있습니다. 따라서 구현 순서는: T009 → (T011, T013)

병렬 실행 예시
- 팀원 A: `T007` (JSON 저장소 구현) 진행 — `specs/001-todo-cli/python-scaffold/todo_lib/storage_json.py`
- 팀원 B: `T011` (`cli add` 구현) 진행 — `specs/001-todo-cli/python-scaffold/cli/main.py`
- 팀원 C: `T013` (`cli list` 구현) 진행 — `specs/001-todo-cli/python-scaffold/cli/main.py`

독립 검증 기준 (각 User Story)
- US1 (add/list): `tests/integration/test_cli_add.py`, `tests/integration/test_cli_list.py`가 모두 통과하고, `pytest --maxfail=1` 기준에서 성공해야 함.
- US2 (complete/delete): `tests/integration/test_cli_complete.py`, `tests/integration/test_cli_delete.py`가 모두 통과해야 함.

MVP 제안
- 우선 `T004`~`T009`(데이터모델·스토리지·서비스 단위 테스트 및 구현)을 완료하여 안정적인 서비스 계층을 확보한 뒤 `T010`~`T013`(US1)을 먼저 완료합니다. 이후 `T014`~`T017`(US2)을 구현합니다.

추가 메모
- 병렬표시 `[P]`는 서로 다른 파일/모듈에 대한 변경으로 서로 충돌 가능성이 낮은 작업에만 붙였습니다.
- 각 태스크 설명의 파일 경로는 작업 커밋에 포함될 주된 변경 대상입니다. 실제 파일명이 다를 경우 커밋 메시지에 변경 파일을 명시하세요.
