# Phase 24 — Acceptance

```
A1. S1 repos — DomainRepo/SeriesRepo update_name + delete (graceful, in-memory + Supabase). domain 삭제 시 하위 series cascade(in-memory 명시 / Supabase FK). [단위]
A2. S1 endpoints — PATCH/DELETE /me/domains/{id} + /me/series/{id}. 소유검증(domain→brand→user / series→domain→brand→user). [단위]
A3. S1 보안 — 익명 401 / 타인 domain·series 404 / 빈 name 422. RLS 격리. graceful(500 금지). [단위]
A4. S1 반영 — 편집 후 list_for_* name 변경, 삭제 후 미존재 → /me/pkm-graph 반영. [단위]
A5. S2 frontend — /brain 구조 섹션 domain/series ✏️편집·🗑삭제 UI + api + refetch. 기존 무변경. [typecheck/lint]
A6. behavior-preserving — 기존 pytest 714 green + scenario_sim 36/36 + audit 0.
A7. ★ 라이브 데모 — /brain 에서 domain 편집·삭제(하위 series 함께) + series 편집·삭제 → 트리/그래프 반영.
A8. contract-change — api_contract §8.7(PATCH/DELETE /me/domains·/me/series) docs-sync(CC).
A9. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A4 | 단위 test(편집/삭제 + cascade + 소유검증 404 + RLS + anon) |
| A5 | typecheck/lint |
| A6 | pytest 714 baseline + scenario_sim 36 + audit 0 |
| A7 | 라이브 /brain 편집/삭제 |
