# Critic Calibration A/B — Human Blind 채점 예비 결과 (rater A, N=1)

> 2026-06-15 · ★ **예비**(채점자 1명=운영자 A). 정식 2명(inter-rater κ 포함)은 팀원(rater B) 채점 후
> `scripts/analyze_blind_ab.py --key ... --rater A --rater B` 로 재산출.
> 데이터: `eval/human_review/2026-06-15-calib-ab-{cases,key}.json` + `-scores-A.json`.

## 1. 설정
- 10케이스(정상 5 = golden_set 도메인 / 얕은 5 = 의도적 빈약 입력), output_mode=director.
- 같은 추천 기획안 1개를 Critic 2번 채점: **A0**(calibration OFF, 현 default) / **A1**(calibration ON: anti-optimism 프리앰블 + per-axis 게이트). LLM=gpt-4o-mini 생성 / gpt-4o critic.
- 사람: blind(Critic 점수 미노출) 5차원 0~5 + depth 0~1. human_avg = 5차원 평균.
- ★ 사전 동결 임계: false-approve = critic verdict=approve AND human_avg < 3.0.

## 2. 통제
Arm 간 차이 = **`critic_calibration_enabled` flag 1개**(env override + cache_clear). planning·plan 동일 — 같은 기획안을 채점만 다르게.

## 3. 결과표
| case | kind | human/5 | A0 | A1 | \|A0−H\| | \|A1−H\| |
|---|---|---|---|---|---|---|
| GS-001 | normal | 2.6 | 4.5 approve | 4.0 approve | 1.9 | 1.4 |
| GS-002 | normal | 2.8 | 4.6 approve | 4.1 approve | 1.8 | 1.3 |
| GS-003 | normal | 1.8 | 4.4 approve | 4.2 approve | 2.6 | 2.4 |
| GS-004 | normal | 1.6 | 4.2 approve | 3.8 approve | 2.6 | 2.2 |
| GS-005 | normal | 2.6 | 4.5 approve | 4.1 approve | 1.9 | 1.5 |
| SHALLOW-1 | shallow | 2.6 | 4.5 approve | 4.2 approve | 1.9 | 1.6 |
| SHALLOW-2 | shallow | 2.0 | 4.4 approve | 4.0 approve | 2.4 | 2.0 |
| SHALLOW-3 | shallow | 1.8 | 4.3 approve | 3.9 approve | 2.5 | 2.1 |
| SHALLOW-4 | shallow | 2.0 | 4.5 approve | 4.3 approve | 2.5 | 2.3 |
| SHALLOW-5 | shallow | 2.0 | 4.6 approve | 4.4 approve | 2.6 | 2.4 |

**종합**: 사람 평균 **2.18/5**(≈44점) · A0 **4.45/5**(≈89점) · A1 **4.10/5**(≈82점).

## 4. 핵심 지표
- ★ **false-approve율: A0 = 10/10 (100%) · A1 = 10/10 (100%)** — calibration이 단 1건도 approve→revise로 못 뒤집음.
- **Judge-사람 괴리** `mean(|critic−human|)`: A0 **2.27** → A1 **1.92** (**−0.35, 15%↓**). 과교정 0(정상셋 2.16→1.76, 얕은셋 2.38→2.08 둘 다 개선).

## 5. 핵심 발견 + 메커니즘
1. **88점 함정 정량 확정**: Critic 89점 vs 사람 44점 = **45점 괴리**. Critic 전수 approve, 사람 전수 "보통 이하".
2. **calibration(A1) = 부분 효과**: 점수를 사람 쪽으로 0.35 당기고 과교정 없음. 그러나 **verdict는 0건도 안 바뀜** → director 모드는 *얕은 입력에서도 깊은 plan을 생성*해 per-axis 게이트(depth/retention<3)가 안 걸림 → approve 게이트 못 넘음.
3. **정성(사람 코멘트)**: COT 발전 / 딥리서치 레퍼런스 / 2nd brain 브랜딩 / "너무 템플릿·단조로움" — critic이 못 보는 깊이 결핍을 일관 지적.

## 6. 판정 + 다음
- **판정**: calibration(프롬프트 + per-axis gate) 단독으론 **verdict를 못 바꿈 = false-approve 100% 잔존**. 점수 보정만 됨.
- **→ 후속 (데이터가 정당화)**: **L3 결정적 깊이 게이트**(plotter식 — LLM 점수 재량 박탈, 비-LLM 계산으로 approve 상한 강제) + **cross-provider 독립 Judge**(OpenAI 생성 → Claude 채점, self-review 편향 차단). 둘 다 같은 10개 plan + 같은 사람 점수에 대보면 됨(재채점 0).
- **한계**: N=1 rater 예비(κ 미산출), N=10 소표본 → 방향성 1차. 팀원 채점(rater B) 후 inter-rater κ + 정식 리포트.
