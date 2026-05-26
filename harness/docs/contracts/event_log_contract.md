# event_log_contract.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 4+
priority: medium
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 0~3은 핵심 흐름 + 인프라 작업 중심. Phase 4(eval 확장) 또는 첫 사용자 행동 분석 시작 시점에 이벤트 스키마를 표준화한다. 그 전까지는 `db_schema.md`의 `feedback_events`, `discovery_choices`, `intent_filter_logs` 잠정 정의로 충분.

## Scope (TBD)

본 contract가 다룰 범위:

- 사용자 행동 이벤트 표준 스키마 (request_id, user_id, project_id, model, tokens, latency, error_type, quality_score)
- 이벤트 카테고리 분류 (click / view / save / feedback / regenerate / reject)
- agent_io_logs와 별도 이벤트 테이블 분리 정책
- 익명화 정책 (user_id hash, IP 마스킹)
- 이벤트 파이프라인 (DB → 분석 도구, Phase 11+)
- batch 적재 vs realtime 적재 (트래픽 규모에 따라)
- 분석용 인덱스 / 파티셔닝 정책
- A/B 테스트 그룹 표기 (experiment_id, variant)
- eval/regression_results와의 연동 (회귀 지표 자동 갱신)
- 이벤트 보존 기간 (data_retention_policy와 정합)
- 외부 분석 도구 연동 후보 (Mixpanel / Amplitude / 자체 ClickHouse)
- privacy: 분석 목적 동의 항목 (user_consent_contract와 정합)
- 옵트아웃 처리

## Known Dependencies (when filled in)

외부 표준:
- OpenTelemetry semantic conventions (events)
- W3C Trace Context (trace_id 형식)
- GA4 / Segment 표준 (참고용)

내부 의존 contract:
- `docs/contracts/db_schema.md` (`feedback_events`, `discovery_choices`, `choice_logs`)
- `docs/contracts/privacy_contract.md` (placeholder)
- `docs/contracts/data_retention_policy.md` (placeholder)
- `docs/contracts/agent_io_contract.md` §11 (agent_io_logs 기록 정책)
- `eval/regression_results/` (회귀 지표 출처)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 4+ 진입 (eval 확장 시작 시점)
- 또는 사용자 행동 분석 시작 시점
- 또는 A/B 테스트 첫 실행 시점

## Related Skill / Phase

- Skill: `eval-design`, `eval-run`
- Phase: 4+
- 책임자: AI(초안) + 사용자(검토)
