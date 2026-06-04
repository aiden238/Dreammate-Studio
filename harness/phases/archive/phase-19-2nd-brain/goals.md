# Phase 19 — 2nd Brain 시각화 (마이페이지 PKM 도식화) — Goals

> 유형: 제품 phase (런타임 有) — gated/additive(신규 /brain 라우트 + 읽기/CRUD endpoint).
> 근거: `meta/proposals/2026-06-04_2nd-brain-visualization-design.md` (검토 반영본).
> 선행: Phase 17(PKM 축적/주입) ✅ + Phase 18(brand_memory source) ✅ — 도식화할 데이터 존재.

## 한 줄 목표
사용자의 **개인 PKM + 브랜드 PKM + 4계층**을 `/brain`에서 보여주고(모바일 카드/리스트 + 데스크톱 그래프 하이브리드), **잠금/편집/삭제로 큐레이션**하게 한다. moat(쌓이는 데이터)를 사용자 자산으로 가시화.

## 사용자 결정 (2026-06-04, 검토)
- viz = **하이브리드**(모바일 카드/리스트 + 데스크톱 react-flow 그래프 lazy-load).
- 라우트 = **신규 `/brain`** (AuthGuard, AppShell 네비).
- 큐레이션 = **잠금(user_locked)/편집/삭제 전부** v1.
- ★ design.md 모바일 우선(원칙#10, "트리 아닌 breadcrumb") → 모바일은 그래프 대신 카드/리스트.

## 산출물
1. `GET /api/v1/me/pkm-graph` 집계 API (개인 pkm_entries + brand_memory + brands/series, RLS) — nodes/edges.
2. `/brain` 프론트 — 모바일 카드/리스트(scope 섹션) + 데스크톱 그래프(react-flow lazy-load).
3. 큐레이션 — PATCH/DELETE endpoint(기존 PkmRepo/BrandMemoryRepo 재사용) + UI(잠금/편집/삭제).
4. (S5) 출처 엣지(feedback→PKM) + 4계층 깊이 + e2e + phase-complete.

## ★ 루프 완성
발굴(Phase 18)→축적(brand_memory)→주입(Phase 17)→**가시화(Phase 19)**. 사용자가 자기 2nd brain이 자라는 걸 보고 소유.
