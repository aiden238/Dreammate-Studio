# Phase 3 — Assumptions (phase-start v1.3.0 §6 4점검)

> 작성: 2026-05-28
> Skill: phase-start v1.3.0 §6 (P-X1 §SELF-VERIFICATION 적용)

---

## 1. Assumptions

### 1.1 확정 가정

| # | 가정 | 근거 |
|---|---|---|
| A1 | Phase 0/1/2 archive baseline 가용 | phases/archive/* |
| A2 | Phase 2 design_handoff 5/5 PASS (변경 가능성 보장 환경) | phases/archive/phase-2-pwa-design/ |
| A3 | **audit_naming.ps1 0 drift** (2026-05-28 진입 시점) | scripts/audit_naming.ps1 실행 결과 |
| A4 | Phase 1 backend (POST /api/v1/generate) 유지 + 회귀 0 | pytest 62/62 |
| A5 | Phase 1 frontend (PlanCard / ErrorCard / ProgressStepper / SubmitButton) 유지 + 보존 | apps/web/components/ |
| A6 | **P-X1 적용 완료** (phase-start v1.3.0, §6.3 §SELF-VERIFICATION) | commit 3d0b0fb |
| A7 | Phase 2 17 spec 파일 read-only (조정 4번 — component_map 절대 보장) | non_goals.md |
| A8 | Thin Vertical 우선 (Slice 2 = Discovery Step 1 end-to-end) | 조정 2번 |
| A9 | PlanCard 4-layer 정합 Phase 4 이관 (D3) | 조정 3번 |
| A10 | 4-layer 4 컴포넌트 + Variants 3 컴포넌트 minimal 정책 (Phase 2 ADR-010/011) | apps/web/component_map.md |

### 1.2 불확실 항목 (U3-X)

| ID | 항목 | 검증 시점 |
|---|---|---|
| U3-1 | spec ↔ 코드 drift 발생 빈도 | Slice 6 변경성 시뮬레이션 회귀 |
| U3-2 | sub-agent forbidden 침범 재발 여부 (P-X1 효과 측정) | 매 Wave git diff 검증 |
| U3-3 | hardcoded 색 발생 (tokens 매핑 누락) | Slice 6 grep 검증 |
| U3-4 | Phase 1 endpoint vs Discovery 7-step UX 어댑터 비용 | Slice 3 진입 시 |
| U3-5 | Step 5 ToneChipsForm chip 개수 적정 (6/8/10) | Slice 3 dispatch 전 (기본 8) |
| U3-6 | session storage state machine Discovery + Quick 충돌 | Slice 4/5 manual |
| U3-7 | Phase 2 component_map.md 직접 수정 충동 (조정 4번 위반 가능성) | 매 Slice deviation 검증 |

### 1.3 Contract cross-reference 점검 (v1.2.0 §6.1)

```
[2026-05-28] scripts/audit_naming.ps1 실행
결과:
  plan_candidates   PASS   0 drift
  video_projects    PASS   0 drift
  critic_evaluation PASS   0 drift
  rag_references    PASS   0 drift

→ Phase 3 진입 baseline OK.
```

---

## 2. Simplest Slice (3회 압축)

```
1차: 모든 컴포넌트 + 모든 routes + middleware + 검증 (전체)
2차: Foundation + Brand card + Discovery Step 1만 (Thin Vertical 진입)
3차: Foundation (Tailwind tokens 매핑) — token 1줄 (primary 색) Tailwind theme.extend 연결만
```

**최종 Slice 1 baseline**: tailwind.config.ts에 tokens primary 매핑 + globals.css CSS variable 1개. 후속 Slice는 같은 패턴 확장.

→ **Slice 2 = Thin Vertical** (조정 2번): Slice 1 baseline 위에 Discovery Step 1 한 페이지 통째 작동.

---

## 3. Surgical Scope

### 3.1 editable

```
apps/web/
  tailwind.config.ts          (갱신)
  app/layout.tsx              (갱신)
  app/globals.css             (갱신)
  app/new/                    (NEW)
    page.tsx
    discovery/step/[n]/page.tsx
    quick/{page,clarify,direction,generate}/page.tsx
  components/
    discovery/  (NEW: BrandDirectionCard, CardGrid5, ToneChipsForm)
    common/     (NEW: DirectionApprovalCard)
    quick/      (NEW: QuickInputCard)
  lib/
    design_tokens.ts          (NEW)
    mode_branching.ts         (NEW)
    state/wizard.ts           (NEW)
    discovery_state.ts        (NEW)
    quick_state.ts            (NEW)
scripts/
  audit_page_component.ps1    (NEW, Slice 6 D5)
  smoke_test_phase_3.ps1      (NEW, Slice 6)
docs/decisions/
  phase_3_tailwind_tokens_mapping.md  (ADR-012)
  phase_3_mode_branching_middleware.md (ADR-013)
phases/active/phase-3-pwa-impl/  (9 entry files — 이미 작성 중)
  deviations.md  (NEW — 조정 4번 추적용)
eval/qa_reports/phase-3-*.md
meta/handoffs/2026-05-28_phase-3-entry.md
meta/retrospectives/phase-3.md (Slice 6)
```

### 3.2 read-only (조정 4번 강조)

```
apps/web/component_map.md   ← ★ 절대 read-only (조정 4번)
apps/web/page_map.md         ← read-only
apps/web/design_handoff.md   ← read-only
apps/web/design_system/*     ← read-only
apps/web/discovery_flow.md, quick_flow.md, mode_branching.md, direction_approval.md  ← read-only
apps/web/wireframes/*        ← read-only
apps/web/design.md           ← read-only
apps/web/app/page.tsx (Phase 1) ← Phase 1 / 보존
apps/web/app/plan/page.tsx (Phase 1) ← /plan 보존
apps/web/components/{PlanCard, ErrorCard, ProgressStepper, SubmitButton}.tsx ← Phase 1 보존
apps/web/lib/{api, types, errors}.ts ← Phase 1 보존
backend/  ← Phase 1 done, 무수정
docs/contracts/  ← read-only (contract-change Skill 필수)
ai_system/, knowledge/, product/  ← read-only
eval/{golden_set, failure_cases, INDEX}.md  ← read-only
.claude/skills/  ← P-X1 적용 완료 (v1.3.0), 추가 변경 없음
```

### 3.3 forbidden

```
phases/archive/  ← Phase 0/1/2
phases/planned/phase_4~30  ← 미래 영역
```

### 3.4 Sub-agent 자기 검증 (P-X1, v1.3.0 §6.3)

**모든 Wave 1~5 sub-agent prompt에 §SELF-VERIFICATION 포함 의무**:

```
1. git status — staged 파일 목록
2. git diff --stat HEAD — 본인 수정 파일 목록
3. editable / forbidden 비교
4. 의도하지 않은 forbidden 변경 시 즉시 revert + 보고
```

특히 **component_map.md 수정 0건 강제** (조정 4번 위반 = critical fail).

---

## 4. Verification

### 4.1 자동 (매 Slice)

| 항목 | 도구 |
|---|---|
| audit_naming | scripts/audit_naming.ps1 |
| pytest 회귀 | python -m pytest -q (62/62 PASS 유지) |
| next build | npm run build |
| tsc | npx tsc --noEmit |
| ESLint | npx next lint |
| sub-agent self-verification | git diff --stat HEAD (P-X1) |

### 4.2 자동 (Slice 6 신규)

- `scripts/audit_page_component.ps1` (D5) — page_map ↔ 실 routes / component_map ↔ 실 components 정합 자동 검사
- `scripts/smoke_test_phase_3.ps1` — Phase 1 smoke + Phase 3 추가 (/new 진입 + Discovery + Quick)

### 4.3 수동

- 변경성 시뮬레이션 5/5 회귀 (Slice 6)
- 브라우저 visual (Slice 2 Thin Vertical / Slice 3/4 routes)
- session storage state 검증

### 4.4 acceptance 매핑

A1~A10 (acceptance.md) → Slice별 자동 + manual 검증.

---

## 5. 4점검 요약

| 점검 | 결과 |
|---|---|
| Assumptions | 확정 10 + 불확실 7 (U3-1~7) + audit_naming 0 drift |
| Simplest Slice | Slice 1 Foundation (Tailwind tokens 매핑) → Slice 2 Thin Vertical |
| Surgical Scope | editable 25+ / read-only 광범위 (component_map 절대) / forbidden 명확 / P-X1 자기 검증 의무 |
| Verification | 자동 5개 매 Slice + Slice 6 신규 2개 + 수동 변경성 시뮬 5/5 |

---

## 6. 변경 이력

- 2026-05-28: Phase 3 진입 4점검 작성 (phase-start v1.3.0 §6 + P-X1 §SELF-VERIFICATION 적용)
