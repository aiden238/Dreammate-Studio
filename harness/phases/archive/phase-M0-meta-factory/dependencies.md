# Phase M0 — Dependencies

## 이전 Phase 의존성 (참조만 — blueprint 역정리용)

| Phase | 상태 | blueprint 역정리 대상 |
|---|---|---|
| Phase 0~9.5 | ✅ done | 전체 하네스 구조 (현재 하네스 blueprint 입력) |
| Phase 8 | ✅ done | MOA orchestrator (Supervisor 패턴 매핑) + prompt_registry semver |
| Phase 9 | ✅ done | feedback/selection + normalize wiring |
| Phase 9.5 | ✅ done | eval-run 정식화 (validation_workflow ↔ eval-run 연동 baseline) |

**모두 done** — 본 phase는 이들을 **참조만** (구조 변경 X, NG9).

## 참조 contract / 문서 (읽기 전용)

| 파일 | 용도 |
|---|---|
| `PROJECT_STATE.md` | 현재 phase 상태 (blueprint §8) |
| `AGENTS.md` / `CLAUDE.md` | 라우터 구조 (blueprint §5, harness_blueprint_schema routing_docs) |
| `PHASE_REGISTRY.md` | phase 구조 (blueprint §8) |
| `.claude/skills/INDEX.md` | Skill 체계 (blueprint §5 + harness-factory 충돌 검토) |
| `.claude/skills/eval-run/SKILL.md` | eval-run 구조 (validation_workflow §5 연동) |
| `meta/self_improvement_loop.md` | 기존 메타 루프 (L3 정합) |
| `docs/contracts/{agent_io,output_schema,api,db_schema}.md` | contract 구조 (blueprint §6, contract_template) |
| `eval/golden_set.md` | eval 구조 (blueprint §7 — 실측 11 케이스) |
| `backend/fastapi/orchestration/moa_orchestrator.py` | Supervisor 패턴 (architecture_patterns 매핑, 읽기만) |

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `multi-llm-validation` | Slice 1 (L3 도입 타당성) | 필수 |
| `contract-change` | Slice 3 (INDEX.md Skill 등록 — CC-006) | 필수 |
| `harness-audit` | Slice 3 (harness-factory 키워드 충돌 검토) + Slice 3 close | 필수 |
| `qa-check` v1.2.0 | Slice 1 + 3 | 필수 |
| `meta-retrospective` | Slice 3 | 필수 |
| `phase-complete` v1.2.0 | Slice 3 (P-X2 아홉 번째) | 필수 |
| `eval-run` | (참조) validation_workflow 연동 설계 — 실행 X | 참조 |
| `design-review` | (미호출) frontend 변경 0 | skip |
| `agent-io-check` | (미호출) agent 변경 0 | skip |

## 환경 / 외부
- 변경 없음 (문서 작업 — 런타임/DB/LLM 무관)
- pytest: 339 유지 (런타임 변경 0 → 회귀 0, 신규 test 없음 또는 meta_factory 구조 존재 검증 0~소수)
- **★ A9 게이트**: FastAPI/Next.js/Supabase 변경 0줄 (git diff로 검증)
