# CLI 명령 계약: 002-tags

본 문서는 002-tags 사이클이 변경하거나 새로 노출하는 CLI 표면을 형식적으로 명세한다. 통합 테스트 단언의 권위 출처다.

## `todo add` (확장)

### 시그니처

```text
todo [--db <path>] add <title> [--due <iso8601>] [--priority {low,medium,high}] [--tag <name> ...]
```

| 옵션 | 누적 | 타입 | 기본값 | 비고 |
|---|---|---|---|---|
| `<title>` | — | str | (필수) | 빈 문자열 거부 (기존) |
| `--due` | 1 | str (ISO-8601) | None | 기존 |
| `--priority` | 1 | choice | None | 기존 |
| **`--tag`** | **N (반복)** | **str** | **없음 → 빈 집합** | **신규** |

### 동작

1. `--tag` 옵션 값은 입력 순서대로 모두 수집된다(argparse `action="append"`).
2. 수집된 원시 태그 리스트는 `services.tags.validate_tags`로 정규화·검증된다.
3. 검증 통과 시 `TodoService.add(title, due, priority, tags=frozenset(...))`가 호출되고 ID가 부여된 항목이 저장된다.

### 표준 출력

성공 시:
```
Created ID <id>
```

(현재 출력 형식 유지 — 태그는 즉시 표시하지 않는다. 확인은 `todo list`로.)

### 종료 코드

| 종료 코드 | 의미 | 트리거 |
|---|---|---|
| 0 | 성공 | 정상 추가 |
| 2 | 도메인 검증 실패 | 빈 제목, 잘못된 우선순위, **태그 한도 초과(>5), 태그 길이 초과(>20), 빈 태그, 금지 문자** |
| (argparse 자체 실패) | 사용 오류 | 알 수 없는 옵션, `--priority` 비허용 값 등 |

### 오류 메시지 (stderr)

- 태그 5개 초과: `오류: 태그는 최대 5개까지 허용됩니다 (입력: <n>개)`
- 태그 길이: `오류: 태그 길이는 1~20자여야 합니다 (입력: '<value>')`
- 빈/공백 태그: `오류: 태그는 비어 있을 수 없습니다`
- 금지 문자: `오류: 태그에 허용되지 않는 문자가 포함되었습니다 (입력: '<value>')`

## `todo list` (확장)

### 시그니처

```text
todo [--db <path>] list [--completed | --pending] [--priority {low,medium,high}] [--tag <name>]
```

| 옵션 | 누적 | 타입 | 기본값 | 비고 |
|---|---|---|---|---|
| `--completed` | 1 | flag | False | 기존, `--pending`과 상호배제 |
| `--pending` | 1 | flag | False | 기존 |
| `--priority` | 1 | choice | None | 기존 |
| **`--tag`** | **1 (마지막값)** | **str** | **None** | **신규 — 단일 태그 정확 일치** |

### 동작

1. `--tag` 값이 주어지면 `services.tags.normalize_tag`로 정규화 후 비교 키로 사용.
2. 항목 필터링은 다음 순서로 AND 결합: 완료 상태 → 우선순위 → 태그 포함 여부.
3. 결과 항목들을 ID 오름차순으로 출력한다.

### 표준 출력 형식 (FR-110)

각 라인:
```
<id>. [ |x] <title> (priority:<p>, due:<d>) tags:[<t1,t2,...>]
```

- `tags:[...]`는 **항상 표시**되며 빈 경우 `tags:[]`로 출력.
- 태그 사이는 콤마(공백 없음). 사전식 오름차순 정렬.
- 항목 0개일 때:
  ```
  (항목이 없습니다)
  ```

### 종료 코드

| 종료 코드 | 의미 |
|---|---|
| 0 | 성공 (빈 결과 포함) |
| 2 | 잘못된 `--tag` 값 (정규화 후 빈 문자열 등) |

## 변경 없는 명령

- `todo complete <id>` — 변경 없음. 통합 테스트 단언만 출력 라인의 `tags:[...]` 부분이 추가될 수 있어 회귀 검증 대상.
- `todo delete <id>` — 변경 없음.

## 도움말 (`--help`) 계약

`todo add --help` 출력에 다음 문구가 포함되어야 한다:
- `--tag` 옵션 행
- "최대 5개" 또는 동등한 한도 안내

`todo list --help` 출력에 다음 문구가 포함되어야 한다:
- `--tag` 옵션 행

## 후방 호환

`tags:[]` 출력이 추가되는 점이 기존 통합 테스트(예: `todo list` 후 `"CLI item" in r.output` 류 단언)에 영향을 주지 않는지 검증한다. 영향 시 부분 문자열 단언으로 보강한다 — 단, 기존 main 회귀 0건 목표 유지.

## 예시 흐름

```text
$ todo add "보고서 작성" --due 2026-06-01 --priority high --tag work --tag 2026Q2
Created ID 1

$ todo list
1. [ ] 보고서 작성 (priority:high, due:2026-06-01) tags:[2026q2,work]

$ todo list --tag work
1. [ ] 보고서 작성 (priority:high, due:2026-06-01) tags:[2026q2,work]

$ todo list --tag missing
(항목이 없습니다)

$ todo add "잡일" --tag work --tag work
Created ID 2

$ todo list --tag work
1. [ ] 보고서 작성 (priority:high, due:2026-06-01) tags:[2026q2,work]
2. [ ] 잡일 (priority:-, due:-) tags:[work]
```
