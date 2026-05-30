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

### Pattern P-X1-EFFECT-001: P-X1 §SELF-VERIFICATION 47연속 PASS 효과 측정 (update 2026-05-31 Phase 9.5)

- **유형**: 반복 성공 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6 + Phase 9.5 5 = **47 Slice 누적**, 0 deviation)
- **최초 식별**: 2026-05-28 (Phase 3) — Phase 4에서 9연속 update — Phase 4.5에서 13연속 update — Phase 6에서 17연속 update — Phase 5에서 22연속 update — Phase 5.5에서 26연속 update — Phase 7에서 31연속 update — Phase 8에서 36연속 update — Phase 9에서 42연속 update — Phase 9.5에서 **47연속 누적 update**
- **관련 회고**: meta/retrospectives/phase-3.md + meta/retrospectives/phase-4.md + meta/retrospectives/phase-4.5.md + meta/retrospectives/phase-6.md + meta/retrospectives/phase-5.md + meta/retrospectives/phase-5.5.md + meta/retrospectives/phase-7.md + meta/retrospectives/phase-8.md + meta/retrospectives/phase-9.md + meta/retrospectives/phase-9.5.md §P-X1 47연속 효과 측정
- **요약**: Phase 2 회고 P-AGENT-SCOPE-001 대응안 P-X1을 Phase 3 pre-entry 적용 → Phase 3 5/5 → Phase 4 4/4 → Phase 4.5 4/4 → Phase 6 4/4 → Phase 5 5/5 → Phase 5.5 4/4 → Phase 7 5/5 → Phase 8 5/5 → Phase 9 6/6 → Phase 9.5 5/5 = **47연속 PASS**. Phase 9.5는 eval module 신규 + critic.py/schemas deprecated 제거 + frontend canonical 전환을 건드리는 delicate phase 임에도 0건 재발 — Slice별 폴더/파일 격리 + forbidden 명시 + ★ 제거 순서 강제(eval→검증→제거)로 baseline 침범 0. **frontend canonical 전환 slice(Slice 4)에서도 lib/types.ts + page.tsx inline으로 PlanCard·component_map 0줄 유지** (P-X1의 frontend 확장). **proposal → 적용 → 10 phase 누적 효과 측정 사이클 + large/보안/consolidation/RAG/orchestration-refactor/feedback-frontend/eval-deprecated-removal 모두 확장 입증**.
- **증거 (Phase 3 + Phase 4 + Phase 4.5 + Phase 6 + Phase 5 + Phase 5.5 + Phase 7 + Phase 8 + Phase 9 + Phase 9.5)**:
  - Slice 1~47 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6 + Phase 9.5 5) 모든 sub-agent commit message에 "§SELF-VERIFICATION PASS / 0 out-of-scope edits" 명시
  - `git diff f50bc74..HEAD -- harness/apps/web/component_map.md` → **0줄 (45연속, Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 + Phase 9.5 5)**
  - `git diff 76b4d2c..HEAD -- harness/apps/web/components/PlanCard.tsx` → **0줄 (35연속, Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 + Phase 9.5 5 — 사용자 결정 6-a 계승, frontend canonical 전환에서도 wrapper로 0줄)**
  - phases/active/phase-3-pwa-impl/deviations.md → 0건 entry
  - phases/active/phase-4-fastapi-extension/deviations.md → 1건 entry (D-1 audit drift, intended → Slice 4 해소)
  - phases/active/phase-4.5-critic-revise-loop/deviations.md → 0건 entry
  - phases/active/phase-6-output-schema-stabilization/deviations.md → 0건 entry
  - phases/active/phase-5-db-auth/deviations.md → 0건 entry (audit_page_component 2 drift는 의도된 신규 Slice 3 — WARN 허용)
  - phases/active/phase-5.5-legacy-db-consolidation/ → 0건 (consolidation mini-phase)
  - phases/active/phase-7-rag-lite/ → 0건 (large RAG phase, audit_page_component 2 drift는 Phase 5 baseline 계승 WARN)
  - phases/active/phase-8-moa-lite/ → 0건 (large orchestration phase, behavior-preserving 의도된 2 version assertion 제외 baseline 수정 0, audit_page_component 2 drift는 Phase 5 baseline 계승 WARN)
  - phases/archive/phase-9-result-feedback/ → 0건 (large feedback phase, normalize wiring additive Optional baseline 수정 0, frontend slice에서도 PlanCard·component_map 0줄, audit_page_component 2 drift는 Phase 5 baseline 계승 WARN)
  - phases/archive/phase-9.5-eval-run/ → 0건 (eval mini-phase, deprecated 0–5 제거는 eval 안전망 + 의도된 test_critic deprecated-fallback delta만, frontend canonical 전환에서도 PlanCard·component_map 0줄, audit_page_component 2 drift는 Phase 5 baseline 계승 WARN)
- **권장 대응**:
  - Phase 10+ 모든 sub-agent prompt에 §SELF-VERIFICATION 의무 유지
  - phase-start v1.3.0 §6.3 의무 절차 보존
  - main session sub-agent 완료 후 `git diff --stat` 검증 의무 절차 보존
- **재평가 시점**: Phase 10 (MVP 통합 + P-AUX-2 agent 실 구현) — agents/* 신규 추가 시
- **연관 Skill / Contract**: phase-start v1.3.0 §6.3, P-AGENT-SCOPE-001 (mitigated 47연속), P-GPT-REVIEW-001 (Phase 4 + Phase 6 두 번째 적용 + Phase 5.5 세 번째 mini-phase 정신 계승), P-VALIDATION-FORMAL-001 (Phase 4.5 + Phase 6 + Phase 5 + Phase 7 + Phase 8 + Phase 9 + Phase 9.5 일곱 번째 입증), P-CRITIC-CANONICAL-001 (Phase 6 → Phase 8 conservative adapter → Phase 9 normalize wiring canonical live → Phase 9.5 deprecated 0–5 Full 제거로 단계적 축소 완료), P-CONTRACT-FIRST-001 (Phase 6 후보 + Phase 5 db_schema.md + Phase 7 rag_data_contract §18 + Phase 8 CC-003 + Phase 9 CC-004 + Phase 9.5 CC-005 누적 6회), P-RLS-001 (Phase 5 신규 + Phase 9 feedback/selection), P-SSE-001 (Phase 5 신규 + Phase 8 progress_store 실 stage), P-SECURITY-REVIEW-001 (Phase 5 신규 후보 + Phase 9 두 번째 정식 — 강화), P-LEGACY-CONSOLIDATION-001 (Phase 5.5 + Phase 7 누적 2회), P-RAG-5STAGE-001 (Phase 7 신규 후보 + Phase 9 candidate pending 적재 정합), P-RAG-GRACEFUL-001 (Phase 7 신규 후보), P-MOA-ORCHESTRATOR-001 (Phase 8 신규 후보 + Phase 9 orchestrator 확장), P-BEHAVIOR-PRESERVING-001 (Phase 8 신규 후보 + Phase 9 additive wiring + Phase 9.5 deprecated 제거 eval 동일 입증), P-FEEDBACK-LOOP-001 (Phase 9 신규 후보), P-CANONICAL-WIRING-001 (Phase 9 신규 후보 + Phase 9.5 deprecated 완전 제거로 wiring 단계 완료), **P-EVAL-HARNESS-001 (Phase 9.5 신규 후보)**, **P-DEPRECATED-REMOVAL-001 (Phase 9.5 신규 후보)**

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

### Pattern P-VALIDATION-FORMAL-001: multi-llm-validation formal self + 외부 분리 패턴 (Phase 4.5 첫 + Phase 6 두 번째 + Phase 5 세 번째 정식 확정 + Phase 5.5 self-strengthen V-form sub-pattern + Phase 7 네 번째 + Phase 8 다섯 번째 + Phase 9 여섯 번째 + Phase 9.5 일곱 번째 입증)

- **유형**: 반복 성공 (Phase 4.5 첫 V1~V4 + Phase 6 두 번째 V1~V5 + Phase 5 세 번째 V1~V6 + Phase 7 네 번째 V1~V7 + Phase 8 다섯 번째 V1~V7 + Phase 9 여섯 번째 V1~V7 + Phase 9.5 일곱 번째 V1~V7 = 7회 누적, 정식 패턴 확정 + Phase 5.5 self-strengthen V-form sub-pattern 보존)
- **최초 식별**: 2026-05-28 (Phase 4.5 Slice 1 — 첫 formal 트리거)
- **두 번째 입증**: 2026-05-29 (Phase 6 Slice 1 — 두 번째 formal 트리거)
- **세 번째 입증 (정식 확정)**: 2026-05-29 (Phase 5 Slice 1 — 세 번째 formal 트리거, V6 large + 보안 phase 추가: Supabase 채택 / JWT / RLS / SSE / revise_history JSONB / canonical DB)
- **Self-strengthen V-form sub-pattern (Phase 5.5 신규)**: 2026-05-29 (Phase 5.5 Slice 3 — external placeholder 3개 모두 self-question + self-answer 형식으로 강화, V-form 합의 추정 PASS, 외부 검토 비교 baseline 확립)
- **네 번째 입증 (Phase 7 RAG)**: 2026-05-29 (Phase 7 Slice 1 — 네 번째 formal 트리거, V7 RAG 영역 추가: ADR-024 5단계 채택 / chunk 512 tokens / top-k=5 threshold=0.7 / OpenAI text-embedding-3-small / graceful 5종 marker / LLM Wiki vs RAG 분리 / hybrid 승인 정책)
- **다섯 번째 입증 (Phase 8 MOA orchestration)**: 2026-05-29 (Phase 8 Slice 1 — 다섯 번째 formal 트리거, V7 MOA orchestration 영역: orchestrator 추출 behavior-preserving / ProgressSink Null default 회귀 0 / SSE progress_store 브릿지 / Critic conservative adapter Phase 6 canonical 불변 / prompt_registry semver / prompt_id-version 단일 출처 정합 / SSE best-effort single-process)
- **여섯 번째 입증 (Phase 9 selection/feedback)**: 2026-05-29 (Phase 9 Slice 1 — 여섯 번째 formal 트리거, V7 selection/feedback 영역: selection/feedback 실 plans 정합 / normalize_to_canonical wiring 회귀 0 / Brand Memory 준비 경계 (agent 미구현 Phase 10+) / 피드백 reason PII 마스킹 / repo graceful PlansRepo 패턴 / 피드백 UI wrapper PlanCard·component_map 0줄 / feedback→candidate pending 적재)
- **일곱 번째 입증 (Phase 9.5 eval-run)**: 2026-05-31 (Phase 9.5 Slice 1 — 일곱 번째 formal 트리거, V7 eval-run 영역: eval mock-deterministic (CI 가능 비용 0) / golden_set markdown→구조화 파싱 (실 11 케이스 단일 출처) / revise effect metric (attempt별 canonical 0–1 delta) / deprecated 제거 경계 (run_critic 0–5 불변 P-007) / 제거 순서 (eval→검증→제거) / 임계값 게이트 (schema 100% / 점수 ±0.3 / 광고 / 차단 단어) / frontend types CriticEvaluation 정합)
- **관련 회고**: meta/retrospectives/phase-4.5.md + meta/retrospectives/phase-6.md + meta/retrospectives/phase-5.md + meta/retrospectives/phase-5.5.md + meta/retrospectives/phase-7.md + meta/retrospectives/phase-8.md + meta/retrospectives/phase-9.md + meta/retrospectives/phase-9.5.md
- **요약**: 사용자 결정 "검증 모델은 너가 직접 (Claude Code, 혹은 codex가 지침 참고하면서 자가 검증), 외부 검증은 따로 작성되도록 할 것" → multi-llm-validation Skill formal 트리거를 다음 패턴으로 정의:
  1. **Self validation**: Claude Code가 지침(CLAUDE.md, contracts, eval, patterns)을 참조하여 자가 검증 → `meta/validations/{date}_{phase}_self.md`
  2. **External validation**: 외부 LLM(GPT/Gemini) 검증은 placeholder로 별도 파일 → `meta/validations/{date}_{phase}_external.md` (사용자가 외부에서 진행 후 채움)
  3. 두 결과의 차이 항목 발견 시 phase notes.md에 기록 + 회고 §개선 제안 반영
- **효과 측정 (Phase 4.5 + Phase 6 + Phase 5 + Phase 7 누적)**:
  - 큰 phase 진입 시 단일 모델 편향 회피 baseline 확립
  - 외부 검증 의무화 부담 없이 분리 가능 → 사용자가 외부에서 진행 여부를 phase별로 결정 가능
  - `meta/validations/` 폴더 누적 → 추후 audit / 회고 / pattern 추출 가능
  - **V dimension 점진 확장**: Phase 4.5 V1~V4 (지침/contract/eval/패턴) → Phase 6 +V5 (frontend types ↔ backend 1:1 매핑) → Phase 5 +V6 (보안 + DB 영속 정합성) → Phase 7 +V7 (RAG architecture — chunk 512 + retrieval threshold + LLM Wiki vs RAG 분리 + hybrid 승인) → Phase 8 V7 재사용 (MOA orchestration — orchestrator 추출 behavior-preserving + ProgressSink + SSE 브릿지 + Critic conservative adapter + prompt semver) → Phase 9 V7 재사용 (selection/feedback — 실 plans 정합 + normalize wiring 회귀 0 + Brand Memory 준비 경계 + 피드백 PII + repo graceful + 피드백 UI wrapper + feedback→candidate 적재)
- **다음 단계**:
  - Phase 10 통합 등 큰 phase 진입 시 동일 패턴 적용
  - 정식 확정 (7회 누적, Phase 7 + Phase 8 + Phase 9 + Phase 9.5 입증) — 모든 큰 phase 의무 baseline
  - external 채움 누적 시 self vs external 차이 분석 회고 별도 (Phase 11+)
- **권장 대응**:
  - 모든 큰 phase 진입 전 self.md + external.md 2 파일 생성 의무
  - phase entry commit message에 "multi-llm-validation formal self PASS" 명시 (재현 가능성 ↑)
- **연관 Skill / Contract**: multi-llm-validation Skill, P-GPT-REVIEW-001 (informal GPT 검토 — Phase 4 baseline)
- **관련 회고**:
  - meta/retrospectives/phase-4.5.md
  - meta/retrospectives/phase-6.md
  - meta/retrospectives/phase-5.md (세 번째 트리거 — 정식 확정)
  - meta/retrospectives/phase-5.5.md (self-strengthen V-form sub-pattern 신규)
  - meta/retrospectives/phase-7.md (네 번째 트리거 — V7 RAG architecture)
  - meta/validations/2026-05-28_phase-4.5-pre-entry_self.md (V1~V4 PASS)
  - meta/validations/2026-05-28_phase-4.5-pre-entry_external.md (placeholder → Phase 5.5 self-strengthen)
  - meta/validations/2026-05-29_phase-6-pre-entry_self.md (V1~V5 PASS)
  - meta/validations/2026-05-29_phase-6-pre-entry_external.md (placeholder → Phase 5.5 self-strengthen)
  - meta/validations/2026-05-29_phase-5-pre-entry_self.md (V1~V6 PASS — 세 번째)
  - meta/validations/2026-05-29_phase-5-pre-entry_external.md (placeholder → Phase 5.5 self-strengthen)
  - meta/validations/2026-05-29_phase-7-pre-entry_self.md (V1~V7 PASS — 네 번째)
  - meta/validations/2026-05-29_phase-7-pre-entry_external.md (placeholder)
  - meta/validations/2026-05-29_phase-8-pre-entry_self.md (V1~V7 PASS — 다섯 번째)
  - meta/validations/2026-05-29_phase-8-pre-entry_external.md (placeholder)
  - meta/retrospectives/phase-8.md (다섯 번째 트리거 — V7 MOA orchestration)
  - meta/validations/2026-05-29_phase-9-pre-entry_self.md (V1~V7 PASS — 여섯 번째)
  - meta/validations/2026-05-29_phase-9-pre-entry_external.md (placeholder)
  - meta/retrospectives/phase-9.md (여섯 번째 트리거 — V7 selection/feedback + normalize wiring + Brand Memory 준비)
  - meta/validations/2026-05-31_phase-9.5-pre-entry_self.md (V1~V7 PASS — 일곱 번째)
  - meta/validations/2026-05-31_phase-9.5-pre-entry_external.md (placeholder)
  - meta/retrospectives/phase-9.5.md (일곱 번째 트리거 — V7 eval mock-deterministic + deprecated 제거 경계 + 임계값 게이트)

### Pattern P-LEGACY-CONSOLIDATION-001: 다중 layer 공존 시 옵션 A 패턴 (Phase 5.5 신규 후보 + Phase 7 두 번째 입증)

- **유형**: 반복 성공 (Phase 5.5 첫 적용 + Phase 7 두 번째 적용 누적 2회, legacy DB Phase 1 supabase_client + Phase 5 client/plans_repo 공존 → deprecated note + DeprecationWarning + Phase 7+ 지연 통합. Phase 7 두 번째: Phase 1 legacy rag/retriever + rag/fallback (psycopg) ↔ Phase 7 신규 rag/retrieval (Supabase RPC) 별개 공존 → Phase 11+ Custom RAG 시점 자연 통합 검토)
- **최초 식별**: 2026-05-29 (Phase 5.5 Slice 2 — 옵션 A 채택, ADR-023)
- **두 번째 입증**: 2026-05-29 (Phase 7 Slice 4 — agents/rag.py Phase 1 baseline 보호 + Phase 7 통합 wrapper 별개 공존, ADR-024 §B 명시)
- **관련 회고**: meta/retrospectives/phase-5.md §개선 제안 §1 (legacy DB 통합 mini-phase) + meta/retrospectives/phase-5.5.md §잘된 것 4 + meta/retrospectives/phase-7.md §잘된 것 6 + §P-LEGACY-CONSOLIDATION-001
- **요약**: Phase 5에서 발견된 "Phase 1 legacy `db/supabase_client.py` + Phase 5 신규 `db/client.py` + `plans_repo` 공존" 문제 → Phase 5.5 mini-phase에서 3가지 옵션 (A 공존+deprecation / B 즉시 통합 / C legacy 완전 제거) 중 **옵션 A 채택**:
  1. **공존 유지**: legacy 파일 인터페이스 그대로 + Phase 5 신규 layer canonical 우선
  2. **Deprecated docstring + DeprecationWarning**: legacy 호출 시 `warnings.warn(DeprecationWarning, ...)` 발행 + `pytest.warns(DeprecationWarning)` capture
  3. **Grace period 명시**: "Phase 7+ RAG 통합 후 별도 mini-phase (Phase 7.5?)에서 실 통합" 명시 (ADR-023)
  4. **Backward-compat 100%**: 호출 사이트 변경 0건 + Phase 1 baseline 보호
  5. **__init__.py canonical 우선 export**: Phase 5 신규 layer 우선 + legacy 분리 export
- **효과 측정 (Phase 5.5 + Phase 7 누적)**:
  - 회귀 0: Phase 5.5 pytest 170 → 172 (+2 deprecation), Phase 7 pytest 172 → 223 (+51 신규) — 기존 테스트 모두 PASS
  - 호출 사이트 변경 0건 (Phase 1 + Phase 5 + Phase 7 baseline 동시 보호)
  - cognitive load 잔존 (공존) ↔ 즉시 통합 risk 회피 trade-off → Phase 11+ 자연 통합 시점 baseline 확립
  - smoke_test_phase_5 12/12 유지 (Phase 5.5) + smoke_test_phase_7 13/13 PASS (Phase 7, RAG 1 추가)
  - **두 번째 적용으로 정식 패턴 채택 임박** (Phase 11+ 실 통합 시점 효과 재측정 후 결정)
- **다음 단계**:
  - Phase 11+ Custom RAG 통합 후 별도 mini-phase에서 legacy rag/retriever + rag/fallback 완전 제거 검토 (Phase 7 회고 §개선 제안 §3)
  - 다른 다중 layer 공존 케이스 (Phase 8+ MOA agents 재구조화 / Phase 9+ feedback schema 등) 발견 시 동일 패턴 적용 가능성 검토
  - Phase 11+ 실 통합 시점 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - 다중 layer 공존 발견 시 3가지 옵션 (A 공존+deprecation / B 즉시 통합 / C legacy 완전 제거) 검토
  - 회귀 risk 최소화 우선 → 옵션 A 권장 (특히 baseline 보호가 critical할 때)
  - ADR로 결정 근거 + grace period + 실 통합 시점 명시 (Phase 5.5 ADR-023 패턴 복제)
  - DeprecationWarning + `pytest.warns(DeprecationWarning)` capture 의무화 (P-CRITIC-CANONICAL-001 정신 계승)
- **연관 Skill / Contract**: contract-change Skill, P-CRITIC-CANONICAL-001 (DeprecationWarning 패턴 계승), P-GRACEFUL-001 (회귀 0 정신 계승), ADR-023 (Phase 5.5 Legacy DB Consolidation 옵션 A)
- **관련 회고**:
  - meta/retrospectives/phase-5.md §개선 제안 §1
  - meta/retrospectives/phase-5.5.md
  - meta/retrospectives/phase-7.md §잘된 것 6 + §개선 제안 §3
  - docs/decisions/phase_5_5_legacy_db_consolidation.md (ADR-023)
  - docs/decisions/phase_7_rag_scope_evolution.md (ADR-024 §B 확대 지점 — Phase 11+ 실 통합 시점)
- **상태**: 신규 등록 후보 → **정식 채택 임박** (Phase 5.5 + Phase 7 누적 2회 적용 — Phase 11+ 실 통합 시점 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-RLS-001: RLS 정책 + 인증/익명 endpoint 분리 패턴 (Phase 5 신규)

- **유형**: 반복 성공 (Phase 5 첫 적용, RLS 4 정책 + auth.uid() + 2-hop subquery + NULLABLE auth_user_id)
- **최초 식별**: 2026-05-29 (Phase 5 Slice 4 — RLS 정책 0003_rls_policy.sql + ADR-021)
- **관련 회고**: meta/retrospectives/phase-5.md §잘된 것 2 + §P-RLS-001
- **요약**: Supabase RLS (Row Level Security) 정책을 DB-level 강제 + 인증/익명 endpoint 동시 운영을 위한 패턴:
  1. **auth.uid() 직접 매칭** (plans, video_projects 1-hop): `auth.uid() = auth_user_id` 정책
  2. **2-hop subquery 정책** (series via video_projects via brand_id): `auth.uid() = (SELECT auth_user_id FROM brands WHERE id = ...)` — series는 brand 통해 user 추적
  3. **anonymous endpoint 호환 NULLABLE**: Phase 1 `/api/v1/generate` 유지를 위해 `auth_user_id NULL` 허용 + RLS bypass (anonymous policy)
  4. **인증 endpoint 가드**: Phase 6+ 신규 endpoint에서 `auth_user_id IS NOT NULL` 가드 추가 권장
  5. **service_role 분리**: 백엔드 admin 작업만 service_role (API 응답에 노출 X)
- **효과 측정 (Phase 5)**:
  - 다른 user plan 접근 차단 4/4 PASS (test_rls.py)
  - anonymous /generate 호환 유지 (Phase 1 baseline 회귀 0)
  - DB-level 강제 → application bug 시에도 보호 (defense in depth)
- **다음 단계**:
  - Phase 6+ Legacy DB 통합 시 service_role boundary 명시
  - Phase 7+ Custom RAG schema 도입 시 동일 패턴 (rag_sources.auth_user_id RLS)
  - Phase 9+ pgtap 자동 검증 도입 (test_rls.py mock → pgtap real)
- **권장 대응**:
  - 새 user-scoped 테이블 추가 시 RLS 4 정책 (SELECT/INSERT/UPDATE/DELETE) 의무
  - 다른 테이블 reference 시 1-hop vs 2-hop subquery 결정 (cost vs cognitive load)
  - ADR로 정책 근거 영구 기록 (Phase 5 ADR-021 패턴 복제)
- **연관 Skill / Contract**: security-review Skill (영역 5 권한/RLS), contract-change Skill (db_schema.md), ADR-021 (Phase 5 RLS Policy)
- **관련 회고**:
  - meta/retrospectives/phase-5.md
  - meta/security_reviews/2026-05-29_phase-5-auth-rls.md (T2 위협 모델)
  - meta/security_reviews/2026-05-29_phase-5-final-verification.md (T2 PASS verify)
  - docs/decisions/phase_5_rls_policy.md (ADR-021)

### Pattern P-SSE-001: SSE 4단계 progress + Origin 검증 + cookie-based auth (Phase 5 신규)

- **유형**: 반복 성공 (Phase 5 첫 적용, SSE event stream + 4 progress steps + Origin whitelist + cookie auth)
- **최초 식별**: 2026-05-29 (Phase 5 Slice 4 — routers/sse.py + lib/sse.ts + ADR-022)
- **관련 회고**: meta/retrospectives/phase-5.md §잘된 것 + §P-SSE-001
- **요약**: 30~60초 대기 시 UX 이탈 방지 (확정 결정 [10]) — SSE 4단계 progress + 부분 결과 노출 패턴:
  1. **SSE event stream** (`text/event-stream` content type): `event: progress\ndata: {...}\n\n` 표준 포맷
  2. **4단계 progress**: intent_analysis (1/4) → wiki_retrieval (2/4) → plan_generation (3/4) → critic_revise (4/4) + complete
  3. **Origin 검증**: `request.headers.get("origin")` whitelist 체크, 미일치 → 403 (CSRF/CORS 1차 방어)
  4. **Cookie-based auth**: EventSource `withCredentials=true` + httpOnly cookie JWT 자동 전송 (Authorization header 노출 회피)
  5. **Heartbeat 30s**: `asyncio.sleep(30)` 무응답 차단
  6. **X-Accel-Buffering: no** header (nginx 호환, 즉시 flush)
  7. **EventSource 자동 재연결**: 브라우저 표준 (네트워크 끊김 시 last-event-id 기반 resume)
- **효과 측정 (Phase 5)**:
  - test_sse.py 4 cases PASS (event_stream content type + 4 steps + schema + invalid origin 403)
  - frontend EventSource wrapper (`lib/sse.ts`) PlanCard 무수정 (wrapper 패턴)
  - 30~60초 UX 이탈 risk ↓ (확정 결정 [10] baseline 활성화)
- **다음 단계**:
  - Phase 8+ MOA Lite 본격화 시 실 worker progress callback 연동 (현 mock asyncio.sleep)
  - Phase 9+ event 재연결 시 last-event-id 기반 resume 정식 활성화
  - Phase 11+ multi-client broadcast (한 plan을 여러 device 동시 표시)
- **권장 대응**:
  - 새 SSE endpoint 추가 시 Origin 검증 + cookie auth + heartbeat + X-Accel-Buffering 4종 의무
  - event schema는 `output_schema.md` 또는 sse_event_schema.md (Phase 11+ 분리) 정합
  - frontend EventSource wrapper 패턴 (wrapper 정신 계승)
- **연관 Skill / Contract**: security-review Skill (T4 SSE hijacking), ADR-022 (Phase 5 SSE Progress)
- **관련 회고**:
  - meta/retrospectives/phase-5.md
  - meta/security_reviews/2026-05-29_phase-5-auth-rls.md (T4 위협 모델)
  - meta/security_reviews/2026-05-29_phase-5-final-verification.md (T4 PASS verify)
  - docs/decisions/phase_5_sse_progress.md (ADR-022)

### Pattern P-SECURITY-REVIEW-001: security-review Skill 2-trigger 패턴 (entry + final) — 보안 phase 표준화 (Phase 5 신규 후보)

- **유형**: 반복 성공 (Phase 5 첫 적용, Slice 1 entry 첫 정식 + Slice 5 final verification 두 번째)
- **최초 식별**: 2026-05-29 (Phase 5 — security-review Skill 첫 정식 + 두 번째 final 트리거)
- **관련 회고**: meta/retrospectives/phase-5.md §잘된 것 2 + §P-SECURITY-REVIEW-001 신규 후보
- **요약**: 보안 영향이 있는 phase (Auth + RLS + JWT + SSE 도입 등)에서 security-review Skill을 2회 트리거:
  1. **Entry 첫 정식 트리거** (Slice 1): 위협 모델 작성 (T1~Tn) + §4 영역 1~10 점검 + 권장 조치 + ADR 작성
  2. **Final 두 번째 트리거** (close Slice): 실 구현 ↔ 권장 조치 verify + 잔존 risk 명시 + 후속 phase 이관 항목 정리
  3. 두 review 결과 모두 `meta/security_reviews/{date}_{phase}_*.md` 누적 → 영구 보관
  4. ADR로 결정 근거 영구 기록 + security_metrics.md 갱신
- **효과 측정 (Phase 5)**:
  - T1~T6 위협 모델 (JWT 누수 / RLS 우회 / Refresh / SSE hijacking / SQL injection / PII) 5 PASS + 1 PARTIAL
  - 영역 1~10 점검: 6 PASS + 2 PARTIAL + 2 N/A
  - 권장 조치 ↔ 실 구현 1:1 verify → 잔존 risk 명시화 (Phase 9+/21+ 이관)
  - 보안 결정 명시화 baseline 확립 (Phase 7+ RAG / Phase 9+ retention / Phase 21+ MFA 시 재사용)
- **다음 단계**:
  - Phase 7+ RAG (security-review §2 RAG 오염), Phase 9+ retention (§9 retention/삭제), Phase 21+ MFA (§8 인증/세션) 진입 시 동일 2-trigger 패턴
  - 정식 채택 결정은 두 번째 phase 보안 진입 시 (Phase 7 또는 Phase 9) 효과 재측정 후
- **권장 대응**:
  - 보안 영향 phase 진입 전 security-review Skill 첫 정식 트리거 의무
  - phase close 직전 security-review 두 번째 final verification 의무
  - ADR + security_metrics.md 갱신 의무
- **연관 Skill / Contract**: security-review Skill, contract-change Skill (security 정책 변경), P-RLS-001 (Phase 5 신규), P-SSE-001 (Phase 5 신규)
- **관련 회고**:
  - meta/retrospectives/phase-5.md
  - meta/security_reviews/2026-05-29_phase-5-auth-rls.md (첫 정식)
  - meta/security_reviews/2026-05-29_phase-5-final-verification.md (두 번째 final)
- **상태**: 신규 등록 후보 (Phase 7+ 또는 Phase 9+ 두 번째 보안 phase에서 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-CRITIC-CANONICAL-001: 다중 fallback → canonical + deprecated 단계적 축소 (Phase 6 신규)

- **유형**: 반복 성공 (Phase 6 첫 적용, Critic verdict 4 fallback → 1 canonical + 1 우선 fallback + 3 deprecated)
- **최초 식별**: 2026-05-29 (Phase 6 Slice 2 — Critic verdict canonical 결정, ADR-018)
- **관련 회고**: meta/retrospectives/phase-6.md §잘된 것 6 + §P-CRITIC-CANONICAL-001
- **요약**: Phase 4.5에서 발견된 "Critic verdict 4 fallback (overall_score_avg / scores / dimensions / eight_dim_scores) 혼재" 문제 → Phase 6 Slice 2 contract-change Skill 트리거로 다음 패턴 정립:
  1. **Canonical 1 결정**: `overall_score: float [0.0~1.0]` + `dimensions: dict[str, float]` (`output_schema.md §9.1 + ADR-018`)
  2. **우선 fallback 1 유지**: `dimensions` 값 평균 (canonical fallback, 같은 정규화 수준)
  3. **Deprecated 3 + DeprecationWarning**: `overall_score_avg` / `scores` / `eight_dim_scores` — Phase 1~4.5 호환을 위해 코드에 잔존하되 `agents/critic.py::select_best_plan_index` 에서 `warnings.warn(DeprecationWarning, ...)` 발행 + `pytest.warns(DeprecationWarning)` capture 의무화
  4. **단계적 제거 시점 명시**: Phase 9+ eval-run 정식화 후 deprecated 3 완전 제거 (별도 contract-change 절차)
- **효과 측정 (Phase 6)**:
  - 코드 단순화: 4 fallback 분기 → canonical 우선 분기로 명확화
  - 회귀 검출 ↑: DeprecationWarning + pytest.warns capture → 누락 발견 자동화
  - 데이터 호환 ↑: Phase 1~4.5 데이터 그대로 동작 (즉시 제거 X)
  - schema_stress_test 22 케이스 PASS — canonical / deprecated 양쪽 모두 검증
- **다음 단계**:
  - Phase 7+ RAG schema, Phase 9+ eval schema 같은 다중 fallback 누적 시 동일 패턴 재사용 가능
  - Phase 9+ eval-run 정식화 후 fallback 완전 제거 시점에 "Resolved" 표기 추가
- **권장 대응**:
  - 큰 schema 결정 시 canonical 1 + 우선 fallback 1 + deprecated N + DeprecationWarning 4단계 명시
  - ADR로 결정 근거 영구 기록 (Phase 6 ADR-018 패턴 복제)
  - `pytest.warns(DeprecationWarning)` capture 의무화 (회귀 자동 검출)
- **연관 Skill / Contract**: contract-change Skill, agent-io-check Skill, ADR-018 (Phase 6 Critic canonical), output_schema.md §9 canonical
- **관련 회고**:
  - meta/retrospectives/phase-6.md
  - docs/decisions/phase_6_critic_canonical.md (ADR-018)

### Pattern P-CONTRACT-FIRST-001: 큰 phase 진입 전 mini-phase로 contract 안정화 (Phase 6 신규 후보)

- **유형**: 반복 성공 (Phase 6 첫 적용 — Phase 5 DB/Auth 15~20h 진입 전 mini-phase 8h로 contract 안정화)
- **최초 식별**: 2026-05-29 (Phase 6 — stabilization mini-phase 형식 두 번째)
- **관련 회고**: meta/retrospectives/phase-6.md §잘된 것 9 + §배운 것 6
- **요약**: 사용자 결정 "Phase 6 → Phase 5 순차 진행" (옵션 B 변형) → Phase 5 DB/Auth 진입 전 Phase 6를 mini-phase로 분리하여 contract 안정화:
  1. **Critic verdict canonical 결정**: 4 fallback → 1+1+3 deprecated (ADR-018)
  2. **Rewriter contract v1.0.0 → v1.1.0**: Pydantic 모델 + graceful 정책 명시 (ADR-019)
  3. **revise_history / recommended_plan_index 정식 등록**: Optional 필드 contract 명시 (§10 Body)
  4. **frontend types.ts canonical mirror**: types ↔ backend 1:1 매핑 정합 (tsc 0 errors)
- **효과 측정 (Phase 6)**:
  - Phase 5 DB/Auth 진입 시 critic_evaluation schema drift 위험 ~0
  - Phase 5 revise_history / recommended_plan_index DB 컬럼 설계 시 schema 결정 부담 ↓
  - mini-phase 8h 비용 → Phase 5+ migration 회귀 비용 ↓↓ (ROI ↑↑)
  - 큰 phase 진입 전 안정화 효과 입증 (Phase 4.5는 Critic revise loop 안정화 / Phase 6은 schema 안정화)
- **다음 단계**:
  - Phase 7 (RAG Lite) 진입 전에 RAG schema 안정화 mini-phase 검토
  - Phase 9+ (eval-run 정식화) 진입 전에 eval schema 안정화 mini-phase 검토
  - Phase 5 entry 시점 사용자 검토 후 정식 패턴 채택 결정 (현재 후보 상태)
- **권장 대응**:
  - 큰 phase (15+h, DB / Auth / RAG / eval 등) 진입 직전 mini-phase로 contract 안정화 검토
  - contract-change Skill + agent-io-check Skill 본격 활용
  - ADR로 결정 근거 영구 기록
  - smoke_test_phase_N + schema_stress_test 신규 (P-X2 v2 패턴)
- **연관 Skill / Contract**: contract-change Skill, agent-io-check Skill, phase-start v1.3.0, P-GPT-REVIEW-001 (Phase 6 두 번째 적용 ▼20% 시간)
- **관련 회고**:
  - meta/retrospectives/phase-6.md
  - meta/retrospectives/phase-4.5.md (Phase 4.5는 Critic revise loop 안정화 mini-phase 첫)

### Pattern P-RAG-5STAGE-001: RAG candidate_knowledge 5단계 transition + hybrid 승인 + promotion_history (Phase 7 신규 후보)

- **유형**: 반복 성공 (Phase 7 첫 적용, 5단계 transition pending → filtered → evaluated → approved → promoted + 자동/수동/거부 hybrid 승인 + promotion_history JSONB append-only)
- **최초 식별**: 2026-05-29 (Phase 7 Slice 2 — promotion + quality_filter + eval_rubric 실 구현 + 0004_rag_5stage migration, ADR-026)
- **관련 회고**: meta/retrospectives/phase-7.md §잘된 것 1 + §P-RAG-5STAGE-001
- **요약**: 사용자 결정 4 (Phase 5.5 명시 — ADR-024 §5단계 MVP) → Phase 7 RAG Lite의 5단계 파이프라인 정식 패턴:
  1. **5단계 stage enum**: pending (input) → filtered (quality_filter 통과) → evaluated (eval_rubric 통과) → approved (사용자 또는 자동 임계) → promoted (approved_knowledge 테이블 이동)
  2. **Hybrid 승인 정책** (ADR-026): 자동 (score ≥ 0.8 자동 approved) / 수동 (0.6~0.8 사용자 검토 큐) / 거부 (< 0.6 자동 reject)
  3. **promotion_history JSONB append-only**: 각 stage transition timestamp + reason + actor (auto / manual / system) 누적 기록
  4. **간이 eval_rubric 3 dim**: relevance / clarity / safety 각 0.0~1.0 (Phase 9+ golden_set 기반 정식 rubric으로 대체 예정)
  5. **quality_filter 3 layer**: PII (이메일/전화/주민번호) + 프롬프트 인젝션 (Phase 1 패턴) + 광고적 표현 차단 단어 (확정 결정 [9])
- **효과 측정 (Phase 7)**:
  - 5단계 transition 10/10 PASS (test_rag_promotion)
  - quality_filter 8/8 PASS (test_rag_quality_filter)
  - eval_rubric 5/5 PASS (test_rag_eval_rubric)
  - end-to-end integration 9/9 PASS (test_rag_integration)
  - candidate_knowledge + approved_knowledge 분리로 운영 단계 검토 큐 baseline 확립
- **다음 단계**:
  - Phase 11+ 사용자 데이터 자동 promotion 활성화 (ADR-024 §A 확대 지점)
  - Phase 9+ 간이 eval_rubric → golden_set 기반 정식 rubric 전환 (Phase 7 개선 제안 §6)
  - 두 번째 적용 (Phase 11+ 사용자 데이터 자동 promotion) 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - RAG 도입 phase에서 5단계 transition 의무화 (자동 ≥ 0.8 / 수동 0.6~0.8 / 거부 < 0.6 hybrid)
  - promotion_history JSONB append-only로 audit trail 보존
  - ADR로 결정 근거 영구 기록 (Phase 7 ADR-026 패턴 복제)
  - 운영 단계 진입 직전 Supabase SQL function `match_approved_knowledge` 정의 (Phase 7 개선 제안 §2)
- **연관 Skill / Contract**: rag-design Skill (Phase 7 첫 정식), rag-update Skill (Phase 7 첫 정식), contract-change Skill (rag_data_contract §18), ADR-025 (RAG architecture), ADR-026 (5단계 promotion logic), P-CONTRACT-FIRST-001 (Phase 7 누적 3회)
- **관련 회고**:
  - meta/retrospectives/phase-7.md
  - docs/decisions/phase_7_rag_architecture.md (ADR-025)
  - docs/decisions/phase_7_promotion_logic.md (ADR-026)
  - docs/contracts/rag_data_contract.md §18 (Phase 7 Slice 2 신규)
- **상태**: 신규 등록 후보 (Phase 7 첫 적용, Phase 11+ 사용자 데이터 자동 promotion 시점 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-RAG-GRACEFUL-001: RAG 5종 marker 표준화 + RAG > LLM Wiki 우선순위 (Phase 7 신규 후보)

- **유형**: 반복 성공 (Phase 7 첫 적용, RAG 실패 시 plan 생성 차단 X + 5종 marker 표준화 + RAG > LLM Wiki 우선순위)
- **최초 식별**: 2026-05-29 (Phase 7 Slice 4 — agents/rag.py 통합, ADR-025 §4 + §5)
- **관련 회고**: meta/retrospectives/phase-7.md §잘된 것 5 + §P-RAG-GRACEFUL-001
- **요약**: P-GRACEFUL-001 (Phase 1 외부 의존성 graceful) 정신 5번째 입증 — RAG Lite 통합 wrapper에서 다음 패턴 표준화:
  1. **5종 marker 표준화** (ADR-025 §5):
     - `rag_unavailable`: retrieval 자체 실패 (Supabase 연결 실패 등)
     - `rag_no_results`: retrieval 정상 + threshold 미달 (0 results)
     - `llm_wiki_unavailable`: LLM Wiki 정적 lookup 실패
     - `embedding_failed`: OpenAI embedding 호출 실패
     - `supabase_unconfigured`: 환경변수 미설정 (개발 환경 graceful)
  2. **RAG > LLM Wiki 우선순위** (ADR-025 §4): priority 1 = approved_knowledge (동적, retrieval.search) → priority 2 = LLM Wiki (정적, llm_wiki.search_by_tags) 보조
  3. **plan 생성 차단 X**: 모든 실패는 `validation.warnings`에 marker 추가하고 진행 (P-GRACEFUL-001 Phase 1 정신 계승)
  4. **wrapper 내부 try/except로 자기설명**: 각 marker는 logger.warning으로 운영 단계 관측 가능
- **효과 측정 (Phase 7)**:
  - graceful failure 통합 케이스 PASS (test_rag_integration 9/9)
  - Supabase 미설정 (개발 환경) 시 응답 200 + warnings list로 자기설명
  - Phase 5.5 legacy backward-compat 100% 정신 계승
- **다음 단계**:
  - Phase 8+ MOA Lite 본격화 시 동일 5종 marker 패턴 적용 (Critic / Rewriter 실패 graceful)
  - Phase 9+ feedback schema에 동일 marker 패턴 적용
  - cost-review Skill 활성 시 marker별 비용 영향 측정
- **권장 대응**:
  - 외부 의존성 (LLM / RAG / DB) 실패 시 marker 의무화 (5종 baseline 또는 phase별 확장)
  - validation.warnings 표준 schema 유지 (P-GRACEFUL-001 정신)
  - ADR로 marker list 영구 기록 (Phase 7 ADR-025 §5 패턴 복제)
- **연관 Skill / Contract**: P-GRACEFUL-001 (Phase 1, 5번째 입증 — Phase 4 + Phase 4.5 + Phase 5 + Phase 5.5 + Phase 7), ADR-025 (RAG architecture §4 + §5), error_response_contract.md, agent_io_contract.md
- **관련 회고**:
  - meta/retrospectives/phase-7.md
  - docs/decisions/phase_7_rag_architecture.md (ADR-025 §4 + §5)
- **상태**: 신규 등록 후보 (Phase 7 첫 적용, Phase 8+ MOA Lite 적용 시 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-MOA-ORCHESTRATOR-001: god-function → service layer 추출 (behavior-preserving) (Phase 8 신규 후보)

- **유형**: 반복 성공 (Phase 8 첫 적용, `plans_generate()` 659줄 god-function → `orchestration/moa_orchestrator.py::generate_plan()` 서비스 레이어 추출 + plans.py 243줄 thin adapter, Envelope byte-identical)
- **최초 식별**: 2026-05-29 (Phase 8 Slice 2 — MOA Orchestrator 추출, ADR-027)
- **관련 회고**: meta/retrospectives/phase-8.md §잘된 것 1 + §배운 것 1 + §P-MOA-ORCHESTRATOR-001
- **요약**: router에 인라인된 MOA orchestration(Intent→RAG→3-plan→Critic+revise→save→Envelope)을 서비스 레이어 orchestrator로 추출하는 behavior-preserving 패턴 (moa_policy §2 "오케스트레이터가 항상 중개" 정합 회복):
  1. **신규 폴더 격리**: `backend/fastapi/orchestration/` (moa_orchestrator + progress_sink + progress_store + responses + __init__) — 기존 routers/agents/schemas 침범 0 (P-X1 36연속 보조)
  2. **late-import monkeypatch honor**: orchestrator 내부에서 agent를 late-import → 기존 test의 monkeypatch mock 호환 유지 (회귀 0)
  3. **ProgressSink Null default**: `generate_plan(..., *, progress=NullProgressSink())` — emit은 Null이면 no-op → 기존 호출 동작 불변
  4. **thin adapter router**: `plans_generate()`는 `return await generate_plan(...)` 위임 (god-function 분해, LOC 659→243)
  5. **에러 코드 / validation.checks 순서 100% 보존**: graceful 처리 + E-LLM-* / INV-* 코드 + checks 순서 그대로 이관
- **효과 측정 (Phase 8)**:
  - plans.py LOC 659 → 243 (god-function 분해)
  - 기존 pytest 223 수정 0 (의도된 Slice 4 version assertion 2건 제외) — behavior-preserving 증거
  - test_moa_orchestrator.py: generate_plan 기본 + ProgressSink emit + NullProgressSink 회귀 0 + 에러 경로 보존 PASS
  - moa_policy §2 정합 회복 (router 인라인 위반 → orchestrator 중개)
- **다음 단계**:
  - Phase 9+ orchestration 확장 (결과 저장 + 피드백 wiring + normalize_to_canonical) 시점 효과 재측정
  - Phase 11+ SSE full async worker 시 progress_store → 외부 store 전환 (P-SSE-001 연계)
  - 두 번째 적용 (Phase 9+ orchestration 확장) 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - god-function 추출 시 신규 폴더 격리 + late-import monkeypatch honor + ProgressSink Null default 3종 조합 검토
  - Envelope byte-identical + 기존 test 수정 0 = behavior-preserving 증거 의무 (P-BEHAVIOR-PRESERVING-001 연계)
  - ADR로 결정 근거 영구 기록 (Phase 8 ADR-027 패턴 복제)
- **연관 Skill / Contract**: ai-architecture-review Skill (Phase 8 첫 정식), contract-change Skill (agent_io_contract §8 orchestrator 중개), ADR-027 (MOA orchestrator behavior-preserving + ProgressSink), ADR-028 (SSE progress integration), P-BEHAVIOR-PRESERVING-001 (Phase 8 신규 후보), P-SSE-001 (progress_store 실 stage), moa_policy §2/§4
- **관련 회고**:
  - meta/retrospectives/phase-8.md
  - docs/decisions/phase_8_moa_orchestrator.md (ADR-027)
  - docs/decisions/phase_8_sse_progress_integration.md (ADR-028)
- **상태**: 신규 등록 후보 (Phase 8 첫 적용, Phase 9+ orchestration 확장 시점 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-BEHAVIOR-PRESERVING-001: behavior-preserving refactor 정당성 = 기존 test 수정 0 (Phase 8 신규 후보)

- **유형**: 반복 성공 (Phase 8 첫 적용, orchestrator 추출 = Envelope byte-identical + 기존 pytest 223 수정 0 — 의도된 contract 변경 2 version assertion 격리 제외)
- **최초 식별**: 2026-05-29 (Phase 8 Slice 2 — behavior-preserving 검증)
- **관련 회고**: meta/retrospectives/phase-8.md §잘된 것 2 + §배운 것 2 + §P-BEHAVIOR-PRESERVING-001
- **요약**: 동작 보존 리팩터(god-function 추출 등)의 정당성을 "기존 test 수정 0"으로 입증하는 패턴:
  1. **기존 test 수정 0 = 동작 불변 증거**: orchestrator 추출 후 기존 pytest 전부 그대로 PASS = Envelope byte-identical 입증. test 수정 필요 = 재작업 신호 (refactor가 동작을 바꿨다는 의미)
  2. **의도된 contract 변경만 최소 assertion 격리**: behavior-preserving 예외는 의도된 contract delta(version bump 등)만 — Phase 8 Critic v1.1.0 version-string assertion 정확히 2건(test_critic:93 + test_e2e_slice1:172), Phase 6 Rewriter v1.1.0 선례와 동일
  3. **격리 assertion에 주석 명시**: version delta 격리 지점에 "Phase N ADR-XXX version bump — 의도된 contract delta" 주석 → 회귀 vs 의도 구분 명확화
  4. **additive helper 우선**: 코드 변경도 additive(강제 주입 X) 우선 → 출력 의미 불변 (Critic normalize_to_canonical helper, run_critic 미강제)
- **효과 측정 (Phase 8)**:
  - 기존 pytest 223 중 의도된 2건만 갱신 (정확히 version assertion) — 나머지 221 수정 0 PASS
  - pytest 223 → 249 (+26 신규) — 신규는 추가, 기존은 보존
  - Envelope byte-identical (test_moa_orchestrator + 기존 test_plans / test_e2e_slice1 graceful 케이스 동일 출력)
  - refactor 정당성을 test diff 0으로 입증 (Phase 6 Rewriter 선례 누적 2회)
- **다음 단계**:
  - Phase 9+ 큰 refactor (feedback wiring / Critic fallback 제거) 시 동일 패턴 적용
  - 두 번째 적용 (Phase 9+ refactor) 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - 동작 보존 리팩터 시 "기존 test 수정 0" 목표 (test 수정 발생 시 = 재작업 신호로 점검)
  - 의도된 contract delta(version bump 등)만 최소 assertion 격리 + 주석 명시
  - additive helper 우선 (강제 주입 X — 출력 의미 불변)
  - ADR §Amendment에 version bump 영향 = 정확히 N baseline assertion 명시 (Phase 8 ADR-029 패턴 복제)
- **연관 Skill / Contract**: P-MOA-ORCHESTRATOR-001 (Phase 8 신규 후보), P-CRITIC-CANONICAL-001 (Phase 6 canonical + deprecated 정신 계승), agent-io-check Skill, ADR-027 (MOA orchestrator), ADR-029 (prompt_registry semver §Amendment)
- **관련 회고**:
  - meta/retrospectives/phase-8.md
  - meta/retrospectives/phase-6.md (Rewriter v1.1.0 version assertion 2건 선례)
  - docs/decisions/phase_8_moa_orchestrator.md (ADR-027 behavior-preserving 제약)
  - docs/decisions/phase_8_prompt_registry_semver.md (ADR-029 §Amendment — version bump 영향 정확히 2 baseline assertion)
- **상태**: 신규 등록 후보 (Phase 8 첫 적용, Phase 9 normalize wiring additive 재확인 — Phase 9.5 deprecated 완전 제거 시점 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-FEEDBACK-LOOP-001: 피드백 영속 graceful + PII 마스킹 (Phase 9 신규 후보)

- **유형**: 반복 성공 (Phase 9 첫 적용, selected_plans + feedback_events 영속화 — PlansRepo graceful + reason 저장 전 PII 마스킹 + RLS user 격리 + candidate 적재 pending)
- **최초 식별**: 2026-05-31 (Phase 9 Slice 2~4 — feedback/selection 영속화, ADR-030 + ADR-031)
- **관련 회고**: meta/retrospectives/phase-9.md §잘된 것 1 + §배운 것 1 + §P-FEEDBACK-LOOP-001
- **요약**: 사용자 plan 선택/피드백을 영속화할 때 회귀 0 + 보안 + 데이터 누적 인프라를 동시 달성하는 패턴:
  1. **PlansRepo graceful 패턴 계승**: SelectionRepo / FeedbackRepo / BrandMemoryRepo — Supabase 실패/미설정 시 in-memory dict fallback (Phase 5 패턴). 응답 200 + graceful → 개발 환경에서도 동작 + testability ↑ (P-GRACEFUL-001 6번째 입증)
  2. **reason 자유 입력 저장 전 PII 마스킹**: feedback reason (자유 텍스트) 는 FeedbackRepo 가 저장 전 PII(이메일/전화/주민번호) 마스킹 (security-review T1)
  3. **RLS user 격리**: feedback_events / selected_plans / brand_memory_entries 모두 RLS 정책 (auth.uid() 또는 brands(id) 2-hop subquery) — Phase 5 P-RLS-001 정신 계승
  4. **candidate 적재는 pending 상태로만**: feedback → candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending') 적재 (자동 승격 X — Phase 7 5단계 정합 NG12) — Brand Memory 자동 추출 agent 는 Phase 10+ 이관
  5. **실 plans 테이블 정합**: selected_plans 는 plan_id + selected_option_index(0–2) — idealized plan_options(option_id FK) 대신 실 plans + plan_candidates JSONB 정합 (4계층 full linkage Phase 11+ NG2). FK 교정: brand_id → brands(id), source_plan_id → plans.id
- **효과 측정 (Phase 9)**:
  - test_selection_feedback (graceful CRUD + PII 마스킹 + in-memory fallback) + test_plans_feedback_api (select/feedback/GET + RLS) + test_brand_memory_prep (feedback→candidate 적재) PASS
  - pytest 249 → 293 (+44 신규), 기존 수정 0 (회귀 0)
  - 개발 환경 Supabase 미설정 시 응답 200 + in-memory fallback (graceful)
- **다음 단계**:
  - Phase 10+ P-AUX-2 brand_memory_extractor agent 실 구현 (candidate pending → 자동 추출) 시점 효과 재측정
  - Phase 10+/11+ 사용자 데이터 자동 promotion (rag-update 두 번째) 연계
  - 두 번째 적용 (Phase 10+ Brand Memory agent) 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - 사용자 데이터 영속화 시 graceful + PII 마스킹 + RLS + pending 적재 4종 조합 검토
  - 자유 입력 텍스트는 저장 전 PII 마스킹 의무 (security-review T1 패턴)
  - candidate 적재는 pending 상태로만 (자동 승격 분리 — Phase 7 5단계 정합)
  - ADR로 결정 근거 영구 기록 (Phase 9 ADR-030/031 패턴 복제)
- **연관 Skill / Contract**: security-review Skill (Phase 9 두 번째 정식 — 피드백 PII), contract-change Skill (db_schema.md CC-004), P-GRACEFUL-001 (Phase 1, 6번째 입증), P-RLS-001 (Phase 5), P-RAG-5STAGE-001 (Phase 7 pending 적재 정합), ADR-030 (feedback/selection persistence), ADR-031 (Brand Memory prep — P-AUX-2 agent Phase 10+)
- **관련 회고**:
  - meta/retrospectives/phase-9.md
  - meta/security_reviews/2026-05-29_phase-9-feedback-pii.md
  - docs/decisions/phase_9_feedback_selection.md (ADR-030)
  - docs/decisions/phase_9_brand_memory_prep.md (ADR-031)
- **상태**: 신규 등록 후보 (Phase 9 첫 적용, Phase 10+ Brand Memory agent 활성 시점 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-CANONICAL-WIRING-001: Phase N helper → live pipeline wiring (additive 회귀 0) (Phase 9 신규 후보)

- **유형**: 반복 성공 (Phase 9 첫 적용, Phase 8 normalize_to_canonical helper(additive, 미연결) → Phase 9 moa_orchestrator critic step 실 wiring, 기존 pytest 249 수정 0)
- **최초 식별**: 2026-05-31 (Phase 9 Slice 3 — normalize_to_canonical wiring, ADR-032)
- **관련 회고**: meta/retrospectives/phase-9.md §잘된 것 2 + §배운 것 2 + §P-CANONICAL-WIRING-001
- **요약**: 이전 phase 에서 additive 로 추가한 helper(미연결, 회귀 0 우선)를 후속 phase 에서 live pipeline 에 wiring 할 때 회귀 0 을 유지하는 패턴 (P-BEHAVIOR-PRESERVING-001 정신 계승):
  1. **helper 비파괴 사본 반환**: `normalize_to_canonical(run_critic(...))` 는 입력을 변형하지 않고 canonical(overall_score 0–1 + dimensions) 추가한 사본 반환 → 원본 deprecated 0–5(scores / overall_score_avg) 병행 유지
  2. **deprecated 병행 유지 (단계적 축소)**: canonical live 활성 + deprecated 병행 (NG3) — 완전 제거는 eval-run 정식화 후 (P-CRITIC-CANONICAL-001 단계적 축소 정신)
  3. **additive Optional → 기존 test 수정 0**: critic_evaluation 에 canonical 추가는 기존 assertion 불침범 → 기존 pytest 249 수정 0 (회귀 0). Phase 8 (의도된 2 version assertion 갱신) 과 달리 **baseline test delta 0건**
  4. **wiring 지점 단일화**: orchestrator critic step 한 곳에서만 wiring (verdict = normalize_to_canonical(...)) → schemas/output.py 불변 + 다른 호출 지점 영향 0
- **효과 측정 (Phase 9)**:
  - critic_evaluation canonical(0–1) live 활성 + deprecated 0–5 병행 (test_critic_canonical_wiring PASS)
  - deprecated warnings 67 → 16 감소 (canonical 우선 경로 정착)
  - 기존 pytest 249 수정 0 (additive Optional — 회귀 0)
  - Phase 8 §개선 제안 §1 (helper 미연결) 해소
- **다음 단계**:
  - Phase 9.5 deprecated 0–5 fallback 완전 제거 (eval-run 정식화 후) 시점 효과 재측정
  - 다른 Phase N helper → live wiring 케이스 (선택/피드백 best-plan 우선순위 등) 발견 시 동일 패턴 적용
  - 두 번째 적용 (Phase 9.5 deprecated 완전 제거) 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - helper → live wiring 시 비파괴 사본 + deprecated 병행 + additive Optional 3종 조합 (기존 test 수정 0 목표)
  - wiring 지점 단일화 (orchestrator 중개 지점 한 곳)
  - ADR §Amendment 에 wiring 영향 = 기존 test 수정 0 명시 (Phase 9 ADR-032 패턴 복제)
- **연관 Skill / Contract**: agent-io-check Skill (critic 정합 drift 0), P-BEHAVIOR-PRESERVING-001 (Phase 8 — additive helper 우선 정신 계승), P-CRITIC-CANONICAL-001 (Phase 6 canonical + deprecated 단계적 축소), P-MOA-ORCHESTRATOR-001 (Phase 8 orchestrator 중개 — wiring 지점), ADR-032 (normalize_to_canonical wiring)
- **관련 회고**:
  - meta/retrospectives/phase-9.md
  - meta/retrospectives/phase-8.md (§개선 제안 §1 — helper 미연결, Phase 9 해소)
  - docs/decisions/phase_9_critic_canonical_wiring.md (ADR-032)
- **상태**: 신규 등록 후보 (Phase 9 첫 적용, **Phase 9.5 deprecated 0–5 Full 제거로 wiring 단계 완료** — canonical 단일 표준화. 다른 helper → live wiring 케이스 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-EVAL-HARNESS-001: golden_set mock-deterministic 회귀 + 임계값 게이트 (Phase 9.5 신규 후보)

- **유형**: 반복 성공 (Phase 9.5 첫 적용, golden_set.md 11 케이스 단일 출처 → mock-deterministic 회귀 runner + schema 100%/structural 채점 + 임계값 게이트 + regression_results, CI 가능 비용 0)
- **최초 식별**: 2026-05-31 (Phase 9.5 Slice 1~3 — eval-design + eval-run Skill 첫 정식, ADR-033)
- **관련 회고**: meta/retrospectives/phase-9.5.md §잘된 것 1 + §배운 것 2 + §P-EVAL-HARNESS-001
- **요약**: 품질 회귀 baseline (확정 결정 [20] semver 회귀)을 mock-deterministic 회귀 runner로 구축하는 패턴 — prompt/RAG/모델 변경 시 자동 품질 검증:
  1. **markdown golden_set 단일 출처 파싱**: `eval/golden_set.md` (GS-001~GS-011, ★ 실 v1.0.0 §2는 11 케이스 — entry plan "47" 표기는 오기, NG10 확대 Phase 10+) → loader가 GS- prefix 필터로 [id, input, expected_properties] 구조화. 케이스 수는 실 출처 단일 진실 (계획 문서와 불일치 시 실 출처 우선)
  2. **mock-deterministic pipeline (CI 가능, 비용 0)**: 각 케이스 → mock pipeline → 결정적 출력 → schema 준수 100% + structural 채점. 실 LLM 8차원 eval은 mode flag + 문서로 분리 (mock primary)
  3. **임계값 게이트** (eval-run §6): schema 준수 100% / 점수 변화 ±0.3 / 광고 표현 >5% fail / 차단 단어 >0% fail → 위반 시 작업 차단 (gate=fail → exit 1)
  4. **regression_results 출력**: `eval/regression_results/phase-N_{trigger}.md` §5 형식 (schema_rate / pass_rate / revise mean_delta 등) 누적 → 회귀 audit trail
  5. **revise effect metric 통합**: revise attempt별 canonical overall_score 0–1 delta (mean_delta / improved_rate / regressed_rate) — Phase 4.5 D6 해소
- **효과 측정 (Phase 9.5)**:
  - test_eval_runner (loader + mock 회귀 + 임계값 게이트) + test_revise_effect (revise effect metric) 통합 45 PASS
  - eval_run.ps1 gate=pass (schema_rate 1.0 / pass_rate 1.0 / revise mean_delta 0.092 / improved 0.6 / regressed 0.2)
  - smoke_test_phase_9_5 Step 16 (eval-run) 통합 — 16/16 (15 PASS + 1 WARN intended)
  - eval-design(설계) + eval-run(실행) 두 Skill 모두 첫 정식 트리거
  - **deprecated 제거 안전망 역할** (P-DEPRECATED-REMOVAL-001 연계): canonical-only 품질 baseline을 제거 전/후 동일 입증
- **다음 단계**:
  - Phase 10+ 실 LLM eval mode 운영 활성 (mode flag → 실 호출, cost-review 연계)
  - Phase 10+ RAG eval_rubric → golden_set 정식화 (동일 harness 흡수, NG1)
  - Phase 10+ golden_set 11 → 확대 (eval-design Skill 두 번째 트리거 baseline, NG10)
  - 두 번째 적용 (Phase 10+ 실 LLM mode / RAG eval) 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - 품질 회귀 baseline 구축 시 mock-deterministic primary (CI 가능 비용 0) + 실 LLM mode flag 분리
  - golden_set markdown 단일 출처 파싱 (계획 문서 ≠ 실 출처 시 실 출처 우선)
  - 임계값 게이트 (schema 100% / 점수 ±delta / 광고 / 차단 단어) 의무 + regression_results 누적
  - ADR로 결정 근거 영구 기록 (Phase 9.5 ADR-033 패턴 복제)
- **연관 Skill / Contract**: eval-design Skill (Phase 9.5 첫 정식), eval-run Skill (Phase 9.5 첫 정식), ADR-033 (eval-run harness mock-deterministic + 임계값 + §eval-design), P-DEPRECATED-REMOVAL-001 (Phase 9.5 신규 — deprecated 제거 안전망), eval/golden_set.md, eval/video_planning_eval.md
- **관련 회고**:
  - meta/retrospectives/phase-9.5.md
  - meta/retrospectives/phase-4.5.md (§D6 revise effect 미측정 — Phase 9.5 해소)
  - meta/retrospectives/phase-9.md (§개선 제안 §4 — eval-run 정식화)
  - docs/decisions/phase_9_5_eval_run_harness.md (ADR-033)
- **상태**: 신규 등록 후보 (Phase 9.5 첫 적용, Phase 10+ 실 LLM mode / RAG eval_rubric 정식화 시점 효과 재측정 후 정식 패턴 채택 결정)

### Pattern P-DEPRECATED-REMOVAL-001: eval 안전망으로 deprecated 제거 (제거 전/후 eval 동일 입증) (Phase 9.5 신규 후보)

- **유형**: 반복 성공 (Phase 9.5 첫 적용, Critic deprecated 0–5 Full 제거 — eval runner 먼저 구축 → 제거 전 canonical-only baseline → 제거 → 제거 후 eval 동일 입증, warnings 16→0)
- **최초 식별**: 2026-05-31 (Phase 9.5 Slice 2~4 — eval → 검증 → 제거 순서, ADR-034 + CC-005)
- **관련 회고**: meta/retrospectives/phase-9.5.md §잘된 것 3 + §배운 것 1 + §P-DEPRECATED-REMOVAL-001
- **요약**: deprecated 코드(fallback / Optional 필드)를 제거할 때 eval을 안전망으로 사용하여 회귀 0을 보장하는 패턴 (P-CRITIC-CANONICAL-001 단계적 축소의 종착점):
  1. **★ 제거 순서 강제 (eval → 검증 → 제거)**: (Slice 2~3) eval runner 먼저 구축 → (Slice 3) eval로 제거 전 canonical-only 품질 baseline 측정 → (Slice 4) deprecated 제거 → 제거 후 eval로 동일 입증. 순서가 핵심 — eval이 dead code 제거의 안전망
  2. **canonical 단일 표준화**: select_best_plan_index deprecated fallback(overall_score_avg / scores / eight_dim_scores + DeprecationWarning) 제거 → canonical(overall_score → dimensions) 2 경로만 + CriticEvaluation Optional 0–5 필드 제거 (Pydantic extra='ignore'로 verdict의 0–5 키 무시 → 회귀 0)
  3. **LLM-facing contract 불변 경계**: run_critic 0–5 출력 + normalize_to_canonical(0–5→0–1)은 P-007 prompt contract로 불변 (NG3) — 제거 대상은 dead code인 deprecated fallback/필드만, 생성 경로(run_critic + normalize)는 유지
  4. **의도 delta 최소화 + 주석 명시**: 기존 test 중 deprecated-fallback pytest.warns 케이스만 의도 delta 갱신/제거 (canonical 케이스 + run_critic 0–5 케이스 보존). 의도 delta 지점에 ADR-034 주석 명시 (회귀 vs 의도 구분)
  5. **contract-change 동반 (CC-005)**: output_schema §9 + agent_io_contract §5 + db_schema critic_evaluation deprecated 제거 정합 + frontend lib/types.ts canonical 전환 (page.tsx 동시 마이그레이션 — PlanCard·component_map 0줄)
  6. **legacy consumer wiring 보강 (실측 발견)**: 점진 wiring(helper → 단일 지점)은 다른 consumer를 자동 커버하지 않음 — Phase 1 legacy /generate endpoint normalize 누락 발견 → generate.py canonical wiring 보강. 향후 신규 critic consumer normalize_to_canonical 경유 필수
- **효과 측정 (Phase 9.5)**:
  - eval 제거 전/후 동일 (canonical-only baseline 회귀 0) — eval_run.ps1 gate=pass 유지
  - Critic deprecated warnings 16 → 0 (deprecated 0–5 fallback + CriticEvaluation Optional 필드 완전 제거)
  - 기존 pytest 293 중 의도된 test_critic deprecated-fallback delta만 갱신 (나머지 보존) — 회귀 0, pytest 339
  - schema_stress_test 5/5 유지 (CriticEvaluation deprecated 제거 정합) + agent-io-check drift 0
  - Critic 평가 체계 canonical(0–1) 단일 표준화 (Phase 6 ADR-018 → Phase 8 conservative adapter → Phase 9 normalize wiring → Phase 9.5 deprecated Full 제거 종착)
- **다음 단계**:
  - 다른 deprecated 코드 제거 시점 (legacy rag/retriever 통합 Phase 11+ 등) 동일 패턴 적용
  - 두 번째 적용 효과 재측정 후 정식 패턴 채택 결정
- **권장 대응**:
  - deprecated 제거 전 eval runner 먼저 구축 (제거 순서 eval→검증→제거 의무)
  - eval로 제거 전/후 동일 입증 (회귀 0 증거)
  - LLM-facing contract / 생성 경로 불변 경계 명시 (제거 대상은 dead code만)
  - 의도 delta 최소화 + 주석 명시 + contract-change 동반 + legacy consumer wiring 점검
  - ADR로 결정 근거 영구 기록 (Phase 9.5 ADR-034 패턴 복제)
- **연관 Skill / Contract**: eval-run Skill (Phase 9.5 — 안전망), contract-change Skill (CC-005), agent-io-check Skill (canonical-only drift 0), P-EVAL-HARNESS-001 (Phase 9.5 신규 — eval baseline), P-CRITIC-CANONICAL-001 (Phase 6 canonical + deprecated 단계적 축소 종착), P-CANONICAL-WIRING-001 (Phase 9 wiring → Phase 9.5 제거 완료), P-BEHAVIOR-PRESERVING-001 (Phase 8 — 기존 test 수정 0 정신 계승), ADR-034 (Critic deprecated 0–5 Full 제거)
- **관련 회고**:
  - meta/retrospectives/phase-9.5.md
  - meta/retrospectives/phase-6.md (§P-CRITIC-CANONICAL-001 — 단계적 제거 시점 명시)
  - meta/retrospectives/phase-9.md (§개선 제안 §2 — Critic deprecated 완전 제거)
  - docs/decisions/phase_9_5_critic_deprecated_removal.md (ADR-034)
- **상태**: 신규 등록 후보 (Phase 9.5 첫 적용 — Critic deprecated 0–5 Full 제거, 다른 deprecated 제거 시점 효과 재측정 후 정식 패턴 채택 결정)
