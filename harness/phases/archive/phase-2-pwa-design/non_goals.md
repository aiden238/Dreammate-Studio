# Phase 2 — Non-Goals

> 명시적으로 **하지 않을 것**. scope creep 방지.

---

## Phase 2에서 하지 않을 것

### 구현 영역 (Phase 3 영역)

- [ ] Next.js `*.tsx` 컴포넌트 코드 작성
- [ ] TypeScript interface 실 코드 (lib/types.ts 갱신은 Phase 3)
- [ ] CSS / Tailwind 클래스 실 작성
- [ ] Storybook / 컴포넌트 단위 테스트
- [ ] Playwright e2e 테스트

### 4-Layer 적용 범위 (의도된 minimal 정책)

- [ ] 4-layer를 **모든** 컴포넌트에 적용
   → 핵심 4개만: BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard
- [ ] Discovery Step 2~7 각각의 wireframe 상세 작성
   → Step 1 template + Step 2~7 4줄 명세 (P-XXX 매핑 + 차이점)
- [ ] PlanCard 4-layer 재정의
   → Phase 1 PlanCard 기존 활용 (Phase 3 진입 시 회고 정합)
- [ ] ResultSummaryCard 별도 정의
   → PlanCard로 충분, 별도 컴포넌트 만들지 않음

### Variants Bank 범위 (의도된 minimal)

- [ ] 모든 컴포넌트에 variants 강제
   → 3개만: BrandDirectionCard (current + horizontal_swipe + grid_2x3) / CardGrid5 / DirectionApprovalCard (minimal + verbose)
- [ ] QuickInputCard variants
   → current만 (Phase 3 구현 중 alt 도출 시 추가)
- [ ] Step별 카드 variants
   → BrandDirectionCard variants를 패턴으로 재사용

### Plan 비교 카드 / 3-plan 영역 (Phase 4 영역)

- [ ] PlanComparisonCard 상세 spec
   → component_map.md에 placeholder 1줄만 (Phase 4 deferred)
- [ ] 3-plan 비교 UX wireframe
   → Phase 4 진입 시 결정
- [ ] Critic verdict UI 상세 (revise 표시 등)
   → Phase 4

### 자동화 도구 (Phase 3 이후)

- [ ] `audit_page_component.ps1` (page ↔ component 정합 자동)
   → Phase 3 진입 후 실 컴포넌트 파일 생기면 작성
- [ ] `audit_design_handoff.ps1` (handoff 매핑 자동 검증)
   → Phase 3 또는 Phase 11+
- [ ] `replaceability_audit.ps1` (hardcoded 색/폰트 탐지)
   → Phase 3 진입 후 실 코드 분석 가능 시점

### Backend 변경

- [ ] backend/fastapi/ 코드 변경
   → Phase 2 = frontend spec only
- [ ] api_contract.md 변경
   → Phase 4 endpoint migration 시 contract-change

### 다국어 / 접근성 본격 (Phase 11+)

- [ ] i18n 시스템
- [ ] WCAG 2.1 AA 완전 준수
- [ ] RTL 언어 지원
- [ ] 스크린 리더 본격 테스트

### Performance / SEO (Phase 10+)

- [ ] Lighthouse 90+ 목표
- [ ] Code splitting 전략
- [ ] Image optimization

### 영구 제외 (mvp_non_goals.md §1)

- [ ] 영상 자동 편집 UI
- [ ] TTS / BGM UI
- [ ] YouTube 자동 업로드 UI

---

## 경계 위반 판단 기준

요청이 위 목록에 있으면:

1. **즉시 거절** — "Phase 2 non-goals에 해당"
2. **Phase 매핑** — Phase 3 / 4 / 10+ / 11+ 어디로 이관할지 명시
3. **예외 검토** — 반드시 필요하면 `meta/proposals/` 제안서 + contract-change Skill

---

## 변경 절차

non_goals 변경 (항목 제거 = Phase 2 scope 확장) 시:
1. `meta/proposals/` 제안 작성
2. `contract-change` Skill 절차
3. **multi-llm-validation 필수** (scope 변경 큰 결정)
4. 사용자 최종 승인

---

## 의도된 단순화 정책 명시

다음은 "Phase 2에서 안 하는" 것이 아니라 **의도된 단순화 (deferred to next phase)**:

| 항목 | Defer 대상 Phase | 이유 |
|---|---|---|
| 모든 컴포넌트 4-layer | Phase 3+ | over-engineering 회피, 실 코드 작성 중 보강이 자연스러움 |
| Variants Bank 전체 | Phase 4+ | 사용자 실 사용 데이터 누적 후 의미 있는 alt 도출 |
| Plan 비교 카드 spec | Phase 4 | 3-plan 활성화 시점에 결정 (premature optimization 회피) |
| audit 자동화 | Phase 3+ | 실 파일 생긴 후 자동 검증 도구 의미 ↑ |
| Step 2~7 wireframe 상세 | Phase 3 진입 시 | template 적용으로 90% 자동 도출 |

→ 이 항목들은 `handoff.md`에 Phase 3 인수 명시.
