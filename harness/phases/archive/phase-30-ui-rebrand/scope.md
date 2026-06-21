# Phase 30 — scope

## editable (Slice 순서대로)
- `apps/web/app/globals.css` · `apps/web/tailwind.config.ts` (Slice 1 — semantic 토큰 + legacy scale 재매핑 + 폰트)
- `apps/web/components/AppShell.tsx` (+ DesktopPrimaryRail / DesktopContextSidebar / MobileBottomNav) (Slice 2)
- `apps/web/app/page.tsx` (Slice 3) · `new/branding`·`new/discovery/**`·discovery 컴포넌트 (Slice 4)
- `apps/web/app/plan/[plan_id]/page.tsx` + wrapper(PlanOptionFrame/PlanComparisonGrid/BrandMemoryAside) (Slice 5)
- final-output presentation (Slice 6, 브리프 깊이만) · `app/brain/**`+PkmGraph 색 (Slice 7) · QA(Slice 8)
- 신규 presentation wrapper 컴포넌트
- **contract-change 경유만**: `apps/web/design_system/tokens.md`, `docs/contracts/frontend_design_contract.md`, `apps/web/design.md` Visual Style

## read-only / reference
- `apps/web/design_reference/**` (핸드오프 레퍼런스 — 시각 기준, 제품 코드 아님)

## forbidden
- `backend/**`, API/output_schema/DB, AI flow
- 새 route 생성(대시보드/레퍼런스보드 = **별도 승인 범위**)
- `components/PlanCard.tsx` 내부 재작성 (wrapper만)
- 새 UI 라이브러리 무단 추가 · 정적 HTML 그대로 이식 · 목업 데이터 하드코딩
