# CLAUDE.md

## 역할

Claude, GPT, Gemini 등 기획·설계·문서 검토형 모델을 위한 라우터다.

## 프로젝트 정의

이 프로젝트는 영상 제작 AI가 아니라 영상기획 AI 에이전트다.
**Hybrid UX**: Discovery Wizard + Quick Mode. 4계층 데이터 모델 (User → Brand → Domain → Series → Video).

## 핵심 흐름

```text
사용자 입력
→ 의도 분석 (Discovery 또는 Quick 자동 분기)
→ 부족한 정보 질문
→ 한 줄 기획 방향 승인
→ LLM Wiki / RAG 검색
→ 영상기획안 3개 생성
→ Critic Agent 검증 (revise 최대 2회)
→ 개선안 반영
→ 결과 저장
→ 사용자 피드백 저장 (Brand Memory 자동 추출)
```

## Skill 구조 (v1.2.0)

모든 Skill은 `.claude/skills/<name>/SKILL.md`에 통합 배치된다.
`applies_to` 태그로 적용 대상 모델 분리:
- `[claude]`: 기획·설계·검토 작업 (이 라우터의 대상)
- `[agents]`: 구현·QA·테스트 작업 (AGENTS.md의 대상)
- `[agents, claude]`: 양쪽 (대부분의 절차 Skill)

자동 트리거는 description 키워드 매칭으로 동작. 수동 호출 불필요.

## 검토 유형별 참조

### 제품 기획

- `product/vision.md`
- `product/positioning.md`
- `product/mvp_scope.md`
- `product/user_scenarios.md`
- `docs/contracts/product_boundary.md`
- `docs/contracts/mvp_non_goals.md`
- Skill: `product-scope-review` (qa-check 카테고리1에 흡수), `phase-review`

### AI 구조

- `ai_system/architecture.md`
- `ai_system/orchestration/flow.md`
- `ai_system/orchestration/moa_policy.md`
- `ai_system/prompts/prompt_registry.md`
- `docs/contracts/agent_io_contract.md`
- `docs/contracts/output_schema.md`
- `eval/video_planning_eval.md`
- Skill: `ai-architecture-review`, `prompt-version-review`

### RAG

- `knowledge/llm_wiki/index.md`
- `knowledge/rag/retrieval_policy.md`
- `knowledge/rag/metadata_schema.md`
- `knowledge/rag/quality_filter.md`
- `knowledge/rag/promotion_rule.md`
- `docs/contracts/rag_data_contract.md`
- Skill: `rag-update` (설계+갱신 통합, 구 rag-design 흡수)

### 프론트 / UX

- `apps/web/design.md`
- `apps/web/page_map.md`
- `apps/web/component_map.md`
- `docs/contracts/frontend_design_contract.md`
- `eval/design_reviews/`
- `eval/ux_eval.md`
- Skill: `design-review`

### 평가 체계

- `eval/golden_set.md`
- `eval/video_planning_eval.md`
- `eval/human_review_rubric.md`
- Skill: `eval-run` (설계+실행 통합, 구 eval-design 흡수)

### 메타 개선

- `meta/self_improvement_loop.md`
- `meta/harness_improvement_proposals.md`
- `meta/guardrails.md`
- `meta/human_review_policy.md`
- `meta/rollback_policy.md`
- `meta/patterns.md`
- `meta/retrospectives/`
- Skill: `meta-retrospective`, `harness-audit`

### 큰 결정 / 교차검증

- `meta/validations/`
- Skill: `multi-llm-validation` (큰 설계 결정, contract 변경, major prompt bump 등)

### 컨텍스트 / 세션 관리

- `meta/handoffs/`
- Skill: `context-compact` (모든 Skill 위 최우선 트리거)

### Phase 운영

- `phases/active/{current-phase}/`
- `PHASE_REGISTRY.md`
- Skill: `phase-start`, `phase-complete`, `phase-review`, `planning-phase-create`

## 우선순위 (충돌 시)

```
context-compact       > 다른 모든 Skill          # 컨텍스트 부족은 항상 최우선
contract-change       > 다른 절차 Skill          # contract 변경은 항상 절차 통과
multi-llm-validation  > 단일 검토 Skill          # 큰 결정은 다중 검증 우선
phase-start           > 다른 절차 Skill          # Phase 컨텍스트 확보 먼저
phase-complete        > meta-retrospective      # 종료 정리 후 회고
```

## 금지

- 전체 문서를 무작정 재작성하지 않는다.
- Phase 범위를 넘겨 구현 제안을 하지 않는다.
- 영상 제작 기능을 MVP에 포함시키지 않는다.
- contracts를 직접 바꾸는 지시를 하지 않는다 (contract-change Skill 절차).
- archive 기본 참조 금지.
