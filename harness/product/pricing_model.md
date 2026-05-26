# pricing_model.md — 가격 모델

> 위치: `product/pricing_model.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/rate_limit_policy.md`, `docs/contracts/tech_stack_contract.md` §2.4 (LLM 단가)
> 참조: `product/mvp_scope.md`, `product/roadmap.md`

---

## 0. 가격 모델 개요

```
MVP (Phase 1~10): 무료 (사용량 제한 있음)
Phase 11+:        유료 tier 도입 검토 (paid / team)
Phase 21+:        Enterprise / Custom RAG tier 검토
```

본 문서는 가격 결정의 **근거 + 정책 + 확장 시나리오**를 다룬다. 실제 결제 구현은 Phase 12+ (`product/roadmap.md`).

---

## 1. MVP 가격 정책 (Phase 1~10)

### 1.1 무료 (사용량 제한)

```
anonymous tier (비로그인 또는 게스트):
  - 일일 영상기획: 5건 / 24시간
  - 분당 요청: 10건 / 분
  - 한도 도달 시: E-RL-005 / "오늘 만들 수 있는 영상 수에 도달했어요"
  - 사용 기록: IP 기반 임시 저장 (계정 미생성 시)

free tier (가입 사용자):
  - 월간 영상기획: 50건 / 30일
  - 일일 영상기획: 10건 / 24시간
  - 분당 요청: 30건 / 분
  - 한도 도달 시: E-RL-001 / "이번 달 사용량 한도에 도달했어요"
  - Brand 슬롯: 최대 3개
  - Series 슬롯: Brand당 최대 5개
  - Video Project 영구 저장
```

→ `docs/contracts/rate_limit_policy.md` 정합

### 1.2 결제 미구현 결정 이유

```
1. MVP는 사용자 가설 검증 우선.
2. 결제 구현 (Stripe / 토스페이먼츠) 자체가 Phase 1개 분량.
3. 무료 운영으로 사용자 100명 확보 → 가격 민감도 측정 후 유료 도입.
4. LLM 비용은 rate_limit으로 통제 (anonymous 5건/일, free 50건/월).
5. 결제 도입 전에 결제 의향 측정 (가입 시 "유료 도입되면 가격 얼마까지?" 설문).
```

### 1.3 MVP 비용 통제 (사용자당)

```
가정:
  - 영상 1건당 LLM 호출: 약 4회 (Intent + Planning x3 + Critic + Rewriter)
  - 호출당 평균 토큰: input 2000 + output 1000
  - 모델 mix: gpt-4o-mini 75% + gpt-4o 25% (Critic)

영상 1건 비용 추정:
  - gpt-4o-mini × 3 호출:
    input 6000 × $0.15/1M  = $0.0009
    output 3000 × $0.60/1M = $0.0018
    합계 = $0.0027
  - gpt-4o × 1 호출 (Critic):
    input 2000 × $2.50/1M  = $0.0050
    output 1000 × $10.00/1M = $0.0100
    합계 = $0.0150
  - embedding (RAG): 약 $0.0001
  - 영상 1건 총: 약 $0.018 (편당 약 24원)

free tier (50건/월) 사용자 비용:
  - 50 × $0.018 = $0.90/월 (1080원)
  - 인프라 + Sentry + Supabase: 사용자당 약 $0.30/월
  - 사용자당 월 총 비용: 약 $1.20 (1440원)
```

→ MVP 무료 운영 시 1000명 사용자당 월 비용 약 $1200 (140만원). 자금 부담 가능 수준.

→ `docs/contracts/tech_stack_contract.md` §2.4 단가 정합

---

## 2. Phase 11+ 유료 도입 검토 (안)

본 안은 **결정이 아니며**, Phase 11+ 진입 시 데이터 기반 확정.

### 2.1 paid tier ($9.99/월 — 12,000원/월 추정)

```
- 월간 영상기획: 500건 (free tier 10배)
- 일일 영상기획: 50건
- 분당 요청: 60건
- Brand 슬롯: 무제한
- Series 슬롯: 무제한
- 우선 처리 큐 (Phase 13+ 비동기 시)
- Sentry / log retention 30일
- 우선 고객 지원
```

비용 마진 계산 (paid tier):

```
사용자 LLM 비용 (500건/월): 500 × $0.018 = $9.00
인프라:                     $0.30/월
운영 (CS 등):                $1.00/월
사용자당 비용 합계:           $10.30/월
사용자 지불:                  $9.99/월
마진:                         -$0.31 (~3% 손해)
```

→ paid tier는 LLM 비용에 거의 marginal. 인플레이션 / 모델 가격 인하 가정 시 흑자 전환.
→ 가격 인상 또는 500건 → 300건 조정 옵션 보유.

### 2.2 team tier ($29.99/월 — 36,000원/월 추정)

```
- 월간 영상기획: 2000건 (paid 4배)
- 사용자 5명 단위 (협업, Phase 15+)
- 팀 단위 Brand 공유
- 상세 사용량 대시보드
- API 접근 (Phase 17+)
```

비용 마진 (team tier, 5명 가정):

```
LLM 비용:        2000 × $0.018 = $36.00
인프라:          $2.00/월
운영:            $5.00/월
사용자당 비용:    $43.00/월
사용자 지불:     $29.99/월
마진:            -$13.01 (~30% 손해, 비합리)
```

→ team tier 가격은 Phase 11+ 진입 시 재산정 필요. **현재 안은 placeholder.**

### 2.3 enterprise tier ($199.99~999.99/월)

```
- 무제한 영상기획
- 무제한 사용자
- Custom RAG (사용자 자체 데이터)
- SLA 99.9% / 우선 기술 지원
- on-premise 옵션 (Phase 21+)
- Audit log 1년 보장
```

→ Phase 21+ Custom RAG와 연동. 본 문서에서는 골격만.

---

## 3. 가격 결정 기준

### 3.1 결정 원칙

```
1. LLM 비용 + 인프라 + 운영 비용을 모두 합한 사용자당 비용을 기준선으로.
2. 마진은 paid 30% / team 40% / enterprise 60% 목표.
3. 사용자 가격 민감도 (PSM: Price Sensitivity Meter) 데이터로 조정.
4. 경쟁사 (ChatGPT Plus $20/월) 대비 절반 이하 위치 (paid tier $9.99).
5. 한국 시장 친화 가격 (만원 이하 또는 1.2만원).
```

### 3.2 가격 민감도 측정 (Phase 10+)

```
조사 항목:
- "지금 무료로 쓰는데 유료가 되면 얼마까지 지불 가능?"
- "월 영상 50건이 적정? 부족? 과한가?"
- "팀 기능이 있다면 추가 지불 의향?"

조사 시점:
- Phase 10 Beta 출시 후 1개월 시점.
- 사용자 100명 이상 도달 시.

조사 방법:
- 인앱 설문 (선택, 응답 시 무료 영상 +5건 보상)
- 사용자 인터뷰 (10명 정도)
```

### 3.3 Phase 21+ 가격 재산정

```
LLM 가격 인하 추세 (GPT-4 출시 시 vs 현재 80% 인하):
- Phase 21+ 시점 gpt-4o-mini가 현재 1/5 수준일 가능성.
- 그 시점 free tier 영상 수 증가 / paid tier 가격 인하 검토.

자체 모델 / Custom RAG 도입:
- 비용 구조가 변경됨 (LLM 호출 비용 ↓ 인프라 비용 ↑).
- 가격 모델 재설계 필요.
```

---

## 4. 사용자 확보 전략 (Free → Paid Conversion Funnel)

### 4.1 Conversion 목표

```
- 가입 사용자 1만 명 (Phase 11+ 시점) 가정.
- free → paid 전환율 5% (= 500명).
- paid 매출 = 500 × $9.99 = $4995/월 (약 600만원/월).
- 이 시점 free tier 운영 비용 = 10000 × $1.20 = $12000/월.
- 적자 운영. 사용자 5만 도달 또는 paid 전환율 15% 도달 시 흑자.
```

### 4.2 Conversion 트리거

```
다음 시점에 paid 추천 알림:
1. free tier 월 50건 한도 80% 도달 시 (1주 전 알림).
2. Brand 슬롯 3개 다 채웠을 때 ("Brand를 더 만들고 싶으세요?").
3. 90일 연속 사용자 (높은 retention).
4. revise 한계 도달 빈도 높은 사용자 (max_revise=2, paid는 4 검토).
```

### 4.3 Conversion 인센티브

```
- 첫 달 50% 할인 ($4.99).
- 연간 결제 시 20% 할인 ($95.90/년).
- 친구 추천 시 1개월 무료.
```

→ 단, 본 인센티브는 Phase 12+ 결제 구현 시점에 재검토.

---

## 5. 사용량 한도 위반 처리

```
무료 사용자 한도 도달 시:
1. UI: "오늘 / 이번 달 사용량 한도에 도달했어요"
2. 옵션: "내일 다시 만나요" (대기) / "paid로 전환" (Phase 12+ 이후)
3. anonymous → free 가입 유도 ("가입하면 10배 더 사용 가능해요")
4. free → paid 가입 유도 (Phase 12+)

paid 사용자 한도 도달 시 (Phase 12+):
1. "이번 달 사용량 한도에 도달했어요. 다음 달까지 +50건 추가하시겠어요?"
2. 옵션: 일회성 $4.99 추가 (100건) / 다음 달 대기
3. team tier 추천
```

→ `docs/contracts/error_response_contract.md` §4.5 (E-RL-001~005)

---

## 6. 환불 / 취소 정책 (Phase 12+)

```
- 첫 결제 후 7일 내 100% 환불 (사유 무관).
- 월 결제: 다음 결제일 전 취소 시 다음 달부터 미결제.
- 연 결제: 사용량 50% 이하 미사용 시 비례 환불.
- 환불 신청은 인앱 또는 이메일 (CS 평균 응답 48시간).
- 환불 사유 통계 누적 (Phase 13+ 개선 시그널).
```

→ 결제 도입 시 토스페이먼츠 / Stripe 표준 정책 따름.

---

## 7. 가격 모델 변경 절차

가격 변경은 `contract-change` Skill 절차 + 사용자 영향이 크므로 추가 절차.

```
1. contract-change 제안서 작성
2. multi-llm-validation 권장 (가격 결정은 중대 사안)
3. 기존 사용자 영향 분석:
   - 가격 인상 시: 기존 paid 사용자는 grandfather (6개월 유지) 또는 30일 사전 공지.
   - 한도 축소 시: 30일 사전 공지 + 미사용분 환불.
4. 사용자 공지 (이메일 + 인앱)
5. PROJECT_STATE.md "최근 변경" 기록
```

---

## 8. 측정 지표 (가격 관련)

```
1. ARPU (Average Revenue Per User) — Phase 12+
   - 목표: $1.00/월 (사용자 전체 평균, free 포함)

2. Free → Paid 전환율
   - 목표: 5% (Phase 12+ 6개월 시점)

3. Churn rate (월간 paid 해지율)
   - 목표: 5% 이하

4. 결제 의향 (인앱 설문)
   - 목표: 가입자의 30% 이상이 "유료로 전환 의향" 응답

5. 한도 도달 빈도 (free tier)
   - 한도 도달 사용자 비율: 20% 이상이면 한도 너무 낮음, 5% 이하면 충분
```

→ `eval/regression_eval.md` cost section과 정합

---

## 9. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 10+: §3.2 가격 민감도 조사 실 데이터로 갱신.
Phase 12+: §4 Conversion funnel 실 데이터로 검증.
Phase 15+: §2.2 team tier 가격 재산정 (협업 기능 도입 후).
Phase 21+: §2.3 enterprise tier 본격 설계 + Custom RAG 가격.
연 1회:    LLM 비용 변동 반영 + 전체 마진 재계산.
```

---

## 10. Open Questions

1. paid tier $9.99/월이 한국 시장에 적절한지 — PSM 조사 후 결정.
2. ChatGPT Plus $20/월 대비 절반 위치가 적절한지 vs 동일 가격이 신뢰감 줄 가능성.
3. team tier 가격이 손해 구조 — 가격 인상 vs 영상 수 축소 결정.
4. 결제 미구현 기간 (Phase 11까지) 동안 운영 비용 부담 — 자금 확보 계획.
5. enterprise tier 진입 트리거 — 사용자 요청 발생 vs 우리가 사전 제안.
6. Custom RAG tier 가격 — 사용자 데이터 양 vs 정액제.

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      MVP 무료 + 사용량 제한, Phase 11+ paid/team tier 안,
                      비용 마진 계산, conversion funnel, 가격 변경 절차.
```
