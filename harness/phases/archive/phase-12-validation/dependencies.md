# Phase 12 — Dependencies

## 선행 phase (Phase 1~11 누적)
| 의존 | Phase 12 에서 |
|---|---|
| Phase 1~9.5 MVP 파이프라인 (3안 + Critic revise + RAG + 저장/피드백) | ★ **측정 대상** — 출력 품질·깊이를 실측하는 주체 |
| Phase 9.5 eval-run (mock-deterministic 회귀 + 임계값 게이트, ADR-033) | golden_set runner + 채점 차원 + 게이트 — Phase 12 가 확장(~25)·실 LLM mode 로 재사용 |
| Phase 10 **실 LLM eval mode capability** (mode flag, default mock — ADR-038/CC-009) | ★ S2 실 LLM eval 실행의 capability 기반. Phase 10 이 경로 wire(default off) → Phase 12 가 측정용으로 1회 ON |
| Phase 10 RAG eval_rubric v1.0.0 + golden_set 11→15 (CC-009) | S1 확장(15→~25)·depth/actionability 차원 추가의 baseline |
| Phase 11 **LLM Gateway B안 (3-provider)** | eval 에 multi-provider 활용 가능(신규 도입 아님, NG4). 깊이 측정 시 provider 다양성 옵션 |

## 측정 capability 의존 (S2·S3)
- `backend/fastapi/eval/` (runner / golden_set_loader / mode / report) — Phase 9.5/10 구축. ★ **읽기·실행만** (Phase 12 운영 코드 0 수정).
- 실 LLM eval mode flag (Phase 10, default mock) — S2 에서 측정용 1회 ON (실비용, 사용자 승인). CI/mock 게이트는 default 유지(NG9).
- 키(OPENAI/ANTHROPIC/GOOGLE) = .env user-provided + .gitignore. 실 호출은 승인된 비용, 키 평문 0(NG10).

## eval / contract 의존 (S1 — contract-change 경유)
- `eval/golden_set.md` (현 **15** 케이스 GS-001~GS-015) — S1 확장 대상(→~25, ★ additive 회귀 보존).
- `eval/human_review_rubric.md` — S4 human review kit 의 채점 rubric 기반.
- `eval/video_planning_eval.md` / `eval/hook_quality_eval.md` / `eval/execution_feasibility_eval.md` / `eval/target_fit_eval.md` — depth/actionability 차원 정합 참조.
- `eval/rag_eval_rubric.md` (v1.0.0, Phase 10) — rubric 버전 관리 패턴 참조.
- `docs/contracts/product_boundary.md` — ★ 확장본(rich)도 "기획 브리프" 경계 유지(NG2) 의 단일 출처.

## ★ B안(Phase 11) 비차단 잔여 — GPT 검토 ④ 반영 (dependency/추적 항목으로 명시)

> Phase 11 B안(3-provider)은 기능 완성·라이브 입증되었으나 정식화 일부가 비차단 잔여로 남음(`PROJECT_STATE.md` §B안). 이들은 Phase 12 의 **비용 추정·범위 기준**에 영향하므로 dependency/추적 항목으로 등록 — **Phase 12 내 또는 직후 처리**.

| ID | 잔여 항목 | Phase 12 영향 | 처리 |
|---|---|---|---|
| **B-RES-1** | `cost_control_policy` 다중-provider cost 재조정 (제안서 §18.D) — 위치: `ai_system/orchestration/cost_control_policy.md` | ★ S2 **실 LLM eval 비용 추정**의 기준 (3-provider 사용 시 호출당 비용). 비용 승인 근거 정합 | Phase 12 내 또는 직후 (cost-review) |
| **B-RES-2** | B안 ADR (3-provider 결정 기록) | Phase 12 범위·가정의 근거 문서(왜 3-provider 가 eval 옵션인지) | Phase 12 직후 (ADR 신규) |
| **B-RES-3** | agent_io / registry contract-change (B안 3-provider 반영) | ★ depth 측정 시 어느 provider/alias 가 어느 slot 인지 contract 정합 | Phase 12 직후 (contract-change) |

→ ★ 이들은 **운영 코드 변경이 아니라 정식화(문서) 잔여** — Phase 12 의 측정·비용 기준에 영향하므로 추적. Phase 12 acceptance 의 blocking 아님(추적 항목).

## Skill 의존
- `eval-design`(S1 golden_set 확장 + depth/actionability rubric) / `eval-run`(S2 실 LLM eval 실행 + S3 깊이 격차 측정) / `contract-change`(S1 golden_set·rubric additive) / `multi-llm-validation`(entry self 11th) / `cost-review`(S2 실 LLM 비용 + B-RES-1) / `meta-retrospective`(S5 종합) / `phase-start`·`phase-complete`(진입·종료) / (참조) `ai-architecture-review`(확장 우선순위 = Phase 13 입력).

## 비의존 / 경계
- apps/web/** (frontend — Phase 12 측정에 미관여, 운영 0 수정) / 영상 제작(영구 non-goal) / 운영 prompt_registry·output_schema(Phase 13 확장 대상, Phase 12 미수정) / staging·배포(Phase 13+).
- ★ behavior-preserving: 기존 endpoint/agent/eval runner 에 **의존하되 변경하지 않음** — eval 은 측정 capability(읽기·실행), golden_set/rubric 만 S1 contract-change 경유.
