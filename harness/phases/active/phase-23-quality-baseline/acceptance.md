# Phase 23 — Acceptance

```
A1. S1 러너 — golden_set 25 로드 + 케이스당 실 rich planning + 9차원 critic. graceful per-case(실패 skip+명시).
A2. S1 baseline 리포트 — overall_score 분포(mean/min/max) + depth_actionability 분포 + verdict(approve/revise/reject) + priority(P0/P1/P2) pass + 광고/차단 violation. eval/regression_results 커밋.
A3. behavior-preserving — 운영 코드 0 수정 → 기존 pytest 714 green + scenario_sim 36/36 + audit 0.
A4. S2 human kit 대조 — Phase 12 S4 kit 2케이스에 LLM-judge(실 critic 9차원) 컬럼 + 사용자 채점 시트(5+1차원). 실채점=사용자(deferred).
A5. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A2 | 실 LLM 전수 실행 + 리포트(점수 분포/P0/광고차단) |
| A3 | pytest 714 baseline + scenario_sim 36 + audit 0 (운영 코드 0) |
| A4 | LLM-judge 대조 시트 + 사용자 채점 시트 |
