# ADR-011: Phase 2 Variants Bank — 3 Components Application

> ADR ID: ADR-011
> Status: accepted
> Date: 2026-05-27
> Author: Claude (Opus 4.7) + GPT 검토 + 사용자 승인
> Related: ADR-010 (4-layer Minimal), `apps/web/design_system/variant_format.md`, Phase 2 Slice 1

---

## Context (배경)

`variant_format.md`에 정의된 Variants Bank는 컴포넌트별로 의미 있는 alt를 명시 + chosen flag로 swap 가능하게 함.

### 의사결정 쟁점

**모든 컴포넌트에 Variants Bank 적용할 것인가?**

- 전체 적용 시: 30+ 컴포넌트 × 평균 2~3 variants = 60~90 variant entry. 관리 비용 큼. 가짜 alt 만들 위험.
- 미적용 시: 컴포넌트 swap 시 매번 직접 redesign.

---

## Decision (결정)

### Variants Bank는 3개 컴포넌트에만 적용

| # | 컴포넌트 | Variants 수 | 사유 |
|---|---|---|---|
| 1 | `BrandDirectionCard` | 3 (current / horizontal_swipe / grid_2x3) | Discovery 5장 카드 배치는 모바일 UX의 핵심 결정 — 의미 있는 alt 3개 존재 |
| 2 | `CardGrid5` | 2~3 (Slice 2에서 정식 결정) | 5장 컨테이너의 vertical / horizontal / grid 분기 — BrandDirectionCard variants와 연동 |
| 3 | `DirectionApprovalCard` | 2 (minimal / verbose) | 한 줄 승인 vs 컴포넌트 분해 — Quick Mode UX와 Discovery 신뢰성 사이 trade-off |

### 나머지 컴포넌트는 current variant만

- `QuickInputCard`: current only (Phase 3 구현 중 alt 도출 시 추가)
- Phase 1 기존 (`PlanCard`, `ErrorCard` 등): variants 없음 (Phase 1 구현 그대로)
- 기타 컴포넌트 (`AgentStatusIndicator` 등): current only

---

## Alternatives Considered (대안)

### A. 전체 컴포넌트 Variants Bank 적용

- **장점**: 모든 컴포넌트 swap 가능
- **단점**:
  - 30+ × 2~3 variants = 60~90 entry. Phase 2 일정 초과.
  - **의미 없는 alt를 만들기 시작** (가짜 alt 위험) — variants format의 가치 ↓
- **결정**: 거부

### B. Variants Bank 0개 (도입 안 함)

- **장점**: 작업 단순
- **단점**: 디자인 swap 시 매번 직접 redesign — 변경 가능성 보장 약함
- **결정**: 거부 — Phase 2 핵심 가치(변경 가능성)와 모순

### C. 1개 컴포넌트만 (BrandDirectionCard)

- **장점**: 최소 baseline
- **단점**: Direction Approval (Quick Mode 핵심)이 variants 없음 → minimal vs verbose 갈등 미해소
- **결정**: 거부 — DirectionApprovalCard는 양 모드 공통 UX라 variants 가치 큼

### D. 3개 컴포넌트 (BrandDirectionCard + CardGrid5 + DirectionApprovalCard) ← **채택**

- **장점**:
  - 의미 있는 alt가 명확히 존재하는 컴포넌트만 (CardGrid5는 BrandDirectionCard variants와 paired)
  - Discovery + Quick 양 모드의 핵심 UX 결정점 모두 cover
  - 작업 가능 범위
- **단점**: QuickInputCard 등은 current만 — Phase 3 진입 시 alt 도출 가능 (관리 가능한 deferred)
- **결정**: **채택**

### E. 5개 컴포넌트 (위 3 + QuickInputCard + PlanCard)

- **장점**: 더 광범위
- **단점**:
  - QuickInputCard alt가 현재 명확하지 않음 (Phase 3 구현 후 자연 도출 예상)
  - PlanCard는 Phase 4 3-plan 활성화 시점에 variants 의미 ↑
- **결정**: 거부 — premature optimization

---

## Consequences (결과)

### Positive

- **의미 있는 alt만 명시** — variants Bank의 신뢰성 ↑ (가짜 alt 없음)
- **양 모드 핵심 UX 결정점 cover** — Discovery 카드 배치 + Direction Approval 표시 방식
- **Phase 9+ A/B 테스트 baseline** — chosen 변경으로 즉시 swap 가능
- **관리 비용 ↓** — 3 컴포넌트 × ~2.5 variants = ~7 entry. Phase 2 일정 내 충분

### Negative

- **QuickInputCard 등은 current만** — Phase 3+ 구현 중 alt 도출 시 추가 필요 (lazy expansion)
- **추가 컴포넌트 variants 필요 시 ADR-X 등재** — 신규 결정 비용

### Mitigation

- `variant_format.md` §0에 적용 범위 명시
- 신규 컴포넌트 variants 추가는 contract-change Skill 절차 적용 안 함 (variants Bank는 contract 외부) — 가벼운 ADR로 충분
- Phase 9+ 사용자 데이터 누적 후 의미 있는 alt 도출 시점에 추가

---

## Phase 2 ↔ Phase 9+ 인수 명시

```
Variants 미적용 컴포넌트 lazy expansion 후보:
  - QuickInputCard: Phase 9 사용자 부족정보 질문 형식 데이터 후 (textarea vs choice button vs 슬라이더)
  - PlanCard: Phase 4 3-plan 활성화 후 (vertical swipe vs horizontal 3-col vs grid 2x2 + 1)
  - ErrorCard: 사용자 행동 데이터 후 (action button 위치 / category icon 형식)

→ 각 추가는 ADR-X 등재 + variant_format.md 형식 그대로 적용.
```

---

## Verification (검증)

```bash
# Phase 2 Slice 6 자동 검증
grep -c "variants:" apps/web/component_map.md
# 예상: ≥ 3 (3개 컴포넌트의 variants yaml 존재)

# chosen=true 정확히 1개씩 (각 variant block당)
grep -c "chosen: true" apps/web/component_map.md
# 예상: 3 (또는 CardGrid5에 따라 더 — 컴포넌트당 정확히 1)
```

---

## Related ADRs / Docs

- ADR-010 (`docs/decisions/phase_2_design_layered_minimal.md`) — 4-layer Minimal Application
- `apps/web/design_system/variant_format.md` — yaml schema 정의
- `apps/web/design_system/replaceability_score.md` — variants swap 비용 정의
- `phases/active/phase-2-pwa-design/assumptions.md` A8 (Variants Bank 3개 컴포넌트 한정)
- `phases/active/phase-2-pwa-design/non_goals.md` §Variants Bank 범위

---

## 변경 이력

- 2026-05-27: ADR-011 최초 작성. Phase 2 Slice 1 진입 시 사용자 승인 (3개 한정 채택).
