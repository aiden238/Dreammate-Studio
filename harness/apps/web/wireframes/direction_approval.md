# Wireframe — Direction Approval Pattern

> 위치: `apps/web/wireframes/direction_approval.md`
> 상태: Phase 2 Slice 3 baseline (2026-05-27)
> 대상: mobile 360px first. 양 모드 공통 (Discovery Step 6 + Quick Mode).
> 참조: `apps/web/direction_approval.md`, `apps/web/component_map.md` §DirectionApprovalCard,
>       `apps/web/design_system/tokens.md`
>
> 원칙: ASCII art는 시각 인지용. 실 측정값은 `tokens.md` 단일 진실 소스.

---

## variant: verbose (chosen=true, Discovery Step 6 권장)

```
┌──────────────────────────────────┐  ← viewport 360px width
│ ← back        6 / 7         menu │  ← WizardStepHeader (Discovery)
├──────────────────────────────────┤
│                                  │
│ 기획 방향을 확인해주세요          │  ← H1 (font.size_3xl, weight_bold)
│ AI가 정리한 한 줄 방향            │  ← subtitle (font.size_sm, text_muted)
│                                  │
├──────────────────────────────────┤
│ ┌────────────────────────────┐   │
│ │ "30대 직장인을 위한 짧고     │   │  ← 한 줄 방향 (highlighted)
│ │  유머러스한 재테크 쇼츠"     │   │     bg=tokens.color.bg_subtle
│ │                            │   │     text=tokens.color.text_default
│ │                       ✎    │   │  ← 편집 icon (text_muted → primary on hover)
│ └────────────────────────────┘   │
│                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │  ← 구분선 (border_subtle)
│ 이유 (verbose만):                 │
│ • Step 1 Brand: 정보형 콘텐츠     │     reasons[] (size_sm, text_muted)
│ • Step 2 Domain: 재테크           │
│ • Step 3 Series: 쇼츠 시리즈      │
│ • Step 4 Target: 30대 직장인      │
│ • Step 5 Tone: 유머/친근/짧음     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                  │
├──────────────────────────────────┤
│ [    이대로 진행 ▶            ]  │  ← primary CTA (height ≥ space.12 = 48px)
│ [    수정 후 진행              ] │  ← secondary (편집 모드 진입 시만 노출)
│ [    다시 생성 ↻               ] │  ← tertiary (text_muted, underline)
└──────────────────────────────────┘
   sticky bottom, padding=space.4
```

### 편집 모드 (✎ 클릭 시)

```
┌──────────────────────────────────┐
│ ┌────────────────────────────┐   │
│ │ [textarea]                 │   │  ← role=textbox, aria-multiline
│ │ 30대 직장인을 위한 짧고     │   │     bg=tokens.color.surface
│ │ 유머러스한 재테크 쇼츠       │   │     border=1px solid border_default
│ │                            │   │     focus: border_focus 2px
│ │                            │   │
│ │ 글자수: 28 / 70             │   │  ← counter (text_muted)
│ └────────────────────────────┘   │     70 초과 시 text_danger
│                                  │
│ [✓ 적용] [✗ 취소]                │  ← inline action (text_muted)
│                                  │
│ ━━ (이유 영역 동일)               │
├──────────────────────────────────┤
│ [    수정 후 진행 ▶           ]  │  ← primary (편집 후 활성)
│ [    다시 생성 ↻               ] │
└──────────────────────────────────┘
```

---

## variant: minimal (chosen=false, Quick Mode 권장)

```
┌──────────────────────────────────┐  ← viewport 360px width
│ ← back              Quick   menu │  ← Quick Mode 헤더
├──────────────────────────────────┤
│                                  │
│ "30대 직장인 재테크 쇼츠"        │  ← 한 줄만 (font.size_xl)
│                          ✎       │  ← 편집 icon
│                                  │
├──────────────────────────────────┤
│ [    이대로 진행 ▶            ]  │  ← primary
│ [    다시 생성 ↻               ] │  ← tertiary
└──────────────────────────────────┘
```

→ verbose의 "이유" section + "수정 후 진행" 별도 버튼 생략 (편집 후 primary가 "수정 후 진행"으로 자동 라벨 변경)

---

## 측정값 (tokens.md 참조 — literal 값 X)

| 항목 | 값 | tokens.md 참조 |
|---|---|---|
| viewport width | 360px | `bp.mobile` |
| header height | 48px | `space.12` |
| page padding (좌/우) | 16px | `space.4` |
| direction card padding | 16px | `space.4` |
| direction card bg | bg_subtle | tokens §1.4 |
| direction card text | text_default | tokens §1.5 |
| direction card border-radius | 12px | `radius.lg` |
| 이유 list bullet font | size_sm (14px) / text_muted | tokens §2.2, §1.5 |
| 구분선 색 | border_subtle | tokens §1.6 |
| primary CTA height | ≥ 48px | `space.12`, frontend_design_contract.md §3.3 |
| primary CTA bg | primary | tokens §1.2 |
| primary CTA text | text_inverse | tokens §1.5 |
| secondary CTA bg | bg_default + border_default 1px | tokens §1.4, §1.6 |
| tertiary CTA | text_muted underline | tokens §1.5 |
| 편집 icon (default) | text_muted | tokens §1.5 |
| 편집 icon (hover) | primary | tokens §1.2 |
| textarea bg (편집) | surface | tokens §1.4 |
| textarea border (focus) | border_focus 2px + offset 2px | tokens §1.6 |
| 글자수 카운터 (정상) | text_muted | tokens §1.5 |
| 글자수 카운터 (≥ 70자) | text_danger | tokens §1.5 |
| bottom area padding | 16px | `space.4` |
| 버튼 간 gap | 12px | `space.3` |
| motion (편집 모드 전환) | base (250ms) | `motion.base` |

---

## 응답/에러 상태 (`apps/web/direction_approval.md` §7 정합)

```
loading:
  ┌────────────────────────────┐
  │ ░░░░░░░░░░░░░░░░░░░░░░░    │  ← pulse skeleton
  │ ░░░░░░░░░░░░░░░░            │
  │                            │
  │ AI가 방향을 정리 중...      │
  └────────────────────────────┘

error:
  ┌────────────────────────────┐
  │ ⚠ 생성에 실패했어요         │  ← ErrorCard (Phase 1 기존)
  │ E-LLM-001 timeout          │
  │ [다시 생성 ↻]               │
  └────────────────────────────┘
```

---

## 변경

- variants chosen swap (verbose ↔ minimal):
  - `component_map.md` DirectionApprovalCard variants yaml 1줄 토글
  - 본 wireframe의 우선 표시 variant 갱신 (선택)
  - 영향: 2 파일 — replaceability **L~M**
- tokens 변경 (색/spacing) → 자동 반영 (literal 값 미사용)
- 편집 모드 inline → modal로 swap → 본 wireframe 편집 모드 section 재작성 + component_map.md Layout layer 갱신 (M)

---

## 변경 이력

- 2026-05-27: Phase 2 Slice 3 최초 작성 — verbose (chosen) + minimal (대안) ASCII art + 측정값 표
