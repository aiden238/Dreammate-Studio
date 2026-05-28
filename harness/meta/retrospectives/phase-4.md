# Retrospective: Phase 4 — FastAPI 기본 백엔드 구현 (확장)

> 작성일: 2026-05-28
> 종류: phase
> 범위: Phase 4 (전체 — GPT 검토 채택 진입 → 4 Slices → final QA → archive)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete v1.1.0 절차 6단계 (회고)

---

## 사실 요약

Phase 4 (FastAPI 기본 백엔드 구현 확장 — 3-plan parallel + multi-model 인터페이스 + Critic verdict)를 **2026-05-28 단일 일자**에 진입부터 archive까지 완수.

진입: phase-start v1.3.0 §6 4점검 통과 (audit_naming 0 drift) + **GPT 검토 채택** (Phase 4 원안 6 Slices → 4 Slices, ▼33%) + 사용자 결정 7개 반영 (4-b multi-model / 5-a Phase 8+ 제거 / 6-a PlanCard 무수정 등). entry commit `76b4d2c`.

4 Slices를 4 Waves로 분해 (sequential, 사용자 결정 2-a):
- Wave 1 (Slice 1): Foundation — 4 contract endpoints (POST /plans/start + wizard/{step} + /generate + GET) + X-API-Deprecation header + ADR-014
- Wave 2 (Slice 2): **Thin Vertical** — 3-plan parallel asyncio.gather + multi-model 인터페이스 + Critic 8-dim verdict 노출 + ADR-015
- Wave 3 (Slice 3): Frontend minimal — `/plan/[plan_id]/page.tsx` + PlanCard × 3 세로 스택 + PlanCard.tsx 무수정 (조정 6-a)
- Wave 4 (Slice 4): final QA + audit_page_component D-1 해소 + smoke + meta-retrospective + archive

총 3 sub-agent dispatch (Slice 1~3, Slice 4 본 회고는 main session). 충돌 0건. **§SELF-VERIFICATION 4/4 PASS**. **component_map.md 4연속 0줄 보존 (Phase 2 6 + Phase 3 5 + Phase 4 4 = 15연속)**. **PlanCard.tsx 4연속 0줄 보존 (Phase 4 전체)**. 변경성 시뮬레이션 4/5 PASS + 1 WARN (Phase 3 결과 유지).

회고 핵심 발견:
- ★ **P-X1 9연속 PASS**: Phase 3 P-X1-EFFECT-001 패턴이 Phase 4 backend phase (apps/web/ + backend/fastapi/ + docs/decisions/ 다영역)에서도 효과 입증. **proposal P-X1 채택 → 2 phase 누적 효과**.
- ★ **GPT 검토 채택 효과 측정**: 6→4 Slices (▼33%), 추정 18~26h → 실측 6~8h (▼66%). multi-llm-validation 정식 호출은 안 했으나 패턴은 동일 — P-GPT-REVIEW-001 신규 등록.
- ★ **multi-model 인터페이스 효과**: config.py openai_models_for_3plan list 단순 도입으로 Phase 21+ Anthropic / Custom 추가 시나리오 ≤ 3 파일 영향 — 변경성 시뮬 §시나리오 8 PASS.
- ★ **D-1 첫 deviations.md 활용**: Slice 3에서 `/plan/[plan_id]` audit_page_component drift를 deviations.md에 intended drift로 기록 → Slice 4에서 audit script 보강으로 해소. **contract-change 우회 + 후속 phase 이관 가이드 baseline 확립**.
- ★ **PlanCard 무수정 (사용자 결정 6-a) 4연속**: D3 (PlanCard 4-layer 재정의) Phase 3 인수 → Phase 4에서 deferred (D3 → Phase 5+) 정신 일관 유지.

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-28 단일일 (다중 세션) |
| Total commits (Phase 4) | 5 (entry 76b4d2c + Slice 1~3 + Slice 4 본 commit) |
| 신규 파일 | ~15 (backend tests 3 + routers/schemas 2 + frontend 1 + ADR 2 + QA 5 + scripts 1 + closing_notes 1) |
| 수정 파일 | 8 (planning.py + output.py + config.py + main.py + generate.py + plan/page.tsx + lib/api.ts + lib/types.ts) |
| 줄 수 변화 | +~5300 (코드 +~1850 / 문서 +~3450) |
| 신규 ADR | 2 (ADR-014 endpoint migration + ADR-015 3-plan multi-model) |
| backend endpoints 신규 | 4 (POST /plans/start + wizard/{step} + /generate + GET /plans/{id}) |
| Frontend routes 신규 | 1 (`/plan/[plan_id]` dynamic, 11 routes total — Phase 3 10 + Phase 4 1) |
| pytest 신규 | 31 (test_plans.py 15 + test_3_plan.py 16) — Phase 1 62 baseline + Phase 4 = **93/93 PASS** |
| audit_naming 결과 | 0 drift (Slice 1~4 모두) |
| audit_page_component 결과 | 0 drift (Slice 3 D-1 발견 → Slice 4 해소) |
| smoke_test_phase_4 결과 | 8/8 PASS (신규 smoke 스크립트) |
| Sub-agent dispatch | 3 (Slice 1~3 — Slice 4 본 회고는 main session) |
| QA reports | 5 (entry + Slice 1~3 + final) |
| next build | 11 routes static + ƒ /plan/[plan_id] dynamic = 11 routes total |
| tsc / lint | 0 errors / clean |
| 변경성 시뮬레이션 | 4/5 PASS + 1 WARN (Phase 3 결과 유지, Phase 4 backend는 +0 영향) |
| 변경성 보조 시나리오 (6/7/8) | 3/3 PASS (Phase 1 endpoint 제거 ≤3 + 3→5 plan ≤2 + multi-provider ≤3) |
| design-review impl | 7 원칙 모두 정합 PASS (PlanCard 무수정 + 3-plan 세로 스택) |
| **P-X1 §SELF-VERIFICATION** | **4/4 PASS (9연속, Phase 3 5 + Phase 4 4)** ★ |
| **component_map.md deviation** | **0건 (15연속, Phase 2 6 + Phase 3 5 + Phase 4 4)** ★ |
| **PlanCard.tsx deviation** | **0건 (4연속, Phase 4 전체)** ★ |
| 식별된 P-pattern (Phase 4 신규) | 1 (P-GPT-REVIEW-001 후보) |
| Phase 4 deferred → Phase 4.5+/5+/8+ 이관 | D6 / D7 / D8 / D3 / D4 / D2 / Phase 1 endpoint 제거 |
| 시간 추정 vs 실측 | 18~26h (원안) → 7~11h (acceptance.md) → 실측 ~6~8h (▼66% 원안 대비) |

---

## 분석

### 잘된 것

1. **★ P-X1 9연속 PASS — backend phase에서도 효과 입증**: Phase 4는 backend (backend/fastapi/), frontend (apps/web/), docs (decisions/) 3영역 동시 작업 phase로 forbidden 영역 침범 위험이 Phase 3보다 높았으나, sub-agent 4개 모두 §SELF-VERIFICATION PASS. P-AGENT-SCOPE-001 mitigation 9연속 누적.
2. **★ GPT 검토 채택 효과**: 원안 6 Slices (revise + SSE + 4-layer 재정의 본격 포함) → 4 Slices로 ▼33%. revise/SSE/4-layer 모두 Phase 4.5/5+ 이관 명시. 시간 ▼66% (18~26h → 6~8h). scope 명확화 (ADR-014 + ADR-015 명문화) + 회귀 위험 ↓.
3. **★ multi-model 인터페이스 효과 (사용자 결정 4-b)**: config.py openai_models_for_3plan list[str] 단순 도입으로 Phase 21+ Anthropic / Custom 추가 시나리오 ≤ 3 파일 영향. 변경성 시뮬 §시나리오 8 PASS. 현 단계는 default `["gpt-4o-mini"] × 3` (cost 효율).
4. **★ PlanCard 무수정 4연속 (사용자 결정 6-a)**: D3 (PlanCard 4-layer 재정의) Phase 3 인수 + Phase 4에서 deferred 정신 일관 유지. Phase 4 frontend `/plan/[plan_id]`에서 PlanCard.tsx import만 (× 3 반복). PlanComparisonCard D4와 함께 Phase 5+에서 재정의 (조정 3번 정합).
5. **★ D-1 첫 deviations.md 활용 → Slice 4 해소**: Slice 3에서 `/plan/[plan_id]` audit_page_component drift를 deviations.md에 intended drift (scope.md ⊃ page_map.md) 기록. Slice 4 audit script 보강 (`audit_page_component.ps1` Phase 4 정규화 case 추가) → 0 drift. **contract-change 우회 + 후속 phase 이관 가이드 baseline 확립**.
6. **Thin Vertical 패턴 backend 적용**: Slice 2를 3-plan parallel + multi-model + Critic verdict end-to-end로 정의 → POST /plans/{id}/generate 한 endpoint 통째 작동 (Intent → RAG → 3-plan parallel → Critic → DB → Envelope 200). P-THIN-VERTICAL-001 효과 backend phase에서도 입증.
7. **graceful 패턴 일관 적용 (P-GRACEFUL-001)**: 3 parallel 중 1~2개 실패 시 retry 1회 + fallback dict + validation.warnings에 명시. Phase 1 baseline 패턴이 Phase 4 multi-call 환경에서도 자연 확장.
8. **Phase 1 endpoint 회귀 0 (X-API-Deprecation header만 추가)**: 사용자 결정 5-a (Phase 8+ 제거) 정합. routers/generate.py 응답 body 무변경 + header 1개 추가. test_e2e_slice1 19개 회귀 0.
9. **pytest 93/93 PASS — 31개 신규 회귀 0**: test_plans.py 15 + test_3_plan.py 16 신규 작성. conftest.py mock_planning_parallel_3_ok 신규 fixture. Phase 1 62 baseline 그대로 유지.

### 안 된 것

1. **D-1 (audit_page_component dynamic route 정규화 누락) Slice 3에서 발견**: Phase 3 audit_page_component.ps1 D5는 `/new/discovery/step/[n]`만 정규화 — Phase 4 `/plan/[plan_id]`는 미커버. Slice 3 작업 중 발견 → deviations.md 기록 → Slice 4에서 해소. **수용 가능 — deviations.md 첫 활용 사이클 완성**. Phase 5+ 새 dynamic route 추가 시 audit script `dynamic_route_normalize_list` 패턴 확장 권장 (Z-X1 후보).
2. **multi-llm-validation Skill 정식 호출 X — 단 패턴은 동일**: 사용자가 GPT 검토를 외부에서 받음. Skill 정식 호출 시 meta/validations/ 결과 저장 + cross-ref 가능했으나 인터랙티브 검토라 skill 흐름 외에서 진행. **결과 채택은 명확 (6→4 Slices)** but skill 누적 로그 0 — Phase 5+ 큰 phase 진입 전 정식 호출 권장.
3. **plan_store in-memory dict (Phase 5+ Supabase 이관 필수)**: Phase 4 scope (사용자 결정 5+6 정합)이라 의도된 단순화. 본 phase 종료 시점 ~5 user 가정으로 OK. Phase 5 DB/Auth 진입 시 plan_store 모듈 abstract 후 Supabase row migration 필요 (D7 SSE와 함께 처리 가능).
4. **Critic revise loop / Rewriter 미구현 (D6 Phase 4.5+ 이관)**: GPT 검토 채택으로 명시 이관. revise_round = 0 + overall_verdict 노출만 (사용자 데이터 누적 후 Phase 4.5+에서 정식 활성화). Phase 4 acceptance A3 PASS — verdict 노출 자체는 OK.

### 배운 것

1. **외부 LLM 검토 (GPT) 채택 효과는 multi-llm-validation Skill 정식 호출 없이도 측정 가능**: 사용자가 외부 검토 받고 결정 → Phase entry에서 채택 명시 (entry commit 76b4d2c message + scope.md GPT 검토 항목) → Slice 결과 측정 (6→4 ▼33% / 18~26h → 6~8h ▼66%). **P-GPT-REVIEW-001 신규 패턴 등록**. Phase 5+ 진입 전 multi-llm-validation Skill 정식 호출 권장 (meta/validations/ 누적).
2. **deviations.md는 contract-change Skill 우회 도구**: spec 파일 (page_map.md) 직접 수정 X + deviations.md에 intended drift 기록 + 후속 phase에서 audit 도구 / contract-change Skill로 해소. Phase 4 D-1 → Slice 4에서 audit script 보강으로 해소 사이클 완성. **Phase 5+ 새 dynamic route / 새 컴포넌트 추가 시 deviations.md 활용 권장**.
3. **§SELF-VERIFICATION의 backend phase 효과**: Phase 3 (frontend) 5/5 → Phase 4 (backend + frontend mixed) 4/4 = 9연속. backend phase는 같은 .py 파일 sub-section 동시 수정 위험 (planning.py + schemas/output.py)이 frontend (.tsx)보다 높으나, sub-agent self-verification + main session 사후 git diff 점검의 2단계 차단으로 0건 재발. **다영역 동시 작업에서도 효과 유지**.
4. **GPT 검토 채택 + Thin Vertical 결합 효과**: Phase 4 Slice 2 (Thin Vertical 3-plan + multi-model end-to-end)가 한 endpoint 통째 작동 → Slice 3 (frontend minimal)이 API contract만 받아 단순 fetch + 렌더링. Phase 3 Thin Vertical (Discovery Step 1 end-to-end → Step 2~7 패턴 복제)의 backend 적용 형태. **P-THIN-VERTICAL-001 backend 입증**.
5. **multi-model 인터페이스는 config 1줄로 충분**: 사용자 결정 4-b 'multi-model 가능 구조'를 config.py openai_models_for_3plan list[str] 단순 도입으로 만족. Phase 21+ Anthropic 추가 시 `anthropic_models_for_3plan` list[str] 같은 패턴 + agents/planning.py provider 분기 (3 파일 영향). **변경성 보장 + 현 단계 over-engineering 회피 동시 달성**.

### 근본 원인 (5 Whys — D-1 발견 분석)

**문제**: Phase 4 Slice 3에서 `/plan/[plan_id]` audit_page_component drift 발견 (D-1).

```
왜 1: Phase 4 신규 dynamic route `/plan/[plan_id]`가 audit_page_component.ps1 정규화 case에 미포함
왜 2: Phase 3 audit_page_component.ps1 (D5)는 Phase 3 dynamic route `/new/discovery/step/[n]`만 정규화 — Phase 4 dynamic route는 작성 시점 미존재
왜 3: Phase 4 진입 시점 (76b4d2c)에는 `/plan/[plan_id]` scope.md §3에 명시되었으나 audit script 미선보강
왜 4: Phase 3 closing_notes Y-X2 (audit_page_component 사용 가이드) 작성 시 dynamic route 추가 시 정규화 패턴 확장 가이드 미명시 — placeholder 수준
왜 5: 자동화된 정규화 패턴 (regex-based) vs whitelist 패턴 (현재 if hardcoded) 선택이 phase별 ad-hoc로 진행됨 — 표준화 미흡
```

**근본 결론**: audit_page_component.ps1 dynamic route 정규화 패턴을 hardcoded if → regex-based whitelist로 리팩토링 권장 (Z-X1 후보). 또는 phase entry 시점에 신규 dynamic route 확인 + audit script preflight 절차 추가 (phase-start v1.4.0 §6.4 후보).

### 부가 근본 원인 (영향-빈도)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| D-1 audit drift | 작음 (deviations.md 기록 + Slice 4 해소) | 1회 (Phase 4) | Z-X1 후보 (audit script 정규화 패턴 표준화) |
| multi-llm-validation skill 미호출 | 작음 (결정 채택 명확) | 1회 (Phase 4 GPT 검토) | Phase 5+ 진입 전 정식 호출 권장 |
| plan_store in-memory dict | 보통 (Phase 5+ migration 필요) | 1회 (Phase 4 scope 의도) | Phase 5 D7 SSE와 함께 처리 |
| Critic revise loop 미구현 | 보통 (verdict 노출만) | 0회 (의도된 D6 이관) | Phase 4.5+ |

---

## 개선 제안

### Z-X1 (선택, 우선순위: 보통): audit_page_component.ps1 dynamic route 정규화 표준화

- **무엇을**: hardcoded if (`/new/discovery/step/[n]` + `/plan/[plan_id]`) → regex-based whitelist (`/\[.*\]/`) 또는 별도 config 파일
- **왜**: Phase 5+ 새 dynamic route 추가 시 audit script 보강 부담 ↓ + drift 자동 검출 정밀도 ↑
- **어디에**: `scripts/audit_page_component.ps1` § dynamic route 정규화 section
- **상태**: Phase 5+ 진입 직전 사용자 검토

### Z-X2 (선택, 우선순위: 낮음): multi-provider client factory baseline

- **무엇을**: agents/planning.py에 `_get_llm_client(provider, model)` factory 함수 + 현재 OpenAI 고정 → 향후 Anthropic 추가 시 단순 분기 baseline
- **왜**: 변경성 시뮬 §시나리오 8 (multi-provider 추가)이 현재 3 파일 영향이나, factory 도입 시 2 파일로 압축 가능 / Phase 21+ 진입 전 baseline 확립
- **어디에**: `backend/fastapi/agents/planning.py` + `backend/fastapi/config.py`
- **상태**: Phase 21+ 진입 전 검토 — 현 단계 over-engineering 가능성 있어 deferred 권장

### Z-X3 (선택, 우선순위: 낮음): Critic best-plan 선택 로직

- **무엇을**: 3-plan 중 Critic 8-dim verdict가 가장 좋은 plan을 evaluate → `body.recommended_plan_index` 노출
- **왜**: 사용자 결정 부담 ↓ (3개 중 추천 1개 highlight) + Critic 효과 측정 가능
- **어디에**: `backend/fastapi/agents/critic.py` + `schemas/output.py` Body 확장
- **상태**: Phase 4.5+ Critic revise loop 도입 시 함께 결정 (사용자 데이터 누적 후)

### Phase 3 Y-X 후속 재평가

- **Y-X1 (design_handoff §6.1 매핑표 spec/code 칸 분리)**: Phase 4 backend에서는 신규 영향 0 → Phase 11+ design phase 재진입 시 적용 권장
- **Y-X2 (audit_page_component.ps1 사용 가이드)**: Phase 4 D-1 발견으로 가이드 필요성 입증 → Z-X1과 통합 권장
- **Y-X3 (Sub-path 분리 패턴 표준 등록)**: Phase 4 backend는 다른 폴더 분리 자연 적용 → 미발생, deferred 유지

### Phase 2 P-X 후속 재평가

- **P-X1 (sub-agent enforcement)**: ✅ accepted + applied, **9/9 효과 입증 — 유지**
- **P-X2 (변경성 시뮬 phase-complete 게이트)**: 미적용 상태 — Phase 5 진입 전 채택 권장 (Y-X1 통합)
- **P-X3 (design-review spec-only)**: 미적용 — Phase 11+ design phase 재진입 시점 재평가
- **P-X4 (worktree isolation)**: deferred 유지 — P-X1 9/9 효과 충분
- **P-X5 (매트릭스 표준 등록)**: deferred — P-X2 통합 자연 흡수 가능

---

## 패턴 등록 (meta/patterns.md 후보)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** (update) | P-X1 §SELF-VERIFICATION **9연속 PASS** 효과 누적 측정 (Phase 3 5 + Phase 4 4) | phase-3 + phase-4 | 갱신 (Phase 4) — backend phase 효과 입증 + component_map 15연속 + PlanCard 4연속 |
| **P-GPT-REVIEW-001** (신규) | 외부 LLM 검토 (GPT) 채택 효과 측정 — Phase 4 6→4 Slices (▼33%) / 18~26h → 6~8h (▼66%) | phase-4 | 신규 등록 (Phase 4) — multi-llm-validation 보조 패턴 |

→ Phase 1/2/3 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 (Phase 4 multi-call 자연 확장 입증) / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1, 9연속 입증) / P-DESIGN-LAYERED-001 / P-X1-EFFECT-001 / P-THIN-VERTICAL-001 (Phase 4 backend 입증) — 모두 효과 유지

---

## Skill 사용 로그 (Phase 4 동안)

| Skill | Phase 4 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 4 진입, P-X1 적용된 v1.3.0 유지 |
| qa-check (v1.2.0) | 5 | 진입 점검 + Slice 1~3 + final |
| contract-change | 0 | Phase 4는 contract 변경 0 (ADR-014/015 정합 — output_schema / agent_io_contract 무변경) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.1.0) | 1 | Phase 4 종료 (smoke_test_phase_4 자동 호출 8/8 PASS) |
| design-review | 1 | Slice 4 (Phase 4 impl phase 확인) |
| multi-llm-validation | 0 (정식 호출) / 1 (패턴 동일 — GPT 검토 채택, 사용자 외부 진행) | Phase 5+ 진입 전 정식 호출 권장 |
| harness-audit | 0 | audit_naming + audit_page_component 자동만 (수동 Skill 호출 없음) |
| agent-io-check | 0 | Phase 4는 agent contract 변경 0 — Phase 4.5+ Rewriter 도입 시 활성화 |
| ai-architecture-review | 0 | Phase 4 MOA Lite 부분 활성화 (Critic verdict 노출만) — Phase 7/8 본격 활성화 |
| 기타 unused | — | eval-design / rag-design / cost-review 등 (Phase 5+ 활성화 예상) |

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md P-X1-EFFECT-001 update (9연속) + P-GPT-REVIEW-001 신규 등록
- [ ] meta/proposals/2026-05-28_phase-4-retrospective-proposals.md 작성 (Z-X1~Z-X3, 선택)
- [x] meta/skill_usage_log.md 갱신 (Phase 4 누적)
- [x] phases/active/phase-4-fastapi-extension/closing_notes.md 작성 (다음 phase A/B/C 옵션 명시)
- [ ] 사용자 검토 (Z-X1~Z-X3 우선순위 / 채택 여부 — 다음 phase 진입 전 선택)
- [x] phases/active → phases/archive 이동 (git mv)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
- [ ] 사용자 결정: 다음 phase 옵션 A (Phase 4.5 mini-phase) / B (Phase 5 DB/Auth) / C (다른 우선순위)
```

---

## 다음 phase 진입 권장 사항 (사용자 결정 3-c)

### 옵션 A: Phase 4.5 mini-phase (Critic revise loop + Rewriter)

```
산출물:
  - D6 본격 구현 (P-008 Rewriter)
  - Critic revise 최대 2회 (overall_verdict='revise'시 P-008 호출)
  - revise_round 0/1/2 노출
  - 최종 응답 verdict approve|reject 강제
추정 시간: 8~12h
Acceptance:
  - Critic verdict 'revise'시 P-008 호출 → 갱신된 plan_candidates
  - revise_round 최대 2 (무한 루프 차단, 사용자 결정 5 정합)
  - 최종 응답 verdict 항상 approve|reject (revise 없음)
의존성: Phase 4 4 endpoints (현재 baseline) + P-007 Critic (Phase 1 baseline) + P-008 placeholder
다음 → Phase 5 (DB/Auth + SSE)
권장 시점: 사용자가 영상기획 품질 안정화를 우선시할 때
```

### 옵션 B: Phase 5 DB/Auth (Critic revise는 Phase 6+)

```
산출물:
  - Supabase Auth + RLS
  - plan_store DB migration (in-memory → Supabase row)
  - SSE Progress streaming (D7)
  - 사용자 세션 인증 + plan_id 권한 검증
추정 시간: 15~20h
Acceptance:
  - 다중 사용자 + plan_id 권한 분리
  - SSE Progress 30~60초 대기 UX 활성화
  - Critic revise는 Phase 6+ 통합
의존성: Phase 4 contract endpoints (DB 이관) + Supabase 프로비저닝
다음 → Phase 6 (Output Schema + Agent IO 안정화 + Critic revise loop 통합)
권장 시점: 사용자가 다중 사용자 데이터 누적 + 보안 우선시할 때
```

### 옵션 C: 다른 우선순위 (사용자 시점 재평가)

```
가능 후보:
  - Phase 6 Output Schema (P-006/P-007/P-008 안정화 + agent_io 통합)
  - Phase 9 결과 저장 + Brand Memory 자동 추출 (UX 데이터 베이스)
  - Phase 11+ 안정화 (eval / cost / UX 검증)
추정 시간: 시점에 따라
권장 시점: 사용자가 본 Phase 4 산출물 실 사용 + 데이터 누적 후 우선순위 재평가
```

---

## 변경 이력

- 2026-05-28: Phase 4 회고 최초 작성 (phase-complete v1.1.0 절차 6단계 자동 호출). **P-X1-EFFECT-001 update (9연속) + P-GPT-REVIEW-001 신규 패턴 등록**. P-AGENT-SCOPE-001 mitigation 9/9 입증. **다음 phase A/B/C 옵션 명시 (사용자 결정 3-c)**.
