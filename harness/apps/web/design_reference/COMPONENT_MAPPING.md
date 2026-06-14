# Component Mapping

## 1. `app/globals.css`

변경:

- semantic color variables
- font variables
- body background
- selection color
- warm neutral form defaults

유지:

- safe-area
- reduced-motion
- legacy aliases

주의:

기존 컴포넌트가 `primary-600`, `neutral-900` 같은 scale class를 직접 사용한다.
semantic 변수만 바꾸면 일부 UI가 보라색·회색으로 남을 수 있다.

따라서 다음 중 하나를 계획적으로 선택한다.

1. legacy Tailwind scale을 새 팔레트로 맞춘다.
2. 해당 컴포넌트를 semantic class로 점진 이행한다.

무작위 혼용 금지.

---

## 2. `tailwind.config.ts`

검토 대상:

- primary scale
- neutral scale
- semantic aliases
- font family
- shadow
- radius

새 라이브러리를 추가하지 않는다.

---

## 3. `components/AppShell.tsx`

목표:

- 모바일: 기존 하단 탭 유지
- 데스크톱: Primary Rail + Secondary Sidebar
- route별 secondary nav 제공

보존:

- `HIDDEN_PREFIXES = ["/login", "/new", "/plan"]`
- focus-visible
- aria-current
- safe-area

권장:

```text
AppShell
├── DesktopPrimaryRail
├── DesktopContextSidebar
└── MobileBottomNav
```

---

## 4. `app/page.tsx`

기존 기능:

- `startPlan`
- 이미지 첨부 최대 4장
- 입력 길이
- 4개 상황 진입
- ErrorCard
- ProgressStepper

디자인 변경:

- Hero
- prompt panel
- warm paper start cards
- orange primary CTA

기능 코드는 분리하거나 유지한다.

---

## 5. Discovery 컴포넌트

권장 컴포넌트:

```text
DiscoveryShell
├── DiscoveryHeader
├── ChoiceGrid
├── ChoiceCard
├── CurrentDirectionPanel
└── BottomActionBar
```

카드 선택은:

- `role=radiogroup`
- 선택 카드 `aria-checked`
- 키보드 탐색
- 색상 외 check 표시

---

## 6. `/plan/[plan_id]`

권장 구조:

```text
PlanResultPageContent
├── GenerationState
├── BrainReflectedBanner
├── PlanComparisonGrid
│   └── PlanOptionFrame
│       └── PlanCard
├── PlanFeedbackControls
└── BrandMemoryAside
```

`PlanCard` 내부를 강제로 재작성하지 않는다.

---

## 7. `ProgressStepper`

- 실제 단계 유지
- 주황 progress
- 완료·진행·대기 라벨
- 색상만으로 상태 구분 금지

---

## 8. `ErrorCard`

- error semantic color는 브랜드 주황과 구분
- 오류는 적갈색
- warning은 앰버
- primary CTA와 error CTA가 혼동되지 않게 한다

---

## 9. `SubmitButton`

- 주황 gradient
- loading
- disabled
- focus-visible
- 44px 이상

---

## 10. `Brain`

- 실제 데이터 구조 유지
- 카드와 그래프 색만 변경
- force graph의 노드 대비 확인
- orange는 selected node
- neutral은 일반 node
