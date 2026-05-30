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

**🟡 pending_user_decision** — Phase M0 ✅ done (2026-05-31, ★ meta-phase) + Phase 9.5 ✅ done (2026-05-31)

Phase M0 (Meta-Factory Prep, ★ meta-phase) ✅ done (2026-05-31) — L3 Meta-Harness Factory skeleton + harness-factory Skill proposal-only. ★ 런타임 변경 0 (A9). meta-phase detour 종료 — 다음 제품 phase는 사용자 결정 대기 (옵션 A Phase 10 통합 / B Phase 11+).

- Phase M0 archive: `phases/archive/phase-M0-meta-factory/` (참조 가능 — ★ meta-phase, closing_notes + 회고 + L3 Meta-Factory skeleton + harness-factory Skill proposal-only + 사용자 §9 보고 + 다음 단계 1~4)
- Phase 9.5 archive: `phases/archive/phase-9.5-eval-run/` (참조 가능 — closing_notes + 회고 + eval-run 정식화 baseline + generate.py deviation + 다음 옵션 A/B)
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

- **A. Phase 10 — MVP 통합 테스트** (6~8h)
  - MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical-only) → save → select → feedback → SSE progress)
  - Phase 1~9.5 누적 baseline 통합 회귀 + eval-run golden_set 회귀 baseline 활용
  - P-AUX-2 brand_memory_extractor agent 실 구현 (Phase 9 schema + 적재 경로 준비 완료) + 실 LLM eval mode 운영 활성 + RAG eval_rubric golden_set 정식화 + 배포 테스트 게이트 A~G 준비
- **B. 다른 우선순위** (Phase 11+)
  - 4계층 full linkage (plan_options/video_projects — selected_plans 실 plans 정합 → idealized schema 연결, 누적 2회)
  - 사용자 데이터 자동 promotion (rag-update Skill 두 번째 — feedback→candidate pending 적재 완료)
  - SSE full async worker (누적 2회) / prompt A/B 실행 인프라 / Supabase SQL function 정의 / cost-review Skill

**Phase M0 핵심 성과 (★ meta-phase, 런타임 변경 0)**:
- **P-X1 §SELF-VERIFICATION 50연속 PASS** (Phase 3 5 + ... + Phase 9.5 5 + Phase M0 3 — ★ 첫 meta-phase 0건 재발)
- **★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9)** — backend/fastapi 0 / apps/web 0 (PlanCard·component_map 0줄) / db/migrations 0 (git diff 게이트 PASS, smoke Step 1)
- **L3 Meta-Harness Factory skeleton** — meta_factory/ 7 루트(README L1/L2/L3 + factory_contract 8 규칙 proposal-first + domain_brief/harness_blueprint schema + architecture_patterns 6 + Dreammate 매핑 + generation_workflow 11단계 + validation_workflow 6 검증) + templates 6 scaffold + 현재 하네스 blueprint 실측 역정리 + outputs 격리
- **harness-factory Skill proposal-only (21번째, 키워드 scoped 충돌 0)** — domain_brief → blueprint 초안 + scaffold 제안 + 충돌 분석. harness-audit/meta-retrospective/phase-start 와 충돌 0 (우선순위 표 편입). generated harness 자동 active 금지
- **validation_workflow ↔ eval-run 연동** — 검증 5는 eval-run Skill §3~§6 cross-ref (별도 평가 체계 신설 X)
- **multi-llm-validation formal 여덟 번째** (V1~V6 PASS — ★ 첫 meta-phase) + **contract-change CC-006** (INDEX harness-factory #21 등록 — Skill 도 contract 처럼 취급)
- ADR-035 (L3 Meta-Factory 도입) + pytest 339 유지 + smoke_test_phase_M0 6/6 + scenario_sim v7 33/33 (P-X2 아홉 번째) + Skill 20→21
- 신규 패턴: P-META-FACTORY-001 + P-X1-EFFECT-001 update (50연속) + P-VALIDATION-FORMAL-001 update (여덟 번째)
- ★ meta-phase 격리 성공 — 제품 phase 흐름 무오염 (phase-M0 번호 분리, next_phase_status 보존)
- 다음 단계: harness-factory dry-run / trigger validation 샘플 / with-without 비교 샘플 (Phase M1+) / Phase 10 연결 (meta_factory blueprint = 온보딩·감사 baseline)
- meta-phase 실측 ~4~7h

**Phase 9.5 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 47연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6 + Phase 9.5 5)
- **PlanCard.tsx 35연속 0줄** (… + Phase 9 6 + Phase 9.5 5 — frontend canonical 전환에서도 wrapper)
- **component_map.md 45연속 0줄** (… + Phase 9 6 + Phase 9.5 5)
- **eval-design + eval-run Skill 둘 다 첫 정식 트리거 (ADR-033)** — golden_set 11 케이스 mock-deterministic 회귀 runner (CI 가능 비용 0) + schema 100%/structural 채점 + 임계값 게이트 (schema 100% / 점수 ±0.3 / 광고 / 차단 단어) + regression_results
- **revise effect eval (Phase 4.5 D6 해소)** — revise attempt별 canonical overall_score 0–1 delta (mean_delta 0.092 / improved 60% / regressed 20%)
- **Critic deprecated 0–5 Full 제거 (ADR-034 + CC-005)** — select_best_plan_index fallback + CriticEvaluation Optional 0–5 필드 제거 → canonical(0–1) 단일 표준 (eval 제거 전/후 동일 입증, run_critic 0–5 불변 P-007 NG3, warnings 16→0)
- **generate.py canonical wiring 보강** — Phase 1 endpoint normalize 누락 회귀 방지 (향후 신규 critic consumer normalize_to_canonical 경유 필수)
- **frontend canonical 전환** — lib/types.ts CriticEvaluation canonical + page.tsx canonical 렌더 (PlanCard·component_map 0줄)
- **contract-change Skill 본격 여섯 번째 (CC-005)** (output_schema §9 + agent_io_contract §5 canonical-only + db_schema)
- **multi-llm-validation formal 일곱 번째** (V1~V7 PASS — eval mock-deterministic + deprecated 제거 경계 + 임계값 게이트)
- **agent-io-check Skill 여섯 번째 회귀** (deprecated 제거 후 agent_io_contract §5 canonical-only ↔ critic.py drift 0)
- 2 ADR 신규 (ADR-033 eval-run harness + ADR-034 Critic deprecated 0–5 Full 제거)
- pytest 293 → **339/339** (+46 신규) + smoke 16/16 + scenario_sim v6 30/30 (P-X2 여덟 번째) + eval gate PASS
- 신규 패턴: P-EVAL-HARNESS-001 + P-DEPRECATED-REMOVAL-001 + P-X1-EFFECT-001 update (47연속) + P-VALIDATION-FORMAL-001 update (일곱 번째)
- 사용자 결정 2건 mapping 완료 (Critic deprecated Full 제거 eval 검증 후 / eval mock-deterministic primary + RAG eval_rubric Phase 10+)
- eval mini-phase 실측 ~7~10h (추정 6~10h 내)
