# Mode Branching Rules

> 위치: `apps/web/mode_branching.md`
> 상태: Phase 2 Slice 4 baseline (2026-05-27)
> 참조: `apps/web/discovery_flow.md`, `apps/web/quick_flow.md`, `apps/web/design.md` §11~§12, `docs/contracts/output_schema.md` §3~§9
>
> 원칙: Discovery vs Quick **자동 분기** + 사용자 **override** 정책.
> yaml format으로 작성 — 변경 시 본 파일 1곳만 수정 (replaceability M, `replaceability_score.md` §3.3).

---

## 0. 개요

### 0.1 분기 흐름

```
사용자 진입 (/new)
  ↓
컨텍스트 검사 (user.brands.count / user.current_brand.series.count)
  ↓
       ┌─────────────────┴─────────────────┐
   Discovery                              Quick
   (신규 / 컨텍스트 부족)              (기존 컨텍스트 충분)
       ↓                                   ↓
   7-step wizard                       short flow (2~4 step)
   (discovery_flow.md)                 (quick_flow.md)
```

### 0.2 결정 우선순위

1. 사용자 명시 override (`override_rules`) — 가장 우선
2. 자동 분기 (`branching_rules`) — priority 숫자 작은 순으로 평가
3. 모든 rule 불일치 시 default (priority 99 = Discovery 안전 fallback)

### 0.3 적용 시점

- Phase 2: spec only (본 yaml은 라우팅 의도 표현)
- Phase 3: Next.js middleware로 라우팅 구현
- Phase 4: backend `/api/v1/plans/start` endpoint가 컨텍스트 검사 + 분기 mode 반환

---

## 1. yaml schema

```yaml
branching_rules:
  - id: <kebab-case identifier>
    condition:
      <key>: <value | comparison string>
    mode: <discovery | discovery_from_stepN | quick>
    rationale: "<1~2줄 사유>"
    priority: <number, 작을수록 우선>
    note?: "<선택, Phase 진화 메모>"

override_rules:
  - id: <kebab-case identifier>
    trigger: "<UI 트리거 또는 사용자 명시 액션>"
    condition?:
      <key>: <value>
    mode: <discovery | quick>
    note?: "<선택>"
```

### 1.1 필드 정의

| 필드 | 타입 | 필수 | 의미 |
|---|---|---|---|
| `id` | string (kebab-case) | yes | 영문 identifier |
| `condition` | object (key:value) | yes (branching) / no (override) | 컨텍스트 조건. value는 literal 또는 비교 문자열 (`">= 1"` 등) |
| `mode` | enum | yes | `discovery` / `discovery_from_stepN` / `quick` |
| `rationale` | string | yes | 분기 사유 |
| `priority` | number | yes (branching) | 작을수록 우선 평가 |
| `trigger` | string | yes (override) | "user 명시 '<X>'" 형식 |
| `note` | string | no | Phase 진화 / 예외 메모 |

### 1.2 mode 종류

- `discovery` — 7-step wizard 전체 (Step 1부터)
- `discovery_from_stepN` — Step N부터 시작 (이전 step 결과 prefill, Phase 3+ 구현)
- `quick` — short flow (quick_flow.md Step 1부터)

---

## 2. 분기 규칙 (yaml)

```yaml
branching_rules:
  - id: rule_new_user
    condition:
      user.brands.count: 0
    mode: discovery
    rationale: "신규 사용자 — Brand 컨텍스트 0. Discovery 7-step 강제 (onboarding)."
    priority: 1
    note: "user_scenarios.md §1 첫 사용자 시나리오 정합"

  - id: rule_brand_no_series
    condition:
      user.brands.count: ">= 1"
      user.current_brand.series.count: 0
    mode: discovery_from_step3
    rationale: "Brand 있음, Series 신규 — Step 1 (Brand) / Step 2 (Domain) skip, Step 3 (Series)부터 시작."
    priority: 2
    note: "Phase 3+ 구현 시 Step 1/2 결과 prefill. discovery_flow.md §3 Step 3 진입 직접 라우팅."

  - id: rule_has_series
    condition:
      user.current_brand.series.count: ">= 1"
    mode: quick
    rationale: "Series 존재 — Quick Mode 짧은 흐름 (기존 컨텍스트 재활용)."
    priority: 3
    note: "quick_flow.md §0.3 진입. Phase 9 임계값 재조정 가능 (series.count >= 2일 때만 quick 더 강조)."

  - id: rule_default
    condition: {}
    mode: discovery
    rationale: "분류 불가 시 안전한 default — Discovery (정보 더 많이 수집)."
    priority: 99
    note: "모든 rule 불일치 시 fallback. 실제 진입 빈도 ≈ 0 예상."
```

### 2.1 priority 평가 순서

- priority 숫자 작은 순으로 condition 평가
- 처음 일치하는 rule에서 mode 결정 (early return)
- rule_new_user (1) → rule_brand_no_series (2) → rule_has_series (3) → rule_default (99)

### 2.2 condition 비교 문자열 해석 (Phase 3+ 구현)

- `0` (literal) — 정확히 0
- `">= 1"` — 1 이상
- `">= 2"` — 2 이상
- `"in [a, b, c]"` — enum 멤버십 (현재 미사용, Phase 9+ 확장 시)

---

## 3. Override 규칙 (yaml)

```yaml
override_rules:
  - id: user_new_project
    trigger: "user 명시 '새로 시작' 버튼 클릭 (Dashboard / Workspace)"
    mode: discovery
    note: "기존 컨텍스트 무시, Discovery 강제. design.md §12 Quick Mode 'Direction 다시 좁히기' 선택지와 동일 진입."

  - id: user_quick_force
    trigger: "user 명시 'Quick Mode' 선택 (Settings advanced 또는 Quick prompt 직접 진입 URL)"
    condition:
      user.brands.count: ">= 1"
    mode: quick
    note: "Brand 있을 때만 허용. Brand 없을 시 자동으로 Discovery 라우팅 (안전 fallback)."

  - id: direction_renarrow
    trigger: "Quick Mode Step 3 DirectionApprovalCard '다시 좁히기' 버튼 클릭"
    mode: discovery
    note: "Quick → Discovery 전환. Step 1부터 (또는 Phase 3 결정 시 Step 3부터). direction_approval.md §3-way 버튼 정합."
```

### 3.1 트리거 위치

| trigger | UI 위치 | 컴포넌트 |
|---|---|---|
| user_new_project | Dashboard "+ 새 프로젝트" / Workspace "새로 시작" | AppShell (Phase 0 entry) |
| user_quick_force | Settings advanced 토글 / Quick URL 직접 진입 | (Phase 11+ 추후) |
| direction_renarrow | DirectionApprovalCard "다시 좁히기" 버튼 | DirectionApprovalCard (Slice 3 entry) |

---

## 4. 매핑 표

| 사용자 상태 | 분기 | 진입 라우트 (Phase 3) | rule_id |
|---|---|---|---|
| 신규 (Brand 0) | Discovery | `/new/discovery/step/1` | rule_new_user |
| Brand 있음, Series 0 | Discovery from Step 3 | `/new/discovery/step/3` | rule_brand_no_series |
| Series 있음 | Quick | `/new/quick` | rule_has_series |
| 명시 "새로 시작" | Discovery (강제) | `/new/discovery/step/1` | user_new_project |
| 명시 "Quick" (Brand 있음) | Quick (강제) | `/new/quick` | user_quick_force |
| Quick Mode "다시 좁히기" | Discovery (전환) | `/new/discovery/step/1` | direction_renarrow |
| 분류 불가 | Discovery (fallback) | `/new/discovery/step/1` | rule_default |

---

## 5. 검증 (Phase 3+ 자동화 가능)

### 5.1 yaml 무결성

```
- branching_rules 최소 3개 (rule_new_user / rule_brand_no_series / rule_has_series) + default fallback 1개
- 각 rule의 priority 고유 (중복 priority 시 평가 순서 불확정)
- mode 값은 enum 정합 (discovery / discovery_from_stepN / quick)
- override_rules 최소 2개 (user_new_project / direction_renarrow)
```

### 5.2 cross-reference 정합 (manual checklist, Slice 5)

```
- branching_rules 의 mode='discovery'/'discovery_from_stepN' → discovery_flow.md §N 존재 확인
- branching_rules 의 mode='quick' → quick_flow.md 존재 확인
- override_rules 의 trigger 컴포넌트 → component_map.md 엔트리 존재 확인 (AppShell / DirectionApprovalCard 등)
```

---

## 6. Phase 별 진화

| Phase | 변경 |
|---|---|
| Phase 2 (현재) | yaml spec only (본 파일 + cross-reference) |
| Phase 3 | Next.js middleware (`/new` route) yaml 해석 + 라우팅 구현 |
| Phase 4 | backend `/api/v1/plans/start` endpoint (api_contract §8.1) 가 mode 반환 + 본 yaml은 backend 정합 reference |
| Phase 9 | 실 데이터 기반 임계값 조정 (예: `series.count >= 2`일 때 quick 더 강조, rule priority 재조정) |
| Phase 11+ | 다국어 / advanced setting UI (user_quick_force trigger 활성) |

---

## 7. 변경성 (replaceability_score.md §3.3 정합)

| 변경 | 영향 파일 | 비용 |
|---|---|---|
| 임계값 변경 (count 숫자만) | `mode_branching.md` 1줄 (yaml) | L |
| 새 branching_rules 추가 (예: rule_brand_no_domain) | `mode_branching.md` (branching_rules 배열 +1) | L |
| 새 override_rules 추가 | `mode_branching.md` (override_rules 배열 +1) | L |
| 새 mode 자체 추가 (예: hybrid) | `mode_branching.md` + 새 flow.md (`hybrid_flow.md`) + `page_map.md` 갱신 | H |
| 분기 polling/condition logic 자체 변경 | `mode_branching.md` + backend (Phase 4+ 구현 영역) | M |
| Mode 자동 분기 자체 폐기 (사용자 항상 선택) | `mode_branching.md` 삭제 + `page_map.md` + Phase 3 라우팅 재설계 | H |

---

## 8. Open Questions (Phase 3 진입 전 확정 권장)

1. `discovery_from_stepN` 구현 정밀도 — Phase 3 진입 시 Step 1/2 prefill 자동 vs 사용자 확인 1회
2. `rule_has_series` 임계값 — `series.count >= 1` 즉시 quick vs `>= 2`부터 (Phase 9 실 데이터 후 결정)
3. `direction_renarrow` 진입 시 Step 시작점 — Step 1 (Brand부터 전부) vs Step 3 (Series부터, Brand는 유지) — Phase 3 UX 테스트 후 결정
4. priority 수치 vs 정성 우선순위 — 현재 1/2/3/99 4단계. 더 세분화 필요 시 5/10/15 간격 권장
5. Mode 명시 토글 (user_quick_force) UI 활성 시점 — Phase 11+ Settings advanced vs MVP에서 hidden flag

---

## 9. 변경 이력

- 2026-05-27: Phase 2 Slice 4 — mode_branching.md 최초 작성 (branching_rules 4개 + override_rules 3개 + 매핑 표 + replaceability L baseline)
