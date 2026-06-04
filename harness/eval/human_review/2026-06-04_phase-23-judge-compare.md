# Phase 23 S2 — human review: compact↔rich LLM-judge 대조 + 사용자 채점 시트

> 2026-06-04 | Phase 12 S4 kit(2케이스) 후속 — LLM-judge 기준선 + 사용자 실채점 시트
> 목적: rich 출력의 실효 가치를 **사람 눈**으로 검증(critic 낙관 편향 상호보완) + human↔LLM 대조 준비.
> ★ 실채점은 **사용자 액션**(deferred — Phase 12 S4 동일). 본 문서는 기준선 + 시트 제공.

## 1. LLM-judge 대조 (실 critic, 2케이스 × compact/rich)

| 케이스 | 모드 | overall (critic 평균) | depth_actionability | verdict | 차원수 |
|---|---|---|---|---|---|
| C1 자취요리(김치볶음밥 쇼츠) | compact | 4.25 | — (미채점) | approve | 8 |
| C1 자취요리 | **rich** | **4.67** | **5** | approve | 9 |
| C2 이어폰 리뷰 | compact | 4.25 | — | approve | 8 |
| C2 이어폰 리뷰 | **rich** | **4.22** | **4** | approve | 9 |

### ★ 핵심 발견 (정직)
- **critic 8차원 overall 은 compact↔rich 를 거의 구분 못 한다**(둘 다 ~4.25, 전부 approve). 즉 generic critic 만으로는 rich 의 우위가 안 보인다 — Phase 16 A/B 의 "generic Δ flat" 와 동일 현상.
- 차이는 **depth_actionability(rich 9번째 차원, 4~5)** 에서만 드러난다. compact 은 이 차원을 아예 못 받음(슬롯 부재).
- → **사람 검증이 필요한 이유**: "8차원은 비슷한데 rich 가 실제로 더 쓸만한가?"는 critic 이 아니라 **사람(would_use/실행가능성)** 이 판정해야 함.

## 2. 사용자 실채점 시트 (★ 작성 요청 — 사용자)

> 각 케이스의 compact vs rich 실 출력은 Phase 12 S4 kit(`2026-06-02_phase-12-s4-review-kit.md`) 또는 운영 /generate(OUTPUT_MODE 토글)로 확인.
> 아래 5+1 차원(human_review_rubric §2)을 0~5(깊이는 0~1)로 채점.

```yaml
# C1 자취요리 — compact
content_quality: _    # 0~5
brand_fit: _          # 0~5
promotion_value: _    # 0~5
user_response_risk: _ # 0~5 (높을수록 안전/적절)
would_use: _          # 0~5 (실제로 이 기획안 쓸 의향)
depth_actionability: _ # 0~1
# C1 자취요리 — rich
content_quality: _ ; brand_fit: _ ; promotion_value: _ ; user_response_risk: _ ; would_use: _ ; depth_actionability: _

# C2 이어폰 리뷰 — compact
content_quality: _ ; brand_fit: _ ; promotion_value: _ ; user_response_risk: _ ; would_use: _ ; depth_actionability: _
# C2 이어폰 리뷰 — rich
content_quality: _ ; brand_fit: _ ; promotion_value: _ ; user_response_risk: _ ; would_use: _ ; depth_actionability: _

free_comment: "___"   # 100자 이내 — rich 가 compact 보다 실제로 나은가?
```

## 3. human↔LLM 대조 (사용자 채점 후)
- 채점 회수 시: 각 차원 `diff = human - LLM` 계산 → critic 신뢰도(특히 depth) 캘리브레이션.
- ★ 핵심 질문: 사용자의 **would_use(compact) vs would_use(rich)** 격차가 critic 의 flat overall 과 달리 rich 우위를 보이는가? (= Phase 16 fit 발견의 사람-검증 확인)
- 누적 n≥5 시 human_avg 산식 + LLM-as-judge 신뢰도 보고(별도).

## 4. 상태
- ✅ LLM-judge 기준선 확정(위 §1). ✅ 채점 시트 제공(§2).
- ⬜ 사용자 실채점 — **deferred(사용자 액션)**. 회수 시 §3 대조.
