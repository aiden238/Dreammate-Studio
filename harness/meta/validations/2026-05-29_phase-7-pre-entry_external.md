# Phase 7 Pre-Entry Multi-LLM Validation — External

> 검증 모델: (예: GPT-4o, Gemini-1.5-Pro 등) — **사용자가 외부에서 진행 후 작성**
> 검증 일자: (기록 시 채울 것)
> 검증 유형: formal — self-validation과 짝 (네 번째 정식 트리거)
> 본 문서: **placeholder** (외부 검증 결과 추가 대기)
> RAG architecture 영향: **HIGH** (chunking + embedding + retrieval + 5단계 promotion 첫 정식 도입) → 외부 검토 **권장**
> Skill 의무 트리거: **rag-design (★ 첫 정식)** + multi-llm-validation (formal 네 번째)

## 작성 가이드

Phase 4.5/6/5/5.5 external placeholder 패턴 계승. 다음 항목을 외부 LLM (GPT/Gemini 등)에 다음 자료와 함께 제시한 후 결과를 기록.

### 외부 LLM에 제공할 자료

1. `harness/phases/active/phase-7-rag-lite/goals.md`
2. `harness/phases/active/phase-7-rag-lite/scope.md`
3. `harness/phases/active/phase-7-rag-lite/non_goals.md`
4. `harness/phases/active/phase-7-rag-lite/dependencies.md`
5. `harness/phases/active/phase-7-rag-lite/acceptance.md`
6. `harness/phases/active/phase-7-rag-lite/assumptions.md`
7. `harness/phases/active/phase-7-rag-lite/multi_slice_plan.md`
8. `harness/phases/active/phase-7-rag-lite/notes.md`
9. 본 self-validation 문서 (`2026-05-29_phase-7-pre-entry_self.md`)
10. `harness/docs/decisions/phase_7_rag_scope_evolution.md` (ADR-024)
11. `harness/docs/decisions/phase_7_rag_architecture.md` (ADR-025 — rag-design Skill 첫 정식 결과)
12. `harness/docs/decisions/phase_7_promotion_logic.md` (ADR-026 — 5단계 promotion logic)
13. `harness/docs/contracts/rag_data_contract.md` (현 상태 — Slice 2 갱신 예정)
14. `harness/docs/contracts/llm_security_contract.md` (RAG poisoning + §6/§7)
15. `harness/knowledge/rag/{promotion_rule, retrieval_policy, quality_filter, metadata_schema}.md`
16. `harness/knowledge/llm_wiki/index.md` (LLM Wiki baseline)
17. (선택) `harness/.claude/skills/rag-design/SKILL.md` (8단계 절차)
18. (선택) `harness/.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

### 외부 LLM에 묻을 질문 (V1~V7)

1. **V1 ADR-024 5단계 채택 정합**:
   - candidate_knowledge 5단계 모두 MVP 구현 (vs 일부만 — 예: pending + promoted 2단계 first)이 적절한가?
   - 5단계 전부가 12~16h에 무리 없이 구현 가능한가?
   - 자동 transition (사용자 승인 미적용) 비율이 quality에 어떤 영향?
   - 다른 RAG 시스템에서 보통 몇 단계 사용? (참고: Pinecone hybrid 2단계, LangChain 3단계 등)

2. **V2 chunk size 512 tokens**:
   - 영상기획 도메인 (한국어 + 영어 혼재)에 512가 적정한가?
   - 256 vs 512 vs 1024 — eval-run 정식화 전에 어느 값 채택이 안전?
   - overlap 50 tokens (10%)가 sentence boundary 우선 전략과 정합?
   - 한국어 token 효율 (1.5~2x) 고려 시 영문 standard 512 그대로 적용 OK?

3. **V3 top-k=5 + threshold=0.7**:
   - 3-plan 생성에 top_k=5 (plan별 ~1~2 chunks)가 충분한가?
   - threshold=0.7 (vs 0.65 / 0.75)가 candidate_knowledge 미숙성 단계에서 균형적인가?
   - brand_id 격리는 retrieval 단계에서 강제하는가, prompt context 단계인가?
   - re-ranking 미적용 시 noise 비율 추정?

4. **V4 OpenAI embedding `text-embedding-3-small`**:
   - `text-embedding-3-small` (1536 dim) vs `text-embedding-3-large` (3072 dim) — MVP 적정?
   - 한국어 + 영어 혼재에 다국어 전용 (multilingual-e5-large 등) 검토 필요?
   - Phase 21+ Custom embedding 교체 시 dim 변경에 대한 migration 전략 권장?
   - OpenAI API outage 대비책 (cache, fallback embedding) 추가 필요?

5. **V5 graceful fallback 정신 (RAG 실패 시 plan 차단 X)**:
   - validation.warnings에 `rag_unavailable` 마커가 응답 schema 정합한가?
   - chunking → embedding → promotion partial state 시 idempotent transition 보장 가능?
   - sustained outage 감지 + alarm 정책 (몇 % 실패 시 차단)?
   - graceful 비율 측정 metric 권장 (Phase 9+ eval)?

6. **V6 LLM Wiki vs RAG 분리 (static vs dynamic, RAG > LLM Wiki 우선순위)**:
   - 분리 baseline + 우선순위 RAG > LLM Wiki가 적절한가?
   - conflict 시 사용자 알림 + 수동 merge 정책 필요?
   - LLM Wiki를 RAG에 흡수하는 대안 (단일 source)이 더 단순한가?
   - rag-design Skill §7 "경계가 모호한 항목은 사용자 결정 요청" 정합?

7. **V7 5단계 hybrid 승인 정책 (자동 0.8+ / 수동 0.6~0.8 / 거부 <0.6)**:
   - hybrid 임계 (0.8 자동 / 0.6 수동) MVP 적정?
   - 간이 eval rubric 3 dim (relevance / clarity / safety)가 Phase 9+ 정식 rubric으로 자연 진화 가능?
   - 사용자 승인 endpoint (`POST /api/v1/rag/promote`)가 UX에 부담 없는가?
   - 자동 비율 목표 70% vs 50% 권장?

### 결과 기록 형식 (Phase 4.5/6/5 패턴 계승)

```
## V1. (외부 LLM 응답)
- 일치 / 차이 / 추가 risk:
- 권장 조치:

## V2. ...
## V3. ...
## V4. ...
## V5. ...
## V6. ...
## V7. ...

## 종합 판정 (외부 LLM)
- Phase 7 entry 허용 / 보류 / 차단:
- 차이 항목이 있을 때 Phase 7 notes.md 갱신 필요 여부:
- Slice 2 contract-change 영향 여부 (rag_data_contract.md):
- Slice 3 retrieval/embedding/chunking 영향 여부:
- Slice 4 LLM Wiki/agents/rag 통합 영향 여부:
```

### RAG-focused 추가 질문 (선택)

`docs/decisions/phase_7_rag_architecture.md` (ADR-025 — rag-design Skill 첫 정식) 본문에 대해 외부 LLM 견해:

- **A1 chunking strategy**: 문장 boundary 우선 + fallback token boundary 정합?
- **A2 embedding cost**: `text-embedding-3-small` 월 비용 추정 (사용자 1000 + 1 user/day 100 chunks 가정)?
- **A3 retrieval index**: pgvector ivfflat vs HNSW — MVP 적정?
- **A4 promotion_history GIN index**: Phase 9+ 도입 시점 권장?
- **A5 quality_filter library 선택**: PII detector (예: presidio, spaCy NER)?

---

**현재 상태**: placeholder — 사용자가 외부 GPT/Gemini 검증 후 결과 추가 예정.

Phase 7은 self-validation V1~V7 PASS + rag-design Skill 첫 정식 트리거 (ADR-025) 결과로 entry 진행. 외부 검증 결과는 추후 추가되어도 본 phase 진행에 영향 X (단, 차이 항목 발견 시 notes.md 또는 Slice 5 회고에 반영).

**RAG architecture 영향이 큰 phase**이므로 사용자 외부 진행 **권장**. 외부 검토 결과 Critical 차이 발견 시 Slice 2 진입 전 사용자 알림 + 차단 검토.

**의무 작성 시점**: Phase 7 Slice 1 entry (현 시점, placeholder). Phase 7 종료 시점에 본 placeholder가 채워지지 않으면 multi-llm-validation formal external 의무 위반 — 다음 phase (Phase 8 또는 Phase 9) entry 4-check에서 차단.

**Phase 5.5 self-strengthen 패턴 가능성**: Phase 5.5에서 Phase 4.5/6/5 external placeholder에 self-strengthen V-form (Claude Code 자가 검토 형식 — V1~V_n self-question + self-answer + 합의 추정)으로 강화한 사례가 있음. Phase 7 external도 사용자 외부 진행 전에 self-strengthen V-form 추가 가능 (단, 본 Slice 1에서는 외부 진행 자체 우선 권장).

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 5 external: `meta/validations/2026-05-29_phase-5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 7 self: `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS — 네 번째 formal)
- Phase 7 external: 본 문서 (placeholder)
