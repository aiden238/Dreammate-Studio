# env_contract.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 2+
priority: medium
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

MVP Phase 0~1은 contract 정의 + 골격 코드 작성 단계. Phase 2+ 첫 staging 환경 구축 시점에 환경변수 이름 / 용도 / 비밀 관리 절차를 고정한다. 그 전까지는 `tech_stack_contract.md` §2.6의 배포 가이드와 `llm_security_contract.md` §5.2의 환경변수 격리 원칙으로 충분.

## Scope (TBD)

본 contract가 다룰 범위:

- 환경 분리 (DEV / STG / PROD)
- 환경변수 이름 표준:
    - LLM provider: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (Phase 5+)
    - Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY` (client), `SUPABASE_SERVICE_ROLE_KEY` (backend only)
    - DB: `DATABASE_URL` (FastAPI 직접 접근용)
    - Redis: `REDIS_URL`
    - Sentry: `SENTRY_DSN` (Phase 2+)
    - Vercel/Render env sync 절차
- 시크릿 관리:
    - 저장소 (Vercel env, Render env, GitHub Secrets)
    - 절대 git commit 금지 (.env.example만 commit)
    - 클라이언트 노출 prefix 정책 (`NEXT_PUBLIC_*`만 노출 가능)
- 비밀 회전 정책:
    - 정기 회전 주기 (분기별 권장)
    - 사고 발생 시 긴급 회전 절차 (24시간 내)
    - 회전 시 무중단 절차 (key 2개 병행 유지 → 마이그레이션 → 구 key 폐기)
- 환경별 차이:
    - DEV: 로컬 .env, 가짜 API key 허용
    - STG: 실 API key, 실 LLM 호출, 비용 quota 제한
    - PROD: 실 API key, 모든 정책 적용
- env 검증 hook (서버 시작 시 누락된 env 즉시 fail-fast)
- env 변경 시 PR 절차 (lock 폴더 또는 별도 env 관리 시스템)

## Known Dependencies (when filled in)

외부 표준:
- 12-factor app §3 (Config)
- OWASP Secrets Management Cheat Sheet

내부 의존 contract:
- `docs/contracts/tech_stack_contract.md` §2.6 (Deploy)
- `docs/contracts/llm_security_contract.md` §5.2 (환경변수 격리)
- `docs/contracts/api_contract.md` §14 (CORS allowlist는 env 기반)
- `docs/contracts/backend_boundary.md` (placeholder)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 2+ 진입 (첫 staging 환경 구축 시점)
- 또는 첫 backend endpoint 구현 시작 시점
- 또는 API key 첫 발급 시점
- 또는 외부 deploy(Vercel / Render) 첫 설정 시점

## Related Skill / Phase

- Skill: `security-review` (env 항목 카테고리)
- Phase: 2+
- 책임자: AI(초안) + 사용자(검토, 시크릿은 사용자가 직접 관리)
