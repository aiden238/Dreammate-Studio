# Eval Run: phase-10_baseline

> Phase 10 Slice 3 eval 정식화 baseline (CC-009). golden_set 11 → 15 확대 후 첫 mock 회귀.
> 실 LLM mode 는 capability 만 wire (default mock — 본 run 도 mock, 실 호출 0).
> 비교: phase-9.5_baseline (11 케이스) 대비 schema/pass/gate/revise 동일 + GS-012~015 4 케이스 추가 전부 pass.

- 트리거: phase-10_baseline
- 모드: mock (mock-deterministic — 실 LLM 미호출, 비용 0)
- 케이스 수: 15
- 비교 대상: canonical-only baseline (ADR-033 / ADR-034 안전망)

## 요약 점수

| 지표 | 값 |
|---|---|
| schema 준수율 | 100.0% |
| 케이스 통과율 | 100.0% |
| structural 평균 | 1.0 |
| 광고 표현 검출율 | 0.0% |
| 차단 단어 검출율 | 0.0% |
| P0 통과율 (7 케이스) | 100.0% |

## 케이스별 결과

| case_id | priority | schema | structural | 광고 | 차단 | 결과 |
|---|---|---|---|---|---|---|
| GS-001 | P0 | ok | 1.0 | - | - | pass |
| GS-002 | P0 | ok | 1.0 | - | - | pass |
| GS-003 | P0 | ok | 1.0 | - | - | pass |
| GS-004 | P0 | ok | 1.0 | - | - | pass |
| GS-005 | P0 | ok | 1.0 | - | - | pass |
| GS-006 | P0 | ok | 1.0 | - | - | pass |
| GS-007 | P1 | ok | 1.0 | - | - | pass |
| GS-008 | P1 | ok | 1.0 | - | - | pass |
| GS-009 | P1 | ok | 1.0 | - | - | pass |
| GS-010 | P0 | ok | 1.0 | - | - | pass |
| GS-011 | P2 | ok | 1.0 | - | - | pass |
| GS-012 | P1 | ok | 1.0 | - | - | pass |
| GS-013 | P1 | ok | 1.0 | - | - | pass |
| GS-014 | P1 | ok | 1.0 | - | - | pass |
| GS-015 | P2 | ok | 1.0 | - | - | pass |

## 임계값 점검 (eval-run §6)

- schema 준수율 < 100%: PASS
- 광고 표현 검출 > 5%: PASS
- 차단 단어 검출 > 0%: PASS
- P0 통과율 < 100%: PASS

## revise effect

revise loop 개선 효과 (mock-based, canonical overall_score 0–1 delta). regressed_rate = revise 후 점수 하락 비율 (Phase 4.5 우려 검증 지표).

| 지표 | 값 |
|---|---|
| 평균 delta (mean_delta) | 0.092 |
| 개선율 (improved_rate) | 60.0% |
| 악화율 (regressed_rate) | 20.0% |
| 무변화율 (no_change_rate) | 20.0% |
| plan 수 (n) | 5 |

| # | initial | final | delta | direction | revised |
|---|---|---|---|---|---|
| 0 | 0.62 | 0.81 | 0.19 | improved | 1 |
| 1 | 0.55 | 0.79 | 0.24 | improved | 2 |
| 2 | 0.84 | 0.84 | 0.0 | no_change | 0 |
| 3 | 0.74 | 0.69 | -0.05 | regressed | 1 |
| 4 | 0.58 | 0.66 | 0.08 | improved | 2 |

## 결정

pass

## 후속 액션

- canonical-only 품질 baseline 확정 (Slice 4 Critic deprecated 0–5 제거 검증 기준).
