# Phase M3 — Dependencies

## 선행 phase
- **M0** machinery skeleton / **M1** dry-run 방법(TEST 격리 + 4상태 + with/without) / **M2** machinery 개선(G1~G8) — M3 는 **개선본**으로 M1 방법을 이질 도메인에 재적용.

## 입력 (읽기)
| 의존 | 역할 |
|---|---|
| `meta_factory/generation_workflow.md` (G2 결정트리) | S1 — 생성 절차 (개선본) |
| `meta_factory/architecture_patterns.md` (G1 결정기준) | S1 — 패턴 선택 (재무 목표유형별 expert vs 단일) |
| `meta_factory/domain_brief_schema.md` (G5 제3자 PII + G6 data_model) | S1 — 재무 brief (개선 필드 활용) |
| `meta_factory/harness_blueprint_schema.md` (G8 pending-by-design) | S1 — blueprint 형식 |
| `meta_factory/templates/*` (G3 conditional_execution / G4 applies_when / G7 harness_status) | S1 — scaffold (개선 슬롯 활용) |
| `meta_factory/validation_workflow.md` (6검증) | S2 — 검증 |
| `meta_factory/outputs/TEST/sample_test_podcast_revalidation.md` | S2 — M2 개선 적용 사례 비교 baseline |
| `eval-run` SKILL §3~§6 | S2 검증5 (절차 적용성 — pending-by-design) |
| `.claude/skills/INDEX.md` | S2 검증2 (Skill 충돌) |

## Skill 의존
- `harness-factory` (#21) — S1·S2 진입 (★ 세 번째 실 트리거).
- `eval-run` (#6) — S2 검증5.
- `meta-retrospective` (#9) — doc-sync 회고.

## 도메인 입력 (외부 지식)
- 개인 재무 플래닝: 재무 목표 유형(저축/부채상환/투자배분/은퇴/비상금), 예산·현금흐름, 리스크 허용도, 부양가족/수익자, 규제 경계(투자권유·원금보장·특정상품추천 금지). 미디어와 공통: planning + 3안 + 검토. 차이: 수치/규제/적합성, 창의 hook 부재.

## 산출물 소비자
- doc-sync retrospective + (분기) Phase 10 entry 또는 새 GAP 백로그.

## 비의존 (격리)
- product runtime / DB / 기존 contract / Skill 본문 / machinery 변경에 비의존 (전부 읽기/outputs/TEST/) → 회귀 0 (A9). pytest 339 무관.
