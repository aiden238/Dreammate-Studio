# human_review_rubric.md — 운영자 수동 검토 가이드

> 위치: `eval/human_review_rubric.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `eval/video_planning_eval.md` (8 차원 채점)
> 참조: `docs/contracts/rag_data_contract.md` §4 5단계 승격 (candidate_knowledge)
> 참조: `meta/human_review_policy.md` (운영자 정책 본체)

---

## 1. 목적

LLM 자동 채점(P-007)과 룰 기반 검사로 거르지 못하는 케이스를 운영자가 수동 검토한다. 본 문서는 검토 체크리스트 / 점수 표 / 코멘트 표준 / SLA를 정형화해, 운영자가 일관된 기준으로 빠르게 결정할 수 있도록 한다. 5단계 RAG 승격(`evaluated → approved`)의 borderline 항목과 신고된 plan이 주 대상.

---

## 2. 검토 차원 (5 개)

### 2.1 content_quality — 콘텐츠 품질

```
정의: 결과물 자체의 기획적 완성도.
측정: P-007 8 차원의 운영자 재채점 (LLM 점수와의 diff 기록).
0점: 다듬어도 사용 불가
3점: 약간 다듬으면 사용 가능
5점: 즉시 사용 가능
```

### 2.2 safety — 안전성

```
정의: 보안 / 광고 단어 / 법적 이슈 / 부적절 콘텐츠.
측정: 광고 단어 1차/2차 + 저작권 위험 + 차별/혐오 표현 + PII 잔존.
0점: 1개라도 발견 (자동 reject)
5점: 없음
운영자가 본 차원에서 0점 부여 시 무조건 reject.
```

### 2.3 brand_fit — 브랜드 적합도

```
정의: brand_memory와의 일관성을 운영자가 재검증.
측정: success_patterns 자연 인용 / avoid_phrases 부재 / 톤 일관.
0점: 충돌
3점: 충돌 없음, 강화 없음
5점: brand 강화
```

### 2.4 promotion_value — 학습 신호 가치 (RAG 승격 시)

```
정의: 본 항목이 다른 사용자의 기획에 참고할 가치가 있는가.
측정: 일반화 가능성 + 구체성 + 신선함.
0점: 너무 특수 또는 너무 일반
3점: 일부 패턴 추출 가능
5점: 분명한 패턴 (다른 brand에도 적용 가능)
주의: rag_data_contract §4.3 자동 승격 미충족 시 본 차원이 결정적.
```

### 2.5 user_response_risk — 사용자 반응 리스크

```
정의: 본 결과를 사용자가 봤을 때 부정 반응(불쾌/실망/오해) 가능성.
측정: 톤 적절성 + 사용자 입력 의도 보존 + 광고적 거리감.
0점: 사용자 항의 예상
3점: 일부 불만 가능
5점: 사용자 만족 예상
```

### 2.6 depth_actionability — 기획 깊이·실행가능성 (사람 채점, 0~1)

> Phase 12 S1 (2026-06-02, CC-011) **additive** 추가. §2.1~2.5 (content_quality / safety /
> brand_fit / promotion_value / user_response_risk) 정의·스케일은 **무변경**.
> 본 차원은 `eval/video_planning_eval.md` §2.A.1 depth_actionability 와 **동일 축** — 사람이 직접 0~1 로 매긴다.
> ★ 0~5 가 아닌 **0~1 실수 스케일** (§2.1~2.5 의 0~5 평균 산식 human_avg 에는 미포함 — 별도 기록).

```
정의: 출력이 "창작자가 추가 질문 없이 바로 촬영·편집에 착수할 만큼 구체적이고 실행 가능한가"를
      사람이 판단. 현재 compact 출력(plan 골격)이 바로 쓰기엔 얼마나 얕은지 / 확장 출력이 얼마나
      깊은지를 사람 눈으로 채점.
측정 (video_planning_eval §2.A.1 과 동일): hook 변형 수 / beat 의 화면·대사·자막·목적 구체성 /
      샷·B-roll / 썸네일·제목·CTA / 레퍼런스 / 길이 변형 포함도 / 전반 실행가능성.
채점 스케일: 0.0 ~ 1.0 (실수).
  0.2  매우 얕음 — 현 compact 수준 (plan 골격만, 바로 찍기엔 추가 질문 다수).
  0.6  보통 — beat 화면·목적은 구체적이나 샷/B-roll/썸네일/제목/CTA/레퍼런스/길이변형 일부 누락.
  1.0  매우 구체적 — hook 변형 + beat 4요소(화면/대사/자막/목적) + 샷·B-roll + 썸네일·제목·CTA
       + 레퍼런스 + 길이 변형까지 포함, 추가 질문 없이 바로 촬영·편집 착수 가능.
용도: Phase 12 검증 — compact vs 확장(B안) 출력의 깊이 격차를 사람 채점으로 정량화.
     plan 생성 결과(P-006/최종 output) 검토 시 채점. RAG 승격/신고 검토에는 선택적.
주의: 자동(LLM/룰) 채점이 의미있게 못 매기는 차원이므로 사람 채점이 1차 기준 (mock 러너 미채점).
```

---

## 3. 입력 / 출력 형식

### 3.1 입력 (검토 큐 항목)

```yaml
review_item_id: uuid
review_type:
  - "rag_promotion"               # candidate_knowledge evaluated → approved
  - "user_report"                 # 사용자 신고
  - "critic_borderline"           # P-007 verdict=revise이지만 LLM이 모호
  - "ad_phrase_violation"         # 자동 재생성 후에도 위반
  - "forced_approve_audit"        # revise_round=2 강제 승격 사후 검토
context:
  user_id: uuid (마스킹)
  video_id: uuid
  plan_or_candidate: { ... }
  llm_scores: { ... }              # 자동 채점 결과 (참고용)
sla_due_at: ISO8601                # SLA 마감 시각
```

### 3.2 출력 (검토 결과)

```yaml
review_id: uuid
reviewer: user_id (운영자)
decision: "approve | reject | revise_request | escalate"
human_scores:
  content_quality: 0~5
  safety: 0~5
  brand_fit: 0~5
  promotion_value: 0~5
  user_response_risk: 0~5
human_avg: 0~5                       # §2.1~2.5 (0~5) 5 차원 평균 — §2.6 미포함
depth_actionability: 0.0~1.0         # §2.6 (Phase 12 S1, CC-011) — plan 깊이·실행가능성, 별도 0~1 축. plan 검토 시 기록(선택)
comment_standard: "string (§5 표준 코멘트 참조)"
comment_free: "string (자유 메모, 100자 이내)"
diff_with_llm: { llm_score - human_score per 차원 }
reviewed_at: ISO8601
```

---

## 4. 자동 평가 vs 수동 평가

본 문서는 **수동 평가 주도**. 자동 평가는 사전 정보 / 참고 점수로만 사용.

```
사전 자동:
  - LLM 점수 (P-007) — 운영자 비교용
  - 광고 단어 검사 결과 — 운영자가 즉시 확인 가능
  - 룰 기반 검사 (저작권 키워드, PII 패턴) — pre-flag

운영자 주도:
  - 최종 결정 (approve/reject/revise)
  - human_scores 5 차원 채점
  - comment_standard 선택
  - 누적 패턴 회고 (meta-retrospective)
```

---

## 5. 코멘트 표준 (선택형)

자유 메모는 100자 이내. 그 외는 아래 표준 코멘트에서 선택해서 카운트 누적.

```
approve 계열:
  A-01  "기준 충족, 그대로 승인"
  A-02  "경계선이나 사용자 가치 명확"
  A-03  "운영자 추가 코멘트 첨부 후 승인"

reject 계열:
  R-01  "광고 단어 위반"
  R-02  "저작권 위험"
  R-03  "타겟 불명확"
  R-04  "메시지 분산"
  R-05  "실행 불가"
  R-06  "사용자 신고 사유 타당"
  R-07  "brand_memory 충돌"
  R-08  "PII 잔존"

revise_request 계열:
  V-01  "hook 다시 만들기 요청"
  V-02  "flow 시간 재조정"
  V-03  "톤 변경 필요"
  V-04  "추가 정보 요청 (missing_info)"

escalate 계열:
  E-01  "법적 검토 필요"
  E-02  "운영진 합의 필요"
  E-03  "Phase 정책 충돌"
```

---

## 6. SLA (Service Level Agreement)

### 6.1 검토 응답 시간

```
review_type            SLA (initial response)   SLA (final decision)
rag_promotion          24시간                    72시간
user_report            6시간                     24시간
critic_borderline      24시간                    48시간
ad_phrase_violation    12시간                    24시간
forced_approve_audit   48시간                    7일 (사후 audit)
```

### 6.2 SLA 초과 정책

```
- 24시간 초과: Slack #ops-alert 자동 알림
- 72시간 초과 (rag_promotion): candidate_knowledge.status='rejected' + rejected_reason='review_timeout' (rag_data_contract §4.3)
- user_report 6시간 초과: 자동 임시 plan 노출 차단 + 사용자에게 "검토 중" 안내
```

### 6.3 검토량 모니터링

```
- 일 검토 건수 / 운영자
- 평균 검토 시간
- LLM-운영자 점수 diff 평균 (캘리브레이션)
- 거절 사유 분포 (R-01 ~ R-08)
```

---

## 7. RAG 승격 검토 (rag_data_contract 연동)

`candidate_knowledge.status` 5단계 중 `evaluated → approved`의 borderline 항목이 주 대상.

```
자동 승격 조건 미충족 (rag_data §4.3):
  - eval_score 0.7~0.85
  - source_kind ∈ {user_choice, user_feedback}
  - 또는 dimensions에 < 3 항목 1개 이상
  → 운영자 수동 검토 필수

운영자 검토 단계:
  1. content 본문 확인 (PII 마스킹 적용 후)
  2. metadata 확인 (brand_id, source_kind)
  3. 5 차원 채점 (특히 promotion_value 강조)
  4. decision:
     - approve   → candidate_knowledge.status='approved' (ETL 큐)
     - reject    → candidate_knowledge.status='rejected' + rejected_reason
     - revise_request → 본문 일부 편집 후 다시 evaluated 재진입 (rare)
```

---

## 8. 관련 contract / Skill 연결

```
contract:
  - rag_data_contract.md §4.3 (evaluated → approved 분기)
  - rag_data_contract.md §13 (운영 절차)
  - error_response_contract.md §10 (운영자 알림 임계)
  - llm_security_contract.md §3.3 (보안 사고 audit)

Skill:
  - meta-retrospective (검토 누적 패턴 회고)
  - harness-audit (검토 큐 운영 감사)
  - contract-change (검토 차원 변경 시)
```

---

## 9. Open Questions

1. 운영자 1인 시기 → 다인 시기로 전환 시 검토 일관성 확보 — calibration 세션 주기.
2. 사용자 신고 시 자동 임시 차단 vs 신고 검토 후 차단 — 현재는 자동 차단(보수적).
3. forced_approve_audit (revise_round=2 강제 승격)의 사후 검토 비율 — 100% vs 샘플링.
4. LLM-운영자 점수 diff가 큰 케이스(±2 이상) — LLM prompt 개선 트리거.
5. promotion_value 차원의 일반화 측정 — embedding 다양성 vs 운영자 직관.
6. 검토 도구 UI 도입 시점 — Phase 11+ admin UI.
