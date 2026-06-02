# Phase 14 — Notes (진행 메모)

## 진입 (2026-06-03)
- 방향 결정: **Scope A(최소 배선)** — project-1(메인 세션 6f30283a) 위저드 분석 검토 결과.
  - project-1 결론: 위저드 mock, 랜딩 `/` 만 실동작, 실연결=한 페이즈 분량, per-step 실 LLM 카드=PKM/RAG(PARKED).
  - → Phase 14 = 위저드 입력 → 실 생성(/generate) 배선 → /plan/[id] rich. per-step LLM 은 NG1(PARKED 이연).
- Phase 13 done(archive) 직후, active phase 없음 상태에서 진입. baseline: pytest 499 / origin main 6574da9 / 키 0.

## 핵심 사실 (실측, project-1 + 직접 확인)
- 기존 endpoint/클라이언트 함수 전부 존재 → **신규 endpoint 0**, 배선만.
- 생성 입력 = `moa_orchestrator.py:88` `plan_entry["initial_input"]`. wizard_data 는 현재 미소비 → S1 에서 additive 조립.
- rich gated 는 /generate 경로 내부 → 위저드 자동 상속.
- 랜딩 `/`(dreammate.slice6.plan → /plan) vs 위저드(wizard.* 키, /plan 미연동) 분리 → 위저드를 /plan/[plan_id](백엔드 read)로 수렴.

## 참조
- project-1 세션(6f30283a, 유지 중) = in-context 위저드 분석 원본 (L6614~6790).
- handoff: `meta/handoffs/2026-06-03_checkpoint-phase13-done.md`.
- PARKED: `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md`(per-step 지능 = 여기) / `2026-06-03_commercial-viral-mode-design.md`.

## TODO (slice 진행하며 갱신)
- [x] **S1 ✅ 백엔드 wizard_data 조립** (2026-06-03, commit 대기): `moa_orchestrator.py` `build_user_input_from_wizard()` 헬퍼(additive) + `_WIZARD_STEP_ORDER` + 입력 우선순위 `initial_input > wizard 조립 > "(빈 입력)"`. ★ 랜딩(initial_input) byte-identical — wizard_data 없으면 기존 동일. 신규 test 9 → **pytest 499→508 green**(기존 499 수정 0). contract 무변경(요청/응답 스키마 불변 — 내부 입력 조립만). 다음=S2.
- [x] **S2 ✅ Quick 위저드 실연결** (2026-06-03, commit 대기): `app/new/quick/generate/page.tsx` mock(buildMockPlan/setTimeout) 제거 → 실 배선. generate 페이지 한 곳에서 수집분(step1 prompt/step2 answer/step3 direction) → `startPlan()`→`wizardStep×3`(quick.initial/clarify/direction)→`generateMultiPlan()`→`router.push('/plan/[id]')`. ProgressStepper 실 await 낙관적 진행 + 에러/재시도 UI. rich gated 자동 상속. 중간 step1/2/3 페이지 무변경(입력수집 유지). typecheck+lint+build(12 routes) green. backend 0. 다음=S3.
- [x] **S3 ✅ Discovery 위저드 실연결** (2026-06-03, commit 대기): `app/new/discovery/step/[n]/page.tsx` `Step7Generate`(n=7) mock(setInterval→/plan) 제거 → 실 배선. step1~6 수집 입력 → `startPlan()`→`wizardStep×6`(step1~step6)→`generateMultiPlan()`→`router.push('/plan/[id]')`. 낙관적 stepper + 에러/재시도 UI. 중간 카드(step2~4)·톤(step5)·방향(step6) 입력수집 UX 유지(NG1). `DiscoveryStep7State` import 제거(미사용). typecheck+lint+build(12 routes) green. backend 0. 다음=S4(라이브 검증).
- [ ] S4 라이브 e2e(rich ON) + 회귀 + close — ★ 사용자 라이브 검증 대기
