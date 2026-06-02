# Phase 14 — Acceptance (A1~A8 + 게이트)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | **백엔드 wizard_data 조립(additive)** — generate 시 `initial_input` 없고 `wizard_data` 있으면 step 입력을 user_input 으로 조립. ★ `initial_input` 있으면 기존과 동일 | test: wizard_data 케이스 user_input 조립 + 랜딩(initial_input) 경로 회귀 0 | S1 |
| **A2-PP** | **랜딩 `/` byte-identical(behavior-preserving)** — `app/page.tsx`/`/generate`/`dreammate.slice6.plan` 동작 불변 | pytest 499 회귀 0 + 랜딩 e2e test | S1·S4 |
| **A3** | **Quick 위저드 실연결** — `/new/quick` 4단계 완주 → `startPlan`→`wizardStep`×→`generateMultiPlan` → `/plan/{plan_id}` 실 3-plan. `buildMockPlan`/setTimeout 제거 | typecheck + 위저드 e2e(mock client 또는 라이브) | S2 |
| **A4** | **Discovery 위저드 실연결** — `/new/discovery/step/1~7` 완주 → 동일 패턴 → `/plan/{plan_id}` 실 3-plan. mock plan 생성 제거 | typecheck + e2e | S3 |
| **A5** | **rich gated 상속** — `rich_output_enabled=true` 시 위저드 결과도 rich 8섹션(자동 상속, 별도 rich 배선 0) / OFF 시 compact | 라이브 데모(ON) + OFF 회귀 | S4 |
| **A6** | **목적지 통일** — 위저드 → `/plan/[plan_id]`(GET `/plans/{id}` 백엔드 read). 위저드 인라인 mock PlanCard 제거 | route 확인 + getPlan 연동 | S2·S3 |
| **A7** | **키 0** — 라이브 데모는 user-provided 키, 평문 commit 0 | `git diff \| grep sk-/AIza` 0 | S4 |
| **A8** | **회귀 + 종료** — pytest 499 + 신규 green + phase-complete(retrospective + archive) | 전체 | S4 |

## ★ behavior-preserving 게이트 (A2-PP — 핵심)
```
랜딩 `/` 경로 = 불변:
  - app/page.tsx → POST /generate → dreammate.slice6.plan → /plan : 동작·직렬화 byte-identical
  - generate.py /generate + moa_orchestrator initial_input 경로 : wizard_data 가 없을 때 기존과 100% 동일
  - S1 백엔드 변경은 additive (wizard_data 있을 때만 새 조립 경로)
검증: pytest 499 green (기존 수정 0) + 랜딩 회귀 test
```

## 검증 자동/수동
| 항목 | 방법 | 자동/수동 |
|---|---|---|
| wizard_data 조립 + 랜딩 회귀 | pytest (mock orchestrator/endpoint) | 자동 |
| Quick/Discovery 위저드 흐름 | typecheck + (가능 시) 위저드 client mock e2e | 자동/반자동 |
| 위저드 → 실 rich 카드 | 라이브(localhost, 실 LLM, rich ON) 1회 | 수동 |
