# Page Map

> 위치: `apps/web/page_map.md`
> 정합 기준: `apps/web/design.md` §5, §7, §8, §9, §11, §12, §13
> Mode: Discovery (Track A) + Quick (Track B) Hybrid

## Mode 진입 분기 (design.md §5)

사용자는 무조건 한 쪽 모드만 쓰지 않는다. 컨텍스트(Brand/Domain/Series 보유 여부)에 따라 `/new` 진입 시 자동으로 Discovery 또는 Quick으로 라우팅된다. 두 모드 사이 명시적 전환 버튼("다시 좁히기" / "직접 입력")도 항상 제공한다.

| 조건 | 기본 모드 |
|---|---|
| 신규 회원 첫 영상 | Discovery (모든 단계) |
| Brand 없음 | Discovery (Brand 단계부터) |
| Brand 있고 Domain 없음 | Discovery (Domain 단계부터) |
| Brand+Domain 있고 Series 없음 | Discovery (Series 단계부터) |
| Brand+Domain+Series 있음 | Quick |
| "직접 입력" 명시 선택 | Quick (Brand 컨텍스트 상속) |
| Quick 결과에서 "다시 좁히기" | Discovery (현재 깊이부터) |

## MVP Pages (10개, design.md §8)

각 페이지: 경로 | 진입 조건 | 표시 카드 | 다음 행동 | 의존 컴포넌트

### 1. Landing (`/`)
- 진입: 비로그인 첫 방문
- 표시: 제품 소개, Login CTA
- 다음 행동: → Login

### 2. Login (`/login`)
- 진입: 로그인 필요
- 인증: Supabase Auth (OAuth + 이메일)
- 다음 행동: 성공 → Onboarding(신규) / Dashboard(기존), 실패 → Landing

### 3. Onboarding (`/onboarding`)
- 진입: 신규 회원 첫 로그인
- 표시: Discovery 압축판 (Step 2 Brand → Step 3 Domain → Step 4 Series, 즉 P-001/P-002/P-003)
- 다음 행동: 첫 Brand 생성 완료 → Dashboard
- 의존: WizardStepHeader, ChoiceOptionCard, ChoiceCardGrid, DirectInputFallback

### 4. Dashboard (`/dashboard`)
- 진입: 기존 사용자 로그인 후 기본 진입점
- 표시: Brand 카드 그리드 + "새 영상" 큰 CTA
- 다음 행동:
  - "새 영상" → `/new` (Mode 자동 분기)
  - Brand 카드 → `/brand/[brandId]` (Domain 트리 펼침)
  - Series 카드 → Quick 진입 (`/new/quick`)
- 의존: AppShell, BreadcrumbBrandPath, ProjectTreeNav

### 5. Discovery Wizard (`/new/discovery`)
- 진입: Mode 분기에서 Discovery 결정 (§5)
- 표시: 단계별 5장 카드 (Brand/Domain/Series/Target/Tone)
- 단계 순서 (design.md §11):
  - Step 1: Idea Input — 자유 입력 1–2줄
  - Step 2: Brand 카드 5장 — P-001 prompt
  - Step 3: Domain 카드 5장 — P-002 prompt
  - Step 4: Series 카드 5장 — P-003 prompt
  - Step 5: Target 카드 5장 — P-004a prompt
  - Step 6: Tone 카드 5장 — P-004b prompt
  - Step 7: Direction Summary — P-005 prompt
- 카드 규칙: 단계당 정확히 5장 (4 추천 + 1 "직접 입력"), 6장 이상 금지
- Skip 허용: Series, Target, Tone (Brand, Domain은 필수)
- 다음 행동: Step 7 완료 → Direction Summary
- 의존: WizardStepHeader, ChoiceOptionCard, ChoiceCardGrid, DirectInputFallback, IdeaInputBox

### 6. Direction Summary (`/new/direction`)
- 진입: Discovery Step 7 완료
- 표시: DirectionSummaryCard (모든 선택 종합)
- 다음 행동: 승인 → Generation Progress / 수정 → 이전 단계로 복귀
- 의존: DirectionSummaryCard, ApprovalToggle

### 7. Quick Prompt (`/new/quick`)
- 진입: Brand+Domain+Series 있음 / "직접 입력" 선택
- 표시: QuickPromptInput (10–200자) + ContextInheritanceBadge (상속된 Brand/Domain/Series) + IntentQuestionCard (부족정보 최대 2개)
- 한 줄 방향: OneLineDirectionCard ("{타깃}을 대상으로 {목적}을 보여주는 {길이} {포맷}")
- 다음 행동: 승인 → Generation Progress / "다시 좁히기" → Discovery (현재 깊이부터)
- 의존: QuickPromptInput, IntentQuestionCard, OneLineDirectionCard, ApprovalToggle

### 8. Generation Progress (`/new/generate`)
- 진입: Direction Summary / Quick 승인 후
- 표시: 4단계 GenerationProgressStepper (Intent → RAG → Plan → Critic) + 부분 결과 즉시 노출
- 대기 시간: 30–60초
- 의존: GenerationProgressStepper, RAGReferencePanel, AgentStatusIndicator

### 9. Project Workspace (`/brand/[brandId]/domain/[domainId]/series/[seriesId]/video/[videoId]`)
- 진입: Generation 완료
- 표시: PlanOptionCard ×3 (콘셉트/후킹/흐름/장점/리스크) 비교 + Brand Memory / 체크리스트
- 카드 배치: 모바일 세로 스와이프, 데스크톱 가로 3열
- 다음 행동: 1개 선택 + 선택 이유 입력 → 저장 → Final Output / 재생성 / 수정 요청
- 의존: PlanOptionCard, BrandMemoryPanel, ChecklistPanel, RegenerateButton, RevisionRequestModal

### 10. Final Output (`/brand/.../video/[videoId]/output`)
- 진입: Project Workspace에서 plan 선택 후 저장
- 표시 순서 (design.md §13):
  1. 한 줄 기획 방향 (OneLineDirectionCard)
  2. 타깃 분석
  3. 후킹 후보 3개 (HookCandidateCard)
  4. 영상 구성안 (VideoStructureTimeline)
  5. 촬영 노트 (ShootingNoteCard)
  6. 품질 평가 점수 (QualityScorePanel, 8차원)
  7. 개선 제안 (RevisionSuggestionCard)
  8. 업로드 문구 + 해시태그 + 커뮤니티 유입 문구
  9. 저장 / 수정 / 재생성
- 의존: OutputViewer, HookCandidateCard, VideoStructureTimeline, ShootingNoteCard, QualityScorePanel, RevisionSuggestionCard, CopyOutputButton

### 추가 경로 (MVP 보조)
- `/saved` — 저장된 기획안 목록 (Series 무관) | 의존: PlanOptionCard
- `/settings` — Brand Memory 관리, 계정, 로그아웃 | 의존: BrandMemoryPanel
- `/new` — Mode trigger entry (자동 분기 라우터, UI 없음)

## 페이지-컴포넌트 매트릭스

| Page | Primary Components |
|---|---|
| Landing | (marketing only) |
| Login | (Supabase Auth UI) |
| Onboarding | WizardStepHeader, ChoiceOptionCard, IdeaInputBox |
| Dashboard | AppShell, BreadcrumbBrandPath, ProjectTreeNav, BottomActionBar |
| Discovery Wizard | WizardStepHeader, ChoiceOptionCard ×5, ChoiceCardGrid, DirectInputFallback, IdeaInputBox |
| Direction Summary | DirectionSummaryCard, ApprovalToggle |
| Quick Prompt | QuickPromptInput, IntentQuestionCard, OneLineDirectionCard, ApprovalToggle |
| Generation Progress | GenerationProgressStepper, RAGReferencePanel, AgentStatusIndicator |
| Project Workspace | PlanOptionCard ×3, BrandMemoryPanel, ChecklistPanel, RegenerateButton, RevisionRequestModal |
| Final Output | OutputViewer, HookCandidateCard, VideoStructureTimeline, ShootingNoteCard, QualityScorePanel, RevisionSuggestionCard, CopyOutputButton |
| Saved | PlanOptionCard |
| Settings | BrandMemoryPanel |

## Phase 매핑

- MVP (Phase 1~10): 위 10개 페이지 + `/saved`, `/settings` 라우트 전부
- Phase 11+ (확장 IA): `/brand-memory/[brandId]`, `/knowledge`, `/team`, `/billing`, `/admin`
- Phase 21+: Expo React Native 모바일 앱 (동일 정보 구조 반영)

## MVP 제외 (영구 / 후속 phase)

- Billing, Team Workspace, Admin Dashboard
- Expo Mobile App (Phase 21+)
- Auto Video Editing / Auto Upload (영구 제외)
