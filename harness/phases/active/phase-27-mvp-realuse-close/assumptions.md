# Phase 27 — assumptions (진입 4점검)

## §1.1 확정 가정

- HIP-006~010 main 머지 토대(a40eb36) — 홈 진입·plan 영속 배선·RAG RPC SQL 존재.
- 외부 의존(Supabase, OpenAI) 가용 — 키는 backend/fastapi/.env (커밋 금지).
- 실사용 활성 = **env 프로파일** 방식. 글로벌 코드 default flag는 OFF 유지(기존 pytest 802 byte-identical).
- output_mode = **director** (사용자 결정 2026-06-05).
- 범위 = **로컬 마감까지** (실 배포·실 migration 실행·human 실채점은 제외, 스크립트/kit 핸드오프까지).
- **audit_naming 통과 (2026-06-05, 0 drift)**.

## §1.2 불확실 항목 (phase-complete 시 회고)

- **U-1**: plans_repo ON 실 영속은 Supabase 실 DB 필요 — 로컬 mock 환경에선 graceful fallback만 확인 가능(실 영속 row 검증은 키 있는 환경 의존).
- **U-2**: rate_limit 저장소 — in-memory(단일 프로세스) vs Supabase 카운터. 최소 구현은 in-memory 우선(멀티프로세스 공유는 M-6와 함께 후속).
- **U-3**: director 토큰 비용 실사용 패턴 미상(프로파일 ON 시 compact 대비 ~수배). cost_control 문서 기준.
- **U-4**: 프론트 시각 e2e는 headless 한계 — DOM/typecheck로 대체.

## §6.2 Simplest Slice (3회 압축)

- 1차: "홈→생성→저장→brain 축적→다음 반영 전체 루프를 실사용 프로파일로 켜고 검증"
- 2차: "실사용 프로파일(env) 정의 + plans_repo ON 검증 + 첫-사용자 e2e"
- 3차: **"실사용 프로파일 env 1개 정의 → 그 프로파일에서 generate 가 effective director 출력 + PKM/plans_repo 경로를 타는지 로컬 1회 확인"** ← Simplest Slice (= S1 핵심)

S1이 서면 S2(네비)/S3(rate_limit)/S4(영속검증)/S5(e2e)로 확장.

## §6.3 Surgical Scope

- editable / read-only / forbidden = scope.md 참조.
- 모든 sub-agent prompt에 P-X1 자기검증(git diff --stat vs editable/forbidden) 의무 포함.

## §6.4 Verification

- 성공 기준 A1~A6 = acceptance.md 와 1:1. 자동(pytest/scenario_sim/audit/typecheck) 우선, A2/A5만 수동 DOM/e2e.
