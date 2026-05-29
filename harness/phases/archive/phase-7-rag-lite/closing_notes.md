# Phase 7 — Closing Notes

> 종료일: 2026-05-29
> 결과: A1~A10 10/10 + M1~M4 4/4 PASS
> 다음 phase: **🟡 pending_user_decision** (Phase 8 MOA / Phase 9 저장-피드백 / Phase 9.5+ eval / 다른 우선순위 Phase 11+)

---

## 최종 산출물

### Backend RAG layer (~+1500 LOC)
- `backend/fastapi/rag/__init__.py` (Slice 2 + Slice 1 export 통합)
- `backend/fastapi/rag/promotion.py` (5단계 transition + hybrid 승인)
- `backend/fastapi/rag/quality_filter.py` (PII + 인젝션 + 광고적 표현)
- `backend/fastapi/rag/eval_rubric.py` (간이 3 dim — relevance / clarity / safety)
- `backend/fastapi/rag/embedding.py` (OpenAI text-embedding-3-small + graceful)
- `backend/fastapi/rag/chunking.py` (512 tokens + overlap 50)
- `backend/fastapi/rag/retrieval.py` (pgvector cosine + top-k=5 + threshold=0.7 + dedupe)
- `backend/fastapi/rag/llm_wiki.py` (정적 5 항목, RAG 보조)
- `backend/fastapi/db/migrations/0004_rag_5stage.sql` (candidate_knowledge + approved_knowledge + RLS + ivfflat)
- `backend/fastapi/agents/rag.py` (Phase 1 baseline 호환 + Phase 7 RAG Lite 통합 wrapper)
- `backend/fastapi/routers/plans.py` (소폭, graceful 5종 marker 노출)
- `backend/fastapi/config.py` (RAG env vars 6개 — rag_embedding_model / rag_chunk_size / rag_chunk_overlap / rag_top_k / rag_threshold + 1)

### Tests (+51 신규)
- `test_rag_promotion.py` (10/10) — 5단계 transition + hybrid 승인 + promotion_history
- `test_rag_quality_filter.py` (8/8) — PII + 인젝션 + 광고
- `test_rag_eval_rubric.py` (5/5) — 간이 3 dim 종합 threshold 0.6
- `test_rag_chunking.py` (7/7) — 512 tokens + overlap 50
- `test_rag_embedding.py` (5/5) — OpenAI mock + graceful
- `test_rag_retrieval.py` (7/7) — pgvector cosine + top-k + threshold
- `test_rag_integration.py` (9/9) — end-to-end (chunking → embedding → promotion → retrieval round-trip + graceful failure)

### Contracts / ADRs
- `docs/contracts/rag_data_contract.md §18` 신규 (5단계 stage enum + promotion_history JSONB + retrieval 정책, contract-change Skill 본격 세 번째)
- `docs/decisions/phase_7_rag_architecture.md` (ADR-025, Slice 1 — rag-design Skill 첫 정식)
- `docs/decisions/phase_7_promotion_logic.md` (ADR-026, Slice 1)

### Meta
- `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS)
- `meta/validations/2026-05-29_phase-7-pre-entry_external.md` (placeholder)
- `meta/rag_updates/2026-05-29_phase-7-initial-promotion.md` (rag-update Skill ★ 첫 정식)
- `meta/retrospectives/phase-7.md` (본 phase 회고)
- `meta/patterns.md` (P-RAG-5STAGE-001 신규 + P-RAG-GRACEFUL-001 신규 + P-X1-EFFECT-001 update 31연속 + P-VALIDATION-FORMAL-001 update 네 번째 + P-LEGACY-CONSOLIDATION-001 update 누적 2회)
- `meta/skill_usage_log.md` (Phase 7 사용 요약 11 Skill — rag-design + rag-update 첫 정식)

### Scripts
- `scripts/smoke_test_phase_7.ps1` 신규 (13 체크 — 12 PASS + 1 WARN intended)
- `scripts/scenario_simulation.ps1 v3` (15 시나리오, S11~S15 RAG 추가, P-X2 다섯 번째)

---

## Phase 7 핵심 baseline

| 지표 | Phase 7 종료 |
|---|---|
| pytest | **223/223** (Phase 5.5 172 baseline + 51 신규) |
| smoke_test_phase_7 | **13/13** (12 PASS + 1 WARN intended — Phase 5 baseline AuthGuard + /login) |
| scenario_simulation v3 | **15/15** (P-X2 다섯 번째 자동 게이트) |
| schema_stress_test | 5/5 (Phase 6 v2 유지) |
| audit_naming | 0 drift |
| audit_page_component | 2 intended WARN (Phase 5 baseline 계승) |
| component_map.md 0줄 | **29연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1) |
| PlanCard.tsx 0줄 | **19연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1) |
| P-X1 streak | **31연속** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5) |

---

## 다음 Phase 옵션 (사용자 결정 대기)

### A. Phase 8 — MOA Lite 본격 (12~16h)
- Intent / Planner / Critic / Rewriter 완전 분리
- agents/* 모두 재구조화 (현재 Phase 1 baseline + Phase 6 canonical + Phase 7 통합 wrapper 공존 → 정리)
- SSE Progress worker 통합 (Phase 5 Slice 4 mock asyncio.sleep → 실 worker callback)
- prompt_registry 정식화 검토 (NG8 Phase 6/5/7 누적 3회 defer 해소)
- **ai-architecture-review Skill ★ 첫 정식 트리거 baseline**

### B. Phase 9 — 결과 저장 + 피드백 (6~10h)
- 사용자 plan 선택 / 수정 / 반려 누적
- Phase 5 plans_repo + RLS + Phase 7 RAG 활용
- **Brand Memory 자동 추출 ADR 신규** (개선 제안 §5, 사용자 결정 5 Phase 5.5 + Phase 7 누적 confirm)
- per-user rate-limit + audit-log (Phase 5 §개선 제안 §5 흡수)

### C. Phase 9.5+ — eval-run Skill 정식화 (4~6h)
- golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 5회 deferred 해소)
- Critic rubric 정식화 (Phase 6 deprecated 4 fallback 완전 제거)
- 간이 RAG eval_rubric → 정식 (Phase 7 개선 제안 §6 흡수)
- **eval-design + eval-run Skill 첫 정식 트리거 baseline**

### D. 다른 우선순위 (Phase 11+)
- 사용자 데이터 자동 promotion (ADR-024 §A, Phase 7 개선 제안 §4 + rag-update Skill 두 번째 트리거)
- Supabase SQL function `match_approved_knowledge` 정의 (Phase 7 개선 제안 §2 — 운영 단계 필수)
- Phase 1 legacy rag 실 통합 (Phase 7 개선 제안 §3 — Phase 11+ Custom RAG)
- cost-review Skill 정식화

---

## RAG 운영 단계 권장

- **Supabase SQL function `match_approved_knowledge` 정의** — 운영 단계 필수 (Phase 8+ MOA Lite 본격 또는 Phase 9+ 결과 저장-피드백 시점 권장)
- **사용자 데이터 누적 시 rag-update Skill 두 번째 호출** — Phase 11+ ADR-024 §A 확대 지점 활성화 baseline
- **chunking tiktoken 도입** — Phase 9+ eval-run Skill 활성 시 동시 검토 (정확도 ↑ + 비용 정밀 제어)
- **간이 eval_rubric → golden_set 기반 정식** — Phase 9+ eval-run Skill 정식화 시 동시 해소
- **Phase 1 legacy rag/{retriever, fallback} 실 통합** — Phase 11+ Custom RAG 시점 자연 통합 (ADR-024 §B + Phase 7 개선 제안 §3, P-LEGACY-CONSOLIDATION-001 누적 2회 → 정식 채택 임박)

---

## Phase 7 사용자 결정 1:1 mapping (3건 Phase 5.5에서 명시 + 0건 Phase 7 추가)

| 결정 ID | 결정 내용 | Phase 7 mapping |
|---|---|---|
| 결정 3 (Phase 5.5) | RAG Lite scope 유지 | ✅ ADR-024 §확대 지점 별도 phase (Phase 8+/11+/21+) — Phase 7 본 phase는 Lite 범위 유지 |
| 결정 4 (Phase 5.5) | candidate_knowledge 5단계 MVP 전부 | ✅ ADR-025 + ADR-026 + 0004_rag_5stage migration + rag/promotion.py (5단계 transition) + rag/quality_filter.py + rag/eval_rubric.py + test_rag_promotion 10/10 + test_rag_integration 9/9 |
| 결정 5 (Phase 5.5) | Brand Memory Phase 9+ 이관 | ✅ NG1 (non_goals.md §NG1) + Phase 7 회고 §개선 제안 §5 (Phase 9+ Brand Memory 자동 추출 ADR 신규 baseline) — 누적 2회 confirm |

추가 결정 0건 (Phase 5.5에서 미리 결정 완료 → Phase 7 진입 시 추가 결정 없이 그대로 채택). **consolidation mini-phase → 다음 phase 진입 부담 ↓ 효과 실측 입증**.

---

## 변경 이력

- 2026-05-29: Phase 7 closing notes 최초 작성 (Slice 5 final). A1~A10 10/10 + M1~M4 4/4 PASS. **rag-design + rag-update Skill 둘 다 ★ 첫 정식 트리거 완료 + ADR-025/026 + contract-change rag_data_contract §18 + P-RAG-5STAGE-001/P-RAG-GRACEFUL-001 신규 후보 + P-X1 31연속 + PlanCard 19연속 + component_map 29연속 + pytest 223/223 + smoke 13/13 + scenario_sim v3 15/15 + P-X2 다섯 번째 자동 게이트**. 다음 phase = 🟡 pending_user_decision (옵션 A Phase 8 MOA / B Phase 9 저장-피드백 / C Phase 9.5+ eval / D Phase 11+).
