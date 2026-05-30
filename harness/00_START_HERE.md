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

**🟡 pending_user_decision** — Phase 9 ✅ done (2026-05-31)

Phase 9 ✅ done (2026-05-31). 다음 phase는 사용자 결정 대기 (옵션 A Phase 9.5 eval-run / B Phase 10 통합 / C Phase 11+).

- Phase 9 archive: `phases/archive/phase-9-result-feedback/` (참조 가능 — closing_notes + 회고 + 결과저장/피드백 baseline + 다음 옵션 A/B/C)
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

- **A. Phase 9.5 — eval-run Skill 정식화** (4~6h)
  - golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 7회 deferred 해소)
  - Critic deprecated 0–5 fallback 완전 제거 (Phase 9 canonical live 활성 → 다음 단계, Phase 6 ADR-018 + Phase 8 + Phase 9 누적 3회)
  - 간이 RAG eval_rubric → 정식 (Phase 7 개선 제안 §6)
  - eval-design + eval-run Skill 첫 정식 트리거 baseline (Phase 9 canonical live 활성으로 eval baseline 준비 완료)
- **B. Phase 10 — MVP 통합 테스트** (6~8h)
  - MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical) → save → select → feedback → SSE progress)
  - Phase 1~9 누적 baseline 통합 회귀
  - P-AUX-2 brand_memory_extractor agent 실 구현 (Phase 9 schema + 적재 경로 준비 완료) + 배포 테스트 게이트 A~G 준비
- **C. 다른 우선순위** (Phase 11+)
  - 4계층 full linkage (plan_options/video_projects — selected_plans 실 plans 정합 → idealized schema 연결, 누적 2회)
  - 사용자 데이터 자동 promotion (rag-update Skill 두 번째 — feedback→candidate pending 적재 완료)
  - SSE full async worker (누적 2회) / prompt A/B 실행 인프라 / Supabase SQL function 정의 / cost-review Skill

**Phase 9 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 42연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6)
- **PlanCard.tsx 30연속 0줄** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 — frontend slice 있어도 wrapper)
- **component_map.md 40연속 0줄** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6)
- **결과 저장(selected_plans) + 피드백(feedback_events) 영속화 graceful (ADR-030)** — PlansRepo graceful 패턴 + reason 저장 전 PII 마스킹 + RLS user 격리 (실 plans 정합)
- **normalize_to_canonical wiring (ADR-032)** — critic_evaluation canonical 0–1 live + deprecated 0–5 병행 회귀 0 (additive 비파괴 사본, 기존 pytest 249 수정 0, warnings 67→16)
- **Brand Memory 준비 (ADR-031)** — schema + BrandMemoryRepo + feedback→candidate(pending) 적재 경로 + P-AUX-2 설계 명세 (agent 미구현 Phase 10+)
- **피드백 UI inline (Slice 5)** — 선택 버튼 + 반려 이유 textarea page.tsx inline (PlanCard·component_map 0줄, wrapper)
- **security-review Skill 두 번째 정식** (Slice 1 — 피드백 reason PII T1~T6, P-SECURITY-REVIEW-001 강화)
- **contract-change Skill 본격 다섯 번째 (CC-004)** (db_schema.md selected_plans/feedback_events 실 plans 정합)
- **multi-llm-validation formal 여섯 번째** (V1~V7 PASS — selection/feedback + normalize wiring + Brand Memory 준비)
- **agent-io-check Skill 다섯 번째 회귀** (normalize wiring 후 agent_io_contract §5 ↔ critic.py drift 0)
- 3 ADR 신규 (ADR-030 feedback/selection + ADR-031 Brand Memory prep + ADR-032 normalize_to_canonical wiring)
- pytest 249 → **293/293** (+44 신규, 기존 수정 0) + smoke 15/15 + scenario_sim v5 25/25 (P-X2 일곱 번째)
- 신규 패턴: P-FEEDBACK-LOOP-001 + P-CANONICAL-WIRING-001 + P-X1-EFFECT-001 update (42연속) + P-VALIDATION-FORMAL-001 update (여섯 번째)
- 사용자 결정 3건 mapping 완료 (Brand Memory 준비만 agent Phase 10+ / 피드백 UI wrapper / normalize wiring deprecated 병행)
- large phase 실측 ~10~13h (추정 10~14h 내)
