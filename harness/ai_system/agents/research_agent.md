# research_agent.md

> ⚠️ **PLACEHOLDER** — 본 agent는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 agent로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 21+
priority: low
estimated_final_lines: 180
last_updated: 2026-05-26
```

## Why Placeholder?

MVP(Phase 0~10)는 RAG Lite(`approved_knowledge` + Planning Agent 한정 주입, agent_io §4.7)로 외부 지식을 활용한다. 자체 research agent(웹 검색, 동향 분석, 경쟁 영상 분석 등)는 Custom RAG 인프라(`knowledge/rag/custom_rag_plan.md`)가 도입되는 Phase 21+에서 분리한다.

현재 단계에서 외부 정보가 필요한 케이스는 사용자가 직접 입력하거나 LLM의 사전학습 지식에 의존한다.

## Scope (when filled in)

- 외부 웹 검색 (실시간 트렌드, 키워드 동향)
- 경쟁 영상 분석 (URL 입력 시 메타데이터 + 텍스트 추출)
- 동향 보고서 자동 생성 (Phase 21+ 분석 기능)
- 자동 데이터 수집 (RSS, Twitter/X, 유튜브 트렌드)
- 외부 source → candidate_knowledge 자동 진입 (rag-update Skill 경유)
- 외부 인용 처리 (저작권 안전 마진)
- 실시간 vs 캐시된 결과 분기

## Input/Output (when filled in)

- Input: 검색 쿼리 (사용자 입력) + 도메인 컨텍스트
- Output: 검색 결과 list (title, url, snippet, source, retrieved_at) + 인용 정보
- Envelope: agent_io_contract §2 공통 envelope 따름

## Known Dependencies (when filled in)

- `knowledge/rag/custom_rag_plan.md` (Custom RAG 구조)
- `knowledge/rag/sources.md` (외부 source 정의)
- `docs/contracts/agent_io_contract.md` (envelope)
- `docs/contracts/data_contract.md` (placeholder, 외부 데이터 적재 정책)
- `docs/contracts/privacy_contract.md` (외부 데이터 PII 처리)
- `docs/contracts/llm_security_contract.md` (외부 URL 인젝션 방어)
- 외부 API (검색 엔진 API, 유튜브 Data API 등)

## Fill-In Trigger

- Phase 21+ 진입 (Custom RAG 인프라 가동)
- 또는 외부 검색 기능 요구 임계 도달
- 또는 실시간 트렌드 분석 첫 요구 발생 시

## Related Skill / Phase

- Skill: `ai-architecture-review`, `rag-design`
- Phase: 21+
- 책임자: AI(초안) + 사용자(검토)
