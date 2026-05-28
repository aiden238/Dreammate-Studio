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

**🟡 pending_user_decision** (Phase 5 ✅ done 2026-05-29)

Phase 5 ✅ done (2026-05-29). 다음 phase 사용자 결정 대기 — 옵션 A Phase 7 RAG / B Phase 6+ legacy / C Phase 9 저장-피드백 / D Phase 8 MOA.

- Phase 5 archive: `phases/archive/phase-5-db-auth/` (참조 가능 — closing_notes + 회고 + Phase 6+/7+/8/9 옵션)
- Phase 6 archive: `phases/archive/phase-6-output-schema-stabilization/` (참조 가능 — contract 안정화 baseline)
- Phase 4.5 archive: `phases/archive/phase-4.5-critic-revise-loop/` (참조 가능 — Critic revise loop + Rewriter baseline)
- Phase 4 archive: `phases/archive/phase-4-fastapi-extension/` (참조 가능 — backend + frontend baseline)
- Phase 3 archive: `phases/archive/phase-3-pwa-impl/` (참조 가능 — frontend baseline)
- Phase 2 archive: `phases/archive/phase-2-pwa-design/` (참조 가능 — design spec baseline)
- Phase 1 archive: `phases/archive/phase-1-mvp-basic-flow/` (참조 가능 — backend baseline)
- Phase 0 archive: `phases/archive/phase-0-migration/` (참조 금지)

**다음 phase 옵션** (사용자 결정 대기):

- **A**: Phase 7 RAG Lite (8~12h) — candidate_knowledge 5단계 + pgvector + rag-design/update 첫 정식
- **B**: Phase 6+ legacy DB 통합 (4~6h) + Phase 7 — Phase 5 §1 발견 해소
- **C**: Phase 9 결과 저장 + 피드백 (6~10h) — plans_repo + RLS 활용 + Brand Memory 자동 추출 활성화
- **D**: Phase 8 MOA Lite 본격 (12~16h) — Intent/Planner/Critic/Rewriter 완전 분리 + SSE worker 통합

**진입 전 권장** (옵션 무관):
1. Legacy DB 통합 결정 (Phase 5 발견 §1)
2. Brand Memory 자동 추출 (확정 결정 [8]) baseline 활성화
3. external validation 사용자 채움 (Phase 5 placeholder)
4. phase-start v1.3.0 4점검 (8번째 trigger)
5. multi-llm-validation formal self (네 번째 트리거)

**Phase 5 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 22연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5)
- **PlanCard.tsx 17연속 0줄** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5)
- **component_map.md 27연속 0줄** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5)
- **Supabase + 4계층 schema migration + plans_repo** (Slice 2, db_schema.md contract + ADR-020)
- **Auth + JWT (httpOnly cookie) + Frontend Login + AuthGuard wrapper** (Slice 3)
- **RLS 정책 (auth.uid() + 4 정책 + 2-hop subquery) + SSE Progress 4단계 D7** (Slice 4, ADR-021/022)
- pytest 144 → **170 (+26)** + smoke 10 → **12** (smoke_test_phase_5) + scenario_sim v2 10/10 (P-X2 세 번째)
- **security-review Skill 첫 정식 (Slice 1) + 두 번째 final (Slice 5)** — T1~T6 위협 모델 + 영역 1~10 baseline 달성
- **contract-change Skill 두 번째 본격** (db_schema.md 신규 — DB schema 첫 정식 contract)
- **multi-llm-validation formal 세 번째** (V1~V6 PASS) — **P-VALIDATION-FORMAL-001 정식 패턴 확정 (3회 누적)**
- **agent-io-check Skill 두 번째 회귀** (Phase 6 baseline 유지)
- 4 ADR 신규 (ADR-020 + ADR-021 + ADR-022)
- 신규 패턴: P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 (신규 후보) + P-X1-EFFECT-001 update (22연속) + P-VALIDATION-FORMAL-001 update (정식 확정)
- graceful fallback 일관 적용 — Supabase 미설정 시 in-memory dict 회귀 0
