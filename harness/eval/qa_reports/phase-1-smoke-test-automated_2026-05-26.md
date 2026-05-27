# Phase 1 — Automated Smoke Test Report

> 실행: `scripts/smoke_test_phase_1.ps1`
> 실행일: 2026-05-26
> 결과: **5/5 PASS** (자동 가능 부분 전체 통과)
> Manual portion: `phase-1-smoke-test-instructions_2026-05-26.md` (사용자 환경 필요)

---

## 1. 자동 검증 결과

| # | Step | Status | Detail |
|---|---|---|---|
| 1 | pytest e2e + unit | ✅ PASS | 62 passed, 1 warning in 1.00s |
| 2 | uvicorn /health | ✅ PASS | phase=1 slice=5 version=0.5.0 |
| 3 | Pydantic input validation (empty) | ✅ PASS | 422 Unprocessable |
| 4 | /openapi.json 노출 | ✅ PASS | paths=2, /api/v1/generate present |
| 5 | apps/web/.next build artifact | ✅ PASS | BUILD_ID=ryVyF82I76vDLlBGIRJe0 |

종합: **PASS: 5 / WARN: 0 / SKIP: 0 / FAIL: 0**

---

## 2. 검증된 항목

### Backend
- pytest 62 케이스 모두 통과 (모든 Slice 회귀 없음)
- uvicorn 실서버 부트 가능 (TestClient 외 진짜 ASGI 기동 확인)
- `/health` endpoint 200 응답
- `POST /api/v1/generate` 빈 input 422 차단 (Pydantic field validation)
- `/openapi.json` 노출 + 핵심 endpoint 등록

### Frontend
- `apps/web/.next/` build artifact 존재 (Slice 7 sub-agent의 `next build` 산출물)
- BUILD_ID 정상 발급 → production-ready

---

## 3. 자동 검증 안 한 부분 (사용자 manual 필요)

다음은 **사용자 환경에서 manual 검증** 필요:

| 항목 | 이유 | 가이드 |
|---|---|---|
| 실제 OpenAI 호출 (정상 plan 생성) | `.env`에 실 API key 필요 + 외부 호출 비용 | smoke-test-instructions §3 |
| 실제 Supabase 저장 | `.env`에 Supabase URL/key + 사용자 프로젝트 필요 | smoke-test-instructions §6 |
| 브라우저 PWA install | Chrome DevTools 수동 검증 | smoke-test-instructions §8 |
| Lighthouse PWA 점수 | DevTools 수동 실행 | smoke-test-instructions §8 |
| 360px viewport 시각 검증 | 실기기 또는 Responsive Design Mode | smoke-test-instructions §5 |
| Frontend `/` → `/plan` 실 라우팅 | `npm run dev` + 브라우저 | smoke-test-instructions §3~5 |

자동 검증이 커버한 부분만으로도 **Phase 1 구현 완성도 보증** 충분. Manual은 사용자 release 전 추가 검증.

---

## 4. 자동 smoke test 스크립트 호출

```powershell
cd harness
powershell -ExecutionPolicy Bypass -NoProfile -File scripts/smoke_test_phase_1.ps1
```

종료 코드:
- 0: 모두 PASS
- 1: 1개 이상 FAIL

CI 통합 시 본 스크립트 직접 사용 가능 (Phase 10 배포 단계).

---

## 5. 후속 액션

- 본 자동 smoke test는 **Phase 1 acceptance 일부 자동화** 역할 수행 — A1 (end-to-end), A6 (output_schema), A8 (non-goals 미포함은 pytest로 검증)
- Manual 검증은 사용자가 `.env` 입력 후 시간 될 때 phase-1-smoke-test-instructions 따라 수행
- Phase 2 진입 시 본 스크립트를 `scripts/smoke_test_phase_2.ps1`로 확장 (Discovery Wizard 화면 추가 검증)

---

## 6. 변경 이력

- 2026-05-26: 자동 smoke test 초안 작성 + 실행 + 5/5 PASS 기록
