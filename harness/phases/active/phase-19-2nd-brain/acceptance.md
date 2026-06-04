# Phase 19 — Acceptance

```
A1. S1 API — GET /me/pkm-graph (authed) → {nodes:[{id,type,label,scope,locked}], edges:[{source,target,kind}]}
    개인 pkm_entries + brand_memory + brands/series 집계, RLS(본인만). 익명/무데이터 → 빈 그래프 graceful. [단위 test mock]
A2. S2 프론트 /brain 모바일 카드/리스트 — scope 섹션(개인/브랜드/시리즈) PKM 칩 + 🔒. AuthGuard. [build/typecheck + 수동]
A3. S3 데스크톱 그래프 — react-flow lazy-load(≥데스크톱), 모바일은 카드 유지. 번들 모바일 영향 0(미로드). [build]
A4. S4 큐레이션 — PATCH(잠금/편집)/DELETE /me/pkm/{id} + UI. user_locked 보호. [단위 test + 라이브 1건]
A5. behavior-preserving — 기존 흐름 byte-identical. 기존 pytest 641 green + scenario_sim + audit 0.
A6. contract-change — api_contract(/me/pkm-graph·/me/pkm) + page_map(/brain) docs-sync(CC).
A7. phase-complete — gates + 회고 + archive + REGISTRY/STATE.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A4 | 단위 test(mock, RLS 격리 + 집계 nodes/edges + PATCH/DELETE) |
| A2/A3 | typecheck/lint + (라이브) /brain 렌더 — 모바일 카드 / 데스크톱 그래프 |
| A5 | pytest 641 baseline + scenario_sim 36 + audit 0 |
