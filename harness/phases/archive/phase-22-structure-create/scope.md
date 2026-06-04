# Phase 22 — Scope

## 포함 (build)
- **S1 backend**:
  - `DomainRepo.create(brand_id, name)` + `SeriesRepo.create(domain_id, name)` (BrandRepo insert 패턴 — Supabase insert→id / in-memory uuid4 / graceful).
  - `POST /api/v1/me/domains` (body `{brand_id, name}`) → `{ok, domain:{id,brand_id,name}}`. 소유검증: brand 가 본인 소유(BrandRepo.list_for_user).
  - `POST /api/v1/me/series` (body `{domain_id, name}`) → `{ok, series:{id,domain_id,name}}`. 소유검증: domain 이 본인 brand 하위(DomainRepo across user brands).
  - 401 익명 / 404 미소유 / 422 빈 name / graceful(500 금지).
  - schemas: 요청/응답 모델. 단위 test(생성+소유검증 404+RLS+anon 401).
- **S2 frontend**:
  - `/brain` 에 도메인/시리즈 추가 affordance (brand 카드 하위 "+ 도메인", domain 하위 "+ 시리즈") + api.ts(createDomain/createSeries) + refetch.
  - ★ **라이브 데모**: mock 백엔드 재기동 → brand→domain→series 생성(UI 또는 API) → /brain 그래프 4계층 표시 확인.
  - CC(api_contract §8.x) + phase-complete.

## 예상 파일 변경
```
editable:
  backend/fastapi/db/repositories/{domain_repo,series_repo}.py (create 추가)
  backend/fastapi/routers/me.py (POST endpoints + 소유검증 헬퍼)
  backend/fastapi/schemas/graph.py 또는 신규 schemas (요청/응답)
  apps/web/app/brain/page.tsx + lib/api.ts + lib/types.ts (추가 UI)
  tests/ + phase/state/meta
read-only(→contract-change):
  docs/contracts/api_contract.md §8 (POST /me/domains·/me/series)
forbidden:
  domains/series migration(테이블 존재) / video_projects 생성(범위 밖) / 신규 데이터모델 / archive
```

## 검증
- behavior-preserving: 기존 /me/pkm-graph(읽기) + 큐레이션 무변경. 기존 pytest 698 green + scenario_sim 36 + audit 0.
- S1: 생성 → DomainRepo/SeriesRepo list 반영 + 소유검증(타 brand/domain 404) + RLS + anon 401 단위 test.
- S2: typecheck/lint + ★ **라이브** /brain 4계층 그래프(domain/series 노드 표시).
