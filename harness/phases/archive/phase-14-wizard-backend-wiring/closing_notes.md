# Phase 14 — Closing Notes (위저드 ↔ 백엔드 실연결, Scope A)

> 종료: 2026-06-03 | 사용자 라이브 검증 PASS 후 phase-complete.

## acceptance 최종 판정

| ID | 항목 | 판정 | 근거 |
|---|---|---|---|
| A1 | 백엔드 wizard_data additive 조립 | ✅ | `moa_orchestrator.build_user_input_from_wizard()` + test 9 (S1) |
| A2-PP | 랜딩 `/` byte-identical | ✅ | initial_input 우선 test + pytest 508(기존 499 수정 0) |
| A3 | Quick 위저드 실연결 | ✅ | S2 + ★ 사용자 라이브 "새로 기획안 만들어봤는데 만들어졌어" |
| A4 | Discovery 위저드 실연결 | ✅(parity) | S3 코드(Quick과 동형 패턴) + build green + 백엔드 로그 step1~6 정상. ★ 사용자 라이브 walk 은 Quick 으로 검증, Discovery 는 동일 패턴 parity |
| A5 | rich gated 상속 | ✅ | GET /plans/{id} 검증 — plan_candidates 3 + rich 슬롯 9 + beat visual/dialogue/caption 전부 채워짐 |
| A6 | 목적지 `/plan/[id]` | ✅ | navigation fix(7cb52e2) 후 위저드 → /plan/<id> + getPlan read |
| A7 | 키 0 | ✅ | 평문 키 commit 0 + Temp 런처 untrack(.gitignore) |
| A8 | 회귀 + 종료 | ✅ | pytest 508 + 프론트 build + scenario_simulation 36/36 + 본 close |

→ **A1~A8 전부 PASS** (A4 Discovery 는 Quick 라이브 PASS + 동형 패턴 parity).

## 라이브 검증 중 발견·수정 (정직 기록)
1. **StrictMode navigation 버그** (fix 7cb52e2): generate 페이지가 React StrictMode(dev) cleanup 의 `cancelled` 플래그에 걸려 생성 완료 후 `/plan/[id]` 이동 실패. → `cancelled` 제거(startedRef 1회 실행 + timer cleanup). 백엔드/생성은 처음부터 정상이었음(로그 plans=3 approve).
2. **`.next` 캐시 오염** (운영 미반영, 환경 이슈): dev 서버 가동 중 검증용 `npm run build` 를 같은 `.next/` 에 돌려 청크 깨짐(`Cannot find module './819.js'`). → dev 정지 + `.next` 삭제 + 재기동으로 복구. **학습: dev 켜진 채 build 금지**(회고 반영).

## 후속 / 추후 업그레이드 (사용자 플래그)
- ★ **더 깊은 대본기획**(레이어 추가/심화): 사용자 요청 — 현재 산출은 "기획 브리프"(product_boundary). 깊은 대본/심화 = **PARKED commercial_viral / director 모드 + per-step 실 LLM 카드(NG1)** 영역. PKM/RAG 데이터레이어 선행조건. → PHASE_REGISTRY PARKED 블록에 이미 정렬됨, 별도 phase(provisional P15~21).
- per-step 실 LLM 카드(P-001~P-005): 위저드 중간 단계를 실 LLM 추천으로 (현재는 입력수집 mock UX) — PKM/RAG(PARKED).

## 산출물
- 코드: `moa_orchestrator.py`(wizard_data additive) + `app/new/quick/generate/page.tsx` + `app/new/discovery/step/[n]/page.tsx`(Step7Generate) 실연결.
- test: `test_wizard_input_assembly.py`(9) → pytest 499→508.
- 신규 endpoint 0 (기존 /plans/start·/wizard·/generate·GET /plans/{id} 배선만).
- 커밋: entry(08b19a0) / S1(b6406b1) / S2(1d42dd1) / S3(0142233) / fix(7cb52e2) / chore(Temp untrack).
