# design.md — 영상기획 AI 에이전트 PWA 프론트엔드

> 위치: `apps/web/design.md`
> 상태: Phase 0–1 진입용 통합 초안 (Track A Guided Discovery + Track B Prompt+Approval 하이브리드)
> 데이터 계층: User → Brand → Domain → Series → Video Project (4-layer)
> 카드 규칙: Discovery 단계당 5개, 최종 기획안 3개

---

## 1. Design Purpose

이 문서는 영상기획 AI 에이전트의 Next.js PWA 프론트엔드 설계 기준을 정의한다.

목적:

- 신규 사용자의 콜드스타트 문제(블랭크 프롬프트 불안)를 Guided Discovery로 해결한다.
- 동일 Series 안에서 영상이 누적되는 헤비유저의 반복 부담을 Quick Prompt 모드로 해결한다.
- 두 모드를 같은 데이터 구조(4계층) 위에서 작동시킨다.
- AI 생성 결과는 비교 가능한 3개 후보로 제시한다.
- 추후 Expo React Native 전환 시 공통 로직과 웹 전용 UI를 분리한다.

이 design.md는 시각 가이드가 아니라 제품/UX/AI 출력/메모리 규칙을 고정하는 설계 기준서이다.

---

## 2. Product UX Principle

```
1. 사용자는 처음부터 완성된 기획을 입력하지 않는다.
2. AI는 막연한 입력을 확정된 답이 아닌 검증 가능한 가설 카드로 제안한다.
3. 모든 영상기획은 Project 단위로 관리하며, Brand/Domain/Series 컨텍스트를 상속한다.
4. 같은 Series 안에서는 컨텍스트가 메모리에서 자동 상속되어 입력 부담이 줄어든다.
5. 결과물은 긴 문단이 아니라 비교 가능한 카드 단위로 분할한다.
6. 사용자의 선택뿐 아니라 거절 이유, 수정 요청도 함께 저장해 다음 기획에 반영한다.
7. AI는 확신 못 하는 부분을 가설/질문/경고로 표시한다.
8. 영상 제작/편집/업로드 기능은 MVP에 포함하지 않는다.
9. 영상기획과 무관한 입력은 Project Memory에 저장하지 않는다.
10. 모든 단계는 모바일에서 한 손으로 조작 가능해야 한다.
```

---

## 3. Target User Context

주요 사용자:

1. 영상기획 경험은 부족하지만 콘텐츠를 꾸준히 만들어야 하는 대학생
2. 창업동아리/소규모 팀 운영자
3. 초기 크리에이터·소상공인
4. 굿즈/부스/행사 운영을 콘텐츠화하려는 운영진

사용자 특성:

- "무엇을 찍어야 할지"보다 "어떻게 기획해야 할지"가 어렵다.
- 전문 영상팀이 아니므로 복잡한 제작 도구를 거부한다.
- 모바일에서 빠르게 아이디어를 정리하고 저장하고 싶어 한다.
- AI 결과가 너무 일반적이거나 광고 같으면 신뢰하지 않는다.

테스트 케이스 브랜드: **드림메이트** (대학생 창업 / 동아리 / 커뮤니티 / 굿즈 / 오프라인 행사가 결합된 복합 브랜드).

---

## 4. Hybrid UX Mode

두 모드를 동시에 운영한다.

### Discovery Mode (Track A)

목적: 신규 사용자, 새 Brand/Domain/Series 생성 시 사용.

특징:

- AI가 단계별로 5개 후보 카드 제시
- 사용자는 클릭으로 좁혀감
- 각 클릭은 명시적 선택 데이터로 저장됨
- 5–6단계 (Brand → Domain → Series → Target → Tone → Direction Summary)

### Quick Mode (Track B)

목적: 같은 Series 안에서 새 영상 추가 시 사용.

특징:

- 짧은 프롬프트 입력
- AI가 부족한 정보 1–2개만 질문
- 한 줄 기획 방향 제시 → 사용자 승인/수정
- Brand/Domain/Series 컨텍스트는 메모리에서 자동 주입

두 모드 모두 같은 `generate_plan` 파이프라인으로 수렴해 3개 기획안 카드를 생성한다.

---

## 5. Mode Trigger Rules

```
조건                                              → 기본 모드
신규 회원 첫 영상                                 → Discovery (모든 단계)
Brand 없음                                        → Discovery (Brand 단계부터)
Brand 있고 Domain 없음                            → Discovery (Domain 단계부터)
Brand+Domain 있고 Series 없음                     → Discovery (Series 단계부터)
Brand+Domain+Series 있음, 같은 Series에 영상 추가 → Quick
사용자가 "직접 입력" 명시 선택                    → Quick (Brand 컨텍스트가 있으면 상속)
Quick 결과가 마음에 안 들어 "다시 좁히기" 클릭    → Discovery (현재 깊이부터)
```

원칙: **사용자가 무조건 Discovery만 하거나 무조건 Quick만 하는 게 아니라, 자신의 컨텍스트 상태에 따라 자동 분기된다.** 두 모드 사이 명시적 전환 버튼도 항상 제공한다.

---

## 6. 4-Layer Hierarchy in UX

### 계층 정의

```
User    → 로그인 주체
Brand   → 사용자가 운영하는 콘텐츠 브랜드 (예: 드림메이트, 게임시네마)
Domain  → Brand 안의 주제 영역 (예: 대학생 창업, 동아리 운영)
Series  → Domain 안의 반복 가능한 콘텐츠 시리즈 (예: 창업 이야기)
Video   → Series 안의 개별 영상 프로젝트 (예: OT 준비 영상)
```

### UX 노출 원칙

- 사용자에게 "Brand/Domain/Series" 같은 용어를 직접 노출하지 않는다.
- 카드 wizard 단계 이름으로 부드럽게 표현한다.

```
Brand   → "어떤 활동/브랜드를 운영하시나요?"
Domain  → "어떤 주제 영역인가요?"
Series  → "어떤 이야기 시리즈로 만들까요?"
Video   → "이번 영상의 주제는?"
```

### Workspace 좌측 네비

- Brand 단위로 폴딩
- Brand 클릭 시 Domain 트리 펼침
- Domain 클릭 시 Series 트리 펼침
- Series 클릭 시 그 안의 Video Project 카드 그리드 표시

모바일에서는 트리가 아니라 breadcrumb 형태로 표시한다.

---

## 7. Information Architecture

### MVP IA

```
/ (Landing)
├── /login
├── /onboarding              # 신규 회원 첫 Brand 생성 wizard
├── /dashboard               # Brand 카드 그리드 (사용자 보유 Brand)
│   └── /brand/[brandId]
│       └── /domain/[domainId]
│           └── /series/[seriesId]
│               └── /video/[videoId]    # Project Workspace
├── /new                     # Mode trigger 시작점 (자동 분기)
│   ├── /new/discovery       # Track A
│   └── /new/quick           # Track B
├── /saved                   # 저장된 기획안 목록 (Series 무관)
└── /settings
```

### 확장 IA (Phase 11+)

```
/brand-memory/[brandId]      # Brand별 톤/피해야할 표현 관리
/knowledge                   # LLM Wiki / RAG 관리
/team                        # 팀 협업
/billing
/admin
```

---

## 8. Page Structure

### MVP Pages (10개)

1. **Landing** — 서비스 소개, 로그인 유도
2. **Login** — Supabase Auth (OAuth + 이메일)
3. **Onboarding** — 첫 Brand 생성 wizard (Discovery 압축판)
4. **Dashboard** — Brand 카드 그리드 + "새 영상" 큰 CTA
5. **Discovery Wizard** — 단계별 5장 카드 (Brand/Domain/Series/Target/Tone)
6. **Direction Summary** — 선택한 방향 요약 + 승인/조정
7. **Quick Prompt** — 짧은 프롬프트 + 한 줄 방향 승인
8. **Generation Progress** — 3개 기획안 생성 중 (Intent→Planner→Critic→Rewriter 진행률)
9. **Project Workspace** — 3개 기획안 비교, 선택, 수정, Brand Memory/체크리스트
10. **Final Output** — 최종 결과물 카드 묶음 + 복사/다운로드

### MVP 제외

- Billing
- Team Workspace
- Admin Dashboard
- Expo Mobile App
- Auto Video Editing / Auto Upload

---

## 9. Core User Flow

### Discovery Mode (신규 사용자)

```
1. Landing → Login
2. Onboarding: 짧은 idea 입력 ("창업동아리 활동을 영상으로")
3. Brand 카드 5장 제시 → 선택 (또는 "직접 입력")
4. Domain 카드 5장 → 선택
5. Series 카드 5장 → 선택
6. Target 카드 5장 → 선택
7. Tone 카드 5장 → 선택
8. Direction Summary 확인 → 승인
9. Generation Progress (30–60초)
10. Project Workspace: 3개 기획안 카드 비교
11. 하나 선택 + 선택 이유 입력 → 저장
12. Final Output 확인
```

### Quick Mode (반복 사용자, 같은 Series)

```
1. Dashboard → Series 카드 클릭 → "새 영상 추가" CTA
2. Quick Prompt: 짧은 입력 ("OT 준비 과정 영상")
3. AI 부족정보 질문 (최대 2개): "영상 길이? 후킹 톤?"
4. 한 줄 방향 카드 제시 → 승인/수정
5. Generation Progress (30–60초)
6. Project Workspace: 3개 기획안 카드 비교
7. 선택 + 저장
8. Final Output
```

---

## 10. Component System

### Layout / Navigation

- `AppShell` — 모바일 하단 탭바 + 데스크톱 좌측 사이드바
- `BreadcrumbBrandPath` — Brand > Domain > Series > Video 경로 표시
- `ProjectTreeNav` — 데스크톱 좌측 트리
- `BottomActionBar` — 모바일 하단 고정 CTA

### Input

- `IdeaInputBox` — 짧은 아이디어 입력 (1–2줄, autosave)
- `QuickPromptInput` — Quick Mode 자유 입력
- `IntentQuestionCard` — AI가 부족정보 질문할 때 표시
- `DirectInputFallback` — Discovery 단계에서 "직접 입력" 클릭 시 표시
- `RevisionReasonInput` — 거절 이유, 수정 요청 입력

### Discovery (Track A)

- `WizardStepHeader` — "3/5단계: 시리즈 선택" 같은 진행 표시
- `ChoiceOptionCard` — 5장 후보 카드 단위 (구조: 이름 / 한 줄 설명 / 적합 상황 / 장점 / 주의점 / 선택 버튼)
- `ChoiceCardGrid` — 5장 카드 모바일 세로 / 데스크톱 가로 배치
- `DirectionSummaryCard` — 모든 선택을 종합한 방향 요약

### Quick (Track B)

- `OneLineDirectionCard` — AI가 제안한 한 줄 방향 (편집 가능)
- `ApprovalToggle` — 승인 / 수정 / 다시 좁히기 3-way

### AI Flow

- `GenerationProgressStepper` — 4단계 (Intent / RAG / Plan / Critic) 진행률
- `RAGReferencePanel` — "참고한 기획 기준" 노출
- `AgentStatusIndicator` — 현재 어떤 Agent가 동작 중인지

### Output

- `PlanOptionCard` — 3개 기획안 비교 카드 (구조: 이름 / 콘셉트 / 후킹 / 흐름 / 장점 / 리스크 / 선택)
- `HookCandidateCard` — 후킹 후보 카드 (한 기획안 안에서)
- `VideoStructureTimeline` — 영상 구성안 타임라인
- `ShootingNoteCard` — 촬영 노트
- `QualityScorePanel` — 8차원 점수 + 이유 + 개선안
- `OutputViewer` — 최종 결과물 묶음
- `ChecklistPanel` — Brand 규칙 / 촬영 체크리스트

### Project Memory / Intent

- `BrandMemoryPanel` — 현재 Brand의 톤/금기 표현/자주 쓰는 표현
- `ProjectMemoryDrawer` — 좌측 슬라이드 패널 (메모리 미리보기)
- `IntentWarningBox` — 영상기획 외 입력 감지 시 부드러운 안내

### Feedback / Action

- `LikeDislikeFeedback`
- `SavePlanButton`
- `RegenerateButton`
- `RevisionRequestModal`
- `CopyOutputButton`

---

## 11. Discovery Wizard Rules (Track A)

### 카드 수

- 단계당 정확히 5장.
- 5장 이하만 의미 있는 경우(예: Tone 후보가 3개뿐) 4장까지 허용.
- 6장 이상 금지.

### 카드 구조 (`ChoiceOptionCard`)

```
[방향 이름]            (8–14자, 명사형)
[한 줄 설명]           (30–50자)
[적합한 상황]          (1줄, 예시 1–2개 포함)
[장점]                 (1줄)
[주의점]               (1줄)
[선택 버튼]
```

### 단계 순서 (전체 흐름)

```
Step 1: Idea Input            (자유 입력 1–2줄)
Step 2: Brand 카드 5장        (P-001 prompt)
Step 3: Domain 카드 5장       (P-002 prompt)
Step 4: Series 카드 5장       (P-003 prompt)
Step 5: Target 카드 5장       (P-004a prompt)
Step 6: Tone 카드 5장         (P-004b prompt)
Step 7: Direction Summary     (P-005 prompt, 요약)
```

Onboarding 압축판은 Step 2–4까지만 진행 후 첫 Brand 생성하고 Dashboard로 보낸다.

### 단계별 규칙

- 각 단계 상단에 진행률 표시 (`3/6`).
- "이전 단계" 버튼은 항상 제공.
- "직접 입력" 옵션은 5장 카드 아래에 별도 버튼으로 항상 제공.
- "직접 입력" 선택 시 해당 단계는 자유 입력으로 전환.
- 단계 건너뛰기(Skip)는 Series, Target, Tone 단계에서만 허용 (Brand, Domain은 필수).

### 카드 생성 품질 기준

- 5장은 서로 충분히 구별돼야 함 (의미적 중첩 30% 미만).
- "적합한 상황"에는 사용자가 입력한 idea의 키워드가 1개 이상 반영돼야 함.
- 너무 광고적이거나 과장된 표현 금지 ("최고의", "혁신적인" 등).

---

## 12. Prompt+Approval Rules (Track B)

### 입력

- 짧은 프롬프트 (10–200자).
- 200자 초과 시 "줄여드릴까요?" 제안.

### 부족정보 질문

- 최대 2개까지만 질문.
- 질문은 항상 4지선다 또는 자유 입력 (혼합).
- "이대로 진행" 버튼으로 질문 무시 가능.

### 한 줄 방향

- 형식: "{타깃}을 대상으로 {목적}을 보여주는 {길이} {포맷}"
- 사용자는 인라인 편집 가능.
- "다시 좁히기" 클릭 시 Discovery Mode 진입 (현재 Brand/Domain 컨텍스트는 유지).

---

## 13. Output Display Rules

### 3개 기획안 비교

3개의 `PlanOptionCard`를 모바일에서는 세로 스와이프, 데스크톱에서는 가로 3열 배치한다.

각 카드 구조:

```
[기획안 이름]         (10–16자)
[콘셉트]              (1–2줄)
[후킹 문장]           (실제 영상 시작 후킹)
[영상 흐름]           (3–6 비트)
[장점]                (1–2줄)
[리스크]              (1줄)
[선택 / 수정 / 거절]  (3-way)
```

### 선택 후 상세 표시 순서

1. 한 줄 기획 방향
2. 타깃 분석
3. 후킹 후보 3개 (`HookCandidateCard`)
4. 영상 구성안 (`VideoStructureTimeline`)
5. 촬영 노트 (`ShootingNoteCard`)
6. 품질 평가 점수 (`QualityScorePanel`, 8차원)
7. 개선 제안 (`RevisionSuggestionCard`)
8. 업로드 문구 + 해시태그 + 커뮤니티 유입 문구
9. 저장 / 수정 / 재생성

### 표시 원칙

- 모바일에서는 한 번에 너무 많이 노출하지 않는다 (접기/펼치기).
- 타임라인은 가로 스크롤로 표시.
- 품질 점수는 점수만이 아니라 항상 이유와 개선 제안을 함께.
- 긴 문단은 카드 단위로 분할.

---

## 14. Project Memory UX

### 저장되는 정보

```
Brand 톤
자주 쓰는 표현
피해야 할 표현
선택한 기획안 + 선택 이유
거절한 기획안 + 거절 이유
수정 요청 내용
최종 결과물
```

### UX 표현

- Project Workspace 좌측에 `ProjectMemoryDrawer`로 접혀 있음.
- 사용자가 펼쳐서 항목별로 확인/수정 가능.
- Brand 단위 메모리는 `BrandMemoryPanel`로 별도 노출 (Brand Detail 페이지).

### 자동 반영

- Quick Mode에서 다음 기획 생성 시 Brand Memory가 자동 prompt 주입됨.
- 사용자에게는 "이 Brand 톤이 자동 반영됐어요" 정도로만 안내.

---

## 15. Intent Filtering UX

### 차단 입력 (Project Memory 저장 금지)

```
일반 코딩 질문 / 학교 과제 대행
연애 상담 / 정치 사회 논쟁
일상 잡담 / 개인 감정 토로
의미 없는 테스트 입력
영상기획과 무관한 정보 검색
```

### UX 처리

- 입력 분석 후 영상기획 외 신호 감지 시 `IntentWarningBox` 표시.
- 문구 예시:
  ```
  이 내용은 현재 영상기획 프로젝트와 직접 관련이 없어 보여서
  Project Memory에는 저장하지 않을게요.
  영상 소재로 만들고 싶으시면 "콘텐츠 방향으로 정리" 버튼을 눌러주세요.
  ```
- 거부가 아니라 안내. 사용자가 명시적으로 "콘텐츠 방향으로 정리"하면 영상 소재로 변환되어 저장됨.

### 예외

```
"자바 과제 도와줘"                         → 저장 금지
"자바 과제하다 겪은 일을 쇼츠 소재로"      → 저장 가능
```

---

## 16. Layout Rules

- 모바일 기준 (360–430px) 세로 스크롤 우선.
- 한 화면 한 주요 CTA.
- 주요 CTA는 하단 고정 (`BottomActionBar`).
- 결과물은 섹션별 카드.
- 긴 텍스트는 접기/펼치기.
- 입력 영역과 결과 영역을 한 화면에 과도하게 섞지 않는다.
- 데스크톱: 좌측 `ProjectTreeNav` + 중앙 작업 영역 + 우측 `BrandMemoryPanel` 3열 구조.

---

## 17. Responsive Rules

### Mobile (360–430px)

- 카드 간 간격 16px 이상.
- 하단 CTA 높이 56px 이상.
- 단계 표시는 상단 가로 진행바.
- Plan Option 카드는 세로 스와이프.

### Tablet (768–1024px)

- 카드 2열 배치 검토.
- 생성 progress와 카드 미리보기 분할 가능.

### Desktop (1024px+)

- 3열 레이아웃 (`ProjectTreeNav` / 중앙 / `BrandMemoryPanel`).
- Plan Option 카드 가로 3열.
- 단, MVP는 모바일 기준을 먼저 만족해야 함.

---

## 18. Visual Style Guide

shadcn/ui 기본 + Tailwind CSS를 사용한다.

> **Phase 30 S1 (2026-06-15): Orange × Beige 종이 워크스페이스로 확정.** 아래 톤·색·폰트는 `apps/web/design_reference/VISUAL_CONTRACT.md` + `apps/web/app/globals.css` :root와 일치.

### 톤

- 따뜻한 종이 위에서 아이디어를 정리하는 학생·기획자용 AI 워크스페이스
- 과한 크리에이터 감성보다 정돈된 실용성, 아이보리·베이지 종이 질감
- 카드 기반 정보 구조
- 명확한 주황 CTA

### 색상 토큰 (Phase 30 S1 확정 — 80% 베이지/아이보리/웜그레이 + 20% 주황)

```
background       : 베이지 (#F5EFE6)
surface          : 카드 배경, 아이보리 (#FFFAF4)
border           : 웜 브라운 반투명 (rgba(102,72,54,.16))
text/primary     : 짙은 브라운 (#352A24)
text/secondary   : 웜그레이 (#78685F)
primary(accent)  : 주황 (#F47B20 — hover #E96818, pressed #D94C1A)
warning          : 앰버 (#E0991C, Intent Warning용)
error            : 적갈색 (#C2452A — 주황 CTA와 구분)
critic/good      : 녹색 (#5C8A3A)
critic/bad       : 적갈색 (#C2452A)
rail             : 데스크톱 Primary Rail 짙은 브라운 (#573A2A)
```

주황은 CTA, 현재 선택, 진행률, focus, 핵심 키워드에만 강하게 사용한다. 장문 본문·전체 패널 배경엔 쓰지 않는다.

### 타이포 (Phase 30 S1 — fallback 체인만, 폰트 파일 추가 없음)

- 본문 모바일: 15–16px
- 카드 제목: 17–19px
- 한 줄 방향: 18–22px
- display=Paperlogy (Hero·제목), ui=SUIT Variable/Pretendard (본문·UI), editorial=Noto Serif KR (대본·긴 인용)
- 같은 문단 안에서 세 글꼴 혼용 금지

### 아이콘

- lucide-react 기본 set 사용
- 카드당 아이콘 1개 미만 (정보 위주)

---

## 19. Accessibility Rules

- 버튼 터치 영역 44×44px 이상.
- 폼 입력에 라벨 항상 제공.
- 색상만으로 상태 구분 금지.
- 오류 메시지는 텍스트로 명확히.
- 키보드 탐색 가능.
- 카드 제목 구조를 `h2/h3`로 일관 유지.
- 카드 wizard 진행률은 스크린리더에 읽힐 수 있도록 `aria-current` 사용.

---

## 20. State & Error Rules

### Required States

- Empty State (아직 Brand 없음, 영상 없음)
- Loading State
- Streaming State (생성 진행 중)
- Partial Result State (Plan 3개 중 1개만 도착)
- Error State
- Retry State
- Save Success State
- Memory Updated State

### AI Error Cases

- LLM 응답 실패 → 재시도 버튼 + 부분 결과 보존
- RAG 검색 실패 → "참고 자료 없이 진행할까요?" 선택지
- JSON 파싱 실패 → 자동 1회 재시도 후 실패 시 사용자에게 표시
- 토큰 초과 → 입력 줄이기 제안
- 비용 제한 초과 → 사용자 친화적 안내 (기술 메시지 금지)
- 네트워크 실패 → 로컬 임시 저장 후 재연결 시 자동 동기화
- 결과 저장 실패 → 로컬 임시 상태 안내

### Error UX 원칙

- "오류가 발생했습니다"만 표시 금지.
- 다음 행동을 항상 제시 (재시도, 부분 결과 사용, 처음으로).
- 부분 결과가 있으면 삭제하지 않고 보여준다.

---

## 21. AI Interaction Rules

- AI는 사용자 입력 직후 최종 결과물을 만들지 않는다.
- Discovery Mode는 단계별로 카드만 생성한다.
- Quick Mode는 한 줄 방향 먼저 제시 후 승인을 받는다.
- 생성 중 현재 단계(`의도 분석 중`, `RAG 검색 중`, `기획 생성 중`, `품질 검증 중`)를 텍스트로 표시한다.
- Critic 결과는 점수만이 아니라 이유와 개선안을 함께.
- 사용자는 모든 결과를 저장/수정/재생성할 수 있어야 한다.
- AI 확신 부족 부분은 가설/질문/경고로 표시.
- RAG 참고 자료가 쓰였으면 "참고한 기획 기준" 섹션 제공.
- AI는 광고적 과장 표현을 자체 검열한다 (Critic의 한 차원).

---

## 22. Generation Latency UX

MOA Lite (Intent → Planner → Critic → Rewriter)는 LLM 호출 4회 이상으로 **30–60초** 소요. 모바일에서 이 대기를 견디게 만드는 게 중요.

### 처리 원칙

1. **단계별 스트리밍**: Intent 결과는 5–10초 안에 보여줘서 사용자가 "AI가 일하고 있다"는 신호를 받게 한다.
2. **`GenerationProgressStepper`**: 4단계 진행률을 항상 보이게.
3. **부분 결과 노출**: Plan 3개 중 1개라도 완성되면 즉시 노출.
4. **백그라운드 허용**: 화면 떠나도 생성은 계속됨. 완료 시 토스트 알림.
5. **취소 가능**: "취소하기" 버튼 항상 노출. 취소해도 부분 결과는 저장.

### 금지

- 빈 로딩 스피너 + 30초 대기 (가장 큰 이탈 원인).
- "잠시만 기다려 주세요" 만 표시.

---

## 23. Empty / Onboarding State

### 신규 회원

- Login 직후 `/onboarding`으로 이동.
- 첫 화면: "어떤 활동/브랜드를 콘텐츠로 만들고 싶나요?"
- Discovery Wizard 압축판 (Brand → Domain → Series 3단계만).
- 끝나면 첫 Brand 생성 완료, Dashboard로 이동.

### Brand 있지만 Domain 없음

- Dashboard에서 Brand 클릭 시 "이 브랜드 안에 어떤 주제를 다룰까요?" 안내 + Domain 카드 5장.

### Domain 있지만 Series 없음

- "어떤 이야기 시리즈로 만들까요?" + Series 카드 5장.

### Series 있지만 Video 없음

- "첫 번째 영상의 주제는?" + Quick Prompt.

---

## 24. Design Review Checklist

- [ ] 신규 사용자가 첫 화면에서 무엇을 해야 하는지 1초 안에 보이는가?
- [ ] Discovery 단계가 6단계 이하인가?
- [ ] 단계당 카드가 정확히 5장(또는 의미 있는 4장 미만)인가?
- [ ] 각 카드에 이름 / 설명 / 적합 상황 / 장점 / 주의점이 있는가?
- [ ] Brand → Domain → Series → Video 컨텍스트가 메모리에서 상속되는가?
- [ ] 같은 Series에서 새 영상 만들 때 Quick Mode로 들어가는가?
- [ ] 한 줄 방향 승인 단계가 있는가?
- [ ] 3개 기획안이 비교 가능하게 표시되는가?
- [ ] 영상 구성안이 타임라인 형태로 보이는가?
- [ ] 품질 평가가 점수+이유+개선안 세트로 제공되는가?
- [ ] 30–60초 생성 대기 동안 단계별 진행률이 보이는가?
- [ ] 부분 결과가 즉시 노출되는가?
- [ ] 영상기획 외 입력에 IntentWarningBox가 작동하는가?
- [ ] 거절 이유, 수정 요청이 함께 저장되는가?
- [ ] 모바일에서 한 손 조작 가능한가?
- [ ] CTA가 항상 하단 고정인가?
- [ ] 영상 제작/편집 UI가 들어가지 않았는가?
- [ ] 광고적 과장 표현이 결과에 없는가?
- [ ] 대학생 현실감/커뮤니티 유입/브랜드 신뢰 중 하나 이상과 연결되는가?

---

## 25. Expansion Design Scope

후속 확장 (Phase 11+):

- Brand Memory 관리 화면 (피해야 할 표현 편집)
- Series 단위 콘텐츠 캘린더
- RAG 지식 관리 화면
- 프롬프트 버전 관리 화면
- 팀 협업 화면 / 권한 관리
- 크레딧/결제 화면
- 관리자 로그 화면
- Expo React Native 앱
- 사용자별 스타일 프로필
- 영상 성과 데이터 연결 (조회수/유입 → 기획 개선)

---

## 26. Open Questions (Phase 1 진입 전 확정 필요)

1. accent 색상 1개 — 드림메이트 컬러로 갈지, 일반 SaaS 톤으로 갈지.
2. Onboarding wizard에서 Brand 생성을 강제할지, 건너뛰기 허용할지.
3. Quick Mode "부족정보 질문"의 최대 개수 (현재 2개 권장).
4. Critic의 8차원 중 사용자에게 보여줄 차원 (전부 vs 핵심 4개).
5. 부분 결과 노출 시점 (Plan 1/3 완성 vs 2/3 완성).
6. Series 단위 메모리 vs Brand 단위 메모리 우선순위.
7. 광고적 표현 자체 검열 강도 (Critic 자동 차단 vs 경고만).
