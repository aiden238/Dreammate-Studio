# accessibility_checklist.md — 접근성 체크리스트 (WCAG 2.1 AA)

> 위치: `eval/accessibility_checklist.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `docs/contracts/frontend_design_contract.md` §5 (a11y)
> 참조: `docs/contracts/accessibility_contract.md` (Phase 7+ 본체)
> 참조: `apps/web/design.md` (접근성 원칙)

---

## 1. 목적

WCAG 2.1 AA 수준의 접근성을 모든 페이지 / 컴포넌트에서 보장한다. 본 체크리스트는 design-review Skill과 디자인 PR 머지 게이트에서 사용된다. AA 미충족 항목은 PR 머지 차단.

---

## 2. 평가 차원 (7 개)

### 2.1 keyboard_navigation — 키보드 탐색

```
정의: 마우스 없이 모든 인터랙션 가능한가.
체크:
  - Tab 키로 모든 인터랙티브 요소 도달
  - 논리적 tab order (DOM 순서 따름)
  - Enter / Space로 버튼 활성화
  - Esc로 모달 닫기
  - 화살표 키로 카드 그리드 이동 (선택)
WCAG 매핑: 2.1.1 (Keyboard), 2.1.2 (No Keyboard Trap)
0점: tab 막힘 또는 일부 요소 도달 불가
5점: 전체 탐색 + 논리적 순서
```

### 2.2 screen_reader — 스크린 리더 호환

```
정의: VoiceOver / NVDA / TalkBack에서 의미 있게 읽히는가.
체크:
  - 모든 img에 alt 텍스트 (장식 이미지는 alt="")
  - form 요소에 label 명시 또는 aria-label
  - 동적 콘텐츠 변경 시 aria-live="polite" 또는 "assertive"
  - 카드 5장에서 5/5 (몇 번째인지) 위치 안내
  - 에러 메시지 즉시 announce (role="alert" 또는 aria-live="assertive")
WCAG 매핑: 1.1.1 (Non-text Content), 4.1.2 (Name, Role, Value)
0점: 의미 없는 div + class만
5점: 시맨틱 HTML + aria 적절 사용
```

### 2.3 color_contrast — 명도 대비

```
정의: 전경 / 배경 대비가 충분한가.
체크 (WCAG 2.1 AA):
  - 일반 텍스트 ≥ 4.5:1
  - 큰 텍스트(18px+ regular 또는 14px+ bold) ≥ 3:1
  - UI 컴포넌트 / 그래픽 ≥ 3:1
  - 비활성 상태도 (대비 면제 가능하나 표시 명확해야 함)
WCAG 매핑: 1.4.3 (Contrast Minimum), 1.4.11 (Non-text Contrast)
0점: 한 곳이라도 4.5:1 미만 (일반 텍스트)
5점: 모든 텍스트 4.5:1 이상 + UI 3:1 이상
검증 도구: Chrome DevTools / axe / WAVE.
```

### 2.4 focus_indicator — 포커스 표시

```
정의: 키보드 포커스가 시각적으로 명확한가.
체크:
  - :focus-visible 스타일 적용 (outline 또는 box-shadow)
  - 포커스 표시 두께 ≥ 2px
  - 포커스 표시 대비 ≥ 3:1
  - 포커스 outline을 절대 outline: none으로 제거 금지 (대체 표시 없이는)
WCAG 매핑: 2.4.7 (Focus Visible), 2.4.11 (Focus Appearance, AAA 권장)
0점: 포커스 표시 없음
5점: 명확한 포커스 표시 + 모든 인터랙티브 요소
```

### 2.5 motion_reduction — 모션 감소

```
정의: prefers-reduced-motion 설정 존중.
체크:
  - @media (prefers-reduced-motion: reduce) 분기
  - 애니메이션 0.2s 이하 또는 비활성
  - 자동 재생 영상 / 슬라이드 비활성
  - 패럴럭스 스크롤 비활성
WCAG 매핑: 2.3.3 (Animation from Interactions, AAA)
0점: 모션 감소 미지원
5점: prefers-reduced-motion 완전 존중
```

### 2.6 alt_text — 대체 텍스트

```
정의: 모든 이미지 / 아이콘에 대체 텍스트.
체크:
  - img에 alt 속성 100%
  - 장식 이미지는 alt="" (스크린 리더가 건너뜀)
  - SVG 아이콘은 role="img" + aria-label (또는 aria-hidden="true")
  - 차트 / 그래프는 longdesc 또는 인접 텍스트
WCAG 매핑: 1.1.1 (Non-text Content)
0점: alt 누락 1개 이상
5점: 모든 이미지 alt 또는 의도된 빈 alt
```

### 2.7 aria_correctness — ARIA 정확성

```
정의: ARIA 속성이 의미 있게 사용되는가.
체크:
  - aria-label / aria-labelledby / aria-describedby 적절
  - role 속성이 native 시맨틱 대체로 남용되지 않음
  - aria-expanded / aria-pressed / aria-selected 상태 동기화
  - aria-hidden은 인터랙티브 요소에 사용 금지
WCAG 매핑: 4.1.2 (Name, Role, Value)
0점: ARIA 오용 (aria-hidden인 버튼 등)
5점: 시맨틱 HTML 우선 + 보조적 ARIA만 정확히
```

---

## 3. 입력 / 출력 형식

### 3.1 입력 (a11y 평가 단위)

```yaml
a11y_target: "page | component | flow"
page_or_component: "string"
test_environment:
  browser: "Chrome | Safari | Firefox"
  screen_reader: "NVDA | VoiceOver | TalkBack | None"
  viewport: "mobile | tablet | desktop"
tools:
  - "axe-core"
  - "lighthouse"
  - "manual_keyboard_test"
  - "manual_screen_reader_test"
```

### 3.2 출력

```yaml
scores:
  keyboard_navigation: 0~5
  screen_reader: 0~5
  color_contrast: 0~5
  focus_indicator: 0~5
  motion_reduction: 0~5
  alt_text: 0~5
  aria_correctness: 0~5
a11y_avg: 0~5
violations:
  - { wcag: "1.4.3", severity: "AA", desc: "...", element: "..." }
suggestions:
  - "..."
tools_used: ["axe-core", "manual"]
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 (axe/Lighthouse) | 수동 (운영자/QA) |
|---|---|---|
| keyboard_navigation | 일부 (tab order 검사) | 주도 (실제 키보드만으로 흐름 완주) |
| screen_reader | 일부 (label/alt 검사) | 주도 (실제 스크린 리더 듣기) |
| color_contrast | 전체 자동 | 보조 |
| focus_indicator | 일부 (outline 검사) | 주도 (시각 확인) |
| motion_reduction | 부분 (media query 검사) | 주도 |
| alt_text | 전체 자동 (alt 존재 여부) | 보조 (alt 텍스트 적절성) |
| aria_correctness | 일부 (axe rule) | 주도 |

자동 검사 통과는 필요조건. AA 충족은 수동 검사 통과까지 필수.

---

## 5. 임계값

```
모든 차원 ≥ 4: passing (WCAG 2.1 AA 충족)
1 차원이라도 < 4: warning + 30일 내 개선 계획
1 차원이라도 < 2: failing (PR 머지 차단)

특수 게이트 (PR 머지 차단):
- color_contrast 4.5:1 미만 1개라도: 즉시 차단
- keyboard_navigation tab trap 발견: 즉시 차단
- alt 누락 1개라도: 즉시 차단
- aria-hidden 인터랙티브 요소: 즉시 차단
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - frontend_design_contract.md §5 (a11y)
  - accessibility_contract.md (Phase 7+ 본체)

Skill:
  - design-review (디자인 PR 시 본 체크리스트 자동 실행)
  - eval-design (차원 갱신 시)
  - security-review (a11y 관련 보안 - 캡차 우회 등)

WCAG 매핑 빠른 표:
  - 1.1.1 → alt_text
  - 1.4.3 / 1.4.11 → color_contrast
  - 2.1.1 / 2.1.2 → keyboard_navigation
  - 2.3.3 → motion_reduction
  - 2.4.7 / 2.4.11 → focus_indicator
  - 4.1.2 → screen_reader, aria_correctness
```

---

## 7. Open Questions

1. AAA 레벨(2.4.11 Focus Appearance) 채택 시점 — Phase 2+ 검토.
2. 다국어 도입 시 lang 속성 / RTL 대응 — Phase 2+ accessibility_contract 확장.
3. 음성 입력 (voice mode) 도입 시 접근성 — Phase 2+ 별도 audit.
4. 사용자가 motion_reduction 직접 설정 가능한 토글 — OS 설정만으로 충분한가.
5. 자동 검사 도구 (axe-core)와 PR CI 통합 시 false positive 처리.
