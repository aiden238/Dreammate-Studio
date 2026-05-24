# AGENTS.md

## 역할

Codex, Copilot Code, Claude Code 등 구현형 AI 에이전트용 라우터 문서다.
모든 지침 본문을 담지 않고, 작업 유형별 참조 문서를 안내한다.

## 기본 원칙

1. 현재 active Phase만 우선 참조한다.
2. archive는 기본 참조하지 않는다.
3. docs/contracts는 직접 수정하지 않는다.
4. 계약 변경은 `docs/contract_changes/` 또는 `meta/proposals/`에 제안한다.
5. MVP 범위 밖 기능을 임의로 구현하지 않는다.
6. 영상 제작 / 자동 편집 / 자동 업로드는 MVP에 넣지 않는다.

## Skill 구조 (v1.2.0)

모든 Skill은 `.claude/skills/<name>/SKILL.md`에 통합 배치된다.
구현 모델 대상 Skill은 frontmatter에 `applies_to: [agents, ...]` 명시.
Codex / Copilot Code는 description / `applies_to` 태그로 적용 여부 판별.

## 기본 참조 순서

```text
1. PROJECT_STATE.md                   (current_phase, migration_progress 확인)
2. PHASE_REGISTRY.md
3. phases/active/{current-phase}/    (goals, scope, non_goals, acceptance)
4. instruction_index/routes.yaml     (작업 유형별 묶음 로드)
5. 관련 docs/contracts/*
6. 관련 eval/*
7. 관련 .claude/skills/*/SKILL.md   (applies_to에 agents 포함된 것)
```

## 작업별 라우팅

### 프론트 구현

- `apps/web/design.md`
- `apps/web/page_map.md`
- `apps/web/component_map.md`
- `docs/contracts/frontend_design_contract.md`
- `docs/contracts/api_contract.md`
- `docs/contracts/output_schema.md`
- `docs/contracts/error_response_contract.md`
- Skill: `design-review`, `qa-check`

### 백엔드 구현

- `docs/contracts/api_contract.md`
- `docs/contracts/db_schema.md`
- `docs/contracts/output_schema.md`
- `docs/contracts/error_response_contract.md`
- `backend/fastapi/README.md`
- Skill: `contract-change`, `qa-check`

### AI 파이프라인 구현

- `ai_system/architecture.md`
- `ai_system/orchestration/flow.md`
- `ai_system/prompts/prompt_registry.md`
- `docs/contracts/agent_io_contract.md`
- `docs/contracts/output_schema.md`
- `eval/video_planning_eval.md`
- Skill: `agent-io-check`, `prompt-version-review`, `eval-run`

### RAG 구현

- `knowledge/rag/metadata_schema.md`
- `knowledge/rag/retrieval_policy.md`
- `knowledge/rag/quality_filter.md`
- `knowledge/rag/promotion_rule.md`
- `docs/contracts/rag_data_contract.md`
- Skill: `rag-update`, `security-review`

### 보안 / 비용

- `docs/contracts/llm_security_contract.md`
- `docs/contracts/rate_limit_policy.md`
- `eval/security_reviews/`
- `eval/cost_snapshots/`
- `meta/security_metrics.md`
- Skill: `security-review`, `cost-review`

### Phase 시작 / 종료

- `PROJECT_STATE.md`
- `PHASE_REGISTRY.md`
- `phases/active/{current-phase}/`
- Skill: `phase-start`, `phase-complete`

### 평가 실행 / 회귀

- `eval/golden_set.md`
- `eval/regression_results/`
- `eval/qa_reports/`
- Skill: `eval-run`, `qa-check`, `prompt-version-review`

### 버그 분류 / 수정

- `docs/bug_reports/`
- `meta/error_taxonomy.md`
- Skill: `bug-triage`

## 금지 행동

- Phase 범위 밖 기능 추가
- contracts 직접 수정 (→ docs/contract_changes/에 제안서 작성)
- archive 무단 참조
- 영상 제작 기능 MVP 추가
- API 응답 스키마 임의 변경
- 사용자 데이터를 바로 global RAG에 넣기 (rag-update 5단계 승격 절차 필수)
- skip hooks (--no-verify) — 사용자 명시 허가 없이는 금지
