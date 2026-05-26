# sdk_rag_policy.md — MVP SDK 기반 RAG 정책

> 위치: `knowledge/rag/sdk_rag_policy.md`
> 대상 Phase: 1-10 (MVP)
> 대비 문서: `knowledge/rag/custom_rag_plan.md` (Phase 21+ 자체 구축)
> 연계: `docs/contracts/tech_stack_contract.md`, `docs/contracts/rag_data_contract.md`

---

## 0. 이 문서의 위치

MVP Phase 1-10 동안 **pgvector + OpenAI SDK 직접 사용**으로 RAG를 운영하는 정책을 정의한다. Pinecone / Weaviate / Chroma 등 외부 vector DB를 도입하지 않는 이유와 한계, 전환 트리거를 포함한다.

대안인 자체 RAG 인프라 계획은 `custom_rag_plan.md` 참조.

---

## 1. 핵심 결정: pgvector + OpenAI SDK

```yaml
임베딩 SDK: OpenAI Python SDK (openai)
모델: text-embedding-3-small (1536 차원)
벡터 DB: PostgreSQL + pgvector extension (ivfflat 인덱스)
검색 라이브러리: psycopg + 직접 SQL 쿼리
인프라: 단일 Postgres 인스턴스 (Phase 1-10)
```

---

## 2. 이 선택의 장점

### 2.1 운영 단순성

```
- DB 1개 (Postgres) — 백업/모니터링/마이그레이션 통합
- 트랜잭션 일관성 — rag_chunks INSERT + candidate_knowledge UPDATE 같은 트랜잭션
- 운영자 학습 비용 ↓ — SQL만 알면 됨
- 신규 인프라 비용 0 — 기존 Postgres에 extension 추가
```

### 2.2 빠른 구축

```
- pgvector extension 활성화: 1줄 SQL (CREATE EXTENSION vector)
- 인덱스 생성: 1줄 SQL
- 검색 쿼리: 표준 SQL (ORDER BY embedding <=> $1::vector)
- 신규 학습 곡선 거의 없음
```

### 2.3 비용 효율

```
Phase 1 예상 운영비:
  - Postgres 인스턴스: $20-50/월 (기존 DB와 공유)
  - OpenAI 임베딩: < $1/월 (Phase 1)
  - 인덱스 추가 메모리: ~100MB (chunks 500개)
  - 총: $0 추가 (기존 인프라에 흡수)

대안 (Pinecone) 비교:
  - Pinecone Free Tier: 100K 벡터까지 무료
  - Pinecone Standard: $70/월 ~ (인프라 별도)
```

### 2.4 표준 SQL 활용

```
- WHERE 절로 metadata 필터 (brand_id, language)
- JOIN으로 rag_documents.is_active 확인
- 트랜잭션으로 일관성 보장
- pg_stat_statements 로 쿼리 분석
```

---

## 3. 이 선택의 단점

### 3.1 멀티 provider 어려움

```
OpenAI에 임베딩 종속.
대안 (Cohere / Anthropic / 자체 모델) 도입 시:
  - 모든 chunks 재임베딩 필요
  - 차원 변경 시 인덱스 재구축
  - 코드 분기 복잡 (provider 추상화 layer 필요)
```

### 3.2 고급 검색 기능 부재

```
없음:
- 하이브리드 검색 (vector + keyword BM25)
- reranking layer (Cohere Rerank API 별도 호출 필요)
- 자동 query expansion
- multi-vector indexing

있음:
- cosine similarity (ivfflat)
- 단순 metadata 필터 (Phase 2+)
```

### 3.3 확장성 한계

```
chunks 수별 예상 성능:
  ~ 10K:    p95 < 50ms (양호)
  ~ 100K:   p95 < 150ms (lists 재조정 필요)
  ~ 1M:     p95 < 500ms (hnsw 검토 또는 외부 DB)
  ~ 10M:    pgvector 한계 (외부 vector DB 필수)
```

### 3.4 운영 부담

```
- pgvector 버전 업그레이드 시 인덱스 재구축
- Postgres 메모리 부족 시 검색 성능 급락
- 백업 크기 증가 (벡터 데이터)
```

---

## 4. 한계 / 전환 트리거

다음 조건 중 하나라도 충족하면 `custom_rag_plan.md` 진행 검토:

### 4.1 데이터 규모

```
- rag_chunks 누적 > 1M 도달
- 일일 INSERT > 10K
- 일일 검색 > 100K
```

### 4.2 성능 저하

```
- 검색 p95 > 500ms 가 지속 (인덱스 튜닝으로도 해결 불가)
- Postgres 메모리 사용 > 16GB (다른 워크로드 영향)
- ETL 배치 처리 시간 > 1시간
```

### 4.3 기능 요구

```
- 하이브리드 검색 (BM25 + vector) 필수 요구사항 도래
- 멀티 provider 임베딩 (Cohere / Anthropic) 필요
- reranking layer 도입 필요 (검색 품질 정체)
```

### 4.4 비용

```
- Postgres scaling 비용 > 외부 vector DB 운영비 (역전)
- 예: Postgres $500/월 vs Pinecone $200/월
```

---

## 5. Phase 1-10 운영 룰

### 5.1 임베딩 호출

```python
from openai import OpenAI
client = OpenAI()  # OPENAI_API_KEY env 사용

def embed(text: str) -> list[float]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding  # 1536 차원

def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts  # max 50 per batch
    )
    return [d.embedding for d in resp.data]
```

### 5.2 검색 쿼리

```python
def search(query_text: str, top_k: int = 5) -> list[dict]:
    q_embedding = embed(query_text)
    sql = """
        select c.chunk_id, c.document_id, d.title, c.content, c.metadata,
               1 - (c.embedding <=> %s::vector) as similarity
        from rag_chunks c
        join rag_documents d on d.document_id = c.document_id
        where d.is_active = true
        order by c.embedding <=> %s::vector
        limit %s
    """
    rows = db.execute(sql, (q_embedding, q_embedding, top_k))
    return [r for r in rows if r["similarity"] >= 0.7][:3]
```

### 5.3 ETL 배치

```python
def promote_batch():
    candidates = db.fetch("""
        select * from candidate_knowledge
        where status = 'approved'
        limit 50
    """)
    for c in candidates:
        chunks = chunk_content(c.content)  # chunking_policy 참조
        embeddings = embed_batch([ch.content for ch in chunks])
        for i, (ch, emb) in enumerate(zip(chunks, embeddings)):
            db.execute("""
                insert into rag_chunks
                (document_id, chunk_index, content, embedding, metadata)
                values (%s, %s, %s, %s, %s)
            """, (c.document_id, i, ch, emb, ch.metadata))
        db.execute("""
            update candidate_knowledge
            set status='promoted', promoted_chunk_id=%s
            where candidate_id=%s
        """, (chunks[0].chunk_id, c.candidate_id))
```

### 5.4 모니터링

```yaml
지표:
  - 일일 임베딩 호출 수 / 비용
  - 검색 latency p50 / p95 / p99
  - 인덱스 메모리 사용량
  - 인덱스 hit rate (sequential scan 비율)

알림:
  - 검색 p95 > 200ms 가 15분 지속 → Slack
  - 임베딩 비용 > $10/일 → Slack (Phase 1 임계)
  - pgvector 메모리 > 1GB → Slack
```

---

## 6. provider lock-in 최소화 (대비)

미래 멀티 provider 도입을 위한 사전 조치:

```python
# 임베딩 함수를 인터페이스로 분리
class EmbedProvider:
    def embed(self, text: str) -> list[float]: ...

class OpenAIEmbed(EmbedProvider):
    def embed(self, text): ...

# Phase 11+ 도입 시 다른 provider 추가
class CohereEmbed(EmbedProvider):
    def embed(self, text): ...

# 호출부는 provider 추상화
embedder: EmbedProvider = get_embed_provider()
```

코드 분리만 미리 해두면 전환 비용 ↓.

---

## 7. Phase 11+ 검토 항목

다음 시점에 sdk_rag_policy 재검토 필요:

```
- chunks > 100K 도달 (인덱스 hnsw 전환 검토)
- 일일 검색 > 10K (Postgres scaling 필요)
- 멀티 provider 임베딩 요구 (provider 추상화)
- 하이브리드 검색 요구 (custom_rag_plan 검토)
```

이 시점에는 `custom_rag_plan.md`의 마이그레이션 절차 활성화.

---

## 8. Open Questions

1. text-embedding-3-large 도입 시점 — small 대비 비용 5배 / recall +3-5%.
2. provider 추상화 layer 시점 — Phase 1 미리 vs Phase 11+ 필요 시.
3. pgvector hnsw 전환 시점 — chunks 100K vs 50K (메모리 여유 따라).
4. reranking layer (Cohere Rerank) — 비용 대비 검색 품질 향상 측정 필요.
5. 임베딩 재계산 정책 — 기존 chunks를 모델 변경 시 점진적 vs 일괄.
6. Postgres scaling 임계 — read replica vs partitioning vs 외부 DB 전환.

---

## 9. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. pgvector + OpenAI SDK 결정 근거,
                      Phase 1-10 운영 룰, 전환 트리거, provider 추상화 사전 조치.
```
