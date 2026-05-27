# Design Tokens

> 위치: `apps/web/design_system/tokens.md`
> 상태: Phase 2 Slice 1 baseline (2026-05-27)
> 원칙: **단일 진실 소스. 변경 시 모든 spec 참조가 자동 일관.**
> 참조: `apps/web/design.md` §18 (Visual Style Guide), `docs/contracts/frontend_design_contract.md` §2 (디자인 토큰)

---

## 0. 이 문서의 위치

- **무엇이다**: 색 / 폰트 / spacing / radius / breakpoint / motion 6 카테고리의 **참조 가능한 골격**
- **무엇이 아니다**: Tailwind config 실 파일 / CSS variable 실 정의 (Phase 3 진입 시 실 코드로 변환)
- **변경 정책**: 본 문서 1곳만 수정 → 후속 spec (component_contract / wireframes / page_map 등) 자동 일관
- **상위 contract**: `docs/contracts/frontend_design_contract.md` §2 (Phase 0 작성, 광범위) — tokens.md는 그 중 Phase 2 Slice 1에서 채택한 **subset baseline**

---

## 1. Color (semantic, not literal)

### 1.1 원칙

- **semantic 토큰 사용** (예: `primary_hover`, `text_default`) — 리터럴 hex 직접 참조 금지
- light mode 우선, dark mode는 자리만 (Phase 11+ 본격)
- 강조색은 1개 (primary)만 사용. UI 전반 chromatic 금지

### 1.2 Primary (CTA, 선택, 활성)

| 토큰 | light | dark (자리, Phase 11+) | 용도 |
|---|---|---|---|
| `color.primary` | `#6366F1` | TBD | 기본 CTA, 카드 선택 상태, 진행률 |
| `color.primary_hover` | `#4F46E5` | TBD | hover 상태 |
| `color.primary_pressed` | `#4338CA` | TBD | pressed/active 상태 |
| `color.primary_disabled` | `#A5B4FC` | TBD | disabled 상태 (50% opacity 대안 허용) |

### 1.3 Accent (보조 강조)

| 토큰 | light | dark | 용도 |
|---|---|---|---|
| `color.accent` | `#06B6D4` | TBD | 정보성 배지 ("AI 생성", "참고 자료 사용") |

### 1.4 Background / Surface

| 토큰 | light | dark | 용도 |
|---|---|---|---|
| `color.bg_default` | `#FAFAFA` | `#0A0A0A` | 페이지 배경 |
| `color.bg_subtle` | `#F5F5F5` | `#171717` | 보조 배경 (카드 선택 시 등) |
| `color.bg_overlay` | `rgba(0,0,0,0.5)` | `rgba(0,0,0,0.7)` | 모달/drawer backdrop |
| `color.surface` | `#FFFFFF` | `#171717` | 카드 본체 |

### 1.5 Text

| 토큰 | light | dark | 용도 |
|---|---|---|---|
| `color.text_default` | `#171717` | `#FAFAFA` | 본문 주 텍스트 |
| `color.text_muted` | `#525252` | `#A3A3A3` | 보조 텍스트, 캡션 |
| `color.text_placeholder` | `#A3A3A3` | `#737373` | input placeholder |
| `color.text_inverse` | `#FFFFFF` | `#171717` | CTA 위 텍스트 (primary 배경 대비) |
| `color.text_danger` | `#B91C1C` | `#F87171` | 에러 텍스트 |
| `color.text_success` | `#15803D` | `#4ADE80` | 성공 텍스트 |

### 1.6 Border

| 토큰 | light | dark | 용도 |
|---|---|---|---|
| `color.border_default` | `#E5E5E5` | `#2A2A2A` | 카드 / input 기본 테두리 |
| `color.border_subtle` | `#F5F5F5` | `#1F1F1F` | 보조 구분선 |
| `color.border_focus` | `#6366F1` | `#818CF8` | 키보드 포커스 outline |

### 1.7 State (semantic)

| 토큰 | light | dark | 용도 |
|---|---|---|---|
| `color.state_success` | `#22C55E` | `#4ADE80` | Critic 좋은 점수, 저장 성공 |
| `color.state_warning` | `#F59E0B` | `#FCD34D` | Intent warning, 광고 단어 안내 |
| `color.state_error` | `#EF4444` | `#F87171` | LLM 실패, 검증 실패 |
| `color.state_info` | `#3B82F6` | `#60A5FA` | RAG 참고 자료 표시 |

### 1.8 Critic 점수 (8차원 색상)

```
color.critic_good   = color.state_success   (점수 4~5)
color.critic_medium = color.state_warning   (점수 2~3)
color.critic_bad    = color.state_error     (점수 0~1)
```

`docs/contracts/frontend_design_contract.md` §2.1 정합. **색상만으로 상태 구분 금지** — 점수 숫자 + 아이콘 + 라벨 동반 (`apps/web/design.md` §19, `accessibility_score`).

---

## 2. Typography

### 2.1 Font Family

| 토큰 | 값 | 용도 |
|---|---|---|
| `font.family_sans` | `"Pretendard Variable", "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif` | 본문 / UI 전반 |
| `font.family_mono` | `"JetBrains Mono", "Menlo", "Consolas", monospace` | 코드 / request_id |

design.md §18: 시스템 폰트 우선, Pretendard 권장.

### 2.2 Font Size Scale (mobile-first)

| 토큰 | 값 (mobile) | 값 (desktop, clamp 상한) | 용도 |
|---|---|---|---|
| `font.size_xs` | 12px | 13px | caption, meta, badge |
| `font.size_sm` | 14px | 14px | 보조 텍스트 |
| `font.size_base` | 15px | 16px | 본문 모바일 (design.md §18) |
| `font.size_lg` | 17px | 19px | 카드 제목 (h3) |
| `font.size_xl` | 18px | 22px | 한 줄 방향 (design.md §18) |
| `font.size_2xl` | 20px | 22px | 섹션 제목 (h2) |
| `font.size_3xl` | 24px | 28px | 페이지 제목 (h1) |

권장 clamp: `font-size: clamp(15px, 1.6vw + 12px, 16px)` (`frontend_design_contract.md` §2.3 정합).

### 2.3 Font Weight

| 토큰 | 값 | 용도 |
|---|---|---|
| `font.weight_regular` | 400 | 본문 |
| `font.weight_medium` | 500 | 강조 본문 |
| `font.weight_semibold` | 600 | 카드 제목, h3/h4 |
| `font.weight_bold` | 700 | h1/h2, display |

### 2.4 Line Height

| 토큰 | 값 | 용도 |
|---|---|---|
| `font.lh_tight` | 1.2 | display, h1 |
| `font.lh_normal` | 1.4 | h2/h3, caption |
| `font.lh_relaxed` | 1.5 | 본문 |

### 2.5 Letter Spacing (선택)

| 토큰 | 값 | 용도 |
|---|---|---|
| `font.tracking_tight` | -0.01em | display, large heading |
| `font.tracking_normal` | 0 | 본문 (기본) |
| `font.tracking_wide` | 0.05em | uppercase badge / label |

→ Phase 2 Slice 1 기준 normal만 적용. tight/wide는 Phase 3 진입 시 사용처별 결정.

---

## 3. Spacing (4px base)

### 3.1 Scale

| 토큰 | 값 | 용도 |
|---|---|---|
| `space.0` | 0 | — |
| `space.1` | 4px | 카드 내부 inline gap (icon ↔ text) |
| `space.2` | 8px | 작은 gap |
| `space.3` | 12px | 카드 내부 항목 간 |
| `space.4` | 16px | **모바일 padding 기본값** / 카드 간 gap |
| `space.5` | 20px | 보조 spacing |
| `space.6` | 24px | 데스크톱 카드 padding |
| `space.8` | 32px | 섹션 간 margin |
| `space.10` | 40px | 큰 섹션 간 |
| `space.12` | 48px | 페이지 padding-top/bottom |
| `space.16` | 64px | 큰 hero / landing |

### 3.2 모바일 기본값

- 카드 padding: `space.4` (16px)
- 카드 간 gap: `space.4` (16px) — design.md §17 (≥16px)
- BottomActionBar 높이: 56px 이상 — 하단 CTA 최소 터치 타겟

`frontend_design_contract.md` §2.2 정합.

---

## 4. Radius

| 토큰 | 값 | 용도 |
|---|---|---|
| `radius.none` | 0 | flat 요소 |
| `radius.sm` | 4px | badge, chip |
| `radius.md` | 8px | button, input |
| `radius.lg` | 12px | **카드 기본값** |
| `radius.xl` | 16px | modal |
| `radius.2xl` | 24px | hero / landing 강조 |
| `radius.full` | 9999px | avatar, pill |

기본 카드: `radius.lg`. 모달: `radius.xl`. (`frontend_design_contract.md` §2.4 정합)

---

## 5. Breakpoint

### 5.1 Scale

| 토큰 | 값 | 디바이스 |
|---|---|---|
| `bp.mobile` | 360px | 최소 target (1열) |
| `bp.mobile_md` | 390px | iPhone 14 / 평균 스마트폰 |
| `bp.sm` | 480px | 큰 폰 |
| `bp.tablet` | 768px | 태블릿 (1~2열 분기) |
| `bp.desktop` | 1024px | 데스크톱 (3열 분기 — Nav/Center/Memory) |
| `bp.desktop_lg` | 1440px | wide 데스크톱 |

### 5.2 정책

- **Mobile-first**: 모든 미디어 쿼리는 `min-width` 기반
- **MVP target**: 360px ~ 430px (한 손 조작 가능 — design.md §17)
- **3열 분기 (Nav / Center / Memory)**: ≥ 1024px

`frontend_design_contract.md` §3 정합.

---

## 6. Motion

### 6.1 Duration

| 토큰 | 값 | 용도 |
|---|---|---|
| `motion.instant` | 0ms | state 변경, prefers-reduced-motion 적용 시 |
| `motion.fast` | 150ms | hover, focus, button press |
| `motion.base` | 250ms | 카드 selection, modal open (`apps/web/design_system` 표준) |
| `motion.normal` | 300ms | card flip (확장 시) |
| `motion.slow` | 400ms | partial result reveal, page transition |

### 6.2 Easing

| 토큰 | 값 | 용도 |
|---|---|---|
| `motion.ease_out` | `cubic-bezier(0, 0, 0.2, 1)` | 진입 효과 (요소 등장) |
| `motion.ease_in_out` | `cubic-bezier(0.4, 0, 0.2, 1)` | 양방향 전환 |
| `motion.spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | 카드 snap, selection bounce (선택) |

### 6.3 prefers-reduced-motion 정책

```
@media (prefers-reduced-motion: reduce):
  - 모든 transition / animation duration → motion.instant
  - scroll-behavior → auto
  - 정보 전달 모션(progress stepper 텍스트 변경)은 유지
```

`frontend_design_contract.md` §2.6 / §5.7 정합. **Phase 3 진입 시 글로벌 CSS 1곳에 적용 강제.**

---

## 7. 사용법 (Phase 3 진입 시)

### 7.1 CSS variable로 변환

```css
:root {
  --color-primary: #6366F1;
  --color-bg-default: #FAFAFA;
  --space-4: 16px;
  --radius-lg: 12px;
  --motion-fast: 150ms;
  /* ... */
}
```

### 7.2 Tailwind config alias

```ts
// tailwind.config.ts (Phase 3 작업)
theme: {
  extend: {
    colors: { primary: 'var(--color-primary)' },
    spacing: { 4: 'var(--space-4)' },
    borderRadius: { lg: 'var(--radius-lg)' },
  }
}
```

### 7.3 컴포넌트에서 참조

- **항상 토큰 alias 통해서만 사용** — 리터럴 `#6366F1` / `16px` 등 하드코딩 금지
- 4-layer Visual layer에서 토큰 명시 (`component_contract.md` §Visual 참조)

### 7.4 디자인 swap 시나리오

| 변경 | 영향 파일 수 | 비용 (replaceability) |
|---|---|---|
| primary 색 변경 (#6366F1 → #FF6B6B) | 1 (tokens.md) | L |
| spacing scale 전체 조정 (4px → 6px base) | 1 (tokens.md) | L |
| 폰트 family 변경 (Pretendard → Noto) | 1 (tokens.md) | L |
| typography scale 전체 재설계 | 1 (tokens.md) + 가능한 컴포넌트별 size 재선택 | L~M |
| breakpoint 추가 (mobile_sm: 320px 등) | 1 (tokens.md) + responsive wireframes 검토 | M |

`replaceability_score.md` 정의 참조.

---

## 8. Open Questions (Phase 3 진입 전 확정 권장)

1. accent 색 — 현재 `#06B6D4` (cyan). 드림메이트 브랜드 컬러 vs 일반 SaaS 톤 (design.md §26 §1)
2. 폰트 — Pretendard Variable vs 정적 (용량 vs 디자인 자유도)
3. Critic 점수 색상 mapping (3단계 vs 5단계) — design.md §26 §4
4. dark mode 활성 시점 (Phase 11+ vs 사용자 누적 후)
5. clamp() 사용 여부 — 모바일/데스크톱 type scale 자동 보간 vs 분기 css

---

## 9. 변경 이력

- 2026-05-27: Phase 2 Slice 1 — tokens.md 최초 작성 (6 카테고리 baseline)
