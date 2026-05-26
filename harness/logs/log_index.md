# log_index.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 100
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1 운영 시작 전까지 로그 파일이 누적되지 않아 인덱스 항목을 확정할 수 없다.
첫 로그 파일이 누적되는 시점에 인덱스 구조를 정립하고 작성한다.

## Scope (TBD)

본 파일이 다룰 범위:
- 전체 logs/ 디렉토리 내 파일 목록 및 역할 설명
- 카테고리별 분류: decision / eval / handoff / security / general
- 각 로그 파일의 최신 엔트리 날짜 및 엔트리 수 요약
- 로그 검색 방법 (파일명 규칙, 날짜 포맷, 카테고리 태그)
- 로그 보존 정책 (보존 기간, 압축/아카이브 기준)
- 로그 추가 절차 (새 카테고리 추가 시 본 인덱스 업데이트 필수)

## Known Dependencies (when filled in)

- `logs/decision_log.md` — 의사결정 로그
- `logs/eval_log.md` — eval 실행 결과 로그
- `logs/handoff_log.md` — context-compact Skill 출력 누적
- 향후 추가될 로그 파일 (security_log.md 등)
- `meta/lessons_learned.md` — 교훈 누적 (로그 → 교훈 흐름)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 운영 시작 시점 (첫 배포 완료)
- logs/ 디렉토리 내 최소 3개 파일에 실제 엔트리 누적

## 예시 인덱스 형식 (fill-in 시 참고)

```
| 파일                   | 카테고리 | 최신 엔트리    | 총 엔트리 수 | 설명                      |
|------------------------|----------|----------------|--------------|---------------------------|
| logs/decision_log.md   | decision | 2026-06-01     | 12           | 일상 의사결정 누적 로그    |
| logs/eval_log.md       | eval     | 2026-06-05     | 8            | golden_set 회귀 결과 로그  |
| logs/handoff_log.md    | handoff  | 2026-06-10     | 5            | context-compact 출력 인덱스|
```

## Related Skill / Phase

- Skill: context-compact, harness-audit
- Phase: 1+
- 책임자: 운영자 / AI
