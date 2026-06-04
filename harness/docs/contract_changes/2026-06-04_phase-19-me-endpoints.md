# Contract Change Log — CC-024: /me PKM 그래프·큐레이션 endpoint (Phase 19)

- 반영일: 2026-06-04
- 제안서: `meta/proposals/2026-06-04_phase-19-me-endpoints.md`
- 상태: approved → 반영 완료

## 반영 내용
- `docs/contracts/api_contract.md` §8.7 신설 — 마이페이지 2nd brain endpoint 3종:
  - `GET /api/v1/me/pkm-graph` (집계 그래프, authed, graceful)
  - `PATCH /api/v1/me/pkm/{node_id}` (content/locked, prefix 라우팅 pkm:/bm:, 소유 검증)
  - `DELETE /api/v1/me/pkm/{node_id}` (동일 라우팅·검증)
- `docs/contracts/api_contract.md` §24 변경 이력 — CC-023(누락 백필) + CC-024 라인 추가.
- `apps/web/page_map.md` §1.3 `/new/branding`(CC-023 백필) + §1.4 `/brain`(CC-024) active route 등록 + §8 변경 이력.

## 정합 확인 (docs-sync)
| 코드 | contract |
|---|---|
| `backend/fastapi/routers/me.py` (GET pkm-graph / PATCH·DELETE pkm) | api_contract §8.7 ✅ |
| `backend/fastapi/schemas/graph.py` | §8.7 응답 형상 ✅ |
| `apps/web/app/brain/page.tsx` + `components/brain/PkmGraph.tsx` | page_map §1.4 ✅ |

## Rollback
§8.7 + page_map §1.4 제거(문서 only). additive — 기존 endpoint/route 무영향.

## 영향
- DB 마이그레이션/데이터 변환/통지: 불필요 (pkm_entries/brand_memory_entries 재사용).
- 보안: RLS 본인 격리 + PATCH/DELETE 소유 검증, service key backend-only.
