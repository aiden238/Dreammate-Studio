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

**Phase 5 (DB/Auth) — pending entry**

Phase 6 ✅ done (2026-05-29). 다음 phase = Phase 5 DB/Auth (사용자 결정 "Phase 6 → Phase 5 순차" 계승).

- Phase 6 archive: `phases/archive/phase-6-output-schema-stabilization/` (참조 가능 — closing_notes + 회고 + Phase 5 진입 체크리스트)
- Phase 4.5 archive: `phases/archive/phase-4.5-critic-revise-loop/` (참조 가능 — Critic revise loop + Rewriter baseline)
- Phase 4 archive: `phases/archive/phase-4-fastapi-extension/` (참조 가능 — backend + frontend baseline)
- Phase 3 archive: `phases/archive/phase-3-pwa-impl/` (참조 가능 — frontend baseline)
- Phase 2 archive: `phases/archive/phase-2-pwa-design/` (참조 가능 — design spec baseline)
- Phase 1 archive: `phases/archive/phase-1-mvp-basic-flow/` (참조 가능 — backend baseline)
- Phase 0 archive: `phases/archive/phase-0-migration/` (참조 금지)

**진입 전 의무**:
1. multi-llm-validation **formal external** 작성 (`meta/validations/2026-05-29_phase-6-pre-entry_external.md` placeholder를 GPT/Gemini로 채움)
2. security-review Skill 첫 호출 준비
3. scenario_simulation.ps1 v2 (DB/Auth용 5 시나리오 추가) — Phase 5 Slice 1에서
4. contract-change Skill (db_schema.md 신규 + 0001_init.sql migration)
5. ADR-020 Supabase 채택 결정 작성

**Phase 6 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 17연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4)
- **PlanCard.tsx 12연속 0줄** (Phase 4 4 + Phase 4.5 5 + Phase 6 3)
- **component_map.md 22연속 0줄** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3)
- **Critic verdict canonical 결정** (overall_score + dimensions, ADR-018)
- **Rewriter contract v1.0.0 → v1.1.0** (Pydantic + graceful, ADR-019)
- **Critic 4 fallback → 1 canonical + 1 우선 fallback + 3 deprecated** (DeprecationWarning)
- pytest 109 → **144 (+35)** + smoke 9 → **10** (smoke_test_phase_6) + scenario_sim 5/5 (P-X2 두 번째) + schema_stress 5/5 (P-X2 v2 신규)
- **agent-io-check Skill 첫 정식 트리거** (Rewriter v1.1.0 + Critic canonical 정합 PASS)
- **contract-change Skill 첫 본격 실 변경 통과** (3 contract + 회귀 0)
- **multi-llm-validation formal 두 번째 트리거** (V1~V5 PASS, 정식 패턴 확정)
- 신규 패턴: P-CRITIC-CANONICAL-001 + P-CONTRACT-FIRST-001 (신규 후보) + P-X1-EFFECT-001 update (17연속) + P-VALIDATION-FORMAL-001 update (두 번째 입증)
- GPT 검토안 6→4 Slice 압축 (▼33%) + 시간 ▼20% (P-GPT-REVIEW-001 두 번째 적용)

**Phase 5 entry 트리거**: 위 5개 의무 사항 완료 후 phase-start v1.3.0 호출.
