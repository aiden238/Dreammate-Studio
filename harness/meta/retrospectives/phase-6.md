# Retrospective: Phase 6 — Output Schema + Agent IO Stabilization

> 작성일: 2026-05-29
> 종류: stabilization mini-phase (Phase 5 DB/Auth 진입 전 contract 안정화)
> 범위: Phase 6 전체 (entry → Slice 1~4 → final QA → archive)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete v1.2.0 절차 7단계 (회고) + §1.6 변경성 시뮬 자동 게이트 두 번째 작동

---

## 사실 요약

Phase 6 (Output Schema + Agent IO Stabilization — Phase 5 DB/Auth 진입 전 contract 안정화 mini-phase)를 **2026-05-29 단일 일자**에 진입부터 archive까지 완수.

진입: phase-start v1.3.0 §6 4점검 PASS + 사용자 결정 (옵션 B 변형 Phase 6 선행 → Phase 5 / 6→4 Slice 압축 / multi-llm-validation formal 두 번째 / 모두 sub-agent / prompt_registry Phase 7+ defer / Critic fallback deprecated 유지). entry commit `8d7232c`.

4 Slices를 4 Waves로 분해 (모두 sequential + 모두 sub-agent dispatch):
- Wave 1 (Slice 1, sub-agent A, `8d7232c`) — Pre-Entry: validations self V1~V5 + external placeholder + contract gap analysis
- Wave 2 (Slice 2, sub-agent B, `dad38c5`) — contract-change 본격 트리거: output_schema.md §9 canonical (overall_score + dimensions) + §10 Body.revise_history Optional + agent_io_contract §6 Rewriter v1.0.0 → v1.1.0 + critic.py select_best_plan_index canonical priority + DeprecationWarning + rewriter.py RewriterInput/RewriterOutput Pydantic + ADR-018/019 + pytest 109 → 122 (+13)
- Wave 3 (Slice 3, sub-agent C, `d0ab5a8`) — Schema Stress + Frontend Types: types.ts CriticEvaluation + ReviseAttempt + CriticDimensions canonical mirror + test_schema_stress.py 22 케이스 + scripts/schema_stress_test.ps1 (P-X2 v2) + pytest 122 → 144 (+22)
- Wave 4 (Slice 4, sub-agent D, final) — Close: smoke 10/10 + scenario_simulation 5/5 (P-X2 두 번째 자동 게이트) + schema_stress 5/5 + agent-io-check 첫 정식 + design-review impl §B + retrospective + patterns + archive + state docs

총 4 sub-agent dispatch (100% sub-agent 패턴, Phase 4.5 정신 계승). 충돌 0건. **§SELF-VERIFICATION 4/4 PASS**.

핵심 회귀 baseline 보존:
- **PlanCard.tsx 0줄 변경 3연속 (Phase 6 Slice 1~3, Slice 4 close)** → 누적 **12연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3) ★
- **component_map.md 0줄 변경 3연속 (Phase 6 Slice 1~3)** → 누적 **22연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3) ★
- pytest 109/109 baseline → **144/144** (+35 신규: critic canonical/best-plan +6 + rewriter Pydantic +7 + schema_stress 22)
- smoke_test_phase_6 **10/10 PASS**
- scenario_simulation **5/5 PASS** (P-X2 두 번째 자동 게이트)
- schema_stress_test **5/5 PASS** (P-X2 v2 신규)
- audit_naming + audit_page_component **0 drift × 2** (Slice 1 entry + Slice 4 final)
- next build 10 routes / tsc 0 / lint clean (Phase 4.5 baseline 유지)

회고 핵심 발견:
- ★ **P-X1 §SELF-VERIFICATION 17연속 PASS**: Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 = 17 Slice 누적. P-AGENT-SCOPE-001 mitigation 17연속 입증.
- ★ **contract-change Skill 첫 본격 트리거**: Phase 1 CC-001 이후 첫 실 변경 통과 — output_schema.md + agent_io_contract.md 양쪽 동시 + 회귀 0. ADR-018 (Critic canonical) + ADR-019 (Rewriter v1.1.0) 작성.
- ★ **agent-io-check Skill 첫 정식 트리거**: Phase 4.5까지 0건 (informal Slice 2 정성 점검만) → Phase 6 Slice 4에서 첫 절차 트리거 → Rewriter v1.1.0 contract §6 ↔ rewriter.py + Critic canonical contract §9.4 ↔ critic.py select_best_plan_index 모두 정합 PASS.
- ★ **multi-llm-validation formal 두 번째 트리거**: Phase 4.5 첫 트리거 (V1~V4) 패턴을 Phase 6에 계승 (V1~V5). self + external placeholder 분리 패턴 두 번째 입증. **P-VALIDATION-FORMAL-001 정식 패턴 등록 확정**.
- ★ **P-X2 자동 게이트 두 번째 트리거**: Phase 4.5 첫 작동 → Phase 6 두 번째 작동 (5/5 PASS). P-X2-EFFECT-001 두 phase 누적 입증.
- ★ **GPT 검토안 정신 계승**: GPT 6 Slice 원안 → 4 Slice 압축 (▼33%) + 시간 8~12h 추정 → 실측 ~8h (시간 ▼20%). P-GPT-REVIEW-001 두 번째 적용 입증.
- ★ **DB 진입 전 contract 안정화 효과**: Critic verdict 4 fallback → 1 canonical + 3 deprecated. Rewriter v1.0.0 → v1.1.0 Pydantic 정식. revise_history Optional 정식 등록. Phase 5 DB schema 진입 전 schema drift 위험 0에 가까움. **P-CONTRACT-FIRST-001 신규 패턴 후보**.

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-29 단일일 (다중 세션, sub-agent 4 dispatch) |
| Total commits (Phase 6) | 4 (Slice 1 8d7232c + Slice 2 dad38c5 + Slice 3 d0ab5a8 + Slice 4 final) |
| 신규 파일 | ~10 (smoke_test_phase_6.ps1 + schema_stress_test.ps1 + test_schema_stress.py + retrospective + closing_notes + ADR-018 + ADR-019 + 2 validations + skill_usage_log entries) |
| 수정 파일 | ~10 (output_schema.md + agent_io_contract.md + api_contract.md + schemas/output.py + agents/critic.py + agents/rewriter.py + tests/test_critic.py + tests/test_rewriter.py + lib/types.ts + meta/skill_usage_log.md + PROJECT_STATE.md) |
| 줄 수 변화 | +~1450 (backend +650 / frontend +85 / tests +400 / contracts +200 / scripts +150 / meta+docs +400) |
| 신규 ADR | 2 (ADR-018 critic canonical + ADR-019 rewriter v1.1.0) |
| 변경된 contract | 3 (output_schema.md + agent_io_contract.md + api_contract.md) — **contract-change Skill 첫 본격 실 변경** |
| backend schemas 신규 모델 | ReviseAttempt (Phase 6 Slice 2) |
| backend agents 강화 | 2 (critic.py canonical + rewriter.py Pydantic) |
| Frontend routes 변화 | 0 (Phase 4 11 routes 유지) |
| Frontend types 신규 interface | CriticEvaluation + ReviseAttempt + CriticDimensions + CriticVerdictAction |
| pytest 결과 | **144/144 PASS** (Phase 4.5 109 baseline + Phase 6 신규 35) |
| pytest 신규 케이스 | 35 (Slice 2 +13 critic canonical/best-plan/rewriter Pydantic + Slice 3 +22 schema_stress) |
| audit_naming | 0 drift (Slice 1 + Slice 4) |
| audit_page_component | 0 drift (Slice 1 + Slice 4) |
| smoke_test_phase_6 | **10/10 PASS** (Phase 4.5 9 + schema_stress 1) |
| scenario_simulation | **5/5 PASS** (P-X2 두 번째 자동 게이트) |
| schema_stress_test | **5/5 PASS** (P-X2 v2 신규) |
| next build | 10 routes (Phase 4.5 baseline 유지) |
| tsc / lint | 0 errors / clean |
| Sub-agent dispatch | 4 (Slice 1~4 모두) |
| **P-X1 §SELF-VERIFICATION** | **4/4 PASS (Phase 6)** ★ |
| **P-X1 누적 streak** | **17연속 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4)** ★ |
| **PlanCard.tsx deviation** | **0건 (Phase 6 전체, 누적 12연속 — Phase 4 4 + Phase 4.5 5 + Phase 6 3)** ★ |
| **component_map.md deviation** | **0건 (Phase 6 전체, 누적 22연속 — Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3)** ★ |
| multi-llm-validation 트리거 | 1 formal self V1~V5 (두 번째) + 1 external placeholder |
| 식별된 P-pattern (Phase 6 신규) | 2 (P-CRITIC-CANONICAL-001 + P-CONTRACT-FIRST-001) + 1 update (P-X1-EFFECT-001 → 17연속) |
| Phase 6 deferred → Phase 5+/7+/9+ 이관 | Supabase / Auth / SSE D7 / DB migration / RAG sources / prompt_registry P-007/P-008 정식화 / revise effect eval / fallback 완전 제거 |
| 시간 추정 vs 실측 | 8~10h (multi_slice_plan) → 실측 ~8h (GPT 정신 계승 ▼20% 시간 절감) |

---

## 분석

### 잘된 것

1. **★ P-X1 17연속 PASS — 4 Slice 모두 sub-agent + 충돌 0건**: Phase 6 Slice 4개 모두 sub-agent dispatch (Phase 4.5 정신 계승). 각 sub-agent가 §SELF-VERIFICATION 수행하여 forbidden 영역 1줄도 침범 안 함. P-AGENT-SCOPE-001 mitigation **17연속 누적 입증**. mini-phase 형식에서도 효과 유지.

2. **★ contract-change Skill 첫 본격 실 변경 통과**: Phase 1 CC-001 (`plan_options` 명명 정리) 이후 contract 직접 변경은 0이었으나 Phase 6 Slice 2에서 **output_schema.md §9 + §10 + agent_io_contract.md §6 + api_contract.md §8.3** 3 contract 동시 변경 + 회귀 0건 통과. ADR-018 (Critic canonical) + ADR-019 (Rewriter v1.1.0) 작성하여 결정 근거 영구 기록. contract-change 절차 (제안 → 검토 → 승인 → 반영) 본격 baseline 확립.

3. **★ agent-io-check Skill 첫 정식 트리거**: Phase 4.5 informal Slice 2 정성 점검만 있었음 → Phase 6 Slice 4 첫 절차 따른 정식 점검. Rewriter v1.1.0 contract §6 ↔ `rewriter.py` 정합 PASS / Critic canonical contract §9.4 ↔ `critic.py::select_best_plan_index` 정합 PASS. 양쪽 모두 type_diff 0 / extra 0 / missing 0 / DeprecationWarning 발행 일치. **agent_io_contract drift 자동 탐지 baseline 확립**.

4. **★ multi-llm-validation formal **두 번째** 트리거 (V1~V5)**: Phase 4.5 V1~V4 패턴 계승 + Phase 6에서 V5 (frontend types ↔ backend 1:1 매핑) 추가하여 5 dimension self validation. self.md + external.md placeholder 분리 패턴 두 번째 입증 → **P-VALIDATION-FORMAL-001 정식 패턴 확정**.

5. **★ P-X2 자동 게이트 두 번째 트리거 + schema_stress P-X2 v2 신규**: phase-complete v1.2.0 §1.6에서 scenario_simulation.ps1 5/5 PASS (두 번째 작동) + Phase 6에서 schema_stress_test.ps1 신규 (P-X2 evolution v2 — pytest matrix + tsc + Pydantic import + frontend canonical key 검증, 5/5 PASS). 자동 게이트 누적 신뢰성 ↑ + schema drift 자동 탐지 baseline 확장.

6. **★ Critic canonical 결정 + fallback 4→1+3 deprecated**: Phase 4.5 회고에서 발견된 "4 fallback (overall_score_avg / scores / dimensions / eight_dim_scores) 혼재" 문제 → Phase 6 Slice 2에서 canonical (overall_score [0~1] + dimensions: dict[str, float]) 결정 + Phase 1~4.5 호환 deprecated 3 (DeprecationWarning 발행 + Phase 9+ eval-run 정식화 후 제거 결정). **P-CRITIC-CANONICAL-001 신규 패턴** — 다중 fallback → canonical + deprecated 축소 패턴 등록 후보.

7. **★ Rewriter contract v1.0.0 → v1.1.0 (ADR-019) Pydantic 도입**: `RewriterInput` / `RewriterOutput` Pydantic 모델 신규 (typing + frontend type mirror용). 기존 dict 반환은 backward-compat 유지 (`routers/plans.py` 0줄 변경 + 회귀 0). graceful 정책 (_rewriter_warning 마커) contract 명시 + 구현 일치.

8. **★ frontend types.ts canonical mirror — page.tsx 자동 호환**: Slice 3 sub-agent가 deprecated 필드를 non-optional 유지 결정 (Optional 강등 시 page.tsx `toFixed` 회귀 발견) → frontend mirror에서 backward-compat 자연 보존 + tsc 0 errors. **wrapper 패턴 (Phase 4.5) + canonical mirror 패턴 (Phase 6) 양립 입증**.

9. **★ Phase 5 DB/Auth 진입 전 contract 안정화 효과**: critic_evaluation schema canonical + revise_history Optional + recommended_plan_index Optional 모두 contract 정식 등록 → Phase 5 DB migration 시 schema drift 위험 ~0. **P-CONTRACT-FIRST-001 신규 패턴 후보** (큰 phase 진입 전 contract 안정화 패턴).

10. **★ GPT 검토안 6→4 Slice 압축 + 시간 ▼20% (P-GPT-REVIEW-001 두 번째 적용)**: Phase 4 GPT 검토 첫 적용 (▼66% 시간) → Phase 6 두 번째 적용 (▼20% 시간). GPT 6 Slice 원안 (8~12h) → 4 Slice (실측 ~8h). Slice 1 (Pre-Entry) + Slice 2 (Critic + Rewriter) + Slice 3 (Schema Stress + Frontend) + Slice 4 (Close). over-engineering 회피 + GPT 정신 정식 채택.

11. **pytest 109/109 → 144/144 (+35 신규) 회귀 0**: Phase 4.5 baseline + Slice 2 신규 13 (critic canonical 6 + rewriter Pydantic 7) + Slice 3 신규 22 (schema_stress 22 케이스). 모두 PASS. conftest.py mock fixture 재사용 + DeprecationWarning capture (`pytest.warns(DeprecationWarning)`) 도입. 회귀 위험 ↓.

### 안 된 것

1. **multi-llm-validation external placeholder만**: Phase 4.5와 같은 패턴 — external.md는 placeholder 작성, 실 외부 GPT/Gemini 검토는 사용자가 외부에서 진행 시 채움. Phase 5 (큰 phase) 진입 전 의무 권장. **수용 가능 — 사용자 결정 정합**.

2. **deprecated 필드 즉시 제거 불가**: Phase 9+ eval-run 정식화 후 제거 결정 (사용자 결정 NG12 `critic_fallback_keep_with_deprecation: yes`). 현재 deprecated 3 필드 (overall_score_avg / scores / eight_dim_scores) backward-compat 유지 — Phase 1~4.5 데이터 호환 필요. **수용 가능 — 단계적 제거 전략**.

3. **prompt_registry P-007/P-008 semver 정식화 미수행**: NG8 (Phase 7+ defer) 사용자 결정 — Phase 6 scope에서 제외. Rewriter PROMPT_VERSION = "v1.1.0" 코드 마커는 추가했으나 prompt_registry.md 본격 정식화 (golden_set 회귀 + A/B 단계) 는 Phase 7+ 이관.

4. **revise effect eval 미수행 (Phase 4.5 D6 effect 계속 deferred)**: revise가 실제 품질을 얼마나 개선했나 eval은 Phase 9+ eval-design 이관. Phase 6 scope (output schema 안정화)에서 제외.

### 배운 것

1. **contract-change Skill 본격 트리거는 ADR + smoke test로 안전성 강화**: Phase 6 Slice 2에서 3 contract 동시 변경 + ADR-018/019 작성 + pytest 109 → 122 + smoke 10/10 + audit 0 drift × 2. **ADR + smoke + audit 3중 게이트가 회귀 0건 보장**. Phase 5+ 큰 contract 변경 (DB schema 도입) 시 동일 패턴 권장.

2. **agent-io-check Skill 첫 정식 트리거 패턴 정립**: 컨트랙트 로드 (agent_io_contract §6 + output_schema §9) → 구현 매핑 (rewriter.py + critic.py) → 차이 식별 (match / extra / missing / type_diff) → 결과 기록. Phase 7+ RAG agent 추가, Phase 9+ Brand Memory Extractor 추가 시 동일 패턴 재사용. **§agent-io-check 결과 기록 형식 baseline 확립**.

3. **canonical + deprecated 단계적 축소 패턴 (P-CRITIC-CANONICAL-001 후보)**: 4가지 fallback 즉시 제거 X → canonical 1 + 우선 fallback 1 + deprecated 3 (DeprecationWarning) → Phase 9+ eval-run 정식화 후 deprecated 제거. **단계적 제거 전략은 회귀 위험 ↓ + 사용자 데이터 호환 ↑**. Phase 5+ DB schema 변경, Phase 7+ RAG schema 변경 시 동일 패턴 재사용 가능.

4. **Pydantic 모델 + dict 반환 backward-compat 양립 패턴**: Rewriter v1.1.0에서 RewriterInput/RewriterOutput Pydantic 도입 + 실제 `run_rewriter` dict 반환 호환 유지 → `routers/plans.py` 0줄 변경 + 회귀 0. **typing 검증 + frontend type mirror + backward-compat 3종 동시 달성**. Phase 7+ 다른 agent (Brand Memory Extractor 등) 추가 시 동일 패턴 권장.

5. **schema_stress_test.ps1 (P-X2 v2) — 자동 게이트 evolution 패턴**: P-X2 첫 (Phase 4.5 scenario_simulation file count 휴리스틱) → P-X2 v2 (Phase 6 schema_stress pytest matrix + tsc + Pydantic import + frontend canonical key 검증). **자동 게이트 evolution 패턴 — 첫 baseline → 표현력 보강 → 도입 비용 ▼ + 정밀도 ↑**. Phase 7+ rag_stress_test, Phase 9+ eval_stress_test 같은 evolution 가능.

6. **P-CONTRACT-FIRST-001 후보 — DB 진입 전 contract 안정화 효과**: Phase 5 (DB/Auth, 15~20h) 진입 직전 Phase 6 (mini-phase 8h)로 contract 안정화 → DB schema 진입 시 Critic verdict canonical / Rewriter contract / revise_history schema 모두 안정. **큰 phase 진입 전 mini-phase로 contract 안정화 패턴 정식 등록 권장**. Phase 7 (RAG), Phase 9+ (eval-run) 진입 전에도 동일 패턴 재사용 가능.

### 근본 원인 (해당 없음 — 본 phase deviation 0건)

Phase 4.5처럼 deviations 0건. closing_notes.md deviations 섹션 비어있음. P-X1 17연속 PASS로 forbidden 영역 침범 0건 — root cause 분석 불요.

### 부가 발견 사항 (개선 후보)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| frontend deprecated 필드 non-optional 유지 결정 | 작음 (page.tsx `toFixed` 회귀 방지) | 1회 (Slice 3 sub-agent 판단) | Phase 9+ eval-run 후 Optional 강등 가능 |
| Critic canonical 4 → 1+3 단계적 축소 | 보통 (3 deprecated 잔존) | 1회 (Phase 6 신규) | Phase 9+ eval-run 정식화 후 deprecated 3 완전 제거 |
| Rewriter prompt body 인라인 (NG7) | 작음 (NG8 Phase 7+ defer 결정) | 1회 (Phase 6 ADR-019 명시) | Phase 7+ prompt_registry P-008 본문 분리 |
| revise effect eval 미수행 | 보통 (D6 effect 계속 deferred) | 1회 (Phase 6 scope 제외) | Phase 9+ eval-design |

---

## 개선 제안 (본 회고 본문 §개선 제안 — mini-phase 권장 사항 적어 별도 proposals 파일 생략)

### 개선 제안 1 (우선순위: ↑): P-CONTRACT-FIRST-001 정식 패턴 등록

- **무엇을**: meta/patterns.md에 P-CONTRACT-FIRST-001 정식 등록 (현 회고에서 후보 → Phase 5 entry 시점 사용자 검토 후 정식 채택 결정 권장)
- **왜**: Phase 6에서 큰 phase (Phase 5 DB/Auth 15~20h) 진입 전 mini-phase 8h로 contract 안정화 → DB schema drift 위험 ~0. Phase 7+ RAG / Phase 9+ eval 도입 전에도 동일 패턴 재사용 가능.
- **어디에**: `meta/patterns.md` § P-CONTRACT-FIRST-001 entry
- **상태**: Phase 5 entry 시점 사용자 검토 (본 Slice 4에서 신규 등록 진행했으나 정식 패턴 vs 후보 분리는 사용자 결정)

### 개선 제안 2 (우선순위: ↑): P-CRITIC-CANONICAL-001 정식 패턴 등록

- **무엇을**: 다중 fallback (4가지) → canonical 1 + 우선 fallback 1 + deprecated 3 + DeprecationWarning + Phase 9+ 제거 단계적 축소 패턴 정식 등록.
- **왜**: Critic verdict 외에도 Phase 7+ RAG schema, Phase 9+ eval schema 같은 다중 fallback 누적 시 동일 패턴 재사용 가능. **DeprecationWarning + pytest.warns capture 의무화** → 회귀 검출 baseline.
- **어디에**: `meta/patterns.md` § P-CRITIC-CANONICAL-001 entry + Phase 9+ eval-run 정식화 후 fallback 완전 제거 시점에 "Resolved" 표기 추가.
- **상태**: 본 Slice 4에서 신규 등록 진행

### 개선 제안 3 (우선순위: 보통): scenario_simulation.ps1 v2 (DB/Auth 시나리오 5 추가)

- **무엇을**: Phase 5 Slice 1에서 scenario_simulation.ps1에 DB/Auth용 5 시나리오 추가 (S6: Supabase 연결 / S7: RLS 정책 / S8: user 분리 / S9: JWT / S10: SSE)
- **왜**: P-X2 자동 게이트 두 번째 트리거 (Phase 6)까지 5 시나리오 baseline. Phase 5 DB/Auth 진입 시 시나리오 표현력 보강 필요 (회고 §4 Phase 4.5에서도 권장).
- **어디에**: `scripts/scenario_simulation.ps1` § S6~S10 추가 (Phase 5 Slice 1 작업)
- **상태**: Phase 5 entry 시점 사용자 결정

### 개선 제안 4 (우선순위: 보통): prompt_registry P-007/P-008 정식화 (Phase 7+)

- **무엇을**: 현재 P-007 (Critic) + P-008 (Rewriter) prompt body 모두 인라인 (NG7 + NG8 deferred). Phase 7+ RAG 본격화 시 prompt_registry.md에 정식 등록 (semver + golden_set 회귀 + A/B 단계적 활성화).
- **왜**: Phase 6 ADR-019에서 PROMPT_VERSION = "v1.1.0" 코드 마커는 추가했으나 prompt_registry.md 본문 정식화는 Phase 7+ 이관 (NG8 사용자 결정). Phase 7+ entry 시점 도입 권장.
- **어디에**: `ai_system/prompts/prompt_registry.md` P-007 + P-008 entry
- **상태**: Phase 7+ entry 시점 prompt-version-review Skill 첫 트리거

### 개선 제안 5 (우선순위: 낮음): revise effect eval (Phase 9+)

- **무엇을**: Phase 4.5 D6 effect (revise가 실제 품질 개선 효과 측정) Phase 9+ eval-design 이관. Phase 6 scope 제외.
- **왜**: Critic revise loop 도입 (Phase 4.5) → revise 1회/2회 시 품질 개선 정량 측정 baseline 필요. Phase 9+ eval-run 정식화 후 측정.
- **어디에**: `eval/video_planning_eval.md` § revise effect metric
- **상태**: Phase 9+ entry 시점 eval-design Skill 트리거

---

## 패턴 등록 (meta/patterns.md 후보)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **17연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4) | phase-3 + phase-4 + phase-4.5 + phase-6 | 갱신 (Phase 6) — mini-phase 두 번째 효과 입증 + PlanCard 12연속 + component_map 22연속 |
| **P-CRITIC-CANONICAL-001** (신규) | 다중 fallback (4가지) → canonical 1 + 우선 fallback 1 + deprecated 3 + DeprecationWarning 단계적 축소 패턴 | phase-6 | 신규 등록 (Phase 6) — Phase 9+ eval-run 정식화 후 fallback 완전 제거 시점에 "Resolved" 표기 |
| **P-CONTRACT-FIRST-001** (신규 후보) | DB 영속화 (Phase 5) 또는 큰 phase 진입 전 mini-phase로 contract 안정화 효과 입증 | phase-6 | 신규 등록 후보 (Phase 5 entry 시점 사용자 검토 후 정식 채택 결정) |
| **P-VALIDATION-FORMAL-001** (update) | multi-llm-validation formal self + 외부 분리 패턴 두 번째 입증 (Phase 4.5 V1~V4 → Phase 6 V1~V5) | phase-4.5 + phase-6 | 정식 패턴 확정 (Phase 6 두 번째 트리거로 입증) |

→ Phase 1~4.5 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 (Phase 4.5 revise loop + Phase 6 Rewriter graceful 자연 확장 입증) / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, **17연속 입증**) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 (update **17연속**) / P-THIN-VERTICAL-001 / P-GPT-REVIEW-001 (Phase 6 두 번째 적용 ▼20% 시간) / P-X2-EFFECT-001 (Phase 6 두 번째 자동 게이트) / P-VALIDATION-FORMAL-001 (Phase 6 두 번째 입증) — 모두 효과 유지

---

## Skill 사용 로그 (Phase 6 동안)

| Skill | Phase 6 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 6 entry, 4점검 PASS |
| qa-check (v1.2.0) | 1 | Slice 1 entry (11 카테고리 정합) |
| contract-change | **1 본격** ★ | Slice 2 output_schema + agent_io_contract + api_contract 3 contract 동시 변경 + ADR-018/019 + 회귀 0 — **첫 본격 실 변경 통과** |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.2.0) | 1 | Phase 6 종료 (v1.2.0 §1.6 **두 번째** 자동 게이트, scenario_simulation 5/5 PASS) |
| design-review | 1 | Slice 4 impl §B (다섯 번째 사용 — PlanCard 12연속 무수정 정합) |
| harness-audit | 1 | Slice 4 audit_naming + audit_page_component 자동 호출 |
| multi-llm-validation | **1 formal self V1~V5** (두 번째) + **1 external placeholder** | **두 번째 formal 트리거** — P-VALIDATION-FORMAL-001 두 번째 입증 |
| **agent-io-check** | **1 ★ 첫 정식** | Slice 4 첫 정식 트리거 — Rewriter v1.1.0 + Critic canonical 정합 PASS |
| 기타 unused | — | eval-design / rag-design / security-review 등 (Phase 5/7/9+ 활성화 예상) |

**Phase 6 사용 요약**: 9 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change ★ 본격 + multi-llm-validation formal 두 번째 + agent-io-check ★ 첫 정식 + harness-audit + design-review + meta-retrospective + phase-complete v1.2.0 두 번째). Phase 1~6 누적 = 10 Skill active, 10 unused. **agent-io-check + contract-change 본격 트리거** (Phase 5 진입 전 baseline 완성).

**Phase 5 진입 시 활성 예상 Skill**: phase-start v1.3.0 + qa-check + contract-change (DB schema 도입) + multi-llm-validation **formal external 의무** + agent-io-check + **security-review ★ 첫 트리거** + harness-audit + design-review.

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md P-X1-EFFECT-001 update (17연속) + P-CRITIC-CANONICAL-001 신규 + P-CONTRACT-FIRST-001 신규 후보 + P-VALIDATION-FORMAL-001 두 번째 update
- [x] meta/skill_usage_log.md 갱신 (Phase 6 누적 + agent-io-check 첫 + contract-change 본격)
- [x] phases/active/phase-6-output-schema-stabilization/closing_notes.md 작성 (Phase 5 진입 조건 체크리스트)
- [x] phases/active → phases/archive 이동 (git mv)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README × 2 갱신
- [ ] 다음 Phase 5 (DB/Auth) 진입 — external validation + security-review + scenario_simulation v2 작성 후
```

---

## 다음 phase 진입 권장 사항

### Phase 5 DB/Auth (사용자 명시 결정: Phase 6 → Phase 5 순차 진행)

```
산출물:
  - Supabase Auth + JWT
  - PostgreSQL + RLS 정책 (4계층 데이터 모델 첫 영속화)
  - plan_store DB migration (in-memory → Supabase row)
  - SSE Progress streaming (D7)
  - 사용자 세션 인증 + plan_id 권한 검증
추정 시간: 15~20h
Acceptance:
  - 다중 사용자 + plan_id 권한 분리
  - SSE Progress 30~60초 대기 UX 활성화
  - Critic revise loop + Rewriter v1.1.0 + recommended_plan_index 모두 baseline 유지
의존성:
  - Phase 6 contract 안정화 (Critic canonical + Rewriter v1.1.0 + revise_history Optional 정식)
  - Supabase 프로비저닝
  - external validation 의무
다음 → Phase 7 (RAG Lite)

진입 전 권장 (체크리스트):
  - [ ] external validation 작성 (`meta/validations/2026-05-29_phase-6-pre-entry_external.md` placeholder를 GPT/Gemini로 채움)
  - [ ] security-review Skill 첫 호출 (Phase 5 entry)
  - [ ] scenario_simulation.ps1 v2 (DB/Auth용 5 시나리오 추가 — Phase 5 Slice 1에서)
  - [ ] multi-llm-validation formal **external 의무** (큰 보안 phase)
  - [ ] contract-change Skill 호출 (db_schema.md 신규 + 0001_init.sql migration)
  - [ ] ADR-020 Supabase 채택 결정 작성

권장 Slice 분할 (Phase 6 작업 시점 plan, 사용자 검토 후 확정):
  1. Pre-Entry + Security (2~3h)
  2. Supabase 연결 + Schema migration (4~5h)
  3. Auth + JWT + Frontend Login (4~5h)
  4. RLS 정책 + SSE Progress D7 (3~4h)
  5. Close + 회귀 검증 (2~3h)

총 15~20h 추정.
```

---

## 변경 이력

- 2026-05-29: Phase 6 회고 최초 작성 (phase-complete v1.2.0 §1.6 두 번째 자동 게이트 + §7 회고 자동 호출). **P-X1-EFFECT-001 update (17연속) + P-CRITIC-CANONICAL-001 신규 + P-CONTRACT-FIRST-001 신규 후보 + P-VALIDATION-FORMAL-001 두 번째 update 패턴 등록**. P-AGENT-SCOPE-001 mitigation 17/17 입증. **agent-io-check Skill 첫 정식 트리거 PASS + contract-change Skill 첫 본격 실 변경 통과**. 다음 phase = Phase 5 DB/Auth (사용자 명시 결정 "Phase 6 → Phase 5 순차" 계승).
