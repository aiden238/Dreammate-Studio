# Phase 32 — acceptance

| # | 기준 | 측정 | 통과선 |
|---|---|---|---|
| A1 | cross/consensus 배선(gated) | plotter 코드+테스트 | OFF=현행 byte-identical, 키 부재 graceful |
| A2 | 편향 차단 효과 | plotter 골든셋 | cross/consensus false-approve ≤ in-provider |
| A3 | 비용 | 일일 가드(NF-M01) | 가드 내 |
| A4 | 직교 합산(게이트∘judge) | Dreammate 측정(Phase 33 S2) | 게이트∘judge가 단독보다 false-approve↓(또는 동률) |

## 통과 조건
- A1(배선) = plotter 적용. A2/A3 = plotter 실측(opt-in 비용). A4 = Dreammate 직교 검증(R2).
- ★ 한계: 방향성(Dreammate N=10·rater A N=1, κ 미산출) — plotter 적용 전 rater B/κ 권장.
