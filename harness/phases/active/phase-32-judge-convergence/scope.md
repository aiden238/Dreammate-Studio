# Phase 32 — scope

## Slices
- **S1 (plotter ADR)** ✅ 초안완료: `meta/proposals/plotter-draft/ADR-0033-cross-provider-judge.md` — cross-provider judge 재고 + consensus-min(gated).
- **S2 (plotter 배선)** ✅ 초안완료 / 🔄 적용 대기: `meta/proposals/plotter-draft/validator-cross-judge.patch.md` — `models.py` cross-judge 매핑 + `CRITIC_CROSS_JUDGE` flag, `validator.py` consensus-min(in-provider ∧ cross). plotter repo 적용·테스트는 user 협조(R3에서 clone 구현 시도).
- **S3 (측정)** 🔄: plotter 골든셋에서 in-provider vs cross vs consensus-min false-approve·사람괴리 비교(사전동결 임계). Dreammate 결과(10/10→0/10)와 대조.

## 영향 영역
- plotter `app/llm/models.py` · `app/agents/validator.py` · `tests/` (원격).
- Dreammate: 측정 도구·근거(`eval/regression_results/2026-06-21-cross-provider-judge.md`) 공유.

## 의존성
- Dreammate cross-provider judge(검증됨) + 측정 데이터. plotter 키(ANTHROPIC/OpenAI) + 일일 비용 가드. 실 측정 = opt-in 비용.
