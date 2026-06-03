# agent-io-check — Phase 15 S4 (Critic P-007 v1.3.0 director, CC-019)

- 일자: 2026-06-03 | 대상: Critic (P-007) | 판정: **PASS (발견 0)**

## 차이 식별
```
contract: prompt_registry §8 P-007 v1.3.0 + output_schema §9 CriticEvaluation.dimensions(자유 dict)
구현    : critic.py DIMENSIONS_DIRECTOR(10) + DIRECTOR_SYSTEM_PROMPT + run_critic output_mode 분기
match   : compact 8 / rich 9 / director 10 — 구현↔registry 일치
extra   : 0 / missing: 0 / type_diff: 0
```
- retention_design = director 10번째 차원, gated(output_mode=director). dimensions 자유 dict → additive(스키마 위반 아님).
- canonical 0–1(ADR-018) 불변 — normalize_to_canonical/verdict 식 구조 동일, 차원 집합만 교체.

## 소비자 회귀 0
- select_best_plan_index / normalize_to_canonical: dimensions dict 소비 — 10키 additive 무영향.
- compact/rich(8/9차원) 경로 byte-identical (effective_output_mode 매핑). pytest 531→536.

## 후속
- contract 변경: prompt_registry P-007 v1.3.0(반영 완료). retention_design 실 LLM anchor 채점 = S6.
