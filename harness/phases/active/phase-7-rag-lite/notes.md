# Phase 7 — Notes

## Entry (2026-05-29)

- phase-start v1.3.0 §6 4점검 PASS (C1~C11, U1~U6)
- audit_naming PASS 0 drift
- Phase 5.5 baseline 완전 유지 (pytest 172/172 + smoke 12/12 + scenario_sim v2 10/10 + P-X1 26연속)
- 5 Slice 모두 sub-agent dispatch
- ADR-024 (Phase 5.5 RAG scope evolution) 기반 진입
- candidate_knowledge 5단계 MVP 전부 구현 (사용자 결정 4)
- Brand Memory Phase 9+ 이관 (사용자 결정 5 계승, NG1)
- **rag-design Skill ★ 첫 정식 트리거** (Slice 1)
- **rag-update Skill ★ 첫 정식 트리거** (Slice 4)
- 추정 12~16h (ADR-024 갱신 정합)

## Slice 1~5 (작업 시 갱신)

### Slice 1 — Pre-Entry (완료, 2026-05-29)

산출물:
- `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS — 네 번째 formal)
  - V1 ADR-024 5단계 채택 정합 / V2 chunk 512 tokens / V3 top-k=5 + threshold=0.7 / V4 OpenAI embedding text-embedding-3-small / V5 graceful fallback / V6 LLM Wiki vs RAG 분리 (RAG > LLM Wiki 우선순위) / V7 5단계 hybrid 승인 정책 (자동 0.8 / 수동 0.6)
- `meta/validations/2026-05-29_phase-7-pre-entry_external.md` (placeholder, Phase 4.5/6/5/5.5 패턴 계승 + self-strengthen V-form 가능 명시)
- **rag-design Skill ★ 첫 정식 트리거** (절차 8단계 모두 적용) → ADR-025 본문 통합
- `docs/decisions/phase_7_rag_architecture.md` (ADR-025): chunking 512 + overlap 50 + 문장 boundary 우선 / embedding text-embedding-3-small (1536 dim, RAG_EMBEDDING_MODEL env) / retrieval pgvector cosine top-k=5 threshold=0.7 + brand_id 격리 + dedupe / LLM Wiki vs RAG 분리 (RAG > LLM Wiki 우선순위) / graceful 5종 marker
- `docs/decisions/phase_7_promotion_logic.md` (ADR-026): 5단계 transition (pending → filtered → evaluated → approved → promoted) / hybrid 승인 (자동 0.8 / 수동 0.6~0.8 / 거부 <0.6) / 간이 3 dim eval rubric (relevance + clarity + safety, Phase 9+ deprecated) / promotion_history JSONB append-only / 자동 비율 70% 목표
- `meta/skill_usage_log.md` 갱신: phase-start 8 → 9 / multi-llm-validation 4 → 5 / **rag-design 0 → 1 (★ 첫 정식 active)** / qa-check 32 → 33
- `PROJECT_STATE.md` 갱신: phase_7_* yaml 필드 신규 + active phase Phase 7 ★ 전환 + total_commits 64 → 65 + current_sprint phase-7-slice-1
- entry commit (Slice 1 entry)

P-X1 §SELF-VERIFICATION PASS (Phase 7 1번째, 누적 27연속).
PlanCard.tsx 0줄 (19연속), component_map.md 0줄 (29연속).

미사용 Skill (의도된, Slice 2~5에서 활성):
- contract-change (Slice 2 — rag_data_contract.md)
- rag-update (Slice 4 — 첫 정식)
- agent-io-check (Slice 5 — agents/rag.py 변경 검증)
- harness-audit / design-review / meta-retrospective / phase-complete (Slice 5)

다음: Slice 2 sub-agent dispatch (contract-change + RAG 5단계 schema/promotion/quality_filter/eval_rubric).
