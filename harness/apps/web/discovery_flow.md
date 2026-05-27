# Discovery Wizard Flow

> 위치: `apps/web/discovery_flow.md`
> 상태: Phase 2 Slice 2 baseline (2026-05-27)
> 적용 범위: §0 개요 + §1 Step 1 Brand 상세. §2~§7는 Slice 3에서 4줄 명세로 추가.
> 참조: `apps/web/design.md` §11, `apps/web/page_map.md`, `docs/contracts/output_schema.md` §3~§9, `apps/web/design_system/component_contract.md`
>
> 원칙: 7단계 카드 wizard. Mode 자동 분기 시 Brand 컨텍스트 없는 신규 사용자 → Discovery 강제.
> 각 단계는 5-card pattern (AI 추천 4 + user_direct_input 1) 또는 form 변형.

---

## 0. 개요

### 0.1 흐름 도식

```
Step 1 Brand (P-001)
   ↓
Step 2 Domain (P-002)
   ↓
Step 3 Series (P-003)
   ↓
Step 4 Target (P-004)
   ↓
Step 5 Tone (P-004 form 변형 — 5-card 예외)
   ↓
Step 6 Direction Summary (P-005) — DirectionApprovalCard 사용 (direction_approval.md 참조 — Slice 3)
   ↓
Step 7 Generate (P-006) — GenerationProgressStepper 4단계 (Intent / RAG / Planning / Critic)
   ↓
→ /plan 결과 페이지
```

### 0.2 공통 정책

- 모든 step은 progress stepper 표시 (`current / total=7`)
- back navigation: 이전 step state 보존 (session storage)
- forward navigation: 다음 step 진입 시 state propagation (선택값 + user_direct_input 텍스트)
- mobile 360px first (`apps/web/design.md` §17, `tokens.md` §5.1 `bp.mobile`)
- a11y: `aria-current="step"` + focus management (`docs/contracts/frontend_design_contract.md` §5)
- 세션 저장: Phase 2 spec 단계 — sessionStorage (Phase 5에서 Auth + DB 저장 도입 시 교체)
- 응답 대기 중 partial result 즉시 표시 (Phase 4+ SSE 도입 후 활성)

### 0.3 단계별 prompt 매핑 (output_schema 참조)

| Step | prompt | 패턴 | 입력 | output_schema § |
|---|---|---|---|---|
| 1 | P-001 | `BrandDirectionCard` × 5 (`CardGrid5`) | user 초기 입력 / 신규 회원 | §3 brand_direction_cards |
| 2 | P-002 | BrandDirectionCard 변형 × 5 | Step 1 선택 | §4 domain_direction_cards |
| 3 | P-003 | BrandDirectionCard 변형 × 5 | Step 1+2 | §5 series_cards |
| 4 | P-004 | BrandDirectionCard 변형 × 5 | Step 1~3 | §6 target_cards |
| 5 | P-004 | **form 패턴 (5-card 예외)** — 슬라이더 또는 다중선택 | Step 1~4 | §7 tone_card (form) |
| 6 | P-005 | `DirectionApprovalCard` | Step 1~5 종합 | §8 direction_summary |
| 7 | P-006 | `GenerationProgressStepper` 4단계 (Intent → RAG → Planning → Critic) | Direction 승인 | §9 plan_generation |

→ Step 2~7 상세는 Slice 3에서 4줄 명세로 추가 (각 step의 입력/출력/다음 단계만).

### 0.4 공통 구성 요소

- **헤더**: WizardStepHeader (현재 step 번호 + 제목 + 이전 단계 버튼)
- **본문**: 각 step의 5-card 또는 form (CardGrid5 + BrandDirectionCard × 5 또는 form 변형)
- **하단**: SubmitButton (sticky bottom) — 1개 선택 후 활성, "다음 단계로 ▶"
- **에러 상태**: ErrorCard (Phase 1 기존, INV-001 / E-LLM-* 시리즈) — `docs/contracts/error_response_contract.md` 참조
- **스킵 정책** (`page_map.md` §5 정합): Brand / Domain 필수, Series / Target / Tone 스킵 허용

### 0.5 라우팅 (Phase 3 진입 시 활성)

```
/new                       → Mode 자동 분기 router (page_map.md §Mode 분기)
/new/discovery             → /new/discovery/step/1 (첫 진입)
/new/discovery/step/1      → Step 1 Brand
/new/discovery/step/2      → Step 2 Domain
...
/new/discovery/step/6      → Direction Summary (DirectionApprovalCard)
/new/discovery/step/7      → Generation Progress
```

→ Phase 2는 spec only. 실 routing 구현은 Phase 3.

---

## 1. Step 1: Brand 방향 카드

### 1.1 목적

- 신규 사용자 onboarding 첫 화면
- 사용자가 자기 브랜드 방향을 선택 (AI 추천 4 + 직접 입력 1)
- 결과: 다음 step (Domain)으로 `brand_direction` 컨텍스트 전달

### 1.2 사용 컴포넌트

- `CardGrid5` (5장 배치 컨테이너) — `component_map.md` 참조
- `BrandDirectionCard` × 5 (개별 카드, kind=ai_suggestion × 4 + kind=user_direct_input × 1) — `component_map.md` 참조
- `SubmitButton` (Phase 1 기존, `apps/web/components/SubmitButton.tsx`) — 비활성 → 1개 선택 후 활성
- `ProgressStepper` (Phase 1 기존 활용 또는 wizard 전용 WizardStepHeader 별도 신규) — Slice 3에서 결정
- `ErrorCard` (Phase 1 기존) — 응답 실패 시

### 1.3 API 호출

- **진입 시**:
  - request: `POST /api/v1/discovery/brand` (또는 wizard endpoint — Phase 4 결정)
  - body: `{ idea: string, locale: "ko-KR" }` (사용자 초기 자유 입력 또는 빈 값)
  - response: P-001 결과 = `brand_direction_cards` envelope (4 cards + 1 user_input_slot)
- **선택 시**:
  - Phase 2 spec 단계: sessionStorage에 저장 → 다음 step 라우팅
  - Phase 4 wizard endpoint 활성 시: `POST /api/v1/discovery/select` (현재 step + 선택 card_id)

### 1.4 State / Events

```
state:
  - cards: Card[] (4 AI + user_input slot)
  - selectedCardId: string | null   ('user_input' 또는 uuid)
  - userInputText: string | null    (user_direct_input일 때만)
  - loading: boolean
  - error: ErrorEnvelope | null

events:
  - onCardSelect(card_id: string)      → BrandDirectionCard 컴포넌트에서 emit
  - onUserInputChange(text: string)    → user_direct_input 카드의 textarea에서 emit
  - onNext()                            → 다음 step 라우팅 (Step 2 Domain)
```

### 1.5 응답/에러 상태 (`design.md` §20 정합)

- **empty**: 5 placeholder 카드 (skeleton)
- **loading**: 5 skeleton (P-001 호출 중)
- **streaming / partial**: 일부 카드만 도착 시 progressive render (Phase 4+ SSE)
- **error**: ErrorCard (Phase 1 기존) — INV-001 입력 검증 / E-LLM-* LLM 실패
- **retry**: 5장 미만 생성 실패 시 retry CTA (`page_map.md` §6, `design.md` §20)

### 1.6 a11y (`frontend_design_contract.md` §5)

- 페이지 aria-label: "브랜드 방향 1단계 (총 7단계 중)"
- 카드 그룹: `role="radiogroup"` (CardGrid5)
- 개별 카드: `role="radio"` + `aria-checked={selected}` + `aria-label={card.name}` (BrandDirectionCard)
- 키보드: Tab 진입 → ↑↓ 또는 ←→로 카드 이동, Space/Enter로 선택
- focus visible: `tokens.color.border_focus` 2px outline + 2px offset
- prefers-reduced-motion: hover scale 제거 (`tokens.md` §6.3)

### 1.7 Wireframe

`apps/web/wireframes/step1_brand.md` 참조 (ASCII art, 360px 적합)

### 1.8 검증 acceptance (Slice 2)

- [ ] `BrandDirectionCard` 4-layer (Behavior / Layout / Visual / Wireframe) + variants 3개 + replaceability M — component_map.md 등재
- [ ] `CardGrid5` 4-layer + variants 2~3개 + replaceability M — component_map.md 등재
- [ ] ASCII wireframe 360px 적합 (가로 스크롤 없음, 1열 5행 + 세로 스크롤)
- [ ] 컴포넌트 cross-reference 정합 (discovery_flow.md ↔ component_map.md ↔ wireframes/step1_brand.md)
- [ ] output_schema.md §3 P-001 brand_direction_cards body 스키마와 Behavior layer Props 정합

---

## 2. Step 2: Domain (산업/주제)

- **prompt**: P-002 (`docs/contracts/output_schema.md` §4 domain_direction_cards)
- **pattern**: `BrandDirectionCard` 변형 × 5 (`CardGrid5`) — Step 1 패턴 재사용
- **입력**: Step 1 선택된 `brand_direction` + user_direct_input 텍스트 (if any)
- **다음 단계**: Step 3 Series (선택된 domain 컨텍스트 전달)

### 2.1 컴포넌트 재사용

- `BrandDirectionCard`: `card.name = "도메인 이름"`, `card.description = "도메인 설명"` (props 형식 동일)
- 카드 5장: AI 추천 4 (예: 재테크 / 건강 / 라이프스타일 / 기술) + user_direct_input 1
- Wireframe: `step1_brand.md` 패턴 그대로 재사용 (H1 + subtitle 텍스트만 변경, 진행 표시 "2 / 7")
- Behavior layer 차이: 없음 (card 필드 동일, 컨텐츠만 domain-specific)

---

## 3. Step 3: Series

- **prompt**: P-003 (`output_schema.md` §5 series_cards)
- **pattern**: `BrandDirectionCard` 변형 × 5
- **입력**: Step 1+2 (brand + domain)
- **다음 단계**: Step 4 Target

### 3.1 재사용 메모

- Step 2와 동일 패턴, 카드 컨텐츠만 series-specific (예: 30초 쇼츠 / 1분 정보 / 인터뷰 / 리뷰 / 직접 입력)
- 진행 표시 "3 / 7"
- Phase 3 진입 시 Behavior layer에 `structure_type`, `cadence_hint` 필드 추가 검토 — 현재 spec은 description 한 줄로 표현

---

## 4. Step 4: Target Audience

- **prompt**: P-004 part 1 (`output_schema.md` §6 target_cards)
- **pattern**: `BrandDirectionCard` 변형 × 5
- **입력**: Step 1~3 (brand + domain + series)
- **다음 단계**: Step 5 Tone

### 4.1 재사용 메모

- 카드 컨텐츠 = target persona (예: 30대 직장인 / 20대 학생 / 자영업자 / 주부 / 직접 입력)
- 진행 표시 "4 / 7"
- Phase 3 진입 시 Behavior layer에 `pain_points`, `watch_motivation` 필드 추가 검토 — 현재는 fit_situation / pros / cautions로 통합

---

## 5. Step 5: Tone & Style (★ form 변형, 5-card 예외)

- **prompt**: P-004 part 2 (`output_schema.md` §6 tone_card form)
- **pattern**: **다중선택 chip (multi-select chips)** — 5-card pattern 예외
- **입력**: Step 1~4
- **다음 단계**: Step 6 Direction Summary

### 5.1 컴포넌트 변형 (form 패턴)

- 사용 컴포넌트: `ToneChipsForm` (Phase 3 신규, Phase 2는 spec only — Phase 3 진입 시 4-layer 작성)
- form 구성:
  - **다중선택 chip × 6~10** (warm / professional / casual / energetic / sincere / humorous / informative / friendly / formal / story-telling)
  - chip 1개당 toggle (선택 / 해제), 선택된 chip에 `tokens.color.border_focus` 또는 `tokens.color.primary` border
  - **"직접 입력" textarea** (선택, 추가 톤 자유 표현)
  - 강도 슬라이더는 **미채택** (Phase 3+ 결정 시 추가 검토)
- 진행 표시 "5 / 7"
- 하단 SubmitButton sticky — 최소 1개 chip 선택 시 활성

### 5.2 사용자 결정 (U2-7)

- **2026-05-27 confirmed**: 다중선택 chip 패턴 채택 (`phases/active/phase-2-pwa-design/assumptions.md` §1.2 U2-7)
- 슬라이더 X, 5-card 예외로 form 변형 적용
- 5-card pattern 예외 사유: tone은 categorical (multi-tag) 성격 — 단일 선택 부적합, 사용자가 여러 톤을 동시에 원함

### 5.3 Wireframe (간략)

- Step 1 wireframe의 5-card 영역을 **chip cloud**로 대체
- 진행 표시 + H1 + subtitle은 동일
- chip 영역: flex-wrap, gap=space.2, chip별 padding=space.2/space.3, radius=radius.sm or radius.full (pill)
- 선택된 chip: bg=tokens.color.primary, text=tokens.color.text_inverse
- 비선택 chip: bg=surface, text=text_default, border=border_default 1px
- 하단 SubmitButton sticky

### 5.4 Phase 3 deferred

- `ToneChipsForm` 4-layer 상세 (Phase 3 진입 시 작성)
- chip 개수 / 라벨 확정 (현재 6~10개 예시 — Phase 4+ 사용자 데이터로 조정 가능)
- chip vs textarea 직접 입력 비율 추적 (Phase 4 analytics)

---

## 6. Step 6: Direction Summary (★ DirectionApprovalCard 사용)

- **prompt**: P-005 oneline_direction (`output_schema.md` §7)
- **pattern**: **DirectionApprovalCard** (`apps/web/direction_approval.md` 참조 — 양 모드 공통)
- **입력**: Step 1~5 종합 → AI가 한 줄 방향 생성
- **다음 단계**: Step 7 Generate (승인 시) / Step 6 재호출 (재생성 시) / inline 편집 후 진행 (수정 시)

### 6.1 컴포넌트 사용

- 컴포넌트: `DirectionApprovalCard` (`apps/web/component_map.md` §DirectionApprovalCard 참조)
- variant: **verbose** (Discovery는 Step 1~5 이유 표시 권장)
- Quick Mode는 같은 컴포넌트 + `variant=minimal` 사용 (Slice 4 작성 `quick_flow.md`)
- 진행 표시 "6 / 7"

### 6.2 Cross-reference

- `apps/web/direction_approval.md` — pattern 본문 (목적 / 행동 모델 / 분석 / a11y / 변경성)
- `apps/web/wireframes/direction_approval.md` — wireframe (verbose chosen + minimal 대안)
- `apps/web/component_map.md` §DirectionApprovalCard — 4-layer + 2 variants yaml

---

## 7. Step 7: Generate

- **prompt**: P-006 plan_candidates (`output_schema.md` §8)
- **pattern**: `GenerationProgressStepper` 4단계 (Intent → RAG → Planning → Critic) + 결과 plan_candidates
- **입력**: Step 6에서 승인된 (또는 수정된) direction
- **다음 단계**: `/plan` 결과 페이지 (Phase 1 PlanCard 활용)

### 7.1 컴포넌트 재사용

- `GenerationProgressStepper` (Phase 0 minimal entry, Phase 1 활용 — 4단계 적용)
- `PlanCard` (Phase 1 기존, `apps/web/components/PlanCard.tsx`) — Phase 1 응답 envelope 그대로 사용 (`plan_candidates[0]`)
- 결과: 1 plan (Phase 1 deviation 명시 — `output_schema.md` §8.2 검증 규칙 validation.warnings)
- Phase 4에서 3 plans + `PlanComparisonCard` 활성화 예정

### 7.2 대기 시간 UX

- 30~60초 대기 (`apps/web/design.md` §13)
- 4단계 stepper 텍스트 업데이트 (현재 sync, Phase 4+ SSE migration)
- partial result 즉시 표시 (Phase 4+ SSE 활성 후)
- 진행 표시 "7 / 7"

### 7.3 Phase 3 deferred

- progress stepper 실 polling 또는 SSE (Phase 1은 sync, Phase 4 SSE migration)
- 3-plan 비교 (`PlanComparisonCard`, Phase 4)
- Critic revise 흐름 UI (revise_count ≤ 2, `apps/web/design.md` §13)

---

## 변경 이력

- 2026-05-27: Phase 2 Slice 2 — §0 개요 + §1 Step 1 Brand 상세 작성. §2~§7은 Slice 3 placeholder.
- 2026-05-27: Phase 2 Slice 3 — §2~§7 4줄 명세로 확정. Step 5 다중선택 chip 패턴 채택 (U2-7 confirmed). Step 6 DirectionApprovalCard cross-reference 명시 (`direction_approval.md`).
