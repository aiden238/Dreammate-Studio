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

## 2~7. Steps 2~7

> Slice 3에서 각 step 4줄 명세로 추가 예정. 현재는 placeholder.
>
> 예상 구조 (Slice 3에서 작성):
>
> ### 2. Step 2: Domain
> - prompt: P-002 / pattern: BrandDirectionCard × 5 재사용
> - 입력: Step 1 선택 (brand_direction)
> - 다음: Step 3 Series
> - 변경점: Behavior layer card 필드에 step-specific 추가 (예: domain_focus)
>
> ### 3. Step 3: Series
> - prompt: P-003 / pattern: BrandDirectionCard × 5 재사용 + structure_type, cadence_hint 필드
> - 입력: Step 1+2
> - 다음: Step 4 Target
>
> ### 4. Step 4: Target
> - prompt: P-004 / pattern: BrandDirectionCard × 5 재사용 + pain_points, watch_motivation 필드
> - 입력: Step 1~3
> - 다음: Step 5 Tone
>
> ### 5. Step 5: Tone (form 패턴 — 5-card 예외)
> - prompt: P-004 / pattern: form (슬라이더 + 다중선택)
> - 입력: Step 1~4
> - 다음: Step 6 Direction Summary
> - 예외 이유: tone은 categorical이 아니라 spectrum이므로 5장 카드 부적합
>
> ### 6. Step 6: Direction Summary
> - prompt: P-005 / pattern: **DirectionApprovalCard** (별도 컴포넌트 — direction_approval.md 참조)
> - 입력: Step 1~5 종합
> - 다음: 승인 → Step 7 Generate, 수정 → 이전 step 복귀, 다시 좁히기 → 동일 깊이 재선택
>
> ### 7. Step 7: Generate
> - prompt: P-006 / pattern: GenerationProgressStepper 4단계 (Intent / RAG / Planning / Critic)
> - 입력: Direction 승인 결과
> - 다음: /plan 결과 페이지 (Phase 4)
> - 대기 시간: 30~60초 (`design.md` §13)

---

## 변경 이력

- 2026-05-27: Phase 2 Slice 2 — §0 개요 + §1 Step 1 Brand 상세 작성. §2~§7은 Slice 3 placeholder.
