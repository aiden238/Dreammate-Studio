# Phase M3 — Multi-Slice Plan

> 2 Slice dry-run (sub-agent, sequential) + assess + doc-sync(main). 총 2.5~3.5h. dry-run outputs/TEST/ only + 런타임 0.

## Wave 구조
```
entry (main) : 8 phase 파일
  ↓
S1 [generation — 개선 machinery 로 재무 harness 생성]   (sub-agent, outputs/TEST/finance)
  ↓
S2 [validation + M2 G1~G8 실사용 점검 + 범용성 판정 + 새 GAP + 분기 권고]  (sub-agent, outputs/TEST/)
  ↓
assess (main): S2 종합 → 분기 (새 GAP 없음 → Phase 10 기획 / 있음 → 백로그+후속)
  ↓
doc-sync (main): retrospective + patterns + skill_usage_log + state + archive (별도 commit)
```

## Slice S1 — generation (~1~1.5h, sub-agent)
1. without baseline 먼저 (machinery 미참조 naive 재무 하네스) → `outputs/TEST/finance/_without_baseline.md`
2. domain_brief (domain_brief_schema **개선본**: data_model G6 = User→Household→FinancialGoal→Plan→Allocation + 제3자 PII risk G5 = 부양가족/수익자 + forbidden_scope = 투자권유/원금보장/상품추천/세무·법률자문 금지) → `finance/domain_brief.md`
3. generation_workflow 11단계(G2 결정트리 포함) → harness_blueprint (architecture_patterns G1 결정기준으로 목표유형별 expert vs 단일 결정 + validation pending-by-design G8) → `finance/harness_blueprint.md`
4. 6 scaffold (templates 개선본 — agent conditional_execution G3=부양가족/부채 조건 / eval applies_when G4=세금모드 / project_state harness_status G7) → `finance/scaffolds/*`
5. P-X1 + commit (`feat(meta-m3): S1 finance harness generation (개선 machinery)`)
- editable: `meta_factory/outputs/TEST/finance/**`
- ★ forbidden: 그 외 전부 (machinery 개선본 읽기만, podcast 산출물 보존, 런타임 0)

## Slice S2 — validation + 범용성 (~1~1.5h, sub-agent)
1. 6검증 (PASS/FAIL/PENDING/PENDING-BY-DESIGN/GAP) — 검증3 조건부산출(G3 행사) / 검증5 eval-run(pending-by-design G8)
2. ★ **M2 G1~G8 실사용 점검표** — 각 사용됨/유효/부적합 + 이질 도메인 적합도 (A3)
3. 범용성 판정 (A5) — 미디어 편향(창의 hook/3-variant/썸네일 강요) 유무 + 재무 적합도 (범용 강함/부분/약함)
4. 새 GAP 검출 (A6) — 범용성 한계. 있으면 목록 + 보완 방향(반영 X), 없으면 "0" 근거
5. with/without 보조 (누락률) + 종합 분기 권고 (A7 — "추가 필요" or "없음 → Phase 10")
6. → `outputs/TEST/sample_test_finance_validation.md`
7. P-X1 + commit (`feat(meta-m3): S2 finance validation + M2 개선 점검 + 범용성 판정`)
- editable: `meta_factory/outputs/TEST/` (validation 리포트 + finance blueprint validation 필드 소폭)
- ★ forbidden: S1 동일 (machinery 읽기만)

## assess (main 세션)
- S2 종합 분기 권고 검토 → **새 GAP/반영/수정 없음**: Phase 10 entry 기획 진입 / **있음**: 백로그 기록 + 사용자 보고 후 결정.

## doc-sync (main, 별도 commit)
- `meta/retrospectives/phase-M3.md` + patterns(P-X1 57 + P-META-FACTORY-002 범용성 2차 update) + skill_usage_log(harness-factory 세 번째 실 트리거) + PROJECT_STATE/PHASE_REGISTRY + closing_notes + archive. (ADR-038 = 분기 결과에 따라 선택)

## 충돌 매트릭스
| Slice | TEST/finance | TEST/validation | meta/state |
|---|---|---|---|
| S1 | ✅ | ❌ | ❌ |
| S2 | (blueprint 소폭) | ✅ | ❌ |
| doc-sync | ❌ | ❌ | ✅ |
Sequential 충돌 0.

## 누적 P-X1
| Phase | streak |
|---|---|
| M2 | 55 |
| M3 | +2 (S1·S2) |
| 누적 | **57** |

## 시간
entry 0.3h + S1 ~1.25h + S2 ~1.25h + assess/doc-sync ~0.5h = **~3.3h**
