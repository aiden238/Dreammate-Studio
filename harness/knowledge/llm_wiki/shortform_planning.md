# shortform_planning.md — 숏폼 기획 가이드

> 위치: `knowledge/llm_wiki/shortform_planning.md`
> 적용: 30-90초 영상 (YouTube Shorts / TikTok / Instagram Reels)
> 연계: `hook_patterns.md`, `evaluation_criteria.md`, `knowledge/rag/sources.md`

---

## 0. 정의

**숏폼(Shortform)**: 30-90초 길이의 세로형 영상. 모바일 시청 최적화. 알고리즘 노출 기반.

```
대표 플랫폼:
  - YouTube Shorts (30-60초 권장)
  - TikTok (15-60초, 최대 10분)
  - Instagram Reels (15-90초)

영상기획 AI 에이전트 적용:
  - format: shorts_30s / shorts_60s / shorts_90s
  - 사용자 80%가 첫 영상으로 숏폼 시도 (예상)
```

---

## 1. 첫 3초 Hook 패턴

숏폼의 생사는 **첫 3초**에 결정된다. 시청자 retention curve의 첫 절벽이 0-3초 구간.

### 1.1 질문형 Hook

```
- "왜 ____는 ____일까?"
- "이거 알고 계셨어요?"
- "1년 동안 ____ 해봤더니?"

효과: 시청자 호기심 유발 (열린 질문)
주의: 너무 일반적이면 무시
```

### 1.2 충격형 Hook

```
- "______가 사라졌어요"
- "이게 ______ 한 결과입니다"
- 통계 + 의외성 ("100명 중 87명이...")

효과: 강한 retention
주의: 광고 단어 회피 (output_schema §14)
```

### 1.3 약속형 Hook

```
- "30초 안에 ____ 알려드릴게요"
- "이 영상 보면 ______ 해결됩니다"

효과: 가치 명확
주의: 약속을 못 지키면 dislike ↑
```

자세한 hook 패턴은 `hook_patterns.md` 참조.

---

## 2. 표준 구조: Hook → Tension → Reveal → CTA

```
0-3s   Hook        시청 유지 잠금
3-15s  Tension     문제 / 갈등 / 호기심 증폭
15-45s Reveal      해결 / 답 / 인사이트
45-60s CTA         좋아요 / 팔로우 / 댓글 / 공유 유도
```

### 2.1 Tension 단계

```
- 문제를 더 구체적으로 (페인 포인트)
- 시청자가 "그래서 어떻게 됐는데?" 궁금해지도록
- 답을 늦추고 정보 흘리기 (drip)
```

### 2.2 Reveal 단계

```
- Hook의 약속 이행
- 시각 자료 / B-roll로 강화
- 짧고 명확하게 (15-30초)
```

### 2.3 CTA 단계

```
강한 CTA:
  - "팔로우하면 다음 편 못 놓쳐요"
  - "댓글로 ____ 알려주세요"
  - "친구 태그하기"
약한 CTA:
  - "좋아요 부탁드려요" (효과 ↓)
```

CTA는 영상기획 AI가 사용자의 brand 톤에 맞춰 변형 제안.

---

## 3. 플랫폼별 차이

### 3.1 YouTube Shorts

```yaml
길이: 30-60초 권장 (60초 넘으면 long-form으로 분류)
세로: 9:16
알고리즘: 시청 시간 + retention + 좋아요
장점: 검색 + 추천 동시
단점: 알고리즘 변동 빠름
```

### 3.2 TikTok

```yaml
길이: 15-60초 (60초 이상도 가능)
세로: 9:16
알고리즘: For You Page (FYP), 첫 5초 retention
장점: 폭발적 노출 가능
단점: 트렌드 사이클 빠름
```

### 3.3 Instagram Reels

```yaml
길이: 15-90초
세로: 9:16
알고리즘: 팔로워 + 추천 비중 균형
장점: 기존 IG 팔로워 활용
단점: TikTok 대비 도달 ↓
```

영상기획 AI는 사용자가 플랫폼 선택 시 해당 가이드를 추가 prompt에 주입 (Phase 2+ metadata filter).

---

## 4. 자주 쓰는 포맷 (영상기획 카드 후보)

| 포맷 | 설명 | 예시 hook |
|---|---|---|
| vlog snippet | 일상 단편 | "오늘 ____ 해본 결과" |
| tutorial | 30초 만에 가르쳐주기 | "____ 하는 가장 빠른 방법" |
| before/after | 변화 보여주기 | "1개월 ____ 한 차이" |
| reaction | 반응 영상 | "이거 보면 누구나 ____ 함" |
| myth busting | 통념 깨기 | "____ 는 거짓말입니다" |
| listicle | 순위/리스트 | "____ TOP 5" |
| storytelling | 짧은 이야기 | "그때 제가 ____ 했었거든요" |
| demo | 즉시 보여주기 | "이게 ____ 입니다" (Hook 직후 demo) |

---

## 5. 광고 단어 회피 가이드

`output_schema.md §14` ad_phrase_blocklist 적용:

```
1차 차단 (검색/CTR 저하):
  - "최저가" / "100%" / "완벽한" / "최고의" / "보장" / "절대"
  → Critic agent가 reject

2차 경고 (사용 신중):
  - "놓치지 마세요" / "지금 바로" / "마지막 기회"
  → 가능하면 대체 표현
```

### 5.1 대체 표현 예시

```
"최저가로 ____" → "합리적인 가격으로 ____"
"100% 효과" → "많은 분이 효과 보셨어요"
"놓치지 마세요" → "이번에만 가능한 ____"
"완벽한 ____" → "충분히 ____한"
```

---

## 6. retention curve 패턴 (Phase 4+ 데이터 누적 후 보강)

```
일반적 retention curve:
  0-3s:   90% 유지 (hook 통과)
  3-15s:  70-80% (tension)
  15-45s: 50-65% (reveal 도달)
  45-60s: 40-55% (CTA 도달)
  완주율 (60s): 40-50%

좋은 영상:
  완주율 ≥ 60% (목표)

낮은 영상:
  완주율 < 30% (hook 또는 tension 약함)
```

영상기획 AI가 추가적으로 retention 예측 모델 도입은 Phase 7+ 검토.

---

## 7. 영상기획 AI 사용 시 체크리스트

Planning agent가 숏폼 plan 생성 시 자동 점검:

```yaml
hook_check:
  - 0-3초 hook 명확한가?
  - hook 패턴 분류됨? (hook_patterns.md 참조)

structure_check:
  - Hook → Tension → Reveal → CTA 4단계 모두 포함?
  - 각 단계 길이 합리적?

cta_check:
  - CTA 1개 이상?
  - 광고 단어 회피?

platform_check:
  - 플랫폼별 길이 제약?
  - 세로 포맷 가정?

brand_check:
  - 사용자 brand 톤 일치?
  - brand_memory 활용?
```

Critic agent (P-007) 가 8차원 평가에서 자동 점검.

---

## 8. Phase 4+ 보강 예정 항목

```
- retention curve 데이터 기반 패턴 분석
- 플랫폼 알고리즘 변화 트래킹 (월간 업데이트)
- 사용자 brand별 successful pattern 분석 (개인화)
- 트렌드 키워드 카탈로그 (시즌별)
- demo 영상 전략 (B-roll 가이드)
- 한국어 vs 영어 hook 비교
- 음악 / 사운드 효과 가이드 (Phase 7+ 음악 라이선스)
```

---

## 9. 실패 패턴 (회피 대상)

```
1. 도입이 길다 (5초 넘는 hook → retention ↓)
2. 타겟이 불명확 ("누구에게나 도움 되는" → 누구에게도 안 됨)
3. 정보 과부하 (30초에 5개 팁 → 다 기억 못 함)
4. CTA 없음 (좋은 영상도 행동 유도 없으면 효과 ↓)
5. 광고 단어 남발 ("최고", "100%" → 알고리즘 페널티)
6. brand 일관성 결여 (이번엔 정중, 다음엔 캐주얼)
7. 첫 3초 정적 (움직임 없는 고정 화면)
```

Critic agent의 8차원에 각 실패 패턴이 매핑됨.

---

## 10. Open Questions / 보강 예정

1. 한국어 숏폼 retention curve 데이터 — Phase 4+ 사용자 데이터 누적 후 정량 분석.
2. 플랫폼별 첫 3초 retention 차이 — TikTok vs Shorts vs Reels 정량 비교.
3. AI 생성 hook의 실제 retention 효과 — 사용자 영상 결과 데이터 회수.
4. 광고 단어 회피 시 CTR 변화 — 정량 측정.
5. 길이 30s vs 60s vs 90s 효과 차이 — 도메인별 (vlog vs tutorial).

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. Hook 첫 3초 / 표준 구조 / 플랫폼별 차이 /
                      자주 쓰는 포맷 / 광고 단어 회피 / 실패 패턴 정리.
```
