# rag_strategy.md — RAG 전략 결정 기록 (ADR)

> 위치: `docs/decisions/rag_strategy.md`
> 상태: Phase 0 Sprint S5 deep 작성
> 참조: `docs/contracts/rag_data_contract.md`, `knowledge/rag/`, `ai_system/orchestration/flow.md`

---

## 0. 본 문서의 위치

본 ADR은 RAG (Retrieval-Augmented Generation) 구축 전략의 단계별 결정 기록이다.
MVP의 SDK 기반 → Phase 11+ 멀티 provider → Phase 21+ Custom RAG 인프라로의 진화 경로를 정의한다.

---

## 1. 결정 요약

```
Phase 1-10 (MVP):       SDK 기반 (OpenAI Embeddings + pgvector 직접 호출)
                        text-embedding-3-small (1536), ivfflat 인덱스
                        candidate_knowledge 5단계 승격 (rag_data §4)
                        top_k=5 → sim≥0.7 → 채택 3 (agent_io §4.7)
Phase 11-20:            멀티 provider 검토 (Anthropic / Voyage / Cohere)
                        hybrid search (vector + BM25) 도입
                        re-ranking layer (cross-encoder)
Phase 21+:              Custom RAG 인프라 (Pinecone / Weaviate / 자체)
                        research_agent 활성화 (외부 웹 검색)
                        지식 그래프 통합
```

---

## 2. 대안 비교

| 방식 | 장점 | 단점 | 채택 시점 |
|------|------|------|---------|
| **pgvector + SDK** | 단일 DB, 운영 단순 | 대규모 검색 한계 | **MVP** |
| Pinecone | 관리형, 확장성 우수 | 비용 ($70+/월) | Phase 21+ 검토 |
| Weaviate | 자체 호스팅 가능 | 운영 부담 | Phase 21+ 대안 |
| Qdrant | Rust 기반 빠름 | 생태계 작음 | 후보 |
| Elastic + dense | 하이브리드 강력 | 무거움 | Phase 11+ 검토 |
| 자체 구축 | 도메인 특화 | 개발 비용 큼 | Phase 21+ 일부 |

---

## 3. 선택 이유

- **단순성**: pgvector는 Supabase에 포함, 별도 인프라 불필요
- **비용**: 문서 10만 개까지 무료 tier에서 충분
- **이식성**: 향후 Pinecone 등으로 마이그레이션 시 메타데이터 schema 보존 가능 (metadata_schema.md)
- **MVP 범위**: 사용자 1만 명 / 문서 100만 chunk까지 pgvector ivfflat로 sub-second 검색 가능

---

## 4. 트레이드오프

- pgvector ivfflat → 정확도 (recall) 약간 손실, 속도 우선
- 단일 provider (OpenAI) → embedding 모델 변경 시 전체 재인덱싱 필요
- hybrid search 미구현 → 키워드 정확 매칭 약함 (Phase 11+에서 보강)
- re-ranking 없음 → top-3 채택 시 noise 가능 (Critic이 일부 보정)

---

## 5. 핵심 정책

### 5.1 검색 정책 (단일 출처: agent_io_contract §4.7)
```
top_k = 5
similarity_threshold = 0.7
adopt_count = 3
cache_ttl = 1 hour (동일 쿼리)
```

### 5.2 5단계 승격 (rag_data_contract §4)
- pending → filtered → evaluated → approved → promoted (+ rejected)
- 단계별 자동 / 수동 책임자 (knowledge/rag/promotion_rule.md)
- P-EVAL-1 prompt가 filtered → evaluated 자동 평가 담당

### 5.3 chunking 정책 (knowledge/rag/chunking_policy.md)
- 의미 단위 200-500 토큰
- overlap 50 토큰
- 문서 유형별 분할 전략

### 5.4 metadata 표준 (knowledge/rag/metadata_schema.md)
- source_kind / source_id / brand_id / language / quality_score / tags / status / access_scope

---

## 6. 재검토 트리거

- 문서 100만 chunk 도달 → pgvector ivfflat 성능 측정 / hnsw 검토
- 검색 응답 1초 초과 → 인덱스 튜닝 또는 Pinecone 도입
- 다국어 사용자 도입 (Phase 11+) → 멀티 provider 검토
- 임베딩 비용 월 $200 초과 → 자체 임베딩 모델 또는 무료 alternative 검토

---

## 7. 향후 진화 후보

### 7.1 Hybrid Search (Phase 11+)
- vector (dense) + BM25 (sparse) 결합
- 키워드 정확도 + 의미 검색 강점 동시 활용

### 7.2 Re-ranking (Phase 11+)
- cross-encoder 모델로 top-10 → top-3 재정렬
- Cohere Rerank API 또는 자체 fine-tune

### 7.3 Knowledge Graph (Phase 21+)
- brand_memory ↔ candidate_knowledge ↔ video_project 관계 그래프화
- 추론 기반 검색 (단순 유사도 → 관계 추론)

### 7.4 research_agent 활성화 (Phase 21+)
- 외부 웹 검색 (Tavily / Perplexity 또는 자체)
- 실시간 트렌드 / 경쟁 영상 / 시즌 이슈 반영

---

## 8. 관련 Skill

- `rag-design`: 구조적 변경 (provider 전환, 새 layer 추가)
- `rag-update`: 일상 운영 (지식 추가, 승격)
- `cost-review`: 임베딩 비용 분석

---

## 9. Open Questions

1. **pgvector hnsw vs ivfflat 전환 시점**: 문서 수? 응답 시간? 정확도 측정 방법?
2. **임베딩 모델 변경 시 재인덱싱**: 점진 vs 일괄? 비용 / 다운타임 트레이드오프?
3. **multi-language 지원**: Phase 11+ 진입 시 언어별 임베딩 분리 / 통합?
4. **prompt cache 도입**: 동일 RAG context 재사용으로 비용 절감 가능 (OpenAI prompt caching)
5. **Custom RAG 전환 비용**: Pinecone 마이그레이션 비용 / 시간 / 운영 부담 정량화

---

## 10. 변경 이력

- 2026-05-26: Phase 0 S5에서 placeholder 해소, ADR 형식으로 작성
