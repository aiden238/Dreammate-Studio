# CLAUDE.md

## 역할

Claude, GPT, Gemini 등 기획·설계·문서 검토형 모델을 위한 라우터다.

## 프로젝트 정의

이 프로젝트는 영상 제작 AI가 아니라 영상기획 AI 에이전트다.

## 핵심 흐름

```text
사용자 입력
→ 의도 분석
→ 부족한 정보 질문
→ 한 줄 기획 방향 승인
→ LLM Wiki/RAG 검색
→ 영상기획안 생성
→ Critic Agent 검증
→ 개선안 반영
→ 결과 저장
→ 사용자 피드백 저장
```

## 검토 유형별 참조

### 제품 기획

- `product/vision.md`
- `product/positioning.md`
- `product/mvp_scope.md`
- `product/user_scenarios.md`
- `docs/contracts/product_boundary.md`
- `docs/contracts/mvp_non_goals.md`

### AI 구조

- `ai_system/architecture.md`
- `ai_system/orchestration/flow.md`
- `ai_system/orchestration/moa_policy.md`
- `docs/contracts/agent_io_contract.md`
- `docs/contracts/output_schema.md`
- `eval/video_planning_eval.md`

### RAG

- `knowledge/llm_wiki/index.md`
- `knowledge/rag/retrieval_policy.md`
- `knowledge/rag/metadata_schema.md`
- `knowledge/rag/quality_filter.md`
- `knowledge/rag/promotion_rule.md`
- `docs/contracts/rag_data_contract.md`

### 프론트/UX

- `apps/web/design.md`
- `apps/web/page_map.md`
- `apps/web/component_map.md`
- `docs/contracts/frontend_design_contract.md`
- `eval/design_review_checklist.md`
- `eval/ux_eval.md`

### 메타 개선

- `meta/self_improvement_loop.md`
- `meta/harness_improvement_proposals.md`
- `meta/guardrails.md`
- `meta/human_review_policy.md`
- `meta/rollback_policy.md`

## 금지

- 전체 문서를 무작정 재작성하지 않는다.
- Phase 범위를 넘겨 구현 제안을 하지 않는다.
- 영상 제작 기능을 MVP에 포함시키지 않는다.
- contracts를 직접 바꾸는 지시를 하지 않는다.
