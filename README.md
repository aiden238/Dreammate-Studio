# Dreammate Studio — 영상기획 AI 에이전트 플랫폼

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤,  
> 검증 에이전트가 기획 품질을 평가·개선하는 **영상기획 특화 AI 에이전트**.

영상 제작 AI가 아니라 **영상기획 AI 에이전트**입니다.

---

## 현재 상태

| 항목 | 내용 |
|---|---|
| **Phase** | 🟡 pending_user_decision (Phase M0 ✅ done 2026-05-31 ★ meta-phase + Phase 9.5 ✅ done 2026-05-31) — 옵션 A Phase 10 통합 / B Phase 11+ |
| **이전 Phase** | Phase M0 — Meta-Factory Prep ✅ done (2026-05-31, ★ meta-phase, 3 Slices + A1~A10 + M1~M3 + ★ 런타임 변경 0 A9 + P-X1 50연속 + L3 Meta-Harness Factory skeleton (meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs) + factory_contract 8 규칙 proposal-first + harness-factory Skill ★ 신규 proposal-only (21번째, 키워드 scoped 충돌 0) + ADR-035 + CC-006 + multi-llm-validation formal 여덟 번째 (첫 meta-phase) + pytest 339 유지 + smoke_test_phase_M0 6/6 + scenario_sim v7 33/33 (P-X2 아홉 번째) + Skill 20→21 + P-META-FACTORY-001 신규 + 실측 ~4~7h) |
| **하네스 규모** | ~87,800줄 (Phase M0 ~+2400 — meta_factory skeleton ~+1600 / harness-factory Skill + INDEX ~+250 / proposal + CC-006 ~+180 / scripts smoke_test_phase_M0 + scenario_simulation v7 ~+180 / meta retrospective + patterns + skill_usage_log + closing_notes ~+200. ★ 런타임 0줄) |
| **Skill 구조** | `.claude/skills/` 단일 (**21개**, v1.3.0 + phase-complete v1.2.0 — 50연속 P-X1 입증 + multi-llm-validation formal 여덟 번째 입증 + harness-factory ★ 신규 proposal-only (#21, 키워드 scoped) + contract-change CC-006 + P-META-FACTORY-001 신규) |
| **Repository** | https://github.com/aiden238/Dreammate-Studio (Private) |

---

## 핵심 흐름

```text
사용자 입력
→ 의도 분석 (Discovery Wizard 또는 Quick Mode 자동 분기)
→ 부족한 정보 질문 (Discovery: 5 카드, Quick: 1–2 질문)
→ 한 줄 기획 방향 승인
→ LLM Wiki / RAG Lite 검색
→ 영상기획안 생성 (Phase 1: 1개, Phase 4+: 3개)
→ Critic Agent 검증 (revise 최대 2회)
→ 결과 저장
→ 사용자 피드백 저장 (Brand Memory 자동 추출)
```

**UX 분기 조건:**  
- 신규 / Brand 없음 → **Discovery Wizard** (5단계 카드)  
- 기존 Series → **Quick Mode** (1–2 질문만)

---

## 폴더 구조

```
Dreammate_Studio/
├── README.md                  ← 이 파일
├── .gitignore
├── harness/                   ← 하네스 (운영 중)
│   ├── 00_START_HERE.md       ← 첫 진입 시 여기부터
│   ├── CLAUDE.md              ← 기획/설계 모델 라우터
│   ├── AGENTS.md              ← 구현/QA 모델 라우터
│   ├── PROJECT_STATE.md       ← 현재 작업 상태
│   ├── PHASE_REGISTRY.md      ← Phase 목록 (0~30)
│   ├── .claude/skills/        ← Skill 21개 (단일 폴더, applies_to 태그 + harness-factory L3)
│   ├── ai_system/             ← MOA Lite + RAG Lite 구조
│   ├── apps/web/              ← Next.js PWA 설계
│   ├── backend/               ← FastAPI + Spring (placeholder)
│   ├── docs/contracts/        ← 모든 결정의 단일 진실 소스
│   ├── eval/                  ← 평가 체계 + golden_set
│   ├── knowledge/             ← LLM Wiki + RAG 지식
│   ├── meta/                  ← 운영 가이드 + 회고
│   ├── phases/active/         ← 현재 Phase 문서
│   ├── phases/archive/        ← 완료 Phase (기본 참조 금지)
│   ├── product/               ← 비전 + 범위 + 로드맵
│   └── tests/ packages/ logs/ ← Phase 진행에 따라 채움
└── _staging/                  ← 이식 소스 (참조용, 변경 금지)
```

---

## Phase 이력

| Phase | 이름 | 상태 | 완료일 |
|---|---|---|---|
| 0 | 하네스 초기화 (Migration) | ✅ done | 2026-05-26 |
| 1 | MVP 기본 플로우 | ✅ done | 2026-05-26 |
| 2 | design.md 기반 PWA 설계 | ✅ done | 2026-05-27 |
| 3 | Next.js PWA 기본 UI 구현 | ✅ done | 2026-05-28 |
| 4 | FastAPI 기본 백엔드 구현 (확장) | ✅ done | 2026-05-28 |
| 4.5 | Critic Revise Loop + Rewriter + Z-X3 + P-X2 | ✅ done | 2026-05-28 |
| 6 | Output Schema + Agent IO Stabilization | ✅ done | 2026-05-29 |
| 5 | DB / Auth / RLS / SSE | ✅ done | 2026-05-29 |
| 5.5 | Legacy DB Consolidation + Validation 강화 + Phase 7 Prep | ✅ done | 2026-05-29 |
| 7 | RAG Lite (candidate_knowledge 5단계 MVP 전부) | ✅ done | 2026-05-29 |
| 8 | MOA Lite 본격 (orchestrator 추출 + SSE worker + prompt_registry 정식화) | ✅ done | 2026-05-29 |
| 9 | 결과 저장 + 피드백 (selected_plans + feedback_events 영속화 + normalize wiring + Brand Memory 준비 + 피드백 UI) | ✅ done | 2026-05-31 |
| 9.5 | eval-run 정식화 + Critic deprecated 0–5 Full 제거 | ✅ done | 2026-05-31 |
| M0 | Meta-Factory Prep (★ meta-phase — L3 Meta-Harness Factory skeleton) | ✅ done | 2026-05-31 |
| **next** | **🟡 pending_user_decision** (A Phase 10 통합 / B Phase 11+) | **next** | — |
| 10 | MVP 통합 테스트 | planned | — |
| 11~30 | 안정화 / 확장 / 고도화 | future | — |

Sprint S0~S5 (Phase 0) 모두 완료 — 6개 commit, 11/11 acceptance 통과.
Phase 1 — 13 commit, 8/8 implementation acceptance + pytest 62/62 + smoke 5/5 PASS.
Phase 2 — 6 commit, 10/10 acceptance + 변경성 시뮬레이션 5/5 PASS + audit_naming 0 drift.
Phase 3 — 7 commit, 10/10 acceptance + audit_naming + audit_page_component 0 drift + smoke 7/7 PASS + P-X1 5/5 PASS + component_map 6연속 0줄.
Phase 4 — 5 commit, 10/10 acceptance + audit_naming + audit_page_component 0 drift (D-1 Slice 4 해소) + smoke 8/8 PASS + **P-X1 §SELF-VERIFICATION 9연속 PASS** + **component_map.md 15연속 0줄** + **PlanCard.tsx 4연속 0줄** + **GPT 검토 채택 효과 ▼66% 시간 (6→4 Slices)**.
Phase 4.5 — 4 commit, 10/10 acceptance + 3/3 메타 검증 + audit 0 drift × 2 + smoke 9/9 PASS + scenario_simulation 5/5 PASS (**P-X2 자동 게이트 첫 작동**) + pytest 109/109 + **P-X1 13연속 PASS** + **PlanCard.tsx 9연속 0줄** + **component_map.md 19연속 0줄** + **multi-llm-validation formal 첫 트리거**.
Phase 6 — 4 commit, 10/10 acceptance + 3/3 메타 검증 + audit 0 drift × 2 + smoke 10/10 PASS + scenario_simulation 5/5 (**P-X2 자동 게이트 두 번째**) + schema_stress 5/5 (**P-X2 v2 신규**) + pytest 144/144 + **P-X1 17연속 PASS** + **PlanCard.tsx 12연속 0줄** + **component_map.md 22연속 0줄** + **Critic canonical 결정 (ADR-018) + Rewriter v1.1.0 (ADR-019) + agent-io-check 첫 정식 + contract-change 본격 + multi-llm-validation formal 두 번째**.
Phase 5 — 5 commit, 10/10 acceptance + 4/4 메타 검증 + audit_naming 0 drift + audit_page_component 2 intended drift WARN + smoke 12/12 PASS (11 PASS + 1 WARN intended) + scenario_simulation v2 10/10 (**P-X2 자동 게이트 세 번째**) + pytest 170/170 + **P-X1 22연속 PASS** + **PlanCard.tsx 17연속 0줄** + **component_map.md 27연속 0줄** + **Supabase + JWT httpOnly + RLS (ADR-021) + SSE 4단계 (ADR-022) + ADR-020 Supabase + security-review 첫 정식 + 두 번째 final + contract-change 두 번째 본격 (db_schema.md) + multi-llm-validation formal 세 번째 정식 확정 + agent-io-check 두 번째 회귀**.
Phase 5.5 — 4 commit, 8/8 acceptance (A1~A8) + 2/2 메타 검증 (M1~M2) + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 유지) + smoke 12/12 (재실행) + scenario_simulation v2 10/10 (**P-X2 자동 게이트 네 번째**) + pytest 172/172 (+2 legacy deprecation 검증) + **P-X1 26연속 PASS** + **PlanCard.tsx 18연속 0줄** + **component_map.md 28연속 0줄** + **ADR-023 Legacy DB 옵션 A + ADR-024 Phase 7 RAG scope evolution + external × 3 self-strengthen V-form + Brand Memory Phase 9+ confirm + legacy backward-compat 100% + P-LEGACY-CONSOLIDATION-001 신규 후보 + consolidation mini-phase 실측 ~4-5h**.
Phase 7 — 5 commit, 10/10 acceptance (A1~A10) + 4/4 메타 검증 (M1~M4) + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + smoke 13/13 (12 PASS + 1 WARN intended) + scenario_simulation v3 15/15 (**P-X2 자동 게이트 다섯 번째**, S11~S15 RAG 5개 추가) + pytest 172 → 223/223 (+51 신규 promotion/quality_filter/eval_rubric/chunking/embedding/retrieval/integration) + **P-X1 31연속 PASS** + **PlanCard.tsx 19연속 0줄** + **component_map.md 29연속 0줄** + **ADR-025 RAG architecture + ADR-026 5단계 promotion logic + rag-design ★ 첫 정식 + rag-update ★ 첫 정식 + contract-change 본격 세 번째 (rag_data_contract.md §18) + multi-llm-validation formal 네 번째 (V1~V7) + agent-io-check 세 번째 회귀 + graceful 5종 marker 표준화 + Phase 1 legacy ↔ Phase 7 신규 공존 누적 2회 (P-LEGACY-CONSOLIDATION-001 정식 채택 임박) + P-RAG-5STAGE-001/P-RAG-GRACEFUL-001 신규 + 5단계 파이프라인 전부 MVP + pgvector retrieval + LLM Wiki 보조 + 실측 ~13~14h**.
Phase 8 — 5 commit, 10/10 acceptance (A1~A10) + 5/5 메타 검증 (M1~M5) + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + smoke 14/14 (13 PASS + 1 WARN intended) + scenario_simulation v4 20/20 (**P-X2 자동 게이트 여섯 번째**, S16~S20 MOA 5개 추가) + pytest 223 → 249/249 (+26 신규 moa_orchestrator/sse_integration/prompt_registry_consistency) + **P-X1 36연속 PASS** + **PlanCard.tsx 24연속 0줄** + **component_map.md 34연속 0줄** + **ADR-027 MOA orchestrator behavior-preserving + ADR-028 SSE progress integration + ADR-029 prompt_registry semver + ai-architecture-review ★ 첫 정식 + prompt-version-review ★ 첫 정식 + contract-change 본격 네 번째 (CC-003 prompt_registry semver + agent_io_contract v1.2.0) + multi-llm-validation formal 다섯 번째 (V1~V7) + agent-io-check 네 번째 회귀 + MOA Orchestrator 추출 (plans.py 659→243 god-function 분해) + behavior-preserving (Envelope byte-identical, 기존 test 수정 0 의도된 2 version assertion 제외) + SSE 실 stage 통합 (progress_store 브릿지) + Critic v1.1.0 conservative adapter (Phase 6 canonical 불변) + prompt_registry semver 정식화 (NG8 누적 3회 해소) + P-MOA-ORCHESTRATOR-001/P-BEHAVIOR-PRESERVING-001 신규 + 실측 ~12~14h**.
Phase 9 — 6 commit, 10/10 acceptance (A1~A10) + 4/4 메타 검증 (M1~M4) + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + smoke 15/15 (14 PASS + 1 WARN intended) + scenario_simulation v5 25/25 (**P-X2 자동 게이트 일곱 번째**, S21~S25 feedback/selection 5개 추가) + pytest 249 → 293/293 (+44 신규 selection_feedback/plans_feedback_api/critic_canonical_wiring/brand_memory_prep, 기존 수정 0) + **P-X1 42연속 PASS** + **PlanCard.tsx 30연속 0줄** + **component_map.md 40연속 0줄** + **ADR-030 feedback/selection persistence + ADR-031 Brand Memory prep (P-AUX-2 설계 agent 미구현 Phase 10+) + ADR-032 normalize_to_canonical wiring + security-review 두 번째 정식 (피드백 reason PII) + contract-change 본격 다섯 번째 (CC-004 db_schema.md selected_plans/feedback_events 실 plans 정합) + multi-llm-validation formal 여섯 번째 (V1~V7) + agent-io-check 다섯 번째 회귀 + 결과저장(selected_plans) + 피드백(feedback_events) 영속화 graceful + PII 마스킹 + normalize_to_canonical wiring (critic_evaluation canonical 0–1 live, deprecated 0–5 병행 회귀 0, warnings 67→16) + Brand Memory 준비 (feedback→candidate pending 적재, agent Phase 10+) + 피드백 UI inline (PlanCard·component_map 0줄, wrapper) + P-FEEDBACK-LOOP-001/P-CANONICAL-WIRING-001 신규 + 실측 ~10~13h**.
Phase 9.5 — 5 commit, 10/10 acceptance (A1~A10) + 4/4 메타 검증 (M1~M4) + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + smoke 16/16 (15 PASS + 1 WARN intended) + scenario_simulation v6 30/30 (**P-X2 자동 게이트 여덟 번째**, S26~S30 eval/deprecated 5개 추가) + eval gate PASS (eval_run.ps1 — schema 1.0 / pass 1.0 / revise mean_delta 0.092 / improved 0.6 / regressed 0.2) + pytest 293 → 339/339 (+46 신규 eval_runner/revise_effect + test_critic 의도 delta) + **P-X1 47연속 PASS** + **PlanCard.tsx 35연속 0줄** + **component_map.md 45연속 0줄** + **ADR-033 eval-run harness (mock-deterministic primary + 실 LLM mode flag + 임계값) + ADR-034 Critic deprecated 0–5 Full 제거 + eval-design ★ 첫 정식 + eval-run ★ 첫 정식 + contract-change 본격 여섯 번째 (CC-005 output_schema §9 + agent_io_contract §5 canonical-only) + multi-llm-validation formal 일곱 번째 (V1~V7) + agent-io-check 여섯 번째 회귀 + golden_set 11 케이스 mock-deterministic 회귀 runner + revise effect eval (Phase 4.5 D6 해소) + Critic deprecated 0–5 Full 제거 (canonical 0–1 단일 표준, eval 제거 전/후 동일 입증, run_critic 0–5 불변 P-007 NG3, warnings 16→0) + generate.py canonical wiring 보강 (Phase 1 endpoint normalize 누락 회귀 방지) + frontend canonical 전환 (lib/types.ts + page.tsx, PlanCard·component_map 0줄) + P-EVAL-HARNESS-001/P-DEPRECATED-REMOVAL-001 신규 + 실측 ~7~10h**.
Phase M0 — 3 commit, ★ **meta-phase** (제품 phase 아님 — L3 Meta-Harness Factory skeleton) + 10/10 acceptance (A1~A10) + 3/3 메타 검증 (M1~M3) + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + **smoke_test_phase_M0 6/6 PASS** (경량 meta-phase — A9 런타임 0 + pytest 339 + audit_naming + meta_factory 구조 + Skill #21 + frontend 0) + scenario_simulation v7 33/33 (**P-X2 자동 게이트 아홉 번째**, SM1~SM3 meta_factory 3개 추가) + pytest 339 유지 (런타임 무관) + **P-X1 50연속 PASS** + **PlanCard.tsx 35연속 0줄** + **component_map.md 45연속 0줄** + **★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9 — git diff fff913e..HEAD backend/apps/migrations = 0) + ADR-035 L3 Meta-Factory 도입 (L1/L2/L3 + proposal-first + payoff deferred) + CC-006 INDEX harness-factory #21 Skill 등록 + harness-factory Skill ★ 신규 proposal-only (21번째, 키워드 scoped 충돌 0 — harness-audit/meta-retrospective/phase-start 비침범) + multi-llm-validation formal 여덟 번째 (V1~V6, ★ 첫 meta-phase) + contract-change 일곱 번째 (CC-006, Skill 도 contract 취급) + harness-audit 키워드 충돌 검토 (충돌 0) + L3 Meta-Harness Factory skeleton (meta_factory/ 7 루트 + templates 6 scaffold + 현재 하네스 blueprint 실측 역정리 + outputs 격리) + factory_contract 8 규칙 (proposal-first 헌법) + domain_brief/harness_blueprint schema + 6 architecture 패턴 + Dreammate 매핑 + validation_workflow ↔ eval-run 연동 + Skill 20→21 + P-META-FACTORY-001 신규 + ★ meta-phase 격리 제품 흐름 무오염 + 실측 ~4~7h**.

---

## 기술 스택

| 계층 | MVP (Phase 1~10) | 확장 (Phase 21+) |
|---|---|---|
| Frontend | Next.js 14 PWA | Expo React Native |
| Backend | FastAPI (Python) | Spring Boot |
| DB | PostgreSQL + pgvector (Supabase) | — |
| LLM | gpt-4o-mini (기본) / gpt-4o (Critic) | Custom Fine-tune |
| RAG | pgvector + candidate_knowledge 5단계 | Custom RAG |

---

## 확정 결정 사항 (주요 25개)

1. Discovery + Quick 하이브리드 UX (1.6x 비용 수용)
2. Mode 자동 분기: 신규 → Discovery, 기존 Series → Quick
3. Discovery 단계당 카드 5장 (AI 4 + 직접입력 1)
4. Plan 후보 3개 생성 (Phase 4+, Phase 1은 1개)
5. Critic revise 최대 2회 (무한 루프 차단)
6. 4계층 데이터 모델 (Brand / Domain / Series / VideoProject)
7. Intent Filter (영상기획 외 입력 차단)
8. Brand Memory 자동 추출 + 사용자 검토 가능
9. 광고적 표현 차단 단어 검사 ("최고의", "혁신적인" 등)
10. 30–60초 대기 시 4단계 progress + 부분 결과 노출
11. Skill 21개, `.claude/skills/` 단일 폴더 (harness-factory L3 proposal-only 포함)
12. 영상 자동 편집 / TTS / BGM / 자동 업로드 → MVP 영구 제외

전체 목록: `harness/PROJECT_STATE.md`의 `confirmed_decisions`

---

## 작업 진입

```
1. harness/00_START_HERE.md  ← 첫 진입 시 여기부터
2. harness/PROJECT_STATE.md  ← 현재 작업 위치 확인 (pending_user_decision, Phase 9.5 done)
3. harness/phases/archive/phase-9.5-eval-run/closing_notes.md  ← Phase 9.5 종료 메모 + generate.py deviation + 다음 옵션 A/B + 운영 권장
4. harness/phases/archive/phase-9-result-feedback/closing_notes.md  ← Phase 9 종료 메모 (참조)
5. harness/phases/archive/phase-8-moa-lite/closing_notes.md  ← Phase 8 종료 메모 (참조)
6. harness/phases/archive/phase-7-rag-lite/closing_notes.md  ← Phase 7 종료 메모 (참조)
7. harness/phases/archive/phase-5-db-auth/closing_notes.md  ← Phase 5 DB/Auth/RLS/SSE baseline (참조)
8. harness/phases/archive/phase-6-output-schema-stabilization/  ← Phase 6 contract 안정화 baseline (참조)
9. harness/apps/web/design_handoff.md  ← Phase 2 핵심 산출물 (변경 가이드)
10. harness/meta/retrospectives/phase-9.5.md  ← Phase 9.5 회고 + 개선 제안 §1~3
11. harness/meta/retrospectives/phase-9.md  ← Phase 9 회고 (참조)
12. harness/meta/patterns.md  ← P-X1-EFFECT-001 47연속, P-EVAL-HARNESS-001/P-DEPRECATED-REMOVAL-001 신규, P-VALIDATION-FORMAL-001 일곱 번째 입증
13. harness/docs/decisions/phase_9_5_eval_run_harness.md  ← ADR-033 (eval-run harness mock-deterministic + 임계값 + §eval-design)
14. harness/docs/decisions/phase_9_5_critic_deprecated_removal.md  ← ADR-034 (Critic deprecated 0–5 Full 제거, run_critic 0–5 불변 P-007 NG3)
15. harness/docs/contracts/output_schema.md §9 + agent_io_contract.md §5  ← Phase 9.5 Slice 4 (CC-005 — Critic canonical-only)
16. harness/eval/regression_results/phase-9.5_baseline.md  ← Phase 9.5 eval 회귀 결과 (golden_set 11 케이스 mock-deterministic)
```

---

## 주의사항

- `docs/contracts/`는 무단 변경 금지 — `contract-change` Skill 절차 필수
- `phases/archive/`는 기본 참조 금지
- 영상 제작 기능은 MVP에 넣지 않는다 (mvp_non_goals.md 참조)
- contract와 다른 문서가 충돌 시 → contract 우선
