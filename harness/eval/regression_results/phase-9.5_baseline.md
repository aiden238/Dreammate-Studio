# Eval Run: phase-9.5_baseline

- 트리거: phase-9.5_baseline
- 모드: mock (mock-deterministic — 실 LLM 미호출, 비용 0)
- 케이스 수: 11
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

## 임계값 점검 (eval-run §6)

- schema 준수율 < 100%: PASS
- 광고 표현 검출 > 5%: PASS
- 차단 단어 검출 > 0%: PASS
- P0 통과율 < 100%: PASS

## 결정

pass

## 후속 액션

- canonical-only 품질 baseline 확정 (Slice 4 Critic deprecated 0–5 제거 검증 기준).
