# user_feedback_data.md — 사용자 피드백 데이터

> 위치: `knowledge/datasets/user_feedback_data.md`
> source_kind: `user_feedback`
> 연계: `db_schema.md` §7 `feedback_events`, `rag_data_contract.md` §8.2, `ai_system/prompts/prompt_registry.md` P-AUX-2

---

## 0. 정의

**사용자 피드백 데이터**: 사용자가 영상기획 결과물에 대해 명시적으로 제공한 평가 / 의견 / 신고. 학습 신호 중 가장 직접적인 형태.

```
주요 피드백 유형:
  - rating         (별점 / 5점 척도 / thumbs)
  - text           (자유 텍스트 댓글)
  - revise_request (수정 요청 + 사유)
  - report         (부적절 / 광고 / 표절 신고)
  - like/dislike   (이진 신호, 가장 자주)
```

---

## 1. 데이터 출처 매핑

### 1.1 feedback_events 테이블

```sql
-- db_schema §7 정합
create table feedback_events (
    feedback_id   uuid primary key default gen_random_uuid(),
    user_id       uuid not null,
    target_kind   text not null,           -- 'card' | 'plan' | 'final' | 'system'
    target_id     uuid,                    -- 평가 대상 (plan_id / video_id 등)
    event_type    text not null,           -- 'like' | 'dislike' | 'rating' | 'text' | 'revise_request' | 'report'
    rating        int,                     -- 1-5 (event_type='rating' 시)
    text          text,                    -- 자유 텍스트 (event_type='text' / 'revise_request' / 'report')
    reason        text,                    -- 사유 코드 (분류)
    metadata      jsonb default '{}'::jsonb,
    created_at    timestamptz default now()
);
```

### 1.2 피드백 유형별 데이터

| event_type | rating | text | reason | 자동 처리 |
|---|---|---|---|---|
| like | (null) | (null) | (null) | 학습 신호 INSERT |
| dislike | (null) | (null) | optional | 거절 신호 누적 |
| rating | 1-5 | (null) | optional | 평균 점수 갱신 |
| text | (null) | required | optional | 운영자 검토 큐 |
| revise_request | (null) | required | required | Rewriter 호출 |
| report | (null) | optional | required | 즉시 회수 검토 |

---

## 2. 피드백 유형별 처리

### 2.1 like (긍정 신호)

```
처리:
  1. feedback_events INSERT
  2. final_output 의 hook + structure 일부를 candidate로 추출
  3. candidate_knowledge.source_kind = 'user_feedback'
  4. 5단계 승격 흐름 (수동 검수 필수)

조건 (rag_data §8.2):
  - target_kind = 'final'
  - target_id 는 final 상태 video_id
  - quality_score_avg ≥ 4.0 인 final만
```

### 2.2 dislike (부정 신호)

```
처리:
  1. feedback_events INSERT
  2. reason 분석 (자동 카테고리 분류, Phase 4+)
  3. candidate에 진입하지 않음 (negative example로 직접 사용 X)
  4. 통계만 누적

활용:
  - 같은 brand에서 반복 dislike 패턴 → prompt 개선 신호
  - 운영자 monthly review
```

### 2.3 rating (별점)

```
처리:
  1. feedback_events INSERT (rating: 1-5)
  2. video_projects 또는 final_output에 평균 갱신
  3. rating ≥ 4 이면 like와 동일 처리

활용:
  - 전반적 만족도 trend
  - 영상기획 품질 KPI
```

### 2.4 text (자유 텍스트 댓글)

```
처리:
  1. feedback_events INSERT (text 필드)
  2. PII 자동 마스킹 (전화/이메일 등)
  3. 운영자 검토 큐 (Phase 11+ admin UI)
  4. 검토 후 분류: 칭찬 / 불만 / 제안 / 부적절

수동 처리:
  - 운영자가 reason 코드 부여
  - 의미 있는 제안은 별도 백로그 등록 (meta/harness_improvement_proposals.md)
```

### 2.5 revise_request (수정 요청)

```
처리:
  1. feedback_events INSERT (text + reason 필수)
  2. Rewriter agent (P-008) 즉시 호출
  3. 사용자에게 수정안 제공 (max 2회, agent_io §6)
  4. revise 후 사용자 like → 학습 신호로 누적

연계:
  - Critic agent의 revise 권고와는 다른 경로 (사용자 능동 요청)
  - 두 경로 모두 ai_system/orchestration/flow.md에서 관리
```

### 2.6 report (신고)

```
처리:
  1. feedback_events INSERT (reason 필수)
  2. reason 코드:
     - 'inappropriate'   부적절 콘텐츠
     - 'ad_violation'    광고 단어 위반
     - 'plagiarism'      표절 의심
     - 'pii_leak'        개인정보 유출
     - 'other'           기타
  3. P0 우선순위로 즉시 운영자 알림 (Slack)
  4. 24시간 내 검토 → 정당하면 즉시 회수 (is_active=false)
  5. 7일 내 최종 판정 (legal 검토 포함)

회수 시:
  - 해당 final_output의 candidate / chunks 모두 회수
  - 같은 패턴 검색 결과에서 제외
  - 신고자 회신
```

---

## 3. 자동 vs 수동 처리

```
자동 처리:
  - like → candidate 진입 (조건 충족 시)
  - dislike → 통계만
  - rating → 평균 갱신
  - 사용자 자동 응답: "피드백 감사합니다"

수동 처리 (운영자):
  - text 자유 댓글 분류
  - report 검토
  - revise_request 사후 모니터링
  - monthly review (dislike 패턴 / 자주 들어오는 text 의견)
```

---

## 4. Brand Memory 자동 추출 (P-AUX-2 트리거)

`ai_system/prompts/prompt_registry.md` P-AUX-2 정합:

```
트리거 조건:
  - feedback_events.event_type = 'like' AND target_kind = 'final'
  - 같은 brand_id에서 누적 ≥ 5건의 like

처리:
  1. P-AUX-2 prompt 호출
  2. 5건의 final_output 패턴 분석
  3. brand_memory_entries 자동 INSERT:
     - tone_profile (톤 일관성)
     - vocabulary (자주 쓰는 어휘)
     - structure_preference (선호 구조)
     - hook_preference (선호 hook 패턴)

미충족 시:
  - 단순 통계 누적만
  - 학습 신호 약함
```

---

## 5. NPS / CSAT (Phase 7+ 검토)

현재 Phase 1은 like/dislike + rating 만. Phase 7+ 도입 검토:

### 5.1 NPS (Net Promoter Score)

```
정의: "이 서비스를 다른 사람에게 추천할 가능성은?" 0-10점
처리:
  - 9-10: 추천자 (promoter)
  - 7-8: 중립 (passive)
  - 0-6: 비추천 (detractor)
  - NPS = %promoter - %detractor

주기: 월 1회 사용자 일부에게 노출 (5% 표본)

활용:
  - 전반 만족도 KPI
  - 비추천 사용자 인터뷰 트리거
```

### 5.2 CSAT (Customer Satisfaction)

```
정의: "이 영상기획 결과에 만족하셨나요?" 1-5점
처리: 평균 점수 trend 분석

주기: 영상기획 완료 직후 (선택적 노출)

활용:
  - 결과 품질 KPI
  - 영상 유형별 (shortform / branding / promo) 차이
```

---

## 6. PII 보호

```yaml
text 자유 댓글:
  - PII 자동 마스킹 (전화/이메일/주민번호/카드/IP)
  - 잔존 위험 발견 (이름+소속 조합) → 운영자 검토

report text:
  - PII 마스킹 (신고자 / 피신고자 모두 보호)
  - 마스킹 후에도 운영자만 원본 접근 가능

candidate 진입 시 (user_feedback):
  - text 필드 직접 포함 안 함
  - final_output의 hook + structure만 추출
  → text의 PII 위험 우회
```

---

## 7. 데이터 누적 추정

### 7.1 Phase 1 (사용자 1000명)

```
영상기획 1건당 피드백:
  - like/dislike: 평균 0.3건 (30%)
  - rating: 평균 0.05건 (5%)
  - text: 평균 0.02건 (2%)
  - revise_request: 평균 0.05건 (5%)
  - report: 평균 0.001건 (0.1%)

월간 (사용자 1000명 × 영상 5건):
  feedback_events INSERT: ~2000건/월
  like INSERT: ~1500건/월 (가장 많음)
  
candidate 진입 (like 중 조건 충족):
  ~500-1000건/월 (PII 검수 필요)
```

### 7.2 Phase 7+ (사용자 10000명)

```
월간 feedback_events: ~20000건
월간 candidate from feedback: ~5000-10000건

→ 운영자 수동 검수 부담 ↑
→ Phase 11+ admin UI 필수
```

---

## 8. 보존 정책

`db_schema §10` + `rag_data §4` 정합:

```yaml
feedback_events:
  영구 보존 (단 user_id 1년 후 익명화)
  text 자유 댓글 30일 후 PII 마스킹

candidate from feedback:
  pending: 90일
  filtered/evaluated: 60일
  promoted: 영구 (user_id 30일 후 익명화)
  rejected: 90일 후 hard delete

report 신고:
  영구 보존 (legal 증빙)
  단 신고자 / 피신고자 user_id는 1년 후 익명화
```

---

## 9. 모니터링

```yaml
일일 지표:
  - feedback_events INSERT 수 per event_type
  - like / dislike 비율
  - 평균 rating
  - report 발생 (즉시 알림)

주간 지표:
  - text 자유 댓글 의미 분류 (운영자 수동)
  - revise_request 비율 (높으면 Planning 품질 문제)
  - brand_memory 자동 추출 수

월간 지표:
  - NPS / CSAT (Phase 7+ 도입 후)
  - 자주 들어오는 의견 top 10
  - report 분류 (광고 / PII / 표절 등)
```

---

## 10. Phase별 마일스톤

### Phase 1 (현재)

- 6 event_type 지원
- like → candidate 자동 진입
- 운영자 SQL 검수

### Phase 4+

- text 자유 댓글 자동 분류 (LLM)
- dislike reason 자동 카테고리
- brand_memory 자동 추출 정확도 향상

### Phase 7+

- NPS / CSAT 도입
- 사용자 본인 피드백 history 조회
- privacy_contract 정형화 후 PII 강화

### Phase 11+

- 운영자 admin UI (피드백 검토 큐)
- 실시간 alert (report / 부정적 trend)
- 사용자 인터뷰 자동 트리거 (NPS 비추천)

---

## 11. Open Questions

1. like 자동 candidate 진입 조건 — 같은 brand 5건 이상 같은 패턴 like 시?
2. dislike reason 자동 분류 정확도 — LLM 활용 vs 운영자 수동.
3. revise_request 의 추가 학습 신호 활용 — Critic agent 학습?
4. NPS / CSAT 도입 시점 (Phase 7+) — 너무 늦지 않은지.
5. report 24시간 SLA — 빠른 회수 vs 충분한 검토.
6. 사용자 본인 피드백 export / delete 권리 (GDPR 정합) — Phase 7+.
7. dislike 데이터를 negative example RAG에 넣을지 (rag_data §16 Open Q 정합).

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 6 event_type 처리, P-AUX-2 자동 추출 트리거,
                      NPS/CSAT Phase 7+ 검토, PII 보호, 데이터 누적 추정.
```
