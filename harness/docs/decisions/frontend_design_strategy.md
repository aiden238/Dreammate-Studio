# frontend_design_strategy.md — 프론트엔드 디자인 전략 (ADR)

> 위치: `docs/decisions/frontend_design_strategy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/tech_stack_contract.md` §2.1, `docs/contracts/frontend_design_contract.md`
> 참조: `apps/web/design.md`, `apps/web/page_map.md`, `apps/web/component_map.md`

---

## 0. 결정 요약

```
스타일링: Tailwind CSS 3.x (utility-first)
컴포넌트: shadcn/ui (Radix UI 기반)
폼:       React Hook Form + zod
상태:
- 서버 상태: SWR 또는 TanStack Query (Phase 1 시점 선택)
- 클라이언트 상태: useState + Context
- 전역 상태: 도입 보류 (Phase 5+ Zustand/Jotai 검토)

디자인 우선순위: 모바일 우선 → PWA → 데스크탑
```

---

## 1. Tailwind + shadcn/ui 선택 이유

### 1.1 Tailwind CSS

```
1. 유틸리티 우선 (utility-first)
   - 작은 컴포넌트 빠르게 (1인 운영 친화)
   - 디자인 토큰을 클래스로 표현 (color / spacing / typography)

2. PostCSS / JIT 빠름
   - dev / build 모두 빠름
   - 사용 안 된 CSS 자동 제거

3. 디자인 토큰 친화
   - tailwind.config.js 에서 토큰 중앙 관리
   - frontend_design_contract.md의 토큰 정책과 일치

4. Next.js 14 친화
   - 공식 가이드 + 마지막 버전 호환

대안 (Styled-Components / Emotion):
- CSS-in-JS는 RSC와 호환성 이슈 (Next.js 14)
- 빌드 성능 떨어짐

대안 (vanilla CSS):
- 컴포넌트 추상화 어려움
- 디자인 토큰 표현 비효율
```

### 1.2 shadcn/ui (Radix UI 기반)

```
1. 라이브러리가 아니라 코드 copy 방식
   - node_modules 부담 없음
   - 컴포넌트 자체를 프로젝트 안에 둠 (커스터마이즈 자유)

2. Radix UI 기반 (접근성)
   - WAI-ARIA 표준 준수
   - 키보드 / 스크린 리더 친화

3. Tailwind 친화
   - 모든 컴포넌트가 Tailwind 클래스로 스타일링
   - 디자인 토큰 즉시 적용

4. 한국 시장 친화
   - shadcn/ui Discord 한국 커뮤니티 활발
   - 학습 자료 풍부

대안 (MUI / Chakra UI):
- node_modules 부담 큼
- 커스터마이즈 어려움 (theme override)
- Tailwind와 충돌

대안 (자체 구축):
- 1인 운영 시 시간 부담 큼
- 접근성 표준 직접 구현 어려움
```

---

## 2. 디자인 토큰 정책

### 2.1 토큰 중앙 관리

```
tailwind.config.js의 theme.extend:

color:
- primary: brand 식별 (영상기획 친근색)
- secondary: 보조 색
- destructive: 에러 / 위험 (광고 단어 차단 등)
- muted: 비활성
- accent: 강조

spacing:
- 4px / 8px / 16px / 24px / 32px / 48px / 64px (8 grid)

typography:
- 한글 우선 (Pretendard / Noto Sans KR)
- 영문: Inter
- 모바일: 14px base (16px 권장이지만 한글은 14가 자연)

border-radius:
- sm / md / lg / xl (모서리 부드러움)

shadow:
- sm / md / lg (카드 단위)
```

→ `docs/contracts/frontend_design_contract.md` §6 정합

### 2.2 토큰 변경 절차

```
1. tailwind.config.js 변경 PR
2. frontend_design_contract.md 동시 갱신
3. design-review Skill 통과
4. 영향 컴포넌트 review (스토리북 시각 회귀)
```

---

## 3. 컴포넌트 재사용 vs 자체 구축 균형

### 3.1 shadcn/ui 사용 (재사용)

```
다음 컴포넌트는 shadcn/ui 직접 copy 사용:
- Button / Input / Select / Card
- Dialog / Drawer / Sheet (모바일 친화)
- Toast / Sonner (notification)
- Form (React Hook Form + zod)
- Tabs / Accordion
- Skeleton (loading)
```

### 3.2 자체 구축 (커스텀)

```
영상기획 도메인 특화 컴포넌트는 자체 구축:
- DiscoveryCard (5장 카드 단위)
- QuickModeInput (한 줄 입력 + 1~2 추가 질문)
- DirectionApprovalCard (한 줄 방향 승인)
- PlanComparisonCard (3 후보 비교)
- GenerationProgressStepper (4단계 progress, design.md §22)
- BrandMemoryEditor (Brand Memory 검토 UI, Phase 9+)
- CriticScoreBadge (Critic 점수 표시)
```

→ `apps/web/component_map.md` (Phase 2+ 작성)

---

## 4. PWA 우선 정책

```
MVP (Phase 1~10):
- next-pwa 사용
- "설치 가능" PWA (오프라인 미지원)
- 모바일 친화 UX 우선

Phase 11+:
- 모바일 PWA UX 강화 (Phase 11)
- 오프라인 제한 지원 검토 (Phase 13+)
- push notification 검토 (Phase 14+)

Phase 21+:
- Expo React Native 네이티브 앱
- PWA는 유지 (양쪽 운영)
```

→ `docs/decisions/mobile_strategy.md` 정합

---

## 5. 모바일 우선 (Mobile-First)

```
디자인 우선순위:
1. 모바일 (375px 기준 = iPhone SE)
2. 태블릿 (768px)
3. 데스크탑 (1024px+)

Tailwind breakpoints:
- sm: 640px (모바일 가로)
- md: 768px (태블릿)
- lg: 1024px (데스크탑)
- xl: 1280px (큰 데스크탑)

이유:
- 페르소나 1 (1인 마케터) 50% 모바일
- 페르소나 3 (크리에이터) 70% 모바일
- 모바일 → 데스크탑 적응이 반대보다 쉬움
```

→ `product/target_users.md` §4 디바이스 분포

---

## 6. 상태 관리 결정

### 6.1 서버 상태 (SWR vs TanStack Query)

```
SWR:
- 가벼움 + 단순
- Vercel 공식 (Next.js 친화)
- stale-while-revalidate 패턴 표준

TanStack Query:
- 더 풍부한 기능 (mutation / optimistic update)
- 학습 곡선 약간 더 높음
- 더 큰 커뮤니티

선택: Phase 1 진입 시 확정 (현재 미결정)
경향: SWR (단순성 우선, 1인 운영)
```

### 6.2 클라이언트 상태 (useState + Context)

```
- Discovery wizard 단계 진행 (Context)
- Quick mode 입력 상태 (useState)
- Critic revise 상태 (Context)
- 전역 상태 (Zustand/Jotai)는 Phase 5+ 검토
```

---

## 7. 접근성 (a11y)

```
표준: WCAG 2.1 AA

체크리스트 (Phase 3 진입 시 design-review):
- 키보드 네비게이션 (Tab / Enter / Esc)
- 색 대비 4.5:1 이상 (Tailwind contrast 확인)
- 스크린 리더 (aria-label / aria-describedby)
- 폼 라벨 명시 (htmlFor)
- 에러 메시지 명시 (aria-live="polite")

도구:
- axe DevTools (브라우저)
- eslint-plugin-jsx-a11y

→ `eval/accessibility_checklist.md` 정합
```

---

## 8. 분석 / 모니터링

```
Phase 1+:
- Vercel Analytics (페이지 뷰)
- Sentry (에러 + performance, Phase 2+)

Phase 5+:
- PostHog 또는 Mixpanel (사용자 이벤트)
- A/B 테스트 인프라 (Phase 14+)
```

---

## 9. 재검토 트리거

```
1. 사용자 모바일 비중 70% 초과 → 모바일 우선 강화
2. shadcn/ui 업그레이드 시 → 영향 컴포넌트 검토
3. Tailwind 4.x 출시 → migration 검토
4. Phase 11+ 모바일 UX 강화 → 디자인 토큰 재검토
5. Phase 21+ Expo 진입 → React Native 컴포넌트 분리
```

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      Tailwind + shadcn/ui 선택 이유, 디자인 토큰, 재사용 vs 자체 구축,
                      PWA 우선, 모바일 우선, 상태 관리, 접근성, 재검토 트리거.
```
