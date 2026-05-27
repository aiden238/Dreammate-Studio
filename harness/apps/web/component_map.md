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

## DirectionApprovalCard (Phase 2 Slice 3)

> 분류: Card (양 모드 공통 핵심 UX — Discovery Step 6 + Quick Mode)
> Phase 진입: Phase 3 Slice 3 (실 구현)
> Replaceability: **M** (variants swap 시 2 파일 영향 — `replaceability_score.md` §3.2)
> Variants: 2개 (verbose / minimal) — `variant_format.md` §4 baseline
> 파일 위치 (Phase 3): `apps/web/components/common/DirectionApprovalCard.tsx`
> 참조 spec: `apps/web/direction_approval.md` (pattern), `apps/web/wireframes/direction_approval.md` (wireframe)
> output_schema 매핑: `docs/contracts/output_schema.md` §7 P-005 oneline_direction
> 사용 컨텍스트: Discovery Step 6 (verbose 권장) + Quick Mode (minimal 권장)

### Behavior

```typescript
interface DirectionApprovalCardProps {
  direction: {
    one_line: string;             // P-005 output_schema §7 (20~70자)
    components?: {
      target: string;
      message: string;
      format: 'shorts_30s' | 'reels_60s' | 'shorts_60s' | 'youtube_3m' | 'youtube_8m' | 'other';
      length_sec: number;
    };
    reasons?: Array<{             // verbose variant only — Step 1~5 요약
      step: 'brand' | 'domain' | 'series' | 'target' | 'tone';
      label: string;              // "Step 1 Brand"
      value: string;              // "정보형 콘텐츠 선택"
    }>;
    confidence?: number;          // 0.0 ~ 1.0
    revise_count: number;         // 재생성 누적 횟수
  };
  variant: 'minimal' | 'verbose';
  onApprove: () => void;                          // "이대로 진행"
  onEditAndApprove: (edited_text: string) => void; // "수정 후 진행"
  onRegenerate: () => void;                        // "다시 생성" (P-005 재호출)
  ariaLabel?: string;                              // default: "기획 방향 승인"
}
```

- **State**:
  - `editMode: boolean` (internal) — ✎ 클릭 시 inline 편집 모드 진입
  - `editedText: string` (internal) — 편집 중 텍스트 buffer
  - `revise_count` controlled by parent (`direction.revise_count` prop, cap ≤ 2 권장)
- **Events**:
  - `onApprove()` — 한 줄 방향 그대로 다음 단계
  - `onEditAndApprove(edited_text)` — 편집된 텍스트로 다음 단계 (P-005 재호출 X)
  - `onRegenerate()` — P-005 재호출 (parent에서 revise_count++ + missing_info 처리)
- **a11y** (`docs/contracts/frontend_design_contract.md` §5):
  - 컨테이너: `role="region"` + `aria-label={ariaLabel}`
  - 한 줄 방향 영역: `role="region"` + `aria-label="AI 생성 기획 방향"`
  - textarea (편집 모드): `role="textbox"` + `aria-multiline="true"` + `aria-label="기획 방향 편집"`
  - 버튼: `role="button"` + 명시 `aria-label`
  - 키보드: Tab → primary CTA → secondary → tertiary, Esc로 편집 취소
- **출력 schema mapping**: `output_schema.md` §7 P-005 oneline_direction (one_line / components / missing_info / confidence)

### Layout

- **mobile (≤ `tokens.bp.mobile_md`, 390px)**: 100% width, `flex-direction: column`
  - container padding: `tokens.space.4` (16px 좌/우)
  - direction card padding: `tokens.space.4`
  - 내부 항목 gap: `tokens.space.3` (12px)
  - 버튼 간 gap: `tokens.space.3`
  - bottom button area sticky (sticky bottom — `apps/web/design.md` §17)
- **verbose layout**: 한 줄 방향 카드 + 구분선 + 이유 list (5줄) + 버튼 영역 (primary + secondary + tertiary)
- **minimal layout**: 한 줄 방향 카드 + 버튼 영역 (primary + tertiary 2개만)
- **편집 모드 layout**: 한 줄 방향 영역이 textarea로 inline 변환 + 글자수 카운터 + [적용] [취소] inline action
- **tablet (≥ `tokens.bp.tablet`)**: 동일 stack, container max-width 480px 중앙 정렬
- **desktop (≥ `tokens.bp.desktop`)**: 동일 stack 유지 (한 줄 방향은 좁은 컬럼에서 더 가독성 ↑)
- **터치 타겟**: 버튼 height ≥ 48px = `tokens.space.12` (`frontend_design_contract.md` §3.3)

### Visual

| 항목 | default | hover | focus | editing | error |
|---|---|---|---|---|---|
| direction card bg | `tokens.color.bg_subtle` | (동) | (동) | `tokens.color.surface` | (동) |
| direction text | `tokens.color.text_default`, `tokens.font.size_xl`, `tokens.font.weight_medium` | (동) | (동) | (동) | (동) |
| direction card radius | `tokens.radius.lg` | (동) | (동) | (동) | (동) |
| 편집 icon (✎) | `tokens.color.text_muted` | `tokens.color.primary` | (동) | hidden | (동) |
| 구분선 (verbose) | 1px solid `tokens.color.border_subtle` | — | — | — | — |
| 이유 list text | `tokens.color.text_muted`, `tokens.font.size_sm` | (동) | (동) | (동) | (동) |
| textarea (편집) | `tokens.color.surface` bg, 1px solid `tokens.color.border_default` | (동) | 2px solid `tokens.color.border_focus` (offset 2px) | (동) | 2px solid `tokens.color.state_error` |
| 글자수 카운터 (정상) | `tokens.color.text_muted` | — | — | (동) | — |
| 글자수 카운터 (≥70자) | `tokens.color.text_danger` | — | — | (동) | — |
| primary CTA bg | `tokens.color.primary` | `tokens.color.primary_hover` | (동) | (동) | `tokens.color.primary_disabled` |
| primary CTA text | `tokens.color.text_inverse` | (동) | (동) | (동) | (동) |
| primary CTA radius | `tokens.radius.md` | (동) | (동) | (동) | (동) |
| secondary CTA | `tokens.color.bg_default` bg + 1px solid `tokens.color.border_default` | `tokens.color.bg_subtle` | (동) | (동) | — |
| tertiary CTA | `tokens.color.text_muted`, underline, transparent bg | `tokens.color.text_default` | (동) | (동) | — |

- **motion**:
  - 편집 모드 진입 (직접 → textarea): `tokens.motion.base` (250ms), `tokens.motion.ease_out`
  - 버튼 hover: `tokens.motion.fast` (150ms)
  - prefers-reduced-motion: 편집 모드 전환 instant, color transition만 유지 (`tokens.md` §6.3)

### Wireframe

`apps/web/wireframes/direction_approval.md` 참조 (verbose chosen + minimal 대안 + 편집 모드 + loading/error 상태)

### Variants

```yaml
variants:
  - id: verbose
    name: "Verbose with reasons (Discovery 권장)"
    chosen: true
    layout: "한 줄 방향 + Step 1~5 이유 list (5줄) + 버튼 3개 (이대로 진행 / 수정 후 진행 / 다시 생성)"
    tradeoff_pros: |
      사용자가 AI 결정 근거(Step 1~5 어떤 선택에서 도출됐는지) 확인 가능 → 신뢰 ↑.
      편집 시 어느 Step을 다시 가야 할지 판단 쉬움.
    tradeoff_cons: |
      세로 길이 증가 (이유 5줄 + 버튼 3개) → 360px 모바일 한 화면 한 CTA 원칙 위반 위험.
      Quick Mode 빠른 흐름에 부적합.
    replaceability_cost: L
    decision_log: "Phase 2 Slice 3 채택 — Discovery 시나리오 가정 (사용자가 Step별 결정 검토 필요)"

  - id: minimal
    name: "Minimal (Quick Mode 권장)"
    chosen: false
    layout: "한 줄 방향 + 버튼 2개 (이대로 진행 / 다시 생성). 편집은 ✎ icon → 편집 후 primary 라벨이 '수정 후 진행'으로 자동 변경"
    tradeoff_pros: |
      빠른 진행 — Quick Mode 짧은 흐름 자연스러움.
      360px 한 화면 적합 (버튼 2개 + 한 줄만).
    tradeoff_cons: |
      AI 결정 이유(이유 list) 미표시 → 신뢰 ↓ 위험.
      편집 시 어떤 Step 다시 가야 할지 단서 부족.
    replaceability_cost: L
    decision_log: "Phase 2 Slice 3 등재 — Quick Mode 짧은 흐름 가정. Phase 4+ 실 데이터로 verbose vs minimal 분포 재평가 (assumptions.md U2-4)"
```

→ variant chosen swap (verbose ↔ minimal): `component_map.md` 1줄 토글 + 영향 wireframe section 1개 우선 표시 변경. Replaceability **L~M** (2 파일 이하).

---

## QuickInputCard (Phase 2 Slice 4)

> 분류: Card (Quick Mode 입력 — 짧은 프롬프트 + 동적 부족정보 질문)
> Phase 진입: Phase 3 Slice 4 (실 구현)
> Replaceability: **L** (단순 input form, 변경 영향 ≤ 1 파일 — `replaceability_score.md` §3.2)
> Variants: **current만** (ADR-011 Variants Bank 3개 한정 정책 — `variant_format.md` §0)
> 파일 위치 (Phase 3): `apps/web/components/quick/QuickInputCard.tsx`
> 참조 spec: `apps/web/quick_flow.md` §1 + §2, `apps/web/wireframes/quick_short.md`
> output_schema 매핑: 직접 매핑 없음 (입력은 `POST /api/v1/quick/start` body로 backend 전달, 응답은 P-005 oneline_direction 또는 clarify_questions)
> 사용 컨텍스트: Quick Mode Step 1 (짧은 프롬프트) + Step 2 (부족 정보 질문, 재사용 — mode prop만 다름)

### Behavior

```typescript
interface QuickInputCardProps {
  mode: 'initial_prompt' | 'follow_up_question';
  question?: string;                  // follow_up_question 모드일 때만 (예: "어떤 분께 보여드릴 영상인가요?")
  placeholder?: string;               // default: mode별 다름
  maxLength?: number;                 // default: initial_prompt=300, follow_up_question=200
  value: string;
  onChange: (text: string) => void;
  onSubmit: () => void;               // primary CTA (다음 ▶ / 답변 후 진행 ▶)
  onSkip?: () => void;                // follow_up_question 모드만 — "이대로 진행 (skip)"
  ariaLabel?: string;
}
```

- **State**: `value`는 parent controlled (sessionStorage 또는 wizard state container 관리)
- **Events**:
  - `onChange(text)` — textarea 입력 시
  - `onSubmit()` — Cmd/Ctrl+Enter 또는 primary CTA 클릭
  - `onSkip()` — follow_up_question 모드의 secondary CTA 클릭 (skip)
- **a11y** (`docs/contracts/frontend_design_contract.md` §5):
  - 컨테이너: `role="region"` + `aria-label={ariaLabel || (mode==='initial_prompt' ? "짧은 프롬프트 입력" : "AI 부족 정보 질문")}`
  - textarea: `role="textbox" aria-multiline="true"` + `aria-label` 자동 연결
  - question (follow_up 모드): `<h2>` 또는 `role="heading" aria-level="2"` + `aria-live="polite"` (동적 변경 알림)
  - char count: `aria-live="polite"` (300자 근접 시 변경 알림, over limit 시 `aria-invalid="true"`)
  - 키보드: Tab → textarea → primary CTA → skip CTA (mode='follow_up' 시), Esc로 입력 clear (optional)
- **출력 schema mapping**: 직접 schema 매핑 없음 (input form, body는 backend 자유 형식 `{short_prompt, brand_id, series_id}` 또는 `{answers: Record<question_id, string>}`)

### Layout

- **mobile (≤ `tokens.bp.mobile_md`, 390px)**: 100% width, `flex-direction: column`
  - container padding: `tokens.space.4` (16px 좌/우)
  - 내부 항목 gap: `tokens.space.3` (12px)
  - textarea min-height: `tokens.space.24` (96px, rows=4) — initial_prompt 모드
  - textarea min-height: `tokens.space.16` (64px, rows=3) — follow_up_question 모드 (짧은 답변 가정)
  - char count: 우측 하단, textarea 내부 absolute positioning
  - resize: vertical disabled (`resize: none`)
  - skip 버튼 (follow_up_question 모드만): primary CTA 위에 배치, 두 CTA 간 gap `tokens.space.3`
- **tablet (≥ `tokens.bp.tablet`)**: 동일 stack, container max-width 480px 중앙 정렬
- **desktop (≥ `tokens.bp.desktop`)**: 동일 stack 유지 (input은 좁은 컬럼이 자연스러움)
- **터치 타겟**: textarea height ≥ 64px, CTA height ≥ 48px (`frontend_design_contract.md` §3.3)

### Visual

| 항목 | default | hover | focus | error (over limit) | disabled |
|---|---|---|---|---|---|
| textarea bg | `tokens.color.surface` | (동) | (동) | (동) | `tokens.color.bg_subtle` |
| textarea text | `tokens.color.text_default`, `tokens.font.size_base` | (동) | (동) | (동) | `tokens.color.text_muted` |
| textarea placeholder | `tokens.color.text_placeholder` | (동) | (동) | — | — |
| textarea border | 1px solid `tokens.color.border_default` | (동) | 2px solid `tokens.color.border_focus` (offset 2px) | 2px solid `tokens.color.state_error` | 1px solid `tokens.color.border_subtle` |
| textarea radius | `tokens.radius.md` (8px) | (동) | (동) | (동) | (동) |
| char count (정상) | `tokens.color.text_muted`, `tokens.font.size_xs` | — | — | — | — |
| char count (over limit) | `tokens.color.text_danger`, `tokens.font.size_xs`, `tokens.font.weight_medium` | — | — | — | — |
| question (follow_up_question) | `tokens.color.text_default`, `tokens.font.size_lg`, `tokens.font.weight_semibold` | — | — | — | — |
| primary CTA bg (외부 SubmitButton) | `tokens.color.primary` | `tokens.color.primary_hover` | (동) | — | `tokens.color.primary_disabled` |
| skip CTA (외부 SubmitButton secondary) | `tokens.color.bg_default` bg + 1px solid `tokens.color.border_default`, text=`tokens.color.text_muted` | `tokens.color.bg_subtle` | (동) | — | — |

- **typography**:
  - placeholder: `tokens.font.size_base` + `tokens.font.weight_regular` + `tokens.color.text_placeholder`
  - input text: `tokens.font.size_base` + `tokens.font.weight_regular` + `tokens.color.text_default`
  - question (follow_up): `tokens.font.size_lg` + `tokens.font.weight_semibold` + `tokens.color.text_default`
- **motion**:
  - focus border 전환: `tokens.motion.fast` (150ms), `tokens.motion.ease_out`
  - question 동적 노출 (mode 변경 시): `tokens.motion.base` (250ms) fade-in
  - prefers-reduced-motion: 전환 instant, color transition만 유지 (`tokens.md` §6.3)

### Wireframe

`apps/web/wireframes/quick_short.md` 참조 (Step 1 initial_prompt + Step 2 follow_up_question 모두 포함).

### Variants

```yaml
variants:
  - id: current
    name: "Single textarea with char count (initial + follow-up dual mode)"
    chosen: true
    layout: "단일 textarea + char count 우측 하단 + primary CTA (외부 SubmitButton). follow_up_question 모드일 때만 question heading + skip CTA 추가."
    tradeoff_pros: |
      단순, 모바일 적합, 학습 비용 0.
      Step 1/Step 2 양쪽 재사용 가능 (mode prop만 차이) → 단일 컴포넌트 유지보수.
      구현 비용 L (Phase 3 진입 시 단순 controlled textarea + sticky CTA).
    tradeoff_cons: |
      부족 정보 질문 시 시각 단조 (선택지 미제공).
      음성 입력 / 멀티모달 입력 미지원 (Phase 11+ 영역).
    replaceability_cost: L
    decision_log: "Phase 2 Slice 4 채택 — Variants Bank 3개 한정 정책 (ADR-011) 정합. QuickInputCard는 current variant 1개만. Phase 3+ 실 구현 중 alt 발생 시 추가 가능 (예: alt_voice / alt_4_choice)."
```

→ alt variants는 deferred:
- `alt_voice` (Phase 11+) — 음성 입력 + 텍스트 transcript
- `alt_4_choice` (Phase 3 사용자 피드백 후) — Step 2 부족 정보 질문을 4지선다 카드로 (`IntentQuestionCard` 패턴 차용)

→ alt 추가 시 본 entry variants yaml에 등재 + `wireframes/quick_short.md` 대안 section 갱신 + ADR 권장 (`variant_format.md` §5 절차).

---

# Phase 2 Slice 5 — Integrated Matrix

> 추가일: 2026-05-27 (Phase 2 Slice 5)
> 목적: Slice 1~4의 모든 컴포넌트 + Phase 0/1 entries를 통합 매트릭스로 한눈에 정리.
> 기존 entries 모두 보존. 본 section은 cross-cutting view + Phase 4 placeholder 추가만.
> 참조: `apps/web/design_handoff.md` (Phase 2 핵심 산출물 — 변경 가이드 본문)

---

## Replaceability 통합 매트릭스

> 모든 컴포넌트의 Replaceability + Variants 수 + 4-layer 완성도 한눈에 확인.
> 본 매트릭스는 `design_handoff.md` §2 매트릭스와 cross-reference.

| # | 컴포넌트 | Phase | Replaceability | Variants 수 | 4-layer | 비고 |
|---|---|---|---|---|---|---|
| 1 | BrandDirectionCard | 2 spec / 3 impl | M | 3 (current / alt_horizontal_swipe / alt_grid_2x3) | ✅ | Slice 2 |
| 2 | CardGrid5 | 2 spec / 3 impl | M | 2 (current / alt_horizontal_swipe) | ✅ | Slice 2 |
| 3 | DirectionApprovalCard | 2 spec / 3 impl | M | 2 (verbose / minimal) | ✅ | Slice 3, 양 모드 공통 |
| 4 | QuickInputCard | 2 spec / 3 impl | L | 1 (current) | ✅ | Slice 4 |
| 5 | ToneChipsForm | 2 sketch / 3 impl | M | TBD (Phase 3 진입 시 결정) | △ deferred | Step 5 form 변형 (5-card 예외) |
| 6 | PlanCard (Phase 1) | 1 done | L | 1 (Phase 1 형식) | △ minimal entry | Phase 4에서 3-plan / PlanComparisonCard로 격상 |
| 7 | ProgressStepper (Phase 1) | 1 done | L | 1 | △ minimal entry | 4단계 sync (Phase 4 SSE 전환) |
| 8 | ErrorCard (Phase 1) | 1 done | L | 1 | △ minimal entry | INV-001 / E-LLM-* 시리즈 |
| 9 | SubmitButton (Phase 1) | 1 done | L | 1 | △ minimal entry | sticky bottom |
| 10 | WizardStepHeader | 2 spec / 3 impl | L | 1 | △ minimal entry | Discovery 진행 표시 |
| 11 | BreadcrumbBrandPath | 0 entry / 3 impl | L | 1 | △ minimal entry | Quick Mode 상단 컨텍스트 |
| 12 | IntentQuestionCard | 0 entry / 3 alt | M | TBD (Phase 3 활성 시 결정) | △ minimal entry | Quick Step 2 대안 패턴 |
| 13 | IntentWarningBox | 0 entry / 3 impl | L | 1 | △ minimal entry | 영상기획 외 입력 감지 |
| 14 | RAGReferencePanel | 0 entry / 4 impl | L | 1 | △ minimal entry | Phase 4 SSE 활성 |
| 15 | PlanComparisonCard | 4 placeholder | M (예상) | TBD (Phase 4 진입 시 결정) | ⚠ Phase 4 deferred | 본 section 별도 placeholder 참조 |
| 16 | DirectionSummaryCard (legacy entry) | 0 entry | L | 1 | △ minimal entry | DirectionApprovalCard로 대체 (Slice 3) — Phase 3 진입 시 정리 검토 |
| 17 | ApprovalToggle (legacy entry) | 0 entry | L | 1 | △ minimal entry | DirectionApprovalCard 내부 흡수 (Slice 3) — Phase 3 진입 시 정리 검토 |
| 18 | OneLineDirectionCard (legacy entry) | 0 entry | L | 1 | △ minimal entry | DirectionApprovalCard로 흡수 (Slice 3) — Phase 3 진입 시 정리 검토 |

### Replaceability 분포

- **L (Low — 1 파일 수정)**: 9개 — 단순 entry, 단일 variant
- **M (Medium — 2~3 파일 수정)**: 8개 — 4-layer + variants 다수 또는 form pattern
- **H (High — 4~5+ 파일)**: 0개 — Phase 2에서 H 컴포넌트는 만들지 않음 (구조적 변경은 §design_handoff.md §1 시나리오 3/5 영역)

→ 18개 중 9개 L + 8개 M = 17개 "변경 가능성 보장" 확보. PlanComparisonCard (Phase 4) 1개만 deferred.

---

## Routes ↔ Components 매핑

> `page_map.md`와 cross-reference. 각 route가 사용하는 컴포넌트 list.
> 본 매핑은 Slice 6 design-review에서 정합 검증 (모든 컴포넌트가 component_map.md에 등재되어야 함).

| Route | 사용 컴포넌트 (진입 순서) | Phase |
|---|---|---|
| `/` (Home) | textarea (native) + SubmitButton + ProgressStepper | 1 active |
| `/plan` | PlanCard + ProgressStepper + ErrorCard | 1 active |
| `/new` (Mode router, UI 없음) | — (middleware only) | 2 spec / 3 impl |
| `/new/discovery/step/1` | WizardStepHeader + CardGrid5 + BrandDirectionCard×5 + SubmitButton + ErrorCard | 2 spec / 3 impl |
| `/new/discovery/step/2` | WizardStepHeader + CardGrid5 + BrandDirectionCard×5 변형 + SubmitButton | 2 spec / 3 impl |
| `/new/discovery/step/3` | WizardStepHeader + CardGrid5 + BrandDirectionCard×5 변형 + SubmitButton | 2 spec / 3 impl |
| `/new/discovery/step/4` | WizardStepHeader + CardGrid5 + BrandDirectionCard×5 변형 + SubmitButton | 2 spec / 3 impl |
| `/new/discovery/step/5` (★ form 예외) | WizardStepHeader + ToneChipsForm + SubmitButton | 2 sketch / 3 impl |
| `/new/discovery/step/6` | WizardStepHeader + DirectionApprovalCard (variant=verbose) | 2 spec / 3 impl |
| `/new/discovery/step/7` | WizardStepHeader + ProgressStepper (4단계) + RAGReferencePanel + PlanCard + ErrorCard | 2 spec / 3 impl |
| `/new/quick` | BreadcrumbBrandPath + QuickInputCard (mode=initial_prompt) + SubmitButton + IntentWarningBox | 2 spec / 3 impl |
| `/new/quick/clarify` | BreadcrumbBrandPath + QuickInputCard (mode=follow_up_question) + SubmitButton (primary + skip) | 2 spec / 3 impl |
| `/new/quick/direction` | BreadcrumbBrandPath + DirectionApprovalCard (variant=minimal) | 2 spec / 3 impl |
| `/new/quick/generate` | BreadcrumbBrandPath + ProgressStepper + PlanCard + ErrorCard | 2 spec / 3 impl |

### Phase 4+ routes (placeholder)
| Route | 사용 컴포넌트 | Phase |
|---|---|---|
| `/plan` (Phase 4 활성) | PlanComparisonCard + ProgressStepper | 4 |
| `/brand/[brandId]/.../video/[videoId]` | PlanOptionCard×3 + BrandMemoryPanel + ChecklistPanel + RegenerateButton + RevisionRequestModal | 4 |
| `/brand/.../output` | OutputViewer + HookCandidateCard + VideoStructureTimeline + ShootingNoteCard + QualityScorePanel + RevisionSuggestionCard + CopyOutputButton | 4 |
| `/login`, `/signup`, `/onboarding`, `/dashboard` | (Phase 5 신규) | 5 |
| `/history`, `/feedback` | (Phase 9 신규 — LikeDislikeFeedback 등) | 9 |
| `/settings` | BrandMemoryPanel + (Phase 11+ dark mode toggle) | 11+ |

→ 본 매핑이 `page_map.md` §1~§4와 일치하는지 Slice 6 검증.

---

## PlanComparisonCard (Phase 4 placeholder)

> **Phase 4 deferred** — Phase 2는 placeholder 1줄만 등재. 본 section은 Phase 4 진입 시 4-layer 정식 entry로 확장 예정.

- **위치 (Phase 4)**: `apps/web/components/discovery/PlanComparisonCard.tsx`
- **역할**: 3-plan 가로 비교 (모바일 세로 스와이프 / 데스크톱 가로 3열) + 1 선택 + 선택 이유 입력
- **Phase 진입**: Phase 4 (MOA Lite 완성 시점, `docs/contracts/api_contract.md` §8.3)
- **Replaceability**: M (예상 — Phase 4 활성 시점에 4-layer 작성하며 확정)
- **Variants**: TBD (Phase 4 진입 시 3개 한정 정책 — ADR-011 정합 — 결정)
- **Wireframe**: `apps/web/wireframes/plan_comparison_placeholder.md` (1줄 placeholder)
- **참조 spec**: `apps/web/design.md` §13 (Final Output 구조) + `output_schema.md` §8 (P-006 plan_candidates)
- **Phase 2 Slice 5 작업**: 본 placeholder entry만 등재. 상세 4-layer는 Phase 4 design-review Skill 호출 후.

---

## Slice 5 통합 검증 체크리스트

본 통합 갱신 후 Slice 6 design-review에서 자동/수동 검증:

- [ ] page_map.md의 모든 route → 사용 컴포넌트가 component_map.md에 존재 (Routes ↔ Components 매핑 표 참조)
- [ ] Replaceability 통합 매트릭스 18 entry 모두 컴포넌트 존재 또는 placeholder 명시
- [ ] 기존 entries (Layout / Input / Discovery / Quick / AI Flow / Output / Project Memory / Feedback) 0줄 수정
- [ ] Phase 2 Slice 2~4 4-layer entries (BrandDirectionCard / CardGrid5 / DirectionApprovalCard / QuickInputCard) 모두 보존
- [ ] PlanComparisonCard placeholder 1개 등재 (Phase 4 deferred)
- [ ] ToneChipsForm placeholder 명시 (Step 5 form 변형, Phase 3 진입 시 4-layer)
- [ ] design_handoff.md §2 매트릭스 18 항목과 본 통합 매트릭스 18 entry 정합 (cross-reference)

---

## 변경 이력 (Slice 5 통합)

- 2026-05-27: Phase 2 Slice 5 통합 갱신
  - Replaceability 통합 매트릭스 18 entry 추가 (모든 컴포넌트 L/M/H 분포 + Variants 수 + 4-layer 완성도)
  - Routes ↔ Components 매핑 표 추가 (page_map.md cross-reference, Phase 1 active + Phase 2 spec + Phase 4+ placeholder)
  - PlanComparisonCard Phase 4 placeholder section 추가 (1~2줄 deferred 명시)
  - ToneChipsForm Step 5 form 변형 deferred 명시
  - 기존 Phase 0/1 + Slice 2/3/4 entries 모두 보존 (0줄 수정, append only)
  - design_handoff.md cross-reference 추가

