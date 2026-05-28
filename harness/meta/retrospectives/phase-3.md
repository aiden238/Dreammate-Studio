# Retrospective: Phase 3 — Next.js PWA 기본 UI 구현 (Discovery + Quick 분기)

> 작성일: 2026-05-28
> 종류: phase
> 범위: Phase 3 (전체 — pre-entry P-X1 적용 → 진입 점검 → 6 Slices → final QA → archive)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete v1.1.0 절차 6단계 (회고)

---

## 사실 요약

Phase 3 (Next.js PWA 기본 UI 구현 — Discovery + Quick 분기)을 **2026-05-28 단일 일자**에 pre-entry부터 archive까지 완수.

Pre-entry: P-X1 (Phase 2 회고 결과 P-AGENT-SCOPE-001 대응안) 선적용 → phase-start v1.2.0 → v1.3.0 (§6.3 sub-agent §SELF-VERIFICATION 절차 추가). commit `3d0b0fb`.

진입 점검: phase-start v1.3.0 §6 4점검 (audit_naming 0 drift, 4 조정 적용 — P-X1 / Thin Vertical / D3 Phase 4 이관 / component_map.md read-only 절대).

6 Slices를 5 Waves로 분해:
- Wave 1 (Slice 1): Foundation — Tailwind config tokens 매핑 + globals.css CSS variables + lib/design_tokens.ts
- Wave 2 (Slice 2): **Thin Vertical** — Discovery Step 1 end-to-end (BrandDirectionCard + CardGrid5 + /step/1 page + state machine)
- Wave 3 (Slice 3+4 병렬): Discovery Step 2~7 확장 ∥ Quick Mode 4 routes
- Wave 4 (Slice 5): Mode Branching middleware + /new redirect + ADR-013
- Wave 5 (Slice 6): final QA + audit_page_component + smoke + meta-retrospective + archive

총 5 sub-agent dispatch. 충돌 0건, push race 0건 (Wave 3 Slice 3 먼저 push → Slice 4 정상 import). **§SELF-VERIFICATION 5/5 PASS**. **component_map.md 6연속 0줄 보존** (조정 4번 강제 성공). **변경성 시뮬레이션 4/5 PASS + 1 WARN** (시나리오 5 코드 phase 자연 증가).

회고 핵심 발견:
- ★ **P-X1 효과 입증**: Phase 2 P-AGENT-SCOPE-001 (sub-agent forbidden 침범)이 Phase 3에서 0건 재발. 5 sub-agent 모두 §SELF-VERIFICATION PASS.
- ★ **Thin Vertical 패턴 효과**: Slice 2를 Discovery Step 1 end-to-end로 정의 → Slice 3이 패턴 복제만으로 Step 2~7 확장 (drift 위험 ↓).
- ★ **Wave 3 병렬 race 깔끔**: Slice 3 (Discovery Step 2~7, daa3e18) 먼저 push → Slice 4 (Quick Mode, 1e4f536) 정상 import. P-FOLDER-PARALLEL-001 (Phase 1) + P-X1 (Phase 2 회고) 결합 효과.
- ★ **D3 Phase 4 이관 (조정 3번 준수)**: PlanCard 4-layer 정합을 Phase 4 PlanComparisonCard와 함께 재정의로 미루어 Phase 3 scope 부풀림 방지.

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-28 단일일 (다중 세션) |
| Total commits (Phase 3) | 7 (pre-entry P-X1 + entry + Slice 1~5 + Slice 6 본 commit) |
| 신규 파일 (apps/web/* + scripts) | 20 (8 page.tsx + 5 component.tsx + 5 lib/.ts + 2 audit script) |
| 수정 파일 | 2 (tailwind.config.ts + globals.css) |
| 줄 수 변화 (apps/web/) | +2905 / -34 (Phase 3 코드) |
| 신규 ADR | 1 (ADR-013 Mode Branching Middleware) |
| 4-layer 컴포넌트 코드 구현 | 4 / 4 (BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard) |
| ToneChipsForm | 1 (Step 5 5-card 예외 form) |
| sessionStorage state machines | 3 (wizard.ts / discovery_state.ts / quick_state.ts) |
| Routes 신규 | 8 (/new + 7 discovery/[n]+1 + 4 quick) — 실 파일 8 page.tsx (dynamic step/[n] 1 + explicit step/1 1) |
| audit_naming 결과 | 0 drift (Slice 1~6 모두) |
| audit_page_component (신규) 결과 | 0 drift (Slice 6 첫 실행) |
| Sub-agent dispatch | 5 (Wave 1 + Wave 2 + Wave 3×2 + Wave 4) — Wave 5 본 회고는 main session |
| QA reports | 7 (entry + Slice 1~5 + final) |
| pytest 영향 | 0 (Phase 3 backend 무변경 — 62/62 유지) |
| next build | 11 routes static prerender OK |
| tsc / lint | 0 errors / clean |
| 변경성 시뮬레이션 | 4/5 PASS + 1 WARN (시나리오 5 코드 phase 자연 증가) |
| design-review impl | 7 원칙 모두 정합 PASS |
| **P-X1 §SELF-VERIFICATION** | **5/5 PASS (5연속)** ★ |
| **component_map.md deviation** | **0건 (6연속, Slice 1~6)** ★ |
| 식별된 P-pattern (Phase 3 신규) | 2 (P-X1-EFFECT-001 / P-THIN-VERTICAL-001) |
| Phase 3 deferred → Phase 4 이관 | D2 / D3 / D4 (D5는 Slice 6 완료) |

---

## 분석

### 잘된 것

1. **★ P-X1 효과 즉시 입증**: Phase 2 회고에서 발견된 P-AGENT-SCOPE-001 (sub-agent forbidden 침범)이 Phase 3 코드 phase (위험 ↑)에서 0건 재발. 5 sub-agent 모두 §SELF-VERIFICATION PASS, main session 사후 git diff 검증도 0 deviation. **proposal → 적용 → 효과 측정 사이클의 모범 사례**.
2. **★ component_map.md 6연속 0줄 보존 (조정 4번)**: Phase 3 진입부터 Slice 6까지 component_map.md 직접 수정 시도 0건. spec ↔ 코드 drift 발견 시 deviations.md 기록 절차도 0건 트리거 (실 drift도 0건).
3. **★ Thin Vertical 패턴 효과**: Slice 2를 Discovery Step 1 end-to-end로 정의 (5 파일 = component + page + state + token + Tailwind 연결) → Slice 3 (Step 2~7 확장)이 dynamic route + 패턴 복제로 진행. drift 0건 + 자기 검증 PASS.
4. **Wave 3 병렬 push race 깔끔**: Slice 3 (Discovery, daa3e18) 먼저 push → Slice 4 (Quick, 1e4f536) 정상 작업. P-FOLDER-PARALLEL-001 (다른 폴더 분리) + P-X1 (자기 검증) 결합으로 conflict 0건. handoff.md §충돌 분석 매트릭스 효과적.
5. **D3 Phase 4 이관 (조정 3번 준수)**: PlanCard 4-layer 정합을 Slice 6에서 처리하지 않고 Phase 4로 미룸 → Phase 3 scope 부풀림 방지. acceptance A2~A10 모두 PASS / Slice 6 부담 최소화.
6. **audit_page_component.ps1 (D5) 첫 실행 0 drift**: page_map.md ↔ 실 routes / component_map.md ↔ 실 components 정합 자동 검사. dynamic route (/step/[n]) 정규화 + Phase 4+ deferred placeholder 인식 로직 포함. Phase 3 종료 시점 자동 회귀 도구 확보.
7. **next build 11 routes static prerender + tsc / lint 0**: Phase 1 baseline (pytest 62/62) 유지 + Phase 3 신규 routes 모두 SSG. type safety + lint clean.
8. **literal hex 0건 정책 코드 강제**: 모든 .tsx 컴포넌트가 Tailwind class (tokens.* 매핑) 또는 CSS variable 참조만 사용. 시나리오 1 (token 변경 → 1~2 파일 swap) 회귀 보장.

### 안 된 것

1. **변경성 시나리오 5 (Quick mode 폐기) 1 WARN**: Phase 2 예상 ≤5 파일 vs Phase 3 실측 7~8 파일. 이유: Phase 2는 spec 측면 (quick_flow / mode_branching / page_map / component_map / wireframes) 5개, Phase 3는 코드 측면 (4 page.tsx + 1 component + 1 state.ts + 1 mode_branching.ts + 1 /new/page.tsx) 추가 7~8개. **수용 가능 — 코드 phase 자연 증가**. Phase 2 매핑표 (design_handoff.md §6.1)에 "코드 phase 추가 영향" 칸 추가 권장 (Y-X 후보).
2. **audit_page_component.ps1 false-positive 가능성**: 첫 실행에서 case-sensitive matching이 필요했음 (PowerShell `-match`는 case-insensitive default). 추후 Phase 4+ 진입 시 spec_only / actual_only 분류 정밀도 재검토 필요 (특히 새 컴포넌트 추가 시 ## 헤더 vs table-row 구분).
3. **Wave 3 병렬 sub-agent 작업 시간 (정성적)**: 동일 폴더 (apps/web/lib + components) 다른 sub-section 작업이라 P-FOLDER-PARALLEL-001 (다른 폴더 분리) 패턴 적용 어려움. Slice 3은 discovery/* + lib/discovery_state.ts, Slice 4는 quick/* + lib/quick_state.ts로 sub-폴더 분리 → 무충돌. **새 패턴 P-SUB-PATH-PARALLEL-001 등록 후보** (또는 P-FOLDER-PARALLEL-001 확장).
4. **D1 (Step 2~7 wireframe 상세) 미작성**: Phase 2 dependencies.md에서 D1을 Phase 3 진입 시 자동 도출로 두었으나, Phase 3는 코드 phase라 wireframe 별도 작성 없이 코드 직접 작성. spec ↔ 코드 정합은 OK (audit_page_component 0 drift) but Phase 11+ design review 시점에 wireframes/step{2,3,4,6,7}.md placeholder가 그대로 남음. Phase 4 진입 직전 또는 Phase 11+에서 처리 권장.

### 배운 것

1. **proposal → 적용 → 효과 측정 1 phase 만에 가능**: P-X1을 Phase 2 회고 → 사용자 검토 → Phase 3 pre-entry 적용 → Phase 3 5 Slice 효과 측정 사이클로 완성. proposal 절차의 유효성 입증.
2. **§SELF-VERIFICATION이 multi-agent dispatch에서 conflict 회피의 본질**: 폴더 분리 (P-FOLDER-PARALLEL-001)만으로는 같은 .tsx 파일 / 같은 lib/* 동시 수정 위험을 차단하지 못함. §SELF-VERIFICATION은 sub-agent가 본인 staged 외 변경을 자체 점검 + main session 사후 검증의 2-단계 차단. spec phase보다 code phase에서 효과 ↑.
3. **Thin Vertical Slice는 코드 phase entry의 표준 패턴**: Slice 1 (Foundation 5 파일)에서 시작하면 추상도 ↑로 진행 비효율. Slice 2 (Thin Vertical end-to-end)에서 시작하면 한 페이지가 완전히 작동 → Slice 3은 같은 패턴 복제로 안전. phase-start §6.2 Simplest Slice의 강화 형태.
4. **Phase 2 spec 변경성 시뮬레이션 5/5 PASS가 Phase 3 코드에서도 4/5+1 WARN 유지**: design system 도입 효과가 spec ↔ code 양쪽에서 입증. 시나리오 5 (Quick mode 폐기)의 +2~3 파일은 코드 phase 자연 증가, 모듈성 자체는 유지 (4 page.tsx + 1 component + 1 state.ts로 깔끔 분리).
5. **조정 4번 (component_map.md read-only 절대) 의 가치**: deviation 발견 시 spec 파일 직접 수정 X → deviations.md 기록만 정책이 Phase 3 6 Slice 모두 깨끗하게 진행 (0 deviation entry). spec ↔ 코드 drift 자동 검출 도구 (audit_page_component.ps1) 보강 후 검증 가능.
6. **dynamic Next.js route 정규화 필요**: `/new/discovery/step/[n]` 같은 dynamic route는 audit_page_component.ps1에서 spec /step/2~7과 자동 매핑 처리 필요. PowerShell `-cmatch` (case-sensitive) 사용 + 정규화 로직이 핵심. 향후 다른 dynamic route 추가 시 같은 패턴 적용.

### 근본 원인 (5 Whys — 발생한 1 WARN 분석)

**문제**: 변경성 시나리오 5 (Quick mode 폐기) Phase 2 예상 ≤5 파일 vs Phase 3 실측 7~8 파일.

```
왜 1: Phase 3 코드 phase는 동일 spec을 더 많은 파일로 분할 — Next.js app router 컨벤션상 route 1 = page.tsx 1 파일
왜 2: 4 Quick routes (page / clarify / direction / generate) + 1 component (QuickInputCard.tsx) + 1 state (quick_state.ts) + 1 mode_branching.ts 수정 + 1 /new/page.tsx 수정 = 8 파일
왜 3: Phase 2 design_handoff.md §6.1 시나리오 5 영향 예측은 spec 파일 단위 (quick_flow / mode_branching / page_map / component_map / wireframes) 5개로 작성됨 — 코드 phase의 page.tsx 단위 분할 미고려
왜 4: design_handoff.md §6.1 매핑표가 "spec 변경" 관점만 다루고 "code 변경" 관점 미분리
왜 5: Phase 2 시점에는 Phase 3 코드 구조 미확정 — Next.js app router 컨벤션의 file-per-route 영향을 예측하기 어려웠음. spec phase의 예측 한계.
```

**근본 결론**: design_handoff.md §6.1 매핑표에 "spec 영향" / "code 영향" 칸 분리 권장 (Y-X 후보 — P-X2 흡수 가능). Phase 4+ design phase 재진입 시 적용.

### 부가 근본 원인 (영향-빈도)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| 시나리오 5 WARN | 보통 (spec / code 영향 분리 미흡) | 1회 (Phase 3) | Y-X 후보 (P-X2 흡수) |
| audit_page_component 미세 false-positive 가능성 | 작음 (Phase 4+ 새 컴포넌트 추가 시) | 0회 (현재) | Phase 4+ 진입 시 재검토 |
| Sub-path 분리 (lib/discovery vs lib/quick) | 보통 — 새 패턴 등록 가능 | 1회 (Phase 3 Wave 3) | 패턴 등록 후보 (P-FOLDER-PARALLEL-001 확장) |

---

## 개선 제안

### Y-X1 (선택, 우선순위: 낮음~보통): design_handoff §6.1 매핑표에 "spec 영향" / "code 영향" 칸 분리

- **무엇을**: design_handoff.md §6.1 변경성 매핑표에 "예상 영향 (spec)" / "예상 영향 (code)" 칸 분리
- **왜**: Phase 3 시나리오 5 WARN의 근본 원인 — spec / code 영향 단위가 다름 (file-per-route 분할)
- **어디에**: Phase 4+ design phase 재진입 시점 (Phase 11+ dark mode / i18n)
- **관련**: P-X2 (변경성 시뮬 phase-complete 게이트)와 통합 가능
- **상태**: Phase 11+ 활용 시점에 사용자 검토

### Y-X2 (선택, 우선순위: 낮음): audit_page_component.ps1 false-positive 감소 가이드

- **무엇을**: audit_page_component.ps1 사용 가이드 (Phase 4+ 새 컴포넌트 추가 시 stop_list / spec_only 분류 정밀도)
- **왜**: Phase 3는 안정 작동했으나 Phase 4+ PlanComparisonCard + 새 routes 추가 시 false positive 발생 가능
- **어디에**: `scripts/audit_page_component.ps1` header 주석 또는 별도 README
- **상태**: Phase 4 진입 직전 사용자 검토

### Y-X3 (선택, 우선순위: 낮음): Sub-path 분리 패턴 표준 등록 (P-FOLDER-PARALLEL-001 확장)

- **무엇을**: 같은 폴더 다른 sub-path (lib/discovery vs lib/quick) 분리도 P-FOLDER-PARALLEL-001 효과 입증 → 패턴 확장
- **왜**: Phase 3 Wave 3 무충돌 효과 측정
- **어디에**: `meta/patterns.md` P-FOLDER-PARALLEL-001 보강 또는 새 P-SUB-PATH-PARALLEL-001
- **상태**: Phase 4+ Wave 3 재발 시 검토

### Phase 2 P-X 후속 재평가

- **P-X1 (sub-agent enforcement)**: ✅ accepted + applied, **5/5 효과 입증 — 유지**
- **P-X2 (변경성 시뮬 phase-complete 게이트)**: 미적용 상태 — Phase 4 진입 전 채택 권장. Phase 3 acceptance A9에서 manual walkthrough 진행, 자동 게이트화하면 Phase 11+ design phase 시점에 자동 트리거 가능
- **P-X3 (design-review spec-only)**: 미적용 — Phase 11+ design phase 재진입 시점에 재평가 (Phase 3는 impl phase라 미적용 적정)
- **P-X4 (worktree isolation)**: deferred — P-X1만으로 5/5 효과 충분, deferred 유지
- **P-X5 (매트릭스 표준 등록)**: deferred — P-X2 통합 자연 흡수 가능

---

## 패턴 등록 (meta/patterns.md 후보)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| **P-X1-EFFECT-001** | P-X1 §SELF-VERIFICATION 5연속 PASS 효과 측정 | phase-3 (Slice 1~5) | 신규 등록 (Phase 3) — P-AGENT-SCOPE-001 mitigation 입증 |
| **P-THIN-VERTICAL-001** | Thin Vertical Slice 효과 (Phase 3 Slice 2 = Discovery Step 1 end-to-end → Slice 3 패턴 복제) | phase-3 (Slice 2~3) | 신규 등록 (Phase 3) — 코드 phase entry 표준 패턴 |

→ Phase 1/2 누적 패턴:
- P-DRIFT-001 (mitigated) / P-SLICE-001 / P-GRACEFUL-001 / P-FOLDER-PARALLEL-001 / P-AGENT-SCOPE-001 (mitigated by P-X1) / P-DESIGN-LAYERED-001 (Phase 3 코드 입증) — 모두 효과 유지

---

## Skill 사용 로그 (Phase 3 동안)

| Skill | Phase 3 사용 횟수 | 비고 |
|---|---|---|
| phase-start (v1.3.0) | 1 | Phase 3 진입, P-X1 적용된 v1.3.0 사용 |
| qa-check (v1.2.0) | 6 | 진입 점검 + Slice 1~5 + final (모든 audit_naming 0 drift, Simplicity 5/5) |
| contract-change | 1 | P-X1 pre-entry — phase-start v1.2.0 → v1.3.0 (commit 3d0b0fb) |
| meta-retrospective | 1 (지금) | 본 문서 |
| phase-complete (v1.1.0) | 1 | Phase 3 종료 (automated smoke test §1.5 Phase 3 smoke 적용) |
| design-review | 1 | Slice 6 두 번째 사용 (Phase 2 spec phase 첫 사용 후 Phase 3 impl phase 두 번째) |
| harness-audit | 0 | audit_naming + audit_page_component 자동만 (수동 Skill 호출 없음) |
| 기타 unused | — | eval-design / rag-design / multi-llm-validation 등 (Phase 4+ 활성화 예상) |

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [x] meta/patterns.md P-X1-EFFECT-001 신규 등록
- [x] meta/patterns.md P-THIN-VERTICAL-001 신규 등록
- [x] meta/proposals/2026-05-28_phase-3-retrospective-proposals.md 작성 (Y-X1~Y-X3, 선택)
- [x] meta/skill_usage_log.md 갱신 (Phase 3 누적)
- [x] phases/active/phase-3-pwa-impl/closing_notes.md 작성
- [ ] 사용자 검토 (Y-X1~Y-X3 우선순위 / 채택 여부 — Phase 4 진입 전 선택)
- [x] phases/active → phases/archive 이동 (git mv)
- [x] PROJECT_STATE / PHASE_REGISTRY / 00_START_HERE / README 갱신
```

---

## Phase 4 진입 권장 사항

Phase 4 (FastAPI 기본 백엔드 구현 확장) 진입 시 본 회고 핵심 항목 반영:

1. **P-X1 유지 + §SELF-VERIFICATION 6/6 강제**: Phase 4는 backend phase — apps/web/* 변경 적을 듯하나 ai_system / docs/contracts / output_schema 동시 수정 위험 있음. sub-agent 5/5 PASS 유지.
2. **D2 / D3 / D4 처리**: PlanCard 4-layer 정합 (D3, 조정 3번 — PlanComparisonCard와 함께 재정의) / PlanComparisonCard 상세 spec (D4) / QuickInputCard alt variants (D2 — Phase 9 데이터 베이스).
3. **3-plan generate endpoint 활성화**: Phase 1 단일 plan → Phase 4 3-plan (P-006 plan_candidates) 전환. Critic revise loop + Rewriter 도입.
4. **변경성 시뮬레이션 자동 게이트 (P-X2) 채택 검토**: Phase 11+ design phase 재진입 시점 효과 측정.
5. **audit_page_component.ps1 false-positive 가이드 (Y-X2) 적용**: 새 컴포넌트 추가 시 stop_list 갱신 절차 명문화.

---

## 변경 이력

- 2026-05-28: Phase 3 회고 최초 작성 (phase-complete v1.1.0 절차 6단계 자동 호출). **P-X1-EFFECT-001 + P-THIN-VERTICAL-001 신규 패턴 등록**. P-AGENT-SCOPE-001 mitigation 5/5 입증.
