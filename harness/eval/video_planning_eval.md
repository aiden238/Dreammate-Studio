# video_planning_eval.md — 영상기획 종합 평가 (8 차원)

> 위치: `eval/video_planning_eval.md`
> 상태: Phase 0–1 진입용 회귀/리뷰 베이스라인
> 참조: `docs/contracts/output_schema.md` §9 P-007 (Critic Agent)
> 참조: `docs/contracts/agent_io_contract.md` §5 Critic Agent
> 참조: `eval/golden_set.md` (GS-005, GS-006 회귀 케이스)
> 참조: `eval/hook_quality_eval.md`, `eval/target_fit_eval.md`, `eval/brand_consistency_eval.md`, `eval/execution_feasibility_eval.md`

---

## 1. 목적

영상기획 결과물(P-006 plan 또는 final_output)의 종합 품질을 8 차원으로 측정한다. Critic Agent(P-007)의 자동 채점과 운영자 수동 검토(`human_review_rubric.md`)에서 동일한 차원/임계를 공유해 학습 데이터를 일관되게 누적한다.

본 문서는 평가 차원의 **정의 / 측정 방법 / 임계값**을 고정한다. 채점 prompt 본문은 `ai_system/prompts/prompt_registry.md` P-007에서 정의.

---

## 2. 평가 차원 (8 개)

각 차원 0~5 정수 점수. 모든 차원은 P-007 출력의 `scores.*` 키에 1:1 매칭.

### 2.1 intent_fit — 의도 적합성

```
정의: approved_direction(한 줄 방향)과 plan의 일치도.
측정: plan의 hook + concept + flow가 approved_direction의 target/message/format을 모두 반영하는가.
가중치: 0.18 (가장 중요, 의도 이탈은 다른 차원이 좋아도 무효)
0점: 의도와 무관
3점: 일부 반영, 일부 누락
5점: 의도 그대로 + 자연스러운 구체화
```

### 2.2 target_clarity — 타겟 명확성

```
정의: plan이 target persona를 명확히 겨냥하는가.
측정: hook / message / flow에 target의 pain_point, motivation, 상황이 언급되거나 암시되는가.
가중치: 0.13
0점: 누가 봐도 될 내용 (mass)
3점: 특정 집단은 알겠으나 모호
5점: target persona가 첫 줄에서 본인 이야기라고 느낌
연관: target_fit_eval.md
```

### 2.3 hook_strength — 후킹 강도

```
정의: 첫 3~5초의 호기심 유발력.
측정: hook 텍스트 단독으로 시청 의지 유발 + 광고 카피톤 부재 + 구체성.
가중치: 0.15 (숏폼에서는 0.18 권장)
0점: 일반적 인사 또는 추상어
3점: 호기심은 있으나 명확성 부족
5점: 첫 줄에서 끝까지 보고 싶게 만듦 + 광고 단어 0개
연관: hook_quality_eval.md
```

### 2.4 message_clarity — 메시지 선명도

```
정의: 영상이 전달하고자 하는 핵심 메시지가 1개로 명확한가.
측정: flow 전체에서 메시지가 변경되거나 분산되지 않음. 마지막 비트에서 메시지 재강조 또는 행동 유도.
가중치: 0.13
0점: 메시지 다중 또는 부재
3점: 메시지는 있으나 강화 부족
5점: 명확한 1 메시지 + 마무리에서 자연스러운 행동 유도
```

### 2.5 structure — 구성 완성도

```
정의: hook → body → ending의 시간 배분과 흐름의 자연스러움.
측정: flow 배열 길이 3~6 (포맷별), duration_sec 합이 length_sec ± 10%, 비트 간 전환 명시.
가중치: 0.10
0점: 단순 나열, 시간 미정
3점: 시간 배분은 있으나 전환 어색
5점: hook-body-ending 균형 + duration 적합 + 전환 자연
```

### 2.6 feasibility — 실행 가능성

```
정의: 대학생/스타트업 1인 제작자가 실제로 만들 수 있는가.
측정: 촬영 난이도 / 출연자 수 / 장소 접근성 / 편집 시간 / 예산.
가중치: 0.10
0점: 비현실 (해외 로케 / 유명인 캐스팅 등)
3점: 가능하나 1~2 항목이 부담
5점: 1인 제작자가 1~2일 안에 가능
연관: execution_feasibility_eval.md
```

### 2.7 brand_consistency — 브랜드 일관성

```
정의: brand_memory (preferred_tone, avoid_phrases, success_patterns)와의 일치도.
측정: avoid_phrases 인용 0개 / preferred_tone과 톤 일치 / preferred_phrases 자연스러운 인용.
가중치: 0.12
0점: avoid_phrases 인용 또는 톤 충돌
3점: 충돌 없으나 강조도 없음
5점: brand 정체성 강화 + 광고 단어 0개
연관: brand_consistency_eval.md
```

### 2.8 differentiation — 차별성

```
정의: 다른 두 plan 옵션과 비교했을 때 접근 방식의 차별성.
측정: approach_label 다름 + hook 표현 다름 + flow 구조 다름.
가중치: 0.09
0점: 다른 옵션과 거의 동일
3점: 약간 차별
5점: 의미 있게 다른 접근 (사용자에게 진짜 선택지 제공)
주의: 3개 plan 비교 컨텍스트가 필요. 단일 plan 채점 시 본 차원은 결측 가능.
```

---

## 2.A 보조 평가 차원 (real LLM / human review 전용)

> Phase 12 S1 (2026-06-02, CC-011) **additive** 추가. §2 의 8 차원 정의/스케일/가중치는 **무변경**.
> 본 §2.A 차원은 §2 의 8 차원과 **별도 축** — overall_score_avg(8 차원 평균) 산식에 포함되지 않으며,
> P-007 mock-deterministic 채점에도 영향 없다 (mock 러너는 §2 의 8 차원만 채점).

### 2.A.1 depth_actionability — 기획 깊이·실행가능성

```
정의: 출력이 "창작자가 추가 질문 없이 바로 촬영·편집에 착수할 만큼 구체적이고 실행 가능한가".
      현재 compact 출력(plan 골격 — name/concept/hook/flow 골격)이 얼마나 얕은지(또는 확장 출력이
      얼마나 깊은지)를 측정하는 축. §2 의 8 차원(품질의 "방향")과 직교 — 같은 방향이라도
      구체성·실행성의 깊이는 별개로 측정된다.

측정 (아래 항목의 포함도·구체성을 종합):
  - hook 변형 수 (단일 vs 2~3개 A/B 변형 제시)
  - 각 beat 의 화면 구성(샷)·대사/나레이션·자막·목적의 구체성 (4요소 명시 여부)
  - 샷 리스트 / B-roll 제안 포함도
  - 썸네일 문구·제목(2~3안)·CTA(행동 유도 문구) 포함도
  - 레퍼런스(참고 영상/패턴) 제시 여부
  - 길이 변형(15s/30s/60s 재구성) 제안 여부
  - 전반적 실행가능성 (창작자가 바로 쓸 수 있는 수준인가)

채점 스케일: 0~1 (★ §2 의 8 차원은 0~5 정수 — 본 차원은 별도 0~1 실수 스케일로,
            §2 평균 산식과 혼입되지 않도록 의도적으로 분리한다).

rubric anchors:
  0.2  매우 얕음 — 현 compact 수준. plan 골격(name/concept/hook 1개/flow 비트 골격)만 존재.
       beat 에 화면/대사/자막 구체성 없음. 샷·B-roll·썸네일·제목·CTA·레퍼런스·길이변형 전부 부재.
       창작자가 "이걸로 뭘 어떻게 찍지?" 추가 질문 다수 발생.
  0.6  보통 — beat 별 화면·목적은 구체적이나 일부 항목 누락. hook 변형 1~2개,
       샷/B-roll 또는 썸네일/제목/CTA 중 일부만 포함. 레퍼런스·길이변형 미포함.
       창작자가 큰 틀은 잡되 세부는 직접 채워야 함.
  1.0  매우 구체적 — 확장 출력 수준. hook 2~3개 변형 + 각 beat 의 화면/대사/자막/목적 4요소 명시
       + 샷 리스트·B-roll 제안 + 썸네일 문구·제목 2~3안·CTA + 레퍼런스 + 길이 변형(15/30/60) 재구성.
       창작자가 추가 질문 없이 바로 촬영·편집 착수 가능.

가중치: 별도 축 (8 차원 가중 평균에 미포함 — §5.2 산식 무변경).

채점 주체: ★ real LLM eval (mode='real') 또는 human review 전용. mock-deterministic 러너는
          plan 골격만 합성하므로 본 차원을 의미있게 채점할 수 없다(항상 ~0.2 부근으로 무의미).
          따라서 mock 러너(`backend/fastapi/eval/runner.py`)는 본 차원을 채점하지 않으며,
          §2 의 8 차원 structural 채점만 수행한다 (behavior-preserving).

용도: Phase 12 검증 — 현 compact 출력이 "바로 쓸 수 있는 깊이"에 못 미치는 정도를 정량화해,
     확장(B안) 출력과의 깊이 격차를 측정하는 기준 축. golden_set GS-005/GS-020 등 plan 생성 케이스가
     real/human 채점 시 본 차원의 주 대상.
연관: eval/execution_feasibility_eval.md (실행가능성 세부), eval/human_review_rubric.md §2.6 (사람 채점).
```

---

## 3. 입력 / 출력 형식

### 3.1 입력 (P-007 input)

`agent_io_contract.md` §5.2 참조. 핵심:

```yaml
target_plan: { plan 1개 }
approved_direction: "..."
selected_context: { brand, domain, series, target, tone }
brand_memory: { avoid_phrases, preferred_tone }
revise_round: 0 | 1 | 2     # server-side 주입
```

### 3.2 출력 (P-007 body)

```yaml
target_plan_id: uuid
scores:
  intent_fit: 0~5
  target_clarity: 0~5
  hook_strength: 0~5
  message_clarity: 0~5
  structure: 0~5
  feasibility: 0~5
  brand_consistency: 0~5
  differentiation: 0~5
reasons: { 동일 키 1:1 }
suggestions: { 동일 키 1:1 }
overall_score_avg: 산술 평균 (또는 가중 평균, §5.2)
overall_verdict: approve | revise | reject
blocking_issues: [string]      # 최대 3개
revise_round: 0                # LLM은 항상 0
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 (LLM/룰) | 수동 (운영자) | 비고 |
|---|---|---|---|
| intent_fit | LLM | 운영자 보조 | LLM 1차, 운영자 borderline 케이스만 |
| target_clarity | LLM | 운영자 보조 | |
| hook_strength | LLM + 룰 | 운영자 주도 | 광고 단어 검사는 룰, 매력도는 LLM |
| message_clarity | LLM | 운영자 보조 | |
| structure | 룰 + LLM | 거의 자동 | duration 합 검증은 룰 |
| feasibility | LLM | 운영자 주도 | 1인 제작자 시뮬레이션은 운영자 강점 |
| brand_consistency | 룰 + LLM | 운영자 보조 | avoid_phrases 룰, 톤은 LLM |
| differentiation | LLM | 운영자 보조 | 3개 plan 비교 컨텍스트 필요 |

자동 평가 결과는 `quality_scores` 테이블에 저장. 운영자가 재채점하면 새 row INSERT (history 보존).

---

## 5. 임계값

### 5.1 verdict 임계 (output_schema §9.2와 정합)

```
approve:  overall_score_avg ≥ 3.5 AND 모든 점수 ≥ 2
revise:   2.5 ≤ avg < 3.5 OR 1~2개 점수가 < 2
reject:   avg < 2.5 OR 3개 이상 점수가 < 2 OR 광고적 표현 위반 발견
```

revise_round = 2에서 다시 revise 시 server-side가 강제 approve (→ `agent_io_contract.md` §5.8).

### 5.2 가중 평균 옵션 (Phase 1.x 검토)

```
weighted_avg =
   0.18 * intent_fit
 + 0.13 * target_clarity
 + 0.15 * hook_strength
 + 0.13 * message_clarity
 + 0.10 * structure
 + 0.10 * feasibility
 + 0.12 * brand_consistency
 + 0.09 * differentiation
 = (합계 1.00)

Phase 1 현재: 산술 평균 사용 (단순성).
Phase 2+ 검토: 가중 평균 도입 (intent_fit / hook_strength 강조).
도입 시 prompt-version-review Skill 절차 + golden_set 회귀.
```

### 5.3 차원별 passing / warning / failing

```
점수    상태
5       excellent
4       passing
3       passing (단 reason에 개선 여지 명시)
2       warning (suggestions 필수)
0~1     failing (blocking_issues 후보)
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §9 (P-007 body)
  - agent_io_contract.md §5 (Critic Agent)
  - error_response_contract.md §4.2 E-LLM-010 (revise 무한 루프)

Skill:
  - eval-design (본 차원 갱신 시)
  - eval-run (회귀 실행)
  - prompt-version-review (P-007 major bump 시 회귀 강제)
  - meta-retrospective (Phase 종료 시 누적 점수 회고)
```

---

## 7. Open Questions

1. 가중 평균 도입 시점 — 산술 평균과의 verdict 차이 측정 후 결정.
2. differentiation 차원의 단일 plan 채점 시 결측 처리 — null 허용 vs 평균에서 제외.
3. 운영자 수동 재채점 시 LLM 점수와의 차이 통계 — 누적 50건 후 캘리브레이션.
4. blocking_issues 최대 3개 제한 — 4개 이상 발견 시 우선순위 결정 규칙.
5. 광고 단어 위반 시 reject 강제 vs revise(개선 기회) — 현재 reject, 운영 데이터로 조정.
