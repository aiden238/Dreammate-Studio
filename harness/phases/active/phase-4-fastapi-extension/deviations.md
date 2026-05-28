# Phase 4 — Deviations Log

> 조정 4번 (page_map.md / component_map.md / design_handoff.md 직접 수정 금지) 위반 시
> deviations.md 에만 기록한다. spec 파일 직접 수정은 contract-change 절차로 별도 진행.

---

## D-1 — `/plan/[plan_id]` dynamic route (Slice 3)

- **발견 일시**: 2026-05-28 (Slice 3 구현 중)
- **위치**: `apps/web/app/plan/[plan_id]/page.tsx` (NEW)
- **drift 형태**: `audit_page_component.ps1` 가 `actual only (spec 누락)` 검출
- **사유**:
  - Phase 4 scope.md §3 (Slice 3)는 `apps/web/app/plan/[plan_id]/page.tsx` 를 명시 산출물로 지정.
  - 한편 `apps/web/page_map.md` 는 `/plan` 단일 route 만 spec 화 (Phase 4에서 `PlanComparisonCard` 활성으로 표기).
  - Phase 4는 API 정합 (POST `/plans/{id}/generate` → GET `/plans/{id}`) 을 위해 dynamic route 가 자연스러우나, page_map.md 는 그 표현을 아직 반영하지 못함.
- **판정**: **intended drift** — scope.md ⊃ page_map.md. spec 갱신은 Slice 4 또는 다음 phase 에서 contract-change 로 처리.
- **임시 조치**:
  - `apps/web/app/plan/page.tsx` 에 query `?plan_id=xxx` 감지 시 `/plan/[plan_id]` redirect 추가 (Phase 1 동작 보존).
  - `audit_page_component.ps1` 의 dynamic-route 정규화 (`step/[n]` 패턴)와 동일하게 `/plan/[plan_id]` 도 가산 처리해야 0 drift 달성 가능.
- **권장 후속 조치**:
  - Slice 4: `audit_page_component.ps1` 에 `/plan/[plan_id]` 정규화 case 추가 (`step/[n]` 처리와 동일 패턴).
  - 또는 다음 phase: contract-change 로 `page_map.md` §1.2 에 `/plan/[plan_id]` route block 추가.

---

## 변경 이력

- 2026-05-28: Phase 4 Slice 3 — D-1 최초 기록.
