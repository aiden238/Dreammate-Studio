# Phase 33 S2 — 결정적 게이트 ∘ cross-provider judge 직교 합산 (10케이스, LLM 0)

> 재현: `python scripts/phase33_gate_judge_measure.py`. 연구 arc 원래 후속(calib-ab-preliminary.md:43)
> = "결정적 깊이 게이트 + cross-provider judge를 같은 10 plan + 같은 사람 점수에 대본다."
> 게이트=결정론(비-LLM)이라 기존 데이터 재사용 → **신규 LLM 콜 0**. judge 결과(calib-ab-claude.json)·사람 점수(scores-A.json) 재사용.

## 설정
- 10케이스(director plan, 정상5+얕은5). 사전동결: false-approve = approve ∧ human_avg < 3.0. 사람 전수 <3(나쁜 plan 10/10).
- 게이트 = `critic_pacing_gate`(payoff 마지막 beat > 30% → 차단). judge = cross-provider Claude(검증분).

## 결과

| 층 | false-approve | 비고 |
|---|---|---|
| in-provider critic (A0) | **10/10** | 전수 approve(88점 함정) |
| **결정적 게이트 단독** | **9/10** | 게이트가 **SHALLOW-4 1건 무-LLM 결정론 차단** |
| **cross-provider judge 단독** | **0/10** | 전수 revise/reject(8 revise·2 reject) |
| **게이트 ∘ judge** | **0/10** | — |

## 직교성
- **게이트 차단(구조/pacing)**: `SHALLOW-4` — payoff bloat을 plan 구조에서 직접 검출(LLM 점수 무관).
- **judge 차단(점수 낙관)**: 10건 전부(SHALLOW-4 포함) — self-review 편향이 다른 provider blind-spot으로 깨짐.
- → 두 층은 **직교**: 게이트는 *구조 붕괴*, judge는 *점수 낙관*을 잡는다.

## 판정
- **convergence 설계 입증**: "결정적 게이트 + cross-provider judge" 둘 다 작동. **judge가 강한 closer**(0/10), **게이트는 무-LLM 저비용 직교 층**.
- **본 데이터셋 한계**: judge가 전수 차단(SHALLOW-4도 score로 잡음) → 게이트의 *marginal-over-judge = 0*. 게이트의 가치 = ① **무-LLM 결정론 차단**(API 0, provider 장애·키 부재에도 작동) ② **defense-in-depth** ③ calibration이 못한 "approve 상한 강제". pacing 결함이 더 많은 셋에선 게이트 차단↑(LLM 콜 절감).
- ★ 방향성(N=10·rater A N=1·κ 미산출). plotter 골든셋·rater B로 재현 권장.

## 시사 (양 프로젝트)
- plotter: 결정적 게이트(structure_pacing_issues) ✅ 보유 → cross-provider judge(Phase 32)만 추가하면 풀세트.
- Dreammate: cross-provider judge ✅ + 게이트(Phase 33 S1) ✅ → 풀세트 보유. default 활성은 prompt-version-review(major).
