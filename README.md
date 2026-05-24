# Dreammate Studio — Video Planning AI Agent

> 사용자의 막연한 콘텐츠 아이디어를 버튼식 선택 UX와 프로젝트 메모리를 통해 반복 가능한 영상기획안으로 발전시키는 웹 기반 기획 워크스페이스.

## 현재 상태

**Stage**: Harness Migration — Stage 0 (Bootstrap 완료)
**Next**: Sprint S0 — 라우팅 + 상태 파일 갱신

GPT가 생성한 155-파일 하네스(골격 우수, 콘텐츠 빈약)와 자체 작성된 18-파일 deliverables(콘텐츠 깊지만 골격 부재)를 병합하는 과정 중이다.

자세한 절차는 [harness/migration_procedure.md](harness/migration_procedure.md) 참조.

## 폴더 구조

```
Dreammate_Studio/
├── README.md                  ← 이 파일
├── .gitignore
├── .claude/                   ← Claude Code 세션 설정
├── harness/                   ← 최종 하네스 (작업 대상)
│   ├── migration_procedure.md         ← 이식 절차 v1.0.0
│   ├── handoff_to_claude_code_sprint_S0.md  ← S0 진입 가이드
│   ├── 00_START_HERE.md / CLAUDE.md / AGENTS.md / ...
│   ├── .agents/skills/        ← 구현형 모델용 (현재 15개 → 11개 목표)
│   ├── .claude/skills/        ← 기획형 모델용 (현재 10개 → 9개 목표)
│   ├── ai_system/  apps/  backend/  docs/  eval/
│   ├── instruction_index/  knowledge/  logs/  meta/
│   ├── packages/  phases/  product/  tests/
│   └── (총 155 파일, 이식 완료 시 약 165~170 파일)
└── _staging/                  ← 이식 소스 (우리 deliverables)
    ├── design.md              (688줄, → harness/apps/web/design.md 교체용)
    ├── db_schema.md           (580줄, → harness/docs/contracts/db_schema.md)
    ├── prompt_registry.md     (628줄, → harness/ai_system/prompts/prompt_registry.md)
    ├── agent_html_spec.md     (789줄, → harness/tools/agent_html_spec.md)
    └── skills/                ← 우리 14 Skill (이식 후 폴더 분리 배치)
```

## 이식 진행 (5 Sprint)

| Sprint | 범위 | 상태 | Commit |
|---|---|---|---|
| S0 | 라우팅 + 상태 (START_HERE, PROJECT_STATE, CLAUDE.md, AGENTS.md, instruction_index) | 대기 | - |
| S1 | Core 3 교체 (design.md, db_schema.md, prompt_registry.md) | 대기 | - |
| S2 | Skill 25→20 정리 (폐기 8 / 우리 14 이식 / GPT 6 재작성) | 대기 | - |
| S3 | 핵심 Contract 8개 보강 (output_schema, agent_io, api 등) | 대기 | - |
| S4 | eval / knowledge / ai_system 보강 | 대기 | - |
| S5 | 보조 파일 + harness-audit 최종 검증 | 대기 | - |

각 Sprint는 git commit 단위로 분리하여 rollback 가능. 자세한 산출물 검증은 [migration_procedure.md §6](harness/migration_procedure.md) 참조.

## 작업 분담

| 영역 | 주력 | 보조 |
|---|---|---|
| 하네스 골격 / 기획 | Claude Code | GPT (교차검증) |
| 세부 지침 / Skill 작성 | Claude Code | Codex (Claude 할당량 소진 시 이전) |
| 코드 작성 (Phase 1 이후) | Codex | Copilot Code (Sonnet 4.6, Codex 소진 시) |
| 큰 결정 | Multi-LLM Validation Skill (3 모델 동시 검토) | - |

## 핵심 결정 사항

1. **하네스 위치**: `Dreammate_Studio/harness/` 하위 (멀티-프로젝트 워크스페이스 확장 대비)
2. **Skill 분리**: `.agents/.claude` 분리 유지 (description 매칭 명확성)
3. **MVP 흐름**: Discovery Wizard (7단계) + Quick Mode 하이브리드
4. **Mobile / Spring**: Phase 21+ 제외 (placeholder marker 처리)
5. **이식 후 Skill 총 개수**: 20개 (.agents 11 + .claude 9)

## 다음 단계

```
1. harness/handoff_to_claude_code_sprint_S0.md 읽기
2. Sprint S0 수행 — 라우팅 + 상태 파일 갱신
3. 검증 체크포인트 통과 → git commit "harness: integrate GPT skeleton + routing decisions (S0)"
4. Sprint S1 진입
```
