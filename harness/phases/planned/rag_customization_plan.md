# rag_customization_plan.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 21+
priority: low
estimated_final_lines: 160
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1-20은 Claude SDK 내장 RAG Lite(pgvector 기반)로 충분하다.
문서 100만 chunk 도달 또는 응답 시간 한계 도달 시점까지 커스텀 RAG 인프라
전환 계획을 상세화할 필요가 없다.

## Scope (TBD)

본 파일이 다룰 범위:
- SDK RAG (pgvector) → 커스텀 RAG 인프라 전환 판단 기준
- 후보 벡터 DB 비교 (Pinecone / Weaviate / Qdrant / 자체 pgvector)
- 마이그레이션 전략 (점진 전환 vs. 일괄 전환, 다운타임 최소화)
- 청킹 정책 고도화 (`knowledge/rag/chunking_policy.md` 연계)
- 하이브리드 검색 (BM25 + Dense) 도입 방안
- 임베딩 모델 교체 전략 (claude-embed → 전용 임베딩 모델)
- 비용 모델 비교 (managed 서비스 vs. 자체 호스팅)

## Known Dependencies (when filled in)

- `docs/decisions/rag_strategy.md` — RAG 전략 결정 기록
- `knowledge/rag/custom_rag_plan.md` — 커스텀 RAG 상세 계획
- `knowledge/rag/chunking_policy.md` — 청킹 정책
- `knowledge/rag/retrieval_policy.md` — 검색 정책
- `knowledge/rag/metadata_schema.md` — 메타데이터 스키마
- `logs/eval_log.md` — RAG 품질 추이 데이터
- 운영 메트릭 (p95 응답 시간, chunk 수 추이)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- RAG 인덱싱 문서가 100만 chunk 도달
- 또는 RAG 검색 p95 응답 시간이 2초 초과 (기준 초과 2주 이상 지속)

## 예시 전환 단계 형식 (fill-in 시 참고)

```
Phase A: 평가 (2주)
  - 후보 벡터 DB 3개 벤치마크 (속도, 비용, 운영 편의성)
  - 현재 RAG 품질 베이스라인 측정

Phase B: 파일럿 (4주)
  - 선택한 DB로 20% 트래픽 라우팅
  - A/B 품질 비교

Phase C: 전환 (2주)
  - 100% 전환 + SDK RAG 롤백 준비 유지 (2주)
```

## Related Skill / Phase

- Skill: rag-design, rag-update
- Phase: 21+
- 책임자: 운영자 / AI
