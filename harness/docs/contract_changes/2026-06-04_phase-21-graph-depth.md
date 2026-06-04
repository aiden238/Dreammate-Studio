# Contract Change Log — CC-029: /me/pkm-graph 4계층 깊이 + 출처 엣지 (Phase 21)

- 반영일: 2026-06-04
- 제안서: `meta/proposals/2026-06-04_phase-21-graph-depth.md`
- 상태: approved → 반영 완료

## 반영 내용 (api_contract.md §8.7)
- nodes type +domain/series/source · edges kind +has_domain/has_series/sourced_from · summary +domains/series/sources(default 0).
- id namespace +domain:/series:/source:<plan_id>. §24 변경이력 CC-029 라인.

## 정합 확인 (docs↔code)
| 코드 | contract |
|---|---|
| routers/me.py 4계층+출처 집계 | §8.7 nodes/edges/summary ✅ |
| schemas/graph.py type/kind literal + summary | §8.7 ✅ |
| repositories/domain_repo·series_repo (graceful/RLS) | §8.7 graceful ✅ |
| apps/web PkmGraph + types.ts | §8.7 ✅ |

## Rollback
§8.7 확장 제거(additive). 코드 revert. graceful: domains/series/source 0 → 노드·엣지 불변.

## 한계
- 개인 pkm_entries 출처(source_plan_id 부재) 미포함 — 이월(migration 필요). 본 CC 는 브랜드 PKM 출처만.
