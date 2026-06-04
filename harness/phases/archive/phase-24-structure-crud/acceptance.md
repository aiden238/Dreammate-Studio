# Phase 24 — Acceptance

```
[x] A1. S1 repos — DomainRepo/SeriesRepo update_name+delete (graceful, in-memory+Supabase). domain 삭제 → series cascade. [단위]
[x] A2. S1 endpoints — PATCH/DELETE /me/domains·/me/series. 소유검증(_owns_domain / _owns_series 3-hop). [단위]
[x] A3. S1 보안 — 익명 401 / 타인 404 / 빈 name 422. RLS. graceful(500 금지). [단위 21]
[x] A4. S1 반영 — rename → name 변경, delete → 미존재 → /me/pkm-graph 반영. [단위+라이브]
[x] A5. S2 frontend — /brain ✏️편집·🗑삭제 UI(cascade 경고) + api + refetch. 기존 무변경. [typecheck/lint+브라우저]
[x] A6. behavior-preserving — hermetic pytest 714→735 + scenario_sim 36/36 + audit 0.
[x] A7. ★ 라이브 데모 — rename 200/미소유 404/DELETE domain→series cascade + /brain ✏️🗑 렌더(end-to-end PASS).
[x] A8. contract-change — api_contract §8.7 PATCH/DELETE — CC-031.
[x] A9. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```
> 판정: 9/9 충족 + 라이브 데모 PASS. /brain 4계층 CRUD 완성(생성·큐레이션·편집·삭제). closing_notes.md.

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A4 | 단위 test(편집/삭제 + cascade + 소유검증 404 + RLS + anon) |
| A5 | typecheck/lint |
| A6 | pytest 714 baseline + scenario_sim 36 + audit 0 |
| A7 | 라이브 /brain 편집/삭제 |
