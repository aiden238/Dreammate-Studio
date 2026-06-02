# Phase 14 회귀/검증 결과 — 위저드 ↔ 백엔드 실연결 (Scope A)

> 2026-06-03 | phase-complete close gate

## 자동 게이트
| 게이트 | 결과 |
|---|---|
| pytest (backend) | **508 passed** (Phase 13 baseline 499 + S1 신규 9, 기존 499 수정 0) |
| 프론트 typecheck (tsc) | PASS (0 error) |
| 프론트 lint (next lint) | PASS (0 warning) |
| 프론트 build (next build) | PASS — 12 routes |
| scenario_simulation.ps1 (P-X2) | **36/36 PASS** |
| 키 commit | 0 (`git diff` sk-/AIza 0, Temp 런처 untrack) |

## behavior-preserving (A2-PP)
- 랜딩 `/` → `/generate` → `dreammate.slice6.plan` → `/plan`: 동작 불변. S1 백엔드는 additive
  (`initial_input` 있으면 기존 경로, `wizard_data` 는 그것이 없을 때만 조립) → pytest 499 수정 0.
- initial_input 우선 test(`test_generate_initial_input_wins_landing_byte_identical`)로 랜딩 경로 보존 입증.

## 라이브 e2e (사용자 확인)
- ★ 위저드(Quick) → `startPlan` → `wizardStep×3` → `generateMultiPlan` → `/plan/<id>` → **실 3안 rich 생성 확인**(사용자).
- 백엔드 로그(라이브): `plans/generate ok plan_id=46172710 plans=3 verdict=approve` + GET /plans/{id} 검증 —
  plan_candidates **3** + rich 슬롯 9(hook_variants/target_audience/tone/shots/thumbnail/title_candidates/cta/references/length_variants) + beat visual/dialogue/caption **전부 채워짐**.
- rich gated 자동 상속 확인(RICH_OUTPUT_ENABLED=true 라이브 데모).

## 발견·수정
- StrictMode navigation 버그(generate 페이지 cancelled 플래그) → fix 7cb52e2. 백엔드/생성은 처음부터 정상.
- `.next` 캐시 오염(dev 중 build) → dev 정지+.next 삭제+재기동 복구. 운영 코드 무관.

## 결론
- Phase 14 Scope A(위저드 입력 → 실 생성 → /plan/[id]) **완료·검증**. 신규 endpoint 0, behavior-preserving, 키 0.
- 더 깊은 대본기획 = PARKED(commercial_viral/director + per-step LLM) 추후 업그레이드.
