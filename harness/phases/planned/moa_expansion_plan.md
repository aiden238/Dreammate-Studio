# moa_expansion_plan.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 11+
priority: medium
estimated_final_lines: 170
last_updated: 2026-05-26
```

## Why Placeholder?

현재 MOA Lite (Intent → Planning → Critic → Rewriter, 4 agent)로 MVP를 운영한다.
Phase 11까지 Lite 구조 한계가 실제로 확인되기 전까지 확장 계획을 상세화하지 않는다.

## Scope (TBD)

본 파일이 다룰 범위:
- MOA Lite (4 agent) 한계 진단 기준 (만족도, 응답 품질, 패턴 다양성)
- LangGraph vs. MCP 기반 오케스트레이션 전환 비교 분석
- 새로운 Agent 추가 절차 (agent_io_contract.md 기반 계약 우선)
- 멀티 Critic 구조 도입 방안 (Critic 병렬화, 특화 Critic)
- 비용/지연 트레이드오프 (agent 수 증가 대비 품질 향상 비율)
- A/B 테스트 절차 (MOA Lite vs. 확장 버전 동시 운영)
- 프롬프트 버전 관리 고도화 (`prompt_registry.md` 연계)

## Known Dependencies (when filled in)

- `docs/decisions/orchestration_strategy.md` — MOA 오케스트레이션 전략
- `ai_system/architecture.md` — 현재 MOA Lite 구조
- `ai_system/orchestration/moa_policy.md` — MOA 정책
- `ai_system/orchestration/flow.md` — 오케스트레이션 흐름
- `eval/video_planning_eval.md` — 품질 평가 기준
- `logs/eval_log.md` — 만족도 및 Critic 점수 추이
- LangGraph / Anthropic MCP SDK (Phase 11 시점 버전 확정)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- MOA Lite 사용자 만족도 70% 미만 (3개월 이상 지속)
- 또는 현재 4 agent 구조로 처리 불가한 새 기획 패턴 요구 2건 이상 발생

## 예시 확장 단계 형식 (fill-in 시 참고)

```
현재: Intent → Planning → Critic → Rewriter (4 agents)

확장 후보 A: +FactCheck Agent (RAG 기반 팩트 검증)
확장 후보 B: +TrendAnalysis Agent (트렌드 데이터 통합)
확장 후보 C: Critic 병렬화 (Brand Critic + UX Critic 분리)
```

## Related Skill / Phase

- Skill: ai-architecture-review, agent-io-check
- Phase: 11+
- 책임자: AI / 운영자
