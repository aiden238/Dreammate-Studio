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
