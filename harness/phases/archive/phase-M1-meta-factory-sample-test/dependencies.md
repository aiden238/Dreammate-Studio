# Phase M1 — Dependencies

## 선행 phase
- **Phase M0 (ADR-035)** 완료 — meta_factory machinery 가 존재해야 함 (본 phase 는 그 실행).

## machinery 의존 (읽기 — 입력)

| 의존 | 역할 (M1 에서) |
|---|---|
| `meta_factory/domain_brief_schema.md` | S1 — 팟캐스트 domain_brief 작성 형식 |
| `meta_factory/generation_workflow.md` (11단계) | S1 — blueprint 생성 절차 |
| `meta_factory/harness_blueprint_schema.md` | S1 — blueprint 출력 형식 (validation 3필드) |
| `meta_factory/architecture_patterns.md` (6 패턴) | S1 — 팟캐스트에 맞는 패턴 선택 (Pipeline/Supervisor 등) |
| `meta_factory/templates/*_template.md` (6) | S1 — 6 scaffold draft 기반 |
| `meta_factory/validation_workflow.md` (6 검증) | S2 — blueprint 검증 절차 |
| `meta_factory/blueprints/dreammate_current_harness_blueprint.md` | S2 G6 — 현재 하네스 5 gaps 재현 여부 비교 기준 |
| `meta_factory/factory_contract.md` (8 규칙) | S1·S2 — proposal-first / 런타임 미변경 / outputs 격리 |

## Skill 의존 (절차 — 읽기)

| Skill | 역할 |
|---|---|
| `harness-factory` (#21, proposal-only) | S1·S2 진입 — meta_factory machinery 절차 트리거 (★ 첫 실트리거) |
| `eval-run` (#6) | S2 검증 5 — golden_set 회귀/임계값 절차 (§3~§6 cross-ref, `eval-run > harness-factory validation`) |
| `.claude/skills/INDEX.md` | S2 검증 2 — Skill 키워드 충돌 규칙 + 우선순위 표 |
| `contract-change` (#3) | S2 검증 3 — contract cross-ref 정합 정신 |

## 도메인 입력 (외부 지식)
- 팟캐스트 에피소드 기획 도메인 상식: 에피소드 포맷(인터뷰/솔로/패널), 오프닝 훅·질문 설계, 세그먼트 구성, 게스트 브리프, 쇼노트, 시리즈/시즌 구조. (영상기획과 공통: 브랜드/타깃/톤/후킹/시리즈. 차이: 시각자료→대화흐름, 썸네일→오프닝 멘트.)

## 산출물 소비자 (후속)
- `meta/retrospectives/phase-M1.md` (별도 doc-sync) — GAP 요약.
- 다음 meta-phase / Phase 10+ — improvement_reports 의 GAP 을 machinery 보강 입력으로.

## 비의존 (격리 확인)
- product runtime / DB / 기존 contract / 기존 Skill 본문 변경에 **의존하지 않음** (전부 읽기). → 회귀 위험 0 (A9/MG1).
