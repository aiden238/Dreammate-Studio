# Phase 19 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- 제안서 검토본 확정(하이브리드 viz / /brain / 큐레이션 전부).
- Phase 17 repos(PkmRepo/BrandMemoryRepo/BrandRepo) + RLS 재사용 — 집계 source.
- **audit_naming 통과 (2026-06-04, 0 drift)**.
- gated/additive: 신규 /brain 라우트 + endpoint만, 기존 byte-identical.
- 모바일=카드/리스트(design.md 제약), 데스크톱=그래프(react-flow lazy-load).
### 1.2 불확실
- U1 react-flow 번들·모바일 영향 / U2 데이터 빈약 UX / U3 반응형 브레이크포인트 — S2/S3에서 확정.

## 2. Simplest Slice (3회 압축)
```
1차: API + 모바일 카드 + 데스크톱 그래프 + 큐레이션.
2차: GET /me/pkm-graph 집계 API(읽기) — 프론트 전.
3차: 인증 사용자 auth_user_id → PkmRepo+BrandMemoryRepo+brands 집계 → {nodes,edges} JSON 반환(RLS, 빈 데이터 graceful).
     ← S1 = API 단독(mock test).
```
→ S1(API) → S2(모바일 카드) → S3(데스크톱 그래프) → S4(큐레이션) → S5(엣지/4계층/e2e/close).

## 3. Surgical Scope
- editable: backend me/brain 라우터 + 집계 헬퍼(기존 repo 재사용) + CRUD + frontend /brain + components + api/types + package.json(react-flow) + tests + phase/state/meta.
- read-only(→contract-change/docs-sync): api_contract · page_map.
- forbidden: archive / 신규 PKM 데이터모델·migration / commercial_viral / 영상 제작.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: 단위 test(mock) — auth_user_id별 nodes/edges 집계 + RLS 격리(타 사용자 0) + 빈 데이터 graceful.
- 각 슬라이스: behavior-preserving(기존 pytest 641 green) + audit 0.
