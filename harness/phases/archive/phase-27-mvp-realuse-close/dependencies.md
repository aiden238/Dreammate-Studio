# Phase 27 — dependencies

| 의존 | 상태 | 근거 |
|---|---|---|
| Phase 1~26 done | ✅ | PHASE_REGISTRY / archive |
| HIP-006~010 → main 머지 | ✅ | a40eb36 (S0, pytest 802 green) |
| 홈 진입 카드 (/new, /new/branding) | ✅ | HIP-008 S4 (app/page.tsx) |
| plan 영속 배선 (`_persist_plan_envelope`, gated) | ✅ | HIP-008 S3 (moa_orchestrator.py) |
| match_approved_knowledge RPC SQL | ✅ | HIP-008 S2 (0008 migration) |
| 핵심 루프 flag (output_mode/PKM/seed/plans_repo) | ✅ 존재(default OFF) | config.py |
| 4계층 /brain CRUD + PKM 루프 | ✅ | Phase 19~26 |
| 위저드 ↔ 백엔드 + 브랜딩→4계층 자동 시드 | ✅ | Phase 14 / Phase 25 |

모든 의존 충족 → 강제 진행 사유 없음.

## 외부 의존 (런타임)

- OpenAI 키 (.env) — director 생성.
- Supabase 키 (.env) — plan/PKM 영속. 단 **로컬 실 DB 영속 검증은 Supabase 프로젝트 의존**(U-1).

## 작업 격리

- 격리 worktree `C:/Users/songb/dreammate-p27` (branch `phase-27-realuse`, main 기준). 동시 HIP-006/007 작업자(main 체크아웃 `phase-27-mvp-realuse-close`)와 인덱스/체크아웃 분리.
