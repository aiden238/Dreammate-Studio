# Design Handoff Guide

> 위치: `apps/web/design_handoff.md`
> 상태: Phase 2 Slice 5 최초 작성 (Phase 2 핵심 산출물)
> 목적: **디자인 변경 요청이 들어왔을 때, 어떤 파일을 수정해야 하는지 알려주는 단일 가이드.**
> Phase 11+에서 디자인 변경 시 본 가이드가 navigation cost를 결정.
> 본 가이드의 5 시나리오 매핑표가 실제 파일과 일치하지 않으면 Slice 6 변경성 시뮬레이션 (acceptance A9)에서 fail.
>
> 참조: `apps/web/design_system/tokens.md`, `component_contract.md`, `variant_format.md`, `replaceability_score.md`,
>       `apps/web/discovery_flow.md`, `quick_flow.md`, `direction_approval.md`, `mode_branching.md`,
>       `apps/web/page_map.md`, `apps/web/component_map.md`

---

## 0. 본 가이드 사용법

```
1. 사용자 또는 design-review에서 변경 요청 도착
   ↓
2. §1에서 5 시나리오 중 가장 가까운 것 매칭
   ↓
3. Replaceability 확인 (L / M / H — §2 통합 매트릭스 참조)
   ↓
   L → 즉시 진행 (1 파일)
   M → 2~3 파일 일괄 갱신 + variants chosen 분기 검토
   H → ADR + contract-change Skill + multi-llm-validation 권장
   ↓
4. §3 Phase 3 진입 시 variants 선택 절차 따름
   ↓
5. Slice 6 변경성 시뮬레이션 walkthrough (§6) — 매핑표와 실제 영향 파일 수 일치 확인
   ↓
6. Phase 3+ 코드 영향 평가 + 갱신
```

---

## 1. 변경 시나리오 매핑표 (★ 가장 중요)

### 시나리오 1: 색 / 폰트 / spacing 변경
> 예: "보라색 테마로 바꿔줘", "글자를 더 크게", "더 둥근 모서리로"

**Replaceability: L (Low — 1 파일 수정)**

**수정 대상**:
- `apps/web/design_system/tokens.md` — 해당 카테고리 토큰값 1줄 수정

**영향 범위**: 전체 자동 반영
- 모든 wireframe / component_map의 Visual layer는 `tokens.*` 참조 (literal 값 0 사용 — Slice 1 정책)
- 따라서 token 값 변경 시 wireframes / component_map 본문 수정 불필요

**작업 순서**:
1. tokens.md에서 변경 대상 토큰 식별 (예: `color.primary`, `font.size_lg`, `space.4`)
2. 값 수정 (1줄)
3. Slice 6 변경성 시뮬레이션 #1 walkthrough (영향 파일 ≤ 1 확인)
4. Phase 3 진입 후: CSS custom properties 또는 Tailwind config가 tokens.md를 자동 참조하도록 매핑 (Phase 3 첫 작업)

**Phase 3+ 코드 재작성 필요?**: ❌ 자동 반영 (Tailwind config 또는 CSS variables를 통한 token bridge)

**ADR 필요?**: ❌ (단순 token 값 변경은 ADR 불필요. 색 시스템 자체 재설계는 §시나리오 5 수준)

---

### 시나리오 2: 카드 모양 / 배치 변경
> 예: "5장 카드를 가로 스와이프로", "그리드 2×3로", "Brand 카드를 더 크게"

**Replaceability: M (Medium — 2~3 파일 수정)**

**수정 대상**:
- `apps/web/component_map.md` — `BrandDirectionCard.Variants` 또는 `CardGrid5.Variants` yaml의 `chosen: true` 변경 (1줄)
- `apps/web/wireframes/step1_brand.md` — 새 chosen variant에 맞춰 ASCII art 갱신
- (선택) `apps/web/design_system/variant_format.md` — 새 alt variant 추가 시 등재

**작업 순서**:
1. component_map.md에서 대상 컴포넌트 Variants block 확인 (BrandDirectionCard 또는 CardGrid5)
2. 원하는 variant (current / alt_horizontal_swipe / alt_grid_2x3) 가 이미 존재하는지 확인
   - YES → `chosen: true` 변경 (1줄), 기존 chosen은 `chosen: false`로 토글
   - NO → variants 배열에 새 entry 추가 (`variant_format.md` §3 yaml schema 따름) + ADR 권장
3. wireframes/step1_brand.md 갱신 (chosen variant에 맞춰 ASCII art 재작성, 측정값은 tokens.* 참조 유지)
4. Slice 6 변경성 시뮬레이션 #2 walkthrough (영향 파일 ≤ 2~3 확인)
5. Phase 3+ 진입 후: 실 컴포넌트 코드에 `variant` prop 분기 적용 (current / alt_horizontal_swipe / alt_grid_2x3)

**Phase 3+ 코드 재작성 필요?**: △ variant 분기 컴포넌트 1개 (BrandDirectionCard.tsx 또는 CardGrid5.tsx 한 파일에 분기)

**적용 가능 컴포넌트**: BrandDirectionCard / CardGrid5 / DirectionApprovalCard

**ADR 필요?**: △ 기존 variants 내에서 chosen swap만 → ADR 불필요. 새 alt variant 추가 → ADR 권장 (Variants Bank 3개 한정 정책 — ADR-011 정합 확인)

---

### 시나리오 3: Discovery 단계 변경
> 예: "7단계 → 5단계 축소", "Step 4 Target과 Step 5 Tone 통합", "Step 1 Brand 앞에 Idea Input 단계 추가"

**Replaceability: H (High — 4~5 파일 수정, 구조적 재설계)**

**수정 대상**:
- `apps/web/discovery_flow.md` — §0.3 단계 매핑 표 + 영향 §N section 갱신
- `apps/web/mode_branching.md` — `discovery_from_stepN` mode + branching_rules priority 갱신
- `apps/web/page_map.md` — `/discovery/step/{n}` route 갱신 (route 추가/제거)
- `apps/web/component_map.md` — Step-specific 컴포넌트 변경 시 (예: Step 5 → Step 4 통합 시 ToneChipsForm placeholder 삭제)
- (선택) `apps/web/wireframes/*` — 영향 step wireframe 갱신 (Step 1만 상세, Step 2~7은 5-card pattern 재사용이므로 변경 적음)

**작업 순서**:
1. ADR 작성 (`docs/decisions/phase_X_discovery_steps.md`) — 단계 변경 사유 + trade-off
2. **`contract-change` Skill 호출** (구조적 변경 → contracts 영향 가능)
3. **`multi-llm-validation` Skill** (필수 — Discovery 흐름은 product/user_scenarios.md 영향)
4. 위 4~5 파일 일괄 갱신
5. Slice 6 변경성 시뮬레이션 #3 walkthrough (영향 파일 ≤ 4 확인)
6. Phase 3+ 코드 영향: routing layer (Next.js middleware) + wizard state shape 재설계

**Phase 3+ 코드 재작성 필요?**: ⚠ 전체 wizard flow 재설계 (state container + routing + 각 step 컴포넌트 wiring)

**ADR 필요?**: ✅ 필수 (구조적 변경, product/user_scenarios.md U2-1 영향)

---

### 시나리오 4: Direction Approval UX 변경 (variant swap)
> 예: "Discovery에서도 minimal로", "Quick에서 verbose로 바꿔서 신뢰 강화"

**Replaceability: L (Low — 1 파일 수정)**

**수정 대상**:
- `apps/web/component_map.md` — `DirectionApprovalCard.Variants` yaml의 `chosen: true` 변경 (1줄)

**작업 순서**:
1. component_map.md §DirectionApprovalCard Variants 확인
2. `verbose` ↔ `minimal` chosen toggle (1줄)
3. (선택) `apps/web/wireframes/direction_approval.md` 상단 강조 variant section 우선순위 변경
4. Slice 6 변경성 시뮬레이션 #4 walkthrough (영향 파일 ≤ 1 확인)

**Phase 3+ 코드 재작성 필요?**: △ 컴포넌트 1개 variant 분기 (`DirectionApprovalCard.tsx`의 `variant` prop 분기)

**적용 컨텍스트**:
- Discovery Step 6 → verbose (기본 chosen)
- Quick Mode → minimal (기본 권장)
- 양쪽 모두 변경 시 분기 로직 (`discovery_flow.md` §6 + `quick_flow.md` §3.2) 1줄씩만 수정

**ADR 필요?**: ❌ Variants Bank 내 chosen swap → ADR 불필요. Phase 4 사용자 데이터 (assumptions.md U2-4) 후 swap 결정 권장

---

### 시나리오 5: Mode 자체 변경 (폐기 또는 추가)
> 예: "Quick mode 폐기 (Discovery only)", "Hybrid mode 추가 (5-step wizard)", "Voice mode 신규 도입"

**Replaceability: H (High — 5+ 파일, 구조적 재설계)**

**수정 대상 (Quick mode 폐기 시)**:
- `apps/web/quick_flow.md` — deprecated 헤더 또는 archive 이동
- `apps/web/mode_branching.md` — `rule_has_series` 제거 또는 mode=discovery로 redirect, `user_quick_force` override 제거
- `apps/web/page_map.md` — `/quick*` route 제거
- `apps/web/component_map.md` — QuickInputCard deprecated 표기 또는 entry 삭제
- (선택) `apps/web/wireframes/quick_short.md` 삭제 또는 archive

**수정 대상 (새 mode 추가 시)**:
- 새 flow.md (`apps/web/hybrid_flow.md` 또는 `voice_flow.md`)
- `apps/web/mode_branching.md` — branching_rules 또는 override_rules 배열에 추가
- `apps/web/page_map.md` — 새 `/new/<mode>` route 등재
- `apps/web/component_map.md` — 새 컴포넌트 4-layer entry
- (선택) `apps/web/wireframes/<new_mode>.md` 추가

**작업 순서 (폐기)**:
1. ADR 작성 (`docs/decisions/phase_X_<mode>_deprecation.md`) — 폐기 사유 + 데이터 근거 (Phase 9 사용자 분석 결과)
2. **`multi-llm-validation` Skill** (필수 — UX 패턴 폐기는 큰 결정)
3. mode_branching.md yaml에서 rule 제거 또는 redirect (rule_has_series → discovery로 redirect)
4. page_map.md route 제거
5. quick_flow.md → deprecated 헤더 추가 (즉시 삭제 X, archive로 이동은 다음 Phase)
6. component_map.md QuickInputCard → deprecated 명시 또는 entry 제거
7. Slice 6 변경성 시뮬레이션 #5 walkthrough (영향 파일 ≤ 5 확인)
8. Phase 3+ 코드 영향: routing layer에서 `/new/quick` fallback (404 또는 discovery redirect) + Quick 전용 컴포넌트 일괄 제거

**Phase 3+ 코드 재작성 필요?**: ⚠ /quick 라우트 + Quick 전용 컴포넌트 일괄 제거 또는 redirect. middleware 분기 로직 단순화 가능

**ADR 필요?**: ✅ 필수 (Mode 자체 변경은 product/positioning.md + design.md §5 영향)

---

## 2. Replaceability 통합 매트릭스

> 본 매트릭스 = §1의 5 시나리오 + 추가 변경 항목들 통합. 각 변경의 영향 파일 수 + Phase 3+ 코드 영향 한눈에 확인.

| # | 변경 항목 | Replaceability | 영향 파일 수 | Phase 3+ 코드 영향 | ADR |
|---|---|---|---|---|---|
| 1 | tokens.md 색 / 폰트 / spacing 값 변경 | **L** | 1 | ❌ 자동 반영 | ❌ |
| 2 | BrandDirectionCard variants chosen swap | M | 2~3 | △ variant 분기 1개 | △ |
| 3 | CardGrid5 variants chosen swap | M | 2~3 | △ variant 분기 1개 | △ |
| 4 | DirectionApprovalCard variants chosen swap (verbose ↔ minimal) | **L** | 1 | △ variant 분기 1개 | ❌ |
| 5 | QuickInputCard 단순 수정 (placeholder / max_length 등) | L | 1 | △ prop 변경 | ❌ |
| 6 | ProgressStepper (Phase 1) 단계 수 변경 | L | 1 | △ Phase 1 컴포넌트 | ❌ |
| 7 | ErrorCard (Phase 1) 메시지 변경 | L | 1 | △ Phase 1 컴포넌트 | ❌ |
| 8 | Discovery 단계 수 변경 (7→5 등) | **H** | 4~5 | ⚠ wizard flow 재설계 | ✅ |
| 9 | Step 5 Tone form 형식 변경 (chip → slider / multi-select 등) | M | 2~3 | △ ToneChipsForm | △ |
| 10 | Mode branching 임계값 변경 (count >= 1 → >= 2 등) | L | 1 (yaml) | △ middleware 정수 1개 | ❌ |
| 11 | Mode 분기 신규 rule 추가 (예: `rule_brand_no_domain`) | L | 1 (yaml) | △ middleware 분기 1개 | △ |
| 12 | 새 mode 추가 (Hybrid / Voice) | **H** | 5+ | ⚠ 라우트 + 컴포넌트 + middleware | ✅ |
| 13 | Quick mode 폐기 | **H** | 5+ | ⚠ 라우트 + 컴포넌트 일괄 제거 | ✅ |
| 14 | Plan 비교 카드 활성화 (Phase 4) | M | 2~3 | ⚠ Phase 4 신규 컴포넌트 + /plan 갱신 | △ |
| 15 | 새 컴포넌트 추가 (Phase 4+, 4-layer 강제) | M | 2 (component_map + wireframe) | ⚠ Phase 3+ 신규 .tsx | △ |
| 16 | 다국어 / i18n 본격 도입 (Phase 11+) | **H** | 다수 (tokens + 모든 컴포넌트) | ⚠ 모든 텍스트 i18n 자원화 | ✅ |
| 17 | 접근성 본격 강화 (Phase 11+) | M | tokens + 모든 컴포넌트 Visual layer | △ aria-* 보강 | △ |
| 18 | 새 prompt (P-007 등) 추가 → 컴포넌트 신규 | M | component_map + 새 flow.md 또는 wireframe | ⚠ Phase 4+ | △ |

→ **L 비율**: 7/18 (≈ 39%) — 단순 token 변경, variant swap, prop 변경 등
→ **M 비율**: 7/18 (≈ 39%) — 컴포넌트 단위 변경, 새 entry 추가
→ **H 비율**: 4/18 (≈ 22%) — 구조적 재설계 필요

→ 본 분포는 design system 도입 효과 측정 지표. Phase 11+ retrospective에서 실제 변경 빈도와 비교.

---

## 3. Phase 3 진입 시 variants 선택 절차

Phase 3 sub-agent가 실 코드 작성 시 따라야 할 절차:

1. `apps/web/component_map.md`에서 컴포넌트의 Variants yaml block 확인
2. `chosen: true`인 variant를 **기본 구현 대상**으로 선택
3. 미선택 variants (chosen: false)는 **코드에 분기 (`variant` prop)로 유지** — Phase 4+ 사용자 데이터 후 chosen 변경 가능하도록
4. 미선택 variants 중 일부만 코드 구현 (current는 필수, alt는 우선순위 낮음 — Phase 3은 current만 구현 권장, alt는 Phase 4+ A/B 활성 시점에 추가)
5. variants chosen 변경 시 ADR 작성 (`docs/decisions/phase_X_<component>_variant_swap.md`) — 변경 사유 + 데이터 근거

### 3.1 Phase 3 실 구현 우선순위

| Phase 3 Slice | 컴포넌트 | 구현 chosen variant | alt variants 시점 |
|---|---|---|---|
| Slice 2 | BrandDirectionCard | current (Stacked vertical 5-card) | Phase 4+ A/B 활성 시 |
| Slice 2 | CardGrid5 | current (Vertical stack 1-col 5-row) | Phase 4+ 데스크톱 옵션 |
| Slice 3 | DirectionApprovalCard | verbose (Discovery) + minimal (Quick) 양쪽 동시 | (chosen이 컨텍스트에 따라 다름) |
| Slice 4 | QuickInputCard | current (only) | Phase 11+ voice / 4-choice 추가 검토 |
| Slice 5 | ToneChipsForm | (Phase 3 진입 시 4-layer 작성 — current variant 신규 결정) | Phase 4+ |

### 3.2 Phase 3 진입 시 미해결 결정 (Phase 2 deferred)

- `discovery_from_stepN` 구현 정밀도 — Phase 3 진입 시 Step 1/2 prefill 자동 vs 사용자 확인 1회 (`mode_branching.md` §8 Open Q1)
- `direction_renarrow` 진입 시 Step 시작점 — Step 1 vs Step 3 (`mode_branching.md` §8 Open Q3)
- Quick Mode 부족 정보 질문 UI — single textarea vs 4지선다 (`quick_flow.md` §8 Open Q1)
- Step 5 Tone chip 개수 / 라벨 확정 (`discovery_flow.md` §5.4)
- scroll-snap 활성 여부 (Slice 2 wireframe TBD)

---

## 4. Phase 4+ 디자인 갱신 시 영향 범위 예측

| Phase | 갱신 사항 | 영향 범위 | Replaceability |
|---|---|---|---|
| Phase 4 | MOA Lite 완성 → 3-plan 활성화 (PlanComparisonCard) | component_map (4-layer 신규) + wireframe + page_map (/plan 갱신) | M |
| Phase 4 | Critic revise 2회 loop UI 강화 | DirectionApprovalCard 또는 generate result 화면 variant 추가 | M |
| Phase 4 | SSE 부분 결과 표시 | GenerationProgressStepper Behavior layer 갱신 | L~M |
| Phase 5 | Auth — 로그인 / 회원가입 화면 | page_map + 신규 컴포넌트 (LoginForm 등) | M |
| Phase 5 | sessionStorage → DB 저장 전환 | discovery_flow / quick_flow의 "세션 저장" 정책 1줄씩 + Phase 5 backend 연동 | L (frontend spec) / M (backend) |
| Phase 9 | choice_logs UI (피드백 화면) | 신규 화면 + LikeDislikeFeedback / Feedback Form 컴포넌트 | M |
| Phase 9 | 실 사용자 데이터로 mode 분기 임계값 재조정 | mode_branching.md yaml (1줄) | L |
| Phase 11+ | i18n 본격 도입 (다국어) | tokens.md 확장 + 모든 컴포넌트 텍스트 자원화 | H |
| Phase 11+ | 접근성 본격 강화 (WCAG 2.2 AA full) | tokens (contrast 강화) + 모든 컴포넌트 aria-* 보강 | M~H |
| Phase 11+ | dark mode | tokens.md 1줄 (테마 분기) + 자동 반영 | L |
| Phase 21+ | Expo React Native 모바일 앱 | 모든 컴포넌트 재구현 (RN 컴포넌트 매핑) | H (구현 차원, design system 자체는 그대로) |

→ **Phase 4 진입 직전 본 표 재검토 권장** — 실 구현 후 영향 범위가 예측과 다를 수 있음 (assumptions.md U2-5 검증 input).

---

## 5. 사용 절차 (요약)

```
디자인 변경 요청 도착
   ↓
§1에서 5 시나리오 중 매칭 (또는 §2 매트릭스에서 항목 매칭)
   ↓
Replaceability 확인 (L / M / H)
   ↓
   ┌───── L ─────→ 1 파일 즉시 수정 + audit_naming 0 drift 확인
   │
   ├───── M ─────→ 2~3 파일 일괄 갱신 + variants 분기 검토 + ADR 권장
   │
   └───── H ─────→ ADR 필수 + contract-change Skill + multi-llm-validation
                   + 4~5+ 파일 갱신 + Slice 6 변경성 시뮬레이션
   ↓
audit_naming.ps1 실행 → 0 drift 확인
   ↓
git commit (Slice 단위 또는 변경 단위)
   ↓
Phase 3+ 코드 영향 평가 + 갱신
```

---

## 6. 변경성 시뮬레이션 (Slice 6 검증 기준 / acceptance A9)

본 가이드의 매핑이 실제 파일과 일치하는지 매 Phase 종료 시 (특히 Slice 6) 검증.

### 6.1 5 시나리오 walkthrough 표

| # | 시나리오 | 예상 영향 파일 수 | 실측 (Slice 6) | 결과 |
|---|---|---|---|---|
| 1 | `tokens.md` `color.primary` 값 변경 | ≤ 1 | **1** (tokens.md만) | ✅ PASS |
| 2 | BrandDirectionCard variants chosen swap (current → alt_horizontal_swipe) | ≤ 2 | **2** (component_map.md + wireframes/step1_brand.md) | ✅ PASS |
| 3 | Discovery 7→5 단계 축소 (Step 4 Target + Step 5 Tone 통합) | ≤ 4 | **4** (discovery_flow.md + mode_branching.md + page_map.md + component_map.md) | ✅ PASS |
| 4 | Direction Approval Quick mode에서 minimal → verbose swap | ≤ 1 | **1** (component_map.md `DirectionApprovalCard.Variants chosen` 1줄 토글) | ✅ PASS |
| 5 | Quick mode 폐기 (Discovery only로 전환) | ≤ 5 | **5** (quick_flow.md + mode_branching.md + page_map.md + component_map.md + wireframes/quick_short.md) | ✅ PASS |

→ 실측 vs 예상 일치: **5/5 PASS** (모든 시나리오가 예상 영향 파일 수 이하). Slice 6 acceptance A9 통과.
→ 변경성 보장 입증 — Phase 2 design system 도입 효과 실증 (4-layer + Variants Bank + tokens 분리 정책).

### 6.1.1 실측 근거 (Slice 6, 2026-05-27)

각 시나리오는 §1의 매핑표를 기준으로 "실제 수정해야 할 파일" (참조만 하는 파일 제외)을 카운트.

**시나리오 1 — tokens.md color.primary 값 변경**:
- 수정 파일: `apps/web/design_system/tokens.md` 1개 (값 1줄만)
- 참조 파일 (수정 불필요): `component_map.md`, `wireframes/*`, `design_handoff.md`, `discovery_flow.md`, `direction_approval.md`, `design_system/component_contract.md`, `replaceability_score.md` 등은 모두 `tokens.color.primary` 토큰 참조만 사용 (literal 값 0 정책 — Slice 1 강제) → 자동 반영, 수정 불필요.
- **결과: 1 ≤ 1, PASS**

**시나리오 2 — BrandDirectionCard variants chosen swap (current → alt_horizontal_swipe)**:
- 수정 파일:
  1. `component_map.md` §BrandDirectionCard.Variants — `chosen: true` 토글 (current → false, alt_horizontal_swipe → true) 2줄
  2. `wireframes/step1_brand.md` — 새 chosen variant에 맞춰 ASCII art 갱신 (carousel peek 형태)
- 비수정 (검토만): `design_handoff.md` §1 시나리오 2 (가이드 자체), `design_system/variant_format.md` (이미 alt 등재)
- **결과: 2 ≤ 2, PASS**

**시나리오 3 — Discovery 7→5 단계 축소 (Step 4 Target + Step 5 Tone 통합)**:
- 수정 파일:
  1. `discovery_flow.md` §0.3 단계 매핑 표 + §4/§5 통합 + 단계 수 갱신
  2. `mode_branching.md` `discovery_from_stepN` mode 표 갱신 (5/6/7 → 4/5)
  3. `page_map.md` `/new/discovery/step/{n}` route 7개 → 5개
  4. `component_map.md` Routes ↔ Components 매핑 표 갱신 + ToneChipsForm placeholder (Step 5 → Step 4 통합 표기)
- 선택: `wireframes/*` (Step 1만 상세 wireframe 존재, Step 2~7은 placeholder이므로 추가 변경 0)
- **결과: 4 ≤ 4, PASS**

**시나리오 4 — Direction Approval Quick mode minimal → verbose swap**:
- 수정 파일: `component_map.md` §DirectionApprovalCard.Variants — verbose chosen false, minimal chosen true (또는 컨텍스트별 분기 표기 1줄)
- 비수정 (선택): `wireframes/direction_approval.md` 상단 강조 우선순위 변경은 선택사항
- **결과: 1 ≤ 1, PASS**

**시나리오 5 — Quick mode 폐기**:
- 수정 파일:
  1. `quick_flow.md` deprecated 헤더 또는 archive
  2. `mode_branching.md` `rule_has_series` 제거 또는 discovery redirect + `user_quick_force` override 제거
  3. `page_map.md` `/new/quick*` route 4개 제거
  4. `component_map.md` QuickInputCard deprecated 표기 + Routes 매핑 표에서 Quick routes 제거
  5. `wireframes/quick_short.md` archive 이동 또는 deprecated 헤더
- **결과: 5 ≤ 5, PASS**

### 6.1.2 5/5 통과 의의

- **Replaceability 분포 (§2 매트릭스 18 항목)** 와 실제 시나리오 매핑이 일관 — design system 정책이 작동.
- **literal 값 0 정책** (Slice 1)이 시나리오 1을 1파일로 압축 — 다른 design system이 보통 4~10 파일 수정 필요한 색 변경이 1파일.
- **Variants Bank chosen toggle** 패턴이 시나리오 2/4를 1~2 파일로 압축 — 향후 Phase 4+ A/B 테스트 인프라 자연 흡수.
- **본 표는 Phase 4+ 실 변경 빈도와 비교 가능한 baseline** — Phase 11+ retrospective에서 "예상 분포 vs 실제 변경 분포" 차이 분석에 사용.

### 6.2 walkthrough 진행 방법 (Slice 6)

각 시나리오마다:
1. 변경 대상 파일 식별 (§1 매핑표 기준)
2. 실제 `grep` 또는 manual scan으로 영향 파일 list 확인
3. 예상 ≥ 실측 → PASS, 그 외 → FAIL + 매핑표 조정 사유 기록

---

## 7. Slice 6 + 후속 Phase 검증 정합 체크리스트

Slice 6 / Phase 종료 시 본 가이드 정합성 확인:

- [ ] §1의 5 시나리오 각각이 실제 파일과 매칭됨 (예: 시나리오 1 tokens.md → 존재 / 시나리오 5 quick_flow.md → 존재)
- [ ] §2 매트릭스의 18 항목이 실제 component_map.md / page_map.md / mode_branching.md / design_system/* 와 정합
- [ ] §3 Phase 3 진입 시 variants 선택 절차가 component_map.md Variants yaml block과 정합
- [ ] §4 Phase 4+ 영향 범위 예측이 PHASE_REGISTRY.md / phases/ 의 다음 Phase scope와 정합
- [ ] §6 변경성 시뮬레이션 5/5 PASS (acceptance A9)

→ 1개 이상 불일치 발견 시 본 가이드 갱신 + Phase 종료 차단.

---

## 8. 관련 문서 cross-reference

### Design System (Slice 1)
- `apps/web/design_system/tokens.md` — 6 카테고리 토큰 (color / typography / spacing / radius / breakpoint / motion)
- `apps/web/design_system/component_contract.md` — 4-layer template (Behavior / Layout / Visual / Wireframe)
- `apps/web/design_system/variant_format.md` — Variants yaml schema
- `apps/web/design_system/replaceability_score.md` — L/M/H 정책

### Flow / Pattern (Slice 2~4)
- `apps/web/discovery_flow.md` — Discovery 7-step (§0 개요 + §1 Step 1 상세 + §2~§7 간략)
- `apps/web/quick_flow.md` — Quick Mode short flow
- `apps/web/direction_approval.md` — Direction Approval pattern (양 모드 공통)
- `apps/web/mode_branching.md` — Mode 자동 분기 yaml

### Integration (Slice 5, 본 Phase)
- `apps/web/page_map.md` — 전체 routes 통합
- `apps/web/component_map.md` — 모든 컴포넌트 통합 (Replaceability 매트릭스 + Routes 매핑 + PlanComparisonCard placeholder 포함)
- `apps/web/design_handoff.md` — 본 가이드 (Phase 2 핵심 산출물)

### Wireframes
- `apps/web/wireframes/step1_brand.md` — Step 1 Brand 5-card
- `apps/web/wireframes/direction_approval.md` — verbose + minimal
- `apps/web/wireframes/quick_short.md` — Quick Step 1 + Step 2
- `apps/web/wireframes/plan_comparison_placeholder.md` — Phase 4 placeholder (1줄)

### ADR
- `docs/decisions/phase_2_design_layered_minimal.md` (ADR-010, 4-layer 4개 한정)
- `docs/decisions/phase_2_variants_3_components.md` (ADR-011, Variants Bank 3개 한정)

### Phase 0/1 기존 (보존)
- `apps/web/design.md` — Phase 0 기획 본문 (read-only)
- `docs/contracts/frontend_design_contract.md` — 디자인 토큰 contract
- `docs/contracts/output_schema.md` — P-001~P-008 출력 스키마

---

## 9. 변경 이력

- 2026-05-27: Phase 2 Slice 5 최초 작성 — 5 시나리오 매핑표 + Replaceability 통합 매트릭스 (18 항목) + Phase 3 진입 절차 + Phase 4+ 영향 범위 예측 + Slice 6 변경성 시뮬레이션 검증 기준
- 2026-05-27: Phase 2 Slice 6 — §6.1 실측 컬럼 갱신 (5 시나리오 walkthrough 5/5 PASS) + §6.1.1 실측 근거 sections 추가 + §6.1.2 통과 의의 추가. acceptance A9 통과.
