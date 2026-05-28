# Phase 4 Retrospective — 개선 제안 (Z-X)

> 작성일: 2026-05-28
> 출처: `meta/retrospectives/phase-4.md` §개선 제안
> 상태: **proposed (사용자 검토 대기)** — 다음 phase 진입 전 채택 여부 결정 권장

---

## 배경

Phase 4 (FastAPI 기본 백엔드 구현 확장 — 3-plan + multi-model + Critic verdict) 종료 시점 회고에서 도출된 개선안.

Phase 4 핵심 성과:
- **P-X1 §SELF-VERIFICATION 9연속 PASS** (Phase 3 5 + Phase 4 4) — P-AGENT-SCOPE-001 mitigation 누적 입증
- **component_map.md 15연속 0줄 보존** (Phase 2 6 + Phase 3 5 + Phase 4 4)
- **PlanCard.tsx 4연속 0줄 보존** (사용자 결정 6-a, D3 Phase 5+ 이관)
- **GPT 검토 채택 효과**: 6→4 Slices (▼33%), 18~26h → 6~8h (▼66%)
- A1~A10 10/10 PASS, smoke 8/8 PASS, audit_naming + audit_page_component 0 drift

본 문서는 Phase 4에서 추가 발견된 **개선 제안 3건** (Z-X1 / Z-X2 / Z-X3) + 기존 Y-X / P-X 후속 재평가 결과를 담는다.

---

## Z-X1 (선택, 우선순위: 보통): audit_page_component.ps1 dynamic route 정규화 표준화

### 무엇을

- 현재: hardcoded `if` (`/new/discovery/step/[n]` + Phase 4에서 추가 `/plan/[plan_id]`) 정규화
- 변경: regex-based whitelist (`/\[[^/]+\]/` 패턴) 또는 별도 config 파일 (e.g., `scripts/audit_dynamic_routes.json`)에서 phase별 정규화 케이스 등록

### 왜

- Phase 5+ 새 dynamic route (예: `/series/[series_id]`, `/brand/[brand_id]/plans`) 추가 시 audit script 보강 부담 ↓
- drift 자동 검출 정밀도 ↑ + Phase 4 D-1 같은 발견 → Slice 후속 해소 사이클 단순화
- (Y-X2 흡수 가능 — audit_page_component.ps1 사용 가이드 작성 시 정규화 표준화 함께 진행)

### 어디에

- `scripts/audit_page_component.ps1` § dynamic route 정규화 section (line ~68-104)
- (선택) `scripts/audit_dynamic_routes.json` 신규 — phase 진입 시 추가 dynamic route 등록

### 예시

```powershell
# 현재 (hardcoded)
if ('/new/discovery/step/[n]' -in $actual_routes) { ... }
if ('/plan/[plan_id]' -in $actual_only) { ... }

# 권장 (config-based)
$dynamic_normalize = Get-Content scripts/audit_dynamic_routes.json | ConvertFrom-Json
foreach ($entry in $dynamic_normalize.entries) {
    if ($entry.actual_route -in $actual_only) {
        # 정규화 적용
    }
}
```

### 영향

- 영향 파일 수: 1~2 (audit_page_component.ps1 + 선택 새 config json)
- 회귀 위험: 0 (Phase 3 + Phase 4 dynamic routes 모두 동일 동작 검증 가능)

### 결정 시점

- Phase 5+ 진입 직전 (Phase 5 새 dynamic route 추가 가능성)
- 또는 Phase 11+ design phase 재진입 시점

---

## Z-X2 (선택, 우선순위: 낮음): multi-provider client factory baseline

### 무엇을

- 현재: `agents/planning.py`가 OpenAI client 고정 (`from openai import AsyncOpenAI`)
- 변경: `_get_llm_client(provider: Literal["openai", "anthropic", "custom"], model: str)` factory 함수 추가
- config.py에 `llm_provider_for_3plan: list[str]` (default `["openai", "openai", "openai"]`)

### 왜

- 변경성 시뮬 §시나리오 8 (multi-provider 추가) 현재 3 파일 영향 (planning.py + config.py + .env.example)
- factory 도입 시 2 파일 영향으로 압축 (agents/planning.py 1줄 변경 + config.py provider list 추가)
- Phase 21+ Anthropic / Custom 진입 전 baseline 확립

### 어디에

- `backend/fastapi/agents/planning.py` (factory 함수 추가)
- `backend/fastapi/config.py` (`llm_provider_for_3plan` 추가)

### 영향

- 영향 파일 수: 2~3 (planning.py + config.py + 선택 새 lib/llm_client_factory.py 분리)
- 회귀 위험: 낮음 (현 default OpenAI 유지 + factory 분기는 단순 if/elif)

### 우려

- Phase 4 종료 시점에 도입하면 over-engineering 가능 (Phase 21+ Anthropic 도입 실제 결정 전)
- **권장**: Phase 21+ 진입 전 검토 → 현 단계 deferred (Z-X2 placeholder만)

---

## Z-X3 (선택, 우선순위: 낮음): Critic best-plan 선택 로직

### 무엇을

- 현재: 3-plan 모두 동일 우선순위로 응답 (Body.plan_candidates 순서 = approach_label 순서)
- 변경: Critic 8-dim verdict로 가장 좋은 plan을 evaluate → `Body.recommended_plan_index: int` (0/1/2) 노출
- frontend `/plan/[plan_id]`에서 추천 plan highlight (Phase 4 PlanCard.tsx 무수정 정신 유지하려면 `recommended` prop 추가 X — wrapper UI로 처리)

### 왜

- 3개 중 사용자 결정 부담 ↓ (추천 1개 highlight + 사용자가 reject 가능)
- Critic 효과 측정 가능 (recommended_plan_index = user_selected_plan_index 일치율 — 추후 eval/golden_set 확장)

### 어디에

- `backend/fastapi/agents/critic.py` (best-plan 선택 로직)
- `backend/fastapi/schemas/output.py` (Body.recommended_plan_index 추가)
- `apps/web/lib/types.ts` (MultiPlanEnvelope.recommended_plan_index 추가)

### 영향

- 영향 파일 수: 3~5 (backend 3 + frontend 2)
- 회귀 위험: 낮음 (`Optional[int]` 추가 — 기존 응답 호환)

### 결정 시점

- Phase 4.5+ Critic revise loop 도입 시 함께 결정 (사용자 데이터 누적 후 best-plan logic 유의미)

---

## 기존 Y-X / P-X 후속 재평가

### Y-X1 (Phase 3, design_handoff §6.1 매핑표 spec/code 칸 분리)

- **Phase 4 적용 여부**: 미적용 — Phase 4는 backend 중심 (spec 변경 0)
- **재평가**: Phase 11+ design phase 재진입 시점 적용 권장
- **상태**: deferred 유지

### Y-X2 (Phase 3, audit_page_component.ps1 사용 가이드)

- **Phase 4 적용 여부**: 미적용 (가이드 작성 X) → Phase 4 D-1 발견으로 가이드 필요성 입증
- **재평가**: Z-X1 (정규화 표준화)과 통합 권장
- **상태**: Z-X1 흡수

### Y-X3 (Phase 3, Sub-path 분리 패턴 표준 등록)

- **Phase 4 적용 여부**: 미발생 (Phase 4 backend는 다른 폴더 분리 자연 적용 — backend/fastapi/* vs apps/web/* + docs/decisions/*)
- **재평가**: P-FOLDER-PARALLEL-001 보강 후보 유지
- **상태**: deferred 유지

### P-X1 (Phase 2, sub-agent §SELF-VERIFICATION)

- **Phase 3+4 적용 여부**: ✅ applied + **9/9 효과 입증** (Phase 3 5 + Phase 4 4)
- **상태**: **유지 — phase-start v1.3.0 §6.3 의무 절차 보존**

### P-X2 (Phase 2, 변경성 시뮬 phase-complete 게이트)

- **Phase 4 적용 여부**: 미적용 — manual walkthrough만 진행
- **재평가**: Phase 5 진입 전 채택 권장 (Y-X1과 통합)
- **상태**: **Phase 5 진입 전 채택 권장 (우선순위 ↑)**

### P-X3 (Phase 2, design-review SKILL.md spec-only 분기)

- **Phase 4 적용 여부**: 미적용 — Phase 4는 impl phase
- **재평가**: Phase 11+ design phase 재진입 시점
- **상태**: deferred 유지

### P-X4 (Phase 2, worktree isolation)

- **Phase 3+4 적용 여부**: 미적용 — P-X1 효과 9/9로 충분
- **상태**: **deferred 유지 (P-X1 효과 9/9 = worktree 불필요)**

### P-X5 (Phase 2, 매트릭스 표준 등록)

- **Phase 4 적용 여부**: 미적용 — multi_slice_plan template에 충돌 분석 매트릭스 이미 포함
- **상태**: P-X2 통합 자연 흡수 (deferred)

---

## 우선순위 요약

| ID | 우선순위 | 결정 시점 | 채택 시 영향 |
|---|---|---|---|
| **Z-X1** | 보통 | Phase 5+ 진입 직전 | audit script 보강 부담 ↓ + 자동화 ↑ |
| **Z-X2** | 낮음 | Phase 21+ 진입 직전 | multi-provider 변경성 ↑ (over-engineering 우려) |
| **Z-X3** | 낮음 | Phase 4.5+ Critic revise 도입 시 | UX ↑ (추천 plan highlight) |
| Y-X1 → Z-X1 | 보통 | Z-X1 통합 | (위와 동일) |
| Y-X2 → Z-X1 | 보통 | Z-X1 통합 | (위와 동일) |
| Y-X3 | 낮음 | Phase 4+ Wave 3 재발 시 | 패턴 등록만 (영향 0) |
| P-X1 | (적용 유지) | — | **9/9 효과 입증** |
| **P-X2** | **높음** | **Phase 5 진입 전** | **변경성 시뮬 자동화 (Y-X1 통합)** |
| P-X3 | 낮음 | Phase 11+ | spec-only 절차 분기 |
| P-X4 | (deferred 유지) | — | (P-X1 충분) |
| P-X5 | (deferred 유지) | — | (P-X2 흡수) |

---

## 채택 절차

1. 사용자 본 문서 읽기 (다음 phase 진입 직전)
2. Z-X1 / Z-X2 / Z-X3 + P-X2 (높음) 채택 여부 결정
3. 채택 항목별 contract-change Skill 절차 (Skill 파일 / config / spec 변경 시) 또는 단순 코드 / 도구 변경
4. PROJECT_STATE.md `phase_4_retrospective_proposals: accepted_X / deferred_Y` 갱신
5. meta/patterns.md / SKILL.md 갱신 (해당 시)
6. 다음 phase entry commit에 채택 항목 명시

---

## 변경 이력

- 2026-05-28: Phase 4 회고 proposals (Z-X1~Z-X3) 작성 + 기존 Y-X / P-X 후속 재평가. **사용자 검토 대기 상태**.
