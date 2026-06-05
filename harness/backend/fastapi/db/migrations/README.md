# DB Migrations — 적용 절차 (Phase 27 S4 / B-4 · M-1)

Supabase(Postgres) 운영 DB에 스키마/RPC를 반영하는 절차. **모든 마이그레이션은 멱등**
(`IF NOT EXISTS` / `CREATE OR REPLACE` / `DROP ... IF EXISTS`) → 재실행 안전.

> ★ Phase 27 범위 = 스크립트/절차 제공까지. 실제 운영 DB 적용은 ops(사용자 인프라).

## 마이그레이션 목록 (적용 순서)

| # | 파일 | 내용 |
|---|---|---|
| 1 | `0001_init.sql` | 4계층 코어 — brands / domains / series / video_projects / plans |
| 2 | `0002_phase_4_5_revise_history.sql` | Critic revise 이력 |
| 3 | `0003_rls_policy.sql` | RLS 정책 (사용자 격리) |
| 4 | `0004_rag_5stage.sql` | RAG candidate→approved 5단계 + pgvector |
| 5 | `0005_feedback_selection.sql` | feedback_events / selected_plans / brand_memory_entries |
| 6 | `0006_pkm_entries.sql` | 개인 PKM (pkm_entries) |
| 7 | `0007_personal_pkm_source.sql` | 개인 PKM 출처(source_plan_id) |
| 8 | `0008_match_approved_knowledge.sql` | **RAG retrieval RPC** `match_approved_knowledge` (B-4) |

> `001_init.sql`(3자리)는 legacy 중복 — 적용 스크립트가 자동 제외(4자리 prefix만).

## 적용 (택1)

### A. 스크립트 (psql 필요)

```bash
# 1) 적용 순서 확인 (오프라인)
python scripts/apply_migrations.py --list

# 2) DATABASE_URL 설정 (backend/fastapi/.env 또는 환경변수)
#    예: postgresql://postgres:<pw>@db.<ref>.supabase.co:5432/postgres
# 3) 순서대로 적용 (멱등 — 재실행 안전)
python scripts/apply_migrations.py --apply

# 4) 핵심 객체(RPC + 테이블) 검증
python scripts/apply_migrations.py --verify
```

### B. Supabase SQL Editor (psql 미설치 시)

대시보드 → SQL Editor 에서 `0001` → `0008` 을 **순서대로** 복붙 실행.

## 검증 기대 결과 (`--verify`)

```
rpc_match_approved_knowledge | t
table_plans                  | t
table_brands                 | t
table_pkm_entries            | t
table_brand_memory_entries   | t
```

## 운영 연결 — plan 영속 / PKM / RAG (B-3 · B-4)

이 마이그레이션이 적용되고 `backend/fastapi/.env` 에 `SUPABASE_*` 가 설정되어야 다음이 **실제 DB**에 기록/조회된다(미적용/미설정 시 graceful — 차단 0, 휘발):

- **plan 영속(B-3)**: `APP_PROFILE=realuse`(→ `plans_repo_enabled=True`) 면 생성된 plan 이
  `plans` 테이블(0001)에 upsert 영속 → 서버 재시작해도 유지. (코드: `orchestration/moa_orchestrator._persist_plan_envelope`, graceful. 테스트: `tests/test_plans_persistence.py`.)
- **PKM 축적/주입**: brand_memory_entries(0005)/pkm_entries(0006) — realuse 프로파일에서 ON.
- **RAG retrieval(B-4)**: `match_approved_knowledge` RPC(0008) 미정의 시 retrieval 이
  graceful-empty(동작 안 함) → 0008 적용 후 실제 검색.

> RLS 실 DB 검증(pgtap/수동)은 운영 단계(Gate B+) 후속.
