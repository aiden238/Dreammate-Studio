# Phase 26 — Acceptance

```
A1. S1 VideoProjectRepo — list_for_series/create/get_or_create/update_title/delete (graceful, in-memory+Supabase). [단위]
A2. S1 /me/videos CRUD — POST/PATCH/DELETE + 소유검증(video→series→domain→brand→user 4-hop). 401/404/422. [단위]
A3. S1 그래프 video — me.py series→video(has_video) 노드 + summary.videos + graph.py type/kind. graceful(video 0=불변). [단위]
A4. S2 migration 0007 — pkm_entries +source_plan_id(ADD COLUMN IF NOT EXISTS + index). idempotent. db_schema CC.
A5. S2 PkmRepo + 추출 훅 — add_entry +source_plan_id, _run_personal_pkm_extract_hook 가 source_plan_id=plan_id 기록. gated. [단위]
A6. S2 그래프 개인 출처 — me.py 개인 PKM source_plan_id→source 노드+sourced_from(브랜드 로직 재사용, dedup 공유). [단위]
A7. behavior-preserving — 기존 pytest 749 green + scenario_sim 36/36 + audit 0. video 0/출처 없음 → 기존 그래프 byte-identical.
A8. S3 frontend — /brain series 하위 video CRUD UI + api + types. [typecheck/lint]
A9. ★ 라이브 데모 — video 생성/편집/삭제 + 그래프 has_video + (피드백→추출→)개인 PKM 출처 엣지.
A10. contract-change — api_contract(/me/videos) + db_schema(pkm source_plan_id) docs-sync(CC).
A11. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A3/A5/A6 | 단위 test(video CRUD+소유검증+그래프 / pkm source 기록+그래프 엣지) |
| A4 | 0007 파일 idempotent + db_schema CC |
| A7 | pytest 749 baseline + scenario_sim 36 + audit 0 |
| A9 | 라이브 video CRUD + 개인 출처 |
