# Phase M2 — Dependencies

## 선행 phase
- **Phase M0 (ADR-035)** — meta_factory machinery 존재 (M2 가 개선할 대상).
- **Phase M1 (ADR-036)** — 8 GAP 발견 (M2 의 입력 = `outputs/TEST/sample_test_podcast_validation.md §D`).

## 입력 (proposal 출처 — 읽기)

| 의존 | 역할 (M2 에서) |
|---|---|
| `meta_factory/outputs/TEST/sample_test_podcast_validation.md §D` | ★ 8 GAP proposal 원천 (G1~G8 + 보완 1줄씩). M2 는 이를 검토 → 승인 → 반영 |
| `meta/retrospectives/phase-M1.md` | GAP 핵심 3 (G2/G3/G5) + 백로그 표 |
| `meta_factory/outputs/TEST/podcast/*` | 재검증 대상 (개선 machinery 재적용 — before/after) |

## 변경 대상 (machinery — editable)

| 파일 | GAP | Slice |
|---|---|---|
| `meta_factory/generation_workflow.md` | G2 | S1 |
| `meta_factory/architecture_patterns.md` | G1 | S1 |
| `meta_factory/domain_brief_schema.md` | G5, G6 | S1 |
| `meta_factory/templates/agent_template.md` | G3 | S2 |
| `meta_factory/templates/contract_template.md` | G3 | S2 |
| `meta_factory/templates/eval_template.md` | G4 | S2 |
| `meta_factory/templates/project_state_template.md` | G7 | S2 |
| `meta_factory/harness_blueprint_schema.md` | G8 | S2 |

## Skill 의존 (절차)

| Skill | 역할 |
|---|---|
| `contract-change` (#3) | ★ machinery = L3 contract → 8 변경 절차 (CC-007). proposal → 검토 → 승인 → 반영 → 로그 |
| `harness-factory` (#21) | S3 재검증 — 개선 machinery 로 validation_workflow 재적용 (M1 두 번째 트리거) |
| `eval-run` (#6) | S3 재검증 5 — 절차 적용성 cross-ref (실측은 여전히 미수행 — NG11) |
| `multi-llm-validation` (#13) | entry — formal self 아홉 번째 (8 GAP 반영 타당성 + backward-compat) |
| `meta-retrospective` (#9) | doc-sync 회고 |

## 정합 의존 (cross-ref — backward-compat 점검)
- `validation_workflow.md` 6검증이 개선된 schema/template 을 여전히 참조 가능해야 함 (additive → 깨짐 0).
- `harness_blueprint_schema.md`(G8 enum 추가) ↔ `validation_workflow.md` §판정 종합 (pending 표현) 정합.
- `domain_brief_schema.md`(G6 data_model) ↔ `generation_workflow.md` 단계1~2(domain_brief 수집) 정합.

## 비의존 (격리)
- product runtime / DB / 기존 product contract / 기존 Skill 본문에 **비의존** (전부 비변경) → 회귀 위험 0 (A9). pytest 339 무관.
