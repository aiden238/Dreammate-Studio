# Phase 23 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- golden_set 25 케이스(GS-001~025) + load_golden_set(eval/golden_set_loader) 파싱. 케이스에 input/priority(P0/P1/P2)/mode.
- depth_actionability = critic 9차원(rich 모드, 0~5) — 실 LLM 채점(mock 미채점). run_planning(rich) + run_critic 재사용.
- 실 LLM 경로: .env(backend/fastapi) OPENAI_API_KEY + run_planning/run_critic 직접 호출(Temp/ 패턴, run_ab/run_commercial_verify 계승).
- **audit_naming 통과 (2026-06-04, 0 drift)**.
### 1.2 불확실
- U1 비용 — 25케이스×(planning+critic)=~50호출 ~$0.3~0.5. 케이스당 1안(rich)으로 통제.
- U2 일부 케이스 LLM 응답 변동/실패 → graceful per-case skip + 리포트 명시.
- U3 human↔LLM 대조는 사람 채점 n 부족 → 본 phase 는 대조 시트 준비(실채점 deferred).

## 2. Simplest Slice (3회 압축)
```
1차: 전수 baseline + human kit + 대조 + close.
2차: 전수 25 실 LLM baseline 리포트; human kit 정비는 S2.
3차: golden_set 로드 → 케이스당 rich planning + critic → 점수 수집 → 집계 리포트.
     ← S1 = 실 LLM 전수 baseline(Temp 러너 + 리포트).
```
→ S1(실 LLM 전수 baseline) → S2(human kit LLM-judge 대조 + 실채점 시트 + close).

## 3. Surgical Scope
- editable: Temp/run_eval_baseline.py(신규, gitignore) + eval/regression_results/(리포트) + eval/human_review/(대조 시트) + phase/state/meta.
- read-only: backend/fastapi/* 운영 코드(호출만, 0 수정) / golden_set.md(측정만).
- forbidden: 운영 코드 변경 / mock CI real 전환 / golden_set 케이스 변경 / 가중치 변경 / archive.

## 4. Verification
- S1: 25 케이스 전수 실행(graceful) + 리포트 — overall/depth 분포 + P0 pass + 광고/차단 0 + verdict 분포. behavior-preserving(운영 코드 0 → pytest 714 불변).
- S2: LLM-judge 대조 시트(2 케이스 compact/rich + 실 critic 9차원) + 사용자 채점 시트.
- 각 슬라이스: pytest 714 + scenario_sim 36 + audit 0.
