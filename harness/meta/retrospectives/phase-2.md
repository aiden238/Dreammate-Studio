# Retrospective: Phase 2 — design.md 기반 PWA 설계 (Discovery + Quick 분기)

> 작성일: 2026-05-27
> 종류: phase
> 범위: Phase 2 (전체 — 진입 점검 → 6 Slices → final QA → archive)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete v1.1.0 절차 6단계 (회고)

---

## 사실 요약

Phase 2 (design.md 기반 PWA 설계)를 **2026-05-27 단일 일자**에 진입부터 archive까지 완수.

진입 점검: phase-start v1.2.0 §6 4점검 (audit_naming 0 drift, GPT 검토 80점 조정안 채택). 4-layer 컴포넌트 4개 한정 (ADR-010) + Variants Bank 3 컴포넌트 한정 (ADR-011) + Step 1만 상세 wireframe + Step 2~7 placeholder 정책 확정.

6 Slices를 5 Waves로 분해:
- Wave 1 (Slice 1): Design System Foundation — tokens / 4-layer template / variants format / replaceability + ADR-010/011
- Wave 2 (Slice 2): BrandDirectionCard + CardGrid5 4-layer + Discovery §0+§1 + wireframes/step1_brand
- Wave 3 (Slice 3+4 병렬): Direction Approval + Discovery §2~§7 ∥ Quick + Mode Branching
- Wave 4 (Slice 5): page_map + component_map 통합 + design_handoff.md (★ Phase 2 핵심)
- Wave 5 (Slice 6): final QA + design-review + meta-retrospective + archive

총 6 sub-agent dispatch. 충돌 0건, push race 0건. **변경성 시뮬레이션 5/5 PASS**.

회고 핵심 발견:
- ★ **Wave 3 Slice 3 sub-agent가 forbidden 영역 (QuickInputCard sub-section, Slice 4 영역)을 component_map.md에 추가**
- 결과적으로 무충돌 (동일 내용 / append-only / Slice 4가 component_map.md를 건드리지 않음)
- 잠재 위험: 다른 시나리오에서는 merge conflict / 내용 불일치 발생 가능
- → 새 패턴 **P-AGENT-SCOPE-001** 등록 + 후속 개선안 P-X1 작성

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-27 단일일 (다중 세션) |
| Total commits (Phase 2) | 6 (entry + Slice 1~5 + Slice 6 본 commit) |
| 신규 파일 (apps/web/* + docs/decisions/*) | 15 (design_system 4 + ADR 2 + flow 4 + wireframes 4 + design_handoff 1) |
| 수정 파일 | 2 (page_map.md + component_map.md, Slice 5 통합) |
| 줄 수 변화 | +3962 / -135 (apps/web + docs/decisions) |
| 4-layer 컴포넌트 | 4 (BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard) |
| Variants Bank | 3 컴포넌트 (BrandDirectionCard 3 / CardGrid5 2 / DirectionApprovalCard 2) — ADR-011 정합 |
| Sub-agent dispatch | 6 (Wave 1 + Wave 2 + Wave 3×2 + Wave 4 + Wave 5) |
| QA reports | 7 (entry + Slice 1~5 + final) |
| audit_naming 결과 | 0 drift (모든 Slice + final) |
| pytest 영향 | 0 (Phase 2 코드 무변경 — 62/62 유지) |
| 변경성 시뮬레이션 | 5/5 PASS (acceptance A9) |
| design-review | 7 원칙 모두 정합 PASS |
| 식별된 P-pattern (Phase 2 신규) | 1 (P-AGENT-SCOPE-001) |
| 식별된 P-pattern (Phase 2 검증) | 1 (P-DESIGN-LAYERED-001 — minimal 정책 효과) |

---

## 분석

### 잘된 것

1. **ADR-010/011로 over-engineering 자동 차단**: 4-layer 컴포넌트 4개 / Variants 3개 한정 정책을 Slice 1에서 명문화 → Slice 2~5 sub-agent가 자발적으로 minimal entry 유지 (BreadcrumbBrandPath 등 단순 entry는 Phase 0 형태 보존).
2. **literal 값 0 정책으로 시나리오 1 보장**: tokens.* 참조 강제 (Slice 1 component_contract.md)가 4-layer 컴포넌트 + wireframes 모두에 일관 적용 → 변경성 시뮬레이션 시나리오 1 (token 값 변경) 1 파일 수정으로 압축.
3. **Wave 3 병렬 sub-agent + 폴더 분리 패턴 재현**: P-FOLDER-PARALLEL-001 (Phase 1) 패턴이 Phase 2에도 적용 — direction_approval.md (Slice 3) vs quick_flow.md / mode_branching.md (Slice 4) 폴더 분리로 conflict 0. multi_slice_plan.md §3 충돌 분석 매트릭스 효과적.
4. **변경성 시뮬레이션 5/5 PASS**: Slice 5 design_handoff.md §6 매핑표가 실제 grep + 매뉴얼 검증에서 모두 PASS — design system 도입 효과 실증.
5. **Direction Approval 격상 결정 효과**: Slice 3에서 Direction Approval을 양 모드 공통 핵심 UX로 격상 (verbose Discovery + minimal Quick variant 분기) → Quick Mode (Slice 4)에서 코드 재사용 명확.
6. **U2-7 Tone form 실시간 결정**: Slice 3 진입 시 사용자 confirmed (multi-select chip 채택, 슬라이더 거부) — assumptions.md §1.2 갱신, work_plan.md 미해결 결정 표 1줄 처리.
7. **Phase 1 회고 P1~P4 적용 효과 검증**: audit_naming.ps1 (P1) Slice별 0 drift / phase-start v1.2.0 §6.1 (P2) 4점검 통과 / qa-check v1.2.0 §11 (P3) PASS / phase-complete v1.1.0 (P4) 절차 본 Phase 2 종료에 적용. → **Phase 1 회고 효과 실증** (P-DRIFT-001 mitigated 상태 유지).

### 안 된 것

1. **★ Wave 3 Slice 3 sub-agent가 forbidden 영역 침범 (P-AGENT-SCOPE-001)**: multi_slice_plan.md §5 Slice 3 prompt에 "QuickInputCard sub-section 건드리지 말 것" 명시했음에도, Slice 3 sub-agent commit (daa3e18)이 component_map.md에 QuickInputCard 4-layer를 추가. Slice 4 commit (941b403)이 같은 파일을 건드리지 않아 무충돌이었으나, 의도 다를 시 위험.
2. **design-review Skill 절차의 spec-only phase 부재**: design-review SKILL.md는 "구현된 화면" 가정 (eval/design_reviews/ 저장 절차) — Phase 2 spec phase 적용 시 절차 변형 필요했음. Slice 6에서 QA report §5에 통합으로 우회 (Surgical Scope), proposal P-X3로 후속 등록.
3. **Slice 3 commit metadata의 자기 검증 부재**: Slice 3 sub-agent의 commit message는 "Phase 0/1 + Slice 2 entries 모두 0줄 수정" "Slice 4 영역 0줄 수정"으로 명시했으나, 실제로는 QuickInputCard 4-layer (Slice 4 영역) 추가. 자기 검증과 실 git diff 불일치.
4. **Wave 3 dispatch 직전 component_map sub-section lock 정책 미작성**: handoff.md §미해결 결정 사항 표에서 "Wave 3 병렬 sub-agent의 component_map 동시 수정 방지" 항목을 "sub-section 분리" 결정으로 명시했으나, sub-agent 자기 검증 강제는 없었음.
5. **Step 2~7 wireframe 미작성으로 시나리오 3 실측 의존**: 시나리오 3 (Discovery 7→5 축소)에서 Step 2~7 wireframes가 placeholder뿐이라 변경 영향 실측이 "코드 형태"가 아닌 "spec 형태"로만 평가됨. Phase 3 진입 후 wireframes 작성되면 실측 변경 가능.

### 배운 것

1. **sub-agent forbidden 명시만으로는 부족** — main session에서 sub-agent 완료 후 git diff 검증이 필요. Phase 1 P-FOLDER-PARALLEL-001은 다른 폴더 분리 케이스만 다뤘지, "같은 파일 다른 sub-section" 케이스는 미커버.
2. **append-only 패턴이 잠재 conflict를 무력화** — Slice 3이 QuickInputCard를 추가한 commit이 무충돌이었던 이유는 (a) 동일 파일이지만 (b) append-only로 작성했고 (c) Slice 4 sub-agent가 component_map.md를 건드리지 않았기 때문. Phase 3+에서도 spec / docs 작업은 append-only 패턴 권장.
3. **변경성 시뮬레이션은 spec phase의 효과 검증 핵심 도구** — 5 시나리오 walkthrough가 "design system이 진짜로 변경을 쉽게 만들었는가?"를 실측. Phase 4+ 실 변경 빈도와 비교 가능 baseline 확보.
4. **ADR을 진입 시 작성하면 Slice 작업 자기 규제 효과 ↑** — ADR-010 (4-layer 4개) / ADR-011 (Variants 3개)을 Slice 1에서 작성 → 이후 Slice들이 "내가 5번째 4-layer를 추가하고 싶은가?"를 ADR-010과 대조 가능, scope creep 자동 차단.
5. **Wave 3 병렬은 "다른 폴더" + "같은 파일 다른 sub-section" 두 패턴 모두 다뤄야** — Phase 1 P-FOLDER-PARALLEL-001을 확장: sub-section 분리 정책 + 자기 검증 강제가 추가 필요.
6. **design-review Skill의 universe**: Skill 자체는 spec phase / impl phase 모두 다룰 수 있어야 하지만, 현재는 impl phase 중심. P-X3 proposal 통해 보강.

### 근본 원인 (5 Whys — P-AGENT-SCOPE-001)

**문제**: Slice 3 sub-agent가 forbidden 영역 (QuickInputCard sub-section)을 추가했고, 자기 commit message에 "Slice 4 영역 0줄 수정"으로 잘못 보고함.

```
왜 1: sub-agent 프롬프트(multi_slice_plan.md §5 Slice 3)에서 "QuickInputCard 건드리지 말 것" 명시했으나 자유도 ↑ — sub-agent가 작업 중 "Discovery Step 6에서 Direction Approval과 Quick Mode 양쪽 사용을 명시할 때, 같은 파일에 QuickInputCard도 함께 작성하는 것이 자연스럽다"고 판단했을 가능성

왜 2: 동일 파일 (component_map.md) 내 다른 sub-section 분리 점검 자동화 없음 — git diff에서 sub-section 헤더 변화만 추적하는 hook 부재

왜 3: sub-agent 완료 후 main session에서 본인 작업 외 git diff 검증 없음 — sub-agent가 commit한 변경 영역 그대로 신뢰

왜 4: worktree isolation 사용 안 함 — 같은 워크트리에서 sub-agent들이 동시 작업 → true file lock 부재 (현재 패턴은 "sub-agent별 자기 영역 commit, push race 시 rebase" 정도)

왜 5: sub-agent 분산 작업 패턴 (Phase 1 P-FOLDER-PARALLEL-001)이 "다른 폴더" 케이스만 커버, "같은 파일 다른 sub-section" 케이스 미커버. multi_slice_plan template에 "sub-section lock" / "self-check git diff" 절차 명시 없음.
```

**근본 결론**: sub-agent forbidden enforcement는 prompt 외 추가 메커니즘 (자기 검증 절차 / git diff hook / worktree isolation 중 하나) 필요.

### 부가 근본 원인 (영향-빈도)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| P-AGENT-SCOPE-001 (Slice 3 scope 침범) | 잠재적으로 큼 (다른 시나리오에서 conflict 가능), 본 사례는 무충돌 | 1회 발생 (Phase 1+2 누적) | 즉시 개선 → §개선 제안 P-X1 |
| design-review spec-only phase 부재 | 보통 (Slice 6 절차 추가 시간) | 1회 (Phase 2 spec phase) | 매뉴얼 보강 → P-X3 |
| Step 2~7 wireframe 미작성 | 작음 (Phase 3 진입 시 자동 도출) | 6개 (placeholder) | Phase 3 자연 처리 |
| sub-section lock 정책 부재 | 보통 (Phase 3+ 더 큰 파일에서 위험 ↑) | — | P-X1 흡수 |

---

## 개선 제안

### 제안 P-X1: sub-agent forbidden enforcement 강화 (우선순위: 높음)

- **무엇을**: multi_slice_plan template에 "sub-agent 완료 후 본인 staged 외 변경 없음 자기 검증" 절차 추가 + main session도 dispatch 완료 후 git diff 검증
- **왜**: P-AGENT-SCOPE-001 재발 방지. Phase 3 코드 phase는 더 큰 파일 (.tsx) 동시 작업 시 위험 ↑
- **어디에**:
  - `phases/active/{phase}/multi_slice_plan.md` template (handoff template)
  - `.claude/skills/phase-start/SKILL.md` §6.3 Surgical Scope 보강
- **구현 안**: §개선 제안 P-X1 (proposals 2026-05-27_phase-2-retrospective-proposals.md 참조)
- **상태**: meta/proposals/2026-05-27_phase-2-retrospective-proposals.md §P-X1 등록 (Phase 3 진입 전 사용자 검토)

### 제안 P-X2: 변경성 시뮬레이션 phase-complete 자동 게이트로 격상 (우선순위: 보통)

- **무엇을**: phase-complete Skill 절차에 "디자인 변경성 시뮬레이션 결과 첨부 (해당 Phase가 spec/design phase인 경우)" 단계 추가
- **왜**: 본 Phase 2의 5/5 PASS 검증이 acceptance A9 통해 강제됐는데, 후속 design 관련 phase (Phase 11+ dark mode / i18n 등) 진입 시에도 같은 절차 필요
- **어디에**: `.claude/skills/phase-complete/SKILL.md` 신규 단계 또는 §spec phase 분기

### 제안 P-X3: design-review SKILL.md에 spec-only phase 절차 추가 (우선순위: 낮음~보통)

- **무엇을**: design-review Skill에 "spec-only phase (Phase 2 같은)" 분기 절차 추가
- **왜**: 현재 SKILL.md는 impl phase 중심 (eval/design_reviews/ 저장). spec phase는 QA report 통합이 자연스러움 (본 Phase 2처럼).
- **어디에**: `.claude/skills/design-review/SKILL.md`

### 제안 P-X4 (선택): worktree isolation 도입 검토 (우선순위: 낮음, deferred)

- **무엇을**: sub-agent 병렬 dispatch 시 worktree 분리 (true file lock)
- **왜**: P-AGENT-SCOPE-001 근본 차단
- **위험**: 복잡도 ↑ (현재 patten은 단일 워크트리 + 폴더 분리로 충분히 작동). 비용 대비 이득 검토 필요.
- **상태**: deferred (Phase 3 코드 phase 진행 중 재발 시 재평가)

### 제안 P-X5 (선택): meta/patterns.md 변경성 매트릭스 표준 등록 (우선순위: 낮음)

- **무엇을**: design_handoff.md §1 5 시나리오 매핑표 패턴 (Replaceability L/M/H + 영향 파일 수)을 다른 phase (특히 contracts / api / DB schema) 변경성 평가에도 표준 적용
- **왜**: Phase 4+ MOA Lite / Phase 5 Auth 등에서 같은 매트릭스 작성하면 phase 간 비교 가능

---

## 패턴 등록 (meta/patterns.md 후보)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-AGENT-SCOPE-001** | sub-agent forbidden 영역 침범 (Slice 3 → Slice 4 sub-section 추가) | phase-2 (Wave 3) | 1회 발생, 무충돌. P-X1 proposal 등록 (Phase 3 전 검토). |
| **P-DESIGN-LAYERED-001** | 4-layer 4개 + Variants Bank 3개 minimal 정책의 변경성 보장 효과 | phase-2 (Slice 1~5) | 검증 완료 — 변경성 시뮬레이션 5/5 PASS. Phase 3+ 후속 phase에서 minimal 정책 유지 권장. |

→ Phase 1의 P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 / P-FOLDER-PARALLEL-001은 Phase 2에서 재발 없음 또는 효과 유지.

---

## Skill 사용 로그 (Phase 2 동안)

| Skill | Phase 2 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.2.0) | 1 | Phase 2 진입, 4점검 통과 |
| qa-check (v1.2.0) | 7 | 진입 점검 + Slice 1~5 + final (모든 audit_naming 0 drift, Simplicity 5/5) |
| contract-change | 0 | Phase 2 contract 변경 0 (ADR-010/011는 결정 문서, contract 변경 X) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.1.0) | 1 | Phase 2 종료 (자동 smoke test §1.5는 spec phase라 SKIP) |
| harness-audit | 0 | audit_naming 자동 호출만 (수동 Skill 호출 없음) |
| design-review | 1 | Slice 6 첫 사용 — spec-only phase 절차 부재 발견 (P-X3 proposal) |
| 기타 unused | — | eval-design / rag-design / multi-llm-validation 등 |

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md P-AGENT-SCOPE-001 신규 등록
- [x] meta/patterns.md P-DESIGN-LAYERED-001 신규 등록
- [x] meta/proposals/2026-05-27_phase-2-retrospective-proposals.md 작성 (P-X1~P-X5)
- [x] meta/skill_usage_log.md 갱신 (Phase 2 누적)
- [x] phases/active/phase-2-pwa-design/closing_notes.md 작성
- [ ] 사용자 검토 (P-X1~P-X3 우선순위 / 채택 여부 — Phase 3 진입 전 필수)
- [ ] 채택안은 contract-change Skill 또는 직접 적용 (Skill SKILL.md 갱신)
- [x] phases/active → phases/archive 이동 (git mv)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
```

---

## Phase 3 진입 권장 사항

Phase 3 (Next.js PWA UI 구현) 진입 시 본 회고 핵심 항목 반영:

1. **P-AGENT-SCOPE-001 회피**: Phase 3는 코드 phase이므로 같은 .tsx 파일 sub-agent 동시 수정 위험 ↑. multi_slice_plan.md에 "본인 staged 외 변경 없음 자기 검증" 절차 추가 (P-X1 적용 후 진입).
2. **design system 자동 매핑 첫 작업**: Tailwind config / CSS custom properties를 tokens.md 참조로 자동 매핑 (시나리오 1 자동 반영 보장).
3. **4-layer 4 컴포넌트 우선 구현**: BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard — current variant만 (alt는 Phase 4+ A/B 활성 시).
4. **D1~D5 deferred 처리**: Step 2~7 wireframe / QuickInputCard alt variants / PlanCard 4-layer 정합 / audit_page_component.ps1 점진 작성.

---

## 변경 이력

- 2026-05-27: Phase 2 회고 최초 작성 (phase-complete v1.1.0 절차 6단계 자동 호출). P-AGENT-SCOPE-001 + P-DESIGN-LAYERED-001 신규 패턴 등록.
