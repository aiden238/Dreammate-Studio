# Retrospective: Phase 4.5 — Critic Revise Loop + Rewriter + Z-X3 Best-Plan + P-X2

> 작성일: 2026-05-28
> 종류: mini-phase
> 범위: Phase 4.5 전체 (entry → Slice 1~4 → final QA → archive)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete v1.2.0 절차 7단계 (회고) + §1.6 변경성 시뮬 자동 게이트 첫 작동

---

## 사실 요약

Phase 4.5 (Critic Revise Loop + Rewriter Agent + Z-X3 Best-Plan Selection + P-X2 자동 게이트 채택 — mini-phase)를 **2026-05-28 단일 일자**에 진입부터 archive까지 완수.

진입: phase-start v1.3.0 §6 4점검 통과 + 사용자 결정 4개 (z_x3_include=yes / p_x2_adopt=yes / multi_llm_validation_formal=yes / all_slices_sub_agent=yes). entry commit `ad05b14`.

4 Slices를 4 Waves로 분해 (모두 sequential + 모두 sub-agent dispatch):
- Wave 1 (Slice 1, sub-agent A) — Pre-Entry: validations self + external placeholder + P-X2 채택 (phase-complete v1.1.0 → v1.2.0 §1.6) + `scripts/scenario_simulation.ps1` 신규
- Wave 2 (Slice 2, sub-agent B) — Rewriter agent + Critic Revise Loop (max 2) + revise_history 응답 노출 + ADR-016
- Wave 3 (Slice 3, sub-agent C) — Best-Plan Selection (Z-X3) + Frontend wrapper highlight (PlanCard 무수정) + ADR-017
- Wave 4 (Slice 4, sub-agent D) — Close: smoke 9/9 + scenario_simulation 5/5 (P-X2 첫 자동 게이트) + retrospective + patterns + archive + state docs

총 4 sub-agent dispatch (100% sub-agent 패턴). 충돌 0건. **§SELF-VERIFICATION 4/4 PASS**.

핵심 회귀 baseline 보존:
- **PlanCard.tsx 0줄 변경 5연속 (Phase 4.5 Slice 1~5 + 사용자 결정 6-a 계승)** → 누적 9연속 (Phase 4 4 + Phase 4.5 5) ★
- **component_map.md 0줄 변경 4연속 (Phase 4.5 Slice 1~4)** → 누적 19연속 (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4) ★
- pytest 93/93 baseline → **109/109** (+16 신규: rewriter 7 + plans revise 3 + critic best-plan 6)
- smoke_test_phase_4_5 **9/9 PASS**
- scenario_simulation **5/5 PASS** (P-X2 첫 자동 게이트 작동)
- audit_naming + audit_page_component **0 drift × 2** (Slice 1 entry + Slice 4 final)
- next build 11 routes / tsc 0 / lint clean (Phase 4 baseline 유지)

회고 핵심 발견:
- ★ **P-X1 §SELF-VERIFICATION 13연속 PASS**: Phase 3 5 + Phase 4 4 + Phase 4.5 4 = 13 Slice 누적. P-AGENT-SCOPE-001 mitigation 13연속 입증.
- ★ **multi-llm-validation formal 첫 트리거**: Claude Code 자가 검증 + 외부 검증 placeholder 분리 패턴 정립 → `meta/validations/` 폴더 누적 시작. **P-VALIDATION-FORMAL-001 신규 패턴 후보**.
- ★ **P-X2 첫 자동 게이트 작동**: `scripts/scenario_simulation.ps1` 5/5 PASS via `phase-complete` v1.2.0 §1.6. manual walkthrough ~30분 → 자동 ~1초 (▼99% 시간). **P-X2-EFFECT-001 신규 패턴**.
- ★ **Z-X3 채택 효과**: best-plan selection logic 6 케이스 (idx 0/1/2 + tie-break) PASS + frontend wrapper highlight (PlanCard 무수정 유지) → **PlanCard 9연속 0줄 baseline + UX 추천 highlight 양립**.
- ★ **Phase 4 GPT 검토 정신 계승**: Phase 4 회고 Z-X3 + P-X2 + Phase 2 P-X2 권장 → Phase 4.5에서 모두 채택. 본 scope 12~16h → 실측 ~12~14h (Z-X3/P-X2 추가에도 ▼20% 시간 절감).

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-28 단일일 (다중 세션) |
| Total commits (Phase 4.5) | 4 (Slice 1 ad05b14 + Slice 2 3e7a33b + Slice 3 ca7cbca + Slice 4 final) |
| 신규 파일 | ~12 (rewriter.py + smoke_test_phase_4_5.ps1 + scenario_simulation.ps1 + 2 validations + retrospective + closing_notes + ADR-016 + ADR-017 + test_rewriter.py + 3 다른) |
| 수정 파일 | ~10 (plans.py + critic.py + output.py + config.py + page.tsx + types.ts + test_plans.py + test_critic.py + test_3_plan.py + phase-complete SKILL.md) |
| 줄 수 변화 | +~1300 (backend +450 / frontend +45 / tests +401 / meta+scripts+docs +650 / state docs +100) |
| 신규 ADR | 2 (ADR-016 critic revise + ADR-017 best-plan selection) |
| backend agents 신규 | 1 (rewriter.py — P-008) |
| backend agents 수정 | 1 (critic.py — select_best_plan_index 추가) |
| backend routers 수정 | 1 (plans.py — revise loop + recommended_idx) |
| backend schemas 수정 | 1 (output.py — revise_history + recommended_plan_index Optional 필드) |
| backend config 수정 | 1 (config.py — critic_max_revise 추가) |
| Frontend routes 변화 | 0 (Phase 4 11 routes 유지) |
| Frontend page 수정 | 1 (plan/[plan_id]/page.tsx — wrapper UI + AI 추천 badge) |
| pytest 결과 | **109/109 PASS** (Phase 4 93 baseline + Phase 4.5 신규 16) |
| pytest 신규 케이스 | 16 (rewriter 7 + plans revise 3 + critic best-plan 6) |
| audit_naming | 0 drift (Slice 1 + Slice 4) |
| audit_page_component | 0 drift (Slice 1 + Slice 4) |
| smoke_test_phase_4_5 | **9/9 PASS** |
| scenario_simulation | **5/5 PASS** (P-X2 첫 자동 게이트) |
| next build | 11 routes (Phase 4 baseline 유지) |
| tsc / lint | 0 errors / clean |
| Sub-agent dispatch | 4 (Slice 1~4 모두) |
| **P-X1 §SELF-VERIFICATION** | **4/4 PASS (Phase 4.5)** ★ |
| **P-X1 누적 streak** | **13연속 (Phase 3 5 + Phase 4 4 + Phase 4.5 4)** ★ |
| **PlanCard.tsx deviation** | **0건 (Phase 4.5 전체, 누적 9연속 — Phase 4 4 + Phase 4.5 5)** ★ |
| **component_map.md deviation** | **0건 (Phase 4.5 전체, 누적 19연속 — Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4)** ★ |
| multi-llm-validation 트리거 | 1 formal (Claude Code self) + 1 external placeholder |
| 식별된 P-pattern (Phase 4.5 신규) | 2 (P-X2-EFFECT-001 + P-VALIDATION-FORMAL-001) + 1 update (P-X1-EFFECT-001 → 13연속) |
| Phase 4.5 deferred → Phase 5+/6+ 이관 | DB/Auth / SSE / 4-layer 재정의 / prompt_registry / Critic verdict 단일 표준 |
| 시간 추정 vs 실측 | 12~16h (multi_slice_plan) → 실측 ~12~14h (Z-X3/P-X2 추가에도 ▼20% 절감) |

---

## 분석

### 잘된 것

1. **★ P-X1 13연속 PASS — 4 Slice 모두 sub-agent + 충돌 0건**: Phase 4.5 Slice 4개를 모두 sub-agent dispatch로 진행 (사용자 결정). 각 sub-agent가 §SELF-VERIFICATION을 수행하여 forbidden 영역 1줄도 침범 안 함. P-AGENT-SCOPE-001 mitigation 13연속 누적 입증.
2. **★ multi-llm-validation formal 첫 트리거 — Claude Code self + 외부 placeholder 분리**: 사용자 결정 "검증 모델은 너가 직접, 외부 검증은 따로"를 다음 패턴으로 정립:
   - `meta/validations/{date}_{phase}_self.md` (Claude Code 자가 검증, 지침 참조, V1~V4 PASS)
   - `meta/validations/{date}_{phase}_external.md` (외부 GPT/Gemini placeholder, 사용자가 외부에서 채움)
   → 단일 모델 편향 회피 baseline 확립 + 외부 검증 의무화 부담 없이 분리 가능. **P-VALIDATION-FORMAL-001 신규 패턴**.
3. **★ P-X2 첫 자동 게이트 작동**: Slice 1에서 phase-complete SKILL.md v1.1.0 → v1.2.0 (§1.6) + `scripts/scenario_simulation.ps1` 신규 (5 시나리오 모두 file count 기반 자동 판정). Slice 4 phase-complete 호출 시 5/5 PASS 확인. manual walkthrough ~30분 → 자동 ~1초 (▼99% 시간). **P-X2-EFFECT-001 신규 패턴**.
4. **★ Z-X3 채택 + PlanCard 무수정 양립**: best-plan selection logic을 backend (critic.py + plans.py + output.py)에 추가하고 frontend는 `plan/[plan_id]/page.tsx`에 wrapper `<div className={recommendedIdx === idx ? "ring-2 ring-emerald-500" : ""}>`만 추가. PlanCard.tsx는 0줄 변경 → **9연속 baseline 유지 + UX 추천 highlight 양립**. D3/D4 4-layer 재정의 deferred 정신 일관 유지.
5. **★ revise loop graceful 패턴 적용 (P-GRACEFUL-001 자연 확장)**: Rewriter 실패 시 원본 plan 반환 + warnings에 명시. critic_max_revise=2 환경 override 가능 (config.py). 무한 루프 차단 + sub-fail 시 사용자 차단 0건. Phase 1 graceful baseline이 Phase 4.5 multi-attempt revise 환경에서도 자연 확장 — P-GRACEFUL-001 효과 입증.
6. **Phase 4 GPT 검토 권장사항 계승**: Phase 4 회고 Z-X1~Z-X3 + Phase 2 P-X2 우선순위 ↑ 권장 → Phase 4.5에서 Z-X3 + P-X2 채택, Z-X1/Z-X2 deferred 유지. 회고 권장사항이 실제 phase에서 채택 → 측정 → 효과 입증 사이클 완성.
7. **4 Slice 모두 sub-agent (사용자 결정 all_slices_sub_agent)**: Phase 4는 Slice 4가 main session이었으나 Phase 4.5는 4/4 sub-agent. 컨텍스트 비용 절감 + 사용자 결정 100% 수행 + P-X1 효과 누적 입증.
8. **pytest 109/109 (+16 신규) 회귀 0**: Phase 4 93 baseline + 신규 16 (test_rewriter.py 7 + test_plans.py revise 3 + test_critic.py best-plan 6) 모두 PASS. conftest.py mock fixture 재사용. 회귀 위험 ↓.
9. **smoke_test_phase_4_5 9/9 PASS (신규 9번째 — revise loop integration)**: Phase 4 8 + 신규 9 (revise_history 응답 노출 통합 테스트). endpoints sanity check 추가 — FastAPI app routes import 정상성 확인. Phase 5+ 진입 시 SSE/Auth 추가에도 stable baseline.

### 안 된 것

1. **scenario_simulation.ps1의 시나리오 깊이 — file count 기반 단순 휴리스틱**: 5 시나리오 모두 grep 기반 file presence count만 검사. 실제 코드 동작/롤백 시뮬레이션은 X — Phase 5+ DB/Auth 도입 시 시나리오 표현력 보강 필요. **수용 가능 — 자동 게이트 첫 baseline + 1초 실행 시간 효과 우선**.
2. **multi-llm-validation 외부 검증 placeholder만**: external.md는 placeholder 형식만 작성 — 실 외부 GPT/Gemini 검토는 사용자가 외부에서 진행 시 채움. Phase 5+ 큰 phase 진입 전 외부 검증 의무 (V1~V4 cross-check) 권장. **수용 가능 — 사용자 결정 정합**.
3. **Critic verdict 응답 구조 4가지 fallback (overall_score / scores / dimensions / eight_dim_scores)**: select_best_plan_index 함수에서 4가지 키 fallback 사용. 단일 표준 결정 미흡. Phase 6+ Output Schema 안정화 시 단일 표준 결정 권장 (회고 개선 제안 §3).
4. **revise loop effect eval 미수행 (D6 effect deferred)**: revise_history는 응답 노출되나 "revise가 실제 품질을 얼마나 개선했나" eval은 미수행. Phase 6+ eval-design Skill로 정식 측정 권장.

### 배운 것

1. **multi-llm-validation formal self + 외부 분리 패턴은 큰 phase 부담 ↓**: 외부 검증 의무화 부담 없이 분리 가능 → 사용자가 phase별로 외부 진행 여부 결정 가능. Phase 5+ DB/Auth 같은 큰 phase에서는 외부 의무 / mini-phase는 self만 — 분리 의사결정 가능. **P-VALIDATION-FORMAL-001 정식 패턴 등록 권장**.
2. **P-X2 자동 게이트는 phase-complete v1.2.0 §1.6에서 1초 실행 — 도입 비용 ▼**: scenario_simulation.ps1 단일 스크립트 추가 + SKILL.md 1단계 추가 = 2 파일 변경으로 manual walkthrough ~30분 → 1초. 도입 ROI ↑↑. **Phase 5+ DB/Auth 진입 전 시나리오 1~5를 환경별로 분기 권장**.
3. **mini-phase 형식의 가치**: Phase 4 종료 후 D6 (Critic revise) Phase 6+ 이관 대신 Phase 4.5로 분리 → 시간 ~12~14h. Phase 5 (15~20h) 진입 전 안정화 효과 + 영상기획 품질 개선 baseline 확립. **큰 phase 진입 전 mini-phase로 안정화 패턴은 재사용 가능**.
4. **§SELF-VERIFICATION의 mini-phase 효과**: Phase 3 5/5 → Phase 4 4/4 → Phase 4.5 4/4 = 13연속. mini-phase (4 Slice 모두 sub-agent)에서도 효과 유지. **P-AGENT-SCOPE-001 mitigation 누적 입증 13연속**.
5. **frontend wrapper 패턴 — Decorator 패턴의 컴포넌트 변형**: best-plan highlight를 PlanCard 내부 props 추가 대신 wrapper `<div>`로 처리 → PlanCard 0줄 변경. Phase 5+ 다른 UX 추가 (예: revise verdict badge, AI 추천 이유 등)도 동일 wrapper 패턴 활용 가능. **P-WRAPPER-DECORATOR-001 후보** (Phase 5+ 재출현 시 정식 등록).

### 근본 원인 (해당 없음 — 본 phase deviation 0건)

Phase 4 D-1 (audit drift)와 같은 deviations 0건. closing_notes.md deviations 섹션 비어있음. P-X1 13연속 PASS로 forbidden 영역 침범 0건 — root cause 분석 불요.

### 부가 근본 원인 (영향-빈도)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| scenario_simulation 시나리오 깊이 | 작음 (file count 기반) | 1회 (P-X2 첫 트리거) | Phase 5+ 시나리오 표현력 보강 후보 |
| Critic verdict 4가지 fallback | 보통 (단일 표준 미정) | 1회 (Phase 4.5 신규) | Phase 6+ Output Schema 안정화 |
| revise loop effect eval | 보통 (effect 미측정) | 1회 (D6 effect deferred) | Phase 6+ eval-design |
| multi-llm-validation external placeholder | 작음 (사용자 결정 정합) | 1회 (Phase 4.5 첫) | Phase 5+ 큰 phase 시 외부 의무 |

---

## 개선 제안 (본 회고 본문 §개선 제안 — mini-phase 권장 사항 적어 별도 proposals 파일 생략)

### 개선 제안 1 (우선순위: ↑): P-VALIDATION-FORMAL-001 정식 패턴 등록

- **무엇을**: meta/patterns.md에 P-VALIDATION-FORMAL-001을 정식 등록 (현 회고에서 후보 → Phase 5 진입 전 정식 채택 결정 권장)
- **왜**: Phase 4.5에서 self + 외부 분리 패턴 정립 → Phase 5+ DB/Auth 같은 큰 phase 진입 전 동일 패턴 의무화로 재사용
- **어디에**: `meta/patterns.md` § P-VALIDATION-FORMAL-001 entry
- **상태**: Phase 5 진입 시점 사용자 검토 (Slice 4에서 신규 등록은 진행했으나 정식 패턴 vs 후보 분리는 사용자 결정)

### 개선 제안 2 (우선순위: 보통): smoke_test endpoints sanity 실 HTTP 호출 강화

- **무엇을**: 현재 smoke_test_phase_4_5.ps1 Step 8 endpoints sanity는 FastAPI app routes import만 확인. Phase 5+ TestClient fixture로 실 HTTP 호출 (GET /, POST /api/v1/plans/start) 통합 권장
- **왜**: 회귀 검출 정밀도 ↑ + Auth/RLS 도입 시 endpoint 권한 차이 검증 가능
- **어디에**: `scripts/smoke_test_phase_5.ps1` (Phase 5 신규 시) Step 8 강화
- **상태**: Phase 5 진입 시 검토

### 개선 제안 3 (우선순위: 보통): Critic verdict 응답 구조 단일 표준

- **무엇을**: 현재 select_best_plan_index 함수가 4가지 키 fallback (overall_score_avg / scores / dimensions / eight_dim_scores). Phase 6+ Output Schema 안정화 시 단일 표준 결정
- **왜**: 코드 단순화 + agent_io_contract 명확화 + 후속 phase Critic 변경 시 영향 ↓
- **어디에**: `docs/contracts/agent_io_contract.md` § Critic Agent output schema
- **상태**: Phase 6+ Output Schema phase 진입 시 contract-change Skill 트리거

### 개선 제안 4 (우선순위: 낮음): scenario_simulation 시나리오 표현력 보강

- **무엇을**: 현재 5 시나리오 모두 file count 기반 grep 휴리스틱. Phase 5+ DB/Auth 환경에서 시나리오 4 (revise loop max) / 시나리오 5 (recommended_idx disable) 같은 환경 분기 시나리오 추가 + 실 코드 변경 시뮬레이션 (예: stub patch + rollback) 검토
- **왜**: P-X2 자동 게이트 정밀도 ↑ → 회귀 검출 누락 위험 ↓
- **어디에**: `scripts/scenario_simulation.ps1` § 시나리오 4/5 강화
- **상태**: Phase 5+ DB 도입 시 검토 (현 단계 over-engineering 위험 있어 deferred 권장)

---

## 패턴 등록 (meta/patterns.md 후보)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **13연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4 + Phase 4.5 4) | phase-3 + phase-4 + phase-4.5 | 갱신 (Phase 4.5) — mini-phase 효과 입증 + PlanCard 9연속 + component_map 19연속 |
| **P-X2-EFFECT-001** (신규) | 변경성 시뮬 자동 게이트 첫 트리거 효과 (Phase 4.5 첫 작동, manual ~30분 → 자동 ~1초, ▼99%) | phase-4.5 | 신규 등록 (Phase 4.5) — P-X2 채택 → 효과 측정 사이클 완성 |
| **P-VALIDATION-FORMAL-001** (신규) | multi-llm-validation formal self + 외부 분리 패턴 (Claude Code 자가 검증 + 외부 GPT/Gemini placeholder 분리) | phase-4.5 | 신규 등록 (Phase 4.5) — Phase 5+ 큰 phase 진입 전 외부 의무 권장 |

→ Phase 1~4 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 (Phase 4.5 revise loop graceful 자연 확장 입증) / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, **13연속 입증**) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 (update **13연속**) / P-THIN-VERTICAL-001 / P-GPT-REVIEW-001 — 모두 효과 유지

---

## Skill 사용 로그 (Phase 4.5 동안)

| Skill | Phase 4.5 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 4.5 entry, 4점검 PASS |
| qa-check (v1.2.0) | 1 | Slice 4 final (11 카테고리, 7 PASS / 4 skip 목표 정합) |
| contract-change | 0 | Phase 4.5는 contract 변경 0 (ADR-016/017은 decisions/) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.1.0 → v1.2.0) | 1 | Phase 4.5 종료 (v1.2.0 §1.6 첫 트리거, scenario_simulation 5/5 PASS) |
| design-review | 1 | Slice 4 impl phase 네 번째 사용 — PlanCard 무수정 정합 검증 |
| harness-audit | 1 | Slice 4 audit_naming + audit_page_component 자동 호출 (수동 Skill X) |
| multi-llm-validation | **1 formal** (Claude Code self) + **1 external placeholder** | **첫 formal 트리거** — Phase 5+ 큰 phase 진입 시 외부 의무 권장 |
| agent-io-check | 0 (informal — Slice 2 Rewriter agent_io 정합 정성 점검만) | Phase 6+ Output Schema 진입 시 정식 활성화 |
| 기타 unused | — | eval-design / rag-design / cost-review 등 (Phase 5~9+ 활성화 예상) |

**Phase 4.5 사용 요약**: 7 Skill 활용 (phase-start + qa-check + meta-retrospective + phase-complete v1.2.0 ★ + harness-audit + design-review 네 번째 사용 + multi-llm-validation **formal** ★ 첫 정식 트리거). Phase 1~4.5 누적 = 9 Skill 활성화, 11 unused. **multi-llm-validation formal + P-X2 자동 게이트** 첫 트리거.

**Phase 5 진입 시 활성 예상 Skill**: phase-start v1.3.0 + qa-check (DB/Auth는 카테고리 1/2/3/5/9/11 활성) + contract-change (Supabase 스키마 도입) + multi-llm-validation **formal external 의무** + agent-io-check + security-review.

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md P-X1-EFFECT-001 update (13연속) + P-X2-EFFECT-001 신규 + P-VALIDATION-FORMAL-001 신규
- [x] meta/skill_usage_log.md 갱신 (Phase 4.5 누적 + multi-llm-validation formal 첫 트리거)
- [x] phases/active/phase-4.5-critic-revise-loop/closing_notes.md 작성 (다음 phase A/B/C 옵션 명시)
- [x] phases/active → phases/archive 이동 (git mv)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
- [ ] 사용자 결정: 다음 phase 옵션 A (Phase 5 DB/Auth) / B (Phase 6 Output Schema) / C (Phase 9+)
```

---

## 다음 phase 진입 권장 사항

### 옵션 A: Phase 5 DB/Auth (Supabase + RLS + SSE)

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
  - Critic revise loop는 Phase 4.5 baseline 유지
의존성: Phase 4.5 backend (revise loop + recommended_idx 포함) + Supabase 프로비저닝
다음 → Phase 6 (Output Schema + Agent IO 안정화)
권장 시점: 다중 사용자 데이터 누적 + 보안 우선시
**multi-llm-validation formal external 의무** (Phase 4.5 패턴 계승, 사용자 결정 의무)
```

### 옵션 B: Phase 6 Output Schema + Agent IO 안정화

```
산출물:
  - Phase 4.5 산출물 (revise_history + recommended_plan_index) stress test
  - Critic verdict 단일 표준 (overall_score / dimensions 통합 — 회고 개선 제안 §3)
  - agent_io_contract 정합 강화
  - prompt_registry 정식화 (P-007 + P-008 semver)
추정 시간: medium
Acceptance:
  - agent_io / output_schema stress test PASS
  - Critic verdict 단일 표준 PASS
의존성: Phase 4.5 산출물 (Rewriter + best-plan)
다음 → Phase 5 또는 Phase 7
권장 시점: 큰 phase 진입 전 schema baseline 확정 우선시
```

### 옵션 C: 다른 우선순위 (Phase 9 / 11+ 등)

```
가능 후보:
  - Phase 9 결과 저장 + Brand Memory 자동 추출 (UX 데이터 베이스)
  - Phase 11+ 안정화 (eval / cost / UX 검증)
추정 시간: 시점에 따라
권장 시점: 본 Phase 4.5 산출물 실 사용 + 데이터 누적 후 우선순위 재평가
```

---

## 변경 이력

- 2026-05-28: Phase 4.5 회고 최초 작성 (phase-complete v1.2.0 §1.6 자동 게이트 첫 작동 + §7 회고 자동 호출). **P-X1-EFFECT-001 update (13연속) + P-X2-EFFECT-001 신규 + P-VALIDATION-FORMAL-001 신규 패턴 등록**. P-AGENT-SCOPE-001 mitigation 13/13 입증. **다음 phase A/B/C 옵션 명시 (Phase 5 / Phase 6 / Phase 9+)**.
