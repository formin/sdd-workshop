# ToDo CLI (Go) - Implementation (scaffold)

이 폴더는 `specs/001-todo-cli`용 Go 기반 스캐폴딩입니다.

구성요소:
- `cmd/todo` - 진입점 및 명령 정의 (cobra 사용 예상)
- `internal/todo` - 도메인 모델 및 서비스
- `internal/storage` - 저장소 추상화 및 JSON 파일 기본 구현

빠른 시작:

```bash
cd specs/001-todo-cli/implementation
go build ./cmd/todo
./todo add "샘플 작업" --due 2026-06-01 --priority high
./todo list
```

향후 작업:
- SQLite 저장소 구현 및 마이그레이션
- 단위/통합 테스트 추가
- `cobra` 의존성 초기화 (go get)

SQLite 사용 안내:

1. sqlite 드라이버 설치(빌드 시 자동으로 가져오지만, 명시적으로 추가하려면):

```bash
go get github.com/mattn/go-sqlite3
```

2. `SQLite` 저장소로 실행 예시:

```bash
# 빌드
go build -o todo.exe ./cmd/todo

# 예: SQLite DB 파일을 직접 사용하는 간단한 실행(향후 플래그로 경로 지정 가능)
./todo.exe list
```

주의: `github.com/mattn/go-sqlite3`는 cgo를 사용하므로 시스템에 C 빌드 도구가 필요할 수 있습니다.
