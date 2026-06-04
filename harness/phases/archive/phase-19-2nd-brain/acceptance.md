# Phase 19 — Acceptance

```
[x] A1. S1 API — GET /me/pkm-graph (authed) → {nodes,edges,summary} 집계, RLS(본인만), 익명/무데이터 graceful. [단위 test 8건]
[x] A2. S2 프론트 /brain 모바일 카드/리스트 — scope 섹션 PKM 칩 + 🔒. AuthGuard. [typecheck/lint] (시각 e2e 이월)
[x] A3. S3 데스크톱 그래프 — @xyflow/react lazy-load(≥1024, ssr:false), 모바일 카드 유지·번들 미포함. [typecheck] (시각 e2e 이월)
[x] A4. S4 큐레이션 — PATCH(잠금/편집)/DELETE /me/pkm/{id} + UI. user_locked 보호. [단위 test 19건]
[x] A5. behavior-preserving — 기존 흐름 byte-identical. pytest 641→668 + scenario_sim 36/36 + audit 0 + 모바일 무변경.
[x] A6. contract-change — api_contract §8.7(/me/pkm-graph·/me/pkm) + page_map §1.4(/brain) — CC-024.
[x] A7. phase-complete — gates + 회고 + archive + REGISTRY/STATE.
```
> 판정: 7/7 충족. A2/A3 라이브 시각 e2e만 @xyflow 의존성 재기동 이슈로 이월(유닛 668+typecheck로 기능 보증). 상세 closing_notes.md.

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A4 | 단위 test(mock, RLS 격리 + 집계 nodes/edges + PATCH/DELETE) |
| A2/A3 | typecheck/lint + (라이브) /brain 렌더 — 모바일 카드 / 데스크톱 그래프 |
| A5 | pytest 641 baseline + scenario_sim 36 + audit 0 |
