# brand_consistency_eval.md — 브랜드 일관성 평가

> 위치: `eval/brand_consistency_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `eval/video_planning_eval.md` §2.7 brand_consistency
> 참조: `docs/contracts/output_schema.md` §14 광고 단어 차단
> 참조: `docs/contracts/agent_io_contract.md` §13 Brand Memory 의존성
> 참조: `docs/contracts/rag_data_contract.md` §8.6 brand_memory vs candidate_knowledge

---

## 1. 목적

영상기획이 brand_memory(preferred_tone, preferred_phrases, avoid_phrases, success_patterns, rejection_patterns)와 일치하는지 평가한다. 일관성은 사용자 신뢰 / 시리즈 누적 효과 / 광고 단어 금지의 3 축으로 측정된다. P-007의 `brand_consistency` 차원이 본 문서를 참고로 채점된다.

---

## 2. 평가 차원 (5 개)

### 2.1 memory_alignment — Brand Memory 일치도

```
정의: plan이 brand_memory의 success_patterns와 일치하는가.
측정: success_patterns의 핵심 표현이 plan의 hook/concept/flow에 (직접 또는 변형) 등장.
0점: success_patterns 무시 또는 정반대
3점: 일치, 강화 없음
5점: success_patterns 자연스럽게 재현 + 신선함 유지
```

### 2.2 tone_consistency — 톤 일관성

```
정의: brand_memory.preferred_tone과 plan의 톤이 일치하는가.
측정:
  - preferred_tone이 "현실적·솔직형"인데 plan이 과장 톤이면 0
  - 사용자가 명시 선택한 tone_card.example_sentences와 같은 구조면 5
0점: 정반대 톤
3점: 충돌은 없으나 강조 부족
5점: 톤이 첫 줄부터 마지막까지 일관
```

### 2.3 avoid_phrase_absence — avoid_phrases 부재

```
정의: brand_memory.avoid_phrases가 plan 본문에 등장하지 않아야 한다.
측정: 정확 매칭 (NFC 정규화). 사용자 본인이 명시한 회피 표현이므로 발견 시 즉시 감점.
0점: avoid_phrases 1개 이상 인용
5점: 0개
주의: 단순 일치뿐 아니라 동의어 인용도 LLM이 별도로 잡음 (Critic suggestion).
```

### 2.4 ad_phrase_absence — 광고 단어 부재

```
정의: output_schema §14의 1차/2차 단어 사전과 교차 검사.
측정:
  1차 단어 1개라도: 0점 + 자동 재생성 (output_schema §14.2)
  2차 단어 1개라도: 3점 + warning (통과)
  없음: 5점
1차: 최고의/혁신적/획기적/완벽한/1위/넘버원/압도적/역대급
2차: 특별한/놀라운/엄청난
```

### 2.5 visual_consistency — 시각 가이드라인 일관성 (placeholder)

```
정의: brand_memory에 visual_guideline이 있으면 plan의 shooting_notes가 일치하는가.
측정: Phase 1에서는 brand_memory에 visual_guideline 필드 없음 → 본 차원은 결측.
Phase 2+에서 brand_visual_guideline 도입 시 활성화.
현재 점수: 3점 고정 (영향 없도록 중립).
```

---

## 3. 입력 / 출력 형식

### 3.1 입력

```yaml
plan: { P-006 plan 1개 }
brand_memory:
  preferred_tone: "string | null"
  preferred_phrases: ["string"]
  avoid_phrases: ["string"]
  success_patterns: ["string"]
  rejection_patterns: ["string"]
selected_tone: { name, example_sentences, avoid_examples }
```

### 3.2 출력

```yaml
scores:
  memory_alignment: 0~5
  tone_consistency: 0~5
  avoid_phrase_absence: 0~5
  ad_phrase_absence: 0~5
  visual_consistency: 3              # placeholder
brand_consistency_avg: 0~5
violations:
  - { type: "avoid_phrase", word: "완벽한" }
  - { type: "ad_phrase_1st", word: "최고의" }
  - { type: "ad_phrase_2nd", word: "엄청난" }
reasons: { 차원별 1줄 }
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| memory_alignment | LLM | 운영자 보조 |
| tone_consistency | LLM | 운영자 1차 |
| avoid_phrase_absence | 룰 (정확 매칭) | — |
| ad_phrase_absence | 룰 (사전 매칭) | — |
| visual_consistency | (placeholder) | — |

룰 기반(avoid_phrase_absence, ad_phrase_absence)은 LLM 호출 직후 즉시 검사 (output_schema §14.2). 위반 시 자동 재생성.

---

## 5. 임계값

```
brand_consistency_avg ≥ 4.0   passing
3.0~3.9                       warning (suggestions 필수)
< 3.0                         failing (revise 후보)

특수 게이트:
- ad_phrase_1st 발견: 자동 재생성 1회 → 재시도 후에도 위반 시 verdict=reject
- avoid_phrase 발견: revise 후보 (운영자 검토 시 reject 가능)
- 1회 재시도 후에도 ad_phrase_1st: validation.passed=false + E-LLM-006 (error_response_contract §4.2)
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §14 (광고 단어 차단 흐름)
  - agent_io_contract.md §13 (Brand Memory 의존성 매트릭스)
  - rag_data_contract.md §8.6 (brand_memory vs candidate_knowledge)
  - error_response_contract.md §4.2 E-LLM-006

Skill:
  - eval-design (차원 갱신)
  - prompt-version-review (avoid_phrases 정책 변경 시 회귀)
  - meta-retrospective (avoid_phrases 누적 패턴 회고)

연관 골든 셋: GS-004 (광고 단어 차단), GS-009 (Brand Memory 추출).
```

---

## 7. Open Questions

1. avoid_phrases 동의어 검사 — 현재 정확 매칭만. LLM 동의어 판단 도입 시 false positive 증가 우려.
2. visual_consistency 차원의 활성 시점 — brand_visual_guideline 도입 Phase 2+.
3. is_user_locked=true 항목과 충돌 시 가중치 — 현재 단순 일치, locked 항목 충돌은 별도 가중 검토.
4. ad_phrase 2차 단어의 누적 통계 — Critic의 의견 채택률 추적해서 1차 승격 후보 도출.
5. 사용자가 의도적으로 avoid_phrase를 깬 plan을 선택한 경우 — brand_memory 자동 갱신(완화) vs 일회성 무시.
