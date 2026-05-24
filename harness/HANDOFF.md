# HANDOFF

## 목적

역할 전환 / 세션 교체 / 모델 교체 시 필요한 정보를 압축해서 전달한다.

본 템플릿은 `context-compact` Skill의 출력 형식이기도 하다.
실제 handoff 파일은 `meta/handoffs/{YYYY-MM-DD}-{slug}.md`에 누적.

## 역할 흐름

```text
Planner          (Claude — 기획 / 설계)
→ Architect      (Claude — 구조 결정)
→ Implementer    (Claude Code / Codex / Copilot — 코드 작성)
→ QA             (Codex / qa-check Skill — 검증)
→ Docs           (Claude Code — 문서 정합)
→ Meta           (Claude — 회고 / 패턴 분석)
```

## Handoff 기본 형식

```md
# Handoff Note

## 1. Current Phase
{Phase 번호, 이름, active 상태}

## 2. migration_progress (Phase 0 한정)
{current_sprint, current_sprint_step, last_completed_action, next_action}

## 3. Completed Work
{이 세션에서 완료한 작업 목록}

## 4. Remaining Work
{다음 세션이 이어서 할 작업}

## 5. Required References
{다음 세션이 반드시 읽어야 할 파일 — instruction_index/routes.yaml의 task_route 키 사용 가능}

## 6. Changed Files
{이 세션에서 수정한 파일 목록. git diff --name-only로 자동 생성 가능}

## 7. Test / Sanity Results
{sanity_end_{Sprint}.ps1 결과 또는 테스트 통과 여부}

## 8. Known Issues
{미해결 이슈, 의도적으로 방치한 항목, 알려진 한계}

## 9. Non-Goals
{이번 / 다음 세션이 건드리면 안 되는 항목}

## 10. Next Role Instructions
{다음 역할에게 명시적 지시. 어떤 Skill로 시작할지 등}
```

## multi-llm-validation 연동

큰 결정 / contract 변경 / major prompt bump 시 handoff에 다음 추가:

```md
## 11. Validation Status (multi-llm-validation 사용 시)
- 검토 모델: {Claude / GPT / Gemini 중 사용한 것}
- 검토 일시: {YYYY-MM-DD}
- 합의 사항: {목록}
- 불일치 사항: {목록 — 사용자 결정 필요 항목}
- 검토 파일: meta/validations/{file}
```

## context-compact 연동

세션이 길어지거나 모델 교체 시:

```
1. context-compact Skill 트리거 (모든 Skill 위 최우선)
2. Skill이 현재 상태 스냅샷 → meta/handoffs/에 저장
3. 다음 세션은 PROJECT_STATE + 최신 handoff 읽고 시작
```

## 금지

- archive 내용을 기본 포함하지 않는다.
- 불확실한 내용을 확정처럼 쓰지 않는다.
- contracts 변경을 완료된 것처럼 쓰지 않는다 (`docs/contract_changes/`에 제안서 상태로 명시).
- Phase 범위 밖 작업을 다음 역할에 넘기지 않는다.
- 큰 결정을 단일 모델 단독으로 처리하지 않는다 (multi-llm-validation 트리거 검토).
