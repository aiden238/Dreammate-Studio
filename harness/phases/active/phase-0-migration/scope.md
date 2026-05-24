# Phase 0. Scope

## 포함 (Sprint S0~S5)

### Sprint S0: 라우팅 + 상태 (현재 진행 중)
- HARNESS_ROOT 확정 (Dreammate_Studio/harness/)
- GPT 하네스 unzip + 우리 deliverables `_staging/`에 보관
- 누락 폴더 14개 + 표준 README 추가
- PROJECT_STATE.md / PHASE_REGISTRY.md / 00_START_HERE.md / CLAUDE.md / AGENTS.md 갱신
- instruction_index/ 3 YAML 갱신 (routes / catalog / dependency_map)
- phases/active/phase-0-migration/ 5 파일 생성
- HANDOFF.md / 10_CLAUDE_CROSS_VALIDATION_PROMPT.md 갱신
- sanity_start.ps1 + sanity_end_S0.ps1 작성
- git commit `(S0)`

### Sprint S1: Core 3 교체
- `apps/web/design.md` GPT 163줄 → 우리 688줄 (Discovery+Quick Hybrid)
- `docs/contracts/db_schema.md` GPT 80줄 → 우리 580줄
- `ai_system/prompts/prompt_registry.md` GPT 8줄 → 우리 628줄
- `apps/web/page_map.md` / `component_map.md` design.md와 정합 갱신

### Sprint S2: Skill 25→20 정리
- `.agents/skills/` 폴더 삭제 (GPT 15개)
- `.claude/skills/`의 GPT 10개 중 폐기 4개 삭제 (docs-design, frontend-design-review, product-scope-review, planning-phase-create)
- 우리 14 Skill을 `.claude/skills/`에 배치 + `applies_to` 태그
- GPT 신규 6개 재작성 (agent-io-check, ai-architecture-review, eval-design, harness-audit, phase-review, rag-design)
- INDEX.md 갱신

### Sprint S3: 핵심 Contract 8개 보강 + placeholder 변환
- output_schema (300줄+), agent_io (350줄+), api (400줄+) 깊은 작성
- error_response, llm_security, rate_limit_policy, rag_data, frontend_design 보강
- 나머지 8개 stub은 placeholder marker로 일괄 변환

### Sprint S4: eval / knowledge / ai_system 보강
- eval/golden_set.md 시드 10케이스 작성
- ai_system/agents/ 6개 prompt_registry와 매핑
- ai_system/orchestration/ 5개 정책 보강
- knowledge/rag/ 8개 보강

### Sprint S5: 보조 파일 + 최종 audit
- product/ 7개 보강
- meta/ 9개 보강
- packages/ 3개 README 보강
- tests/ 3개 보강
- `tools/agent_html_spec.md` 신규 추가 (우리 789줄)
- harness-audit Skill 실행 → 0 critical / 0 high 확인

## 제외 (Non-Goals 참조)

자세한 제외 항목은 `non_goals.md` 참조.
