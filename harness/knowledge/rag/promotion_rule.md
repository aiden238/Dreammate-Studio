# promotion_rule.md — 5단계 승격 운영 룰

> 위치: `knowledge/rag/promotion_rule.md`
> 단일 출처: `docs/contracts/rag_data_contract.md` §4 (5단계 승격 흐름)
> 본 문서는 contract의 운영자 친화 해설 + 실무 결정 트리

---

## 0. 이 문서의 위치

RAG 후보(candidate_knowledge)가 `pending → filtered → evaluated → approved → promoted` 5단계를 거쳐 검색 가능한 본체(rag_chunks)로 변환되는 과정의 **운영 룰**을 정의한다. `rejected`는 모든 단계에서 종결 가능한 6번째 상태. 임계치 / 트리거 / 강등 정책을 포함한다.

수치 충돌 시 `rag_data_contract.md §4` 우선.

---

## 1. 5단계 + 1종결 상태 요약

| 상태 | 의미 | 다음 상태 | 책임자 |
|---|---|---|---|
| pending | 후보 INSERT 직후 | filtered / rejected | 시스템 |
| filtered | 자동 필터 통과 | evaluated / rejected | 시스템 (LLM) |
| evaluated | LLM 평가 통과 | approved / rejected | 시스템(자동) or 운영자 |
| approved | 승격 승인 | promoted | 시스템 (ETL) |
| promoted | rag_chunks 진입 | (회수 시 rejected) | (정상 운영) |
| rejected | 종결 | (불가) | (종결) |

---

## 2. 단계별 임계값 (Phase 1)

### 2.1 pending → filtered

자동 필터 4종 모두 통과:

```yaml
pii_check:           # PII 마스킹 (rag_data §9)
  pass: pii_masked=true OR 원본에 PII 없음
  fail: 잔존 위험 발견 (이름+소속+학번 등 조합) → rejected('pii_residual')

ad_phrase_check:     # 광고 단어 (output_schema §14)
  pass: 1차 차단 단어 없음
  fail: 1차 차단 단어 발견 → rejected('ad_phrase_violation')
  warn: 2차 경고 단어만 발견 → 통과하되 metadata.has_ad_warning=true

length_check:
  pass: 10자 ≤ len(content) ≤ 2000자
  fail_short: len < 10 → rejected('too_short')
  fail_long:  len > 2000 → rejected('too_long')

language_check:
  pass: 한국어 비율 ≥ 40%
  fail: 영어/일어/기타 ≥ 60% → rejected('non_korean')

duplicate_check:
  pass: 같은 brand_id 내 cosine ≥ 0.95인 기존 chunk 없음
  fail: 중복 발견 → rejected('duplicate')
  exception: source_kind='manual' 인 경우 warning만 (운영자 의도 허용)
```

### 2.2 filtered → evaluated

LLM 평가 (P-EVAL-1, Phase 1 신규):

```yaml
eval_score:          # 0.0 ~ 1.0
  pass: ≥ 0.7 AND verdict='pass' → evaluated
  borderline: 0.5 ≤ eval_score < 0.7 OR verdict='borderline' → evaluated (수동 검수 큐 진입)
  fail: < 0.5 OR verdict='fail' → rejected('low_eval_score')

dimensions:          # 5차원 0~5점 (rag_data §4.2)
  - clarity (명확성)
  - utility (Planning 참고 가치)
  - specificity (구체성)
  - freshness (시의성)
  - brand_safety (광고/부적절)
```

### 2.3 evaluated → approved

**자동 승격 조건 (모두 충족 시):**

```yaml
all_of:
  - eval_score: ≥ 0.85
  - dimensions: 모두 ≥ 3
  - source_kind: ∈ [final_output, manual, external_seed]
                # user_choice / user_feedback은 항상 수동 검수
  - same_pattern_count: ≥ 3
                # 같은 brand_id에서 동일 패턴 3회 이상 발견
  - pii_masked: false
                # 마스킹이 필요했던 항목은 무조건 수동 검수
```

**수동 승격 (운영자 검수):**

자동 조건 미충족이지만 evaluated 상태인 모든 항목 → 운영자 검수 큐 진입. 운영자는 reviewer 필드에 user_id 기록 + review_notes 필수. Phase 11+ admin UI 도입 전까지는 SQL 직접 UPDATE.

### 2.4 approved → promoted

ETL 배치 (`rag_data §4.4`):

```
1. rag_documents INSERT
2. content chunking (500자 + overlap 100자)
3. embedding 생성 (text-embedding-3-small, dim=1536, 배치 10개)
4. rag_chunks INSERT (각 chunk)
5. candidate_knowledge.status = 'promoted' + promoted_chunk_id 기록
```

실패 시 approved 유지 + 재시도 큐 (3회 후 운영자 알림).

---

## 3. 자동 vs 수동 결정 트리

```
[candidate INSERT]
       │
       ▼
   pending 자동 필터
       │ ↘ rejected (PII/광고/길이/언어/중복)
       ▼
   filtered LLM 평가
       │ ↘ rejected (eval_score < 0.5)
       ▼
   evaluated
       │
       ├─ eval_score ≥ 0.85 AND
       │  source ∈ {final_output, manual, external_seed} AND
       │  same_pattern ≥ 3
       │  → 자동 approved
       │
       └─ 그 외 → 운영자 검수 큐
              ├─ 운영자 승인 → approved
              ├─ 운영자 거절 → rejected
              └─ 60일 timeout → rejected (review_timeout)
       │
       ▼
   approved ETL
       │ ↘ ETL 3회 실패 → 운영자 알림 (approved 유지)
       ▼
   promoted (정상 운영)
       │
       └─ 운영자 회수 → rejected + is_active=false
```

---

## 4. 단계 전환 트리거

### 4.1 자동 트리거 (시스템 발동)

- candidate_knowledge INSERT → 즉시 pending 자동 필터 시작 (트랜잭션 후 비동기)
- pending → filtered 통과 → 즉시 LLM 평가 dispatch (큐 enqueue)
- filtered → evaluated 통과 → 자동 승격 조건 평가 → 충족 시 즉시 approved
- approved → 정기 ETL 배치 (5분 주기)

### 4.2 LLM eval 트리거

- 큐에서 batch (50개) 단위로 P-EVAL-1 호출
- 비용 상한: 1일 candidate 1000개 (이상 시 운영자 알림)
- 실패 시 재시도 1회 → 그래도 실패면 filtered 유지 (재시도 큐)

### 4.3 human review 트리거

- 운영자 admin UI (Phase 11+) 또는 SQL 직접 UPDATE
- evaluated 60일 timeout 시 자동 rejected
- 자동 승격 조건 미충족 항목은 운영자에게 daily Slack 요약 알림 (Phase 2+)

### 4.4 time-based 트리거

- pending 90일 → hard delete (보관기간 초과)
- filtered 60일 → rejected('filtered_timeout')
- evaluated 60일 → rejected('review_timeout')
- rejected 90일 → hard delete

---

## 5. 강등 (downgrade) 정책

promoted 항목을 다시 낮은 상태로 되돌리는 정책:

### 5.1 promoted → rejected (회수)

```yaml
트리거:
  - 운영자가 명시적 회수 (legal / 광고 단어 잔존 발견 / 품질 저하 / 사용자 신고)
  - 자동 (현재 없음. Phase 4+ 검토)

처리:
  - candidate_knowledge.status = 'rejected'
  - rag_documents.is_active = false (chunks는 유지하되 검색 제외)
  - review_notes에 회수 사유 명시
  - 회수 사례는 monthly review 대상
```

### 5.2 promoted → approved (한시 비활성, Phase 4+)

```yaml
용도: 검증 필요한 일시 비활성 (예: 신고 접수 후 재검토)
처리:
  - candidate_knowledge.status = 'approved' (한 단계 강등)
  - rag_documents.is_active = false (검색 제외)
  - 재검토 후 다시 promoted 복귀 OR rejected 종결
```

Phase 1에서는 사용 안 함 (단순 rejected로 처리). Phase 4+ admin UI 도입 시 검토.

### 5.3 강등 금지 사례

```
- approved → evaluated: 금지 (이미 ETL 진행 중 가능성)
- evaluated → filtered: 금지 (LLM 비용 낭비)
- 강등은 항상 promoted 또는 rejected에서만 발동
```

---

## 6. 보관 기간 요약

```
pending:    90일 (이 단계에서 멈춘 항목 hard delete)
filtered:   60일 (LLM 평가 큐에서 처리 안 된 항목 rejected)
evaluated:  60일 (운영자 검수 timeout)
approved:   영구 (단 promoted 후 30일 rollback 윈도우)
promoted:   영구 (출처 user_id는 30일 후 익명화)
rejected:   90일 → hard delete
```

---

## 7. 자동 승격이 막아주는 위험

```
사용자 PII 노출:    user_choice/user_feedback은 자동 승격 불가 → 항상 운영자 검수
일회성 데이터:       same_pattern ≥ 3 조건으로 우연한 1회 데이터 차단
저품질 데이터:       eval_score ≥ 0.85 (높은 기준)
편향:                dimensions 모두 ≥ 3 (한 차원만 강한 데이터 제외)
```

---

## 8. 운영자 검수 큐 우선순위 (Phase 11+ admin UI)

```
P0 (즉시): legal 위험 신고된 promoted 항목
P1 (1일):  source_kind=user_feedback (사용자 정서적 의견)
P2 (3일):  source_kind=user_choice (선택 신호)
P3 (1주): borderline eval_score (0.5-0.7)
P4 (배치): 자동 승격 조건 미충족 evaluated 항목
```

---

## 9. Phase별 마일스톤

### Phase 1 (현재)

- 자동 필터 + LLM 평가
- 자동 승격: final_output / manual / external_seed
- 수동 승격: SQL 직접 UPDATE
- 강등: rejected만

### Phase 4+

- 자동 승격 조건 데이터 기반 조정
- promoted → approved 한시 강등 도입
- daily Slack 요약 알림

### Phase 11+

- 운영자 admin UI
- 검수 큐 우선순위 자동 계산
- A/B 테스트 (다른 임계값 비교)

---

## 10. Open Questions

1. 자동 승격 임계값 (eval_score 0.85) — 초기 데이터 축적 후 0.80 또는 0.90 검토.
2. same_pattern_count 정의 — 키워드 매칭 vs cosine similarity 기반.
3. user_choice/user_feedback의 자동 승격 허용 조건 — PII 완전 마스킹 확인 시 허용 가능?
4. 회수된 chunks의 hard delete 시점 (현재 90일) — 검색 통계 보존을 위해 더 길게 둘지.
5. 강등(promoted → approved)을 Phase 4+에 정말 도입할지 vs 단순 회수만 유지할지.
6. 운영자 검수 큐 P0~P4 우선순위가 합리적인지 (운영 데이터 누적 후 재조정).

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 5단계 임계값, 자동/수동 결정 트리,
                      강등 정책, 보관 기간, 운영자 검수 큐 우선순위.
```
