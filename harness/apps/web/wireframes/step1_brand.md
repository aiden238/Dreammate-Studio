# Wireframe — Discovery Step 1 (Brand Direction Cards)

> 위치: `apps/web/wireframes/step1_brand.md`
> 상태: Phase 2 Slice 2 baseline (2026-05-27)
> 대상: mobile 360px first. 가로 스크롤 없음. 1열 5행 + 세로 스크롤.
> 참조: `apps/web/discovery_flow.md` §1, `apps/web/component_map.md` (BrandDirectionCard / CardGrid5), `apps/web/design_system/tokens.md`
>
> 원칙: ASCII art는 시각 인지용. 실 구현은 컴포넌트의 4-layer Visual / Layout layer + tokens.md를 단일 진실 소스로 사용.

---

## 현재 chosen variant: `current` (Stacked vertical 5-card)

```
┌──────────────────────────────────┐  ← viewport 360px width
│ ← back        1 / 7         menu │  ← WizardStepHeader (height = space.12)
├──────────────────────────────────┤
│                                  │
│   브랜드 방향을 선택하세요         │  ← H1 (font.size_3xl, font.weight_bold)
│   AI가 추천한 4가지 + 직접 입력    │  ← subtitle (font.size_sm, text_muted)
│                                  │
├──────────────────────────────────┤
│                                  │  ← CardGrid5 시작 (role="radiogroup")
│ ┌────────────────────────────┐   │
│ │ [icon] 성장 기록형          │   │  ← BrandDirectionCard #1 (ai_suggestion)
│ │ 대학생이 시행착오 겪으며     │   │     name (size_lg, semibold)
│ │ 배우는 모습 보여주는 방향    │   │     description (size_base, 2 lines)
│ │ ─────────────────────────  │   │
│ │ Fit  창업동아리 / 프로젝트   │   │     fit_situation (size_sm, muted)
│ │ Pros 진정성·공감대          │   │     pros (size_sm, muted)
│ │ ⚠ Cautions 일기처럼 보임     │   │     cautions (size_sm, muted)
│ │ ●●●●○ confidence 0.78       │   │     confidence visual
│ └────────────────────────────┘   │
│                                  │  ← gap: space.3 (12px)
│ ┌────────────────────────────┐   │
│ │ [icon] 브랜드 B             │   │  ← BrandDirectionCard #2 (ai_suggestion)
│ │ ...                          │   │
│ └────────────────────────────┘   │
│                                  │
│ ┌────────────────────────────┐   │
│ │ [icon] 브랜드 C             │   │  ← BrandDirectionCard #3 (ai_suggestion)
│ │ ...                          │   │
│ └────────────────────────────┘   │
│                                  │
│ ┌────────────────────────────┐   │
│ │ [icon] 브랜드 D             │   │  ← BrandDirectionCard #4 (ai_suggestion)
│ │ ...                          │   │
│ └────────────────────────────┘   │
│                                  │
│ ┌────────────────────────────┐   │
│ │ ✎ 직접 입력                  │   │  ← BrandDirectionCard #5 (user_direct_input)
│ │ ┌────────────────────────┐  │   │     name (size_lg, semibold)
│ │ │ [textarea]               │  │   │     textarea (rows=3, min-height=72px)
│ │ │ "직접 브랜드 방향을 입력 │  │   │     placeholder (text_placeholder)
│ │ │  해주세요..."             │  │   │
│ │ └────────────────────────┘  │   │
│ └────────────────────────────┘   │
│                                  │  ← bottom padding: space.4
├──────────────────────────────────┤
│ [        다음 단계로 ▶         ]  │  ← SubmitButton (sticky bottom, primary)
│   1개 카드를 선택해주세요          │     선택 전: disabled + 안내 (text_muted)
└──────────────────────────────────┘
```

### Selected 상태 (카드 선택 시)

```
┌────────────────────────────┐
│ [✓] [icon] 성장 기록형      │  ← border 2px primary, ✓ icon (text_inverse on primary)
│ ... (동일 컨텐츠)            │     bg: bg_subtle
│                            │
└────────────────────────────┘
```

### Focus 상태 (키보드 탐색)

```
╔════════════════════════════╗
║ [icon] 브랜드 B             ║  ← outline 2px border_focus + outline-offset 2px
║ ...                          ║
╚════════════════════════════╝
```

---

## 측정값 (tokens.md 참조 — literal 값 X)

| 항목 | 값 | tokens.md 참조 |
|---|---|---|
| viewport width | 360px | `bp.mobile` |
| header height | 48px | `space.12` |
| page padding (좌/우) | 16px | `space.4` |
| card width | `100% - 2 * space.4` = 328px | 계산값 |
| card padding | 16px | `space.4` |
| card 내부 항목 gap | 12px | `space.3` |
| card 간 gap | 12px | `space.3` |
| card border-radius | 12px | `radius.lg` |
| card border (default) | 1px solid border_default | tokens §1.6 |
| card border (selected) | 2px solid primary | tokens §1.2 |
| card border (focus) | 2px solid border_focus + 2px offset | tokens §1.6 |
| H1 font | size_3xl (24px) / weight_bold | tokens §2.2~§2.3 |
| name font | size_lg (17px) / weight_semibold | tokens §2.2~§2.3 |
| description font | size_base (15px) / weight_regular | tokens §2.2 |
| sub fields font | size_sm (14px) / text_muted | tokens §2.2, §1.5 |
| confidence color (filled) | primary | tokens §1.2 |
| confidence color (empty) | border_default | tokens §1.6 |
| bottom button height | ≥56px | `frontend_design_contract.md` §3.3 (터치 타겟) |
| bottom button bg | primary | tokens §1.2 |
| bottom button text | text_inverse | tokens §1.5 |

---

## 대안 variants (`variant_format.md` §3 + `component_map.md` BrandDirectionCard variants 참조)

### alt_horizontal_swipe (chosen=false)

```
┌──────────────────────────────────┐
│ ← back        1 / 7         menu │
├──────────────────────────────────┤
│ 브랜드 방향을 선택하세요          │
├──────────────────────────────────┤
│ ◀ [Card A      ] [Card B ⋯]  ▶  │  ← 가로 스와이프, 1.5장 peek
│   ●●●○○                         │  ← page indicator
├──────────────────────────────────┤
│ [        다음 단계로 ▶         ]  │
└──────────────────────────────────┘
```

→ trade-off: exploration 강조 / user_input 슬롯 발견 어려움 (5번째 위치 스와이프 비용)

### alt_grid_2x3 (chosen=false)

```
┌──────────────────────────────────┐
│ [Card A] [Card B]                │  ← 2 col × 3 row 그리드
│ [Card C] [Card D]                │  ← 360px에선 무리 (text overflow 위험)
│ [Card E] [    ──    ]            │
└──────────────────────────────────┘
```

→ trade-off: 전체 조망 / 360px 무리 (desktop_lg 활성화 시 검토)

→ 두 alt variants는 component_map.md의 BrandDirectionCard `variants` yaml에 등재. chosen 변경 시 본 wireframe 갱신.

---

## 변경 시

- `tokens.md` 색/spacing 변경 → wireframe 측정값 자동 반영 (literal 값 사용 안 함)
- BrandDirectionCard variants chosen 변경 → 본 wireframe 또는 새 wireframe 작성 (`replaceability_score.md` §3.2 M비용)
- CardGrid5 variants chosen 변경 → 모든 Step wireframe 영향 (M~H 비용)

---

## 변경 이력

- 2026-05-27: Phase 2 Slice 2 — 최초 작성 (current variant + alt 2개 placeholder)
