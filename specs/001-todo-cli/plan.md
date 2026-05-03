# Implementation Plan: ToDo CLI

**Branch**: `001-todo-cli` | **Date**: 2026-05-03 | **Spec**: [specs/001-todo-cli/spec.md](specs/001-todo-cli/spec.md)

## Summary

간단한 로컬 CLI 기반 ToDo 관리 툴을 빠르게 제공하는 것을 목표로 한다. 핵심 기능은 항목 추가, 목록 조회(필터 포함), 항목 완료, 항목 삭제로 한정하며, 초기 구현은 로컬 JSON 파일 저장 기반으로 단일 사용자 환경을 전제한다. 향후 필요 시 SQLite 구현체로 교체 가능하도록 storage 추상화를 둔다.

## Technical Context

- **언어/버전**: Python 3.11 — 표준 라이브러리만으로도 CLI·JSON·테스트 환경을 구성할 수 있고 빠른 프로토타입에 적합.
- **Primary Dependencies**: 표준 라이브러리(`argparse`, `json`, `dataclasses`, `pathlib`) 우선. 테스트는 `pytest`, 개발 품질은 `ruff`(lint+format). (CLI 라이브러리 `click`은 기본 미도입; 도입 시 `## Dependency Justification`에 근거 추가 필요.)
- **Storage**: 로컬 JSON 파일 (사용자 홈 디렉터리 또는 `--db` 옵션). SQLite는 향후 옵션.
- **Testing**: `pytest` 기반 단위(`tests/unit/`)·통합(`tests/integration/`) 테스트. CI에서 통과를 병합 조건으로 강제.
- **Target Platform**: 로컬 개발자 머신 (Windows, macOS, Linux).
- **Project Type**: CLI application (단일 프로젝트, 표준 입출력 인터페이스).

## Constitution Check

- **원칙 1 — 레이어 분리**: PASS — `cli/` → `services/` → `storage/` 3-레이어 유지, 서비스/도메인은 CLI 핸들러를 직접 호출하지 않는다.
- **원칙 2 — 테스트 우선 (NON-NEGOTIABLE)**: REQUIRED — 모든 기능 구현 전에 실패하는 테스트(RED)를 먼저 작성한다. CI는 테스트 통과를 병합 게이트로 강제한다.
- **원칙 3 — 최소 의존성**: PASS — 런타임 외부 의존성 없음(표준 라이브러리만). 개발 의존성은 `pytest`(테스트), `ruff`(lint+format)로 한정. 추가 의존성 도입 시 아래 `## Dependency Justification`에 근거를 기록한다.
- **원칙 4 — 단순함 우선**: PASS — JSON 단일 저장소로 시작, 인터페이스 추상화는 두지만 구현체는 1개로 한정. 패키징·릴리스 자동화 등 미증명 요구는 보류.
- **원칙 5 — CLI 도구 구현 (범위 제한)**: PASS — 표준 입출력만 사용, REST/GUI 없음.

## Project Structure

```text
specs/001-todo-cli/python-scaffold/
├── src/
│   ├── cli/            # 명령어 파서 및 진입점 (argparse 기반)
│   │   └── main.py
│   ├── services/       # 비즈니스 로직 (TodoService) + 도메인 모델/유틸
│   │   ├── models.py       # ToDoItem dataclass
│   │   ├── due_date.py     # ISO-8601 파싱·UTC 정규화
│   │   └── todo_service.py
│   └── storage/        # 저장소 추상화 + JSON 구현
│       ├── base.py     # Storage 인터페이스
│       └── json_store.py
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_due_date.py
│   │   ├── test_storage_contract.py
│   │   ├── test_storage_json.py
│   │   └── test_service.py
│   └── integration/
│       ├── test_cli_add.py
│       ├── test_cli_list.py
│       ├── test_cli_complete.py
│       └── test_cli_delete.py
├── pyproject.toml
└── README.md
```

`src/` 하위 패키지는 `services → storage`, `cli → services` 방향으로만 의존한다. 역방향 import 금지.

## Phase Breakdown

1. **Phase 1 — Setup (P0)**
   - 프로젝트 구조 및 `pyproject.toml` 초기화, CI 워크플로 연동 확인.
2. **Phase 2 — Foundational (blocking)**
   - `ToDoItem` 모델, `Storage` 추상화 + JSON 구현, `TodoService` 단위 테스트 및 구현.
   - 시간대 안전한 ISO-8601 마감일 파싱 단위 테스트 포함 (Edge Case 1).
   - JSON 파일 권한·I/O 오류 처리 단위 테스트 포함 (Edge Case 3).
3. **Phase 3 — User Story P1 (MVP)**
   - `cli add` (빈 제목 오류 포함), `cli list`(`--completed`/`--pending`/`--priority` 필터) 통합 테스트 및 구현.
4. **Phase 4 — User Story P2**
   - `cli complete <id>`, `cli delete <id>` (각각 비존재 ID 오류 케이스 포함) 통합 테스트 및 구현.
5. **Phase 5 — Polish**
   - SC-001(95% 사례 1초 이내) 검증용 성능 회귀 테스트, SC-003 buildable proxy로 `--help` 텍스트 검증, README/quickstart 문서, `ruff` lint+format 설정 및 CI에 `ruff check` 단계 통합.

## Dependency Justification

| 의존성 | 종류 | 근거 |
|--------|------|------|
| (런타임) 없음 | — | 표준 라이브러리만으로 CLI·JSON I/O·날짜 파싱·dataclass 기반 모델을 구현 가능. 헌법 원칙 3 충족. |
| `pytest` | 개발/테스트 | 테스트 우선(원칙 2) 강제를 위한 표준 도구. `unittest`보다 fixture/parametrize 표현력이 좋아 테스트 작성·유지 비용을 줄임. |
| `ruff` | 개발/품질 | 단일 바이너리로 lint(`flake8`/`pycodestyle`/`pyflakes` 호환)와 format(`black` 호환)을 모두 제공해 도구 수를 1개로 유지. 헌법 원칙 3·4 충족. |

추가 의존성(예: `click`)을 도입하려면 본 표에 행을 추가하고, 표준 라이브러리로 대체 불가한 사유를 기록한 뒤 PR 리뷰에서 승인받아야 한다.

## Complexity & Decisions

- **저장소 선택**: 초기 구현은 JSON 파일로 확정. SQLite는 향후 옵션이며 현 범위 밖.
- **CLI 라이브러리**: 표준 `argparse`로 확정. `click` 등 추가 라이브러리는 위 정당화 절차를 거쳐야 도입 가능.
- **ID 발급**: 단조 증가 정수(저장소가 부여). UUID는 단일 사용자·로컬 파일 환경에서 과한 추상화로 판단 (원칙 4).

## Deliverables

- `specs/001-todo-cli/plan.md` (본 파일)
- 구현 브랜치: `001-todo-cli`
- `specs/001-todo-cli/python-scaffold/` 하위에 동작하는 Python 패키지와 `pytest` 통합 테스트 스위트
- 모든 FR(FR-001~FR-005) 및 buildable SC(SC-001, SC-002)에 대응하는 자동화 테스트 (+ SC-003 buildable proxy via `--help` 텍스트 검증)

## Next Steps

1. `/speckit-tasks`로 본 plan에 정렬된 tasks.md 재생성 (이미 갱신됨).
2. `/speckit-implement`로 Phase 1부터 RED→GREEN→REFACTOR 흐름으로 진행.
