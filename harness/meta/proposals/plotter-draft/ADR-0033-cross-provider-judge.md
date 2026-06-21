# ADR-0033: Cross-provider Judge 재고 — consensus-min (gated)

> ★ **초안(draft)** — Dreammate(`Dreammate-Studio`) 세션이 plotter 적용용으로 작성. plotter repo에 옮겨 본인 결정 후 Accepted 처리.

- **상태**: **Proposed (draft, 2026-06-22, Dreammate 측정 근거)**
- **연관**: **ADR-0007**(LLM-as-Judge — 대안C cross-family / 대안D ensemble 기각) · **ADR-0031**(자기검토 강화 — D1-C "항상 Opus" cross-provider **보류**, "B로 cross-model 편향 남으면 재고") · ADR-0023(per-request 모델) · ADR-0009(MoA)

> **목적**: ADR-0031이 보류한 D1-C(cross-provider judge)를, 자매 프로젝트(Dreammate)의 정량 측정이 그 **재고 트리거**("B로 cross-model 편향 남으면")를 충족시켰으므로 재고한다. 단 비용/키 의존을 **gated 옵션 + consensus-min**으로 통제한다.

## 1. 배경 — 재고 트리거 충족

ADR-0031은 D1=B(같은 provider 한 급 위 judge: gpt-4o-mini→gpt-4o 등)를 채택하고, D1-C(항상 Opus·cross-provider)는 "Anthropic 키 의존·비용·트랙 자족성"을 이유로 **보류**하며 후속에 `[ ] open: D1-C 재고 — B로 cross-model 편향이 남으면`을 남겼다.

자매 프로젝트 Dreammate가 같은 문제(critic 낙관편향)를 같은 방법론(human blind N=10, 사전동결 임계)으로 측정:
- **in-provider 채점(OpenAI 생성→OpenAI critic)**: critic 평균 89점 vs 사람 44점, **false-approve 10/10**(전수). calibration(프롬프트+per-axis 게이트) 단독은 **verdict 0건 flip**.
- **cross-provider judge(OpenAI 생성→Claude 채점)**: approve 10건 전부 뒤집어 **false-approve 10/10→0/10**, 사람괴리 2.27→**0.53**(ko 사람정렬). "모델 교체 = 다른 blind spot"이 in-provider(Haiku→Opus)보다 강함.

→ **"B(같은 provider 한 급 위)로도 cross-model 편향이 남는다"가 정량 확인됨** = ADR-0031 D1-C 재고 트리거 충족. (Dreammate `eval/regression_results/2026-06-15-critic-calib-ab-preliminary.md`, `2026-06-21-cross-provider-judge.md`.)

★ ADR-0007 대안C(GPT cross-Judge)의 우려였던 "한국어 평가 일치도↓"는, Dreammate가 Claude judge의 ko 사람정렬(괴리 0.53)을 측정해 **부분 반박**. 대안D(3-judge ensemble) 기각은 유지 — 본 ADR은 ensemble이 아니라 **2-judge consensus-min**(다른 메커니즘).

## 2. 고려한 대안 (D1-C 재고)

- **A — 현행(같은 provider 한 급 위) 유지**: cross-model 편향 잔존(측정됨). **기각**.
- **B — cross-provider judge 교체(항상 Opus)**: gpt/gemini 트랙 judge를 Anthropic Opus로 교체. 가장 독립적이나 모든 요청에 Anthropic 키 의존 + 트랙 자족성 깨짐(ADR-0031 D1-C 원 우려). **부분 채택(옵션)**.
- **C — consensus-min(in-provider judge ∧ cross judge, 더 엄격)** *[채택]*: 기존 in-provider judge는 유지하고, **cross-provider judge를 추가로 돌려 둘 중 더 엄격한 판정(threshold_pass = in_pass ∧ cross_pass)**을 채택. 단조(절대 더 약해지지 않음). 키 부재 시 graceful(현행으로). 비용은 gated + 일일 가드.

## 3. 결정

**D1-C 재고 = C(consensus-min)를 gated 옵션으로 도입.** `CRITIC_CROSS_JUDGE` env(default off=현행 byte-identical). ON 시 in-provider judge 통과 후 **cross-provider judge(다른 provider flagship)**로 재검, 둘 다 통과해야 `threshold_pass`. ANTHROPIC/OpenAI 키 부재면 graceful(cross skip=현행). JUDGE_TEMPERATURE=0 불변(ADR-0007).

## 4. 이유

1. **결정적 게이트(ADR-0031 D2 축 게이트 + structure_pacing_issues)와 직교**: 게이트는 *구조 붕괴*(시간배분·축)를, cross judge는 *점수 낙관*(self-review 편향)을 막는다. **둘 다 필요**(Dreammate calib-ab-preliminary §6: calibration 단독 0건 flip → 결정적 게이트 + cross judge 합산). plotter는 게이트 ✅ 보유, cross judge가 **누락된 절반**.
2. **consensus-min은 단조** — in-provider보다 절대 더 약해지지 않음(안전 default 후보). ensemble(3-judge 평균/다수결, ADR-0007 기각)과 달리 2-judge AND라 분석 부담·비용 작음.
3. **gated + graceful**로 ADR-0031 D1-C 원 우려(키 의존/비용/자족성)를 흡수 — default off면 트랙 자족성 불변.

## 5. 결과 (예상)

**긍정**: in-provider judge가 놓친 self-review 낙관(false-approve)을 cross judge가 차단. 결정적 게이트와 합쳐 false-approve 2중 방어.
**부정/제약**: ON 시 judge 2회 = 비용↑(일일 가드 NF-M01 상한 보호). cross judge provider 키 필요(부재 시 graceful). plotter 골든셋 실측 전 = 방향성(Dreammate N=10·rater A N=1, κ 미산출).

## 6. 후속 작업
- [ ] `models.py` cross-judge 매핑 + `CRITIC_CROSS_JUDGE` flag, `validator.py` consensus-min 경로 (아래 patch 초안).
- [ ] plotter 골든셋으로 **in-provider vs cross vs consensus-min** false-approve·사람괴리 측정(사전동결 임계).
- [ ] rater B(팀원) κ — Dreammate·plotter 공통 미충족.
- [ ] default 전환 검토는 측정 후(major).

## 7. Negative Result Survivability
- "같은 provider 한 급 위 judge로도 cross-model 편향이 남는다"(Dreammate 측정) — self-critique 시스템 일반 교훈. 독립성은 *모델 급*이 아니라 *provider(blind-spot) 교차*에서 나온다.
