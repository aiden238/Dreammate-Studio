# Phase 21 — Acceptance

```
A1. S1 repos — DomainRepo.list_for_brand + SeriesRepo.list_for_domain (graceful, RLS, in-memory fallback). [단위]
A2. S1 집계 — /me/pkm-graph 에 domain/series 노드 + has_domain/has_series 엣지 + 브랜드 PKM source 노드 +
    sourced_from 엣지(source_plan_id). summary +domains/series/sources. [단위: 시드 데이터]
A3. S1 graceful — domains/series 0 + source_plan_id 없음 → 기존 그래프(user/brand/pkm) 노드·엣지 불변(byte-identical). [단위]
A4. S1 스키마 — graph.py type +domain/series/source, kind +has_domain/has_series/sourced_from (literal 확장, additive). [단위]
A5. S2 frontend — PkmGraph domain/series/source 노드 스타일 + 레이아웃 + types.ts. rich 그래프 무변경. [typecheck/lint]
A6. behavior-preserving — 기존 pytest 691 green + scenario_sim 36/36 + audit 0. RLS 본인 격리.
A7. contract-change — api_contract §8.7 응답 스키마 확장(domain/series/source 노드·엣지) docs-sync(CC).
A8. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A2/A3/A4 | 단위 test(시드 4계층 집계 + source 엣지 + graceful empty + RLS + literal) |
| A5 | typecheck/lint + (선택) 라이브 /brain |
| A6 | pytest 691 baseline + scenario_sim 36 + audit 0 |
