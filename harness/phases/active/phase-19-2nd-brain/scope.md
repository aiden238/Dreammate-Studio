# Phase 19 — Scope

## 포함 (in-scope)
- **S1**: `GET /api/v1/me/pkm-graph` — 인증 사용자(auth_user_id)의 pkm_entries(personal) + brand_memory_entries(소유 brands) + brands/series(4계층)를 **nodes/edges** 구조로 집계(RLS 격리). 신규 테이블 0(읽기). 스키마(node: id/type/label/scope/locked, edge: source/target/kind).
- **S2**: 프론트 `/brain` — 모바일 **카드/리스트**(scope 섹션: 개인/브랜드/시리즈, PKM 칩 + 🔒). 반응형 base. AppShell 네비 진입 + AuthGuard.
- **S3**: 데스크톱 **react-flow 그래프**(`next/dynamic` ssr:false lazy-load, ≥데스크톱 브레이크포인트만; 모바일은 S2 카드 유지 → 번들 영향 0).
- **S4**: 큐레이션 — `PATCH /me/pkm/{id}`(잠금 토글/편집) + `DELETE /me/pkm/{id}`(기존 PkmRepo/BrandMemoryRepo CRUD 재사용) + UI.
- **S5**: 출처 엣지(feedback→PKM 파생) + 4계층 깊이 + 라이브 e2e + phase-complete.

## 예상 파일 변경
| 분류 | 경로 |
|---|---|
| editable | `backend/fastapi/routers/`(신규 me/brain 라우터 or plans 확장: pkm-graph/pkm CRUD) · `db/repositories/`(read 집계 헬퍼, 기존 repo 재사용) · `apps/web/app/brain/`(신규) · `apps/web/components/`(graph/card) · `apps/web/lib/api.ts`+types · `package.json`(react-flow) · tests · phase/state/meta |
| read-only(→contract-change) | `docs/contracts/api_contract.md`(신규 endpoint) · `apps/web/page_map.md`(/brain) |
| forbidden | `phases/archive/*` · 신규 PKM 데이터모델/migration · commercial_viral · 영상 제작 |

## gated/additive 원칙
- 신규 라우트/endpoint/page **추가만** — 기존 흐름 byte-identical.
- RLS: 본인 auth_user_id/brand_id만(Phase 5/17 격리). 교차 노출 0.
- react-flow = 데스크톱 lazy-load(모바일 미로드).
- 큐레이션 삭제 = user_locked 보호 + 확인. PKM governance(≥0.9 추출) 유지.
