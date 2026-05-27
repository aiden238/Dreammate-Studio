# Wireframe — Quick Mode Short Flow

> 위치: `apps/web/wireframes/quick_short.md`
> 상태: Phase 2 Slice 4 baseline (2026-05-27)
> 대상: mobile 360px first. Brand/Series 있는 기존 사용자.
> 참조: `apps/web/quick_flow.md`, `apps/web/component_map.md` (QuickInputCard / DirectionApprovalCard), `apps/web/design_system/tokens.md`
>
> 원칙: ASCII art는 시각 인지용. 실 구현은 컴포넌트의 4-layer Visual / Layout layer + tokens.md를 단일 진실 소스로 사용.

---

## 현재 chosen variant: `current` (single textarea — QuickInputCard variants Bank §QuickInputCard)

---

## Step 1 — 짧은 프롬프트 입력

```
┌──────────────────────────────────┐  ← viewport 360px width
│ ← back            Quick     menu │  ← BreadcrumbBrandPath + Mode badge (height = space.12)
├──────────────────────────────────┤
│                                  │
│   Brand A · Series B             │  ← 현재 컨텍스트 (size_xs, text_muted)
│                                  │
│   이번엔 어떤 영상을?              │  ← H1 (font.size_3xl, font.weight_bold)
│   짧게 의도만 입력하면 돼요         │  ← subtitle (font.size_sm, text_muted)
│                                  │
├──────────────────────────────────┤
│                                  │  ← QuickInputCard 시작 (mode='initial_prompt')
│ ┌────────────────────────────┐   │
│ │ [textarea]                  │   │  ← textarea (rows=4, min-height=space.24)
│ │                            │   │     bg=color.surface, border=1px border_default
│ │ 예: "다른 스타일로 한 편 더" │   │     placeholder (text_placeholder)
│ │                            │   │
│ │                            │   │
│ │                       0/300 │   │  ← char count (size_xs, text_muted, aria-live)
│ └────────────────────────────┘   │
│                                  │  ← gap: space.4 (16px)
├──────────────────────────────────┤
│ [        다음 ▶                ] │  ← SubmitButton (sticky bottom, primary)
└──────────────────────────────────┘     value 비어있을 때: disabled (primary_disabled)
```

측정값 (모두 tokens.md 참조):
- viewport: 360px (`tokens.bp.mobile`)
- 좌우 padding: `tokens.space.4` (16px)
- textarea min-height: `tokens.space.24` (96px, rows=4 + padding)
- textarea radius: `tokens.radius.md` (8px)
- char count font: `tokens.font.size_xs` (12px)
- SubmitButton height: 56px (≥ touch target — `frontend_design_contract.md` §3.3)

---

## Step 2 — 부족 정보 질문 (1~2개, Optional)

```
┌──────────────────────────────────┐
│ ← back            Quick     menu │
├──────────────────────────────────┤
│                                  │
│   한 가지만 더!                    │  ← H1 (size_3xl, bold)
│   AI가 영상 만들기 전 확인해요      │  ← subtitle (size_sm, text_muted)
│                                  │
├──────────────────────────────────┤
│                                  │
│  Q. 어떤 분께 보여드릴             │   ← 동적 질문 (size_lg, semibold)
│     영상인가요?                    │      aria-live="polite"
│                                  │
│ ┌────────────────────────────┐   │
│ │ [textarea]                  │   │  ← QuickInputCard (mode='follow_up_question')
│ │                            │   │     placeholder: "예: 20대 대학생"
│ │                            │   │
│ │                       0/200 │   │
│ └────────────────────────────┘   │
│                                  │
│  (필요 시 Q2도 — 최대 2개)         │   ← size_xs, text_muted
│                                  │
├──────────────────────────────────┤
│ [    이대로 진행 (skip) ▷       ] │  ← SubmitButton secondary (text_muted)
│ [    답변 후 진행 ▶            ] │  ← SubmitButton primary
└──────────────────────────────────┘
```

측정값:
- 질문 텍스트 영역: `tokens.space.4` padding + `tokens.font.size_lg`
- 두 CTA 간 gap: `tokens.space.3` (12px)
- skip 버튼: bg=transparent, border=1px border_default, text=text_muted

상태:
- 답변 1개 이상 입력 → "답변 후 진행" 활성 (primary)
- 답변 없음 → "답변 후 진행" 비활성, skip만 활성

---

## Step 3 — Direction Approval (minimal variant)

→ `wireframes/direction_approval.md` minimal variant 참조 (Slice 3 작성).

Quick Mode는 항상 minimal variant 사용 (`quick_flow.md` §3.2).

요약:
- 한 줄 방향 텍스트 (P-005 oneline_direction)
- [승인] [수정] [다시 좁히기] 3-way 버튼
- 수정 시 인라인 textarea
- "다시 좁히기" → Discovery 전환 (`mode_branching.md` override `direction_renarrow`)

---

## Step 4 — Generate

→ Phase 0 기존 컴포넌트 재사용:
- `GenerationProgressStepper` 4단계 (Intent → RAG → Plan → Critic)
- `PlanOptionCard` × 3 (Phase 4 활성 시)

Discovery Step 7과 동일 화면 (모드 차이 없음 — 양 모드 공유).

---

## 변경 시나리오 (replaceability_score.md §3.3 정합)

| 변경 | 영향 wireframe | 비용 |
|---|---|---|
| QuickInputCard variants chosen 토글 (다른 variant 추가 시) | quick_short.md (Step 1 + Step 2 ASCII 교체) | L~M |
| Step 2 부족 정보 질문 컴포넌트 교체 (textarea → 4지선다) | quick_short.md (Step 2) + component_map.md (QuickInputCard or IntentQuestionCard) | M |
| Step 2 skip 정책 제거 | quick_short.md (Step 2 CTA 영역) + quick_flow.md §2.4 | L |
| 200자 → 500자 character limit 확장 | quick_short.md (char count 표시) + quick_flow.md §1.4 | L |
| tokens.color.primary 변경 | tokens.md 1줄, 본 wireframe 자동 (literal 값 0) | L |

---

## 대안 variants (chosen=false, 참고용)

본 wireframe은 QuickInputCard `current` variant 기준. 향후 alt 추가 시:

- **alt_voice** (Phase 11+ 가능): 음성 입력 + 텍스트 transcript 표시
- **alt_4_choice** (Phase 3 사용자 피드백 후): Step 2 질문을 4지선다 카드로 (`IntentQuestionCard` 패턴)

→ alt 추가 시 본 wireframe 별도 section 추가 + `component_map.md` QuickInputCard variants yaml에 등재.

---

## 변경 이력

- 2026-05-27: Phase 2 Slice 4 — Step 1/2 ASCII wireframe 작성 (360px 적합), Step 3/4는 외부 wireframe 참조
