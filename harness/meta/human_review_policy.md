# human_review_policy.md — 인간 검토 정책

> 위치: `meta/human_review_policy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `eval/human_review_rubric.md` (검토 rubric), `meta/self_improvement_loop.md`
> 참조: `knowledge/rag/promotion_rule.md`, `docs/contracts/llm_security_contract.md`

---

## 0. 인간 검토 정의

> **AI가 결정하면 안 되는 영역은 사람이 검토한다.**

본 정책은 자동 처리 vs 인간 검토의 경계를 정의한다. 잘못된 자동 처리 (예: 잘못된 데이터를 RAG로 promotion)는 시스템 전체에 영향을 끼치므로 반드시 사람 검토가 필요.

---

## 1. 자동 처리 vs 인간 검토 결정 기준

### 1.1 자동 처리 가능 (사람 개입 불필요)

```
- 정상 영상기획 요청 처리 (MOA Lite 전체)
- agent_io_logs 기록
- 광고 표현 자동 차단 (광고 단어 사전 적용)
- PII 자동 마스킹
- rate_limit 자동 적용
- error 응답 자동 생성 (error_response_contract)
- Brand Memory 자동 추출
- candidate_knowledge 1~3 단계 (pending → filtered → evaluated)
- 영구 제외 (영상 제작) 사용자 요청 거절
```

### 1.2 인간 검토 필수

```
- candidate_knowledge 4단계 (evaluated → approved)
- 보안 인시던트 (security_block 누적 / 데이터 노출 의심)
- 광고 단어 2차 경고 (자동 sanitize 실패 후 반복 발생)
- 사용자 계정 정지 결정
- 환불 결정 (Phase 12+ paid tier)
- 운영자 알림 도달 시 처리
- prompt 변경 (P-XXX semver bump)
- contract 변경
- Phase 진입 결정
```

### 1.3 그레이존 (검토자 권한에 따라)

```
- 큰 비용 변동 (5분 평균 사용자당 비용이 평소 3배)
- 새 광고 단어 사전 추가
- 새 prompt injection 패턴 추가
- Brand Memory 자동 추출 결과 (사용자가 거부 시)
- intent_filter false positive 신고
```

---

## 2. 검토 대상 상세

### 2.1 candidate_knowledge promotion

```
파이프라인: pending → filtered → evaluated → approved → promoted

자동: pending → filtered (quality_filter 자동)
자동: filtered → evaluated (LLM 평가 자동)
인간: evaluated → approved (인간 검토 필수)  ← 본 정책의 핵심
자동: approved → promoted (RAG 적재 자동)
```

검토자가 보는 정보:

```
- candidate_knowledge.raw_text
- 추출된 metadata (Brand / Domain / Series)
- quality_filter 점수
- LLM 평가 점수 (relevance, quality, safety)
- 광고 단어 / PII 감지 여부
- 유사 promoted 항목 (중복 검사용)
```

→ `knowledge/rag/promotion_rule.md` §검토 절차

### 2.2 보안 인시던트

```
인시던트 종류:
A. 데이터 노출 의심 (PII 로그에 노출 / 사용자 간 데이터 격리 위반)
B. 외부 공격 패턴 (1분에 50회 이상 요청 / 동일 IP에서 다수 계정)
C. 부적절 콘텐츠 누적 (E-SEC-004 3회 이상)
D. 광고 단어 사전 우회 시도 (LLM이 우회 표현 생성)

검토자 액션:
- A: 즉시 조사 + 영향 사용자 알림 + 24시간 내 patch
- B: IP 차단 + 인증 강화 + 운영자 알림
- C: 계정 정지 검토 + 사용자 안내
- D: 사전 갱신 + prompt 강화
```

→ `docs/contracts/error_response_contract.md` §10 운영자 알림 임계

### 2.3 광고 단어 2차 경고

```
자동 처리: 광고 단어 1차 감지 → 자동 재시도
자동 처리: 광고 단어 2차 감지 → 자동 sanitize
인간 검토: sanitize 실패 후 같은 사용자 3회 이상 발생 시

검토자 액션:
- 광고 단어 사전 갱신 후보 분석
- 사용자 가이드 강화 검토
- prompt 변경 검토 (광고 표현 차단 강조)
```

---

## 3. 검토자 / SLA

### 3.1 검토자 역할

```
운영자 (사용자 본인 또는 운영 인력):
- 모든 인간 검토 최종 결정자.
- Phase 1~10 (MVP): 사용자 본인이 운영자 겸임.
- Phase 11+: 운영 인력 확장 시 검토자 권한 위임.

AI (보조 역할):
- 검토 자료 자동 정리.
- 유사 사례 자동 검색.
- 결정 후보 제시 (단 최종 결정은 사람).
```

### 3.2 SLA (Service Level Agreement)

검토 응답 시간 기준. 위반 시 정책 검토.

```
24시간 SLA (긴급):
- 데이터 노출 의심 (security A)
- 외부 공격 패턴 (security B)
- 큰 비용 사고 (5분 평균 평소 3배)

72시간 SLA (보통):
- candidate_knowledge approved 결정
- 부적절 콘텐츠 누적 (security C)
- 환불 신청 (Phase 12+)

7일 SLA (낮은 우선순위):
- 광고 단어 2차 경고
- intent_filter false positive 신고
- 사용자 가이드 개선 제안
- prompt 변경 제안

30일 SLA (장기 검토):
- harness_improvement_proposals
- 가격 모델 변경
- Phase 진입 결정
```

### 3.3 SLA 위반 시 절차

```
1. SLA 도달 12시간 전 자동 알림 (Slack #ops-alert)
2. SLA 도달 시 자동 escalation (운영자 추가 알림)
3. SLA 50% 초과 시 패턴으로 등록 (meta/patterns.md)
4. SLA 100% 초과 시 회고 (meta-retrospective Skill)
```

---

## 4. 검토 UI / API

### 4.1 검토 UI (Phase 9+)

```
대시보드: /admin/review-queue
구성:
- 대기 중 / 진행 중 / 완료 (탭)
- 우선순위 정렬 (긴급 → 보통 → 낮음)
- 검토 항목별:
  - 자동 분석 결과
  - 유사 사례 (이전 결정 기준)
  - AI 추천 결정
  - 검토자 결정 입력 (승인 / 반려 / 보류 / 조건부)
  - 결정 사유 필수 입력
```

### 4.2 검토 API (Phase 11+ 외부 시스템 연동)

```
GET /api/v1/admin/review-queue
POST /api/v1/admin/review/{review_id}/decide
GET /api/v1/admin/review/{review_id}/history

권한: admin role (Supabase Auth)
인증: service role key + JWT
```

→ `docs/contracts/api_contract.md` 정합

---

## 5. 검토 결과 기록

### 5.1 기록 위치

```
candidate_knowledge.status:
  pending / filtered / evaluated / approved / promoted / rejected

candidate_knowledge.review_history:
  - reviewer_id
  - decision: approve / reject / hold
  - reason: text
  - decided_at: timestamp

eval/regression_results/:
  - 인간 검토 결과의 회귀 영향 측정 (Phase 7+)

meta/security_metrics.md:
  - 보안 인시던트 검토 결과 누적 (Phase 7+)

meta/lessons_learned.md:
  - 큰 결정의 학습 사항 (meta-retrospective 연동)
```

### 5.2 결정 사유 기록 의무

```
모든 검토 결정에 사유 필수:
- 승인: "왜 승인했는가" (간단 1~2줄)
- 반려: "왜 반려했는가 + 무엇이 부족한가" (필수, 사용자에게 피드백 가능)
- 보류: "추가로 무엇이 필요한가" + 보류 기한
- 조건부 승인: "어떤 조건 하에서 승인했는가" + 모니터링 기간

기록 누락 시: 검토 완료 처리 불가 (UI 검증)
```

### 5.3 결정 retroactive 변경

```
한 번 내린 결정을 변경하려면:
1. 새 review_record 생성 (기존 record 유지)
2. retroactive_reason 필수 기록
3. 영향 분석 (이미 promoted된 RAG 데이터 회수 등)
4. 7일 보류 후 적용
```

---

## 6. human_review_rubric 연동

상세 평가 rubric은 `eval/human_review_rubric.md` 참조. 본 정책에서는 **언제** 검토하는지, rubric은 **어떻게** 검토하는지.

```
candidate_knowledge 승격 rubric:
- relevance (영상기획 도메인 관련성) >= 0.7
- quality (정보 품질) >= 0.6
- safety (안전성) = 1.0 (광고 / PII / 부적절 없음)
- uniqueness (기존 RAG와 중복도) <= 0.8

보안 인시던트 rubric:
- 영향 범위 (단일 사용자 / 일부 / 전체)
- 데이터 민감도 (PII / Brand / 일반)
- 재발 가능성 (즉시 patch / 모니터링)
- 사용자 통보 필요 여부

→ eval/human_review_rubric.md 정합
```

---

## 7. 검토 효율화 (AI 보조)

다음 작업은 AI가 자동화하여 검토자 부담 감소.

```
자동 정리:
- 유사 사례 자동 검색 (이전 결정 기준)
- 자동 분석 보고서 생성 (관련 metadata + 통계)
- AI 추천 결정 (단 최종 결정은 사람)

자동 우선순위:
- 긴급도 자동 분류 (24h / 72h / 7d / 30d)
- 비슷한 케이스 batch 묶음 (한 번에 여러 건 처리)

자동 알림:
- SLA 12시간 전 알림
- 새 검토 항목 도착 알림
```

→ Phase 9+ 운영 대시보드 도입 시 구현

---

## 8. 검토 부담 분산

```
1인 운영 (MVP, 1~10):
- 모든 검토를 사용자(=운영자) 1명이 처리.
- 검토 대기 시 자동 영향 분석 + 검토자 알림.
- SLA 위반 시 자동 보류 처리 (긴급은 즉시 escalation).

운영 인력 확장 (Phase 11+):
- 검토 권한 분리:
  - candidate_knowledge approved: 콘텐츠 담당
  - 보안 인시던트: 보안 담당
  - 결제 / 환불: CS 담당
- 권한별 dashboard 분리.

자동 결정 비율 증가 (Phase 21+):
- AI가 작은 결정은 자동 (조건부).
- 큰 결정만 사람.
- 자동 결정 비율 목표: 80% (단 잘못된 자동 결정 0건).
```

---

## 9. 측정 지표

```
1. 검토 대기 건수 (실시간)
   - 목표: 24h SLA 대기 5건 이하

2. 평균 검토 응답 시간 (긴급도별)
   - 24h: 평균 12시간 이하
   - 72h: 평균 36시간 이하

3. SLA 준수율
   - 목표: 95% 이상

4. 결정 일관성
   - 같은 유형 사례의 결정 통계 (분산 측정)
   - 분산이 크면 rubric 갱신 필요

5. 자동화 비율
   - 인간 검토 / 전체 결정
   - Phase 1~10: 20% 자동화 / 80% 인간
   - Phase 21+: 80% 자동화 / 20% 인간 (목표)
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 9+:  검토 UI 본격 구현 (현재는 직접 DB 조회 + Skill 활용).
Phase 11+: 검토 권한 분리 (운영 인력 확장).
Phase 21+: AI 자동 결정 비율 증가 (조건부 자동화).
연 1회:    rubric 갱신 (eval/human_review_rubric.md).
```

---

## 11. Open Questions

1. 1인 운영 시 검토 부담이 너무 클 위험 — 자동화 우선순위 결정 필요.
2. AI 추천 결정에 검토자가 끌려갈 위험 (확증 편향) — 추천 hide 옵션 검토.
3. SLA 위반이 누적되면 정책 자체가 무력화 — escalation 메커니즘 강화.
4. 검토 결정의 retroactive 변경이 RAG 데이터 회수 시 영향 — 7일 보류 적정성.
5. 권한 분리 시 (Phase 11+) 단일 검토자가 여러 영역 담당 가능한지 결정.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      자동 vs 인간 검토 기준, 3 검토 대상, SLA, 검토 UI,
                      결과 기록 의무, rubric 연동, 측정 지표.
```
