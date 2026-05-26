# custom_rag_plan.md — Phase 21+ 자체 RAG 인프라 계획

> 위치: `knowledge/rag/custom_rag_plan.md`
> 대상 Phase: 21+ (장기)
> 대비 문서: `knowledge/rag/sdk_rag_policy.md` (현재 MVP)
> 연계: `docs/contracts/tech_stack_contract.md`

---

## 0. 이 문서의 위치

MVP의 `pgvector + OpenAI SDK` 구조에서 **자체 RAG 인프라**로 전환하는 장기 계획을 정의한다. Pinecone / Weaviate / Chroma / 자체 구축 후보 비교, 트리거 조건, 마이그레이션 전략을 포함한다.

본 문서는 **검토 단계**이며 실제 시점은 데이터/성능 트리거 도달 후 결정.

---

## 1. 전환 트리거 (sdk_rag_policy §4 정합)

다음 중 하나라도 충족 시 본 계획 활성화:

```yaml
data_scale:
  chunks_total: > 1M
  daily_insert: > 10K
  daily_search: > 100K

performance:
  search_p95_ms: > 500
  postgres_memory_gb: > 16
  etl_batch_min: > 60

features:
  hybrid_search_required: true   # BM25 + vector
  multi_provider_required: true   # OpenAI + Cohere + ...
  reranking_required: true

cost:
  postgres_monthly_usd: > 500
  postgres_vs_pinecone_ratio: > 1.0
```

---

## 2. 후보 비교

### 2.1 Pinecone

```yaml
장점:
  - 운영 부담 0 (managed)
  - 자동 scaling
  - 멀티 region
  - hnsw + product quantization
단점:
  - 비용 $70/월부터 (Pinecone Standard)
  - 트랜잭션 일관성 약함 (Postgres와 분리)
  - 데이터 종속 (이전 비용 ↑)
적합 시점:
  - chunks 1M-10M
  - 운영자 수 적음 (DevOps 부담 ↓ 우선)
```

### 2.2 Weaviate

```yaml
장점:
  - 오픈소스 + managed 옵션
  - 하이브리드 검색 내장 (BM25)
  - GraphQL API
  - 멀티 모달 (이미지/텍스트)
단점:
  - 자체 호스팅 시 운영 부담
  - 학습 곡선 (스키마 정의 방식)
적합 시점:
  - 하이브리드 검색 필수
  - 멀티 모달 데이터 도입
```

### 2.3 Chroma

```yaml
장점:
  - 가장 단순 (Python SDK)
  - 무료 (오픈소스)
  - 빠른 프로토타입
단점:
  - production scale 검증 부족
  - 분산 처리 약함
  - 운영자 수 ↑ 필요
적합 시점:
  - 중간 규모 (100K-500K chunks)
  - 단일 인스턴스로 충분
```

### 2.4 자체 구축 (Faiss + custom service)

```yaml
장점:
  - 완전 제어 (성능 / 비용 최적화)
  - 종속성 0
  - 멀티 모달 / 하이브리드 자유 설계
단점:
  - 초기 구축 비용 매우 큼 (개발자 N개월)
  - 운영 부담 가장 큼
  - 분산 처리 / 인덱스 재구축 직접 관리
적합 시점:
  - chunks > 10M
  - 매우 특수한 요구 (legal / 데이터 주권)
  - 자체 임베딩 모델 운영
```

---

## 3. 비용 비교 (1년 운영 추정)

Phase 21+ 가정: chunks 5M, 일일 검색 50K, 일일 INSERT 5K.

```
pgvector (현재 연장):
  Postgres 인스턴스 (8 vCPU, 32GB RAM): $400/월
  스토리지 (500GB): $50/월
  백업: $30/월
  → 연 $5,760

Pinecone Standard:
  $70/월 (Starter) ~ $500/월 (Standard)
  → 연 $840 ~ $6,000

Weaviate Cloud:
  $25/월 (Sandbox) ~ $300/월 (Production)
  → 연 $300 ~ $3,600

자체 구축 (AWS):
  EC2 (m5.2xlarge): $280/월
  EBS (1TB): $100/월
  개발 인건비 (3개월): $30,000 (1회성)
  운영 인건비 (월 10시간): $1,000/월
  → 1년차 연 $44,560 / 이후 연 $14,560
```

데이터 규모와 운영 부담을 고려하면 **Phase 21+ 초입에는 Pinecone 또는 Weaviate Cloud 우선 검토**.

---

## 4. 마이그레이션 전략

### 4.1 단계 1: dual-write (병행 운영, 1-2개월)

```
ETL이 candidate → promoted 시:
  1. 기존 pgvector에 INSERT (기존 검색 유지)
  2. 새 vector DB에도 INSERT (동시)
  3. 검색은 여전히 pgvector

목표: 데이터 정합성 검증, 새 DB 안정성 확인
```

### 4.2 단계 2: shadow read (병행 검색, 1개월)

```
사용자 검색 시:
  1. pgvector 검색 (응답에 사용)
  2. 새 DB 검색 (응답에 사용 안 함, 로그만)
  3. 두 결과 비교 → 회귀 평가

목표: recall@5 동등성 검증, latency 비교
```

### 4.3 단계 3: gradual cutover (점진 전환, 2주)

```
1주차: 10% 트래픽 새 DB로 → 모니터링
2주차: 50% → 모니터링
3주차: 100% → pgvector는 read-only (회수 윈도우)
```

### 4.4 단계 4: pgvector 정리

```
1주: pgvector 데이터 백업 (cold storage)
2주: pgvector 인덱스 DROP
3주: rag_chunks 테이블 archive
```

### 4.5 rollback 정책

각 단계 실패 시:

```
단계 1 실패: 새 DB INSERT 비활성화 → pgvector 단독 운영
단계 2 실패: shadow read 비활성화 → pgvector 단독
단계 3 실패: 트래픽 비율 복귀 → 0% 새 DB
단계 4 실패: pgvector 인덱스 재구축 → 복귀
```

---

## 5. contract / 코드 영향

### 5.1 rag_data_contract 수정 사항

```
- §7 pgvector 인덱스 정책 → 새 DB 인덱스 정책으로 교체
- §11 metadata 스키마 → 새 DB 필드 매핑 명시
- §6 임베딩 모델 → provider 선택 영향 (Cohere 검토 시)
```

contract-change Skill 절차 필수.

### 5.2 코드 변경

```python
# 기존 (sdk_rag_policy)
class RAGProvider:
    def search(self, query, top_k): ...
    def insert(self, chunk, embedding): ...

# 신규 (custom_rag_plan)
class PineconeRAG(RAGProvider): ...
class WeaviateRAG(RAGProvider): ...

# 호출부는 인터페이스만 의존
rag = get_rag_provider()
results = rag.search(query, top_k=5)
```

sdk_rag_policy §6의 provider 추상화 사전 조치가 여기서 빛난다.

---

## 6. 회귀 평가

전환 검증을 위한 `eval/golden_set.md` 활용:

```yaml
회귀 평가 기준:
  recall_at_5: >= 기존 - 3%      # 검색 정확도 유지
  latency_p95_ms: <= 200          # 성능 유지
  cost_per_search_usd: <= 기존    # 비용 유지
  error_rate: <= 0.1%             # 안정성 유지

평가 데이터:
  - golden_set 50개 시드 케이스
  - 매주 1회 회귀 실행 (dual-write 기간)
  - 모든 차원 충족 시에만 다음 단계 진행
```

---

## 7. 의사결정 절차

```
1. 전환 트리거 도달 → 운영자 review
2. 후보 3개 (Pinecone / Weaviate / Chroma) 비용/기능 비교 보고서 작성
3. multi-llm-validation Skill 사용 (큰 결정)
4. 의사결정 후 contract-change Skill로 rag_data_contract 수정
5. dual-write 단계 시작 (1-2개월)
6. shadow read (1개월)
7. gradual cutover (2주)
8. 정리 (3주)
```

총 기간: 약 4-6개월.

---

## 8. 위험 / 완화

| 위험 | 완화 |
|---|---|
| 새 DB 데이터 손실 | dual-write 기간 충분 (1-2개월) |
| recall 저하 | shadow read에서 회귀 평가 통과 후만 진행 |
| latency 증가 | gradual cutover로 트래픽 점진 증가 |
| 비용 폭증 | 단계 1 부터 비용 모니터링 |
| 벤더 종속 | provider 추상화 layer 유지 |
| 마이그레이션 실패 | 각 단계 rollback 절차 |

---

## 9. Open Questions

1. 전환 트리거 도달 시점 추정 — Phase 21+ 가 너무 늦지 않을까 (Phase 11+ 또는 15+ 검토).
2. Pinecone vs Weaviate — 운영 부담 vs 기능 균형.
3. 자체 임베딩 모델 운영 (한국어 특화) 가치 — 비용 대비 recall 향상 폭.
4. 멀티 region 필요성 — 글로벌 확장 시점 (Phase 21+ 다국어 도입과 연동).
5. dual-write 기간 1-2개월이 충분한지 — 트래픽 패턴에 따라 더 길어질 수 있음.
6. contract 변경을 단계별로 할지 (단계 1 진입 vs cutover 시점) — 운영 안정성 vs 변경 빈도.

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 후보 4개(Pinecone/Weaviate/Chroma/자체) 비교,
                      비용 1년 추정, 마이그레이션 4단계, 회귀 평가, 의사결정 절차.
```
