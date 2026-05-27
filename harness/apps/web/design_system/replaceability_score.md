# Replaceability Score (L / M / H)

> 위치: `apps/web/design_system/replaceability_score.md`
> 상태: Phase 2 Slice 1 baseline (2026-05-27)
> 원칙: **단순 3단계** — 너무 정교하게 만들지 않음 (over-engineering 회피).
> 참조: `apps/web/design_system/tokens.md`, `component_contract.md`, `variant_format.md`

---

## 0. 목적

각 컴포넌트 / 영역의 변경 비용을 미리 가시화 → **사용자가 "이거 바꿔" 요청 시 즉시 비용 예측**.

`design_handoff.md` (Slice 5) 작성의 baseline이 됨.

---

## 1. 정의

| Score | 의미 | 영향 파일 수 | 영향 layer | 예시 |
|---|---|---|---|---|
| **L** (Low) | tokens.md 또는 컴포넌트 1개 수정으로 swap 가능 | ≤ 1 | Visual only | 색 변경 / 폰트 변경 / spacing 1개 조정 / variant chosen 토글 (단순) |
| **M** (Medium) | 2~4 파일 수정, Layout/Behavior 일부 변경 | 2 ~ 4 | Visual + Layout | 카드 패턴 swap / 카드 수 5 → 4 / variants chosen 교체 (영향 wireframe 동반) |
| **H** (High) | 5+ 파일, 구조적 재설계 | 5+ | Behavior + Layout + Visual + Schema | Discovery 단계 수 변경 / Mode 폐기 / 4계층 데이터 모델 변경 |

### 1.1 판정 기준

- **L**: 의미가 같고 시각만 다른 경우 (`primary: indigo → cyan`)
- **M**: 의미 동일하지만 배치/패턴이 다른 경우 (`vertical stack → grid`)
- **H**: 의미 자체가 변하는 경우 (`Discovery 7단계 → 5단계` = UX 정의 변경)

---

## 2. 부여 정책

각 컴포넌트 / 영역에 **하나의 score 부여**:
- `component_map.md`의 각 컴포넌트 entry에 `replaceability: L | M | H` 명시 (Slice 2~5)
- 단일 score = "이 컴포넌트를 swap할 때 일반적 비용"

**variants 별로도 score 부여** (variant_format.md `replaceability_cost`) — variant 단위 비용은 컴포넌트 단위와 다를 수 있음.

---

## 3. 예시 표 (Phase 2 baseline)

### 3.1 Design System 자체

| 항목 | Score | 사유 |
|---|---|---|
| `tokens.md` 자체 변경 | L | 단일 파일 수정으로 전체 swap |
| `tokens.md` color subset만 변경 | L | 1 카테고리만 (예: primary 변경) |
| `tokens.md` 카테고리 추가 (예: opacity scale) | M | tokens.md + 영향 컴포넌트 Visual layer 보강 |

### 3.2 핵심 컴포넌트 (4-layer 적용)

| 컴포넌트 | Score | 사유 |
|---|---|---|
| `BrandDirectionCard` Visual 변경 (색/폰트) | L | tokens 1줄 수정 |
| `BrandDirectionCard` Layout 변경 (variants chosen) | M | variants chosen 토글 + 영향 wireframe 1개 |
| `BrandDirectionCard` Behavior 변경 (props 추가) | H | TypeScript types + 호출자 코드 + 테스트 모두 영향 |
| `CardGrid5` variants chosen 변경 | M | 모든 Step wireframe 영향 (5장 배치 변경) |
| `DirectionApprovalCard` minimal → verbose | M | variant swap 명시된 대안 |
| `DirectionApprovalCard` 3-way → 2-way 버튼 | H | UX 의미 변경 + Quick/Discovery 양 모드 영향 |
| `QuickInputCard` Visual 변경 | L | tokens 참조만 |
| `QuickInputCard` 부족정보 질문 형식 변경 | M | Behavior layer 일부 + dispatch 로직 |

### 3.3 Page-level 변경

| 변경 | Score | 사유 |
|---|---|---|
| Discovery 7 → 5 단계 축소 | H | `discovery_flow.md` + `mode_branching.md` + `page_map.md` + `component_map.md` + wireframes (5+ 파일) |
| Discovery Step 추가 (Step 8) | H | flow + branching + page_map + 새 wireframe |
| Quick Mode 폐기 | H | `quick_flow.md` 삭제 + `mode_branching.md` 전면 재작성 + page_map 정리 (5+ 파일) |
| Quick Mode 부족정보 질문 수 변경 (2→3) | L | `quick_flow.md` 1줄 |
| Mode 자동 분기 규칙 추가 | M | `mode_branching.md` + 영향 page (2 파일) |

### 3.4 Output / Plan 영역 (Phase 4)

| 변경 | Score | 사유 |
|---|---|---|
| Plan 비교 카드 활성화 (Phase 4) | M | placeholder → 실 spec, 다른 컴포넌트 무영향 |
| Plan 카드 수 3 → 2 또는 3 → 5 | M | `component_map.md` (PlanCard variants) + page_map (Output 페이지) |
| 8차원 점수 → 4차원 축소 | M | QualityScorePanel + Critic schema 영향 (output_schema 변경 = contract-change Skill) |

---

## 4. 사용 시나리오

### 4.1 사용자 요청: "primary 색을 indigo에서 brand orange로 바꾸자"

```
1. replaceability_score.md 확인 → "tokens.md color subset 변경 = L"
2. 예상 작업: tokens.md primary 4 토큰 (default/hover/pressed/disabled) 변경
3. 영향 파일: 1 (tokens.md만)
4. 예상 시간: 5분
5. 위험: 거의 없음 (tokens 참조만 하면 자동 반영)
6. 검증: visual smoke test (스크린샷) — Phase 3 진입 후
```

### 4.2 사용자 요청: "Discovery를 5단계로 줄이자"

```
1. replaceability_score.md 확인 → "H"
2. 예상 작업: 5+ 파일 수정 (flow + branching + page_map + component_map + wireframes)
3. 사용자에게 비용 미리 공유: "Discovery 단계 변경은 H 비용. flow / branching / page_map / wireframes 5+ 파일 영향. 1~2일 작업 예상"
4. 결정 후 ADR (`docs/decisions/phase_X_discovery_5_steps.md`) 작성
5. contract-change Skill 적용 검토 (output_schema의 단계별 prompt_id 매핑 영향이 있다면)
```

### 4.3 사용자 요청: "BrandDirectionCard를 가로 스와이프로 바꿔보자"

```
1. variant_format.md 확인 → BrandDirectionCard alt_horizontal_swipe (replaceability_cost: M)
2. 예상 작업:
   - component_map.md의 variants yaml에서 chosen toggle (current → alt_horizontal_swipe)
   - Layout layer 갱신
   - step1_brand wireframe 갱신 (가로 스와이프 ASCII)
3. 영향 파일: 2~3
4. ADR 권장
```

---

## 5. 통합 매트릭스 (Slice 5에서 design_handoff.md로 통합)

Slice 5의 `design_handoff.md`는 본 score를 **변경 시나리오 → 영향 파일 → 비용 매핑표**로 종합. 본 문서는 그 baseline 정의.

```
design_handoff.md (Slice 5):
  변경 시나리오 X → tokens.md / component_map.md / wireframes / ... 어떤 파일?
  → 영향 라인 수 / 영향 layer / replaceability score
  → 사용자 미리 비용 공유 가능
```

---

## 6. 의도된 단순화

다음은 **하지 않음**:

- 정량 점수 (1~10) — L/M/H 3단계로 충분, 정밀도보다 의사결정 속도 우선
- 자동 측정 도구 — Phase 3+ 실 코드 생긴 후 grep 기반 측정 가능. Phase 2는 spec 단계
- Per-property granularity (color vs typography vs spacing 별도 점수) — 카테고리 묶음으로 충분

---

## 7. 변경 이력

- 2026-05-27: Phase 2 Slice 1 — L/M/H 3단계 정책 + 예시 매트릭스 baseline
