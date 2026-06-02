# Phase 14 — Dependencies

## 선행 Phase (전부 done)
| Phase | 상태 | 본 phase 가 의존하는 것 |
|---|---|---|
| Phase 4 (3-plan endpoints) | ✅ done | `POST /plans/start` · `/plans/{id}/wizard/{step}` · `/plans/{id}/generate` · `GET /plans/{id}` skeleton + `_plan_store` |
| Phase 8 (MOA orchestrator) | ✅ done | `orchestration/moa_orchestrator.generate_plan()` (위저드 generate 가 위임) |
| Phase 9 (저장/피드백) | ✅ done | `/plan/[plan_id]` 결과 표시 + select/feedback (위저드 목적지 재사용) |
| Phase 13 (rich gated) | ✅ done (archive) | `rich_output_enabled` 분기 + PlanCard rich 조건부 8섹션 (위저드가 자동 상속) |

## 기존 자산 (재사용 — 신규 endpoint 불필요)
- 클라이언트: `apps/web/lib/api.ts` `startPlan`/`wizardStep`/`generateMultiPlan`/`getPlan` (정의됨, **위저드가 호출만 안 함**).
- 백엔드: `routers/plans.py` 4 endpoint + `_plan_store[plan_id].wizard_data`.
- 생성 입력: `moa_orchestrator.py:88` `plan_entry["initial_input"]` (S1 에서 `wizard_data` 조립 additive 추가).
- 목적지: `app/plan/[plan_id]/page.tsx` (GET `/plans/{id}` read) + PlanCard rich.

## 외부 의존 (가정)
- OpenAI(+gateway) 키 = .env user-provided (라이브 데모/실 생성 시). 회귀 테스트는 mock.
- 로컬 서버 재기동: 백엔드 `Temp/run_local_backend.py`(+`RICH_OUTPUT_ENABLED=true` 데모 시) / 프론트 `cd apps/web && npm run dev`.

## 회귀 게이트
- pytest **499** (Phase 13 baseline) = OFF byte-identical 회귀 게이트. S1 백엔드 변경은 additive(랜딩 경로 불변)로 499 유지 + 신규.
