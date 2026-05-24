# Phase 0. Acceptance

## 11개 acceptance (migration_procedure §11.8)

- [ ] **A1. Sprint S0 완료** — 라우팅 + 상태 + 누락 폴더 14개 추가
- [ ] **A2. Sprint S1 완료** — Core 3 contract 이식 (design.md 688줄, db_schema.md 580줄, prompt_registry.md 628줄)
- [ ] **A3. Sprint S2 완료** — Skill 20개 정리 (`.claude/skills/` 단일, applies_to 태그)
- [ ] **A4. Sprint S3 완료** — 핵심 8 contract 보강 + placeholder marker 8개
- [ ] **A5. Sprint S4 완료** — eval / knowledge / ai_system 보강
- [ ] **A6. Sprint S5 완료** — 보조 파일 + 최종 audit
- [ ] **A7. harness-audit Skill 1회 실행** — 결과 0 critical / 0 high
- [ ] **A8. 9줄 stub 파일 0개** — 모두 보강 또는 placeholder marker
- [ ] **A9. 모든 Skill의 related_contracts 파일이 실존**
- [ ] **A10. PROJECT_STATE.migration_progress = "completed"**
- [ ] **A11. tools/agent_html_spec.md 신규 추가** (v1.0 그대로, v1.2.0 Skill 결정으로 갱신 불필요)

## Sprint별 검증 항목

### S0 검증 (현재)
- [ ] HARNESS_ROOT 설정 + git repo 초기화 + 첫 commit ✅ (Stage 0에서 완료)
- [ ] GPT 하네스 155 파일 복제 완료 ✅
- [ ] `_staging/`에 우리 deliverables 보관 완료 ✅
- [ ] 누락 폴더 14개 + 표준 README/marker
- [ ] PROJECT_STATE.md 갱신 (confirmed_decisions 25개, migration_progress 필드)
- [ ] PHASE_REGISTRY.md 갱신 (Phase 0 active, Phase 1 pending, Phase 2-3 Discovery+Quick)
- [ ] phases/active/phase-0-migration/ 폴더 + 5 파일 생성
- [ ] CLAUDE.md, AGENTS.md 갱신 (신규 Skill 3개 라우팅)
- [ ] instruction_index/ 3 YAML 갱신
- [ ] sanity_start.ps1 + sanity_end_S0.ps1 작성
- [ ] sanity_end_S0.ps1 실행 결과 모두 PASS
- [ ] git commit `harness: integrate GPT skeleton + routing decisions (S0)`

### S1 검증 (다음 Sprint)
- [ ] apps/web/design.md ≥ 680줄
- [ ] db_schema.md candidate_knowledge / brand_memory_entries / plan_options 테이블 존재
- [ ] prompt_registry P-001~P-008 + P-AUX 전부 존재

### S2 검증
- [ ] `.agents/skills/` 폴더 삭제
- [ ] `.claude/skills/` 총 20개 SKILL.md 존재
- [ ] 각 SKILL.md에 YAML frontmatter (name, description, applies_to, version)
- [ ] description 키워드 충돌 검사 통과 (INDEX.md 작성)

### S3 검증
- [ ] output_schema.md ≥ 300줄
- [ ] agent_io_contract.md ≥ 350줄
- [ ] api_contract.md ≥ 400줄
- [ ] 9줄 stub 보강 8개 + placeholder 8개 (총 16개 정리)
- [ ] 모든 Skill의 related_contracts 파일이 실존

### S4 검증
- [ ] golden_set 케이스 ≥ 10개
- [ ] eval/ 모든 파일 ≥ 30줄 또는 placeholder marker
- [ ] ai_system/agents/ 각 정의가 prompt_registry P-XXX와 매핑

### S5 검증
- [ ] harness-audit Skill 실행: 0 critical, 0 high
- [ ] product/, meta/, tests/, packages/ placeholder 외 보강
- [ ] tools/agent_html_spec.md 위치 확정
- [ ] 9줄 stub = 0개

## Done Definition

위 11개 acceptance 모두 통과 + git log에 Sprint S0~S5 6개 commit 존재 + harness-audit 결과 통과.

## 통과 후 다음 Phase

**Phase 1. MVP 기본 플로우** — Next.js + FastAPI 실 코드 작업 시작.
