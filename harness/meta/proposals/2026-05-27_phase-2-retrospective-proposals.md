# Proposal Batch — Phase 2 Retrospective 결과 (P-X1~P-X5)

> 출처: `meta/retrospectives/phase-2.md` §개선 제안
> 작성일: 2026-05-27
> 상태: **partial accepted (P-X1 적용, 2026-05-28 Phase 3 pre-entry)**
> 결정:
>   - **P-X1: ✅ accepted + applied (2026-05-28)** — phase-start v1.2.0 → v1.3.0
>     변경 로그: docs/contract_changes/2026-05-28-px1-sub-agent-self-verification.md
>   - P-X2, P-X3, P-X4, P-X5: pending (Phase 3 진행 중 또는 종료 시점 재검토)

---

## 채택 권장 제안 5개 (P-X1~P-X5)

### P-X1 — sub-agent forbidden enforcement 강화 (우선순위: 높음)

**근거**: Wave 3 Slice 3 sub-agent가 forbidden 영역 (QuickInputCard sub-section, Slice 4 영역)을 component_map.md에 추가. multi_slice_plan.md §5 Slice 3 prompt에 "QuickInputCard 건드리지 말 것" 명시했음에도 발생. 결과적으로 무충돌 (append-only, Slice 4가 같은 파일 미수정) — 그러나 Phase 3+ 코드 phase는 같은 .tsx 파일 동시 수정 위험 ↑.

**5 Whys 결론** (phase-2 §근본 원인): sub-agent forbidden enforcement는 prompt 외 추가 메커니즘 (자기 검증 절차 / git diff hook / worktree isolation 중 하나) 필요.

**변경 대상**:
- `phases/active/{phase}/multi_slice_plan.md` template 갱신
- `.claude/skills/phase-start/SKILL.md` v1.2.0 → v1.3.0 §6.3 Surgical Scope 보강
- (선택) sub-agent 분산 패턴 표준 가이드 (`meta/guardrails.md` 또는 새 문서)

**구현 안**:

```markdown
## sub-agent 자기 검증 절차 (추가)

각 sub-agent는 작업 완료 직전 다음 자기 검증 수행:

1. `git status --short` 실행
2. staged 파일 list와 multi_slice_plan.md §5의 본 Slice "editable" 영역 매트릭스 cross-check
3. **editable 외 staged 변경이 1개라도 있으면**:
   - main session에 명시 통보 ("Out-of-scope edit detected: <file> — reason: <자유 텍스트>")
   - 또는 자체 revert (`git restore --staged <file>` + `git checkout <file>`)
4. commit message에 본 자기 검증 결과 명시 ("Self-check: 0 out-of-scope edits" or "Out-of-scope: <list>")
5. main session은 sub-agent commit 후 자체 `git diff HEAD~1 HEAD --stat`으로 재검증
```

**예상 영향**: sub-agent dispatch 당 +2~3분 (자기 검증 + main session 검증)
**위험**: 작음 (절차 강화만, 기존 동작 보존)

**적용 권장 시점**: Phase 3 진입 전 (코드 phase는 위험 ↑이므로 필수)

---

### P-X2 — 변경성 시뮬레이션 phase-complete 자동 게이트로 격상 (우선순위: 보통)

**근거**: Phase 2의 acceptance A9 "변경성 시뮬레이션 5/5"가 매 design phase 종료 시 동일 절차로 강제되면 좋음. 그러나 현재는 acceptance.md에 1회 명시 + Slice 6에서 manual walkthrough. phase-complete Skill에 통합되면 Phase 11+ dark mode / i18n / 새 컴포넌트 추가 phase 등에서 자동 트리거.

**변경 대상**:
- `.claude/skills/phase-complete/SKILL.md` v1.1.0 → v1.2.0
- (선택) 새 메타 절차 또는 phase-complete §spec phase 분기

**변경 내용 (§1.6 신규)**:

```markdown
### 1.6 [Spec/Design phase only] 변경성 시뮬레이션 게이트

해당 Phase가 spec/design phase인 경우 (코드 변경 < 10%, markdown 변경 > 90% 등):

1. phases/active/{phase}/acceptance.md에서 "변경성 시뮬레이션" 항목 존재 확인
2. 없으면 phase-complete 차단 (사용자 결정 — acceptance 보강 또는 skip 사유 기록)
3. 있으면 해당 시뮬레이션 walkthrough 결과를 final QA report §변경성 Eval에 첨부
4. N개 중 M개 PASS 비율 80%+ → PASS, 미만 → 사용자 결정 (보강 또는 강제 종료)
```

**예상 영향**: phase-complete 실행 시간 +5~10분 (해당 phase만)
**위험**: 없음 (조건부 절차)

**적용 권장 시점**: Phase 3 진입 직후 (Phase 3 자체는 코드 phase라 미적용, Phase 4+ 회귀 검증 시 활용)

---

### P-X3 — design-review SKILL.md에 spec-only phase 절차 추가 (우선순위: 낮음~보통)

**근거**: design-review Skill SKILL.md는 "구현된 화면" 가정 (eval/design_reviews/ 저장). Phase 2는 spec phase — wireframes ASCII / 4-layer markdown 검토만 가능. Slice 6에서 QA report §5에 통합으로 우회 (Surgical Scope 회피).

**변경 대상**:
- `.claude/skills/design-review/SKILL.md` v1.0.0 → v1.1.0

**변경 내용 (§분기 절차 신규)**:

```markdown
## 적용 phase 분기

### A. Spec-only phase (Phase 2 같은 design phase)
- 대상: design.md / page_map / component_map / 4-layer markdown / wireframes ASCII
- 절차:
  1. 해당 phase entry 시 baseline (design.md Phase 0) 로딩
  2. Phase 신규 spec과 baseline 정합 점검 (모바일 우선 / 카드 단위 / Intent Filtering 등 design.md 원칙)
  3. 결과를 phase-N-final QA report §design-review에 통합 (별도 eval/design_reviews/ 파일 생성 회피)

### B. Impl phase (Phase 3 같은 코드 phase)
- 대상: 실 컴포넌트 .tsx / 스토리북 / 실 브라우저 visual
- 절차: (기존 SKILL.md 절차 유지)
- 결과: `eval/design_reviews/{date}_{phase}_review.md`
```

**예상 영향**: design-review SKILL.md ~30줄 추가
**위험**: 없음

**적용 권장 시점**: Phase 11+ (dark mode 등 design phase 재진입 시) 또는 임의 시점

---

### P-X4 — worktree isolation 도입 검토 (우선순위: 낮음, deferred)

**근거**: P-AGENT-SCOPE-001의 근본 차단 — sub-agent 병렬 시 별도 worktree에서 작업하면 true file lock으로 forbidden 침범 0.

**변경 대상**:
- 새 가이드: `meta/worktree_dispatch_pattern.md`
- multi_slice_plan template 신규 옵션

**구현 안 (개요)**:

```bash
# main session에서:
git worktree add ../dreammate-slice-3 main
git worktree add ../dreammate-slice-4 main
# sub-agent 3 → worktree slice-3에서 작업
# sub-agent 4 → worktree slice-4에서 작업
# 완료 후 main에 merge / rebase
```

**예상 영향**: dispatch 절차 복잡도 ↑ (worktree 생성/제거/merge), 디스크 사용 ↑
**위험**: 보통 (단일 워크트리 패턴이 현재 충분히 작동 — P-AGENT-SCOPE-001 1회 발생, 무충돌)

**상태**: deferred — Phase 3+ 코드 phase 진행 중 재발 시 재평가. P-X1만 적용 후 효과 측정.

---

### P-X5 — meta/patterns.md 변경성 매트릭스 표준 등록 (우선순위: 낮음)

**근거**: design_handoff.md §1 5 시나리오 매핑표 패턴 (Replaceability L/M/H + 영향 파일 수)을 다른 phase (특히 contracts / api / DB schema) 변경성 평가에도 표준 적용하면, Phase 4 MOA Lite / Phase 5 Auth 등에서 같은 매트릭스 작성 가능.

**변경 대상**:
- `meta/patterns.md` — P-DESIGN-LAYERED-001 보강 또는 새 P-REPLACEABILITY-MATRIX 패턴 등록
- (선택) `phases/_template/` (있다면) acceptance.md template에 "변경성 시뮬레이션" section

**상태**: P-X2 적용 후 자연 통합 가능 — 별도 작업 deferred.

---

## 미채택 / 보류 제안

(현재 없음 — P-X4 / P-X5는 deferred로 분류하되 reject은 아님)

---

## Phase 1 P5/P6 deferred 재평가

Phase 1 회고의 deferred 보류 항목 — Phase 2 진행 중 재발 여부:

### P5 (tech_stack Python 패키지명 충돌 방지 가이드)
- Phase 2 코드 변경 0 → 재발 0 → **deferred 적정 유지**

### P6 (assumptions.md §1.2 자동 트래킹)
- Phase 2 assumptions.md §1.2 U2-1~U2-8 항목 모두 정확 추적 (manual)
- U2-7 (Tone form 패턴) Slice 3 진입 시 실시간 결정 — 트래킹 효과적
- → **deferred 적정 유지** (P-X2 적용 후 자연 트래킹 통합 가능)

---

## 의존 / 적용 순서

```
P-X1 (sub-agent enforcement) ──→ Phase 3 진입 전 필수
       ↓
       └──→ P-X2 (변경성 시뮬 게이트) ──→ Phase 4+ 시점 적정
       └──→ P-X3 (design-review spec-only) ──→ Phase 11+ 또는 임의 시점

P-X4 (worktree isolation) → P-X1 적용 후 재발 시 재평가
P-X5 (매트릭스 표준) → P-X2 통합 자연 흡수
```

---

## 사용자 검토 결과 (대기)

```yaml
status: proposed (awaiting user review)
decision_date: TBD
decision: TBD
recommended_for_phase_3_entry: [P-X1]
recommended_general: [P-X2, P-X3]
deferred_recommended: [P-X4, P-X5]
```

**검토 권장 시점**: Phase 3 진입 전 (특히 P-X1).

---

## 변경 이력

- 2026-05-27: Phase 2 회고 결과 5 제안 배치 작성 (P-X1~P-X5)
