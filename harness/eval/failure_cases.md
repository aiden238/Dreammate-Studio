# failure_cases.md — 영상기획 결과물 실패 케이스 모음

> 위치: `eval/failure_cases.md`
> 작성: 2026-05-26 (Phase 1 진입 시 — 5 케이스 시드)
> 목적: AI가 만든 영상기획안이 **품질 미달**인 패턴을 누적.
>       Critic Agent 평가 기준 학습 + 회귀 차단용.
> 참조: `eval/golden_set.md` (정답), `eval/failure_taxonomy.md` (분류 체계)

---

## 0. 사용 방법

```
golden_set.md → 통과해야 할 정답 케이스
failure_cases.md → 거부해야 할 실패 케이스  ← 본 파일
failure_taxonomy.md → 실패 사유 분류 체계
```

각 케이스는 다음을 포함:
- 입력 (input)
- AI 출력 (output)
- 왜 실패인가 (failure reason)
- 어떤 차원에서 미달인가 (dimension)
- 개선 방향 (improvement direction)

---

## 1. failure_taxonomy 매핑

| 분류 | 정의 | 본 파일 케이스 |
|---|---|---|
| **F1. 후킹 약함** | 첫 3초 시청 유도 실패 | FC-001 |
| **F2. 타겟 모호** | 시청자 정의 부정확 | FC-002 |
| **F3. 실행 불가능** | 촬영 / 편집 비현실적 | FC-003 |
| **F4. AI스러움** | "혁신적", "최고의" 광고 표현 | FC-004 |
| **F5. 브랜드 톤 위반** | Brand Memory 불일치 | (Phase 4+ 추가) |
| **F6. Hallucination** | 사실관계 오류 | FC-005 |
| **F7. 형식 오류** | output_schema 미준수 | (구현 Eval에서 잡힘) |
| **F8. 안전성 위반** | PII 노출, 광고 차단 단어 | (security_eval 영역) |

---

## 2. Phase 1 시드 실패 케이스 (5개)

### FC-001 — 후킹 약함

```yaml
input: "20대 직장인 대상 재테크 유튜브 채널 첫 영상 기획"
output_excerpt:
  title: "재테크의 기본"
  hook: "안녕하세요, 오늘은 재테크에 대해 알아보겠습니다."
  first_3s: "재테크는 중요합니다."

failure_reason: |
  첫 3초에 시청자가 스크롤할 이유가 너무 명확.
  "안녕하세요" 형 인사로 시작 = 알고리즘에 죽음.
  
dimension: hook_quality
score_expected: hook < 2/5

improvement_direction: |
  - 질문형 hook: "월급 300인데 5년째 통장 잔고 0인 이유?"
  - 충격적 사실: "30대 평균 자산이 X원밖에 안 되는 이유"
  - 부정 hook: "재테크 책 사지 마세요"
  
critic_should_flag:
  - hook.score: 1
  - hook.suggestion: "첫 3초 hook 재작성 필수"
```

---

### FC-002 — 타겟 모호

```yaml
input: "건강 관련 쇼츠 만들고 싶어"
output_excerpt:
  target_audience: "건강에 관심 있는 모든 사람"
  age_range: "10대 ~ 60대"
  pain_point: "건강을 챙기고 싶어함"

failure_reason: |
  타겟이 너무 광범위 = 누구도 타겟이 아님.
  10대와 60대의 건강 관심사는 정반대.
  
dimension: target_fit
score_expected: target_fit < 2/5

improvement_direction: |
  - 구체화: "30대 후반 야근 잦은 사무직"
  - pain_point 구체화: "허리 통증 + 시간 부족"
  - 행동 구체화: "5분 안에 데스크에서 할 수 있는 스트레칭"

critic_should_flag:
  - target_fit.score: 1
  - target_fit.suggestion: "타겟 페르소나 1명으로 축소"
```

---

### FC-003 — 실행 불가능

```yaml
input: "1인 운영 카페 홍보 영상"
output_excerpt:
  shots:
    - "드론 항공 촬영으로 카페 전경"
    - "슬로우모션 라떼 푸어링 8K 해상도"
    - "야간 타임랩스 6시간 분량"
  estimated_budget: "200만원+"
  estimated_time: "촬영 3일 + 편집 1주"

failure_reason: |
  1인 운영자가 드론 + 8K + 6시간 타임랩스 불가능.
  예산 200만원도 1인 카페 홍보 영상에 과도.
  
dimension: execution_feasibility
score_expected: execution_feasibility < 2/5

improvement_direction: |
  - 스마트폰 1대로 가능한 샷만 제안
  - 1시간 안에 촬영 완료 가능한 구성
  - 무료 편집 앱(CapCut 등) 활용 가정
  - 예산 0원 옵션 추가

critic_should_flag:
  - execution_feasibility.score: 1
  - execution_feasibility.suggestion: "1인 + 스마트폰 + 0원 가정으로 재작성"
```

---

### FC-004 — AI스러움 (광고적 표현)

```yaml
input: "수제 비누 브랜드 첫 영상"
output_excerpt:
  hook: "혁신적인 수제 비누의 최고의 경험을 만나보세요."
  voiceover: "최첨단 기술과 자연의 만남, 완벽한 피부를 위한 최선의 선택."
  cta: "지금 바로 구매하세요! 한정 수량!"

failure_reason: |
  "혁신적", "최고의", "완벽한", "최선의" = 광고 차단 단어.
  수제 비누 브랜드에 "최첨단 기술" = 거짓말.
  CTA가 홈쇼핑 톤 = 영상기획 가치 훼손.
  
dimension: brand_consistency + ai_likeness
score_expected: overall < 2/5

improvement_direction: |
  - 광고 차단 단어 사용 금지 (PROJECT_STATE confirmed_decision #9)
  - 구체적 사실로 대체: "5가지 식물 오일 / 24시간 숙성"
  - CTA는 가치 중심: "내 피부에 맞는 비누 찾기"
  - 사람 톤: "처음 만들었을 때 실패한 이야기"

critic_should_flag:
  - brand.score: 1
  - blocked_words_detected: ["혁신적", "최고의", "완벽한", "최선의", "최첨단"]
  - suggestion: "광고 표현 전면 재작성 + 구체 사실로 대체"
```

---

### FC-005 — Hallucination (사실 오류)

```yaml
input: "스타벅스 신메뉴 출시 영상 기획"
output_excerpt:
  facts_used:
    - "스타벅스는 1971년 시애틀에서 창업"  # 사실
    - "한국 진출은 1999년 이대 1호점부터"   # 사실
    - "신메뉴 출시 때마다 전국 평균 매출 30% 상승"  # 거짓 (출처 없음)
    - "한국인 50%가 스타벅스 회원"  # 거짓
  source: null

failure_reason: |
  검증 불가능한 통계를 사실처럼 제시.
  source / reference 없는 수치 = hallucination.
  광고/PR 영상에서 거짓 통계 = 법적 리스크.
  
dimension: factual_accuracy + hallucination
score_expected: overall < 2/5

improvement_direction: |
  - 검증 불가 통계 제거 또는 "[출처 필요]" 마킹
  - RAG Lite 검색 결과에서 가져오지 않은 수치는 사용 금지
  - body.rag_references 비어있는 경우 → 통계 사용 금지
  - Critic이 수치 등장 시 검증 단계 추가

critic_should_flag:
  - factual_accuracy.score: 1
  - hallucination_detected: true
  - suggestion: "RAG references 미존재 통계 전면 제거"
```

---

## 3. 케이스 사용 방법

### 3.1 Critic Agent 학습

각 FC-XXX는 Critic이 **반드시 flag해야 할** 패턴.  
Slice 3 (Critic Agent) 구현 시:

```python
# 의사 코드
def test_critic_flags_fc001():
    output = call_critic(FC_001_input, FC_001_output)
    assert output["scores"]["hook"] <= 2
    assert "hook" in output["suggestions"][0]
```

### 3.2 회귀 차단

```
새 prompt version 배포 시:
1. golden_set 11개 모두 통과 확인 (정답)
2. failure_cases 5개 모두 차단 확인 (실패)
3. 둘 중 하나라도 실패 = 배포 차단
```

### 3.3 사람 리뷰 (Phase 1 종료 시)

5개 FC를 사람이 직접 보고:
- AI가 정말 거부했는지
- 거부 이유가 맞는지
- 새 failure pattern 발견됐는지

→ `eval/human_review_rubric.md` 절차 사용.

---

## 4. 추가 정책

### 4.1 신규 FC 추가 절차

```
1. 사용자 또는 Critic이 실패 패턴 발견
2. eval/regression_results/에 raw output 저장
3. FC-XXX 형식으로 본 파일에 추가
4. failure_taxonomy.md F1~F8 중 분류
5. 다음 회귀 테스트에 포함
```

### 4.2 누적 목표

| Phase | 목표 케이스 수 |
|---|---|
| Phase 1 (현재) | 5 (FC-001~005) |
| Phase 4 (Critic 완성) | 15 |
| Phase 7 (RAG 완성) | 25 |
| Phase 10 (배포 직전) | 40 |

---

## 5. 관련 문서

- `eval/golden_set.md` — 정답 케이스 (GS-001~GS-011)
- `eval/failure_taxonomy.md` — 실패 분류 체계 (F1~F8)
- `eval/video_planning_eval.md` — 종합 평가 5차원
- `eval/hook_quality_eval.md` — F1 관련
- `eval/target_fit_eval.md` — F2 관련
- `eval/execution_feasibility_eval.md` — F3 관련
- `eval/brand_consistency_eval.md` — F5 관련
- `ai_system/agents/critic_agent.md` — Critic 정의
- `docs/contracts/llm_security_contract.md` — F8 관련

---

## 6. 변경 이력

- 2026-05-26: Phase 1 진입 시 최초 작성, FC-001~FC-005 시드
