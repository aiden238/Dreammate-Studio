# Variants Bank Format

> 위치: `apps/web/design_system/variant_format.md`
> 상태: Phase 2 Slice 1 baseline (2026-05-27)
> 원칙: **변경 가능성 우선** — variant chosen 변경 1줄로 디자인 swap.
> 참조: `apps/web/design_system/component_contract.md`, `docs/decisions/phase_2_variants_3_components.md` (ADR-011)

---

## 0. 적용 범위 (Minimal Application Policy)

**Variants Bank는 3개 컴포넌트에만 적용** (ADR-011):
1. `BrandDirectionCard` — 3 variants (current / horizontal_swipe / grid_2x3)
2. `CardGrid5` — 2~3 variants (Slice 2에서 정식 결정)
3. `DirectionApprovalCard` — 2 variants (minimal / verbose)

**나머지 컴포넌트**는 current variant만 (의도된 단순화):
- `QuickInputCard` — current only (Phase 3 구현 중 alt 발생 시 추가)
- Phase 1 기존 컴포넌트 (PlanCard 등) — Phase 1 구현 그대로 (variants 없음)

이유: variants Bank는 **의미 있는 trade-off가 있는 alt**가 있을 때만 가치. 모든 컴포넌트 강제 시 관리 비용만 증가. 사용자 실 사용 데이터(Phase 9+) 누적 후 의미 있는 alt 추가가 자연스러움.

---

## 1. yaml schema

```yaml
variants:
  - id: <kebab-case identifier>
    name: "<human readable name>"
    chosen: false                    # 현재 사용 중인 variant는 true (1개만)
    layout: "<1 line description>"
    tradeoff_pros: "<장점 1~2 줄>"
    tradeoff_cons: "<단점 1~2 줄>"
    replaceability_cost: L           # L | M | H (이 variant로 swap 시 비용)
    decision_log: "<선택/거부 사유 1줄, ADR 참조 가능>"
```

### 1.1 필드 정의

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `id` | string (kebab-case) | yes | 영문 identifier (`current`, `alt_horizontal_swipe` 등) |
| `name` | string | yes | 사람이 읽는 이름 |
| `chosen` | boolean | yes | **정확히 1개**의 variant만 `true` |
| `layout` | string (1줄) | yes | 배치 / 인터랙션 한 줄 요약 |
| `tradeoff_pros` | string (1~2줄) | yes | 이 variant의 장점 |
| `tradeoff_cons` | string (1~2줄) | yes | 이 variant의 단점 |
| `replaceability_cost` | enum (L\|M\|H) | yes | 이 variant로 swap 시 비용 (`replaceability_score.md` 참조) |
| `decision_log` | string (1줄) | yes (chosen=true 시 필수) | 선택/거부 사유 + ADR 참조 (있다면) |

### 1.2 운영 정책

- **최소 1개 (current) 필수** — chosen=true 단 1개
- **추가 variants 권장 (반드시 X)** — 의미 있는 alt만 등재. 가짜 alt 만들지 않음
- **chosen 변경 시**:
  - 단순 swap → variant_format.md 형식 따라 `chosen` flag만 토글
  - decision_log에 변경 사유 + 날짜 + 사용자 승인 기록
  - ADR 작성 권장 (`docs/decisions/`)
- **variant 추가/제거 시**: contract-change Skill 절차 적용 안 함 (variants Bank는 contract 외부)

---

## 2. 위치 (어디에 yaml 작성?)

각 컴포넌트의 entry 내부 (component_map.md):

```markdown
### BrandDirectionCard

- 분류: Card
- Phase 진입: Phase 3 Slice 2
- Replaceability: M

#### Behavior
...

#### Layout
...

#### Visual
...

#### Wireframe
...

#### Variants

\`\`\`yaml
variants:
  - id: current
    name: "Stacked vertical 5-card"
    chosen: true
    ...
\`\`\`
```

→ Slice 2~3에서 정식 등재.

---

## 3. 적용 예시: BrandDirectionCard

> Slice 2에서 `component_map.md`에 등재될 정식 yaml의 **template 시연**.

```yaml
variants:
  - id: current
    name: "Stacked vertical 5-card"
    chosen: true
    layout: "세로 1열 5행, swipe X, 한 화면에 ~2장 보임 + 스크롤"
    tradeoff_pros: |
      360px 모바일 적합 — 한 손 스크롤만으로 5장 탐색.
      user_input 슬롯(5번째)이 자연스럽게 발견됨.
    tradeoff_cons: |
      전체 5장 동시 조망 어려움 (스크롤 필요).
      세로 길이 증가로 BottomActionBar까지 거리 멀어짐.
    replaceability_cost: L
    decision_log: "Phase 2 Slice 2 채택 — 모바일 우선 정책 (design.md §17)"

  - id: alt_horizontal_swipe
    name: "Horizontal swipe carousel"
    chosen: false
    layout: "가로 스와이프 carousel, 1화면에 1.5장 보임 (peek)"
    tradeoff_pros: |
      exploration 유도 — peek로 다음 카드 인지 유도.
      시각 강조 효과 ↑ (한 장당 면적 큼).
    tradeoff_cons: |
      user_input 슬롯이 5번째라 발견 어려움 (스와이프 누적 비용).
      swipe gesture 학습 비용 + 키보드 접근성 ↓.
    replaceability_cost: M
    decision_log: "Phase 9 실 사용자 피드백 후 재검토 (탐색성 vs 발견성 trade-off)"

  - id: alt_grid_2x3
    name: "Grid 2 col × 3 row"
    chosen: false
    layout: "2×3 그리드 (1자리 user_input, 1자리 비움 또는 ai_suggestion 5번째)"
    tradeoff_pros: |
      전체 5~6장 한 화면 조망 가능.
      비교 의사결정 빠름.
    tradeoff_cons: |
      카드 크기 작아짐 → 본문(description) 가독성 ↓.
      360px 환경에서는 무리 (text overflow 위험).
    replaceability_cost: M
    decision_log: "Phase 11+ 데스크톱/태블릿 전용 옵션으로 재검토 가능"
```

---

## 4. 적용 예시: DirectionApprovalCard

```yaml
variants:
  - id: minimal
    name: "한 줄 방향 + 3-way 버튼"
    chosen: true
    layout: "한 줄 텍스트 (inline edit 가능) + [승인] [수정] [다시 좁히기] 3 버튼"
    tradeoff_pros: |
      Quick Mode 흐름에 최적 (빠른 승인 1초).
      Direction 본질에만 집중 — 부가 정보 없음.
    tradeoff_cons: |
      Direction 근거(어떤 선택에서 도출됐는지)를 사용자가 못 봄.
      수정 시 어떤 컴포넌트(target/tone 등) 바꿔야 할지 불명확.
    replaceability_cost: L
    decision_log: "Phase 2 Slice 3 채택 — Quick Mode 우선, Direction Approval은 빠른 승인 UX"

  - id: verbose
    name: "Direction + components breakdown + 편집 모드"
    chosen: false
    layout: "한 줄 방향 + 컴포넌트 분해 (target/tone/length/format) + 컴포넌트별 인라인 편집"
    tradeoff_pros: |
      Direction 도출 근거 시각화 — 사용자 신뢰 ↑.
      컴포넌트별 편집으로 정밀 조정 가능.
    tradeoff_cons: |
      세로 길이 길어짐 — 한 화면 한 CTA 원칙 위반 위험.
      Quick Mode 흐름 느려짐.
    replaceability_cost: M
    decision_log: "Phase 9 사용자 데이터 (편집 빈도) 후 minimal과 A/B 비교"
```

---

## 5. variant chosen 변경 절차

```
1. 현재 chosen=true variant 식별
2. 변경 사유 명시 (사용자 피드백 / A/B 결과 / 사업 결정 등)
3. 영향 분석:
   - replaceability_cost 확인 (L/M/H)
   - 영향 파일 예측 (replaceability_score.md 표 참조)
4. ADR 작성 권장 (`docs/decisions/phase_X_variant_swap_<component>.md`)
5. component_map.md의 variants yaml에서:
   - 현재 chosen=true → chosen=false (decision_log 갱신)
   - 새 chosen=false → chosen=true (decision_log 갱신)
6. 영향 파일 (Visual layer / Layout layer) 갱신
7. audit_naming.ps1 실행 — 0 drift 확인
8. commit + push
```

### 5.1 변경 비용 예시

| 변경 | 영향 파일 | 비용 |
|---|---|---|
| `BrandDirectionCard` current → alt_grid_2x3 | component_map.md (variants) + Layout layer 갱신 + step1_brand wireframe 갱신 | M (2~4 파일) |
| `DirectionApprovalCard` minimal → verbose | component_map.md (variants) + Layout layer 갱신 | L~M (1~2 파일) |
| `CardGrid5` current → alt | component_map.md + 모든 Step wireframe 영향 | M (3~5 파일) |

---

## 6. 검증 grep (Phase 2 Slice 6)

```bash
# variants yaml 존재 확인
grep -c "variants:" apps/web/component_map.md
# 예상: ≥ 3 (BrandDirectionCard + CardGrid5 + DirectionApprovalCard)

# chosen=true 정확히 1개씩 확인 (variant block당)
grep -c "chosen: true" apps/web/component_map.md
# 예상: variants 보유 컴포넌트 수와 일치
```

---

## 7. 변경 이력

- 2026-05-27: Phase 2 Slice 1 — variant yaml schema 정립 + BrandDirectionCard / DirectionApprovalCard 예시 2개
