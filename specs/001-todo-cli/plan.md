# Implementation Plan: ToDo CLI

**Branch**: `001-todo-cli` | **Date**: 2026-05-02 | **Spec**: [specs/001-todo-cli/spec.md](specs/001-todo-cli/spec.md)

## Summary

간단한 로컬 CLI 기반 ToDo 관리 툴을 빠르게 제공하는 것을 목표로 한다. 핵심 기능은 항목 추가, 목록 조회(필터 포함), 항목 완료, 항목 삭제로 한정하며, 초기 구현은 로컬 저장(파일 또는 SQLite) 기반으로 단일 사용자 환경을 전제한다.

## Technical Context

- **언어/버전**: 미정 (권장: Python 3.11 — 간단한 CLI와 테스트 환경 구성 및 빠른 프로토타입에 적합)
- **Primary Dependencies**: 최소화 (표준 라이브러리 우선). 권장: `argparse`/`click` 중 하나(선택 시 추가), `pytest`(테스트)
- **Storage**: 초기: JSON 파일 또는 SQLite (결정 필요)
- **Testing**: `pytest` 기반 단위/통합 테스트
- **Target Platform**: 로컬 개발자 머신 (Windows, macOS, Linux)
- **Project Type**: CLI application

## Constitution Check

- **범위 확인 (CLI 전용)**: PASS — 스펙은 CLI 전용.
- **테스트 우선(TDD)**: REQUIRED — 모든 P1 흐름에 대해 실패하는 테스트를 먼저 작성.
- **최소 의존성 검토**: REQUIRED — 외부 패키지는 근거 문서화.
- **레이어 분리 확인**: REQUIRED — `cli/` → `services/` → `storage/` 구조를 유지.

미충족 항목(예: storage 선택)은 Phase 0에서 결정하고 Plan에 반영한다.

## Project Structure

```text
src/
├── cli/           # 명령어 파서 및 진입점
├── services/      # 비즈니스 로직
└── storage/       # 저장소 추상화 (json/sqlite 구현체)

tests/
├── unit/
└── integration/

docs/
``` 

## Phase Breakdown

1. Phase 1 — Setup (P0)
   - T1: 저장소 및 가상환경 초기화
   - T2: 프로젝트 구조 생성 (`src/cli`, `src/services`, `src/storage`, `tests/`)
   - T3: CI 워크플로 연동(이미 존재) 확인

2. Phase 2 — Foundational (blocking)
   - T4: `ToDoItem` 데이터 모델 정의 및 테스트(단위)
   - T5: `storage` 추상화 인터페이스 + JSON 구현(테스트 포함)
   - T6: 서비스 계층 인터페이스(추가/조회/완료/삭제) 및 단위 테스트

3. Phase 3 — User Story P1 (MVP)
   - T7: `cli add` 구현 (테스트 먼저)
   - T8: `cli list` 구현 (필터 테스트 포함)

4. Phase 4 — User Story P2
   - T9: `cli complete` 구현 (테스트)
   - T10: `cli delete` 구현 (테스트)

5. Phase 5 — Polish & Release
   - T11: 사용성(명령어 도움말) 문서화
   - T12: 린트/포맷 적용
   - T13: README 및 quickstart 추가

## Complexity & Decisions

- 스토리지 선택(파일 vs SQLite): 초기에는 JSON 파일로 빠르게 시작하고, 필요시 SQLite로 교체하는 방안을 권장.
- CLI 라이브러리: `argparse`로 충분하지만, 커맨드 확장성과 사용자 편의성을 고려하면 `click` 권장(의존성 검토 필수).

## Deliverables

- `specs/001-todo-cli/plan.md` (본 파일)
- 구현 브랜치: `001-todo-cli`
- 기본 테스트 스위트: `pytest`를 통해 모든 기능의 회귀 검사

## Next Steps (권장)

1. 결정: 저장 방식 선택(JSON 초안 권장) — `/speckit.clarify`로 확정하거나 제가 자동으로 JSON 선택하여 Plan에 반영할까요?
2. 작업: Phase 1~2의 T4~T6 테스트 파일을 먼저 작성(TDD) 후 구현 시작.
