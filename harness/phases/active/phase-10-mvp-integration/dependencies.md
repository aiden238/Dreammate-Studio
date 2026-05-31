# Phase 10 — Dependencies

## 선행 phase (Phase 1~9.5 누적 — 통합 대상)
| 의존 | Phase 10 에서 |
|---|---|
| Phase 1 `/api/v1/generate` + 3안 + Critic | end-to-end 통합 흐름 시작점 |
| Phase 3 Next.js PWA (Discovery+Quick 11 routes) | 프론트 흐름 (page 레벨 통합 — PlanCard 무수정) |
| Phase 5 Supabase + JWT + RLS + SSE | save/auth/progress 통합 |
| Phase 7 RAG Lite | RAG 검색 통합 + RAG eval_rubric (G5) |
| Phase 8 MOA orchestrator | orchestration 통합 흐름 |
| Phase 9 selected_plans/feedback_events + **brand_memory_repo + feedback→candidate 적재** | save/select/feedback 통합 + ★ **P-AUX-2 의 입력 경로** (ADR-031) |
| Phase 9.5 eval-run harness (golden_set 11 + runner + 임계값) | G4 eval mode + G5 golden_set 확대 baseline |

## 구현 의존 (S2 P-AUX-2)
- `db/repositories/brand_memory_repo.py` (Phase 9 — 적재 대상) + `rag/feedback_to_candidate.py` (Phase 9 — 입력) + ADR-031 (Brand Memory prep 설계).
- agent 격리 패턴(orchestrator 경유) + graceful + PII 마스킹 (Phase 9 security-review 계승).

## eval 의존 (S3)
- `backend/fastapi/eval/{runner, golden_set_loader, report}.py` (Phase 9.5) — mode flag wire 대상.
- ADR-033 (eval-run harness — 실 LLM mode flag 명시) + `eval/golden_set.md` (11 → 확대).
- knowledge/rag/* (RAG eval_rubric 대상).

## Skill 의존
- `qa-check`(통합 release gate) / `eval-run`(G4·G5 회귀) / `eval-design`(golden_set 확대 + RAG rubric 설계) / `agent-io-check`(P-AUX-2 IO 정합) / `contract-change`(CC-008/009) / `prompt-version-review`(P-AUX-2 prompt) / `security-review`(brand memory PII) / `multi-llm-validation`(10th formal) / `ai-architecture-review`(P-AUX-2 agent 추가 — orchestration 영향) / `design-review`(page 레벨, PlanCard 무수정 확인) / `phase-start`/`phase-complete`/`meta-retrospective`.

## 비의존 / 경계
- meta_factory (detour 종료 — 무관) / 영상 제작 (영구 non-goal) / Phase 11+ 항목.
- ★ behavior-preserving: 기존 endpoint/test 에 의존하되 **변경하지 않음** (신규 추가만).
