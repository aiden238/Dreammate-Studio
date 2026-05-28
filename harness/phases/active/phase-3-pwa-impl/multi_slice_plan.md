# Phase 3 — Multi-Slice Execution Plan (Wave 1~5)

> 작성: 2026-05-28
> 방식: sub-agent 분산 + P-X1 §SELF-VERIFICATION 의무 + Wave 3 병렬 (Discovery ∥ Quick)

---

## 1. 의존성 그래프

```
Slice 1 (Foundation) ─→ Slice 2 (Thin Vertical Discovery Step 1)
                              ↓
                ┌─────────────┴─────────────┐
            Slice 3                       Slice 4
        (Discovery 2~7)              (Quick 4-step)
                ↓                         ↓
                └─────────────┬─────────────┘
                       Slice 5 (Middleware + /new)
                              ↓
                       Slice 6 (audit + smoke + 회고 + archive)
```

---

## 2. Wave 분할

### Wave 1 — 순차 (1 sub-agent)
- **A: Slice 1** — Foundation (Tailwind tokens 매핑)

### Wave 2 — 순차 (1 sub-agent)
- **B: Slice 2** — Thin Vertical Discovery Step 1 ★ Phase 3 핵심

### Wave 3 — 병렬 (2 sub-agents)
- **C: Slice 3** — Discovery 확장 (Step 2~7 + DirectionApprovalCard + ToneChipsForm)
- **D: Slice 4** — Quick Mode 4-step + QuickInputCard

폴더 분리:
- Slice 3 → `apps/web/app/new/discovery/`, `components/discovery/ToneChipsForm`, `components/common/DirectionApprovalCard`, `lib/discovery_state.ts`
- Slice 4 → `apps/web/app/new/quick/`, `components/quick/QuickInputCard`, `lib/quick_state.ts`
- 공유: Slice 4는 DirectionApprovalCard import만 (Slice 3 산출물)

### Wave 4 — 순차 (1 sub-agent)
- **E: Slice 5** — Mode Branching middleware + /new 진입점

### Wave 5 — 순차 (1 sub-agent)
- **F: Slice 6** — audit + smoke + retrospective + archive

총 sub-agent dispatch: **6**

---

## 3. 충돌 분석 매트릭스

| Wave | Slices | 변경 영역 | 충돌 위험 | 완화 |
|---|---|---|---|---|
| 1 | 1 | tailwind.config / globals.css / design_tokens.ts / app/layout.tsx | — | — |
| 2 | 2 | components/discovery/{BrandDirectionCard, CardGrid5} + app/new/discovery/step/1 + lib/state/wizard + lib/discovery_state | — (단독) | — |
| 3 | 3 + 4 | (3): app/new/discovery/step/[n] + components/discovery/ToneChipsForm + components/common/DirectionApprovalCard + lib/discovery_state ∥ (4): app/new/quick/* + components/quick/QuickInputCard + lib/quick_state | **0 (폴더 분리)** | sub-agent prompt에 다른 영역 forbidden 명시 + P-X1 §SELF-VERIFICATION 필수 |
| 4 | 5 | lib/mode_branching + app/new/page.tsx + (선택) middleware + ADR-013 | — | — |
| 5 | 6 | scripts/* + eval/qa_reports + meta/* + phases/archive + 상태 파일 | — | 단일 |

### 3.1 Wave 3 추가 안전 장치

- **Slice 3에서 DirectionApprovalCard 작성** → Slice 4가 import만 사용
- **Slice 4 sub-agent 프롬프트**: "DirectionApprovalCard 신규 작성 금지, Slice 3 산출물 활용. 만약 Slice 3가 아직 push 안 했으면 git pull --rebase 후 진행"
- Slice 3가 먼저 push 권장 (Slice 4 약간 지연 시작) — race 회피

### 3.2 P-X1 (component_map.md 절대 보호)

**모든 Wave 1~5 sub-agent prompt에 명시**:
```
component_map.md / page_map.md / design_handoff.md / design_system/* / wireframes/* / *flow.md 수정 0건 강제 (조정 4번).
spec ↔ 코드 drift 발견 시 phases/active/phase-3-pwa-impl/deviations.md에 기록만.
```

---

## 4. Sub-Agent 공통 절차 (P-X1 적용)

각 sub-agent 4-Phase + §SELF-VERIFICATION:

```
Phase A. 컨텍스트 로딩 (Slice 1 baseline + 이전 Slice 산출물만 — Surgical Scope)
Phase B. 파일 생성 (editable만, 4-layer chosen variant + variant prop 분기)
Phase C. 자동 검증:
  - npx tsc --noEmit
  - next build (또는 selective)
  - audit_naming 0 drift
  - pytest 62/62 (backend 무변경 확인)
Phase D. SELF-VERIFICATION (P-X1 v1.3.0 §6.3):
  - git status
  - git diff --stat HEAD
  - editable / forbidden 비교
  - forbidden 변경 발견 시 즉시 revert
  - 특히 component_map.md / page_map.md / design_handoff.md 0줄 수정 확인 (조정 4번)
Phase E. 하네스 기록 + commit + push:
  - eval/qa_reports/phase-3-slice-{N}_{date}.md
  - git commit + push
```

---

## 5. Slice별 sub-agent prompt 핵심

### Slice 1 (Wave 1)
- editable: tailwind.config.ts / globals.css / design_tokens.ts / app/layout.tsx / ADR-012 / QA report
- forbidden: 모든 spec 파일 (component_map etc.) + backend + Phase 1 components
- acceptance: next build OK + literal hex 0

### Slice 2 (Wave 2) ★
- editable: components/discovery/{BrandDirectionCard, CardGrid5} + app/new/discovery/step/1 + lib/state/wizard + lib/discovery_state + QA report
- forbidden: component_map.md (절대) + Phase 2 spec + 다른 Slice 영역
- acceptance: npm run dev 동작 + 카드 5장 + 선택

### Slice 3 (Wave 3, A)
- editable: app/new/discovery/* + components/discovery/ToneChipsForm + components/common/DirectionApprovalCard + lib/discovery_state + QA report
- forbidden: app/new/quick/* + components/quick/* + lib/quick_state (Slice 4 영역)
- 명시: ToneChipsForm 다중선택 chip 8개 + skip / DirectionApprovalCard verbose+minimal prop 분기

### Slice 4 (Wave 3, B)
- editable: app/new/quick/* + components/quick/QuickInputCard + lib/quick_state + QA report
- forbidden: app/new/discovery/* + components/discovery/* + DirectionApprovalCard 신규 작성
- 명시: DirectionApprovalCard는 Slice 3 산출물 import만

### Slice 5 (Wave 4)
- editable: lib/mode_branching + app/new/page.tsx + (선택) middleware + ADR-013 + QA report
- forbidden: 모든 spec 파일 + 다른 Slice 영역

### Slice 6 (Wave 5)
- editable: scripts/* + eval/qa_reports + meta/* + closing_notes + phases/active → archive 이동 + 상태 파일 4개
- forbidden: component_map.md (조정 4번 절대) + 다른 영역 코드 추가
- Skill 호출: design-review + qa-check v1.2.0 + meta-retrospective + phase-complete v1.1.0

---

## 6. 안전 장치

### 6.1 P-X1 §SELF-VERIFICATION (모든 sub-agent)

git diff --stat HEAD 자기 검증 — forbidden 변경 발견 시 즉시 revert.

### 6.2 Main session 후속 검증

각 Wave 완료 후:
```bash
git log -1 --stat
git diff HEAD~1 HEAD -- apps/web/component_map.md apps/web/page_map.md apps/web/design_handoff.md apps/web/design_system/ apps/web/wireframes/ apps/web/*flow.md apps/web/direction_approval.md apps/web/mode_branching.md
```

위 명령 결과 0줄 변경 확인. 1줄이라도 변경 시 revert 검토.

### 6.3 deviations.md 운영

Phase 3 진행 중 발견된 spec ↔ 코드 drift는 `phases/active/phase-3-pwa-impl/deviations.md`에 누적:

```yaml
- date: 2026-05-XX
  slice: N
  finding: "..."
  spec_file: "apps/web/component_map.md §X"
  code_file: "apps/web/components/Y.tsx"
  resolution: "deviation_log only (조정 4번 — component_map 수정 X)"
  follow_up: "Phase 4 proposal 등록 또는 그대로 유지"
```

### 6.4 PROJECT_STATE / PHASE_REGISTRY 충돌 회피

- 모든 Wave 1~5 sub-agent에 PROJECT_STATE / PHASE_REGISTRY 수정 금지 명시
- Slice 6 sub-agent만 최종 갱신

---

## 7. 진행 트래킹

```yaml
phase_3_multi_slice_progress:
  wave_1:
    status: pending
    sub_agents: [A_slice_1]
  wave_2:
    status: pending
    sub_agents: [B_slice_2]  # ★ Thin Vertical
  wave_3:
    status: pending
    sub_agents: [C_slice_3, D_slice_4]
  wave_4:
    status: pending
    sub_agents: [E_slice_5]
  wave_5:
    status: pending
    sub_agents: [F_slice_6]
deviation_count: 0  # 조정 4번 추적 — component_map 직접 수정 시도 횟수
```

---

## 8. 종료 조건 (Phase 3 완료)

- Slice 1~6 commit + push
- A1~A10 모두 PASS
- 변경성 시뮬 5/5 회귀 PASS
- pytest 62/62 + next build / tsc / lint 0 errors
- audit_naming + audit_page_component 0 drift
- **component_map.md 0줄 수정** (조정 4번 강제)
- meta/retrospectives/phase-3.md 작성
- archive 이동

---

## 9. 변경 이력

- 2026-05-28: 최초 작성 (Phase 3 진입 시, Wave 1~5 분할 + P-X1 적용)
