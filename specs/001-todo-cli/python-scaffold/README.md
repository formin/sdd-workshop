# ToDo CLI (Python)

로컬 JSON 파일을 저장소로 사용하는 단일 사용자 ToDo CLI 도구.

- 스펙: [`../spec.md`](../spec.md)
- 계획: [`../plan.md`](../plan.md)
- 태스크: [`../tasks.md`](../tasks.md)

## 배지

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

> 위 배지의 `OWNER/REPO`는 실제 GitHub 소유자/저장소로 교체하세요.

## 빠른 시작

### 설치

```powershell
cd specs/001-todo-cli/python-scaffold
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 사용 예시

```powershell
# 항목 추가
todo add "보고서 작성" --due 2026-06-01 --priority high

# 전체 목록
todo list

# 미완료만 보기
todo list --pending

# 우선순위 필터
todo list --priority high

# 항목 완료
todo complete 1

# 항목 삭제
todo delete 1
```

저장 파일은 기본 `todo.json`이며 `--db <경로>` 옵션으로 변경할 수 있습니다.

## 테스트

```powershell
pytest -q                  # 전체 테스트
ruff check .               # lint
ruff format --check .      # format 검증
```

## 구조

```text
src/
├── cli/main.py              # argparse 진입점 (서브커맨드)
├── services/
│   ├── models.py            # ToDoItem dataclass
│   ├── due_date.py          # ISO-8601 → UTC 정규화
│   └── todo_service.py      # 비즈니스 규칙
└── storage/
    ├── base.py              # Storage 추상 + StorageError
    └── json_store.py        # JSON 구현체
tests/
├── unit/                    # 모델·서비스·저장소·시간대 단위 테스트
└── integration/             # CLI 통합·도움말·성능 테스트
```

CI: GitHub Actions(`.github/workflows/ci.yml`) — Python 3.11, ruff lint/format, pytest.
