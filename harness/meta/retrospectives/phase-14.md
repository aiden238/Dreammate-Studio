# Phase 14 회고 — 위저드 ↔ 백엔드 실연결 (Scope A)

> 2026-06-03 | 제품 phase (프론트 배선 + 백엔드 additive). 사용자 결정 B + Scope A.

## 1. 한 일
mock 위저드(/new/quick 4 · /new/discovery 7)를 기존 endpoint(`/plans/start`·`/wizard/{step}`·`/generate`·GET `/plans/{id}`)에 배선 → 위저드도 실 3안 rich 생성(랜딩 `/` 외 흐름 완성). 신규 endpoint 0.

- S1: `moa_orchestrator.build_user_input_from_wizard()` — wizard_data → user_input **additive** 조립(랜딩 byte-identical). pytest 499→508.
- S2/S3: Quick·Discovery generate 페이지 mock 제거 → startPlan→wizardStep×→generateMultiPlan→/plan/[id]. 중간 step 카드는 입력수집 UX 유지(NG1).
- fix: StrictMode navigation 버그(cancelled 플래그) 제거.

## 2. 잘된 것
- ★ **실측 우선 진입**: project-1(메인 세션) 위저드 분석 + 직접 코드 확인으로 "endpoint 이미 존재, 배선만" + "per-step LLM=PARKED" 를 사전 확정 → Scope A 로 정확히 좁힘(과投자 방지).
- ★ **behavior-preserving**: 백엔드 additive(initial_input 우선) → 랜딩 회귀 0(pytest 499 수정 0). 프론트는 generate 페이지 한 곳 집중 → 표면 최소.
- ★ **진단의 힘**: 위저드 stuck 을 "성능/레이어 문제"로 오인하기 쉬웠으나, 네트워크 패널(generate 200 23.48s) + 백엔드 로그(plans=3 approve)로 **백엔드 정상 / 프론트 navigation 버그**로 정확 분리.

## 3. 실수 / 학습 (정직)
- ★ **`.next` 캐시 오염**: dev 서버 가동 중 검증용 `npm run build` 를 같은 `.next/` 에 돌려 청크 깨짐(819.js). → **학습: dev 켜진 채 `next build` 금지.** 검증은 typecheck/lint 로, 프로덕션 build 는 dev 정지 후. (회고 개선안 P-NEXT-DEV-BUILD)
- ★ **StrictMode 1회-실행 패턴 함정**: `startedRef` 가드 + per-effect `cancelled` 조합이 StrictMode(dev) 에서 "유일 run 을 첫 cleanup 이 취소"하는 데드락. → **학습: 1회-실행 effect 에서 cleanup 의 cancelled 로 핵심 side-effect(navigation)를 막지 말 것.** (P-STRICTMODE-ONESHOT)
- ★ **git add -A 우발 포함**: Temp 런처가 fix 커밋에 섞임 → untrack + .gitignore. → 커밋 전 `git status` 확인 습관(이미 규율, 재확인).

## 4. 메트릭
- pytest 499→**508** (+9, S1). 프론트 build 12 routes / typecheck·lint 0. scenario_simulation 36/36.
- 신규 endpoint 0. 운영 .py: moa_orchestrator(additive) 1 + frontend 2. 키 0.
- 커밋 6 (entry/S1/S2/S3/fix/chore). 실측 ~1세션.

## 5. 다음에 가져갈 것
- ★ **더 깊은 대본기획 = 추후 업그레이드**(사용자 플래그): PARKED commercial_viral/director + per-step 실 LLM(NG1) + PKM/RAG 데이터레이어. provisional P15~21, 선행조건(위저드 실연결=본 phase) 충족됨 → 다음 검증/결정 시 후보.
- Discovery 라이브 walk 은 Quick parity 로 대체 — 차기 실사용 시 Discovery 단독 확인 권장.

## 6. 신규 패턴 후보
- **P-STRICTMODE-ONESHOT-001**: StrictMode 1회-실행 effect 에서 cleanup-cancelled 가 navigation/완료 side-effect 를 막지 않게 (startedRef 가드 + cleanup 은 timer 정리만).
- **P-NEXT-DEV-BUILD-001**: dev 서버 가동 중 `next build` 금지(.next 청크 오염) — 검증은 typecheck/lint.
- P-WIZARD-WIRING-001: 위저드 multi-step → 백엔드 wizard_data additive 조립 + 최종 generate 집중 배선(중간 UX 보존, behavior-preserving).
- P-BEHAVIOR-PRESERVING-001 update (프론트 배선 phase에도 적용 — 랜딩 byte-identical).
