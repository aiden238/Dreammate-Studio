# Phase 14 — Scope (위저드 실연결, Scope A 최소 배선)

> ★ Scope A = 위저드 입력을 모아 **실 생성 경로**로 연결(중간 step 카드 현행 유지). per-step 실 LLM 카드(P-001~P-005)는 **PARKED(PKM/RAG)** 이연. 랜딩 `/` byte-identical.

## 현황 (실측)
| 경로 | 백엔드 호출 | 저장/이동 | 상태 |
|---|---|---|---|
| 랜딩 `/` | ✅ POST `/api/v1/generate` | `dreammate.slice6.plan` → `/plan` | **실동작 (불변 대상)** |
| `/new/quick/*` (4) | ❌ mock(setTimeout) | `wizard.quick.*` (인라인 PlanCard) | **실연결 대상** |
| `/new/discovery/step/*` (7) | ❌ mock(setInterval) | `wizard.discovery.*` (인라인) | **실연결 대상** |
| `/plan/[plan_id]` | ✅ GET `/api/v1/plans/{id}` | 백엔드 read | **위저드 목적지 (재사용)** |

기존 자산(이미 존재, 호출만 안 됨): client `startPlan`/`wizardStep`/`generateMultiPlan`/`getPlan` (`lib/api.ts`) + 백엔드 `POST /plans/start`·`/plans/{id}/wizard/{step}`·`/plans/{id}/generate`·`GET /plans/{id}` (`routers/plans.py`). 생성 입력은 `moa_orchestrator.py:88` `plan_entry["initial_input"]`.

## 포함 (In-Scope) — Entry + S1~S4
### Entry (본 문서)
- `phases/active/phase-14-wizard-backend-wiring/` 8 entry + `meta/validations/2026-06-03_phase-14-pre-entry_self.md`(self 13th) + PHASE_REGISTRY/PROJECT_STATE active.

### S1 — 백엔드: wizard_data → 생성 입력 additive 소비
- `routers/plans.py` 또는 `orchestration/moa_orchestrator.py`: generate 시 `initial_input` 이 비어있고 `wizard_data` 가 있으면 step 입력을 **조립해 user_input** 으로 사용 (additive). ★ 랜딩 경로(`initial_input` 채움) byte-identical — `wizard_data` 없으면 기존과 동일.
- (필요 시) `docs/contracts/api_contract.md` §8.2/§8.3 위저드 생성 입력 소비 명시 — contract-change.
- tests: wizard_data 조립 + 랜딩 회귀 0.

### S2 — 프론트: Quick 위저드 실연결
- `app/new/quick/*`: `buildMockPlan`/setTimeout 제거 → `startPlan` → step별 `wizardStep` → `generateMultiPlan` → `router.push('/plan/{plan_id}')`. plan_id 를 위저드 상태에 보관.
- tests/typecheck/lint + design.md 준수.

### S3 — 프론트: Discovery 위저드 실연결
- `app/new/discovery/step/*`: 동일 패턴(7단계 입력 누적 → generate → /plan/[id]). mock 카드는 **입력 수집 UX로 유지**(per-step 실 LLM = non-goal).

### S4 — 검증 + 종료
- 위저드 end-to-end 라이브(실 LLM, 키 user-provided, rich ON 데모 1회) + 회귀(pytest 499 + 신규 green) + phase-complete(retrospective + archive + REGISTRY/STATE).

## contract-change 대상 (있으면)
- `docs/contracts/api_contract.md` (§8 위저드 생성 입력 소비 명시 — S1, additive). frontend_design_contract/page_map 갱신(필요 시).

## ★ 변경 허용 / 금지
```
editable:
  Entry : phases/active/phase-14-*/** + validation self + PHASE_REGISTRY + PROJECT_STATE
  S1    : routers/plans.py / orchestration/moa_orchestrator.py (wizard_data 조립 additive) + api_contract(필요 시) + tests
  S2    : apps/web/app/new/quick/** + lib/api/state (위저드 실연결) + 필요한 lib
  S3    : apps/web/app/new/discovery/** + lib (위저드 실연결)
  S4    : eval/regression_results/phase-14-* + retrospective + closing + state docs
forbidden:
  ★ 랜딩 `/` 경로(app/page.tsx, generate.py /generate, dreammate.slice6.plan) 동작 변경 (byte-identical 유지)
  ★ per-step P-001~P-005 실 LLM 카드 생성 (PARKED PKM/RAG — non-goal)
  ★ rich default OFF→ON 전환 (별도 결정)
  ★ 완성 대본/영상 제작 (product_boundary)
  ★ 실 키 평문 commit
```
