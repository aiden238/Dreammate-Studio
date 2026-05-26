# eval_log.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 140
last_updated: 2026-05-26
```

## Why Placeholder?

golden_set 회귀 실행 및 Critic 점수 추이가 쌓이기 전까지 eval 로그 형식과
첫 엔트리를 확정할 수 없다. Phase 1 + 첫 golden_set 회귀 실행 이후 작성한다.

## Scope (TBD)

본 파일이 다룰 범위:
- golden_set 회귀 테스트 결과 누적 로그 (실행 날짜, 통과율, 실패 케이스)
- Critic 점수 추이 (중앙값, 최소/최대, 기준값 대비 변화)
- 사용자 만족도 수치 누적 (NPS 또는 별점 평균, 수집 주기별)
- eval 실행 환경 기록 (모델 버전, prompt 버전, 데이터셋 버전)
- 실패 케이스 분류 (failure_taxonomy.md 연계 태그)
- 회귀 통과/실패 판정 기준 및 판정 결과 기록
- eval-run Skill 실행 출력 요약 자동 추가 절차

## Known Dependencies (when filled in)

- `eval/regression_eval.md` — 회귀 평가 기준
- `eval/golden_set.md` — 평가 케이스 원천
- `eval/failure_taxonomy.md` — 실패 분류 태그
- `eval/human_review_rubric.md` — 인간 검토 기준
- `eval-run` Skill — eval 자동 실행 훅
- `logs/log_index.md` — 로그 인덱스 업데이트
- prompt_registry.md 버전 태그 (eval 실행 시 버전 기록 필수)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 + golden_set 10케이스 이상 활성화
- eval-run Skill로 첫 회귀 실행 완료

## 예시 엔트리 형식 (fill-in 시 참고)

```markdown
## EVAL-20260610-001

- **날짜**: 2026-06-10
- **Phase**: 1
- **트리거**: prompt_registry v0.3.0 → v0.4.0 변경
- **golden_set 버전**: gs-v1.2
- **모델**: claude-sonnet-4-6
- **결과**: 통과 18/20 (90%) | 실패 2/20
- **Critic 중앙값**: 7.8 (기준 7.5 이상 → 통과)
- **실패 케이스**: GS-003 (hook_quality 미흡), GS-017 (brand_fit 불일치)
- **실패 분류**: F-HOOK-001, F-BRAND-002
- **판정**: 통과 (회귀 기준 80% 이상 충족)
- **조치**: GS-003 원인 분석 후 다음 prompt 버전에 반영
```

## Related Skill / Phase

- Skill: eval-run, eval-design
- Phase: 1+
- 책임자: AI / 운영자
