# Phase 6 — Non-Goals

> Phase 6에서 명시적으로 제외하는 항목. scope creep 시 즉시 사용자 알림.

## 명시적 제외 (NG1~NG12)

| ID | 항목 | 이관 | 사유 |
|---|---|---|---|
| **NG1** | Supabase Auth + JWT | Phase 5 | DB/Auth는 Phase 5 단일 phase 격리 |
| **NG2** | PostgreSQL + RLS 정책 | Phase 5 | |
| **NG3** | SSE Progress streaming (D7) | Phase 5 | |
| **NG4** | DB migration files (0001_init.sql 등) | Phase 5 | Phase 6은 schema **결정**만, migration **실행**은 Phase 5 |
| **NG5** | in-memory `_plan_store` → DB 영속화 | Phase 5 | |
| **NG6** | **PlanCard.tsx 수정** | Phase 7+ | **10연속 0줄 baseline 유지** |
| **NG7** | **component_map.md 수정** | Phase 7+ | **20연속 0줄 유지** |
| **NG8** | prompt_registry **본문 정식 작성** | Phase 7+ | semver/io/rollback 골격만 contract에 등록, 본문 인라인 유지 |
| **NG9** | revise loop 효과 eval (golden_set 자동 평가) | Phase 9+ | eval-run Skill 정식화 후 |
| **NG10** | multi-provider client factory (Z-X2) | Phase 21+ | over-engineering 회피 |
| **NG11** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ | 사용자 결정 5-a 계승 |
| **NG12** | fallback 4가지 완전 제거 | Phase 9+ eval | Phase 6에서는 **deprecation note만**, 실제 제거는 eval 안정화 후 |

## 단어 수준 금지 (신규 파일에 등장 금지)

- `supabase`, `RLS`, `row_level_security`
- `SSE`, `EventSource` (LLM streaming "stream"은 허용)
- `migration` (단, `migration_progress` PROJECT_STATE 갱신 또는 ADR 참조 본문은 허용)
- `JWT`, `auth.uid()`
- `Anthropic`, `Claude API`, `claude-3`

## 회피 패턴

- ❌ "조금만"이라며 DB 진입을 Phase 6에 끌어옴
- ❌ contract 변경 김에 prompt body까지 정식 작성
- ❌ Critic fallback 완전 제거 (회귀 위험 ↑ — Phase 9+ eval 후로 미룸)
- ❌ PlanCard 수정 ("type 명시 변경 김에")

## 사용자 결정 6-a 계승 (PlanCard 무수정)

Phase 4부터 5연속, Phase 4.5에서 9연속 → Phase 6 끝에 **10연속 baseline**. types.ts에서 CriticVerdict type 추가/수정은 OK이지만 PlanCard prop은 추가 X (wrapper UI 정신 유지).
