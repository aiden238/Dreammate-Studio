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

**🟡 pending_user_decision** — Phase 8 ✅ done (2026-05-29)

Phase 8 ✅ done (2026-05-29). 다음 phase는 사용자 결정 대기 (옵션 A Phase 9 저장-피드백 / B Phase 9.5+ eval-run / C Phase 10 통합 / D Phase 11+).

- Phase 8 archive: `phases/archive/phase-8-moa-lite/` (참조 가능 — closing_notes + 회고 + MOA orchestrator baseline + 다음 옵션 A/B/C/D)
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

- **A. Phase 9 — 결과 저장 + 피드백** (6~10h)
  - 사용자 plan 선택 / 수정 / 반려 누적
  - Phase 5 plans_repo + RLS + Phase 7 RAG + Phase 8 orchestrator 활용
  - Brand Memory 자동 추출 ADR 신규 (Phase 8 개선 제안 §5, 누적 3회 confirm)
  - normalize_to_canonical wiring 연결 (Phase 8 개선 제안 §1) + per-user rate-limit + audit-log
- **B. Phase 9.5+ — eval-run Skill 정식화** (4~6h)
  - golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 6회 deferred 해소)
  - Critic deprecated 0–5 fallback 완전 제거 (Phase 8 개선 제안 §4, Phase 6 ADR-018 다음 단계)
  - 간이 RAG eval_rubric → 정식 (Phase 7 개선 제안 §6)
  - eval-design + eval-run Skill 첫 정식 트리거 baseline
- **C. Phase 10 — MVP 통합 테스트** (6~8h)
  - MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise → save → SSE progress)
  - Phase 1~8 누적 baseline 통합 회귀 + 배포 테스트 게이트 A~G 준비
- **D. 다른 우선순위** (Phase 11+)
  - SSE full async worker (Phase 8 개선 제안 §2, 누적 2회) / prompt A/B 실행 인프라 (Phase 8 개선 제안 §3)
  - 사용자 데이터 자동 promotion (rag-update Skill 두 번째)
  - Supabase SQL function 정의 (운영 단계 필수) / cost-review Skill

**Phase 8 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 36연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5)
- **PlanCard.tsx 24연속 0줄** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5)
- **component_map.md 34연속 0줄** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5)
- **MOA Orchestrator 추출 (ADR-027)** — plans.py 659→243 god-function 분해 (behavior-preserving, Envelope byte-identical)
- **behavior-preserving** — 기존 pytest 223 수정 0 (의도된 2 version assertion 제외, 회귀 0 = 동작 불변 증거)
- **ProgressSink + progress_store 브릿지 (ADR-028)** — SSE 실 stage 연동 (graceful fallback, background task 미도입)
- **prompt_registry semver 정식화 (ADR-029, CC-003)** — P-001~P-008 + AUX semver + Critic v1.1.0 conservative adapter (Phase 6 canonical 불변, NG8 누적 3회 해소)
- **ai-architecture-review Skill ★ 첫 정식 트리거** (Slice 1 ADR-027 + Slice 5 회고)
- **prompt-version-review Skill ★ 첫 정식 트리거** (Slice 1 분석 + Slice 4 적용, ADR-029)
- **contract-change Skill 본격 네 번째 (CC-003)** (prompt_registry + agent_io_contract v1.2.0)
- **multi-llm-validation formal 다섯 번째** (V1~V7 PASS — MOA orchestration)
- **agent-io-check Skill 네 번째 회귀** (agent_io_contract §5 ↔ critic.py drift 0)
- 3 ADR 신규 (ADR-027 MOA orchestrator + ADR-028 SSE progress integration + ADR-029 prompt_registry semver)
- pytest 223 → **249/249** (+26 신규) + smoke 14/14 + scenario_sim v4 20/20 (P-X2 여섯 번째)
- 신규 패턴: P-MOA-ORCHESTRATOR-001 + P-BEHAVIOR-PRESERVING-001 + P-X1-EFFECT-001 update (36연속) + P-VALIDATION-FORMAL-001 update (다섯 번째)
- 사용자 결정 3건 mapping 완료 (Scope 3개 모두 / Critic conservative adapter / SSE progress_store 브릿지)
- large phase 실측 ~12~14h (추정 12~16h 내)
