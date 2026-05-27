# ADR-010: Phase 2 4-Layer Design — Minimal Application

> ADR ID: ADR-010
> Status: accepted
> Date: 2026-05-27
> Author: Claude (Opus 4.7) + GPT 검토 (회고 80점) + 사용자 승인 (조정안 채택)
> Related: `apps/web/design_system/component_contract.md`, ADR-011 (Variants 3개), Phase 2 Slice 1

---

## Context (배경)

Phase 2 진입 시 디자인 명세 작성 전략을 검토하면서 **4-layer 분리** (Behavior / Layout / Visual / Wireframe) 적용 범위가 쟁점이 됨.

### 4-layer 원칙

- **Layer 1 Behavior**: Props / State / Events / a11y (가장 안정, 변경 비용 H)
- **Layer 2 Layout**: 배치 / responsive / spacing (변경 비용 M)
- **Layer 3 Visual**: 색 / 폰트 / radius / motion (가장 변경 쉬움, 변경 비용 L)
- **Layer 4 Wireframe**: ASCII art / 시각 참고 (변경 비용 L)

→ layer 단위로 변경 영향을 한정해서, 디자인 swap 시 다른 layer 영향 0.

### 의사결정 쟁점

**모든 컴포넌트 (`apps/web/design.md` §10 기준 30+ 컴포넌트)에 4-layer 강제할 것인가?**

- 강제 시: 문서 30+ × 4 layer = 120+ section. 작성/유지 비용 큼.
- 미강제 시: 변경 가능성 보장 약함.

GPT 회고 (80점) + 사용자 검토에서 **조정안** 제시: 핵심 컴포넌트만 강제.

---

## Decision (결정)

### 4-layer 강제는 4개 핵심 컴포넌트에만 적용

| # | 컴포넌트 | 이유 |
|---|---|---|
| 1 | `BrandDirectionCard` | Discovery Step 1~7의 카드 패턴 baseline (재사용 빈도 ★★★) |
| 2 | `CardGrid5` | 5장 배치 컨테이너, Discovery 전 단계 공통 |
| 3 | `DirectionApprovalCard` | 양 모드(Discovery + Quick) 공통 핵심 UX |
| 4 | `QuickInputCard` | Quick Mode 입력 + 부족정보 질문, 양 모드 분기점 |

### 나머지 컴포넌트는 minimal entry만

`component_map.md`에:
- 이름 / 분류 / 의존성 / Phase 진입 시점만

→ Phase 3+ 실 구현 중 자연스러운 보강.

---

## Alternatives Considered (대안)

### A. 모든 컴포넌트 4-layer 강제 (재구성 초안)

- **장점**: 변경 가능성 100% 보장 — 어떤 컴포넌트도 4-layer 단위 swap
- **단점**: 30+ 컴포넌트 × 4 layer 작성/유지 = 큰 문서 부채. Phase 2 일정 초과.
- **결정**: **거부** — over-engineering. 변경 빈도 낮은 컴포넌트까지 4-layer 명세는 비용 대비 가치 ↓

### B. 4-layer 채택 안 함 (기존 plan)

- **장점**: 작업 단순
- **단점**: 변경 가능성 보장 약함. 디자인 swap 시 매번 직접 grep.
- **결정**: **거부** — Phase 2 핵심 가치(변경 가능성 baseline)와 모순

### C. 4개만 강제 + 예시 1개로 정립 + 후속 Phase에서 보강 ← **채택**

- **장점**:
  - 변경 빈도 높은 컴포넌트만 보장 (실효성 우선)
  - Phase 2 일정 내 작성 가능
  - Phase 3 진입 sub-agent가 template 그대로 적용 가능
- **단점**: 4개 외 컴포넌트는 4-layer 미적용 — Phase 3+ 보강 필요 (deferred 명시)
- **결정**: **채택** (사용자 승인, GPT 검토 80점)

### D. 3개만 강제 (QuickInputCard 제외)

- **장점**: 더 minimal
- **단점**: Quick Mode 핵심 입력 컴포넌트가 minimal entry만이면 양 모드 분기 UX 보증 약함
- **결정**: **거부** — QuickInputCard는 양 모드 분기점이라 4-layer 가치 큼

---

## Consequences (결과)

### Positive

- **변경 비용 ↓**: Visual swap 1 파일 (tokens.md), Layout swap 2~4 파일 (variants)
- **Phase 3 진입 sub-agent가 template 그대로 적용** — `component_contract.md` §2 template 복사
- **over-engineering 회피**: 변경 빈도 낮은 컴포넌트는 minimal entry로 충분
- **단계적 보강 가능**: Phase 3 구현 중 필요 시 컴포넌트 entry를 4-layer로 승격 (lazy expansion)

### Negative

- **4개 외 컴포넌트는 4-layer 미적용** → Phase 3+ 보강 필요 (handoff.md에 deferred 명시)
- **신규 컴포넌트 추가 시 4-layer 적용 여부 결정 비용** → 본 ADR §1.4 패턴 재사용 정책으로 완화

### Mitigation

- `component_contract.md` §0에 적용 범위 명시
- `component_contract.md` §5에 minimal entry 형식 명시
- Phase 2 acceptance에 "4 핵심 컴포넌트 4-layer 작성" 명시
- Phase 3 진입 시 implementation sub-agent가 추가 4-layer 필요성 발견 시 ADR-X로 보강

---

## 4-Layer 적용 안 하는 컴포넌트 (Phase 3 deferred)

| 컴포넌트 | 적용 시점 (예상) | 사유 |
|---|---|---|
| `PlanCard` (Phase 1 기존) | Phase 4 (3-plan 활성화 시) | 현재 단일 사용, Phase 4에서 3-plan 비교 패턴 도입 시 4-layer 의미 ↑ |
| `ErrorCard` (Phase 1 기존) | Phase 3 구현 중 자연스러운 보강 | error_response_contract §6 8 user_action 처리는 이미 contract에 명시 |
| `ProgressStepper` (Phase 1 기존) | Phase 3 구현 중 | 4단계 stepper는 frontend_design_contract §8에 이미 spec |
| `AgentStatusIndicator`, `RAGReferencePanel` | Phase 7 (RAG 도입) | 현재 placeholder, Phase 7에서 실 데이터 영향 ↑ |
| `BrandMemoryPanel`, `ProjectMemoryDrawer` | Phase 8 (Memory 활성화) | Phase 8에서 본격 |
| `IntentWarningBox` | Phase 3 또는 Phase 5 | output_schema P-AUX-1 매핑은 이미 contract 명시 |
| Layout (`AppShell`, `BottomActionBar` 등) | Phase 3 구현 중 | shadcn/ui wrap 기본 패턴 적용 |

---

## Phase 2 ↔ Phase 3 인수 명시

`phases/active/phase-2-pwa-design/handoff.md` (Slice 6에서 작성)에:

```
4-layer 미적용 컴포넌트 deferred list:
  - PlanCard / ErrorCard / ProgressStepper / SubmitButton (Phase 1 기존)
  - AgentStatusIndicator / RAGReferencePanel (Phase 7 시점)
  - BrandMemoryPanel / ProjectMemoryDrawer (Phase 8 시점)
  - IntentWarningBox / Layout (Phase 3 구현 중)

→ Phase 3 sub-agent는 component_map.md의 minimal entry + 4-layer 4개를 baseline으로 작업.
→ 4-layer 추가 필요 시 ADR-X로 등재 후 작성.
```

---

## Verification (검증)

```bash
# Phase 2 Slice 6 자동 검증
grep -c "## Behavior\|## Layout\|## Visual\|## Wireframe" apps/web/component_map.md
# 예상: ≥ 16 (4 컴포넌트 × 4 layer)
```

Slice 6에서 design-review Skill 실행 시 본 ADR 정책 준수 확인.

---

## Related ADRs / Docs

- ADR-011 (`docs/decisions/phase_2_variants_3_components.md`) — Variants Bank 3개 적용
- `apps/web/design_system/component_contract.md` — 4-layer template 정의
- `apps/web/design_system/tokens.md` — Visual layer 참조 토큰
- `meta/proposals/2026-05-26_phase-1-retrospective-proposals.md` P1~P4 — Phase 2 진입 baseline
- `meta/retrospectives/phase-1.md` — P-DRIFT-001 패턴 (Phase 2 의도 회피)
- `phases/active/phase-2-pwa-design/goals.md` G1, G2 (Design System Foundation, 4-layer 핵심 컴포넌트)

---

## 변경 이력

- 2026-05-27: ADR-010 최초 작성. Phase 2 Slice 1 진입 시 사용자 승인 + GPT 검토 80점 기반 조정안 채택.
