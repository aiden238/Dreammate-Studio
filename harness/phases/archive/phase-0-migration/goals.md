# Phase 0. 하네스 초기화 (Migration) — Goals

## Goal

GPT가 생성한 155-파일 하네스(골격 우수, 콘텐츠 빈약)와 자체 작성된 깊은 콘텐츠 18-파일을 병합하여
운영 가능한 영상기획 AI 에이전트 하네스를 완성한다.

## 세부 목표

1. **골격 채택**: GPT의 폴더 구조 + 라우팅 시스템(00_START_HERE / CLAUDE.md / AGENTS.md / instruction_index)
2. **콘텐츠 이식**: 우리 깊은 deliverables (design.md 688줄, db_schema.md 580줄, prompt_registry.md 628줄, agent_html_spec.md 789줄, Skills 14개)
3. **Skill 통합**: 25개(GPT) + 14개(우리) → 20개로 통합, 모두 `.claude/skills/`에 배치 (v1.2.0 결정)
4. **placeholder 일관성**: 9줄 stub 16개를 표준 marker 형식으로 일괄 변환 또는 깊게 보강
5. **검증 자동화**: Sprint별 sanity 스크립트 + harness-audit Skill 최종 실행
6. **재진입 안전망**: PROJECT_STATE.migration_progress 필드로 부분 완료 감지

## 성공 정의

- 165~170 파일, 약 10,000~12,000 줄
- Skill 총 20개 (`.claude/skills/` 단일)
- 9줄 stub 0개 (모두 보강 또는 placeholder marker)
- harness-audit Skill 결과: 0 critical, 0 high
- 모든 Skill의 related_contracts가 실재
- git log에 Sprint S0~S5 6개 commit 존재

## 예상 소요

- 세션 수: 6~9
- Claude Code: 4~5 (구조 / 콘텐츠 정합성)
- Codex: 3~4 (일괄 placeholder 변환, frontmatter 통일)
- Copilot Code: 1~2 (검토 / 교차검증)
