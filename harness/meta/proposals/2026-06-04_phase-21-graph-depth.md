# Contract Change Proposal: /me/pkm-graph 4계층 깊이 + 출처 엣지 (Phase 21)

- 제안일: 2026-06-04
- 제안자: Claude (Phase 21 S2)
- 대상 contract: docs/contracts/api_contract.md §8.7
- 변경 종류: 신규 (additive, graceful)
- 긴급도: 보통
- CC: **CC-029**

## 변경 사유
Phase 21에서 `/brain` 그래프를 4계층 깊이(domain/series) + 브랜드 PKM 출처(source)로 확장. me.py 집계 + graph.py 스키마가 추가한 노드/엣지 타입을 contract 동기화. Phase 19(CC-024) 패턴 계승.

## 변경 내용 (§8.7 GET /me/pkm-graph)
- nodes type: +`domain`/`series`/`source` (기존 user/brand/pkm).
- edges kind: +`has_domain`(brand→domain) / `has_series`(domain→series) / `sourced_from`(brand pkm bm→source).
- summary: +`domains`/`series`/`sources` (additive, default 0).
- id namespace: +`domain:<id>` / `series:<id>` / `source:<plan_id>`.

## 영향 받는 영역
- [x] API 응답 형식 (§8.7 nodes/edges/summary 확장 — additive)
- [x] 프론트 컴포넌트 (/brain PkmGraph 렌더 + types)
- [ ] DB(재사용 domains/series 0001 + brand_memory.source_plan_id 0005, 신규 migration 0) / Agent IO / Prompt 무관
- [x] 보안 (RLS 본인 격리 — DomainRepo/SeriesRepo graceful)

## 영향 받는 파일
```
docs/contracts/api_contract.md §8.7 + §24
구현(기반): backend/fastapi/routers/me.py + schemas/graph.py + repositories/{domain,series}_repo.py
프론트: apps/web/components/brain/PkmGraph.tsx + lib/types.ts
```

## Rollback
§8.7 확장 텍스트 제거(additive). 코드 revert. ★ graceful: domains/series/source 0 → 기존 그래프 노드·엣지 불변(summary 0키만 additive).

## 마이그레이션
- 불필요 (기존 테이블 재사용, 읽기 집계).
- ★ 한계: 개인 pkm_entries 출처는 source_plan_id 컬럼 부재 → 미포함(향후 migration = 이월).

## 승인 기준
Phase 19(CC-024)와 동형 additive/graceful 그래프 확장 — Phase 21 빌드("다 → 4계층")에 포함. 코드 hermetic pytest 698 검증 완료된 사후 docs-sync.

## 결정
- [x] 승인 (Phase 21 S2 docs-sync)
- 결정일: 2026-06-04
