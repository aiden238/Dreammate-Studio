# hook_quality_eval.md — Hook(첫 3~5초) 품질 평가

> 위치: `eval/hook_quality_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `eval/video_planning_eval.md` §2.3 hook_strength
> 참조: `docs/contracts/output_schema.md` §8 P-006 (plans[*].hook 20~60자)
> 참조: `docs/contracts/output_schema.md` §14 광고 단어 차단

---

## 1. 목적

영상의 첫 3~5초(hook)는 시청 이탈 여부를 결정한다. 본 문서는 hook 텍스트의 품질을 5 차원으로 분해하고, 숏폼(30~60초)과 롱폼(3분 이상)의 가중치 차이를 정형화한다. P-007의 `hook_strength` 차원이 본 문서의 종합 평가에 매핑된다.

---

## 2. 평가 차원 (5 개)

각 차원 0~5 정수.

### 2.1 curiosity — 호기심 유발

```
정의: 첫 줄에서 다음 장면이 궁금해지는가.
측정: 질문형 / 의외성 / 결과 선노출 / 갈등 암시 중 1개 이상.
0점: 평이한 인사 ("안녕하세요")
3점: 정보성 한 줄, 호기심 약함
5점: 명확한 hook ("이 영상 끝까지 봐야 하는 이유" 수준)
```

### 2.2 specificity — 구체성

```
정의: 추상어가 아니라 구체적 상황 / 숫자 / 인물이 등장하는가.
측정: 고유명사 또는 숫자 또는 행동 동사 포함 여부.
0점: 추상어만 ("성공적으로 운영하는 방법")
3점: 일부 구체
5점: 첫 줄에 구체 명사·동사·숫자 ("3명짜리 동아리가 100명 모은 비결")
```

### 2.3 differentiation — 차별성

```
정의: 다른 두 plan 옵션의 hook과 표현·접근이 다른가.
측정: 동일 접근(질문 vs 결론 vs 갈등)이 3 옵션 중 2개 이상이면 감점.
0점: 다른 옵션과 같은 접근 + 같은 문구
3점: 접근은 같으나 문구 다름
5점: 접근 자체가 다름 (질문형 / 결론형 / 비주얼형)
```

### 2.4 brevity — 짧음 (글자 수)

```
정의: 숏폼은 짧을수록 좋다. 롱폼은 약간 길어도 됨.
측정: 글자 수 (한글 NFC 기준).
숏폼 (shorts_30s, shorts_60s, reels_60s):
  ≤ 30자  → 5점
  31~40자 → 4점
  41~50자 → 3점
  51~60자 → 2점 (output_schema §8.2 hook 상한)
  > 60자  → 0점 (validation fail)
롱폼 (youtube_3m, youtube_8m):
  ≤ 40자  → 5점
  41~55자 → 4점
  56~70자 → 3점
  > 70자  → 0점
```

### 2.5 ad_phrase_absence — 광고 단어 부재

```
정의: 1차 차단 단어 / 2차 경고 단어가 없어야 한다 (output_schema §14).
측정: 정확 매칭 + NFC 정규화 후.
1차 단어 1개라도: 0점 (자동 재생성, output_schema §14.2)
2차 단어 1개라도: 3점 (warning, 통과)
없음: 5점
```

---

## 3. 입력 / 출력 형식

### 3.1 입력

```yaml
hook_text: "string"
format: shorts_30s | shorts_60s | reels_60s | youtube_3m | youtube_8m | other
context:
  approved_direction: "string"   # 의도 일치 검증용
  other_plan_hooks: ["string"]   # differentiation 비교용 (선택)
```

### 3.2 출력

```yaml
scores:
  curiosity: 0~5
  specificity: 0~5
  differentiation: 0~5
  brevity: 0~5
  ad_phrase_absence: 0~5
hook_score_avg: 0~5
hook_score_weighted: 0~5         # §5 가중치 적용
violations:
  - { type: "ad_phrase_1st", word: "최고의" }   # 있을 때만
reasons: { 차원별 1줄 }
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| curiosity | LLM | 운영자 1차 |
| specificity | LLM | 운영자 보조 |
| differentiation | LLM (3 hook 입력 시) | 운영자 보조 |
| brevity | 룰 (글자 수) | — |
| ad_phrase_absence | 룰 (사전 매칭) | — |

룰 기반 차원(brevity, ad_phrase_absence)은 CI에서 즉시 검증 가능. LLM 기반 차원은 P-007의 hook_strength로 통합되어 채점.

---

## 5. 가중치 (숏폼 vs 롱폼)

```
숏폼 (3~60초):
  curiosity         0.30   # 첫 줄이 모든 것
  specificity       0.20
  differentiation   0.15
  brevity           0.15
  ad_phrase_absence 0.20

롱폼 (3분 이상):
  curiosity         0.25
  specificity       0.25
  differentiation   0.15
  brevity           0.10   # 약간 덜 중요
  ad_phrase_absence 0.25
```

`hook_score_weighted`는 위 가중치로 계산. 임계:

```
≥ 4.0   passing (P-007 hook_strength 4 이상)
3.0~3.9 warning (suggestions 필수)
< 3.0   failing (revise 후보)
ad_phrase_1st 발견: 즉시 0 점화 + 재생성
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §8.2 (hook 20~60자 검증)
  - output_schema.md §14 (광고 단어 차단)
  - frontend_design_contract.md §5 (hook UI 노출 시 광고 단어 inline warning)

Skill:
  - eval-design (차원 갱신)
  - eval-run (회귀)
  - design-review (UI에 hook 노출되는 화면 검토)

연관 골든 셋: GS-004 (광고 단어), GS-005 (Critic revise).
```

---

## 7. Open Questions

1. brevity의 모바일 vs 데스크톱 한국어 가독성 차이 — 모바일에서 30자 1줄, 데스크톱은 40자 1줄.
2. specificity의 "구체"를 LLM이 어떻게 측정할지 — 고유명사 사전 vs LLM-as-judge.
3. 동영상 자막의 hook과 텍스트 hook이 분리될 때(자막 vs 음성) 채점 대상 — 현재는 텍스트 hook만.
4. differentiation에서 다른 plan을 모를 때 (단일 plan 채점) 결측 처리.
5. 다국어 도입 시 brevity 글자 수 기준 (영어 vs 한국어).
