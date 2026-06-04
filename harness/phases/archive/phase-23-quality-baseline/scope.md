# Phase 23 — Scope

## 포함 (build)
- **S1 실 LLM 전수 baseline** (제가 실행):
  - Temp/ 러너 — golden_set 25 케이스 로드(load_golden_set) → 각 케이스 `OUTPUT_MODE=rich` 실 planning(run_planning) + 실 critic(run_critic, 9차원 depth 포함) → 점수 수집.
  - 집계: per-case overall_score_avg + depth_actionability + verdict + 광고/차단 검사. priority(P0/P1/P2)별 pass + 전체 분포(mean/min/max).
  - 리포트: `eval/regression_results/2026-06-04_phase-23-real-baseline.md` (커밋 — 영구 baseline).
  - ★ 비용 ~$0.3~0.5(50 호출). 1회 실행.
- **S2 human review 정비**:
  - Phase 12 S4 kit(compact vs rich 2케이스)에 **LLM-judge 점수 컬럼** 추가(같은 케이스 실 critic 9차원) → human↔LLM 대조 준비.
  - 사용자 실채점 시트(5+1차원, human_review_rubric §2) 정비 — ★ 실채점은 사용자(deferred).
  - phase-complete.

## 예상 파일 변경
```
editable:
  Temp/run_eval_baseline.py (신규, gitignore — 실행만)
  eval/regression_results/2026-06-04_phase-23-real-baseline.md (신규 리포트)
  eval/human_review/2026-06-04_phase-23-s4-judge-compare.md (신규 — LLM-judge 대조 + 채점 시트)
  phase/state/meta
read-only:
  운영 코드(backend/fastapi/*) — 0 수정(eval 은 호출만)
forbidden:
  운영 코드 변경 / golden_set 케이스 변경(채번 고정) / mock CI 경로 변경 / 자동 CI real 전환 / archive
```

## 검증
- behavior-preserving: 운영 코드 0 수정 → 기존 pytest 714 green + scenario_sim 36 + audit 0.
- S1: 25 케이스 전수 실행(graceful per-case) + 리포트(점수 분포 + P0 pass + 광고/차단 0).
- S2: LLM-judge 대조 시트 + 사용자 채점 시트(실채점 deferred).
