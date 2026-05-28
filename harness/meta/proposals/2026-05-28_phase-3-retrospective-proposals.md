# Proposal Batch — Phase 3 Retrospective 결과 (Y-X1~Y-X3)

> 출처: `meta/retrospectives/phase-3.md` §개선 제안
> 작성일: 2026-05-28
> 상태: proposed (Phase 4 진입 전 사용자 검토)
> 우선순위: **모두 낮음~보통** — Phase 2 P-X1 효과 5/5 입증으로 큰 신규 proposal 불필요. Y-X 시리즈는 미세 개선안.

---

## 채택 권장 제안 3개 (Y-X1~Y-X3)

### Y-X1 — design_handoff §6.1 매핑표에 "spec 영향" / "code 영향" 칸 분리 (우선순위: 낮음~보통)

**근거**: Phase 3 변경성 시나리오 5 (Quick mode 폐기) Phase 2 예상 ≤5 vs Phase 3 실측 7~8. 원인: Phase 2 design_handoff §6.1은 spec 파일 단위 영향만 다루고, Next.js app router 컨벤션 (file-per-route)에 의한 code 분할 미고려.

**5 Whys 결론** (phase-3 §근본 원인): spec phase의 예측 한계 — code 분할 정도가 phase 진입 후 결정됨. 매핑표 칸 분리하면 양쪽 모두 추적 가능.

**변경 대상**:
- `apps/web/design_handoff.md` §6.1 매핑표 (read-only, 조정 4번 — contract-change Skill 절차 필요)
- 또는 `phases/active/{design phase}/` 진입 시 보강

**구현 안 (예시)**:

```markdown
| # | 시나리오 | 예상 영향 (spec) | 예상 영향 (code) | 실측 (spec) | 실측 (code) | 결과 |
|---|---|---|---|---|---|---|
| 1 | tokens 색 변경 | ≤ 1 (tokens.md) | ≤ 2 (globals.css + design_tokens.ts) | 1 | 2 | PASS |
| 5 | Quick mode 폐기 | ≤ 5 (quick_flow + ...) | ≤ 8 (4 page.tsx + 1 component + ...) | 4 | 7~8 | PASS |
```

**예상 영향**: design_handoff.md ~15줄 추가 (매핑표 칸 확장)
**위험**: 낮음 (spec 파일 직접 수정 — contract-change Skill 필요)

**적용 권장 시점**: Phase 11+ (dark mode 등 design phase 재진입 시) 또는 P-X2 (변경성 시뮬 phase-complete 게이트) 채택 시 통합

---

### Y-X2 — audit_page_component.ps1 사용 가이드 / false-positive 감소 (우선순위: 낮음)

**근거**: Phase 3 Slice 6에서 첫 작성 후 case-sensitive matching (`-cmatch`) + stop_list 정제가 필요했음. Phase 4+ 새 컴포넌트 추가 시 (PlanComparisonCard / 새 routes 등) stop_list 누락으로 false-positive 가능.

**변경 대상**:
- `scripts/audit_page_component.ps1` header 주석 보강
- (선택) `scripts/README.md` 신규 작성 — audit_naming + audit_page_component + smoke 통합 가이드

**구현 안 (개요)**:

```powershell
# audit_page_component.ps1 — Phase 3 Slice 6 (D5)
# 사용 가이드:
#   - PowerShell -match 는 case-insensitive default — 본 도구는 -cmatch 사용 (case-sensitive)
#   - component_map.md section 헤더 (## Layout, ## Input 등)는 stop_list에 추가 필요
#   - 새 컴포넌트 추가 시 자동 검출 — 단, 새 비-컴포넌트 ## 헤더 (e.g. ## Replaceability)도 stop_list 추가
#   - dynamic route (예: /step/[n])는 dynamic_coverage 로직으로 spec /step/2~7과 매핑
```

**예상 영향**: 주석 +20줄 / 별도 README 작성 시 +50줄
**위험**: 없음

**적용 권장 시점**: Phase 4 진입 직전 또는 새 컴포넌트 추가 시점

---

### Y-X3 — Sub-path 분리 패턴 표준 등록 (P-FOLDER-PARALLEL-001 확장, 우선순위: 낮음)

**근거**: Phase 3 Wave 3 (Slice 3 + Slice 4 병렬)이 같은 폴더 다른 sub-path 분리 (lib/discovery_state.ts + components/discovery/* vs lib/quick_state.ts + components/quick/*)로 무충돌. P-FOLDER-PARALLEL-001 (다른 폴더 분리)의 자연 확장.

**변경 대상**:
- `meta/patterns.md` P-FOLDER-PARALLEL-001 §확장 또는 새 P-SUB-PATH-PARALLEL-001 등록

**구현 안 (개요)**:

```markdown
### Pattern P-SUB-PATH-PARALLEL-001 (또는 P-FOLDER-PARALLEL-001 §확장):
같은 root 폴더 (예: apps/web/lib/, apps/web/components/) 다른 sub-path 분리도 병렬 dispatch 안전.
조건: sub-agent 프롬프트에서 sub-path를 명시 + §SELF-VERIFICATION (P-X1) 강제.
효과: 같은 디렉토리 내 작업 분리 시 폴더 새로 만들 필요 없이 sub-path 분리만으로 충돌 회피.
```

**예상 영향**: meta/patterns.md +15줄
**위험**: 없음 (패턴 등록만)

**적용 권장 시점**: Phase 4+ Wave 3 재발 시 (재발 없으면 deferred)

---

## Phase 2 P-X 후속 재평가 (Phase 3 종료 시점)

### P-X1 (sub-agent enforcement 강화)
- 상태: ✅ accepted + applied (Phase 3 pre-entry, commit `3d0b0fb`)
- **효과 측정 (Phase 3)**: 5/5 PASS (Slice 1~5 모든 sub-agent §SELF-VERIFICATION PASS, component_map.md 0줄 6연속 보존)
- 결정: **유지** — Phase 4+ 모든 sub-agent dispatch에 의무 적용 (phase-start v1.3.0)

### P-X2 (변경성 시뮬레이션 phase-complete 게이트)
- 상태: pending
- **Phase 3 검토**: Phase 3 acceptance A9는 manual walkthrough (Slice 6 본 보고서)로 진행, 자동 게이트화하면 design phase 재진입 시 효과
- 결정: **Phase 4 진입 전 채택 권장** (sub-acceptance: spec/code phase 분기 + Y-X1 통합)

### P-X3 (design-review SKILL.md spec-only 분기)
- 상태: pending
- **Phase 3 검토**: Phase 3는 impl phase — design-review SKILL.md §B 절차 그대로 적용 (Slice 6 §5). spec-only phase 분기 필요성은 Phase 11+ design phase 재진입 시점에 발생
- 결정: **Phase 11+ 재진입 시 채택 검토** — Phase 4 진입 직전에는 불필요

### P-X4 (worktree isolation)
- 상태: deferred
- **Phase 3 검토**: P-X1만으로 5/5 효과 충분 — worktree 복잡도 도입 불필요
- 결정: **deferred 유지** (P-X1 효과 부족 시 재평가)

### P-X5 (매트릭스 표준 등록)
- 상태: deferred
- **Phase 3 검토**: P-X2 통합 자연 흡수 가능 — 별도 작업 불필요
- 결정: **deferred 유지** (P-X2 채택 시 자연 흡수)

---

## Phase 1 P5/P6 deferred 재평가 (Phase 3 종료 시점)

### P5 (tech_stack Python 패키지명 충돌 방지 가이드)
- Phase 3 backend 무변경 → 재발 0 → **deferred 적정 유지**

### P6 (assumptions.md §1.2 자동 트래킹)
- Phase 3 assumptions.md U2-* 추적 (manual) — 코드 phase는 spec phase보다 가정 변경 적음
- → **deferred 적정 유지** (P-X2 적용 후 자연 트래킹 통합 가능)

---

## 의존 / 적용 순서

```
P-X2 (변경성 시뮬 게이트) ── Phase 4 진입 전 채택 권장
  └── Y-X1 (매핑표 칸 분리) 통합 가능
  └── P-X5 (매트릭스 표준) 자연 흡수

Y-X2 (audit_page_component 가이드) ── Phase 4 진입 직전 또는 임의 시점
Y-X3 (Sub-path 분리 패턴) ── Phase 4+ Wave 3 재발 시 (조건부)

P-X1 (sub-agent enforcement) ── ✅ applied + 5/5 효과 입증
P-X3 (design-review spec-only) ── Phase 11+ design phase 재진입 시
P-X4 (worktree isolation) ── deferred 유지
```

---

## 사용자 검토 결과 (대기)

```yaml
status: proposed (awaiting user review, Phase 4 진입 전)
decision_date: TBD
decision: TBD
recommended_for_phase_4_entry: [P-X2 (Phase 2 P-X2 + Y-X1 통합)]
recommended_general: [Y-X2 audit gardrail]
deferred_recommended: [Y-X3, P-X3, P-X4, P-X5]
```

**검토 권장 시점**: Phase 4 진입 전 (특히 P-X2 + Y-X1 통합 검토).

---

## 변경 이력

- 2026-05-28: Phase 3 회고 결과 3 제안 배치 작성 (Y-X1~Y-X3) + Phase 2 P-X1~P-X5 재평가 (P-X1 ✅ 효과 입증 / P-X2 채택 권장 / P-X3 Phase 11+ / P-X4/P-X5 deferred 유지)
