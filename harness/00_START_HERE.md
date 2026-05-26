# START HERE

## 프로젝트 정의

이 프로젝트는 영상 제작 AI가 아니라 **영상기획 AI 에이전트 플랫폼**이다.

한 줄 정의:

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤, 검증 에이전트가 기획 품질을 평가·개선하는 영상기획 특화 AI 에이전트.

## 핵심 흐름

본 제품은 **Hybrid UX**: Discovery Wizard(신규/콜드스타트용 5단계 카드) + Quick Mode(같은 Series 추가 시). 두 모드는 같은 generate_plan 파이프라인으로 수렴.

```text
사용자 입력
→ 의도 분석 (Discovery 또는 Quick 자동 분기)
→ 부족한 정보 질문 (Discovery: 5 카드, Quick: 1–2 질문)
→ 한 줄 기획 방향 승인
→ LLM Wiki / RAG 검색
→ 영상기획안 3개 생성 (P-006 plan_candidates)
→ Critic Agent 검증 (revise 최대 2회)
→ 개선안 반영
→ 결과 저장
→ 사용자 선택·피드백 저장 (Brand Memory 자동 추출)
```

## 반드시 지킬 원칙

1. AGENTS.md와 CLAUDE.md는 지침 본문이 아니라 라우터로 사용한다.
2. PROJECT_STATE.md에는 최신 상태만 압축 기록한다.
3. phases/archive/는 기본 참조하지 않는다.
4. docs/contracts/는 무단 변경하지 않는다.
5. contract 변경은 docs/contract_changes/ 또는 meta/proposals/에 먼저 제안한다.
6. 구조는 처음부터 크게 만들고, 내용은 Phase 진행에 따라 얇게 채운다.
7. 영상 제작, 자동 편집, TTS/BGM, 자동 업로드는 MVP에 넣지 않는다.

## 첫 진입 시 읽을 문서

1. `PROJECT_STATE.md` (현재 active Phase, migration_progress 확인)
2. `PHASE_REGISTRY.md`
3. `product/mvp_scope.md`
4. `docs/contracts/mvp_non_goals.md`
5. `phases/active/{current-phase}/` 폴더 전체 (goals, scope, non_goals, acceptance, dependencies)
6. 현재 작업에 필요한 contracts

## 현재 active Phase

**Phase 1. MVP 기본 플로우** — Next.js + FastAPI 실 코드 작업 중.
- 진입: `phases/active/phase-1-mvp-basic-flow/`
- 핵심 contracts: `docs/contracts/api_contract.md`, `docs/contracts/agent_io_contract.md`, `docs/contracts/output_schema.md`
- Phase 0 archive: `phases/archive/phase-0-migration/` (기본 참조 금지)
