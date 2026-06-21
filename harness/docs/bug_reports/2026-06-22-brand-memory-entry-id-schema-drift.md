# Bug Report: brand_memory_entries `entry_id`/`id` 스키마-코드 불일치

- 발견일: 2026-06-22 (CODEX 독립 검토 → 본 세션 검증)
- 보고자: CODEX 검토 + 검증
- 분류: **DB (schema/code drift) + Auth/Permission (소유검증) + Frontend-facing (큐레이션)**
- 긴급도: **High** (사용자-facing 기능 전체 비동작, 다수 영향) — ★ 데이터 손상 없음(조용한 no-op/404)
- 상태: triaged → fixing → **fixed → verified** (2026-06-22, pytest 841 passed, 회귀 가드 3 추가)

## 수정 결과 (반영)
- `brand_memory_repo.py`: `_norm`(entry_id→id 미러) + `_identity` 추가. update/delete Supabase `.eq("entry_id", …)`(실 PK), in-memory `_identity` 매칭, add 는 entry_id 생성. list/add 반환에 id 보장 → me.py 무변경(경계 격리).
- `test_pkm_curation.py::_seed_brand`: 실 Supabase row(entry_id, no id) 모사로 정정 — 구 `["id"]` 주입(회귀 미검출 원인) 제거.
- `test_brand_memory_prep.py`: 회귀 가드 3(update/delete 가 entry_id 컬럼 쿼리 + list 가 id 미러). 구 코드면 실패.

## 재현 절차
환경: 실 Supabase (in-memory mock 아님)
입력: 인증 사용자가 /brain 에서 **브랜드 PKM** entry 편집/잠금/삭제(큐레이션)
기대: entry 갱신/삭제
실제: 404(미소유) 또는 조용한 no-op — 갱신/삭제 안 됨
빈도: 매번 (브랜드 PKM 한정. 개인 PKM 은 정상)

## 근본 원인
- `brand_memory_entries` PK = **`entry_id`** (`0005_feedback_selection.sql:62`) — `id` 컬럼 없음.
- 그러나 코드는 `id` 를 기대:
  - `routers/me.py:120` `_pkm_node` — `row.get("id")` (None → synthetic `entry_type:content` 노드 id).
  - `routers/me.py:507` `_brand_owns_entry` — `row.get("id") == raw_id` (None → 소유검증 항상 실패).
  - `db/repositories/brand_memory_repo.py:170,201` — `.eq("id", entry_id)` (존재 않는 컬럼 → 0행 매칭).
  - 동 repo in-memory `186,217,226` — `row.get("id")` (저장 행은 `entry_id`/키없음 → 미매칭).
- 깨진 체인(실 DB): list(entry_id) → 그래프 노드 id=가짜 → 프론트가 가짜 id 전송 → 소유검증/쿼리 미매칭 → 404/no-op.
- 대조: 개인 `pkm_entries` PK = `id` (`0006_pkm_entries.sql:31`), `pkm_repo.py` 는 `.eq("id")` 정합 → **정상**.

## 영향 범위
- 영향 기능: **브랜드 PKM 큐레이션(편집/잠금/삭제)** — 실 Supabase 에서 전체 비동작.
- 영향 사용자: 브랜드 PKM 을 가진 모든 인증 사용자.
- 데이터 손상: 없음(쓰기가 매칭 0이라 조용히 무동작).
- 개인 PKM: 영향 없음(정상).

## 왜 테스트가 못 잡았나
기존 테스트가 mock row 에 `id` 를 직접 주입 → 실 스키마(`entry_id`) 와 다름. live-schema 회귀 미검출.

## 수정 계획
- BrandMemoryRepo 를 **실 컬럼 `entry_id`** 에 정합 + 호출측 `id` 컨벤션 보존(read 시 `id`=`entry_id` 노출):
  - update/delete Supabase 쿼리 `.eq("entry_id", ...)`.
  - list/add/in-memory 반환 행에 `id`(=entry_id) 보장 → me.py 무변경(경계 격리).
  - in-memory add 는 entry_id 생성(식별 가능).
- ★ **회귀 테스트**: 실 스키마처럼 `entry_id`(no `id`) row 로 list→graph→소유검증→update/delete 라운드트립 검증.

## 후속
- 회귀 테스트 추가: 예 (live-schema 모사)
- contract 변경 필요: 아니오 (db_schema §6 = entry_id 가 이미 정답; 코드가 drift)
