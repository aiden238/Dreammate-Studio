# Phase 22 — Acceptance

```
[x] A1. S1 repos — DomainRepo.create + SeriesRepo.create (Supabase insert / in-memory uuid4 / graceful). [단위]
[x] A2. S1 endpoints — POST /me/domains(brand 소유) + /me/series(domain→brand→user 2-hop). {ok,domain|series}. [단위]
[x] A3. S1 보안 — 익명 401 / 타인 brand·domain 404 / 빈 name 422 / repo 실패 503. RLS 격리. [단위 16]
[x] A4. S1 반영 — 생성 → list 반영 → /me/pkm-graph 4계층 노드(라이브 summary domains/series). [단위+라이브]
[x] A5. S2 frontend — /brain 지식 구조 UI(도메인/시리즈 추가) + api + refetch. 기존 /brain 무변경. [typecheck/lint+브라우저]
[x] A6. behavior-preserving — hermetic pytest 698→714 + scenario_sim 36/36 + audit 0.
[x] A7. ★ 라이브 데모 — 생성 API→4계층 그래프 반영→/brain 트리 렌더(end-to-end PASS, eval/.../phase-22-structure-live.md).
[x] A8. contract-change — api_contract §8.7 POST /me/domains·/me/series — CC-030.
[x] A9. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```
> 판정: 9/9 충족 + 라이브 데모 PASS. 데스크톱 그래프 domain/series 노드 시각만 이월(headless 한계). closing_notes.md.

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A4 | 단위 test(create + 소유검증 404 + RLS + anon + graph 반영) |
| A5 | typecheck/lint |
| A6 | pytest 698 baseline + scenario_sim 36 + audit 0 |
| A7 | 라이브 /brain 4계층 그래프 |
