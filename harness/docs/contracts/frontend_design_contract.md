# frontend_design_contract.md — 프론트엔드 디자인 / 토큰 / 접근성 Contract

> 위치: `docs/contracts/frontend_design_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `apps/web/design.md` (전체 UX 기준, 689줄)
> 참조: `apps/web/page_map.md` (MVP 10 페이지)
> 참조: `apps/web/component_map.md` (컴포넌트 그룹)
> 참조: `docs/contracts/error_response_contract.md` (user_action 매핑)
> 참조: `docs/contracts/output_schema.md` §14 (광고 단어 차단 UI)
> 참조: `docs/contracts/api_contract.md` §13 (SSE progress stepper)
> 참조: `docs/contracts/tech_stack_contract.md` (S3-3에서 완성, Next.js + shadcn/ui + Tailwind 확정)

---

## 0. 이 문서의 위치

`apps/web/design.md`가 "왜/무엇을 만드는가"를 정의한다면, 이 문서는 그 결정을 **재사용 가능한 디자인 토큰 / 컴포넌트 명명 규칙 / 접근성 기준 / UI 매핑 표**로 정형화한다.

이 문서가 정의하는 대상:

1. 디자인 토큰 (color / spacing / typography / radius / shadow / motion)
2. 반응형 breakpoints
3. 컴포넌트 명명 규칙
4. 접근성 표준 (WCAG 2.1 AA)
5. PWA 표준 (offline / install / splash)
6. error_response의 user_action → UI 매핑
7. 4단계 progress stepper → 컴포넌트 매핑
8. 광고 단어 차단 → UI inline warning 정책
9. 디자인 리뷰 체크리스트 (design-review Skill 연동)

이 문서가 정의하지 않는 대상:

- 전체 UX 흐름 / 페이지 구조 → `apps/web/design.md`, `page_map.md`
- 컴포넌트 props 상세 → `apps/web/component_map.md`
- 에러 응답 형식 → `error_response_contract.md`
- 기술 스택 결정 → `tech_stack_contract.md` (S3-3에서 완성)

---

## 1. 설계 원칙

```
1. 모바일 우선. 360px 너비에서 한 손 조작 가능해야 함.
2. shadcn/ui 컴포넌트를 기본 사용. 필요 시 wrap해서 우리 토큰 주입.
3. 토큰은 CSS variable로 노출. Tailwind config는 토큰을 alias.
4. 모든 색상은 light/dark 모드 쌍을 가진다 (dark는 Phase 2+ 활성).
5. 접근성은 design-time 기본값. 컴포넌트 PR에서 a11y 체크리스트 통과 필수.
6. 광고/금기 표현 단어는 입력 시 inline warning. 차단 아닌 안내.
7. 모든 진행 시간 ≥ 30s 작업은 4단계 stepper로 분해.
8. 에러는 카드 단위로 표시. 토스트는 일시적/부가 정보에만.
9. 모션은 prefers-reduced-motion을 항상 존중.
10. Web Vitals 목표: LCP < 2.5s, FID < 100ms, CLS < 0.1 (모바일 3G 기준).
```

---

## 2. 디자인 토큰

### 2.1 Color

토큰 명명: `--color-{role}-{scale}`. 스케일은 50/100/.../900.

> **Phase 30 S1 (2026-06-15): Orange × Beige 리브랜딩.** 아래 값은 `apps/web/tailwind.config.ts` legacy scale 및 `apps/web/design_reference/DESIGN_TOKENS.css` / `VISUAL_CONTRACT.md` §2와 일치. 비율 80% 베이지·아이보리·웜그레이 + 20% 주황(CTA/선택/진행/focus만).

#### Primary (accent, CTA) — Orange #F47B20

```
--color-primary-50:   #FFF6E8
--color-primary-100:  #FFE9C4
--color-primary-200:  #FFD68B
--color-primary-300:  #FFBF57
--color-primary-400:  #FF9A2F
--color-primary-500:  #F47B20   /* base accent */
--color-primary-600:  #E96818   /* hover */
--color-primary-700:  #D94C1A   /* pressed */
--color-primary-800:  #AD3817
--color-primary-900:  #7C2915
```

용도: 주요 CTA, 선택 상태, 진행률 바, 활성 탭. (장문 본문·전체 패널 배경엔 금지.)

#### Secondary (보조 강조)

```
--color-secondary-500: #FFB23F   /* amber accent */
```

용도: 보조 강조, 정보성 배지 (예: "AI 생성", "참고 자료 사용").

#### Neutral (text/surface/border) — Warm beige~brown

```
--color-neutral-0:   #FFFFFF
--color-neutral-50:  #FFFAF4   /* surface (아이보리) */
--color-neutral-100: #F5EFE6   /* background (베이지) */
--color-neutral-200: #EEE3D5   /* subtle bg / border */
--color-neutral-300: #DDCDBD
--color-neutral-400: #A08E82   /* placeholder */
--color-neutral-500: #78685F   /* muted text */
--color-neutral-600: #65544B
--color-neutral-700: #4D3D35
--color-neutral-800: #3F3029
--color-neutral-900: #352A24   /* primary text (짙은 브라운) */
```

매핑:
- `background`: neutral-100 (베이지)
- `surface` (카드): neutral-50 (아이보리)
- `border`: `rgba(102,72,54,.16)` (웜 브라운 반투명)
- `text/primary`: neutral-900
- `text/secondary`: neutral-500
- `text/placeholder`: neutral-400

#### Semantic — 웜 톤과 구분 (error=적갈색, warning=앰버)

```
/* Success (Critic 좋은 점수, save 성공) */
--color-success-50:  #EAF1E0
--color-success-500: #5C8A3A
--color-success-700: #3F6326

/* Warning (Intent warning, ad phrase 2차 경고) — 앰버 */
--color-warning-50:  #FCF1DC
--color-warning-500: #E0991C
--color-warning-700: #9C6A12

/* Error (LLM 실패, 검증 실패) — 적갈색, primary 주황과 구분 */
--color-error-50:    #F7E6E0
--color-error-500:   #C2452A
--color-error-700:   #8F2E1B

/* Info (참고 자료, RAG 사용 표시) */
--color-info-50:     #E6EDF5
--color-info-500:    #4A6FA5
--color-info-700:    #34507A
```

#### Critic 점수 시각화 (8차원)

```
--color-critic-good:    var(--color-success-500)
--color-critic-medium:  var(--color-warning-500)
--color-critic-bad:     var(--color-error-500)
```

점수 매핑: 4–5 → good, 2–3 → medium, 0–1 → bad.

**금지:** primary 외 색상은 강조에만 제한 사용. UI 전반을 chromatic하게 만들지 않음 (design.md §18).

### 2.2 Spacing (4px base unit)

```
--space-0:   0
--space-1:   4px
--space-2:   8px
--space-3:   12px
--space-4:   16px    /* default gap */
--space-5:   20px
--space-6:   24px
--space-8:   32px
--space-10:  40px
--space-12:  48px
--space-16:  64px
--space-20:  80px
```

용도:
- 카드 padding: space-4 (모바일), space-6 (데스크톱)
- 카드 간 gap: space-4 이상 (design.md §17)
- 섹션 간 margin: space-8 ~ space-12

### 2.3 Typography

토큰 명명: `--font-{role}-{size|weight|line}`.

#### Font Family

> **Phase 30 S1 (VISUAL_CONTRACT §4):** font-family **fallback 체인만** 정의 — 폰트 파일/deps 추가 없음. display=Paperlogy(제목), ui=SUIT/Pretendard(본문·UI), editorial=Noto Serif KR(대본·인용). 같은 문단 내 3종 혼용 금지.

```
--font-family-display:    "Paperlogy", "SUIT Variable", "SUIT", "Pretendard Variable", "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif
--font-family-sans:       "SUIT Variable", "SUIT", "Pretendard Variable", "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif
--font-family-editorial:  "Noto Serif KR", "MaruBuri", "Nanum Myeongjo", serif
--font-family-mono:       "JetBrains Mono", "Menlo", "Consolas", monospace
```

design.md §18: 시스템 폰트 우선. Hero/제목은 display, 본문·UI는 sans, 대본·긴 인용은 editorial.

#### Type Scale

| 토큰 | font-size | line-height | font-weight | 용도 |
|---|---|---|---|---|
| `--font-display` | 28–32px | 1.2 | 700 | landing hero |
| `--font-h1` | 24–28px | 1.25 | 700 | 페이지 제목 |
| `--font-h2` | 20–22px | 1.3 | 600 | 섹션 제목 |
| `--font-h3` | 17–19px | 1.35 | 600 | 카드 제목 (design.md §18) |
| `--font-h4` | 15–17px | 1.4 | 600 | 카드 부제 |
| `--font-body-lg` | 18–22px | 1.5 | 400 | 한 줄 방향 (design.md §18) |
| `--font-body` | 15–16px | 1.5 | 400 | 본문 모바일 |
| `--font-body-sm` | 14px | 1.5 | 400 | 보조 텍스트 |
| `--font-caption` | 12–13px | 1.4 | 400 | placeholder, meta |
| `--font-mono` | 13–14px | 1.4 | 400 | code, request_id |

모바일 / 데스크톱 사이즈는 clamp 사용 권장:
```css
font-size: clamp(15px, 1.6vw + 12px, 16px);
```

### 2.4 Radius

```
--radius-sm:   4px    /* badge, chip */
--radius-md:   8px    /* button, input */
--radius-lg:   12px   /* card */
--radius-xl:   16px   /* modal */
--radius-2xl:  24px   /* hero */
--radius-full: 9999px /* avatar, pill */
```

기본 카드: radius-lg. 모달: radius-xl.

### 2.5 Shadow

```
--shadow-xs:   0 1px 2px 0 rgba(0,0,0,0.05)
--shadow-sm:   0 1px 3px 0 rgba(0,0,0,0.10), 0 1px 2px -1px rgba(0,0,0,0.10)
--shadow-md:   0 4px 6px -1px rgba(0,0,0,0.10), 0 2px 4px -2px rgba(0,0,0,0.06)
--shadow-lg:   0 10px 15px -3px rgba(0,0,0,0.10), 0 4px 6px -4px rgba(0,0,0,0.06)
--shadow-xl:   0 20px 25px -5px rgba(0,0,0,0.10), 0 8px 10px -6px rgba(0,0,0,0.04)
```

용도:
- 기본 카드: shadow-sm (hover 시 shadow-md)
- 떠 있는 패널 (BottomActionBar): shadow-lg
- 모달: shadow-xl
- BrandMemoryPanel slide: shadow-md

### 2.6 Motion

```
--motion-instant:   0ms                  /* state 변경, prefers-reduced 시 사용 */
--motion-fast:      150ms ease-out       /* hover, focus, button press */
--motion-normal:    300ms ease-in-out    /* card flip, modal open */
--motion-slow:      600ms cubic-bezier(0.4, 0, 0.2, 1)   /* page transition, partial result reveal */
--motion-spring:    cubic-bezier(0.34, 1.56, 0.64, 1)    /* card snap, selection bounce */
```

#### prefers-reduced-motion 처리

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0ms !important;
    transition-duration: 0ms !important;
    scroll-behavior: auto !important;
  }
}
```

모든 컴포넌트가 이 미디어 쿼리를 존중해야 함. 단 progress stepper 같은 정보 전달 모션은 fade만 0ms로 단축하고 텍스트 변경은 유지.

### 2.7 Z-index

```
--z-base:           0
--z-dropdown:       10
--z-sticky:         20
--z-fixed:          30      /* BottomActionBar */
--z-overlay:        40      /* drawer backdrop */
--z-drawer:         50      /* BrandMemoryPanel, ProjectMemoryDrawer */
--z-modal:          60      /* RevisionRequestModal */
--z-toast:          70
--z-popover:        80
--z-tooltip:        90
```

---

## 3. 반응형 Breakpoints

Mobile-first. 미디어 쿼리는 `min-width` 기반.

```
--bp-xs:   0       /* default, 360px+ */
--bp-sm:   480px   /* 큰 폰 */
--bp-md:   768px   /* tablet */
--bp-lg:   1024px  /* desktop */
--bp-xl:   1440px  /* wide desktop */
```

### 3.1 레이아웃 분기 (design.md §17 정합)

| 범위 | 레이아웃 | 카드 배치 |
|---|---|---|
| 360–479 (mobile xs) | 1열, BottomActionBar 고정 | Plan Option 세로 스와이프 |
| 480–767 (mobile lg) | 1열, 카드 폭 증가 | Plan Option 세로 |
| 768–1023 (tablet) | 1열 또는 2열, 사이드 패널 옵셔널 | Plan Option 1–2열 |
| 1024–1439 (desktop) | 3열 (Nav / Center / Memory) | Plan Option 가로 3열 |
| 1440+ (wide) | 3열, 카드 폭 증가 | Plan Option 가로 3열 + 더 큰 카드 |

### 3.2 SafeArea (PWA)

```css
padding-top:    env(safe-area-inset-top);
padding-bottom: env(safe-area-inset-bottom);
padding-left:   env(safe-area-inset-left);
padding-right:  env(safe-area-inset-right);
```

iOS 노치 / 안드로이드 제스처 영역에서 BottomActionBar가 가려지지 않도록.

### 3.3 터치 타겟

design.md §19 정합: 모든 인터랙티브 요소는 **min 44×44px**. 작은 아이콘 버튼도 padding으로 영역 확보.

---

## 4. 컴포넌트 명명 규칙

`apps/web/component_map.md`가 컴포넌트 목록의 단일 출처. 이 문서는 명명 규칙만 고정.

### 4.1 PascalCase + 종류별 suffix

```
Layout:       AppShell, BreadcrumbBrandPath, ProjectTreeNav, BottomActionBar
Card:         ChoiceOptionCard, PlanOptionCard, HookCandidateCard, ShootingNoteCard
Button:       SavePlanButton, RegenerateButton, CopyOutputButton
Input:        IdeaInputBox, QuickPromptInput, RevisionReasonInput
Panel:        BrandMemoryPanel, QualityScorePanel, RAGReferencePanel, ChecklistPanel
Drawer:       ProjectMemoryDrawer
Modal:        RevisionRequestModal
Header:       WizardStepHeader
Indicator:    AgentStatusIndicator, GenerationProgressStepper, IntentWarningBox
Toggle:       ApprovalToggle, LikeDislikeFeedback
Badge:        ContextInheritanceBadge
Timeline:     VideoStructureTimeline
Grid:         ChoiceCardGrid
Fallback:     DirectInputFallback
Viewer:       OutputViewer
```

### 4.2 props 명명

```
- 콜백: onXxx (onSelect, onApprove, onShorten, onAnswer)
- boolean: isXxx / hasXxx / canXxx
- 데이터: 단수 명사 또는 ~s 복수 (card, cards[5])
- 외부 ID: xxxId (brandId, planId)
```

### 4.3 file structure (제안)

```
apps/web/components/
  layout/
    AppShell/
      AppShell.tsx
      AppShell.stories.tsx     (Storybook, Phase 2+)
      AppShell.test.tsx        (Phase 1 후반)
      index.ts
  discovery/
    ChoiceOptionCard/
    ChoiceCardGrid/
    WizardStepHeader/
  ai-flow/
    GenerationProgressStepper/
    AgentStatusIndicator/
    RAGReferencePanel/
  ...
```

배치 그룹은 component_map.md의 그룹 (Layout / Input / Discovery / Quick / AI Flow / Output / Project Memory / Feedback).

### 4.4 import 규칙

- 상대 경로 import는 같은 그룹 내에서만
- 그룹 간은 alias 사용 (`@/components/discovery/...`)
- shadcn/ui 컴포넌트는 항상 wrap (직접 import 금지)
  - 예: `Button` (shadcn) → `PrimaryButton`, `GhostButton`, `DangerButton` 등 wrap

---

## 5. 접근성 표준 (WCAG 2.1 AA)

### 5.1 키보드 네비게이션

모든 인터랙티브 요소는 키보드 단독 조작 가능.

```
Tab          → 다음 focusable로 이동
Shift+Tab    → 이전 focusable로 이동
Enter / Space → 활성화 (버튼/카드 선택)
Esc          → 모달/드로어 닫기, 진행 취소
방향키       → 카드 그리드 내 이동 (5장 카드 사이)
```

### 5.2 포커스 표시

```css
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
```

마우스 클릭 시(`:focus`)는 outline 숨김, 키보드 포커스(`:focus-visible`)만 표시. shadcn/ui 기본값 활용.

### 5.3 스크린 리더

```
- 모든 버튼: aria-label 또는 visible text
- 카드 wizard 진행률: aria-current="step" (design.md §19)
- 진행 상태 변경: aria-live="polite" (AgentStatusIndicator)
- 에러 메시지: role="alert", aria-live="assertive"
- 모달 열림: aria-modal="true", focus trap 적용
- 카드 그리드: role="radiogroup" (5장 중 1장 선택 의미)
- 각 카드: role="radio", aria-checked
```

### 5.4 색상 대비

| 요소 | 최소 대비 | 비고 |
|---|---|---|
| 본문 텍스트 | 4.5:1 | WCAG AA 일반 텍스트 |
| 큰 텍스트 (18px+ 또는 14px+ bold) | 3:1 | WCAG AA 큰 텍스트 |
| UI 컴포넌트 (border, icon) | 3:1 | 비텍스트 |
| 포커스 표시 | 3:1 (배경 대비) | |

토큰 조합 검증 (Phase 30 S1 웜 팔레트 기준):
- text-default(#352A24) on bg-default(#F5EFE6): ~10:1 ✓ (본문)
- text-muted(#78685F) on bg-default(#F5EFE6): ~3.7:1 → 본문은 14px+ 또는 보조 텍스트로 제한, 작은 본문엔 text-default 사용
- primary CTA(#F47B20) 배경 위 텍스트는 짙은 브라운(text-default) 사용 — 흰 텍스트 대비 부족 주의 (VISUAL_CONTRACT §7)
- warning-500(앰버)·error-500(적갈색) 텍스트는 700 단계 사용해 대비 확보

### 5.5 색상만으로 상태 구분 금지 (design.md §19)

Critic 점수 시각화:
- 색상 + 숫자 + 아이콘 3중 표시
- 막대 그래프 길이로도 표현
- "좋음/보통/주의" 텍스트 라벨 동반

### 5.6 폼 라벨

- 모든 input은 명시적 label 또는 aria-labelledby
- placeholder만으로 label 대체 금지
- 오류는 aria-describedby로 input과 연결

### 5.7 모션 감소

`prefers-reduced-motion: reduce` 시:
- 모든 transition / animation 0ms (§2.6)
- 단 정보 변경(텍스트 교체, 상태 표시)은 유지
- progress stepper의 단계 변경은 fade 0ms로 변경하되 텍스트 업데이트는 즉시

### 5.8 글자 크기 확대

브라우저 200% 확대 시에도 horizontal scroll 없이 모든 콘텐츠 접근 가능. 모바일 ≥ 320px 너비에서도.

### 5.9 다국어 lang

```html
<html lang="ko">
```

Phase 2+ 다국어 도입 시 동적 변경.

---

## 6. PWA 표준

### 6.1 manifest.json (최소 필드)

```json
{
  "name": "영상기획 AI 에이전트",
  "short_name": "영상기획",
  "description": "Discovery + Quick 모드로 영상기획 후보를 만들어요",
  "start_url": "/dashboard",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#FAFAFA",
  "theme_color": "#6366F1",
  "lang": "ko",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### 6.2 Service Worker

```
- workbox 또는 Next.js next-pwa 플러그인
- 캐시 전략:
  - HTML / JS / CSS: stale-while-revalidate
  - 이미지: cache-first (max-age 7d)
  - API 응답: network-first, 5s timeout, 폴백 캐시
  - SSE / WebSocket: 캐시 제외 (no-store)
```

### 6.3 Offline fallback

- 라우트 `/offline.html` 항상 캐시
- API 요청 실패 시 "오프라인이에요. 연결되면 자동으로 다시 시도할게요" 토스트
- localStorage / IndexedDB에 미저장 입력 보관 → 재연결 시 자동 sync

### 6.4 Install prompt

- 사용자 첫 영상 생성 완료 후 `beforeinstallprompt` 이벤트 표시
- 첫 진입에 즉시 노출 금지 (이탈 방지)
- 노출 후 거절 시 30일간 재노출 안 함

### 6.5 Splash screen

- iOS: apple-touch-startup-image 메타 태그
- Android: theme_color + background_color 자동 사용
- 첫 진입 후 첫 페인트까지 < 1.5s 목표

---

## 7. error_response의 user_action → UI 매핑

`error_response_contract.md` §6의 8가지 user_action 키를 컴포넌트로 매핑.

| user_action | 버튼 라벨 | 동작 | 우선순위 | 매핑 컴포넌트 |
|---|---|---|---|---|
| `retry` | "다시 시도" | 같은 요청 재시도 (retry_after 카운트다운 표시) | 1 | `RetryButton` |
| `reframe_input` | "다시 입력하기" | 입력 폼 이전 단계로 복귀 (입력값 보존) | 3 | `ReframeButton` |
| `wait` | (버튼 없음) | retry_after 카운트다운만 표시 | — | `WaitCountdown` |
| `contact_support` | "문의하기" | request_id 미리 채운 문의 폼 | 4 | `ContactSupportLink` |
| `go_back` | "처음으로" | 현재 진행 폐기, 홈/대시보드로 | 4 | `GoBackButton` |
| `continue_partial` | "부분 결과로 진행" | partial_result.data 사용 | 2 | `ContinuePartialButton` |
| `skip_rag` | "참고 자료 없이 진행" | rag_context=[]로 Planner 재호출 | 2 | `SkipRagButton` |
| `manual_edit` | "직접 다듬기" | 사용자 편집 모드 진입 | 3 | `ManualEditButton` |

### 7.1 동시 노출 규칙

`error_response_contract.md` §6 정합: 동시에 최대 2개 액션 노출.

UI 컨테이너:
```
ErrorCard
  ├─ icon (category별)
  ├─ title (categoryTitle)
  ├─ user_message
  ├─ context (request_id, small/muted)
  └─ actions (max 2)
       ├─ PrimaryAction  (우선순위 1순위)
       └─ SecondaryAction (우선순위 2~4순위 중 1개)
```

### 7.2 category별 시각

| category | icon | accent color |
|---|---|---|
| input_validation | ⓘ | info-500 |
| llm_failure | ⚠ | warning-500 |
| rag_failure | ⓘ | info-500 |
| db_failure | ✗ | error-500 |
| rate_limit | ⏱ | warning-500 |
| security_block | ⚠ | error-500 |
| unknown | ? | neutral-500 |

### 7.3 retry_after 카운트다운

```
retryable=true AND retry_after > 0:
  버튼 라벨: "5초 후 다시 시도" → "4초 후..." → ... → "다시 시도"
  카운트 끝 → 자동 재시도 (사용자가 다른 액션 안 했을 때만)
  컴포넌트: <CountdownButton initial={5} onComplete={onRetry} />
```

`prefers-reduced-motion`: 카운트다운 숫자는 그대로 갱신하되 애니메이션 transition은 0.

---

## 8. 4단계 progress stepper → 컴포넌트 매핑

`api_contract.md` §13 SSE / `error_response_contract.md` §7 / `agent_io_contract.md` §8.3 그래프 정합.

### 8.1 단계 정의

```
[1] intent   → [2] rag    → [3] planner   → [4] critic   → done
```

### 8.2 컴포넌트: `GenerationProgressStepper`

```typescript
type StepperProps = {
  currentStage: "intent" | "rag" | "planner" | "critic" | "done";
  stageStatus: {
    intent:   "pending" | "active" | "completed" | "failed";
    rag:      "pending" | "active" | "completed" | "failed" | "skipped";
    planner:  "pending" | "active" | "completed" | "failed" | "partial";
    critic:   "pending" | "active" | "completed" | "failed" | "partial";
  };
  partialResult?: PartialResult;   // error_response_contract §7
  onCancel?: () => void;
  onRetry?: () => void;
  onSkipRag?: () => void;
  onContinuePartial?: () => void;
};
```

### 8.3 시각

```
모바일:
┌────────────────────────────────┐
│ ●──○──○──○                     │
│ Intent  RAG  Plan  Critic     │
│   ✓     ⟳    -     -          │
│                                │
│ "AI가 참고 자료를 찾고 있어요"   │  ← AgentStatusIndicator (aria-live)
│                                │
│ ESTIMATED 30s left            │
└────────────────────────────────┘

데스크톱: 가로 4단계, partial result side panel.
```

### 8.4 상태 색상

| status | 시각 | 색상 |
|---|---|---|
| pending | 빈 원 `○` | neutral-300 |
| active | 회전 원 `⟳` | primary-500 |
| completed | 체크 `✓` | success-500 |
| failed | X `✗` | error-500 |
| skipped | 빗금 `/` | neutral-400 |
| partial | 반쪽 `◐` | warning-500 |

### 8.5 partial_result 노출

`error_response_contract.md` §7과 정합:

```
stage='planner' AND status='partial':
  partial_result.data.plans.length === 1 or 2
  →  UI: 완성된 1~2개 plan card 즉시 노출 + "추가 생성 중" 카드 placeholder
  →  버튼: "이대로 진행" (continue_partial) + "다시 생성" (retry)

stage='rag' AND status='failed':
  →  UI: "참고 자료를 못 가져왔어요" 카드
  →  버튼: "참고 자료 없이 진행" (skip_rag) + "다시 시도" (retry)
```

### 8.6 취소 정책

`onCancel`은 항상 노출 (design.md §22 정합). 취소 시:
- 진행 중인 LLM 호출 abort
- 부분 결과는 보존 (status='generating_cancelled')
- 사용자에게 "부분 결과는 저장됐어요" 토스트

---

## 9. 광고 단어 → UI inline warning

`output_schema.md` §14 정합.

### 9.1 사용자 입력 시 검사

다음 입력 컴포넌트에 inline 검사 적용:
- `IdeaInputBox`
- `QuickPromptInput`
- `RevisionReasonInput`
- `DirectInputFallback`

검사 시점:
- 입력 변화 후 500ms debounce
- 입력 blur 시
- 제출 직전 (마지막 검증)

### 9.2 UI 표시

```
1차 차단 단어 발견 (output_schema §14.1):
┌──────────────────────────────────┐
│ "최고의" 같은 광고적 표현은       │
│ 결과 품질이 떨어질 수 있어요.     │
│ 다른 표현을 추천해드릴까요?       │
│  [추천 받기]  [그래도 사용]      │
└──────────────────────────────────┘
색상: warning-50 배경 + warning-700 텍스트
아이콘: ⚠
```

```
2차 경고 단어 발견:
( inline hint, 위 카드 없음 )
  • "특별한" 같은 표현이 들어있어요. 충분한 맥락이 있다면 괜찮아요.
색상: neutral-600 텍스트만
```

### 9.3 차단 vs 안내

**1차 차단 단어:** 제출 자체는 막지 않음. 안내 후 사용자 선택.
- "추천 받기" → 사전 기반 대체어 제시
- "그래도 사용" → 제출은 되지만 metadata.has_ad_violation 기록

**2차 경고 단어:** 안내만. 사용자 액션 강제 없음.

### 9.4 응답에서 발견 시

LLM 응답에 광고 단어 발견 (자동 재생성 후에도 실패):
- 카드 단위로 표시
- "AI 응답에 광고적 표현이 포함됐어요. 다시 시도해주세요."
- user_action: `retry` 단독

---

## 10. 상태 (State) 표준

design.md §20 정합.

### 10.1 필수 상태

모든 화면이 다음 상태를 명시적으로 처리:

| 상태 | 컴포넌트 표시 |
|---|---|
| Empty | `EmptyState` 컴포넌트 (illustration + CTA) |
| Loading | Skeleton (실제 컴포넌트 모양) 또는 spinner |
| Streaming | partial_result 노출 + 다음 단계 placeholder |
| Partial Result | 완성된 부분만 노출 + "추가 생성 중" 안내 |
| Error | `ErrorCard` (§7.1) |
| Retry | 카운트다운 + retry 버튼 |
| Save Success | 토스트 또는 inline success badge |
| Memory Updated | "이 Brand 톤이 자동 반영됐어요" 토스트 |

### 10.2 Skeleton 패턴

```
ChoiceCardGrid 로딩 시:
- 4개 ChoiceOptionCard 모양의 skeleton (실제 카드 비율)
- shimmer 효과 (prefers-reduced-motion 시 정적 색상만)
- 사용자 입력에서 trigger 후 ≤300ms 안에 skeleton 노출
```

### 10.3 Toast 사용 제한

토스트는 일시적/부가 정보에만:
- "저장됐어요"
- "Brand 톤이 반영됐어요"
- "취소했어요"

다음은 토스트 금지 (카드/inline 사용):
- 에러 (ErrorCard 사용)
- LLM 진행률 (GenerationProgressStepper 사용)
- 사용자 액션이 필요한 안내 (모달 또는 카드 사용)

토스트 위치: 데스크톱 우상단, 모바일 하단 BottomActionBar 위. 자동 dismiss 4s.

---

## 11. 컴포넌트 → output_schema 매핑

| 컴포넌트 | output_schema 참조 | 데이터 구조 |
|---|---|---|
| `ChoiceOptionCard` (Brand) | §3 P-001 | card.name / description / fit_situation / pros / cautions |
| `ChoiceOptionCard` (Domain) | §4 P-002 | 동일 |
| `ChoiceOptionCard` (Series) | §5 P-003 | + structure_type / cadence_hint |
| `ChoiceOptionCard` (Target) | §6 P-004 target_card | + pain_points / watch_motivation |
| `ChoiceOptionCard` (Tone) | §6 P-004 tone_card | + example_sentences / avoid_examples |
| `DirectionSummaryCard` | §7 P-005 | one_line + components |
| `PlanOptionCard` | §8 P-006 | plan_id / name / concept / hook / flow / pros / risks / approach_label |
| `HookCandidateCard` | §17 final_outputs.hook_candidates | hook / rationale / risk |
| `VideoStructureTimeline` | §17 final_outputs.video_structure | section / time_range / content / visual_note |
| `ShootingNoteCard` | §17 final_outputs.shooting_notes | type / note |
| `QualityScorePanel` | §9 P-007 | 8 차원 점수 + reasons + suggestions + overall_verdict |
| `RevisionSuggestionCard` | §10 P-008 + §17 revision_suggestions | changes_made / priority / suggestion |
| `RAGReferencePanel` | §8.3 rag_used[] / §17 rag_references | source_id / title / used_reason |
| `IntentWarningBox` | §11 P-AUX-1 | decision / reason / reframe_suggestion |
| `BrandMemoryPanel` | §12 P-AUX-2 + db_schema §6 | entries grouped by entry_type |

---

## 12. 디자인 리뷰 체크리스트

`design-review` Skill 트리거 시 사용. design.md §24의 18개 항목 + 본 contract 추가 항목.

### 12.1 콘텐츠 / UX

- [ ] 신규 사용자가 첫 화면에서 무엇을 해야 하는지 1초 안에 보이는가?
- [ ] Discovery 단계가 6단계 이하인가?
- [ ] 단계당 카드가 정확히 5장(또는 의미 있는 4장 미만)인가?
- [ ] 각 카드에 이름 / 설명 / 적합 상황 / 장점 / 주의점이 있는가?
- [ ] Brand → Domain → Series → Video 컨텍스트가 상속되는가?
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

### 12.2 토큰 / 디자인 시스템

- [ ] 모든 색상이 토큰 (--color-*)을 거치는가? 하드코딩 #hex 금지.
- [ ] 모든 spacing이 토큰 단위 (--space-*)인가? 임의 px 금지.
- [ ] typography가 type scale (--font-*)을 따르는가?
- [ ] radius / shadow / motion 모두 토큰 사용?
- [ ] dark mode 대응 (background / surface / text 페어 정의)?
- [ ] critic 점수 색상이 critic-good / medium / bad 토큰 사용?

### 12.3 접근성

- [ ] 모든 인터랙티브 요소가 키보드 단독 조작 가능한가?
- [ ] focus-visible 표시가 있는가?
- [ ] 카드 wizard가 aria-current="step"인가?
- [ ] AgentStatusIndicator가 aria-live="polite"인가?
- [ ] 에러가 role="alert"인가?
- [ ] 색상 대비 4.5:1 / 3:1 충족?
- [ ] 색상만으로 상태 구분하지 않는가?
- [ ] 터치 타겟 44×44px 이상?
- [ ] prefers-reduced-motion 존중?
- [ ] 200% 확대 시 horizontal scroll 없이 접근 가능?
- [ ] 폼 input에 명시적 label?

### 12.4 PWA / 성능

- [ ] manifest.json 모든 필수 필드?
- [ ] service worker 등록?
- [ ] offline fallback 라우트 캐시?
- [ ] safe-area-inset 적용?
- [ ] LCP < 2.5s (3G 시뮬레이션)?
- [ ] FID < 100ms?
- [ ] CLS < 0.1?

### 12.5 에러 / 부분 결과

- [ ] 모든 에러가 ErrorCard 형식?
- [ ] user_action이 §7 매핑표대로 표시?
- [ ] 동시 액션 최대 2개?
- [ ] retry_after 카운트다운 동작?
- [ ] partial_result가 보존되는가?

---

## 13. dark mode (Phase 2+)

Phase 2+에서 활성화. Phase 1은 light 단일.

### 13.1 토큰 페어

```
@media (prefers-color-scheme: dark) {
  :root {
    --color-neutral-0:   #0A0A0A
    --color-neutral-50:  #171717
    --color-neutral-100: #1F1F1F
    --color-neutral-200: #2A2A2A
    --color-neutral-900: #FAFAFA
    /* ... */
  }
}
```

또는 `[data-theme="dark"]` 클래스 기반 (사용자 명시 선택). 둘 다 지원 검토.

### 13.2 shadow는 dark에서 더 미묘

dark mode에서는 shadow 대신 border가 카드 구분에 더 효과적. shadow opacity 감소.

---

## 14. 국제화 (i18n) (Phase 2+)

Phase 1은 ko-KR 단일. 단 구조는 i18n 가능하도록.

### 14.1 텍스트 분리 원칙

- 컴포넌트 안에 한국어 문자열 하드코딩 금지
- `t('user.message.welcome')` 같은 키 기반
- 메시지 파일: `apps/web/locales/ko-KR/*.json`

### 14.2 출력 vs UI 텍스트

- AI 응답 본문(`one_line`, `card.description` 등)은 LLM이 생성한 텍스트 그대로 렌더링 (i18n 우회)
- UI chrome (버튼 라벨, 메뉴, 에러 카드 제목)만 i18n 대상

---

## 15. 확장 가능성 (Phase 2+)

```
- dark mode 토큰 완전 정의
- 다국어 (en-US, ja-JP)
- 사용자 커스텀 accent color (Brand 단위)
- Storybook 도입 (모든 컴포넌트 docs)
- design token을 Style Dictionary로 export (React Native 공유 - Phase 21+)
- 영상 미리보기 / thumbnail 컴포넌트
- 팀 협업 UI (presence, real-time cursor)
- 키보드 단축키 (Cmd+K palette)
- 음성 입력 (mobile)
```

---

## 16. Cross-reference 빠른 표

| 항목 | 의존 contract / 문서 |
|---|---|
| 페이지 구조 | apps/web/design.md §7, §8 / page_map.md |
| 컴포넌트 목록 | apps/web/component_map.md |
| 에러 표시 | error_response_contract.md §3, §6 |
| 진행률 stepper | api_contract.md §13 / error_response_contract.md §7 |
| LLM 출력 매핑 | output_schema.md §3~§12, §17 |
| 광고 단어 차단 | output_schema.md §14 |
| 4계층 데이터 | db_schema.md §3 |
| accent / brand 톤 | design.md §18, §26 (Open Q 1) |

---

## 17. Open Questions

1. accent 색상 — 현재 indigo (#6366F1). 드림메이트 브랜드 컬러 vs 일반 SaaS 톤 선택 (design.md §26 §1).
2. 모바일 카드 그리드를 세로 스와이프 vs 세로 스택 — 사용자 테스트 후 결정.
3. dark mode 활성 시점 — Phase 2 초반 vs 사용자 누적 후.
4. Storybook 도입 시점 — 컴포넌트 수 ≥ 30개 (현재 30+개로 도입 검토).
5. critic 8차원 중 사용자 노출 차원 — 전부 vs 핵심 4개 (design.md §26 §4).
6. PWA install prompt 노출 정책 — 첫 영상 성공 후 vs 3회 방문 후.
7. 한국어 폰트 — Pretendard 정적 vs Variable, 용량 vs 디자인 자유도.

---

## 18. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-2 초안. 디자인 토큰 (color/spacing/typography/radius/shadow/motion),
                      반응형 breakpoints, 컴포넌트 명명 규칙, WCAG 2.1 AA 접근성,
                      PWA 표준, user_action → UI 매핑, 4단계 stepper 매핑,
                      광고 단어 inline warning, 디자인 리뷰 체크리스트.
```
