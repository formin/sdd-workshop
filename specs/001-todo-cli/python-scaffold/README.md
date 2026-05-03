# ToDo CLI (Python) 스캐폴드

이 폴더는 `specs/001-todo-cli`용 Python 구현 스캐폴드입니다. 목표는 다음과 같습니다:

- 언어: Python 3.12
- 패키지 관리: `pyproject.toml` (uv 권장 흐름에 맞춰 나중에 조정)
- 런타임 의존성: `typer`, `sqlalchemy`
- 개발 의존성: `pytest`, `pytest-cov`
- 레이어: `todo_lib/`(비즈니스), `cli/`(Typer 기반), `tests/`

빠른 시작

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest --cov=todo_lib tests/
```

DB 초기화

```powershell
# DB 파일과 테이블을 생성
python -m cli.main init-db --db ./todo.db
```

통합 테스트

```powershell
& '.venv\Scripts\python.exe' -m pytest tests/test_cli_integration.py -q
```
