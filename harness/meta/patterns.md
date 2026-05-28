# meta/patterns.md

> 🚧 Placeholder (Phase 0 진입 직후 생성. 첫 retrospective 발생 시점부터 누적)

## 목적

meta-retrospective Skill이 회고를 거듭하면서 식별하는 **반복되는 패턴**(반복 실패 / 반복 성공 / 위험 신호)을 한곳에 누적한다.

회고는 개별 사건의 5 Whys + 액션을 담고, 이 파일은 패턴화된 인사이트만 모은다.

## 작성 트리거

- `meta-retrospective` Skill이 같은 카테고리의 회고를 3회 이상 누적했을 때
- harness-audit Skill 실행 시 발견한 구조적 패턴
- 사용자가 명시적으로 "이건 패턴이다"라고 지적했을 때

## 항목 형식

```markdown
### Pattern P-{NN}: {짧은 이름}

- **유형**: 반복 실패 | 반복 성공 | 위험 신호 | 운영 인사이트
- **최초 식별**: {YYYY-MM-DD}
- **관련 회고**: meta/retrospectives/{...}
- **요약**: 1–3줄
- **권장 대응**:
  - {액션 1}
  - {액션 2}
- **연관 Skill / Contract**: {목록}
```

## 보존 정책

- 영구 보존 (회고와 별도)
- 패턴이 해소되면 "Resolved" 표기만 추가, 삭제 금지

## 인덱스

### Pattern P-DRIFT-001: sub-agent 분산 작성 시 contract 명명 drift 사후 발견

- **유형**: 반복 실패 → **Mitigated** (2026-05-27)
- **최초 식별**: 2026-05-26 (Phase 1)
- **관련 회고**: meta/retrospectives/phase-1.md §근본 원인 (5 Whys)
- **요약**: contract를 sub-agent 분산으로 작성하면 contract 내부 cross-reference (예: API body 키 = DB 테이블 = TS interface) 명명 일관성이 자동 검증되지 않아 다음 Phase 구현 중 발견됨. Phase 1에서 CC-001 (`plan_options` / `plans` / `plan_candidates` 3-way drift).
- **적용된 대응 (2026-05-27)**:
  - ✅ scripts/audit_naming.ps1 신규 작성 (NAMING_POLICY + whitelist)
  - ✅ harness-audit v1.1.0 §6.5 audit_naming 단계 추가 (P1)
  - ✅ phase-start v1.2.0 §6.1 Contract cross-reference 점검 추가 (P2)
  - ✅ qa-check v1.2.0 카테고리 11 Contract Drift 추가 (P3)
- **다음 재평가 시점**: Phase 2 종료 시 — 새 contract 추가/변경 시 audit_naming이 실제로 신규 drift를 잡았는지 회고
- **연관 Skill / Contract**: harness-audit, phase-start, qa-check, contract-change, audit_naming.ps1

### Pattern P-SLICE-001: Simplest Slice 3회 압축 원칙 채택

- **유형**: 반복 성공 (Phase 1 7 Slices 모두 적용, 회귀 0)
- **최초 식별**: 2026-05-26 (Phase 1)
- **관련 회고**: meta/retrospectives/phase-1.md §잘된 것
- **요약**: "이 phase 작동 가능 최소 단위" 도출 시 "더 줄일 수 있는가?"를 3회 반복 → 디버깅·rollback 비용 최소화. Phase 1 Slice 1을 5 파일로 시작 → 7 Slices로 점진 확장.
- **권장 대응**: phase-start v1.1.0 §6.2 채택 완료 — 후속 Phase 모두 적용
- **연관 Skill / Contract**: phase-start §6.2

### Pattern P-GRACEFUL-001: 외부 의존성 실패 graceful 패턴이 testability ↑

- **유형**: 운영 인사이트 (반복 성공)
- **최초 식별**: 2026-05-26 (Phase 1 Slice 4/5)
- **관련 회고**: meta/retrospectives/phase-1.md §배운 것
- **요약**: 외부 의존성(RAG/DB/LLM) 실패 시 사용자 차단 0건 + 응답 200 + validation.warnings로 자기설명. 부작용: pytest로 모든 실패 케이스 mock 자동화 가능 → testability ↑.
- **권장 대응**:
  - Phase 4+ MOA Lite revise loop도 동일 패턴 채택
  - error_response_contract.md에 graceful 패턴 가이드 명시
- **연관 Skill / Contract**: error_response_contract, agent_io_contract

### Pattern P-FOLDER-PARALLEL-001: sub-agent 병렬 dispatch 폴더 분리 표준

- **유형**: 반복 성공 (Phase 1 Wave 1/4 + Phase 2 Wave 3 적용, 충돌 0)
- **최초 식별**: 2026-05-26 (Phase 1)
- **관련 회고**: meta/retrospectives/phase-1.md §잘된 것, meta/retrospectives/phase-2.md §잘된 것
- **요약**: 같은 폴더 변경 sub-agent 병렬은 충돌 위험. 다른 폴더(backend/ vs apps/web/)는 충돌 0. multi_slice_plan.md §2 충돌 분석 매트릭스 패턴 효과적.
- **한계 (Phase 2 발견)**: "같은 파일 다른 sub-section" 케이스는 미커버 — P-AGENT-SCOPE-001 참조. 본 패턴은 "다른 폴더" 분리 케이스만 효과 보장.
- **권장 대응**: phases/active/{phase}/multi_slice_plan.md template에 충돌 분석 매트릭스 섹션 표준화 + sub-section lock 정책 (P-X1 적용 후)
- **연관 Skill / Contract**: phase-start §6.3 Surgical Scope, multi_slice_plan template

### Pattern P-AGENT-SCOPE-001: sub-agent forbidden 영역 침범 (sub-section)

- **유형**: 반복 실패 (잠재) → **Mitigated (2026-05-28)** — Phase 3 P-X1 적용으로 5/5 PASS, 0건 재발
- **Mitigation 증거**: phase-3 회고 §P-X1 효과 측정 + P-X1-EFFECT-001 패턴 등록. component_map.md 6연속 0줄 보존
- **유형 (이전)**: 1회 발생, 큰 위험은 미발현 (무충돌)
- **최초 식별**: 2026-05-27 (Phase 2 Wave 3)
- **관련 회고**: meta/retrospectives/phase-2.md §근본 원인 (5 Whys)
- **요약**: Wave 3 Slice 3 sub-agent (Direction Approval)가 forbidden 명시된 `QuickInputCard` sub-section을 `component_map.md`에 추가. Slice 4 (Quick) 작업 영역 침범. 결과적으로 동일 내용 + append-only로 무충돌이었으나, 의도 다를 시 conflict / 데이터 손실 / 내용 불일치 가능. P-FOLDER-PARALLEL-001 (다른 폴더 분리)의 한계 케이스 — "같은 파일 다른 sub-section" 케이스에서는 폴더 분리가 보호하지 않음.
- **증거**:
  - Slice 3 commit (daa3e18) diff: `component_map.md`에 `+## DirectionApprovalCard` + `+## QuickInputCard` 2개 sub-section 추가
  - Slice 4 commit (941b403): `component_map.md` 0줄 수정 (4 신규 파일만 commit)
  - Slice 3 commit message: "Slice 4 영역 0줄 수정"으로 잘못 자기 보고 — 자기 검증 절차 부재
- **권장 대응**:
  - sub-agent 프롬프트에 forbidden enforcement 강화 (capital + 반복 + "본인 staged 외 변경 없음 자기 검증" 절차 강제)
  - main session에서 sub-agent 완료 후 `git diff HEAD~1 HEAD --stat` 자체 검증
  - (선택) worktree isolation (P-X4 deferred)
- **상태**: meta/proposals/2026-05-27_phase-2-retrospective-proposals.md §P-X1 등록 (Phase 3 진입 전 사용자 검토 필수)
- **재평가 시점**: Phase 3 코드 phase 진행 중 (같은 .tsx 파일 sub-section 동시 수정 위험 ↑) — P-X1 적용 후 효과 측정
- **연관 Skill / Contract**: phase-start §6.3, multi_slice_plan template, sub-agent prompt format

### Pattern P-X1-EFFECT-001: P-X1 §SELF-VERIFICATION 13연속 PASS 효과 측정 (update 2026-05-28 Phase 4.5)

- **유형**: 반복 성공 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 = **13 Slice 누적**, 0 deviation)
- **최초 식별**: 2026-05-28 (Phase 3) — Phase 4에서 9연속 update — Phase 4.5에서 **13연속 누적 update**
- **관련 회고**: meta/retrospectives/phase-3.md + meta/retrospectives/phase-4.md + meta/retrospectives/phase-4.5.md §P-X1 13연속 효과 측정
- **요약**: Phase 2 회고 P-AGENT-SCOPE-001 대응안 P-X1을 Phase 3 pre-entry 적용 → Phase 3 5/5 PASS → Phase 4 4/4 PASS → Phase 4.5 4/4 PASS = **13연속**. Phase 4.5는 mini-phase 형식(4 Slice 모두 sub-agent dispatch)에서도 0건 재발. **proposal → 적용 → 3 phase 누적 효과 측정 사이클 완성**.
- **증거 (Phase 3 + Phase 4 + Phase 4.5)**:
  - Slice 1~13 (Phase 3 5 + Phase 4 4 + Phase 4.5 4) 모든 sub-agent commit message에 "§SELF-VERIFICATION PASS / 0 out-of-scope edits" 명시
  - `git diff f50bc74..HEAD -- harness/apps/web/component_map.md` → **0줄 (19연속, Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4)**
  - `git diff 76b4d2c..HEAD -- harness/apps/web/components/PlanCard.tsx` → **0줄 (9연속, Phase 4 4 + Phase 4.5 5 — 사용자 결정 6-a 계승)**
  - phases/active/phase-3-pwa-impl/deviations.md → 0건 entry
  - phases/active/phase-4-fastapi-extension/deviations.md → 1건 entry (D-1 audit drift, intended → Slice 4 해소)
  - phases/active/phase-4.5-critic-revise-loop/deviations.md → 0건 entry
- **권장 대응**:
  - Phase 5+ 모든 sub-agent prompt에 §SELF-VERIFICATION 의무 유지
  - phase-start v1.3.0 §6.3 의무 절차 보존
  - main session sub-agent 완료 후 `git diff --stat` 검증 의무 절차 보존
- **재평가 시점**: Phase 5+ DB/Auth phase (Supabase + RLS 새 영역 도입) — 재발 시 P-X4 (worktree isolation) 재검토 트리거
- **연관 Skill / Contract**: phase-start v1.3.0 §6.3, P-AGENT-SCOPE-001 (mitigated 13연속), P-GPT-REVIEW-001 (Phase 4 신규), P-VALIDATION-FORMAL-001 (Phase 4.5 신규)

### Pattern P-THIN-VERTICAL-001: Thin Vertical Slice 효과 (코드 phase entry 표준)

- **유형**: 반복 성공 (Phase 3 Slice 2 → Slice 3 패턴 복제 성공)
- **최초 식별**: 2026-05-28 (Phase 3)
- **관련 회고**: meta/retrospectives/phase-3.md §잘된 것 3
- **요약**: Phase 3 Slice 2를 Discovery Step 1 end-to-end (component + page + state + token + Tailwind 연결 = 5 파일)로 정의 → Slice 3 (Step 2~7 확장)이 dynamic route + 패턴 복제만으로 진행. drift 0건 + §SELF-VERIFICATION PASS. phase-start §6.2 Simplest Slice의 강화 형태 — "한 페이지 통째 작동 후 확장".
- **핵심 메커니즘**:
  1. **end-to-end working slice**: 1 페이지 (`/new/discovery/step/1`)가 컴포넌트 / state / API mock / Tailwind class 모두 작동
  2. **패턴 복제 단순화**: Slice 3은 dynamic route (`/step/[n]`)로 Step 1 코드 패턴 그대로 적용
  3. **drift 자동 회피**: spec ↔ 코드 일치성 Slice 2에서 한 번 확보 → Slice 3+ 자동 상속
- **권장 대응**:
  - Phase 4+ 첫 코드 작업 단계 (예: Phase 4 Slice 2~3, 3-plan generate endpoint)에서 동일 패턴 적용 — "한 endpoint 통째 작동 후 확장"
  - phase-start v1.3.0 §6.2 Simplest Slice 보강 후보 (Y-X 흡수 가능)
- **연관 Skill / Contract**: phase-start §6.2 Simplest Slice, P-SLICE-001 (Phase 1)

### Pattern P-GPT-REVIEW-001: 외부 LLM 검토 (GPT) 채택 효과 — scope 축소 + 시간 절감

- **유형**: 반복 성공 (Phase 4 첫 적용, 6→4 Slices)
- **최초 식별**: 2026-05-28 (Phase 4)
- **관련 회고**: meta/retrospectives/phase-4.md §GPT 검토 채택 효과 측정 + §잘된 것 2
- **요약**: Phase 4 원안 6 Slices (Critic revise + SSE + 4-layer 재정의 본격 포함) → 사용자 외부 GPT 검토 후 4 Slices로 축소 (revise/SSE/4-layer Phase 4.5/5+ 이관). 시간 18~26h → 6~8h (▼66%), Slices 6→4 (▼33%), scope 명확화 (ADR-014 + ADR-015 명문화), 회귀 위험 ↓. multi-llm-validation Skill 정식 호출은 아니었으나 패턴은 동일.
- **핵심 메커니즘**:
  1. **외부 LLM 검토** (GPT) — 단일 모델 (Claude) 편향 회피
  2. **채택 결정 후 사용자 7개 결정**으로 세부 조율 (4-b multi-model / 5-a Phase 8+ 제거 / 6-a PlanCard 무수정 등)
  3. **Slice 분해 후 deferred 명세** (D6/D7/D8/D3/D4/D2/Phase 1 endpoint 제거) — 각 항목 권장 다음 phase 명시
- **증거**:
  - entry commit 76b4d2c message + scope.md §GPT 검토 항목
  - acceptance.md A1~A10 모두 4 Slices 범위에서 충족
  - 실측 시간 ~6~8h (acceptance.md 추정 7~11h 내, 원안 18~26h 대비 ▼66%)
- **권장 대응**:
  - 후속 큰 phase (Phase 5+) 진입 전 multi-llm-validation Skill 정식 호출 권장 (meta/validations/ 누적)
  - 외부 검토 결과 채택 시 entry commit message + scope.md에 명시 (재현 가능성 ↑)
  - 채택 항목별 ADR 작성 (Phase 4 ADR-014/015 패턴 복제)
- **연관 Skill / Contract**: multi-llm-validation Skill, ADR-014 (endpoint migration), ADR-015 (3-plan multi-model)
- **누적 외부 검토 채택 횟수**: 3회 (Phase 2 GPT 80점 채택 → Phase 3 P-X1 적용 → Phase 4 GPT 6→4 채택)

### Pattern P-DESIGN-LAYERED-001: 4-layer 4개 + Variants Bank 3개 minimal 정책의 변경성 보장 효과

- **유형**: 반복 성공 (Phase 2 Slice 1~5 적용, 변경성 시뮬레이션 5/5 PASS)
- **최초 식별**: 2026-05-27 (Phase 2)
- **관련 회고**: meta/retrospectives/phase-2.md §잘된 것 1
- **요약**: ADR-010 (4-layer 컴포넌트 4개 한정) + ADR-011 (Variants Bank 3 컴포넌트 한정) 정책을 Slice 1 design system foundation에서 명문화 → Slice 2~5 sub-agent가 자발적으로 minimal entry 유지. over-engineering 회피와 변경 가능성 보장을 동시에 달성. 변경성 시뮬레이션 5/5 PASS (design_handoff.md §6.1) — design system 도입 효과 실증.
- **핵심 메커니즘**:
  1. **literal 값 0 정책** (`component_contract.md` Visual layer 강제) — tokens.* 참조 강제로 시나리오 1 (token 변경) 1 파일로 압축
  2. **Variants Bank chosen toggle** — 시나리오 2/4 (variant swap)가 1~2 파일 수정으로 압축, Phase 4+ A/B 인프라 자연 흡수
  3. **ADR 진입 시 작성** — Slice 1에서 ADR-010/011 작성 → 후속 Slice의 self-regulation 효과
- **권장 대응**:
  - Phase 3+ 후속 phase에서 같은 minimal 정책 유지 (component 추가 시 4-layer 4개 / Variants 3개 한정 재검토)
  - Phase 4 PlanComparisonCard 추가 시 ADR 갱신 후 4-layer 작성
  - Phase 11+ dark mode / i18n 시 본 패턴 효과 재측정 (변경성 시뮬레이션 회귀)
- **연관 Skill / Contract**: design-review, component_contract.md, variant_format.md, replaceability_score.md, ADR-010, ADR-011, design_handoff.md

### Pattern P-X2-EFFECT-001: 변경성 시뮬 자동 게이트 효과 (Phase 4.5 첫 트리거)

- **유형**: 반복 성공 (Phase 4.5 첫 적용, scenario_simulation.ps1 5/5 PASS)
- **최초 식별**: 2026-05-28 (Phase 4.5 Slice 4 — 첫 자동 게이트 작동)
- **관련 회고**: meta/retrospectives/phase-4.5.md §잘된 것 3 + §P-X2-EFFECT-001
- **요약**: Phase 4 회고에서 P-X2 (변경성 시뮬 phase-complete 자동 게이트) 제안 → Phase 4.5 진입 시 사용자가 채택 결정. Phase 4.5 Slice 1에서 phase-complete SKILL.md v1.1.0 → v1.2.0 (§1.6) + `scripts/scenario_simulation.ps1` 신규 작성. Slice 4에서 phase-complete 자동 호출 → 변경성 시뮬 **5/5 PASS** 확인.
- **핵심 메커니즘**:
  1. **phase-complete SKILL.md §1.6 자동 호출**: Phase 종료 시 `scripts/scenario_simulation.ps1` 1단계 실행 (PowerShell 5.1 호환, 1초 미만)
  2. **5 시나리오 fixed (Phase 4.5 baseline)**: PlanCard visual tone / component_map entry / wrapper UI ring / revise loop max / recommended_idx disable
  3. **판정 기록**: PASS → PROJECT_STATE.md yaml `phase_X_changeability_simulation: 5/5 PASS (auto-gate)` / FAIL → Phase 종료 차단 + 회고 §개선 제안
- **효과 측정 (Phase 4.5)**:
  - 기존 manual walkthrough: ~30분 / phase × 5 phase = ~2.5h
  - 자동 게이트: ~1초 / phase × 5 phase = 5초 (**▼ ~99% 시간**)
  - 시나리오 누락 위험 ↓ (Phase 4까지 4/5 + 1 WARN 수준 → Phase 4.5 5/5 일관성 ↑)
  - 5 시나리오 모두 file count 기반 grep 휴리스틱 — 깊이는 보통, 도입 비용 ▼
- **다음 단계**:
  - Phase 5+에서 시나리오 1~5를 환경별로 분기 (DB 도입 시 시나리오 4/5 갱신)
  - 시나리오 추가/수정 절차를 contract-change Skill로 정식화 (Phase 6+ 권장)
  - 시나리오 표현력 보강 (file count → stub patch + rollback 시뮬레이션) — 회고 §개선 제안 4
- **권장 대응**:
  - Phase 5+ 모든 phase 종료 시 phase-complete v1.2.0 §1.6 호출 의무 유지
  - 시나리오 변경 시 ADR 작성 (Phase 4.5 ADR-016/017 패턴 복제)
- **연관 Skill / Contract**: phase-complete v1.2.0 §1.6, scenario_simulation.ps1, P-X1-EFFECT-001 (13연속과 함께 회귀 차단 baseline)
- **관련 회고**:
  - meta/retrospectives/phase-4.5.md
  - meta/proposals/2026-05-28_phase-4-retrospective-proposals.md §P-X2 (채택 권장)

### Pattern P-VALIDATION-FORMAL-001: multi-llm-validation formal self + 외부 분리 패턴 (Phase 4.5 첫 트리거)

- **유형**: 반복 성공 (Phase 4.5 첫 적용, formal self V1~V4 PASS + external placeholder 분리)
- **최초 식별**: 2026-05-28 (Phase 4.5 Slice 1 — 첫 formal 트리거)
- **관련 회고**: meta/retrospectives/phase-4.5.md §잘된 것 2 + §P-VALIDATION-FORMAL-001
- **요약**: 사용자 결정 "검증 모델은 너가 직접 (Claude Code, 혹은 codex가 지침 참고하면서 자가 검증), 외부 검증은 따로 작성되도록 할 것" → multi-llm-validation Skill formal 트리거를 다음 패턴으로 정의:
  1. **Self validation**: Claude Code가 지침(CLAUDE.md, contracts, eval, patterns)을 참조하여 자가 검증 → `meta/validations/{date}_{phase}_self.md`
  2. **External validation**: 외부 LLM(GPT/Gemini) 검증은 placeholder로 별도 파일 → `meta/validations/{date}_{phase}_external.md` (사용자가 외부에서 진행 후 채움)
  3. 두 결과의 차이 항목 발견 시 phase notes.md에 기록 + 회고 §개선 제안 반영
- **효과 측정 (Phase 4.5)**:
  - 큰 phase 진입 시 단일 모델 편향 회피 baseline 확립
  - 외부 검증 의무화 부담 없이 분리 가능 → 사용자가 외부에서 진행 여부를 phase별로 결정 가능
  - `meta/validations/` 폴더 누적 시작 → 추후 audit / 회고 / pattern 추출 가능
  - Phase 4.5 self V1~V4 4/4 PASS (지침 정합성, contract 정합성, eval 정합성, 패턴 정합성)
- **다음 단계**:
  - Phase 5 (큰 phase, DB/Auth) 진입 전 동일 패턴 적용 (사용자 결정 의무, external 채움 권장)
  - skill_usage_log.md에 formal vs informal 트리거 구분 기록 (이미 Phase 4.5 entry에서 구분)
  - Phase 5+ external 채움 시 V1~V4 cross-check (self vs external 차이 회고 §개선 제안)
- **권장 대응**:
  - Phase 5+ 모든 큰 phase 진입 전 self.md + external.md 2 파일 생성 의무
  - phase entry commit message에 "multi-llm-validation formal self PASS" 명시 (재현 가능성 ↑)
- **연관 Skill / Contract**: multi-llm-validation Skill, P-GPT-REVIEW-001 (informal GPT 검토 — Phase 4 baseline)
- **관련 회고**:
  - meta/retrospectives/phase-4.5.md
  - meta/validations/2026-05-28_phase-4.5-pre-entry_self.md (V1~V4 PASS)
  - meta/validations/2026-05-28_phase-4.5-pre-entry_external.md (placeholder)
