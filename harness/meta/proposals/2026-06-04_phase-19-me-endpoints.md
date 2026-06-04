# Contract Change Proposal: /me PKM 그래프·큐레이션 endpoint (Phase 19)

- 제안일: 2026-06-04
- 제안자: Claude (Phase 19 close)
- 대상 contract: docs/contracts/api_contract.md (+ apps/web/page_map.md docs-sync)
- 변경 종류: 신규 (additive)
- 긴급도: 보통
- CC: **CC-024**

## 변경 사유
Phase 19(2nd brain 시각화)에서 마이페이지 `/brain`이 소비하는 신규 endpoint 3종이 구현됨 — api_contract에 명세 누락. 코드가 진실, contract 동기화 필요. 모두 인증 사용자 본인 데이터(RLS), additive (기존 endpoint 무변경).

## 변경 내용 (After — §8.7 신설)

### POST/GET 요약
- **GET /api/v1/me/pkm-graph** (authed) → `{nodes:[{id,type:user|brand|pkm,label,scope?,entry_type?,locked?}], edges:[{source,target,kind:owns|has_personal|has_brand_pkm}], summary:{personal,brand,brands}}`. 개인 pkm_entries + 소유 brands + 브랜드 brand_memory 집계. id namespace: `user:`/`brand:<id>`/`pkm:<id>`(개인)/`bm:<id>`(브랜드). RLS 본인만, 익명/무데이터 → 빈 그래프(graceful, 500 금지).
- **PATCH /api/v1/me/pkm/{node_id}** (authed) — body `{content?, locked?}` → `{ok, node:{...}}`. node_id prefix 라우팅: `pkm:`→pkm_entries(개인), `bm:`→brand_memory(브랜드 소유 검증). 401 익명 / 404 미소유·부재 / 500 금지.
- **DELETE /api/v1/me/pkm/{node_id}** (authed) → `{ok, deleted:true}`. 동일 prefix 라우팅 + 소유 검증. 401/404 동상.

## 영향 받는 영역
- [x] API 응답 형식 (신규 §8.7)
- [ ] DB 스키마 (재사용 — pkm_entries/brand_memory_entries, 신규 0)
- [x] 프론트 컴포넌트 (/brain, page_map docs-sync)
- [ ] Agent IO / Output Schema / Prompt / RAG (무관)
- [x] 보안 / 권한 (RLS 본인 격리 + 소유 검증, service key backend-only)

## 영향 받는 파일 목록
```
docs/contracts/api_contract.md (§8.7 신설, §24 변경이력)
apps/web/page_map.md (/brain route 등록 + 변경이력)
구현(기참조): backend/fastapi/routers/me.py, schemas/graph.py, repositories/{pkm_repo,brand_memory_repo}.py
프론트(기참조): apps/web/app/brain/page.tsx, components/brain/PkmGraph.tsx
```

## Rollback 방안
§8.7 + page_map 항목 제거로 즉시 복원 (문서 only, additive). 코드 endpoint는 Phase 19 커밋 revert.

## 마이그레이션 필요 여부
- [ ] DB 마이그레이션 / 데이터 변환 / 통지 — 전부 불필요 (기존 테이블 재사용, 신규 읽기+큐레이션).

## 승인 기준
self-approved 범위 초과(신규 endpoint 3종) → 단, 코드가 이미 구현·테스트(pytest 668)된 사후 docs-sync이며 additive·읽기/본인-큐레이션 한정. Phase 19 빌드 승인("빌드")에 포함된 것으로 간주, 본 CC는 문서 정합화.

## 결정
- [x] 승인 (Phase 19 빌드 일부, docs-sync)
- 결정자: 사용자(빌드 승인) / Claude(반영)
- 결정일: 2026-06-04
