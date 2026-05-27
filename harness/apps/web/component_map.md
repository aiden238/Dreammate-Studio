# Component Map

> 위치: `apps/web/component_map.md`
> 정합 기준: `apps/web/design.md` §10, §11, §12, §13
> 그룹: Layout / Input / Discovery / Quick / AI Flow / Output / Project Memory / Feedback

## Layout / Navigation

| Component | Purpose | Used In |
|---|---|---|
| AppShell | 모바일 하단 탭바 + 데스크톱 좌측 사이드바 | Dashboard, Workspace 전반 |
| BreadcrumbBrandPath | Brand > Domain > Series > Video 경로 표시 | Project Workspace |
| ProjectTreeNav | 데스크톱 좌측 트리 (Brand 폴딩) | Dashboard, Workspace |
| BottomActionBar | 모바일 하단 고정 CTA | 모든 모바일 페이지 |

## Input Components

| Component | Purpose | Props (요약) | Used In |
|---|---|---|---|
| IdeaInputBox | 짧은 아이디어 입력 1–2줄 (autosave) | { value, onChange, maxLen=200 } | Onboarding, Discovery Step 1 |
| QuickPromptInput | Quick Mode 자유 입력 (10–200자, 200자 초과 시 줄임 제안) | { value, onChange, onShorten } | Quick Prompt |
| IntentQuestionCard | AI 부족정보 질문 (최대 2개, 4지선다 또는 자유 입력) | { question, options[], onAnswer, onSkip } | Quick Prompt |
| DirectInputFallback | Discovery 단계 "직접 입력" 클릭 시 자유 입력 전환 | { step, onSubmit } | Discovery 5단계 모두 |
| RevisionReasonInput | 거절 이유 / 수정 요청 입력 | { reason, onSubmit } | Project Workspace |

## Discovery (Track A) Components

| Component | Purpose | Props | Notes |
|---|---|---|---|
| WizardStepHeader | "3/6단계: 시리즈 선택" 같은 진행 표시 + "이전 단계" 버튼 | { currentStep, totalSteps, title } | 항상 상단 노출 |
| ChoiceOptionCard | 5장 후보 카드 단위 (이름/한 줄 설명/적합 상황/장점/주의점/선택 버튼) | { name, description, fitContext, pros, cons, onSelect } | design.md §11 카드 구조 |
| ChoiceCardGrid | 5장 카드 배치 (모바일 세로 / 데스크톱 가로) | { cards[5], layout } | 단계당 정확히 5장 |
| DirectionSummaryCard | 모든 선택을 종합한 방향 요약 | { brand, domain, series, target, tone, summary } | Step 7 출력 (P-005) |

## Quick (Track B) Components

| Component | Purpose | Props | Notes |
|---|---|---|---|
| OneLineDirectionCard | AI가 제안한 한 줄 방향 (인라인 편집 가능) | { direction, editable, onEdit } | 형식: "{타깃}을 대상으로 {목적}을 보여주는 {길이} {포맷}" |
| ApprovalToggle | 승인 / 수정 / 다시 좁히기 3-way | { onApprove, onEdit, onNarrow } | "다시 좁히기" → Discovery 진입 |
| ContextInheritanceBadge | 상속된 Brand/Domain/Series 표시 | { brand, domain, series } | Quick mode 상단 노출 |

## AI Flow Components

| Component | Purpose | Props | State |
|---|---|---|---|
| GenerationProgressStepper | 4단계 진행률 (Intent / RAG / Plan / Critic) | { currentStep 0–3, partials[] } | 30–60초 동안 단계 표시 |
| RAGReferencePanel | "참고한 기획 기준" 노출 | { references[] } | 펼침/접힘 |
| AgentStatusIndicator | 현재 동작 중인 Agent 표시 | { agent: "intent"\|"planner"\|"critic"\|"rewriter" } | 진행 중 |

## Output Components

| Component | Purpose | Props | Notes |
|---|---|---|---|
| PlanOptionCard | 3개 기획안 비교 카드 (이름/콘셉트/후킹/흐름/장점/리스크/선택) | { plan, isRecommended, onSelect, onEdit, onReject } | P-006 출력, 모바일 세로 / 데스크톱 3열 |
| HookCandidateCard | 후킹 후보 카드 (한 기획안 내 3개) | { hook, index } | design.md §13 §3 |
| VideoStructureTimeline | 영상 구성안 타임라인 (3–6 비트) | { segments[] } | 가로 스크롤 |
| ShootingNoteCard | 촬영 노트 | { notes[] } | 펼침/접힘 |
| QualityScorePanel | 8차원 점수 + 이유 + 개선안 | { scores: {hook, target, ...} } | Critic 결과, design.md §13 §6 |
| OutputViewer | 최종 결과물 묶음 (Final Output 페이지 컨테이너) | { plan, sections[] } | §13 표시 순서 1–9 |
| ChecklistPanel | Brand 규칙 / 촬영 체크리스트 | { items[], checked[] } | Project Workspace 사이드 |
| RevisionSuggestionCard | Rewriter 개선안 | { suggestions[] } | §13 §7 |

## Project Memory / Intent Components

| Component | Purpose | Notes |
|---|---|---|
| BrandMemoryPanel | 현재 Brand의 톤 / 금기 표현 / 자주 쓰는 표현 | Project Workspace, Settings |
| ProjectMemoryDrawer | 좌측 슬라이드 패널 (메모리 미리보기) | Workspace |
| IntentWarningBox | 영상기획 외 입력 감지 시 부드러운 안내 | 자유 입력 위치 전반 |

## Feedback / Action Components

| Component | Purpose |
|---|---|
| LikeDislikeFeedback | plan 단위 좋아요/별로 피드백 |
| SavePlanButton | 저장 CTA |
| RegenerateButton | 재생성 CTA (Critic revise 최대 2회) |
| RevisionRequestModal | 수정 요청 입력 modal |
| CopyOutputButton | 결과물 복사 (Final Output) |

## State Coverage (design.md §20)

각 컴포넌트가 반드시 다뤄야 하는 상태:
- Empty / Loading / Streaming (부분 결과) / Partial Result / Error / Retry / Save Success
- Discovery 단계는 5장 미만 생성 실패 시 Retry 상태 필수

## 의존 contract

- `docs/contracts/frontend_design_contract.md` — 디자인 토큰, 색상, 타이포그래피
- `docs/contracts/output_schema.md` — Plan, Hook, QualityScore JSON 형식
- `docs/contracts/error_response_contract.md` — Error / Retry 데이터 형식
- `ai_system/prompts/prompt_registry.md` — P-001..P-008 출력 스키마와 카드 1:1 매핑

---

# Phase 2 Slice 2 — 4-Layer 핵심 컴포넌트

> 추가일: 2026-05-27 (Phase 2 Slice 2)
> 범위: Discovery Step 1 + 5-card pattern 적용 (2개 컴포넌트만 4-layer 강제)
> 참조: `apps/web/design_system/component_contract.md` (4-layer template),
>       `apps/web/design_system/variant_format.md` (yaml schema),
>       `apps/web/design_system/replaceability_score.md` (L/M/H 정책),
>       `apps/web/design_system/tokens.md` (Visual 참조 토큰)
>
> 정책: 이 section의 컴포넌트는 4-layer (Behavior / Layout / Visual / Wireframe) 모두 작성.
>       위 section의 Phase 0/1 컴포넌트는 minimal entry 그대로 유지 (over-engineering 회피).

---

## BrandDirectionCard (Phase 2 Slice 2)

> 분류: Card (Discovery 카드 패턴 baseline — Step 2~7 카드의 template 재사용)
> Phase 진입: Phase 3 Slice 2 (실 구현)
> Replaceability: **M** (variants swap 시 2~4 파일 영향 — `replaceability_score.md` §3.2)
> Variants: 3개 (current / alt_horizontal_swipe / alt_grid_2x3)
> 파일 위치 (Phase 3): `apps/web/components/discovery/BrandDirectionCard.tsx`
> output_schema 매핑: `docs/contracts/output_schema.md` §3 P-001 brand_direction_cards.cards[i]

### Behavior

```typescript
interface BrandDirectionCardProps {
  card: {
    card_id: string;          // P-001 output_schema §3 (uuid v4)
    kind: 'ai_suggestion' | 'user_direct_input';
    name: string;             // 8~14자 명사형 (design.md §11)
    description: string;      // 30~50자 한 줄 설명
    fit_situation?: string;   // 1줄 적합 상황 (ai_suggestion만)
    pros?: string;            // 1줄 장점 (ai_suggestion만)
    cautions?: string;        // 1줄 주의점 (ai_suggestion만)
    confidence?: number;      // 0.0 ~ 1.0 (ai_suggestion만)
  };
  selected: boolean;
  onSelect: (card_id: string) => void;
  onUserInputChange?: (text: string) => void;  // user_direct_input일 때만 사용
}
```

- **State**: `selected`는 parent (CardGrid5) controlled (5장 중 1장 선택 관리)
- **Events**:
  - `onSelect(card_id)` — 카드 클릭 / Space / Enter 시 emit
  - `onUserInputChange(text)` — user_direct_input 카드의 textarea 변경 시
- **a11y** (`frontend_design_contract.md` §5):
  - `role="radio"`
  - `aria-checked={selected}`
  - `aria-label={card.name}`
  - 키보드: Tab으로 진입 → Space/Enter로 선택, 방향키로 형제 카드 이동
- **출력 schema mapping**: `output_schema.md` §3 P-001 (Step 2~7도 동일 schema 패턴 재사용)

### Layout

- **mobile (≤ `tokens.bp.mobile_md`, 390px)**: 100% width, `flex-direction: column`
  - card padding: `tokens.space.4` (16px)
  - 내부 항목 gap: `tokens.space.3` (12px)
  - min-height: 컨텐츠 의존 (4~6 줄)
- **tablet (≥ `tokens.bp.tablet`, 768px)**: 동일 stack, 카드 max-width 480px
- **desktop (≥ `tokens.bp.desktop`, 1024px)**: 가로 배치 가능 (CardGrid5 variants 따름)
- **터치 타겟**: 카드 전체가 클릭 가능 — 높이 ≥ 56px 자동 충족 (`frontend_design_contract.md` §3.3)

### Visual

| 항목 | default | hover | focus | selected | disabled |
|---|---|---|---|---|---|
| bg | `tokens.color.surface` | `tokens.color.bg_subtle` | (동) | `tokens.color.bg_subtle` | `tokens.color.bg_subtle` (60% opacity) |
| text | `tokens.color.text_default` | (동) | (동) | (동) | `tokens.color.text_muted` |
| border | 1px solid `tokens.color.border_default` | (동) | 2px solid `tokens.color.border_focus` (offset 2px) | 2px solid `tokens.color.primary` | 1px solid `tokens.color.border_subtle` |
| radius | `tokens.radius.lg` (12px) | (동) | (동) | (동) | (동) |
| motion | — | `transform: scale(1.02)` / `tokens.motion.fast` | — | `tokens.motion.base` | — |

- **typography**:
  - name: `tokens.font.size_lg` + `tokens.font.weight_semibold`
  - description: `tokens.font.size_base` + `tokens.font.weight_regular`
  - fit_situation / pros / cautions: `tokens.font.size_sm` + `tokens.font.weight_regular` + `tokens.color.text_muted`
  - confidence: visual indicator (●●●○○) — `tokens.color.primary` filled, `tokens.color.border_default` empty
- **user_direct_input variant**:
  - textarea: `tokens.color.surface` bg, 1px solid `tokens.color.border_default`, placeholder `tokens.color.text_placeholder`
  - icon: ✎ (pencil)
- **prefers-reduced-motion**: hover scale 제거, color transition만 유지 (`tokens.motion.instant`) — `tokens.md` §6.3

### Wireframe

`apps/web/wireframes/step1_brand.md` 참조 (CardGrid5 5장 배치 wireframe 포함).

### Variants

```yaml
variants:
  - id: current
    name: "Stacked vertical 5-card"
    chosen: true
    layout: "세로 1열 5행, swipe X, 한 화면에 ~2장 보임 + 스크롤"
    tradeoff_pros: |
      360px 모바일 적합 — 한 손 스크롤만으로 5장 탐색.
      user_input 슬롯(5번째)이 자연스럽게 발견됨.
    tradeoff_cons: |
      전체 5장 동시 조망 어려움 (스크롤 필요).
      세로 길이 증가로 BottomActionBar까지 거리 멀어짐.
    replaceability_cost: L
    decision_log: "Phase 2 Slice 2 채택 — 모바일 우선 정책 (design.md §17)"

  - id: alt_horizontal_swipe
    name: "Horizontal swipe carousel"
    chosen: false
    layout: "가로 스와이프 carousel, 1화면에 1.5장 보임 (peek)"
    tradeoff_pros: |
      exploration 유도 — peek로 다음 카드 인지.
      시각 강조 효과 ↑ (한 장당 면적 큼).
    tradeoff_cons: |
      user_input 슬롯(5번째) 발견 어려움 (스와이프 누적 비용).
      swipe gesture 학습 비용 + 키보드 접근성 ↓.
    replaceability_cost: M
    decision_log: "Phase 9 실 사용자 피드백 후 재검토 (탐색성 vs 발견성)"

  - id: alt_grid_2x3
    name: "Grid 2 col × 3 row"
    chosen: false
    layout: "2×3 그리드 (1자리 user_input, 1자리 비움 또는 5번째 ai_suggestion)"
    tradeoff_pros: |
      전체 5~6장 한 화면 조망 가능.
      비교 의사결정 빠름.
    tradeoff_cons: |
      카드 크기 작아짐 → description 가독성 ↓.
      360px 환경 무리 (text overflow 위험).
    replaceability_cost: M
    decision_log: "Phase 11+ 데스크톱/태블릿 전용 옵션으로 재검토 가능"
```

---

## CardGrid5 (Phase 2 Slice 2)

> 분류: Grid (Discovery 5-card 배치 컨테이너)
> Phase 진입: Phase 3 Slice 2
> Replaceability: **M** (variants chosen 변경 시 모든 Step wireframe 영향 — `replaceability_score.md` §3.2)
> Variants: 2개 (current / alt_horizontal_swipe) — alt_grid_2x3은 BrandDirectionCard variants와 연동되므로 별도 등재 X
> 파일 위치 (Phase 3): `apps/web/components/discovery/CardGrid5.tsx`
> 역할: BrandDirectionCard 5개 배치 (4 AI suggestions + 1 user_direct_input)

### Behavior

```typescript
interface CardGrid5Props {
  cards: BrandDirectionCardProps['card'][];           // 4 AI suggestions
  userInputSlot: BrandDirectionCardProps['card'];     // 1 user_direct_input
  selectedCardId: string | null;                      // 'user_input' 또는 uuid
  userInputText?: string;
  onSelect: (card_id: string) => void;
  onUserInputChange: (text: string) => void;
  ariaLabel?: string;                                  // 예: "브랜드 방향 선택"
}
```

- **State**: `selectedCardId`는 controlled (parent step container가 관리)
- **Events**:
  - `onSelect(card_id)` — 자식 BrandDirectionCard에서 bubble up
  - `onUserInputChange(text)` — user_direct_input 카드의 textarea 변경
- **a11y**:
  - `role="radiogroup"`
  - `aria-label={ariaLabel}` (default: "5장 카드 중 1장 선택")
  - 키보드: 첫 카드 Tab 진입 후 ↑↓/←→로 형제 이동, Home/End로 처음/끝
- **출력 schema mapping**: 직접 mapping 없음 (자식 카드가 매핑)

### Layout

- **mobile (≤ `tokens.bp.mobile_md`)**: `flex-direction: column`
  - container padding: `tokens.space.4` (16px 좌/우)
  - 카드 간 gap: `tokens.space.3` (12px)
  - 1열 5행, 세로 스크롤
- **tablet (≥ `tokens.bp.tablet`)**: 동일 column stack (max-width 600px 컨테이너 중앙 정렬)
- **desktop (≥ `tokens.bp.desktop`)**: variants에 따라 column or 가로 (current variant는 column 유지)
- **scroll**: vertical, smooth scroll, scroll-snap optional (Phase 3 결정)
- **하단 여백**: BottomActionBar / SubmitButton 영역 확보 — `tokens.space.16` (64px) bottom padding

### Visual

- **bg**: `tokens.color.bg_default` (페이지 배경 그대로 — 컨테이너 자체는 transparent)
- **scroll-behavior**: smooth (prefers-reduced-motion 시 auto)
- **motion**:
  - 카드 entry stagger animation (선택) — 각 카드 50ms 지연 + `tokens.motion.fast` fade-in
  - prefers-reduced-motion 시 instant
- **focus management**: 카드 그룹 진입 시 첫 카드 또는 selected 카드에 focus

### Wireframe

`apps/web/wireframes/step1_brand.md` 참조 (1열 5행 stack — current variant)

### Variants

```yaml
variants:
  - id: current
    name: "Vertical stack 1-col 5-row"
    chosen: true
    layout: "세로 1열 5행, 카드 width=100%, gap=space.3, 세로 스크롤"
    tradeoff_pros: |
      360px 모바일 적합 (한 손 스크롤).
      user_input 슬롯(5번째) 자연 발견.
      구현 단순 (flex-column 1줄).
    tradeoff_cons: |
      전체 5장 한 화면 조망 어려움.
      세로 길이 증가 → BottomActionBar까지 거리.
    replaceability_cost: L
    decision_log: "Phase 2 Slice 2 채택 — design.md §17 모바일 우선 + design.md §11 5장 카드 규칙"

  - id: alt_horizontal_swipe
    name: "Horizontal swipe carousel (1.5 cards visible)"
    chosen: false
    layout: "가로 스와이프, 1화면 1.5장 peek, page indicator (●●●○○)"
    tradeoff_pros: |
      exploration 강조 (peek로 다음 카드 인지).
      카드 한 장당 면적 큼 → 시각 강조 ↑.
    tradeoff_cons: |
      user_input 슬롯(5번째) 발견 어려움 (스와이프 4번 누적).
      swipe gesture 학습 비용 + 키보드 접근성 ↓.
      모든 Step wireframe 영향 (M~H 비용).
    replaceability_cost: M
    decision_log: "Phase 9 사용자 데이터 누적 후 A/B 테스트 가능"
```

→ 참고: BrandDirectionCard의 `alt_grid_2x3`는 CardGrid5 차원에서 별도 alt로 등재하지 않음 (BrandDirectionCard variants와 1:1 매핑되므로 중복 등재 회피).

---
