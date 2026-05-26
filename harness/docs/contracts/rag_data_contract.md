# rag_data_contract.md — RAG 데이터 흐름 + 5단계 승격 Contract

> 위치: `docs/contracts/rag_data_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `docs/contracts/db_schema.md` §7.2 `candidate_knowledge`, §7.3 `rag_documents` / `rag_chunks`
> 참조: `docs/contracts/agent_io_contract.md` §4.7 RAG 검색 정책
> 참조: `docs/contracts/output_schema.md` §8 P-006 (`rag_used[]`)
> 참조: `docs/contracts/error_response_contract.md` §4.3 `E-RAG-*`
> 참조: `knowledge/rag/metadata_schema.md` (현재 stub, Phase 1 중 확장)
> 참조: `knowledge/rag/retrieval_policy.md`, `quality_filter.md`, `promotion_rule.md`
> 참조: `docs/contracts/privacy_contract.md` (Phase 7+ fill-in)

---

## 0. 이 문서의 위치

RAG (Retrieval-Augmented Generation) 데이터 라이프사이클을 5단계 승격(`pending → filtered → evaluated → approved → promoted`)으로 표준화하고, Planner Agent(P-006)가 사용하는 검색 정책을 고정한다.

이 문서가 정의하는 대상:

1. RAG 데이터 흐름 (수집 → 필터 → 평가 → 승인 → 승격 → 검색)
2. `candidate_knowledge.status` 5단계 (+ `rejected` 종결)
3. 각 단계의 진입/출구 조건, 책임자, 보관 기간
4. 자동 승격 vs 수동 승격 분기
5. 검색 정책 (top_k, similarity threshold, 채택 수)
6. 임베딩 모델 / pgvector 인덱스 / 차원 결정
7. 학습 신호 연동 (choice_logs, brand_memory_entries, feedback_events)
8. PII 마스킹 hook (privacy_contract placeholder 참조)
9. 광고 단어 필터 적용 위치

이 문서가 정의하지 않는 대상:

- LLM 호출 자체 → `agent_io_contract.md`
- LLM 출력 본문 구조 → `output_schema.md`
- 검색 결과를 어떻게 prompt에 끼워넣는지 → `ai_system/prompts/prompt_registry.md`
- 운영자 검수 워크플로 → Phase 11+ (별도 admin UI)

---

## 1. 설계 원칙

```
1. RAG는 사용자 입력의 출처가 아니다. 검증된 영상기획 패턴만 검색 대상.
2. 후보(candidate_knowledge)와 본체(rag_chunks)는 물리적으로 분리한다.
3. 승격 흐름은 5단계 + 1종결. 단계 건너뛰기 금지 (단, 자동 승격 경로는 단계 자동 처리).
4. 모든 후보는 출처(source_kind + source_id)를 가진다. 익명/출처 불명 항목 금지.
5. PII는 candidate 단계에서 마스킹. promoted 단계로 넘어가기 전 반드시 통과.
6. 광고적 표현은 evaluated 단계에서 자동 거절.
7. 검색 정책은 Planner(P-006)에만 적용. 다른 agent는 RAG 직접 호출 금지 (agent_io §4.7).
8. 임베딩 모델 변경 시 모든 rag_chunks 재임베딩 (배치). 차원 변경 = breaking change.
9. 사용자 학습 신호(feedback_events.event_type)는 자동 promotion 트리거가 아니다.
   누적 통계 기반의 자동 제안만 (운영자 검수 필수).
10. promoted 항목은 사용자의 원본 텍스트가 아니라 추출된 패턴/문장만 저장 (PII 우회).
```

---

## 2. 데이터 흐름 개요

```
[수집 소스]
   ├─ user_choice         (사용자가 선택한 카드 + 선택 이유)
   ├─ user_feedback       (like/dislike + reason)
   ├─ final_output        (최종 패키지에서 추출한 패턴)
   ├─ manual              (운영자가 LLM Wiki에서 직접 입력)
   └─ external_seed       (외부 영상기획 사례 시드, 운영자 수동)
        │
        ▼
[candidate_knowledge]  status='pending'
        │
        ▼  품질 자동 필터 + PII 마스킹
        │
[candidate_knowledge]  status='filtered'
        │
        ▼  LLM 자동 평가 (또는 운영자 평가)
        │
[candidate_knowledge]  status='evaluated'
        │
        ▼  운영자 승인 (자동 분기 조건 충족 시 자동)
        │
[candidate_knowledge]  status='approved'
        │
        ▼  ETL: rag_documents + rag_chunks INSERT + embedding 생성
        │
[candidate_knowledge]  status='promoted'      ↘ status='rejected' (종결)
        │
        ▼
[rag_documents] + [rag_chunks (with embedding)]
        │
        ▼  pgvector 검색 (Planner P-006 호출 시)
        │
   rag_context[] → Planner prompt
```

---

## 3. candidate_knowledge 테이블 (참조)

`db_schema.md` §7.2 그대로:

```sql
create table candidate_knowledge (
    candidate_id  uuid primary key default gen_random_uuid(),
    source_kind   text not null,              -- 'user_choice' | 'user_feedback' | 'final_output' | 'manual' | 'external_seed'
    source_id     uuid,                       -- 출처 레코드 ID
    content       text not null,              -- 본문 (PII 마스킹 후)
    metadata      jsonb default '{}'::jsonb,
    quality_score real,                       -- 0–1, 품질 필터 점수
    status        text not null default 'pending',
    reviewer      text,                       -- 'auto' | user_id | 'human_reviewer'
    review_notes  text,
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);
```

### 3.1 추가 운영 컬럼 (Phase 1 확장 검토)

```sql
alter table candidate_knowledge
    add column if not exists pii_masked       boolean default false,
    add column if not exists ad_phrase_check  boolean default false,
    add column if not exists ad_violations    text[],
    add column if not exists eval_score       real,             -- LLM 평가 점수
    add column if not exists eval_reasons     jsonb,            -- {clarity: "...", utility: "..."}
    add column if not exists promoted_chunk_id uuid,            -- 승격 후 rag_chunks 참조
    add column if not exists rejected_reason  text;
```

---

## 4. 5단계 승격 흐름

### 4.1 `pending`

**진입 조건:**
- `candidate_knowledge` row INSERT
- `source_kind ∈ {user_choice, user_feedback, final_output, manual, external_seed}`
- `content`가 1자 이상 + 길이 제한 (≤2000자, Phase 1)

**출구 조건:**
- 자동 필터 통과 → `filtered`
- 자동 필터 거절 → `rejected` (직접 종결)

**책임자:** 시스템 (자동)

**보관 기간:** 90일 (이 단계에서 멈춘 항목은 90일 후 hard delete)

**자동 필터 단계 (pending → filtered):**

```
1. PII 마스킹 검사 (privacy_contract §3, S3-3 또는 Phase 7+):
   - 전화번호 / 이메일 / 주민번호 / 카드번호 패턴 → 마스킹
   - 마스킹 적용 시 pii_masked=true
   - 마스킹 후에도 잔존 위험 발견 → rejected (rejected_reason='pii_residual')

2. 광고적 표현 검사 (output_schema §14):
   - 1차 차단 단어 발견 → rejected (rejected_reason='ad_phrase_violation', ad_violations=[...])
   - 2차 경고 단어 발견 → 통과하되 metadata.has_ad_warning=true 기록
   - ad_phrase_check=true 마킹

3. 최소 품질 점수:
   - 길이 검사 (10자 미만 → rejected, 'too_short')
   - 의미 없는 텍스트 패턴 (반복 문자, 공백 위주) → rejected, 'noise'
   - 영어/일어/기타 비한국어 비율 ≥ 60% → rejected, 'non_korean'

4. 중복 검사:
   - 같은 brand_id 내에서 cosine similarity ≥ 0.95인 기존 chunk 존재 → rejected, 'duplicate'
   - 단 source_kind='manual'은 운영자가 의도한 중복 허용 (warning만)
```

자동 거절 사례는 모두 `candidate_knowledge.status='rejected'` + `rejected_reason`. 다음 단계로 넘어가지 않음.

---

### 4.2 `filtered`

**진입 조건:** pending 단계의 모든 자동 필터 통과.

**출구 조건:**
- LLM 자동 평가 점수 충족 → `evaluated`
- LLM 자동 평가 점수 미달 → `rejected`

**책임자:** 시스템 (LLM 자동 평가) 또는 운영자 (수동 평가 트리거)

**보관 기간:** 60일

**LLM 자동 평가 (filtered → evaluated):**

평가는 별도 prompt (`P-EVAL-1`, Phase 1 신규)로 호출:

```
입력: candidate.content + metadata + source_kind
출력: {
  "eval_score": 0.0~1.0,
  "dimensions": {
    "clarity": 0~5,         // 명확성
    "utility": 0~5,         // Planner에서 참고할 가치
    "specificity": 0~5,     // 구체성 (너무 일반적이면 0)
    "freshness": 0~5,       // 시의성 (오래된 트렌드는 0)
    "brand_safety": 0~5     // 광고적 표현 / 부적절 콘텐츠
  },
  "reasons": { /* per dimension */ },
  "verdict": "pass | borderline | fail"
}
```

**임계치 (Phase 1 초기):**
- `eval_score ≥ 0.7` AND `verdict='pass'` → `evaluated`
- `eval_score < 0.5` OR `verdict='fail'` → `rejected`
- 그 사이 (borderline) → `evaluated` (운영자 수동 검수 큐 진입)

`eval_score`와 `eval_reasons`를 candidate row에 저장.

---

### 4.3 `evaluated`

**진입 조건:** LLM 평가 통과 또는 borderline.

**출구 조건:**
- 자동 승격 조건 충족 → `approved` (자동)
- 운영자 승인 → `approved`
- 운영자 거절 → `rejected`

**책임자:** 시스템 (자동 분기) 또는 운영자

**보관 기간:** 60일 (보류 중 60일 초과 시 자동 rejected, 'review_timeout')

**자동 승격 조건 (evaluated → approved):**

```
모두 충족 시 자동 approve:
- eval_score ≥ 0.85
- dimensions 모두 ≥ 3
- source_kind ∈ {final_output, manual, external_seed}
  (user_choice / user_feedback은 항상 수동 검수 필수, 사용자 PII 위험)
- 같은 brand_id에서 동일 패턴이 누적 ≥ 3회 발견 (반복 신호 기반 신뢰)
- pii_masked=false (마스킹이 필요한 항목은 항상 수동 검수)
```

**수동 승격 조건 (운영자 검수):**

위 자동 조건 미충족 시 운영자가 `reviewer='human_reviewer'`로 직접 승인. 검수 UI는 Phase 11+에서 도입. Phase 1에서는 SQL 직접 UPDATE 가능.

```
운영자 검수 시 기록:
- reviewer = user_id (운영자 id)
- review_notes (변경/거절 사유)
- updated_at 갱신
```

---

### 4.4 `approved`

**진입 조건:** 자동 또는 수동 승인.

**출구 조건:**
- ETL 배치가 `rag_documents` + `rag_chunks`로 복제 + embedding 생성 → `promoted`
- ETL 실패 → `approved` 유지 (재시도 큐)

**책임자:** 시스템 (ETL)

**보관 기간:** 영구 (단 promoted 후 30일은 rollback 윈도우)

**ETL 작업 (approved → promoted):**

```
1. rag_documents INSERT:
   - source_type = (source_kind에 따라 'user_promoted' | 'curated' | 'external_seed')
   - source_path = null (DB 내부 데이터) 또는 외부 url
   - title = metadata.title 또는 content 첫 50자
   - metadata = candidate.metadata + {candidate_id, promoted_at}

2. content chunking (Phase 1: 단순 분할):
   - 500자 단위 split (overlap 100자)
   - 작은 candidate (≤500자)는 chunk 1개
   - 큰 candidate (≥1500자)는 3+개

3. embedding 생성:
   - 모델: text-embedding-3-small (OpenAI)
   - dimension: 1536
   - 배치 처리 (10개씩)
   - 실패 시 재시도 1회

4. rag_chunks INSERT (각 chunk):
   - document_id
   - chunk_index (0부터)
   - content (chunk 본문)
   - embedding (vector(1536))
   - metadata (knowledge/rag/metadata_schema.md 참조)

5. candidate_knowledge UPDATE:
   - status = 'promoted'
   - promoted_chunk_id = 첫 chunk_id (대표)
   - updated_at = now()
```

ETL 실패 시 `candidate_knowledge.status='approved'` 유지하고 retry queue. 3회 실패 후 운영자 알림 (Slack).

---

### 4.5 `promoted`

**진입 조건:** ETL 완료, rag_chunks에 데이터 존재.

**출구 조건:**
- (정상 운영) 검색 대상으로 사용
- 운영자 회수 → `rejected` (단, 회수는 별도 absolute event)

**책임자:** 시스템 (검색 endpoint가 자동 사용)

**보관 기간:** 영구 (단 출처 user_id는 30일 후 익명화)

**회수 정책:**

운영자가 `promoted` 상태의 항목을 회수해야 할 경우:
- candidate_knowledge.status를 `rejected`로 UPDATE
- 동시에 rag_documents.is_active = false (chunks는 유지하되 검색에서 제외)
- 회수 사유는 review_notes에 기록
- 회수 사례는 운영자 monthly review 대상

---

### 4.6 `rejected` (종결)

**진입 경로:**
- pending → rejected (자동 필터)
- filtered → rejected (LLM 평가)
- evaluated → rejected (운영자 거절 또는 timeout)
- promoted → rejected (운영자 회수)

**보관 기간:** 90일 후 hard delete (`db_schema.md` §10).

**복원:** 불가. 동일 content를 다시 candidate로 INSERT하면 새 candidate_id 발급.

---

## 5. 검색 정책 (Planner P-006 전용)

`agent_io_contract.md` §4.7과 정합. 본 문서가 단일 출처 (single source of truth).

### 5.1 검색 쿼리 구성

```
query_text = approved_direction
           + " | " + selected_series.name
           + " | " + selected_domain.name
```

(공백+pipe로 결합. embedding 검색에 사용)

### 5.2 검색 파라미터

```
top_k:                  5         (pgvector cosine similarity 상위 5)
similarity_threshold:   0.7       (이 미만은 무시)
final_adoption:         3         (top_k 5 중 threshold 통과한 최대 3개만 채택)
exclude_filter:         is_active=false 항목 제외
metadata_filter:        없음 (Phase 1). Phase 2+에서 brand_id/domain/series 필터 검토.
```

### 5.3 pgvector 쿼리 예시

```sql
select
    c.chunk_id,
    c.document_id,
    d.title,
    c.content,
    c.metadata,
    1 - (c.embedding <=> $1::vector) as similarity   -- cosine similarity
from rag_chunks c
join rag_documents d on d.document_id = c.document_id
where d.is_active = true
order by c.embedding <=> $1::vector
limit 5;
```

`$1`은 query_text의 embedding (1536차원, OpenAI text-embedding-3-small).

이후 application-level에서 `similarity ≥ 0.7` 필터 + 최대 3개 채택.

### 5.4 빈 결과 처리

- 검색 결과 0건 (모두 threshold 미만 포함):
  - Planner 호출 시 `rag_context=[]` 주입
  - response envelope의 `validation.warnings`에 `no_rag_reference` 기록
  - 사용자 UI에는 "참고 자료 없이 만든 결과예요" 안내 (design.md §21)
- 검색 자체 실패 (pgvector 인덱스 오류, DB timeout):
  - E-RAG-001 또는 E-RAG-004 (error_response_contract §4.3)
  - Planner는 `rag_context=[]`로 계속 진행 (폴백)

### 5.5 RAG 사용 기록

P-006 응답의 `rag_used[]`에는 실제로 prompt에 주입된 chunk만 기록 (≤3개):

```json
"rag_used": [
  {
    "source_id": "<rag_chunks.chunk_id>",
    "title": "<rag_documents.title>",
    "used_reason": "<왜 이 chunk를 참조했는지 LLM이 자유 텍스트로>"
  }
]
```

---

## 6. 임베딩 모델

### 6.1 Phase 1 선택

```
model:          text-embedding-3-small (OpenAI)
dimension:      1536
cost:           $0.02 / 1M tokens
latency:        p95 < 500ms (batch 10개)
provider:       OpenAI API (server-side env var)
```

### 6.2 차원 결정 근거

- 1536은 OpenAI 권장 dimension (small/large 통일 가능, large는 truncate)
- pgvector ivfflat lists=100은 데이터 누적 10K~100K chunk 범위에 적합
- 768차원(다른 모델)로 변경 시 모든 chunks 재임베딩 필수 → **breaking change**

### 6.3 모델 변경 정책

```
1. 새 모델 후보 → 별도 staging table에 embedding 생성
2. 동일 query로 회귀 평가 (eval/golden_set의 50개 시드 케이스)
3. recall@5 ≥ 기존 모델 - 5% 유지 확인
4. cost / latency 비교
5. 통과 시: 전체 rag_chunks 재임베딩 (배치) → cutover (1주일 dual-write)
6. major bump + contract-change Skill 절차
```

### 6.4 다국어 (Phase 2+)

- 현재 ko-KR 단일. text-embedding-3-small은 다국어 호환이지만 Phase 1은 한국어만.
- 다국어 도입 시 metadata에 `language` 추가 + 검색 시 filter.

---

## 7. pgvector 인덱스 정책

### 7.1 인덱스 정의 (db_schema.md §7.3)

```sql
create index idx_rag_embedding on rag_chunks
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100);
```

### 7.2 lists 파라미터

```
lists = 100  → 적정 데이터 범위: 10K ~ 100K chunks
lists = sqrt(chunks_count) 권장

Phase 1 예상: ~500 chunks (lists=100 충분)
Phase 11+ 예상: ~10K chunks (lists=100 유지)
Phase 21+ 예상: ~100K chunks (lists=sqrt(100K)=316, 재구축 필요)
```

### 7.3 인덱스 재구축 시점

- 누적 chunks 수가 lists^2를 초과하면 검색 성능 저하
- 모니터링: 평균 검색 latency p95 ≥ 200ms 시 재구축 검토
- 재구축은 무중단 (CONCURRENTLY) 가능

### 7.4 hnsw 대안 (Phase 11+ 검토)

- pgvector 0.5+의 `hnsw` 인덱스는 ivfflat보다 빠르지만 메모리 사용 증가
- Phase 11+에서 데이터 100K 초과 시 검토

---

## 8. 학습 신호 연동

RAG 후보 수집은 사용자의 자연스러운 행동에서 비롯됨. 다음 신호들을 candidate_knowledge로 자동 INSERT.

### 8.1 source_kind='user_choice' (discovery_choices)

**트리거:** `discovery_choices` INSERT (사용자가 카드 선택).

**INSERT 규칙:**
- `selected_card`가 있고 `direct_input`이 null인 경우만 (AI 추천 채택 신호)
- content = `selected_card.name + " — " + selected_card.description`
- metadata = `{ step_name, brand_id, domain_id, series_id, video_id, confidence: card.confidence }`
- source_id = choice_id

**자동 INSERT 조건:**
- `selected_card.confidence ≥ 0.7`
- 동일 brand_id에서 같은 카드 누적 3회 이상 (반복 신호)

미충족 시 INSERT 안 함 (로그만).

### 8.2 source_kind='user_feedback' (feedback_events)

**트리거:** `feedback_events.event_type='like'` AND `target_kind='final'`.

**INSERT 규칙:**
- 좋아요한 final_output의 hook + structure 일부를 candidate로 추출
- content = `final_output.hook + " | " + JSON(final_output.structure[0])`
- metadata = `{ feedback_id, target_id, video_id, reason: feedback.reason }`
- source_id = feedback_id

### 8.3 source_kind='final_output'

**트리거:** `video_projects.status` → `final` 전이 시.

**INSERT 규칙:**
- final_output에서 hook / structure / shooting_notes 각각 candidate로 분할 INSERT
- content = 해당 섹션 텍스트
- metadata = `{ video_id, quality_score_avg: 8차원 평균, brand_id, domain_id, series_id }`
- 단, `quality_score_avg ≥ 4.0`인 final만 (낮은 품질은 학습 신호 제외)

### 8.4 source_kind='manual'

**트리거:** 운영자가 SQL 또는 admin UI(Phase 11+)로 직접 INSERT.

**INSERT 규칙:**
- 자유 (운영자 책임)
- 단 source_id는 null 허용
- 자동 승격 분기에서 우대 (수동 입력은 신뢰도 ↑)

### 8.5 source_kind='external_seed' (Phase 0 데이터 부트스트랩)

**트리거:** 운영자가 외부 사례를 시드로 입력 (knowledge/llm_wiki/).

**INSERT 규칙:**
- knowledge/llm_wiki/의 markdown 파일에서 ETL
- source_path를 metadata.source_url에 보관
- 자동 승격 가능 (이미 운영자 검토 거친 데이터)

### 8.6 brand_memory_entries와의 차이

| 항목 | brand_memory_entries | candidate_knowledge |
|---|---|---|
| 범위 | 사용자별 / brand별 | 전역 (모든 사용자 공유) |
| 사용처 | LLM prompt 직접 주입 | RAG 검색을 거쳐 주입 |
| PII | 사용자 자기 데이터 (마스킹 안 함) | **마스킹 필수** |
| 추출 prompt | P-AUX-2 | P-EVAL-1 (Phase 1) |
| 충돌 시 | 자기 데이터 우선 | 운영자 검수 후 결정 |

---

## 9. PII 마스킹 hook

### 9.1 적용 위치

```
pending → filtered 단계 (4.1):
  1. 전화번호, 이메일, 주민번호, 카드번호 패턴 자동 마스킹
  2. content 필드 UPDATE (원본은 보존 안 함, 마스킹본만)
  3. pii_masked=true 마킹
  4. 마스킹 후에도 잔존 위험 발견 (예: 이름+생년월일+지역명 조합) → rejected
```

### 9.2 마스킹 패턴 (error_response_contract §9.2 정합)

```
전화번호: \d{2,3}-\d{3,4}-\d{4}    → 010-****-****
이메일:   \S+@\S+\.\S+              → u***@***.com
주민번호: \d{6}-\d{7}                → ******-*******
카드번호: \d{4}-\d{4}-\d{4}-\d{4}   → ****-****-****-****
IP주소:   \d+\.\d+\.\d+\.\d+         → 192.168.1.*
```

### 9.3 잔존 위험 판정

다음 조합 발견 시 자동 rejected:
- 사람 이름 (한국 흔한 이름 사전 매칭) + 학교/소속 + 학번
- 사람 이름 + 주소(시/구/동)
- 사람 이름 + 직책 + 회사명

판정 알고리즘은 Phase 7+ `privacy_contract.md`에서 정형화. Phase 1에서는 단순 패턴 기반.

### 9.4 사용자 자기 데이터 예외

`brand_memory_entries`는 사용자 자기 데이터로서 PII 검사 대상이 아님 (사용자 본인의 표현, 본인 동의). 단 RAG로 승격하지 않음.

---

## 10. 광고 단어 필터

### 10.1 적용 위치

```
1. pending → filtered (자동 필터, §4.1.2):
   - 1차 차단 단어 발견 → rejected (rejected_reason='ad_phrase_violation')
   - 2차 경고 단어 발견 → 통과하되 metadata.has_ad_warning=true

2. filtered → evaluated (LLM 평가, §4.2):
   - dimensions.brand_safety가 < 2이면 evaluated → rejected 분기

3. approved → promoted (ETL, §4.4):
   - 마지막 안전 검사 (혹시라도 누락된 광고 단어 1회 더 확인)
   - 발견 시 ETL 중단 + 운영자 알림
```

### 10.2 단어 사전

`output_schema.md` §14.1과 정합. 단일 출처는 `knowledge/llm_wiki/style_guide/ad_phrase_blocklist.md` (Phase 1 중 생성).

### 10.3 사용자 직접 입력은 검사 대상 아님

`output_schema.md` §14.3 정합: 사용자가 직접 입력한 텍스트(`direct_input`)는 검사 안 함. 단 RAG candidate로 들어올 때는 검사함 (자기 표현이 아닌 학습 신호로 사용되므로).

---

## 11. metadata 스키마

RAG 검색 결과의 metadata는 `knowledge/rag/metadata_schema.md`에서 정의 (현재 stub, Phase 1 중 확장).

### 11.1 필수 키 (Phase 1 초안)

```json
{
  "source_kind": "user_choice | user_feedback | final_output | manual | external_seed",
  "promoted_at": "ISO8601",
  "candidate_id": "uuid",
  "language": "ko-KR",
  "quality_score": 0.85,
  "brand_id": "uuid | null",
  "domain_id": "uuid | null",
  "series_id": "uuid | null",
  "structure_type": "growth_record | ... | null",
  "approach_label": "narrative | ... | null",
  "format": "shorts_30s | ... | null"
}
```

`brand_id` 등이 null인 경우 = manual / external_seed 출처 (특정 사용자 데이터 아님).

### 11.2 선택 키 (Phase 2+ 확장 검토)

```
- topic_tags: string[]    (자동 태깅 도입 시)
- audience_age: string    (target 분석 도입 시)
- format_duration: int    (포맷별 길이 통계)
- view_count_signal: int  (외부 영상 데이터 연동 시)
```

---

## 12. 검색 성능 / 모니터링

### 12.1 모니터링 지표

```
- 평균 검색 latency (p50, p95)
- recall@5 (관련 chunk가 top 5 안에 들어오는 비율, 운영자 평가)
- threshold 미통과율 (검색은 했지만 0건 채택 비율)
- rag_chunks 총량 / 활성 비율
- candidate → promoted 비율 (퍼널)
- LLM 평가 PASS / borderline / FAIL 비율
```

### 12.2 임계 알림

```
검색 latency p95 ≥ 200ms / 15분    → Slack #ops-alert (인덱스 재구축 검토)
threshold 미통과율 ≥ 50% / 1일     → Slack #ops-alert (데이터 부족 신호)
candidate → promoted 비율 < 10%   → Slack #ops-alert (필터 너무 엄격)
ETL 실패 ≥ 3회 / 1시간             → Slack #ops-alert
```

### 12.3 회귀 평가

`eval/video_planning_eval.md`의 골든 셋 사용:
- 50개 시드 케이스에 대해 P-006 호출 → recall@5 측정
- 새 chunks 추가 시 1주일에 1회 회귀 실행

---

## 13. 운영 절차

### 13.1 새 manual 데이터 입력

```
1. 운영자가 candidate_knowledge에 SQL INSERT (source_kind='manual')
2. 자동 필터 통과 → filtered → evaluated (자동 LLM 평가)
3. 자동 승격 조건 충족 시 자동 approved → promoted
4. ETL 완료까지 ~1분 (배치 주기)
5. 운영자 dashboard에서 상태 확인
```

### 13.2 데이터 회수 (rollback)

```
1. 운영자가 candidate_knowledge.status='rejected' + rejected_reason 기록
2. ETL 후속 작업이 rag_documents.is_active=false 처리
3. 검색에서 즉시 제외 (다음 검색부터)
4. 회수 사례는 monthly review 대상
```

### 13.3 임베딩 재생성

```
모델 변경 또는 chunk content 갱신 시:
1. 운영자가 batch job 실행
2. rag_chunks의 embedding 컬럼 UPDATE
3. ivfflat 인덱스 자동 갱신
4. 대규모 변경은 staging 환경에서 dual-write 후 cutover
```

---

## 14. Phase별 마일스톤

### Phase 1 (MVP, 현재)

```
- 5단계 승격 흐름 구현
- 자동 필터 (PII / 광고 단어 / 기본 품질)
- LLM 자동 평가 (P-EVAL-1)
- 자동 승격 분기 (final_output / manual)
- 검색 정책 (top_k=5, threshold=0.7, 채택=3)
- 임베딩 모델: text-embedding-3-small (1536)
- pgvector ivfflat (lists=100)
```

### Phase 11+ (확장)

```
- 운영자 검수 admin UI
- metadata 자동 태깅
- hnsw 인덱스 검토 (chunks > 100K 시)
- 다국어 (en-US, ja-JP)
- 시리즈/도메인 단위 검색 필터
```

### Phase 21+

```
- 외부 사례 자동 크롤링 + 시드 입력
- 사용자 그룹별 RAG 격리 (team workspace)
- 영상 성과 데이터(view, retention) 기반 자동 가중치
```

---

## 15. Cross-reference 빠른 표

| 단계 | 책임자 | 다음 단계 진입 조건 | 의존 contract |
|---|---|---|---|
| pending | 시스템 | 자동 필터 통과 | output_schema §14 (광고), privacy (Phase 7+) |
| filtered | 시스템/운영자 | LLM 평가 pass 또는 borderline | P-EVAL-1 prompt (Phase 1 중 정의) |
| evaluated | 시스템/운영자 | 자동 승격 조건 또는 운영자 승인 | — |
| approved | 시스템 (ETL) | 임베딩 + INSERT 완료 | db_schema §7.3 |
| promoted | (정상 운영) | (없음, 회수 시만 rejected) | agent_io §4.7 검색 정책 |
| rejected | (종결) | 복원 불가 | db_schema §10 보존 정책 |

---

## 16. Open Questions

1. P-EVAL-1 prompt의 정확한 차원 가중치 — clarity / utility / specificity / freshness / brand_safety 평균 vs 가중평균.
2. 자동 승격 임계치 (eval_score 0.85) — 초기 데이터 누적 후 조정.
3. text-embedding-3-small vs text-embedding-3-large — 비용 5배 차이, recall 향상 폭 검증 필요.
4. metadata에 사용자 user_id 보관 시 익명화 시점 (현재 30일) — 학습 신호 vs PII.
5. RAG 검색을 Critic / Rewriter에도 확장 검토 (현재 Planner 한정).
6. external_seed 데이터의 출처 인용 표기 (final_output 사용자 노출 시 저작권).
7. 동일 사용자가 같은 brand에서 반복 거절한 패턴(rejection_pattern)을 negative example로 RAG에 넣을지.

---

## 17. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-2 초안. 5단계 승격 흐름, 검색 정책, 임베딩 모델 선택,
                      학습 신호 연동, PII / 광고 단어 필터 hook, metadata 스키마 초안.
```
