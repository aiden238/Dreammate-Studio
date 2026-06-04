# Phase 21 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- domains/series 테이블(0001) + brand_memory.source_plan_id(0005) 존재 — 집계 source (조사 완료).
- Phase 19 그래프 패턴(me.py 집계 + graph.py 스키마 + PkmGraph 렌더) 계승. additive/graceful.
- DomainRepo/SeriesRepo 는 BrandRepo 패턴(list + graceful + RLS + in-memory fallback)으로 신규.
- **audit_naming 통과 (2026-06-04, 0 drift)**.
### 1.2 불확실 / 한계
- U1 domains/series 실데이터 희소 → graceful empty(기존 그래프 불변). 풍부함은 실사용.
- U2 개인 PKM source_plan_id 부재 → 개인 출처 엣지 불가(이월, migration).
- U3 source 노드 라벨(plan_id uuid) 가독성 — "기획안 출처" 류 라벨 + dedup.

## 2. Simplest Slice (3회 압축)
```
1차: backend(repos+집계+스키마) + frontend(렌더) + CC + 라이브.
2차: backend 집계(domain/series/source 노드·엣지) + 스키마 + tests; 프론트는 S2.
3차: me.py 집계에 domain/series 노드(DomainRepo/SeriesRepo) + 브랜드 PKM source 노드·엣지 추가
     + graph.py type/kind literal 확장. graceful(데이터 0 = 기존 byte-identical). 단위 test.
     ← S1 = backend 집계 확장(mock/시드 단위 test).
```
→ S1(backend 집계+repos+스키마) → S2(frontend 렌더+CC+close).

## 3. Surgical Scope
- editable: db/repositories/{domain,series}_repo(신규) + routers/me.py + schemas/graph.py + apps/web(PkmGraph/types) + tests + phase/state/meta.
- read-only(→contract-change): api_contract.md §8.7.
- forbidden: 개인 PKM source migration / domains·series 생성 UI / video 노드 / archive / 신규 데이터모델.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: 4계층 시드(brand→domain→series)로 노드/엣지 집계 + 브랜드 PKM source_plan_id→source 노드/엣지 + ★ graceful(domains/series 0 → 기존 그래프 노드/엣지 불변) + RLS 격리 단위 test.
- 각 슬라이스: behavior-preserving(기존 pytest 691) + scenario_sim 36 + audit 0.
