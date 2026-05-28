# Phase 5 — Notes

## Entry (2026-05-29)

- phase-start v1.3.0 §6 4점검 PASS (C1~C11, U1~U6)
- audit_naming PASS 0 drift
- Phase 6 baseline 완전 안정 (Critic canonical + Rewriter v1.1.0 + revise_history canonical) — DB 진입 안전
- 5 Slice, 모두 sub-agent dispatch
- 핵심 의무: **security-review Skill 첫 정식 트리거** (Slice 1) + ADR-020 Supabase 채택 + scenario_simulation v2 (DB/Auth 5 시나리오 추가)
- Phase 4.5 wrapper UI 패턴 계승: PlanCard.tsx 13연속 0줄 + AuthGuard / SSE Progress UI는 wrapper

## Slice 1~5 (작업 시 갱신)

### Slice 1 — Pre-Entry + Security (★ 완료, 2026-05-29)

- multi-llm-validation formal **세 번째 정식 트리거** — V1~V6 PASS
  - V1 Supabase 채택 / V2 JWT 정책 / V3 RLS 정책 / V4 SSE schema / V5 revise_history JSONB / V6 canonical DB 호환
  - meta/validations/2026-05-29_phase-5-pre-entry_self.md
  - meta/validations/2026-05-29_phase-5-pre-entry_external.md (placeholder, 사용자 외부 진행 권장)
- **security-review Skill ★ 첫 정식 트리거** — T1~T6 위협 모델 + §4 영역 1~10 점검
  - T1 JWT 누수 HIGH / T2 RLS 우회 HIGH / T3 Refresh token MEDIUM / T4 SSE hijacking MEDIUM / T5 SQL injection LOW / T6 PII MEDIUM
  - 영역 1~10: PASS 5 (1, 3, 6, 7, 10) + PARTIAL 2 (5, 8 → Slice 3/4 후 PASS) + N/A 3 (2, 4, 9 → Phase 7+)
  - meta/security_reviews/2026-05-29_phase-5-auth-rls.md
- **ADR-020 Supabase 채택** — docs/decisions/phase_5_supabase_adoption.md
  - 대안 비교 (Supabase / PostgreSQL 자체 / Firebase / 자체 서버)
  - Free tier 0원 + RLS 내장 + pgvector 호환 (Phase 7 RAG 정합)
  - vendor lock-in trade-off 명시 + Phase 21+ 마이그 계획
- **scenario_simulation.ps1 v2** — 5 → 10 시나리오
  - S1~S5 (Phase 4.5/6 baseline) + S6 Supabase / S7 RLS / S8 user 분리 / S9 JWT / S10 SSE
  - Slice 1 시점 5/10 PASS (의도된 PARTIAL, S6~S10는 Slice 2~4에서 파일 생성)
  - Slice 5 final 10/10 PASS 목표 (P-X2 세 번째 자동 게이트)
- **skill_usage_log 갱신**: security-review 1 (첫 정식) + multi-llm-validation 4 (formal 세 번째) + phase-start 7 + qa-check 30
- **PROJECT_STATE 갱신**: phase_5_* 키 신규 + current_sprint phase-5-slice-1 + total_commits 53 → 54

### Slice 2~5 (대기)

- Slice 2 (4~5h): Supabase + Schema migration + plans_repo + contract-change (db_schema.md 신규)
- Slice 3 (4~5h): Auth + JWT + Frontend Login + AuthGuard (httpOnly cookie)
- Slice 4 (3~4h): RLS + SSE Progress D7 + ADR-021/022
- Slice 5 (2~3h): Close + 회귀 검증 + security-review 두 번째 + P-X2 세 번째 자동 게이트 + retrospective

### Open issues / 외부 검토 차이

- 본 placeholder는 사용자 외부 진행 시 채울 것
- 외부 검토 차이 발견 시 본 §Open issues에 기록 + Slice 5 회고 §개선 제안 반영
