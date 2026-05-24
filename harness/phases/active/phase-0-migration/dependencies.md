# Phase 0. Dependencies

## 이전 Phase 의존성

**없음.** Phase 0는 이 프로젝트의 첫 Phase다.

## 외부 자료 의존성

| 자료 | 위치 | 용도 | 상태 |
|---|---|---|---|
| GPT 하네스 155 파일 | harness/ (unzip 완료) | 골격 채택 대상 | ✅ Stage 0 완료 |
| 우리 deep 4 deliverable | _staging/ | 콘텐츠 이식 소스 | ✅ Stage 0 완료 |
| 우리 14 Skill | _staging/skills/ | Skill 이식 소스 | ✅ Stage 0 완료 |
| migration_procedure.md v1.2.0 | harness/ | 절차 명세 | ✅ Stage 0 완료, v1.2.0 갱신 완료 |
| handoff_to_claude_code_sprint_S0.md | harness/ | S0 진입 가이드 | ✅ Stage 0 완료 |

## 도구 의존성

- Git (≥ 2.40) — Sprint별 commit + rollback
- PowerShell 5.1+ (또는 PowerShell 7) — sanity 스크립트 실행
- Windows 11 환경 — 작업 환경

## 인간 결정 의존성

S0 시작 전 확인된 결정 (Stage 0에서 사용자 답변):

```
✅ HARNESS_ROOT = Dreammate_Studio/harness/
✅ git init 즉시 + README.md 작성
✅ 작업 분담: Claude(하네스/기획) + Codex/Copilot(코드)
✅ Skill 구조: .claude/skills/ 단일 + applies_to (v1.2.0)
```

## 후속 Phase 의존성

Phase 0 완료가 다음 Phase의 선행 조건:

```
Phase 1. MVP 기본 플로우
  ← Phase 0의 Sprint S5 완료 + harness-audit 통과
  ← apps/web/design.md, docs/contracts/output_schema.md, 
    ai_system/prompts/prompt_registry.md 모두 깊은 버전 완성
```

## 차단 요인 (현재)

```
없음. Sprint S0 진행 가능.
```

향후 차단 가능성 점검:
- Sprint S1: `_staging/design.md` 손상 → 교체 불가 (현재 OK)
- Sprint S2: GPT 신규 Skill 6개 재작성 시간 부담 (Codex 협업 가능)
- Sprint S3: contract 깊은 작성 시 사용자 결정 필요 사항 (open questions) → 차단 시 placeholder marker로 대체
