# B1 Specificity-Amplification Rewrite — B0 vs B1 (same Claude judge, claude-sonnet-4-6)

- intervention: specificity_amplification_rewrite  | rewriter: gpt-4o  | judge: claude-sonnet-4-6 temp=0.1
- n=10  failures=0  schema_guard=enforced  output_mode=director
- B0 mean=2.710 → B1 mean=3.040  (Δ=+0.330)  | human rater A mean=2.18 (reference)

## Per-case overall + verdict

| case_id | kind | B0 overall | B1 overall | Δ | B0 verdict | B1 verdict | shift |
|---|---|---|---|---|---|---|---|
| GS-001 | normal | 2.80 | 3.10 | +0.30 | revise | revise | none |
| GS-002 | normal | 2.90 | 3.00 | +0.10 | revise | revise | none |
| GS-003 | normal | 3.00 | 3.30 | +0.30 | revise | revise | none |
| GS-004 | normal | 2.30 | 3.00 | +0.70 | reject | revise | reject→revise |
| GS-005 | normal | 2.90 | 3.30 | +0.40 | revise | revise | none |
| SHALLOW-1 | shallow | 2.50 | 2.90 | +0.40 | revise | revise | none |
| SHALLOW-2 | shallow | 2.40 | 3.20 | +0.80 | reject | revise | reject→revise |
| SHALLOW-3 | shallow | 2.50 | 3.00 | +0.50 | revise | revise | none |
| SHALLOW-4 | shallow | 2.90 | 2.90 | +0.00 | revise | revise | none |
| SHALLOW-5 | shallow | 2.90 | 2.70 | -0.20 | revise | revise | none |

## Floor axes (raw 0~5, mean B0→B1)

| axis | B0 mean | B1 mean | Δ |
|---|---|---|---|
| differentiation | 1.90 | 2.10 | +0.20 |
| hook_strength | 1.90 | 2.70 | +0.80 |
| retention_design | 2.20 | 2.30 | +0.10 |
| target_clarity | 2.30 | 2.70 | +0.40 |

## Per-case core dims (raw 0~5): differentiation / hook_strength / retention_design

| case_id | diff B0→B1 | hook B0→B1 | retention B0→B1 |
|---|---|---|---|
| GS-001 | 2→2 | 2→3 | 2→2 |
| GS-002 | 2→2 | 2→3 | 2→2 |
| GS-003 | 2→3 | 2→4 | 2→2 |
| GS-004 | 2→2 | 1→2 | 2→2 |
| GS-005 | 2→2 | 2→3 | 2→3 |
| SHALLOW-1 | 1→2 | 2→2 | 2→2 |
| SHALLOW-2 | 2→2 | 2→3 | 2→3 |
| SHALLOW-3 | 2→2 | 2→2 | 2→2 |
| SHALLOW-4 | 2→2 | 2→2 | 3→3 |
| SHALLOW-5 | 2→2 | 2→3 | 3→2 |

## Aggregate

- verdict B0: {'approve': 0, 'revise': 8, 'reject': 2}
- verdict B1: {'approve': 0, 'revise': 10, 'reject': 0}
- approve 신규: 0  | reject→revise: 2  | verdict 상향(총): 2
- per-dim mean Δ: intent_fit=+0.40, target_clarity=+0.40, hook_strength=+0.80, message_clarity=+0.60, structure=+0.10, feasibility=+0.00, brand_consistency=+0.60, differentiation=+0.20, depth_actionability=+0.10, retention_design=+0.10

## Note (measurement integrity)
- 단일 변인 = specificity-amplification rewrite. judge/입력/output_mode=director/스키마/temp(0.1) 동일.
- B0 점수는 2026-06-15-calib-ab-claude.json(동일 judge) 재사용. B0 평균 2.71·verdict(approve0/revise8/reject2) 일치 확인.
- 1차 실행 시 5 case 가 judge 출력 절단(max_tokens=2000)으로 실패 → 동일 judge·동일 산식, 출력 버짓만 4000 으로 상향해 재채점(B1 plan 동일 rewriter 재생성). 산식·프롬프트 byte-identical.
