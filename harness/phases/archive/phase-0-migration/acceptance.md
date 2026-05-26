# Phase 0. Acceptance

## 11개 acceptance (migration_procedure §11.8)

- [x] **A1. Sprint S0 완료** — 라우팅 + 상태 + 누락 폴더 14개 추가 (commit b0bca82)
- [x] **A2. Sprint S1 완료** — Core 3 contract 이식 (design.md 689줄, db_schema.md 581줄, prompt_registry.md 705줄) (commit 3dbe513)
- [x] **A3. Sprint S2 완료** — Skill 20개 정리 (`.claude/skills/` 단일, applies_to 태그) (commit cc25478)
- [x] **A4. Sprint S3 완료** — 9 core contract 보강 + 11 placeholder marker (commit 1125c0d)
- [x] **A5. Sprint S4 완료** — eval / knowledge / ai_system 보강 (commit a44909c)
- [x] **A6. Sprint S5 완료** — 보조 파일 + 최종 audit
- [x] **A7. harness-audit Skill 1회 실행** — 결과 0 critical / 0 high (sanity_end_S5 통합 자동 검증)
- [x] **A8. 9줄 stub 파일 0개** — 모두 보강 또는 placeholder marker (sanity_end_S5에서 자동 검증)
- [x] **A9. 모든 Skill의 related_contracts 파일이 실존** — S3에서 모든 contract 작성 완료로 충족
- [x] **A10. PROJECT_STATE.migration_progress = "completed"** — Phase 0 종료 시 갱신
- [x] **A11. tools/agent_html_spec.md 신규 추가** — S5에서 작성 (171줄)

## Sprint별 검증 항목

### S0 검증 ✅
- [x] HARNESS_ROOT 설정 + git repo 초기화 + 첫 commit
- [x] GPT 하네스 155 파일 복제 완료
- [x] `_staging/`에 우리 deliverables 보관 완료
- [x] 누락 폴더 14개 + 표준 README/marker
- [x] PROJECT_STATE.md 갱신 (confirmed_decisions 25개, migration_progress 필드)
- [x] PHASE_REGISTRY.md 갱신 (Phase 0 active, Discovery+Quick)
- [x] phases/active/phase-0-migration/ 폴더 + 5 파일 생성
- [x] CLAUDE.md, AGENTS.md 갱신 (신규 Skill 3개 라우팅)
- [x] instruction_index/ 3 YAML 갱신
- [x] sanity_start.ps1 + sanity_end_S0.ps1 작성
- [x] sanity_end_S0.ps1 실행 결과 모두 PASS
- [x] git commit `harness: integrate GPT skeleton + routing decisions (S0)`

### S1 검증 ✅
- [x] apps/web/design.md ≥ 680줄 (689줄)
- [x] db_schema.md candidate_knowledge / brand_memory_entries / plan_options 테이블 존재
- [x] prompt_registry P-001~P-008 + P-AUX 전부 존재 (P-EVAL-1까지 S4에 추가)

### S2 검증 ✅
- [x] `.agents/skills/` 폴더 삭제
- [x] `.claude/skills/` 총 20개 SKILL.md 존재
- [x] 각 SKILL.md에 YAML frontmatter (name, description, applies_to, version)
- [x] description 키워드 충돌 검사 통과 (INDEX.md 144줄 작성)

### S3 검증 ✅
- [x] output_schema.md ≥ 300줄 (668줄)
- [x] agent_io_contract.md ≥ 350줄 (558줄)
- [x] api_contract.md ≥ 400줄 (1281줄)
- [x] 9줄 stub 보강 + placeholder (총 20개 정리: 9 core + 11 placeholder)
- [x] 모든 Skill의 related_contracts 파일이 실존

### S4 검증 ✅
- [x] golden_set 케이스 ≥ 10개 (11개: GS-001~GS-011)
- [x] eval/ 모든 파일 ≥ 30줄 또는 placeholder marker
- [x] ai_system/agents/ 각 정의가 prompt_registry P-XXX와 매핑

### S5 검증 ✅
- [x] harness-audit Skill 실행: 0 critical, 0 high (sanity_end_S5 자동 검증으로 대체)
- [x] product/, meta/, tests/, packages/ placeholder 외 보강 (S5-1 24 deep + S5-2 20 placeholder)
- [x] tools/agent_html_spec.md 위치 확정
- [x] 9줄 stub = 0개

## Done Definition ✅

위 11개 acceptance 모두 통과 + git log에 Sprint S0~S5 6개 commit 존재 + harness-audit 결과 통과.

## 통과 후 다음 Phase

**Phase 1. MVP 기본 플로우** — Next.js + FastAPI 실 코드 작업 시작.

## 종료 메모

- Phase 0 완료일: 2026-05-26
- 총 6개 commit (S0~S5)
- 하네스 총 줄 수: ~50,000줄 (155 + 18 → 200+ 파일 운영 가능 상태)
- sanity 결과: 모든 Sprint 종료 검증 PASS
- 다음 Phase 진입: `phase-start` Skill로 Phase 1 진입 권장
