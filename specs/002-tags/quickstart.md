# Quickstart: 002-tags 태그 부여 및 필터

## 사전 조건

- 001-todo-cli가 main에 머지되어 있고 `specs/001-todo-cli/python-scaffold/`에 정상 작동하는 ToDo CLI가 설치되어 있다.
- `pip install -e ".[dev]"`로 개발 의존성 설치 완료.

## 1) 태그를 부여해 항목 추가

```powershell
todo add "보고서 작성" --due 2026-06-01 --priority high --tag work --tag 2026Q2
# Created ID 1
```

- `--tag`는 반복 지정 가능 (최대 5개).
- 같은 태그를 두 번 지정해도 정규화 후 1개로 합쳐진다 (`--tag Work --tag work` → `work`).
- 태그를 지정하지 않으면 기존과 동일하게 항목이 생성된다 (`tags:[]`).

## 2) 태그 표시 확인

```powershell
todo list
# 1. [ ] 보고서 작성 (priority:high, due:2026-06-01) tags:[2026q2,work]
```

태그는 사전식 오름차순으로 정렬되어 항상 표시된다.

## 3) 태그로 필터링

```powershell
todo list --tag work
# 1. [ ] 보고서 작성 (priority:high, due:2026-06-01) tags:[2026q2,work]

todo list --tag urgent
# (항목이 없습니다)
```

## 4) 다른 필터와 결합

```powershell
todo complete 1
todo list --tag work --completed
# 1. [x] 보고서 작성 (priority:high, due:2026-06-01) tags:[2026q2,work]
```

`--tag`는 `--completed`/`--pending`/`--priority`와 AND 결합으로 동작한다.

## 5) 검증 규칙 확인

```powershell
# 빈 태그 → 거부
todo add "x" --tag ""
# 오류: 태그는 비어 있을 수 없습니다

# 21자 이상 → 거부
todo add "x" --tag aaaaaaaaaaaaaaaaaaaaa
# 오류: 태그 길이는 1~20자여야 합니다 (입력: 'aaaaaaaaaaaaaaaaaaaaa')

# 6개 이상 → 거부
todo add "x" --tag a --tag b --tag c --tag d --tag e --tag f
# 오류: 태그는 최대 5개까지 허용됩니다 (입력: 6개)

# 금지 문자 → 거부
todo add "x" --tag "no spaces"
# 오류: 태그에 허용되지 않는 문자가 포함되었습니다 (입력: 'no spaces')
```

## 6) 기존 데이터(태그 필드 없음) 호환 확인

본 기능 도입 이전의 `todo.json`이 있다면 추가 작업 없이 사용 가능하다.

```powershell
todo --db .\old-todo.json list
# 기존 항목들이 모두 tags:[]로 표시되며 정상 출력
```

다음 추가/완료/삭제 시 파일이 재기록될 때 모든 항목에 `"tags": []` 키가 자동으로 추가된다.

## 7) Unicode 정규화 확인 (개발자 검증용)

```powershell
# NFKC 정규화로 결합 문자/완성형이 동일 태그가 됨
todo add "테스트1" --tag café       # NFC 합성형
todo add "테스트2" --tag cafe´       # NFD 결합형 (입력 환경에 따라)
todo list --tag café
# 두 항목 모두 매칭됨
```

## 검증 체크리스트

- [ ] `pytest -q` → 56 (기존) + 신규 테스트 모두 통과
- [ ] `ruff check . && ruff format --check .` → 0 issues
- [ ] 기존 `todo.json`(태그 필드 없음)을 새 코드로 읽기 후 `list`/`complete`/`delete` 모두 정상
- [ ] 6개 태그·21자·빈 태그·금지문자 모두 stderr 메시지로 거부
- [ ] `todo list` 출력의 모든 항목에 `tags:[...]` 표시
