# Phase 21 — Acceptance

```
[x] A1. S1 repos — DomainRepo.list_for_brand + SeriesRepo.list_for_domain (graceful, RLS, in-memory). [단위]
[x] A2. S1 집계 — /me/pkm-graph domain/series 노드 + has_domain/has_series 엣지 + 브랜드 PKM source 노드 + sourced_from(dedup). summary +domains/series/sources. [단위]
[x] A3. S1 graceful — domains/series 0 + source 없음 → 기존 그래프(user/brand/pkm) 노드·엣지 불변. [단위]
[x] A4. S1 스키마 — graph.py type +domain/series/source, kind +has_domain/has_series/sourced_from. [단위]
[x] A5. S2 frontend — PkmGraph domain/series/source 스타일+레이아웃 + types.ts. 기존 그래프 무변경. [typecheck/lint] (시각 e2e 이월)
[x] A6. behavior-preserving — hermetic pytest 691→698 + scenario_sim 36/36 + audit 0. RLS 격리.
[x] A7. contract-change — api_contract §8.7 확장 — CC-029.
[x] A8. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```
> 판정: 8/8 충족. A5 프론트 시각 e2e만 이월(typecheck+backend 집계로 기능 보증). 개인 PKM 출처는 source_plan_id 부재로 이월(migration). 상세 closing_notes.md.

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A2/A3/A4 | 단위 test(시드 4계층 집계 + source 엣지 + graceful empty + RLS + literal) |
| A5 | typecheck/lint + (선택) 라이브 /brain |
| A6 | pytest 691 baseline + scenario_sim 36 + audit 0 |
