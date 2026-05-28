# Phase 3 — Non-Goals

> 명시적으로 **하지 않을 것**. scope creep 방지.

---

## Phase 2 spec 영역 (read-only 절대 보장)

- [ ] `apps/web/design.md` 수정
- [ ] `apps/web/page_map.md` 수정
- [ ] **`apps/web/component_map.md` 수정 (조정 4번 — read-only 절대)**
- [ ] `apps/web/design_handoff.md` 수정
- [ ] `apps/web/design_system/*` 수정
- [ ] `apps/web/discovery_flow.md`, `quick_flow.md`, `mode_branching.md`, `direction_approval.md` 수정
- [ ] `apps/web/wireframes/*` 수정

**deviation 발견 시 처리** (조정 4번 핵심):
- Phase 2 spec과 실 코드 차이 발견 → deviation_log에 기록 (NEW: `phases/active/phase-3-pwa-impl/deviations.md`)
- 또는 `meta/proposals/2026-05-28_*.md` 제안서 작성
- component_map / design_handoff 직접 수정 0건 강제

---

## 4-layer 범위

- [ ] 모든 컴포넌트 4-layer 전체 구현
   → 4-layer 컴포넌트 4개 + chosen variant만
- [ ] 모든 variants 구현
   → chosen만 구현, alt는 `variant` prop 분기 + TODO 주석
- [ ] PlanCard 4-layer 회고 정합 (D3)
   → **조정 3번: Phase 4 이관**

---

## API 영역 (Phase 4 영역)

- [ ] backend/fastapi/ 수정
- [ ] api_contract.md 수정 (contract-change 절차 필수)
- [ ] multi-step wizard endpoint 구현 (Phase 4)
- [ ] 3-plan 동시 생성 (Phase 4)
- [ ] SSE / WebSocket (Phase 4)
- [ ] PlanComparisonCard 상세 spec (Phase 4)

---

## Auth / Feedback (Phase 5 / 9)

- [ ] 로그인 / 회원가입 UI
- [ ] Supabase Auth 통합 (Phase 5)
- [ ] choice_logs UI (Phase 9)
- [ ] Brand Memory UI (Phase 9)

---

## 다국어 / 접근성 본격 (Phase 11+)

- [ ] i18n 시스템
- [ ] WCAG 2.1 AA 완전 준수
- [ ] RTL 언어 지원
- [ ] 스크린 리더 본격 테스트

---

## 자동화 도구 (Phase 3 외)

- [ ] Playwright e2e 테스트 (Phase 4+)
- [ ] Lighthouse PWA score (Phase 10+)
- [ ] CI/CD 파이프라인 (Phase 10)
- [ ] Storybook (Phase 11+ 선택)

---

## Backend / contracts

- [ ] backend/fastapi/ 코드 수정
- [ ] docs/contracts/ 수정 (contract-change 절차 필수)
- [ ] ai_system/, knowledge/, product/ 수정

---

## Phase 4 이관 항목 (deferred)

| ID | 항목 | 이관 Phase |
|---|---|---|
| D2 | QuickInputCard alt variants | Phase 4 (실 사용 후 alt 결정) |
| D3 | PlanCard 4-layer 정합 | **Phase 4 (조정 3번)** |
| D4 | PlanComparisonCard 상세 spec | Phase 4 (3-plan 활성화 시) |

---

## 경계 위반 판단 기준

요청이 위 목록에 있으면:
1. **즉시 거절** — "Phase 3 non-goals"
2. **Phase 매핑** — Phase 4 / 5 / 9 / 11+ 어디로 이관
3. **예외 검토** — `meta/proposals/` 제안 + contract-change Skill

### 특별 강조 (조정 4번)

**component_map.md 수정은 어떤 사유로도 금지**.
- spec vs 코드 drift 발견 → `phases/active/phase-3-pwa-impl/deviations.md`에 기록만
- 변경 필요 → `meta/proposals/` 제안 + 사용자 승인 + Phase 4 적용
