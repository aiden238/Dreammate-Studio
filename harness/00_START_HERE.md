# START HERE

## 프로젝트 정의

이 프로젝트는 영상 제작 AI가 아니라 **영상기획 AI 에이전트 플랫폼**이다.

한 줄 정의:

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤, 검증 에이전트가 기획 품질을 평가·개선하는 영상기획 특화 AI 에이전트.

## 핵심 흐름

본 제품은 **Hybrid UX**: Discovery Wizard(신규/콜드스타트용 5단계 카드) + Quick Mode(같은 Series 추가 시). 두 모드는 같은 generate_plan 파이프라인으로 수렴.

```text
사용자 입력
→ 의도 분석 (Discovery 또는 Quick 자동 분기)
→ 부족한 정보 질문 (Discovery: 5 카드, Quick: 1–2 질문)
→ 한 줄 기획 방향 승인
→ LLM Wiki / RAG 검색
→ 영상기획안 3개 생성 (P-006 plan_candidates)
→ Critic Agent 검증 (revise 최대 2회)
→ 개선안 반영
→ 결과 저장
→ 사용자 선택·피드백 저장 (Brand Memory 자동 추출)
```

## 반드시 지킬 원칙

1. AGENTS.md와 CLAUDE.md는 지침 본문이 아니라 라우터로 사용한다.
2. PROJECT_STATE.md에는 최신 상태만 압축 기록한다.
3. phases/archive/는 기본 참조하지 않는다.
4. docs/contracts/는 무단 변경하지 않는다.
5. contract 변경은 docs/contract_changes/ 또는 meta/proposals/에 먼저 제안한다.
6. 구조는 처음부터 크게 만들고, 내용은 Phase 진행에 따라 얇게 채운다.
7. 영상 제작, 자동 편집, TTS/BGM, 자동 업로드는 MVP에 넣지 않는다.

## 첫 진입 시 읽을 문서

1. `PROJECT_STATE.md` (현재 active Phase, migration_progress 확인)
2. `PHASE_REGISTRY.md`
3. `product/mvp_scope.md`
4. `docs/contracts/mvp_non_goals.md`
5. `phases/active/{current-phase}/` 폴더 전체 (goals, scope, non_goals, acceptance, dependencies)
6. 현재 작업에 필요한 contracts

## 현재 active Phase

**🟡 pending_user_decision** — Phase 7 ✅ done (2026-05-29)

Phase 7 ✅ done (2026-05-29). 다음 phase는 사용자 결정 대기 (옵션 A Phase 8 MOA / B Phase 9 저장-피드백 / C Phase 9.5+ eval / D Phase 11+).

- Phase 7 archive: `phases/archive/phase-7-rag-lite/` (참조 가능 — closing_notes + 회고 + RAG Lite baseline + 다음 옵션 A/B/C/D)
- Phase 5.5 archive: `phases/archive/phase-5.5-legacy-db-consolidation/` (참조 가능 — Phase 7 진입 baseline)
- Phase 5 archive: `phases/archive/phase-5-db-auth/` (참조 가능 — DB/Auth/RLS/SSE baseline)
- Phase 6 archive: `phases/archive/phase-6-output-schema-stabilization/` (참조 가능 — contract 안정화 baseline)
- Phase 4.5 archive: `phases/archive/phase-4.5-critic-revise-loop/` (참조 가능 — Critic revise loop + Rewriter baseline)
- Phase 4 archive: `phases/archive/phase-4-fastapi-extension/` (참조 가능 — backend + frontend baseline)
- Phase 3 archive: `phases/archive/phase-3-pwa-impl/` (참조 가능 — frontend baseline)
- Phase 2 archive: `phases/archive/phase-2-pwa-design/` (참조 가능 — design spec baseline)
- Phase 1 archive: `phases/archive/phase-1-mvp-basic-flow/` (참조 가능 — backend baseline)
- Phase 0 archive: `phases/archive/phase-0-migration/` (참조 금지)

**다음 phase 옵션 (사용자 결정 대기)**:

- **A. Phase 8 — MOA Lite 본격** (12~16h)
  - Intent / Planner / Critic / Rewriter 완전 분리
  - agents/* 모두 재구조화 (Phase 1 baseline + Phase 6 canonical + Phase 7 wrapper 공존 → 정리)
  - SSE Progress worker 통합 (mock → 실 worker callback)
  - prompt_registry P-007/P-008 정식화 (NG8 누적 3회 defer 해소)
  - ai-architecture-review Skill ★ 첫 정식 baseline
- **B. Phase 9 — 결과 저장 + 피드백** (6~10h)
  - 사용자 plan 선택 / 수정 / 반려 누적
  - Phase 5 plans_repo + RLS + Phase 7 RAG 활용
  - Brand Memory 자동 추출 ADR 신규 (Phase 7 개선 제안 §5)
- **C. Phase 9.5+ — eval-run Skill 정식화** (4~6h)
  - golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 5회 deferred 해소)
  - Critic deprecated 4 fallback 완전 제거
  - 간이 RAG eval_rubric → 정식 (Phase 7 개선 제안 §6)
- **D. 다른 우선순위** (Phase 11+)
  - 사용자 데이터 자동 promotion (rag-update Skill 두 번째)
  - Supabase SQL function 정의 (운영 단계 필수)
  - Phase 1 legacy rag 실 통합 / cost-review Skill

**Phase 7 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 31연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5)
- **PlanCard.tsx 19연속 0줄** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1)
- **component_map.md 29연속 0줄** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1)
- **5단계 파이프라인 전부 MVP** (pending → filtered → evaluated → approved → promoted + hybrid 승인 + promotion_history JSONB)
- **pgvector retrieval** (cosine + top-k=5 + threshold=0.7) + **OpenAI text-embedding-3-small** + **chunking 512 tokens + overlap 50** + **LLM Wiki 보조 (RAG > LLM Wiki 우선순위)**
- **rag-design Skill ★ 첫 정식 트리거** (Slice 1, ADR-025)
- **rag-update Skill ★ 첫 정식 트리거** (Slice 4, initial promotion procedure)
- **contract-change Skill 본격 세 번째** (rag_data_contract.md §18)
- **multi-llm-validation formal 네 번째** (V1~V7 PASS — RAG architecture)
- **agent-io-check Skill 세 번째 회귀** (agents/rag.py 검증, 회귀 0)
- 2 ADR 신규 (ADR-025 RAG architecture + ADR-026 5단계 promotion logic)
- pytest 172 → **223/223** (+51 신규) + smoke 13/13 + scenario_sim v3 15/15 (P-X2 다섯 번째)
- 신규 패턴: P-RAG-5STAGE-001 + P-RAG-GRACEFUL-001 (5종 marker 표준화) + P-X1-EFFECT-001 update (31연속) + P-VALIDATION-FORMAL-001 update (네 번째) + P-LEGACY-CONSOLIDATION-001 update (누적 2회 — 정식 채택 임박)
- graceful 5종 marker (P-GRACEFUL-001 Phase 1 정신 5번째 입증)
- 사용자 결정 3건 mapping 완료 (Phase 5.5에서 이미 명시 → 추가 결정 0건)
- large phase 실측 ~13~14h (추정 12~16h 내)
