---
name: rag-update
description: |
  RAG 지식을 추가하거나 candidate_knowledge를 approved_knowledge로 승격시킬 때 사용한다.
  사용자 데이터, LLM Wiki 신규 항목, 외부 시드 데이터 등 어떤 출처든 RAG에 진입하기 전
  필수로 거치는 5단계 파이프라인(후보 → 품질 필터 → 평가 → 승인 → 승격)을 강제한다.
  트리거: "RAG 추가", "지식 추가", "candidate_knowledge", "approved_knowledge",
  "llm_wiki 추가", "승격", "promotion", "knowledge update".
applies_to: [agents, claude]
phase: [phase-7, phase-8, phase-9, phase-10, ongoing]
related_contracts:
  - docs/contracts/privacy_contract.md
  - docs/contracts/llm_security_contract.md
  - docs/contracts/db_schema.md (candidate_knowledge, rag_documents, rag_chunks)
related_state:
  - knowledge/candidate_knowledge/
  - knowledge/approved_knowledge/
  - knowledge/llm_wiki/
version: v1.0.0
---

# rag-update

RAG 지식이 운영 시스템에 들어가기 전 거쳐야 하는 5단계 승격 파이프라인.

## 핵심 원칙

```
1. 사용자 데이터를 바로 global RAG에 넣지 않는다.
2. 모든 후보 지식은 candidate_knowledge 테이블/디렉터리에 먼저 적재된다.
3. 5단계 (pending → filtered → evaluated → approved → promoted)를 모두 통과해야
   rag_documents/rag_chunks로 이동한다.
4. 단계 사이에 rollback 가능해야 한다.
5. 승격된 지식의 원 출처 정보는 보존하되, 사용자 식별 정보는 익명화된다.
6. 자동 승격은 금지. approved → promoted 단계는 반드시 사람 또는 명시적 승인.
```

## 트리거되는 상황

- 사용자가 "이 기획을 다음에도 참고해" 같은 요청
- 영상 final_output이 완료되어 Brand Memory 후보 추출
- LLM Wiki에 새 항목 추가
- 외부 시드 데이터 import
- candidate_knowledge → approved_knowledge 승격 요청
- approved_knowledge → rag_documents 승격 요청

## 5단계 파이프라인

### Step 1. pending — 후보 수집

새로운 지식 후보를 `candidate_knowledge` 테이블에 INSERT한다.

```sql
status        = 'pending'
source_kind   = 'user_choice' | 'user_feedback' | 'final_output'
                | 'manual' | 'external_seed' | 'brand_memory_extract'
source_id     = 원 데이터의 ID (있는 경우)
content       = 후보 텍스트
metadata      = { brand_id, domain_id, language, created_by, ... }
quality_score = null
```

**금지**:
- 사용자 raw 입력을 그대로 candidate_knowledge에 넣지 말 것. 항상 정제된 형태로.
- 식별 정보(이메일, 실명, 전화번호 등)는 이 단계에서 마스킹.

### Step 2. filtered — 자동 품질 필터

자동 점검을 통과한 후보만 `status = 'filtered'`로 전환한다.

#### 자동 검사 항목

```
1. 개인정보 검사
   - 정규식: 이메일, 전화번호, 주민번호, 카드번호
   - 발견 시 → status: 'rejected', reason: 'pii_detected'

2. 영상기획 관련성 검사
   - intent_filter Skill 또는 P-AUX-1 prompt로 판정
   - decision: 'block'이면 → status: 'rejected', reason: 'off_topic'

3. 중복 검사
   - 기존 rag_chunks와 cosine similarity > 0.92
   - 발견 시 → status: 'rejected', reason: 'duplicate'

4. 길이 검사
   - 50자 미만 또는 5000자 초과 → status: 'rejected', reason: 'length'

5. 광고적 표현 검사
   - "최고의", "혁신적인" 등 차단 단어
   - 발견 시 → status: 'rejected', reason: 'ad_language'

6. 안전 검사
   - 프롬프트 인젝션 시도 텍스트 (예: "ignore previous", "system:", 등)
   - 발견 시 → status: 'rejected', reason: 'injection_attempt'
   - 보안 로그에 기록

7. 언어 검사
   - 지원 언어(현재 ko-KR)인지 확인
```

기준 변경은 contract-change Skill로.

### Step 3. evaluated — 품질 평가

자동 통과한 후보를 사람 또는 LLM Critic이 평가한다.

#### LLM Critic 평가 (자동)

```
P-007(Critic) prompt를 후보에 적용.
점수 출력: 8차원 × 0–5점.
quality_score = (sum / 40)  (0–1 정규화)

quality_score >= 0.7 → status: 'evaluated', reviewer: 'auto'
0.5 <= quality_score < 0.7 → status: 'evaluated', reviewer: 'auto', flag: needs_human
quality_score < 0.5 → status: 'rejected', reason: 'low_quality'
```

#### 사람 검토 (선택적)

`flag: needs_human` 또는 `source_kind = 'external_seed'`인 경우:
- 검토자가 review_notes 작성
- 통과 시 status: 'evaluated', reviewer: {user_id}

### Step 4. approved — 승인

evaluated 단계의 후보를 approved_knowledge로 이동시키기 위한 명시적 승인.

#### 승인 기준

```
| source_kind        | 승인 방식                        |
|--------------------|----------------------------------|
| external_seed      | 사용자 명시 승인 필수           |
| manual             | 작성자 자체 승인 가능           |
| user_choice        | 자동 (quality_score >= 0.8)     |
| user_feedback      | 자동 (quality_score >= 0.8)     |
| final_output       | 자동 (quality_score >= 0.85)    |
| brand_memory_extract | 자동 (confidence >= 0.7)      |
```

자동 승인 임계값 변경은 contract-change Skill로.

#### 승인 시 작업

```
1. status: 'evaluated' → 'approved'
2. knowledge/approved_knowledge/{brand_id}/{slug}.md 생성 (Markdown 파일)
3. 메타데이터 YAML frontmatter 작성
4. 사용자 식별 정보 익명화 (user_id → anon_hash)
5. agent_io_logs에 approval 이벤트 기록
```

### Step 5. promoted — rag_documents 승격

approved_knowledge를 검색 가능한 RAG로 승격한다.

#### 승격 작업

```
1. status: 'approved' → 'promoted'
2. rag_documents에 INSERT (source_type: 'user_promoted' 또는 'curated')
3. content를 chunk_size 기준으로 분할 (보통 500–800 토큰 + 100 토큰 overlap)
4. 각 chunk를 임베딩 모델로 벡터화
5. rag_chunks에 INSERT (embedding 컬럼 포함)
6. ivfflat 인덱스 영향 확인 (1000개 이상 일괄 추가 시 REINDEX 권장)
```

#### 승격 후 회귀 평가 (필수)

```
1. eval/golden_set.md의 케이스 중 RAG 영향 받는 케이스 식별
2. 새 RAG 포함 / 제외 두 가지로 동일 prompt 실행
3. 결과 품질 점수 비교
4. 5% 이상 하락하면 → 해당 chunk 비활성화 (is_active: false)
   원인 분석 후 contract-change 절차로 재검토
```

## Rollback 절차

각 단계별 rollback:

```
pending    → 삭제 (hard delete)
filtered   → 자동 (필터 재실행)
evaluated  → status 되돌리기 + review_notes 갱신
approved   → approved_knowledge 파일 보관, status: 'rejected'로 전환
promoted   → rag_chunks 비활성화 (is_active: false), 24h 후 hard delete
             ivfflat 인덱스 REINDEX
```

복원 가능 보장:
- candidate_knowledge에서 promoted까지의 모든 단계 이력은 audit 로그로 남김.
- promoted 후 7일 동안은 즉시 rollback 가능 상태 유지.

## 자주 발생하는 실수

1. **개인정보 마스킹 누락**: Step 1에서 정제 안 하고 그대로 INSERT.
2. **자동 승격 임계값 임의 조정**: 비밀번호 같은 contract. contract-change 없이 절대 변경 금지.
3. **중복 검사 건너뛰기**: cosine similarity 비교 비용 아끼다가 RAG가 같은 지식 반복 누적.
4. **회귀 평가 생략**: 승격 후 golden_set 실행 안 함 → 다음 영상에서 품질 하락 발견.
5. **외부 시드 자동 승인**: external_seed는 항상 사용자 승인 필수.
6. **사용자별 RAG와 global RAG 혼동**: brand별 isolation 필요. global RAG는 익명화된 패턴만.

## 보안 / 프라이버시 체크포인트

```
Step 1: PII 마스킹
Step 2: 프롬프트 인젝션 차단
Step 4: 익명화 (user_id → anon_hash)
Step 5: 사용자별 isolation (brand_id로 검색 필터링)
모든 단계: agent_io_logs에 감사 추적
```

## 산출물

rag-update 1회 실행의 산출물:

```
candidate_knowledge: 상태 전이 로그
knowledge/approved_knowledge/{brand_id}/*.md (해당하는 경우)
rag_documents + rag_chunks INSERT (해당하는 경우)
agent_io_logs: 모든 LLM 호출 기록 (Critic 평가 등)
회귀 평가 결과 (Step 5 진행 시)
```

## 종료 조건

- 후보가 promoted까지 완주 → 정상 종료
- 어느 단계에서든 rejected → 사유 기록 후 종료
- 회귀 평가에서 품질 하락 → 즉시 rollback + contract-change Skill로 위임
