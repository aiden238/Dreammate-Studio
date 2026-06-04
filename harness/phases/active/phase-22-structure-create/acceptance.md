# Phase 22 — Acceptance

```
A1. S1 repos — DomainRepo.create(brand_id,name) + SeriesRepo.create(domain_id,name) (Supabase insert / in-memory uuid4 / graceful). [단위]
A2. S1 endpoints — POST /me/domains(brand 소유검증) + POST /me/series(domain→brand→user 소유검증). 201/200 + {ok,domain|series}. [단위]
A3. S1 보안 — 익명 401 / 타인 brand·domain 404 / 빈 name 422. RLS 본인 격리. graceful(500 금지). [단위]
A4. S1 반영 — 생성 후 DomainRepo.list_for_brand / SeriesRepo.list_for_domain 에 나타남 → /me/pkm-graph 4계층 노드. [단위]
A5. S2 frontend — /brain 도메인/시리즈 추가 UI + api(createDomain/createSeries) + refetch. 기존 /brain 무변경. [typecheck/lint]
A6. behavior-preserving — 기존 pytest 698 green + scenario_sim 36/36 + audit 0.
A7. ★ 라이브 데모 — mock 백엔드 재기동 → brand→domain→series 생성 → /brain 그래프 4계층(domain/series 노드) 표시.
A8. contract-change — api_contract §8(POST /me/domains·/me/series) docs-sync(CC).
A9. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A4 | 단위 test(create + 소유검증 404 + RLS + anon + graph 반영) |
| A5 | typecheck/lint |
| A6 | pytest 698 baseline + scenario_sim 36 + audit 0 |
| A7 | 라이브 /brain 4계층 그래프 |
