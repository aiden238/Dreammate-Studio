# Phase 17 — Scope

## 포함 (in-scope)

- **가-S1**: auth 신원(auth_user_id/brand_id)을 생성 흐름에 연결 (라우터 → orchestrator → planning).
  현재 익명(user_id=NULL) 경로에 신원을 **선택적으로** 흘려보낸다 (gated, 익명도 그대로 동작).
- **가-S2**: brand_memory_entries 로드(BrandMemoryRepo) → `build_constraint_preamble` 구속 주입을
  운영 planning 에 연결 (gated flag; brand_memory 없으면 기존 프롬프트 byte-identical).
- **다-S3**: `pkm_entries`(personal scope) migration + PkmRepo(graceful) + 개인 메모리 적재/조회.
- **다-S4**: 개인+brand(+series) 통합 주입 + 실 e2e 테스트 + (가능 시) 실데이터 fit 재측정.

## 예상 파일 변경

| 분류 | 경로 |
|---|---|
| editable | `backend/fastapi/routers/{generate,plans}.py`(신원 전달) · `orchestration/moa_orchestrator.py`(신원→brand_memory→주입) · `agents/planning.py`(주입 슬롯, gated) · `config.py`(gated flag) · `db/migrations/0006_*`(pkm_entries) · `db/repositories/`(PkmRepo) · tests |
| editable | `phases/active/phase-17-*`, `PROJECT_STATE`, `PHASE_REGISTRY`, `meta/*` |
| read-only (→ contract-change) | `docs/contracts/{db_schema,agent_io_contract,output_schema}.md` · `ai_system/prompts/prompt_registry.md`(주입이 P-006 동작 바꾸면) |
| forbidden | `phases/archive/*` · commercial_viral · 영상 제작 |

## gated / behavior-preserving 원칙 (필수)

```
- 신원 없음(익명) → 기존 경로 그대로 (회귀 0).
- brand_memory/PKM 없음 → 프롬프트 byte-identical (주입 0).
- 주입 ON 은 (신원 有 + 메모리 有 + flag) 일 때만. 기존 pytest green 유지.
- 키/PII: brand_memory 주입은 RLS 격리 데이터만, .env 키 평문 0.
```
