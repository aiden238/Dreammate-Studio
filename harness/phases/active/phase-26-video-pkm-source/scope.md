# Phase 26 — Scope

## 포함 (build)
- **S1 video backend**:
  - `VideoProjectRepo`(신규, SeriesRepo 패턴): list_for_series / create / get_or_create / update_title / delete (graceful, in-memory + Supabase).
  - `/me/videos` CRUD: POST(body {series_id, title}) / PATCH {title} / DELETE — 소유검증(_owns_video = video→series→domain→brand→user 4-hop).
  - me.py 그래프: series→video 노드(`has_video`) + summary.videos.
  - graph.py: type +`video`, kind +`has_video`, summary +`videos`. tests.
- **S2 개인 PKM 출처**:
  - migration `0007_personal_pkm_source.sql`: `ALTER TABLE pkm_entries ADD COLUMN IF NOT EXISTS source_plan_id uuid REFERENCES plans(id) ON DELETE SET NULL` + index. (idempotent)
  - PkmRepo.add_entry +`source_plan_id` 인자(BrandMemoryRepo 패턴) — in-memory row 에도 포함.
  - `_run_personal_pkm_extract_hook`(plans.py:446)에서 add_entry(..., source_plan_id=plan_id).
  - me.py 그래프: 개인 PKM(pkm:) 루프에 source_plan_id→source 노드+`sourced_from`(브랜드 PKM 로직 재사용, source_ids dedup 공유).
  - db_schema.md CC(pkm_entries source_plan_id). tests.
- **S3 frontend + close**:
  - /brain 구조 섹션: series 하위 video 표시 + 생성/편집/삭제(domain/series UI 확장). api(createVideo/update/delete) + types.
  - ★ 라이브 데모(video CRUD + 개인 PKM 출처 엣지) + api_contract CC(/me/videos) + phase-complete.

## 예상 파일 변경
```
editable:
  backend/fastapi/db/repositories/video_repo.py (신규) + pkm_repo.py(source_plan_id)
  backend/fastapi/db/migrations/0007_personal_pkm_source.sql (신규)
  backend/fastapi/routers/me.py (video CRUD + 그래프 video/개인 source) + plans.py(추출 훅 source)
  backend/fastapi/schemas/graph.py (video type/kind/summary)
  apps/web/* (video CRUD UI)
  tests/ + phase/state/meta
read-only(→contract-change): docs/contracts/{api_contract,db_schema}.md
forbidden: legacy video_project.py 재활성(ADR-023) / 신규 데이터모델(테이블 존재) / archive
```

## 검증
- behavior-preserving: video 0 + 출처 없음 → 기존 그래프 byte-identical. 기존 pytest 749 green + scenario_sim 36 + audit 0.
- S1: video CRUD + 소유검증 + 그래프 has_video + graceful empty.
- S2: 추출 훅 source_plan_id 기록 + 그래프 개인 source 엣지 + migration idempotent + gated.
- S3: ★ 라이브 — video 생성/그래프 + 개인 PKM 출처 표시.
