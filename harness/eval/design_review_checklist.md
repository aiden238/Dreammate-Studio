# design_review_checklist.md — 디자인 리뷰 체크리스트

> 위치: `eval/design_review_checklist.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `apps/web/design.md` §24 디자인 리뷰 정책 (예정)
> 참조: `docs/contracts/frontend_design_contract.md` §2 토큰 / §5 a11y
> 참조: `eval/accessibility_checklist.md` (a11y 별도)
> 참조: `eval/ux_eval.md` (UX 별도)
> Skill 연동: `design-review`

---

## 1. 목적

디자인 PR / 디자인 변경 / 새 페이지 도입 시점에 동일한 기준으로 검토한다. 본 체크리스트는 design-review Skill이 자동으로 적용한다. 광고 단어 inline warning, 카드 5장 정책, 4단계 stepper, 토큰 일관성, 반응형, 접근성 7 차원으로 측정한다.

---

## 2. 평가 차원 (7 개)

### 2.1 token_consistency — 디자인 토큰 일관

```
정의: 디자인이 frontend_design_contract §2의 토큰만 사용하는가.
체크:
  - 색상: --color-primary-* / --color-secondary-* / --color-neutral-* / --color-{success|warning|error|info}-*
    rgba(...) 또는 hex literal 사용 금지 (토큰 외)
  - spacing: --space-1 ~ --space-20 만 사용 (4px base)
  - typography: --font-{display|h1|h2|h3|h4|body-lg|body|body-sm|caption|mono}만 사용
  - radius / shadow: 토큰만 사용
0점: 토큰 외 inline 스타일 1개 이상
5점: 100% 토큰 사용
```

### 2.2 component_naming — 컴포넌트 명명

```
정의: shadcn/ui base를 wrap한 컴포넌트 명명이 규칙을 따르는가.
체크:
  - PascalCase
  - prefix: 기능 그룹 (CardGrid / FlowStepper / BrandMemoryBadge 등)
  - props 명명 camelCase
  - shadcn primitives는 그대로 import (Button, Dialog 등)
0점: 규칙 위반 1개 이상
5점: 100% 규칙
참고: apps/web/component_map.md.
```

### 2.3 responsive — 반응형

```
정의: 모바일 우선 + 3 breakpoint (360 / 768 / 1280) 모두 사용 가능.
체크:
  - 360px: 카드 1열, thumb zone CTA
  - 768px: 카드 2열, 보조 정보 노출
  - 1280px: 카드 4열, 사이드 정보 노출
  - 가로 스크롤 발생 금지 (table 등은 overflow-x 명시)
0점: 모바일 미지원
5점: 3 breakpoint 모두 자연스러움
```

### 2.4 accessibility_pass — 접근성 통과

```
정의: eval/accessibility_checklist.md의 7 차원 모두 4 이상.
체크:
  - WCAG 2.1 AA 충족
  - color_contrast 4.5:1 이상 (텍스트)
  - keyboard / screen_reader / focus / motion / alt / aria 모두 통과
0점: 1 차원이라도 < 2
5점: 모두 5
```

### 2.5 ad_phrase_inline_warning — 광고 단어 inline warning

```
정의: 사용자 입력 폼 / 카드 편집 등에서 광고 단어 입력 시 inline warning 노출.
체크:
  - 1차 단어 입력 → 빨간 inline warning + "이 표현은 사용하지 않는 것이 좋습니다" 안내
  - 2차 단어 입력 → 노란 inline warning + "주의: 광고적 표현일 수 있어요"
  - 사용자가 무시하고 진행 가능 (차단 아님, 안내만)
  - 안내 톤은 친근체 (~예요)
0점: warning 없음 또는 영어 메시지
5점: 1차/2차 구분 + 친근체 + 무시 가능
참고: output_schema §14, frontend_design_contract §1.6.
```

### 2.6 stepper_integration — 4단계 stepper 통합

```
정의: 30초 이상 작업이 stepper로 분해되는가.
체크 (apps/web/design.md §22, error_response §7):
  - [1] Intent → [2] RAG → [3] Plan → [4] Critic 노출
  - 단계별 ✓ / ✗ / - 상태 명확
  - 에러 시 partial_result 노출 + user_action 카드
  - 모바일에서도 stepper 가로 스크롤 없이 노출 (compressed view)
0점: stepper 없이 스피너만
5점: 4단계 + 부분 결과 + 에러 처리 완전
```

### 2.7 brand_guideline_compliance — 브랜드 가이드 준수

```
정의: 영상기획 AI 에이전트의 톤·시각 가이드를 따르는가.
체크:
  - primary color 외 chromatic 남용 금지 (design.md §18)
  - 광고적 시각 표현 (큰 화살표 / 별 / 폭죽 등) 금지
  - 영상 제작 UI (편집 타임라인 / 카메라 컨트롤 등) 금지 (MVP 범위 외)
  - 친근체 + 존댓말 일관
0점: 브랜드 정체성 충돌
5점: 가이드 완전 준수
참고: CLAUDE.md "영상 제작 기능을 MVP에 포함시키지 않는다".
```

---

## 3. 입력 / 출력 형식

### 3.1 입력

```yaml
review_target:
  - "page"                       # page_map.md의 페이지
  - "component"                  # component_map.md의 컴포넌트
  - "flow"                       # Discovery / Quick / 에러 회복 흐름
target_path: "apps/web/.../File.tsx"
pr_url: "https://..."
viewports: ["360", "768", "1280"]
reviewer: "user_id (디자이너 또는 운영자)"
```

### 3.2 출력

```yaml
scores:
  token_consistency: 0~5
  component_naming: 0~5
  responsive: 0~5
  accessibility_pass: 0~5
  ad_phrase_inline_warning: 0~5
  stepper_integration: 0~5
  brand_guideline_compliance: 0~5
design_review_avg: 0~5
blockers:                         # passing 임계 미달 항목
  - { dim: "accessibility_pass", reason: "..." }
suggestions:
  - "..."
linked_issues:                    # GitHub issue 링크 (선택)
  - "..."
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| token_consistency | Stylelint + 토큰 사전 매칭 | 운영자 보조 |
| component_naming | ESLint 규칙 | 운영자 보조 |
| responsive | Playwright viewport screenshot | 운영자 1차 |
| accessibility_pass | axe-core + Lighthouse | 운영자 주도 (실 스크린 리더) |
| ad_phrase_inline_warning | 컴포넌트 storybook + 자동 입력 테스트 | 운영자 1차 |
| stepper_integration | 코드 검사 (stepper 컴포넌트 존재 여부) | 운영자 주도 |
| brand_guideline_compliance | (자동 어려움) | 운영자 주도 |

---

## 5. 임계값

```
모든 차원 ≥ 4: passing
1 차원이라도 < 4: warning (PR 본문에 자동 코멘트)
1 차원이라도 < 2: failing (PR 머지 차단)

PR 머지 차단 (특수 게이트):
- accessibility_pass < 4: 즉시 차단
- ad_phrase_inline_warning < 3: 즉시 차단
- brand_guideline_compliance < 3: 즉시 차단 (영상 제작 UI 포함 시 등)
- token_consistency = 0: 즉시 차단
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - frontend_design_contract.md (전체)
  - output_schema.md §14 (광고 단어)
  - error_response_contract.md §7 (4단계 stepper)
  - tech_stack_contract.md (shadcn/ui + Tailwind)

Skill:
  - design-review (PR 시 본 체크리스트 자동 실행)
  - eval-design (체크리스트 갱신)
  - contract-change (frontend_design_contract 변경 시)

연관 골든 셋: GS-005 (revise UX), GS-007 (RAG 사용 표시).
연관 평가:
  - accessibility_checklist.md (a11y 본체)
  - ux_eval.md (UX 본체)
```

---

## 7. Open Questions

1. brand_guideline_compliance의 LLM 자동 채점 — 영상 제작 UI 감지 자동화 가능한가.
2. token_consistency의 false positive — shadcn 내부 토큰과 충돌 시 예외 처리.
3. 광고 단어 inline warning의 디자인 일관성 — error vs warning color 사용.
4. stepper의 모바일 compressed view 디자인 — 가로 스크롤 vs vertical stack.
5. 디자인 PR이 contract 변경을 동반할 때 — contract-change Skill 절차 트리거 정책.
