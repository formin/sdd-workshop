# Feature Specification: ToDo CLI

**Feature Branch**: `001-todo-cli`  
**Created**: 2026-05-02  
**Status**: Draft  
**Input**: User description: "CLI 기반의 ToDo 관리 앱을 만들고 싶어요. 사용자: 터미널을 사용하는 개인 개발자. 주요 기능: 1) ToDo 항목 추가: 제목(필수), 마감일(선택), 우선순위(선택) 2) 전체 목록 조회: 완료/미완료/우선순위로 필터링 가능 3) 항목 완료 처리: 항목 ID로 완료 표시 4) 항목 삭제: 항목 ID로 삭제. 기술스택: Go (권장)"

> **Note**: 위 "Input"은 사용자가 처음 제출한 원문으로 보존됩니다. 현재 확정된 기술스택·아키텍처는 [`plan.md`](./plan.md)(Python 3.11 + pytest + JSON 저장소)가 권위 있는 출처입니다. 원문의 "기술스택: Go (권장)"은 더 이상 유효하지 않습니다.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 항목 추가 (Priority: P1)

터미널에서 사용자는 새로운 ToDo 항목을 추가할 수 있다. 항목은 제목(필수), 마감일(선택), 우선순위(선택)를 포함한다.

**Why this priority**: 핵심 기능이며 다른 모든 흐름의 전제이다.

**Independent Test**: CLI 명령을 실행하여 새 항목을 추가하고, 목록 조회에서 해당 항목이 존재함을 확인한다.

**Acceptance Scenarios**:
1. **Given** 빈 목록, **When** `todo add "제목" --due 2026-06-01 --priority high`, **Then** 새 항목이 생성되고 ID가 반환된다.
2. **Given** 제목이 비어있음, **When** `todo add ""`, **Then** 오류 메시지가 출력되고 항목은 생성되지 않는다.

---

### User Story 2 - 전체 목록 조회 및 필터 (Priority: P1)

사용자는 전체 목록을 조회하고 `--completed/--pending` 또는 `--priority high` 등으로 필터링할 수 있다.

**Why this priority**: 사용자가 항목을 확인·관리하는 기본 인터페이스.

**Independent Test**: 여러 항목을 추가한 후 필터 옵션을 사용해 결과가 기대대로 반환되는지 확인.

**Acceptance Scenarios**:
1. **Given** 다수의 항목(완료/미완료 혼재), **When** `todo list --completed`, **Then** 완료된 항목만 나열된다.
2. **Given** 다수의 항목, **When** `todo list --priority high`, **Then** 우선순위가 high인 항목만 나열된다.

---

### User Story 3 - 항목 완료 처리 (Priority: P2)

사용자는 항목 ID로 항목을 완료 표시할 수 있다.

**Why this priority**: 목록 관리 흐름의 연속성 제공.

**Independent Test**: 항목을 추가한 뒤 `todo complete <id>`를 호출하면 상태가 완료로 변경되는지 확인.

**Acceptance Scenarios**:
1. **Given** 항목 ID가 존재함, **When** `todo complete 3`, **Then** 항목 3이 완료 상태로 표시된다.
2. **Given** 존재하지 않는 ID, **When** `todo complete 999`, **Then** 적절한 오류 메시지가 출력된다.

---

### User Story 4 - 항목 삭제 (Priority: P2)

사용자는 항목 ID로 항목을 삭제할 수 있다.

**Independent Test**: 항목을 추가한 뒤 `todo delete <id>` 호출하면 목록에서 제거되는지 확인.

**Acceptance Scenarios**:
1. **Given** 항목 ID가 존재함, **When** `todo delete 2`, **Then** 항목이 삭제되고 확인 메시지가 출력된다.
2. **Given** 존재하지 않는 ID, **When** `todo delete 999`, **Then** 적절한 오류 메시지가 출력되고 다른 항목은 영향을 받지 않는다.

---

### Edge Cases

- 시스템 시간대가 다른 환경에서 마감일 파싱 오류가 발생할 수 있음.
- 동일한 제목의 항목이 여러 개인 경우 ID 기반으로 정확히 참조되어야 함.
- 로컬 저장소(파일) 권한 문제 발생 시 친절한 오류 메시지 제공.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `todo add` 명령으로 항목을 추가할 수 있어야 한다 (제목 필수, 마감일/우선순위 선택).
- **FR-002**: 시스템은 `todo list` 명령으로 모든 항목을 나열할 수 있어야 하며, `--completed`, `--pending`, `--priority` 필터를 지원해야 한다.
- **FR-003**: 시스템은 `todo complete <id>` 명령으로 항목을 완료로 표시할 수 있어야 한다.
- **FR-004**: 시스템은 `todo delete <id>` 명령으로 항목을 삭제할 수 있어야 한다.
- **FR-005**: 모든 입력/출력은 터미널(표준 입출력)을 통해 수행되어야 하며, REST API나 GUI는 범위 밖이다.

### Key Entities

- **ToDoItem**: 항목을 나타냄. 주요 속성: `id`(정수), `title`(문자열), `due_date`(옵션, ISO 날짜), `priority`(옵션: low/medium/high), `completed`(불리언), `created_at`(타임스탬프)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자가 `todo add` 명령으로 항목을 추가하면 95% 사례에서 1초 이내에 항목이 등록되어야 한다.
- **SC-002**: `todo list` 필터 기능은 테스트 케이스의 100%를 성공적으로 통과해야 한다.
- **SC-003**: CLI 사용성 테스트에서 90% 이상의 사용자가 기본 작업(추가/조회/완료/삭제)을 문제없이 수행할 수 있어야 한다.

## Assumptions

- 이 기능은 개인 개발자가 로컬에서 사용하는 CLI 도구로 설계한다(네트워크 동기화는 범위 외).
- 기본 영구 저장소는 로컬 파일(예: JSON 또는 SQLite)로 시작하되, 구현 시 결정한다.
- 개발 초기에는 단일 사용자 환경을 가정한다.

## Implementation Notes (권장)

- 아키텍처: `cli/` 핸들러 → `services/` 도메인 로직 → `storage/` 추상화 계층(파일 또는 SQLite). 레이어 분리를 준수.
- 테스트: `tests/` 아래 단위 테스트와 통합 테스트를 먼저 작성하여 TDD 흐름을 따른다.
- 의존성: 외부 패키지 도입은 최소화; 필요한 경우 `pyproject.toml`(또는 대응 매니페스트)에 이유를 기록한다.
