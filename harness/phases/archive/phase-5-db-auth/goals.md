# Phase 5 — Goals

> Phase: phase-5-db-auth
> 유형: large phase (DB / Auth / RLS / SSE — MVP 본격 영속화)
> 진입일: 2026-05-29
> 예상 시간: 15~20h (5 Slice)

## 한 줄 정의

Phase 6에서 안정화된 canonical schema를 PostgreSQL/Supabase에 영속화하고, Supabase Auth + JWT + Row Level Security + SSE Progress(D7)를 도입하여 **다중 사용자 안전 운영** baseline 확립.

## 핵심 목표 (G1~G7)

| ID | 목표 | 검증 매핑 |
|---|---|---|
| **G1** | Supabase + PostgreSQL 연결 + 4계층 데이터 모델 schema 영속화 (brands / domains / series / video_projects + plans + users) | A1, A2 |
| **G2** | in-memory `_plan_store` → DB 영속화 (graceful fallback 유지, Phase 6 schema 적용) | A3 |
| **G3** | Supabase Auth + JWT + 세션 처리 (frontend AuthGuard + /auth/login) | A4, A5 |
| **G4** | Row Level Security 정책 (plans / video_projects user_id = auth.uid()) — 다른 user plan 접근 차단 | A6 |
| **G5** | SSE Progress streaming (D7) — 30~60초 대기 시 4단계 progress + 부분 결과 노출 | A7 |
| **G6** | Phase 6 canonical schema 100% 호환 (Critic canonical + revise_history + recommended_plan_index DB 저장) | A8 |
| **G7** | 회귀 0 — Phase 6 baseline 유지 (pytest 144/144 → 165+/165+, smoke 10/10 → 12/12) | A9, A10 |

## 메타 목표 (M1~M4)

| ID | 목표 | 결과물 |
|---|---|---|
| **M1** | multi-llm-validation **formal self** 세 번째 트리거 + **external 실제 작성** (Phase 6에서 placeholder만 있던 형식을 사용자가 외부 GPT/Gemini로 채우거나 Claude 자가 verification 강화) | `meta/validations/2026-05-29_phase-5-pre-entry_self.md` + external |
| **M2** | **security-review Skill 첫 정식 트리거** (Auth/RLS 도입은 보안 인시던트 risk, Skill 절차 따름) | `meta/security_reviews/2026-05-29_phase-5-auth-rls.md` |
| **M3** | scenario_simulation.ps1 **v2** — DB/Auth용 5 시나리오 추가 (Supabase 연결 / RLS 정책 / user 분리 / JWT / SSE event schema) | `scripts/scenario_simulation.ps1` v2 |
| **M4** | P-X1 §SELF-VERIFICATION **22연속 PASS** (Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5) | sub-agent 5 dispatch |

## 사용자 가치 (Why)

- **다중 사용자 안전 운영**: RLS 정책으로 user 간 plan 분리 → MVP 운영 baseline
- **데이터 영속화**: 새로고침/세션 만료 시에도 plan 보존
- **UX 개선**: SSE Progress로 30~60초 대기 시 사용자 이탈 방지 (확정 결정 [10])
- **보안 baseline**: Auth + RLS + JWT → 사용자 데이터 보호 (확정 결정 [19] PII)
- **장기 운영**: Brand Memory 자동 추출 (확정 결정 [8])의 DB 영속 baseline (Phase 6+에서 활성화)

## 비목표 (별도 문서: non_goals.md)

Brand Memory 자동 추출 / RAG 본격화 / 결제 / 팀 기능 / multi-provider / Phase 1 endpoint 제거 — 모두 Phase 7+/8+/21+ 이관.
