# Phase 27 S5 — 첫-사용자 루프 e2e 검증 (1차 MVP 실사용 마감)

> 2026-06-05 | 격리 worktree `phase-27-realuse` | 통과 기준 = "처음 온 사용자가 도움 없이 director 기획안 1개 생성 → 저장 → 내 brain 축적 → 다음 기획에 반영"

## 1. 자동 검증 (무비용, 완료)

| 검증 | 방법 | 결과 |
|---|---|---|
| realuse 프로파일 부팅 | TestClient(app) under `APP_PROFILE=realuse` + /health | ✅ 200 ok |
| 프로파일 해석 | get_settings() | ✅ app_profile=realuse / eff_output=**director** / plans_repo=True / brand·personal 주입·추출=True / branding_seed=True / rate_limit=False(의도대로 제외) |
| 코드 default 보존 | default(미설정) 경로 | ✅ 모두 OFF / compact = byte-identical |
| 실사용 프로파일 단위 | test_realuse_profile.py | ✅ 6 (default OFF / realuse ON / override 2 / env / invalid) |
| plan 영속(B-3) | test_plans_persistence.py | ✅ 4 (OFF no-op / ON update / ON upsert / graceful) |
| rate_limit(B-7) | test_rate_limit.py | ✅ 5 (OFF no-op / ON 429 / 신원 / 양 window / 독립) |
| AppShell 네비(B-2) | next build + typecheck + lint | ✅ 14/14 라우트 + 0 에러 |
| migration 적용(B-4·M-1) | apply_migrations.py --list/--verify | ✅ 8 순서 + graceful |
| 게이트 | hermetic pytest / scenario_simulation / audit_naming | ✅ 813 / 36/36 / 0 drift |

→ **루프 배선 + 프로파일 활성 + 회귀 0 입증.** 실 생성 품질·실 영속·PKM 누적은 아래 실-런(키/Supabase 필요).

## 1.5 ★ 실 라이브 데모 결과 (2026-06-05, 실 LLM + 실 Supabase)

사용자 opt-in 으로 실제 실행 — **PASS** (P-LIVE-VERIFY-001).

- DB 준비: migration 0007(개인 PKM 출처) + 0004(pgvector + RAG 테이블) + 0008(match_approved_knowledge RPC) 실 Supabase 적용·검증(REST). RAG 인프라 ON(approved_knowledge 비어있음=정상).
- 생성: `generate_plan`(realuse, 실 gpt-4o-mini) → **director 기획안 3개**, director 슬롯(hook_system/retention_architecture/scene_breakdown) + rich 슬롯(hook_variants/shots/thumbnail/title_candidates/cta) **전부 채움**. scene_breakdown 씬별 intent/emotion/retention 구조.
- 영속: **plans 테이블 rows=1 영속됨 ✓** (재시작해도 유지).

### ★ 라이브가 잡은 버그 (자동 테스트가 못 잡음)
- **HIP-008 `_persist_plan_envelope` 스키마 버그**: plans 에 없는 단일 `envelope` 컬럼 insert → PGRST204 → 영속 실패(graceful in-memory 폴백, 휘발). mock 테스트가 스키마 미강제라 통과.
- **수정**: envelope→plans 구조화 컬럼(plan_candidates/critic_evaluation/recommended_plan_index/mode/auth_user_id) 분해. 회귀 테스트 추가(814). 실 Supabase 영속 재확인 PASS. → "automated green ≠ works" 재입증.

## 2. 실-런 체크리스트 (사용자 opt-in — 실 LLM + Supabase, 비용/DB 변경)

> 전제: `backend/fastapi/.env` 에 OPENAI_API_KEY (+ 영속 원하면 SUPABASE_* + migration 0001~0008 적용).

```powershell
# 1) migration 운영 적용 (1회)
python scripts/apply_migrations.py --apply
python scripts/apply_migrations.py --verify   # rpc/테이블 t 확인

# 2) 실사용 프로파일로 백엔드 기동
powershell -ExecutionPolicy Bypass -NoProfile -File scripts/run_realuse_local.ps1
#   (별 터미널) cd apps/web; npm run dev
```

**브라우저 루프 (홈 → 저장 → brain → 반영):**
1. `localhost:3000/` 홈 → 하단 네비(🏠 홈 / ✏️ 새 기획 / 🧠 내 brain) 보임(AppShell).
2. 기획안 생성(빠른 입력 또는 ✏️ 새 기획) → 결과가 **director 깊이**(hook_system / retention_architecture / scene_breakdown 슬롯).
3. 결과 저장 + 피드백 → (인증 + Supabase) plan 영속 + PKM 추출(≥0.9) 적재.
4. 🧠 내 brain → 축적된 PKM/4계층 노드 확인.
5. 같은 사용자로 다음 기획 생성 → 직전 PKM 선호가 반영(톤/방향).

**API 빠른 확인(curl):**
```bash
curl -s -X POST localhost:8000/api/v1/plans/start -H "Content-Type: application/json" -d '{"locale":"ko-KR"}'
# → plan_id 로 /generate 호출 시 director 슬롯 채워짐 확인
```

## 3. human 채점 핸드오프 (B-5)

- 채점 kit + second-opinion = `eval/human_review/2026-06-05_quality-verification.md` (compact/rich/director 실출력 + would_use 시트).
- ★ 사용자 실채점 = deferred(사용자 액션). 회수 시 critic 낙관 편향 캘리브레이션.

## 4. 정직한 한계

- 실 생성 품질(director)·실 Supabase 영속·PKM 누적·다음-반영은 **실-런(§2, opt-in)** 에서만 확인 — 비용 + 사용자 인프라.
- 프론트 시각 e2e(하단 네비 렌더 등)는 자동 build/typecheck 로 갈음(headless 한계, M-2).
