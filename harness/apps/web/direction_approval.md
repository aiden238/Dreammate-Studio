# Direction Approval Pattern

> 위치: `apps/web/direction_approval.md`
> 상태: Phase 2 Slice 3 baseline (2026-05-27)
> 격상 사유: Discovery Step 6 + Quick Mode **양 모드 공통 핵심 UX 컴포넌트**.
> P-005 oneline_direction (`docs/contracts/output_schema.md` §7) 결과 표시 + 사용자 승인 / 수정 / 재생성.
>
> 참조: `apps/web/component_map.md` (DirectionApprovalCard), `apps/web/wireframes/direction_approval.md`,
>       `apps/web/design_system/component_contract.md` §4.3, `apps/web/design_system/variant_format.md` §4,
>       `apps/web/design_system/replaceability_score.md` §3.2, `apps/web/design_system/tokens.md`

---

## 1. 목적

- AI가 생성한 **한 줄 기획 방향**을 사용자가 검토
- **승인 / 수정 / 재생성** 3가지 행동 가능 (verbose) 또는 **승인 / 재생성** 2가지 (minimal)
- 승인 시 → 다음 단계 (Discovery Step 7 Generate 또는 Quick Mode Generate)
- 영상기획의 **분기점** — 이 한 줄이 P-006 plan_candidates 생성의 입력

---

## 2. 사용 컨텍스트

### 2.1 Discovery Step 6
- 입력: Step 1~5 종합 (brand + domain + series + target + tone)
- API: P-005 oneline_direction
- variant 권장: **verbose** (Step 1~5 이유 표시 → 사용자 신뢰 ↑)
- 다음: Step 7 Generate (승인) / 재호출 (재생성, revise_count++)

### 2.2 Quick Mode
- 입력: 짧은 자유 입력 + AI 부족정보 질문 1~2개 응답
- API: P-005 (동일 prompt, missing_info ≤ 2)
- variant 권장: **minimal** (빠른 흐름 우선)
- 다음: Quick Generate (승인) / 재호출 (재생성)

→ **같은 컴포넌트** (`DirectionApprovalCard`) — `variant` prop만 다름. 모드 분기는 `apps/web/mode_branching.md` 참조 (Slice 4 작성).

---

## 3. 컴포넌트

- 컴포넌트: `DirectionApprovalCard` (`apps/web/component_map.md` §DirectionApprovalCard 참조)
- 4-layer 전체 정의 (Behavior / Layout / Visual / Wireframe)
- 2 variants:
  - `verbose` (chosen=true) — Discovery 권장
  - `minimal` (chosen=false) — Quick Mode 권장
- Replaceability: **M** (variants swap 시 2 파일 영향 — component_map.md + wireframe)

---

## 4. 사용자 행동 모델

| 행동 | UI | 다음 단계 |
|---|---|---|
| 승인 | "이대로 진행 ▶" primary CTA | Generate 진입 (Discovery Step 7 또는 Quick Generate) |
| 수정 | inline 편집 모드 진입 → textarea → "수정 후 진행" | Generate 진입 (수정된 텍스트 전달, P-005 재호출 X) |
| 재생성 | "다시 생성 ↻" tertiary | P-005 재호출 (revise_count++), 다른 변형 한 줄 방향 |

### 4.1 편집 모드 (verbose에서 ✎ 클릭)
- 한 줄 방향 텍스트가 textarea로 변환 (inline edit)
- 글자 수 카운터 (≤ 70자, ≥ 20자 — output_schema §7.2 검증 규칙)
- 70자 초과 시 텍스트 카운터 `tokens.color.text_danger`
- 편집 후 "수정 후 진행" 또는 "취소"

### 4.2 재생성 cap
- revise_count ≤ 2 권장 (Critic revise 정책과 동일 — `apps/web/design.md` §13)
- 3회째 재생성 시 mode-down 제안 (Discovery → "다시 좁히기 권장" 안내)

---

## 5. 사용자 행동 추적 (Phase 4+ Analytics)

Phase 1/2는 spec만. Phase 4+에서 다음 추적:

| 지표 | 측정 방법 | 목적 |
|---|---|---|
| 승인 vs 수정 vs 재생성 비율 | 클라이언트 이벤트 + DB | minimal vs verbose 선택 기준 |
| 재생성 횟수 분포 | revise_count 누적 분포 | cap 적정성 (현재 2회) |
| 수정 텍스트 패턴 | 편집 전후 diff | 자주 수정되는 컴포넌트 식별 (target / format 등) |
| Discovery vs Quick 승인률 차이 | mode flag + 승인 이벤트 | mode 분기 정책 보강 |

→ **U2-4 검증 input** (`phases/active/phase-2-pwa-design/assumptions.md` §1.2) — Phase 4 실 사용자 데이터로 verbose ↔ minimal chosen swap 결정.

---

## 6. 매핑

| 항목 | 매핑 |
|---|---|
| API (생성) | P-005 oneline_direction (`docs/contracts/output_schema.md` §7) |
| API (재생성) | P-005 동일 prompt + revise_count++ |
| Discovery Step | §6 (`apps/web/discovery_flow.md` §6) |
| Quick Mode | `apps/web/quick_flow.md` (Slice 4 작성) — DirectionApprovalCard 재사용 |
| DB 매핑 | `video_projects.one_line_direction` (output_schema §7.3) |
| Component | `apps/web/component_map.md` §DirectionApprovalCard (4-layer + 2 variants) |
| Wireframe | `apps/web/wireframes/direction_approval.md` (verbose + minimal 양쪽) |

---

## 7. 응답/에러 상태 (`apps/web/design.md` §20 정합)

| 상태 | UI |
|---|---|
| empty | 진입 직후 — skeleton 1줄 + 버튼 placeholder |
| loading | P-005 호출 중 — pulse skeleton + "AI가 방향을 정리 중..." caption |
| success | 한 줄 방향 + (verbose: 이유) + 버튼 노출 |
| error | ErrorCard (Phase 1 기존, INV-001 / E-LLM-* 시리즈) + "다시 생성" retry CTA |
| validation_failed | one_line 길이 / 광고 표현 검증 실패 시 — `output_schema.md` §7.2 — 자동 재생성 1회, 2회 실패 시 error |

---

## 8. a11y (`docs/contracts/frontend_design_contract.md` §5)

- 페이지 aria-label: "기획 방향 승인"
- 한 줄 방향 영역: `role="region"` + `aria-label="AI 생성 기획 방향"`
- 편집 모드 textarea: `role="textbox"` + `aria-multiline="true"` + `aria-label="기획 방향 편집"`
- 버튼 3개 (verbose): `role="button"` + `aria-label` 명시 ("이대로 진행", "수정 후 진행", "다시 생성")
- 버튼 2개 (minimal): "이대로 진행", "다시 생성"
- 키보드:
  - Tab: 본문 → primary CTA → secondary → tertiary
  - 편집 모드: Tab으로 textarea 진입, Esc로 취소
- focus visible: `tokens.color.border_focus` 2px outline (offset 2px)
- prefers-reduced-motion: 편집 모드 전환 instant (`tokens.md` §6.3)

---

## 9. 변경성 (`apps/web/design_system/replaceability_score.md` §3.2)

| 변경 시나리오 | 영향 파일 | 비용 |
|---|---|---|
| variants chosen swap (verbose ↔ minimal) | component_map.md (1줄) + wireframe (선택, 우선순위 변경 시) | **L~M** |
| 추가 액션 추가 (예: "스타일만 바꿔") | component_map.md (Behavior + Visual layer) | **M** |
| 양 모드 분리 (다른 컴포넌트로 swap) | mode_branching.md + 2 별도 컴포넌트 spec + page_map.md | **H** |
| Visual 토큰 변경 (색/spacing) | tokens.md (1줄) — DirectionApprovalCard 자동 반영 | **L** |
| 편집 모드 UX 변경 (inline → modal) | component_map.md (Layout + Behavior) + wireframe | **M** |

---

## 10. Wireframe

`apps/web/wireframes/direction_approval.md` 참조.
- variant=verbose (Discovery Step 6 기준, current chosen)
- variant=minimal (Quick Mode 기준, 대안)
- 측정값은 모두 `tokens.md` 참조 (literal 값 X)

---

## 11. Phase 3 deferred

다음은 Phase 3 진입 시 결정 / 구현:
- 편집 모드 inline vs modal (현재 spec: inline)
- 재생성 cap 3회째 mode-down 제안 UI (Discovery로 안내 vs 강제 진입)
- partial result (P-005 한 줄 streaming) — Phase 4+ SSE 도입 후
- 한 줄 방향 외 components (target / message / format) 표시 여부 (현재 verbose에서 이유로 통합)

---

## 변경 이력

- 2026-05-27: Phase 2 Slice 3 최초 작성 — Direction Approval pattern 격상 (양 모드 공통 핵심 UX)
