# Component Contract (4-Layer Template)

> 위치: `apps/web/design_system/component_contract.md`
> 상태: Phase 2 Slice 1 baseline (2026-05-27)
> 원칙: **변경 가능성 우선** — 4-layer 분리로 변경 영향 범위를 layer 단위로 한정.
> 참조: `apps/web/design_system/tokens.md`, `docs/decisions/phase_2_design_layered_minimal.md` (ADR-010)

---

## 0. 적용 범위 (Minimal Application Policy)

**4-layer 강제는 4개 핵심 컴포넌트에만 적용** (ADR-010):
1. `BrandDirectionCard` (Discovery Step 1 + Step 2~7 패턴 재사용 baseline)
2. `CardGrid5` (5장 배치 컨테이너)
3. `DirectionApprovalCard` (양 모드 공통 핵심 UX)
4. `QuickInputCard` (Quick Mode 입력 + 부족정보 질문)

**나머지 컴포넌트**는 `component_map.md`에 minimal entry만:
- 이름 / 분류 / 의존성 / Phase 진입 시점

이유: **over-engineering 회피**. 4-layer 강제는 변경 빈도가 높은 컴포넌트에만 가치 있음. 나머지는 Phase 3+ 실 구현 중 자연스럽게 보강.

---

## 1. 4-Layer 구조

### Layer 1: Behavior (가장 안정 — 변경 비용 H)

**변경 시 영향**: Props 타입 변경은 caller 코드 / 테스트 / contract 모두 영향.

명시 항목:
- **Props** (TypeScript interface 형식) — 입력 데이터 + callbacks
- **State** — internal vs controlled by parent
- **Events** — `onXxx` callback signature
- **a11y** — `aria-*`, `role`, 키보드 인터랙션
- **출력 schema mapping** — `output_schema.md` § 참조 (해당 시)

### Layer 2: Layout (중간 — 변경 비용 M)

**변경 시 영향**: responsive 분기 / spacing tokens 영향. Behavior 무영향.

명시 항목:
- **배치** — flex / grid / stack 방향
- **Responsive** — mobile-first, breakpoint별 분기 (`tokens.bp.*`)
- **Spacing** — `tokens.space.*` 참조
- **Z-index** — 필요 시

### Layer 3: Visual (가장 변경 쉬움 — 변경 비용 L)

**변경 시 영향**: 색/폰트/radius/shadow만. Behavior / Layout 무영향. 토큰만 바꾸면 swap.

명시 항목:
- **Color** — `tokens.color.*` 참조 (리터럴 hex 금지)
- **Typography** — `tokens.font.*` 참조
- **Radius / Shadow / Motion** — `tokens.radius.*`, `tokens.motion.*` 참조
- **States** — default / hover / focus / active / disabled / selected

### Layer 4: Wireframe (참고용 — 변경 비용 L)

**변경 시 영향**: 시각 인지용. 실 구현에 직접 의존 없음.

명시 항목:
- **ASCII art** (mobile 360px 기준) — 인라인 또는
- **wireframes/ 폴더 파일 참조** — `apps/web/wireframes/<name>.md`

---

## 2. 4-Layer Template (복사용)

```markdown
## <ComponentName>

> 분류: <Card | Grid | Panel | ...>
> Phase 진입: <Phase X>
> Replaceability: <L | M | H>
> Variants: <count, 또는 'current only'>

### Behavior

```typescript
interface <ComponentName>Props {
  // 입력 데이터
  // ...

  // 콜백 / 이벤트
  // ...
}
```

- State: <controlled | internal — 명시>
- Events: <onXxx 목록>
- a11y: <role, aria-*, 키보드>
- 출력 schema mapping: <output_schema.md § 참조 (있다면)>

### Layout

- mobile (≤ tokens.bp.mobile_md): <배치>
- tablet (≥ tokens.bp.tablet): <배치 차이>
- desktop (≥ tokens.bp.desktop): <배치 차이>
- spacing: <tokens.space.*>

### Visual

- bg: <tokens.color.*>
- text: <tokens.color.*>, <tokens.font.*>
- border: <tokens.color.* + width>
- radius: <tokens.radius.*>
- motion: <tokens.motion.* — hover/focus/selected>
- states:
  - default: ...
  - hover: ...
  - focus: ... (focus-visible)
  - selected: ...
  - disabled: ...

### Wireframe

```
( ASCII art 또는 wireframes/<name>.md 참조 )
```

### Variants
참조: `apps/web/design_system/variant_format.md` 형식. 본 컴포넌트의 variants는 `component_map.md` 컴포넌트 entry에 yaml로 명시.
```

→ 위 template을 `component_map.md`의 4 핵심 컴포넌트 entry에 그대로 적용. Slice 2~4에서 작성.

---

## 3. 예시: BrandDirectionCard (Slice 1 baseline)

> 이 예시는 Slice 2에서 `component_map.md`에 정식 등재될 컴포넌트의 **template 시연**.  
> 실 변경/보강은 Slice 2에서.

### 분류 / 메타

- **분류**: Card (Discovery 카드 패턴 baseline)
- **Phase 진입**: Phase 3 Slice 2 (Discovery Step 1 구현 시점)
- **Replaceability**: M (variants swap 시 2~4 파일 영향)
- **Variants**: 3개 (current / horizontal_swipe / grid_2x3) — `variant_format.md` 형식

### 3.1 Behavior

```typescript
interface BrandDirectionCardProps {
  card: {
    card_id: string;          // P-001 output_schema §3
    kind: 'ai_suggestion' | 'user_direct_input';
    name: string;             // 8~14자 명사형 (design.md §11)
    description: string;      // 30~50자 한 줄 설명
    fit_situation?: string;   // 1줄 적합 상황
    pros?: string;            // 1줄 장점
    cautions?: string;        // 1줄 주의점
    confidence?: number;      // 0.0 ~ 1.0
  };
  selected: boolean;
  onSelect: (card_id: string) => void;
}
```

- **State**: `selected`는 parent controlled (CardGrid5가 5장 중 1장 관리)
- **Events**: `onSelect(card_id)` — 단일 콜백
- **a11y**:
  - `role="radio"` (5장 중 1장 선택 의미 — `frontend_design_contract.md` §5.3)
  - `aria-checked={selected}`
  - `aria-label={name}`
  - 키보드: Tab으로 진입 후 Space/Enter로 선택, 방향키로 형제 카드 이동
- **출력 schema mapping**: `output_schema.md` §3 P-001 (Brand 단계) — Step 2~7도 동일 schema 패턴 재사용

### 3.2 Layout

- **mobile (≤ tokens.bp.mobile_md, 390px)**: 100% width, `flex-direction: column` (stack vertical)
  - card padding: `tokens.space.4` (16px)
  - 내부 항목 gap: `tokens.space.3` (12px)
  - min-height: 컨텐츠 의존 (4~6 줄)
- **tablet (≥ tokens.bp.tablet, 768px)**: 동일 stack, 카드 폭 증가 (max-width 480px 정도)
- **desktop (≥ tokens.bp.desktop, 1024px)**: 가로 배치 가능 (CardGrid5 variants에 따라)
- **터치 타겟**: 카드 전체가 클릭 가능 — 높이 ≥ 56px 자동 충족 (`frontend_design_contract.md` §3.3)

### 3.3 Visual

| 항목 | default | hover | focus | selected | disabled |
|---|---|---|---|---|---|
| bg | `tokens.color.surface` | `tokens.color.bg_subtle` | (동) | `tokens.color.bg_subtle` | `tokens.color.bg_subtle` (60% opacity) |
| text | `tokens.color.text_default` | (동) | (동) | (동) | `tokens.color.text_muted` |
| border | `1px solid tokens.color.border_default` | (동) | `2px solid tokens.color.border_focus` (outline-offset 2px) | `2px solid tokens.color.primary` | `1px solid tokens.color.border_subtle` |
| radius | `tokens.radius.lg` (12px) | (동) | (동) | (동) | (동) |
| motion | — | `transform: scale(1.02)` / `tokens.motion.fast` | — | `tokens.motion.base` | — |

- **typography**:
  - name: `tokens.font.size_lg` + `tokens.font.weight_semibold`
  - description: `tokens.font.size_base` + `tokens.font.weight_regular`
  - fit_situation / pros / cautions: `tokens.font.size_sm` + `tokens.font.weight_regular` + `tokens.color.text_muted`
  - confidence: visual indicator (●●●○○) — `tokens.color.primary` for filled, `tokens.color.border_default` for empty

- **prefers-reduced-motion**: hover scale 제거, color transition만 유지 (`tokens.motion.instant`)

### 3.4 Wireframe

```
┌─────────────────────────────────────────────┐
│ [✓]  드림메이트 (h3 semibold)               │   ← name (card_id badge 선택 시 ✓)
│                                             │
│ 대학생 창업/굿즈/오프라인 행사를 결합한      │   ← description (15~16px, 2줄)
│ 복합 브랜드 (한 줄 설명, 30~50자)           │
│                                             │
│ ─────────────────────────────────────       │
│                                             │
│ Fit  대학생 콘텐츠 / 행사 운영              │   ← fit_situation (sm, muted)
│ Pros 다양한 소재, 커뮤니티 유입             │   ← pros (sm, muted)
│ ⚠ Cautions 톤 일관성 유지 필요             │   ← cautions (sm, muted)
│                                             │
│ confidence: ●●●●○                          │   ← 0.0~1.0 visual
└─────────────────────────────────────────────┘

  default 상태: border_default 1px
  selected 상태: border primary 2px + ✓ icon 표시
  focus 상태: 외곽선 border_focus 2px (outline-offset 2px)
```

→ Slice 2에서 `apps/web/wireframes/step1_brand.md`로 분리 (CardGrid5 5장 배치 wireframe 포함).

### 3.5 Variants (Slice 2에서 정식 등재)

3개:
- `current` — Stacked vertical 5-card (모바일 우선)
- `alt_horizontal_swipe` — Horizontal swipe carousel (탐색 강조)
- `alt_grid_2x3` — Grid 2×3 (전체 조망)

각 variant의 trade-off는 `variant_format.md` §3 예시 참조.

---

## 4. 패턴 재사용 (Step 2~7 + Direction Approval)

### 4.1 Discovery Step 2~7 카드 = BrandDirectionCard 패턴 변형

```
Step 2 Domain         → BrandDirectionCard 그대로 (output_schema §4 P-002)
Step 3 Series         → BrandDirectionCard + structure_type/cadence_hint 필드 추가 (P-003)
Step 4 Target         → BrandDirectionCard + pain_points/watch_motivation 필드 추가 (P-004)
Step 5 Tone           → BrandDirectionCard 변형 + example/avoid 필드 추가 (P-004)
                        OR form 패턴 (5-card 예외 가능 — Slice 3에서 결정)
Step 6 Direction      → DirectionApprovalCard 사용 (별도 컴포넌트)
Step 7 Generate       → ProgressStepper 사용 (Phase 1 기존)
```

→ 각 Step의 카드는 BrandDirectionCard의 Behavior layer에 step-specific 필드만 추가. Layout/Visual은 그대로 재사용.

### 4.2 CardGrid5

- Behavior: 5장 카드 배열 + 1장 선택 관리
- Layout: variants에 따라 vertical stack / horizontal swipe / grid 2×3
- Visual: 컨테이너 자체는 transparent. 자식 카드 spacing만 관리.
- Wireframe: Step별로 동일.

### 4.3 DirectionApprovalCard

- 별도 컴포넌트 (BrandDirectionCard와 패턴 다름)
- Behavior: 한 줄 방향 텍스트 + 인라인 편집 + "승인 / 수정 / 다시 좁히기" 3-way
- Variants 2개: minimal (한 줄 + 3 버튼) / verbose (요약 + 컴포넌트 분해 + 편집 모드)
- `apps/web/direction_approval.md`에서 Slice 3 상세

### 4.4 QuickInputCard

- 별도 컴포넌트 (단일 input + dynamic question)
- Behavior: 짧은 프롬프트 입력 → AI 부족정보 질문 1~2개 동적 노출
- Variants: current only (Phase 3 구현 중 alt 발생 시 추가)
- `apps/web/quick_flow.md`에서 Slice 4 상세

---

## 5. 4-Layer 적용 안 하는 컴포넌트 (minimal entry)

`component_map.md`에 다음 형식만:

```markdown
### <ComponentName>

- 분류: <Card | Panel | ...>
- Phase 진입: <Phase X Slice Y>
- 의존성: <다른 컴포넌트 / contract 참조>
- 비고: <1줄>
```

대상:
- Phase 1 기존: `PlanCard`, `ErrorCard`, `ProgressStepper`, `SubmitButton`
- Discovery 보조: `WizardStepHeader`, `DirectInputFallback`
- AI Flow 보조: `AgentStatusIndicator`, `RAGReferencePanel`
- Layout: `AppShell`, `BottomActionBar`, `BreadcrumbBrandPath`
- 기타 (`apps/web/design.md` §10 전체 참조)

→ Phase 3 진입 시 구현 중 자연스러운 보강. 본 Phase 2에서 모든 컴포넌트 4-layer 강제하지 않음.

---

## 6. 검증 grep (Phase 2 Slice 6에서 자동화)

```bash
# 4-layer 형식 존재 확인 (4 핵심 컴포넌트에서)
grep -c "## Behavior\|## Layout\|## Visual\|## Wireframe" apps/web/component_map.md
# 예상: ≥ 16 (4 컴포넌트 × 4 layer)

# tokens 참조 검증 (Visual layer에 리터럴 hex 없는지)
grep -E "#[0-9A-Fa-f]{3,6}\b" apps/web/component_map.md
# 예상: 0 (또는 명시적 placeholder 주석 내부만)
```

---

## 7. 변경 이력

- 2026-05-27: Phase 2 Slice 1 — 4-layer template 정립 + BrandDirectionCard 예시 1개
