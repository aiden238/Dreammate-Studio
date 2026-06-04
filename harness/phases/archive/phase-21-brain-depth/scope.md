# Phase 21 — Scope

## 포함 (build)
- **S1 backend**:
  - `DomainRepo.list_for_brand(brand_id)` + `SeriesRepo.list_for_domain(domain_id)` 신규 (BrandRepo 패턴 — graceful, RLS, in-memory fallback).
  - `me.py /me/pkm-graph` 확장: brand→domain(`has_domain`)→series(`has_series`) 노드/엣지 + 브랜드 PKM 출처(source_plan_id)→`source` 노드 + `sourced_from` 엣지. graceful(데이터 0 = 기존과 동일).
  - `schemas/graph.py`: PkmGraphNode.type +`domain`/`series`/`source`, PkmGraphEdge.kind +`has_domain`/`has_series`/`sourced_from`. summary +domains/series/sources.
  - 단위 test: 4계층 집계 + 출처 엣지 + graceful empty(기존 그래프 불변) + RLS.
- **S2 frontend**: PkmGraph 노드 스타일(domain/series/source 타입) + 레이아웃 좌표 확장 + types.ts. CC(api_contract §8.7) + 라이브(선택) + phase-complete.

## 예상 파일 변경
```
editable:
  backend/fastapi/db/repositories/{domain_repo,series_repo}.py (신규)
  backend/fastapi/routers/me.py (집계 확장)
  backend/fastapi/schemas/graph.py (type/kind literal +)
  apps/web/components/brain/PkmGraph.tsx + lib/types.ts (렌더)
  tests/ + phase/state/meta
read-only(→contract-change):
  docs/contracts/api_contract.md §8.7 (응답 스키마 확장)
forbidden:
  개인 PKM source_plan_id migration(이월) / domains·series 생성 UI(범위 밖) / 신규 데이터모델 / archive
```

## 검증
- behavior-preserving: 데이터 없는 사용자(domains/series 0)는 기존 그래프와 **동일**(노드/엣지 불변). 기존 pytest 691 green + scenario_sim 36 + audit 0.
- S1: 4계층 시드 데이터로 domain/series/source 노드·엣지 집계 + graceful(빈 데이터) + RLS 격리 단위 test.
- S2: typecheck/lint + (선택) 라이브 /brain 렌더.
