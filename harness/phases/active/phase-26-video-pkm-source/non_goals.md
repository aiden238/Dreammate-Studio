# Phase 26 — Non-Goals

```
- legacy video_project.py(insert_video_project, ADR-023 deprecated) 재활성 금지 — 신규 VideoProjectRepo 별도.
- video 자동 생성(generate→video 자동 연결) 미포함 — 본 phase 는 /brain 수동 CRUD + 그래프. (generate↔video 자동은 후속.)
- pkm_entries 신규 데이터모델/embedding/series-scope 미포함 — source_plan_id 컬럼 1개만(0007).
- 기존 개인 PKM 추출 로직(extract_brand_memory_candidates) 변경 금지 — add_entry 에 source_plan_id 전달만.
- 브랜드 PKM 출처(Phase 21)·domain/series CRUD(Phase 22/24) 변경 금지 — 재사용만.
- migration 적용(Supabase push)은 운영 단계(NG11) — 본 phase 는 0007 파일 작성 + in-memory/contract. 실 적용은 사용자.
- 가중치/산식 변경 금지.
```
