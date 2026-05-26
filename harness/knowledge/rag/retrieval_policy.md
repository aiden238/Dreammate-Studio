# retrieval_policy.md — RAG 검색 정책

> 위치: `knowledge/rag/retrieval_policy.md`
> 단일 출처: `docs/contracts/agent_io_contract.md` §4.7 + `docs/contracts/rag_data_contract.md` §5
> 적용 agent: **Planning Agent (P-006) 한정** — Intent / Critic / Rewriter는 RAG 직접 호출 금지

---

## 0. 이 문서의 위치

영상기획 AI 에이전트의 **검색 단계 정책**을 정의한다. 어떤 데이터를 어떤 방식으로 검색하고, 몇 개를 채택할지 결정한다. 본 문서는 `agent_io_contract.md` §4.7과 `rag_data_contract.md` §5에 정의된 정책의 **운영자 친화 해설서**다. 수치 충돌 시 contract 우선.

---

## 1. 검색 트리거

검색은 다음 시점에 **단 1회** 발생한다:

```
Intent 단계 완료
  → 사용자가 approved_direction 승인
  → orchestrator가 Planning(P-006) 호출 직전
  → RAG 검색 1회 실행
  → 결과 chunk[] 를 P-006 prompt에 주입
```

다른 시점(Discovery 카드 생성 / Critic 평가 / Rewriter 재작성)에는 절대 호출하지 않는다. 이유: 비용 증가, 일관성 저하, 검색 결과를 둘러싼 agent 간 충돌.

---

## 2. 검색 파라미터 (Phase 1 고정)

```yaml
top_k: 5                      # pgvector cosine similarity 상위 5개 가져오기
similarity_threshold: 0.7     # 이 미만은 application-level 필터에서 제외
final_adoption: 3             # threshold 통과한 chunk 중 상위 최대 3개만 prompt 주입
exclude_filter:
  - is_active: false          # 회수된 document 제외
  - status_not_in: [pending, filtered, evaluated, approved, rejected]
                              # promoted만 검색 대상
metadata_filter: null         # Phase 1은 brand_id / domain 필터 안 함 (Phase 2+ 검토)
```

이 4개 숫자는 **모두 단일 출처**가 `rag_data_contract.md §5.2`다. 변경 시 contract-change Skill 절차 필수.

---

## 3. 검색 쿼리 구성

### 3.1 쿼리 텍스트

```
query_text =
    approved_direction
    + " | "
    + selected_series.name
    + " | "
    + selected_domain.name
```

- 공백 + pipe 문자(`|`)로 결합
- 시리즈/도메인이 null인 경우(Quick Mode 일부): pipe 없이 approved_direction만
- 길이 제한: 최대 500자 (이상 시 앞 500자만 사용)

### 3.2 임베딩 모델

```
모델: text-embedding-3-small (OpenAI)
차원: 1536
provider: server-side OPENAI_API_KEY 사용
```

쿼리 임베딩은 동일한 모델로 처리되어야 검색이 의미를 가진다 (chunk 임베딩과 일치). 모델 변경 시 모든 chunks 재임베딩 (`rag_data_contract.md §6.3` breaking change).

---

## 4. 검색 대상 범위

### 4.1 포함 (검색 대상)

- `rag_chunks` 중 `rag_documents.is_active = true`
- 원본 candidate가 `status = 'promoted'`인 항목만
- 출처(`source_kind`)는 `manual / external_seed / final_output / user_choice / user_feedback` 모두 허용 (이미 5단계 승격 거침)

### 4.2 제외 (검색 대상 아님)

- `candidate_knowledge`의 `pending / filtered / evaluated / approved` 상태 — **본체 테이블이 아님**
- `rag_documents.is_active = false` (회수된 항목)
- `brand_memory_entries` — 사용자별 prompt 직접 주입 경로 (RAG 우회)
- 사용자 입력 원본 (`discovery_choices.direct_input`, `user_feedback.text`) — candidate_knowledge로 승격된 경우에만 간접 노출

---

## 5. 캐싱 정책

### 5.1 query embedding 캐싱

```
키: SHA256(query_text)
값: vector(1536)
TTL: 1시간
저장소: in-memory (Phase 1) / Redis (Phase 2+)
효과: 동일 쿼리 재검색 시 임베딩 비용 0
```

### 5.2 검색 결과 캐싱

```
키: SHA256(query_text) + rag_chunks_version
값: chunk_id[]
TTL: 1시간
무효화: rag_chunks INSERT / UPDATE 발생 시 version 증가 → 캐시 자동 무효
```

### 5.3 캐싱 안 함

- Planning agent 응답 전체는 캐싱 안 함 (다양성 우선 — `agent_io_contract §4.6`)
- 단 같은 request_id 재시도는 캐싱 활용 (idempotency)

---

## 6. 쿼리 변형 (Phase 5+ 검토)

현재 Phase 1은 단순 쿼리만 사용. 다음 기법은 Phase 5+ 검토:

### 6.1 HyDE (Hypothetical Document Embeddings)

- LLM이 "가상의 정답 문서" 생성 → 그것을 임베딩 → 검색
- 장점: 짧은 쿼리 → 풍부한 검색
- 단점: LLM 호출 추가 비용 (한 번 더), latency +500ms

### 6.2 Query Rewriting

- 원본 쿼리를 LLM으로 2-3개 변형 → 각각 검색 → 합집합
- 장점: recall 향상
- 단점: 비용 N배

### 6.3 Multi-vector

- 한 쿼리를 여러 임베딩(예: 키워드 / 의도 / 톤)으로 표현
- 장점: 다차원 매칭
- 단점: 구현 복잡도

---

## 7. 빈 결과 처리

### 7.1 threshold 미통과 (0건 채택)

```yaml
조건: top_k 5개 모두 similarity < 0.7
처리:
  - Planning prompt에 rag_context = [] 주입
  - response envelope의 validation.warnings에 "no_rag_reference" 추가
  - 사용자 UI: "참고 자료 없이 만든 결과예요" 안내 노출
  - 학습 신호: 해당 쿼리를 Slack 알림 (데이터 부족 신호)
```

### 7.2 DB / pgvector 실패

```yaml
조건: timeout, connection error, index corruption
에러 코드: E-RAG-001 (timeout) / E-RAG-004 (index)
처리:
  - Planning은 rag_context = [] 로 계속 진행 (graceful degradation)
  - 사용자 응답에 "참고 자료 검색이 일시적으로 어려웠어요" 표시
  - Slack #ops-alert 알림 (15분 이내 3건 발생 시)
```

---

## 8. 검색 결과 사용 기록

P-006 응답의 `rag_used[]`에 실제 prompt 주입된 chunk만 기록 (최대 3개):

```json
"rag_used": [
  {
    "source_id": "<rag_chunks.chunk_id>",
    "title": "<rag_documents.title>",
    "used_reason": "쇼츠 hook에서 질문형 패턴 참고"
  }
]
```

- `output_schema.md §8` P-006 출력 스키마와 정합
- 사용자 UI에서 "참고한 자료" 영역으로 노출 가능 (출처 인용)
- 운영자 review에서 RAG 활용도 추적

---

## 9. 성능 목표

```yaml
검색 latency p50: < 80ms
검색 latency p95: < 200ms
검색 latency p99: < 500ms
임계 알림: p95 ≥ 200ms 가 15분 이상 지속 → Slack #ops-alert
```

인덱스 재구축 시점 / hnsw 전환 검토는 `rag_data_contract.md §7` 참조.

---

## 10. Phase별 마일스톤

### Phase 1 (현재 MVP)

- 단순 쿼리 + 단일 임베딩 모델
- 캐싱 in-memory
- metadata filter 없음

### Phase 5+

- HyDE / Query Rewriting 검토
- Redis 캐싱
- domain 단위 filter

### Phase 11+

- hnsw 인덱스 전환 검토 (chunks > 100K 시)
- 다국어 (ko/en/ja) 분리 검색

### Phase 21+

- 외부 사례 자동 크롤링 + 통합 검색
- 사용자 그룹 격리 (team workspace)

---

## 11. Open Questions

1. similarity_threshold 0.7 — 초기 데이터 누적 후 0.65 또는 0.75로 조정 필요한지 데이터 수집.
2. top_k=5 — recall 향상을 위해 10으로 늘리고 후처리 reranking 검토 (Phase 5+).
3. 검색 결과 0건 시 fallback: brand_memory만으로 Planning 진행 vs 사용자에게 "정보 더 필요" 안내 후 재질문.
4. Quick Mode (시리즈/도메인 미선택)에서 검색 품질이 Discovery 대비 얼마나 떨어지는지 측정.
5. 사용자별 검색 가중치 — 본인이 과거 like한 chunk를 우선 노출할지 (Phase 7+ 개인화).
6. RAG 검색을 Critic의 brand_consistency 검사에도 확장할지 (현재 Planning 한정).

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. agent_io §4.7 + rag_data §5 단일 출처 명시,
                      캐싱/쿼리변형/빈결과/성능목표 추가, Phase 마일스톤 정리.
```
