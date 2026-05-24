# AGENTS.md

## 역할

Codex, Copilot Code, 구현형 AI 에이전트용 라우터 문서다. 모든 지침 본문을 담지 않고, 작업 유형별 참조 문서를 안내한다.

## 기본 원칙

1. 현재 active Phase만 우선 참조한다.
2. archive는 기본 참조하지 않는다.
3. docs/contracts는 직접 수정하지 않는다.
4. 계약 변경은 `docs/contract_changes/` 또는 `meta/proposals/`에 제안한다.
5. MVP 범위 밖 기능을 임의로 구현하지 않는다.
6. 영상 제작/자동 편집/자동 업로드는 MVP에 넣지 않는다.

## 기본 참조 순서

```text
1. PROJECT_STATE.md
2. PHASE_REGISTRY.md
3. phases/active/{current_phase}.md
4. instruction_index/routes.yaml
5. 관련 docs/contracts/*
6. 관련 eval/*
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

### 백엔드 구현

- `docs/contracts/api_contract.md`
- `docs/contracts/db_schema.md`
- `docs/contracts/output_schema.md`
- `docs/contracts/error_response_contract.md`
- `backend/fastapi/README.md`

### AI 파이프라인 구현

- `ai_system/architecture.md`
- `ai_system/orchestration/flow.md`
- `docs/contracts/agent_io_contract.md`
- `docs/contracts/output_schema.md`
- `eval/video_planning_eval.md`

### RAG 구현

- `knowledge/rag/metadata_schema.md`
- `knowledge/rag/retrieval_policy.md`
- `knowledge/rag/quality_filter.md`
- `docs/contracts/rag_data_contract.md`

## 금지 행동

- Phase 범위 밖 기능 추가
- contracts 직접 수정
- archive 무단 참조
- 영상 제작 기능 MVP 추가
- API 응답 스키마 임의 변경
- 사용자 데이터를 바로 global RAG에 넣기
