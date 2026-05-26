# target_fit_eval.md — 타겟 적합도 평가

> 위치: `eval/target_fit_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `eval/video_planning_eval.md` §2.2 target_clarity
> 참조: `docs/contracts/output_schema.md` §6 P-004 (target_cards + tone_cards)
> 참조: `docs/contracts/output_schema.md` §7 P-005 (components.target)

---

## 1. 목적

영상이 누구를 향하는지를 평가한다. 타겟이 명확할수록 hook이 꽂히고, 메시지가 짧아지고, 플랫폼 선택이 단순해진다. 본 문서는 target 정의 / 적합도 / 플랫폼 매핑의 평가 기준을 고정한다. P-007의 `target_clarity` 차원이 본 문서를 참고로 채점된다.

---

## 2. 평가 차원 (5 개)

### 2.1 persona_specificity — 타겟 페르소나 구체성

```
정의: target이 단일 페르소나로 좁혀지는가.
측정: 연령대 + 상황 + 동기 중 2개 이상 명시.
0점: "대학생" 같은 광범 카테고리
3점: "창업동아리 소속 대학생"
5점: "3학년 창업동아리 회장, 사업계획서 준비 중, 시간 부족" (단일 페르소나)
```

### 2.2 pain_point_reflection — pain point 반영도

```
정의: P-004의 target_cards.pain_points가 hook/message/flow에 반영되는가.
측정: pain_points 텍스트 또는 동의어가 plan 본문에 나타나는가.
0점: pain_point 무관 콘텐츠
3점: 일부 반영
5점: pain_point가 첫 줄 + 마무리 행동 유도에 모두 반영
```

### 2.3 tone_alignment — 메시지 톤 적합도

```
정의: target의 정서 상태와 톤이 일치하는가.
측정: P-004 tone_cards.example_sentences vs avoid_examples.
0점: avoid_examples 인용 또는 톤 정면 충돌
3점: 충돌 없음, 강화 없음
5점: tone_card의 example_sentences와 동등한 표현이 자연스럽게 등장
연관: brand_consistency_eval.md (브랜드 톤은 별도)
```

### 2.4 platform_fit — 플랫폼 적합도

```
정의: 영상 포맷과 플랫폼의 일치도.
측정:
  shorts_30s, shorts_60s   → YouTube Shorts / TikTok / Instagram Reels
  reels_60s                 → Instagram Reels (primary)
  youtube_3m                → YouTube long
  youtube_8m                → YouTube long
0점: 포맷-플랫폼 불일치 (예: 8분 영상을 Shorts 의도)
3점: 호환되나 최적은 아님
5점: 포맷-플랫폼-target 시청 습관이 일치
참고: 타겟 연령대별 플랫폼 선호도는 §5.1 참조.
```

### 2.5 watch_motivation — 시청 동기 명시도

```
정의: target이 왜 끝까지 볼지 명확한가.
측정: P-004 watch_motivation 필드가 plan 본문에 (직접 또는 비유로) 등장.
0점: 시청 동기 추정 불가
3점: 추정 가능
5점: 첫 줄과 마무리에서 시청 동기 강화
```

---

## 3. 입력 / 출력 형식

### 3.1 입력

```yaml
plan: { P-006 plan 1개 }
selected_target: { name, description, pain_points, watch_motivation, fit_score_rationale }
selected_tone: { name, example_sentences, avoid_examples }
approved_direction: "..."
format: shorts_30s | ... | other
```

### 3.2 출력

```yaml
scores:
  persona_specificity: 0~5
  pain_point_reflection: 0~5
  tone_alignment: 0~5
  platform_fit: 0~5
  watch_motivation: 0~5
target_fit_avg: 0~5
reasons: { 차원별 1줄 }
warnings:
  - "platform_mismatch"          # 있을 때만
  - "pain_point_missing"
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| persona_specificity | LLM | 운영자 보조 |
| pain_point_reflection | LLM + 룰(키워드 검사) | 운영자 보조 |
| tone_alignment | LLM | 운영자 1차 |
| platform_fit | 룰 (포맷-플랫폼 매핑) | — |
| watch_motivation | LLM | 운영자 1차 |

---

## 5. 플랫폼 매핑 표

### 5.1 포맷 → 플랫폼 우선순위

```
shorts_30s, shorts_60s:
  primary:   YouTube Shorts, TikTok
  secondary: Instagram Reels
  age_fit:   10대 후반 ~ 30대 초반 (mass)

reels_60s:
  primary:   Instagram Reels
  secondary: YouTube Shorts
  age_fit:   20~35

youtube_3m:
  primary:   YouTube
  secondary: 거의 없음 (3분은 long shorts와 short long 사이)
  age_fit:   20~40

youtube_8m:
  primary:   YouTube
  age_fit:   25~45 (정보성 콘텐츠 강함)

other:
  → missing_info에 "영상 포맷 확정" 자동 포함 (output_schema §7.2)
  → platform_fit 채점 보류
```

### 5.2 임계 (target_fit_avg)

```
≥ 4.0   passing
3.0~3.9 warning (P-007 target_clarity 3 매핑)
< 3.0   failing (revise 후보)
platform_mismatch warning: target_fit_avg와 무관하게 별도 노출
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §6 (P-004 target + tone)
  - output_schema.md §7 (P-005 components.format)
  - frontend_design_contract.md §5 (target 카드 5장 UI)

Skill:
  - eval-design (차원 갱신)
  - eval-run (회귀)

연관 골든 셋: GS-002 (Quick mode + brand context), GS-008 (포맷 분기).
```

---

## 7. Open Questions

1. 타겟 연령대별 플랫폼 선호도 데이터 소스 — 외부 통계 vs 자체 누적 데이터.
2. tone_alignment의 LLM 채점 일관성 — temperature 0.1로 회귀해도 ±1 점수 변동 관찰.
3. "other" 포맷의 platform_fit 채점 — 현재 보류, Phase 2+에서 자유 입력 허용 시 재설계.
4. 다중 페르소나 타겟(예: 부모와 자녀)의 채점 — 현재 단일 페르소나만 가정.
5. watch_motivation이 비주얼/음향 요소에 있을 때 (텍스트 부재) — 현재 텍스트 기반 채점만.
