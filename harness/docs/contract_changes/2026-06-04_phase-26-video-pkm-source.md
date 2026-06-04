# Contract Change Log — CC-033/034: video 노드 + 개인 PKM 출처 (Phase 26)

- 반영일: 2026-06-04
- 상태: approved → 반영 (Phase 26 빌드 승인, Phase 21/22/24 그래프·CRUD 패턴 동형 additive)

## CC-033 — api_contract §8.7 video (Phase 26 S1)
- **POST/PATCH/DELETE /me/videos**(소유검증 video→series→domain→brand→user 4-hop) + pkm-graph `video` 노드 + `has_video`(series→video) 엣지 + summary.videos. 4계층 마지막(Video). additive/graceful(video 0=불변).
- 정합: VideoProjectRepo(신규, SeriesRepo 패턴) + me.py CRUD/그래프 + schemas/graph.py(type/kind/summary + MeVideo*). legacy video_project.py(ADR-023) 무관.

## CC-034 — db_schema.md pkm_entries.source_plan_id (Phase 26 S2)
- pkm_entries 에 `source_plan_id uuid REFERENCES plans(id) ON DELETE SET NULL` 추가(migration 0007, idempotent ADD COLUMN IF NOT EXISTS + index). 개인 PKM 도 출처(plan) 추적 — brand_memory(0005)와 동형.
- 정합: 0007_personal_pkm_source.sql + PkmRepo.add_entry(+source_plan_id) + _run_personal_pkm_extract_hook(source_plan_id=plan_id) + me.py 개인 PKM sourced_from→source 엣지(Phase 21 재사용, graph.py 스키마 변경 0).

## Rollback
§8.7 video 라인 + GET enum 추가분 + db_schema source_plan_id + §24 CC-033/034 제거(additive). 코드 revert. video 0/출처 없음 → 그래프 byte-identical.

## 영향
- video: 테이블 0001 재사용(migration 0). pkm source: migration 0007 additive(실 적용=운영, NG11). 그래프 builder graceful. hermetic pytest 749→(S1 773)→(S2 +).
