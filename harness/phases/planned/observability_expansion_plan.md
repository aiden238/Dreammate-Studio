# observability_expansion_plan.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 7+
priority: medium
estimated_final_lines: 150
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1-6은 Sentry 기본 오류 추적으로 충분하다. Phase 7 보안 진입 또는
사용자 1만 도달 시점에 OpenTelemetry → Grafana/Datadog 확장 계획을 상세화한다.

## Scope (TBD)

본 파일이 다룰 범위:
- Sentry → OpenTelemetry 기반 분산 추적 전환 계획
- Grafana / Datadog 대시보드 설계 (LLM 호출 추적, RAG 품질 모니터링)
- `meta/security_metrics.md` 연계 보안 메트릭 본격 운영
- 비용 모델 비교 (Grafana Cloud vs. Datadog vs. 자체 호스팅)
- 알림 규칙 정의 (에러율, 응답 시간, LLM 비용 이상 감지)
- LLM 호출 비용 추적 대시보드 (anthropic API usage 통합)
- 사용자 행동 분석 파이프라인 (이벤트 추적 → 제품 개선 루프)

## Known Dependencies (when filled in)

- `docs/decisions/observability_strategy.md` — 관측 전략 결정
- `meta/security_metrics.md` — 보안 메트릭 정의
- `meta/guardrails.md` — 알림 트리거 가드레일 기준
- `backend/fastapi/README.md` — OpenTelemetry 계측 포인트
- `eval/security_eval.md` — 보안 평가와 모니터링 연계
- Sentry, OpenTelemetry, Grafana/Datadog (Phase 7 시점 버전 확정)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 7 보안 강화 Phase 진입
- 또는 등록 사용자 1만 명 도달

## 예시 단계별 확장 계획 형식 (fill-in 시 참고)

```
Phase 7: OpenTelemetry 도입
  - FastAPI에 OTel 계측 추가 (트레이싱 + 메트릭)
  - Grafana Cloud 연결 (무료 티어)
  - LLM 호출 비용 추적 대시보드 초기 버전

Phase 10: 보안 메트릭 본격 운영
  - security_eval.md 기반 자동 알림 설정
  - 이상 감지 (비용 급증, 에러율 급증) 알림

Phase 15+: Datadog 전환 검토 (사용자 규모 대비)
```

## Related Skill / Phase

- Skill: security-review, harness-audit
- Phase: 7+
- 책임자: 운영자 / AI
