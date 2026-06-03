# Contract Change Log — Phase 17 다-S3 pkm_entries (개인 PKM)

> ID: CC-022 | Status: **decided + applied** (2026-06-04) | Date: 2026-06-04
> Decision: 개인 PKM(`pkm_entries`, personal scope, auth_user_id 격리) **additive** 신규 테이블 등록 + RLS.
> 대상: `docs/contracts/db_schema.md` §6.2 (신규) · migration `0006_pkm_entries.sql`
> 근거: PKM/RAG orchestrator design `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md` §8.2 (사용자 검토필 설계) + 사용자 결정 "2(다-S3 개인 PKM)"
> 절차: contract-change (db_schema 직접 편집 금지 → 본 로그 + §6.2 additive 반영)

## 1. 변경 요약
| 대상 | 변경 |
|---|---|
| `db_schema.md` §6.2 | **신규** pkm_entries 정의(additive — 기존 §6 brand_memory_entries 본문 불변). User 계층 brand-독립 개인 메모리, auth_user_id 격리, RLS(auth.uid() OR NULL). |
| `0006_pkm_entries.sql` | 신규 마이그레이션(idempotent CREATE IF NOT EXISTS + RLS, 0001~0005 불변). |

## 2. 영향 받는 영역
- [x] DB 스키마 (신규 테이블, additive)
- [ ] API 응답 / agent_io / output_schema (불변 — 주입은 입력측 user_input prepend)
- [ ] prompt_registry (불변 — P-006 템플릿 무변경, 입력 augmentation gated)

## 3. 회귀 안전
- additive only: 기존 0001~0005 + brand_memory_entries(§6) 본문 0 변경.
- 코드 경로 gated: `personal_pkm_injection_enabled` default OFF → 주입 0, byte-identical.
- pytest 589→600(+11, 기존 0 수정). 마이그레이션은 미적용 가능(Supabase 미설정 시 PkmRepo in-memory graceful).

## 4. scope / governance
- 본 slice = personal scope **읽기(주입)** 경로만. 자동 쓰기 X (ADR-031 NG12 계승 — 적재는 추출 governance/운영자 경유, brand 와 동일 원칙).
- 우선순위: user_locked/personal > brand (design §6.2) — 주입 시 personal preamble 이 brand preamble 앞.
- full 스키마(brand_id/series_id/embedding/source_candidate_id) + series scope = 후속 additive(별도 migration).

## 5. Rollback
- `0006_pkm_entries.sql` 미적용 또는 DROP TABLE pkm_entries + db_schema §6.2 revert + `personal_pkm_injection_enabled` 제거. 코드 graceful(테이블 부재 시 in-memory/skip)이라 부분 rollback 안전.

## 6. 변경 이력
- 2026-06-04: Phase 17 다-S3 — pkm_entries additive 신규(CC-022) + 개인 PKM 주입(gated default OFF).
