# Phase 4.5 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 0 | ✅ done (2026-05-26) | 하네스 골격 (참조 금지) |
| Phase 1 | ✅ done (2026-05-26) | `agents/intent.py`, `agents/planning.py` (run_planning 1-plan), `agents/rag.py`, `agents/critic.py` (verdict 구조) |
| Phase 2 | ✅ done (2026-05-27) | `apps/web/design_handoff.md`, `page_map.md`, `component_map.md` (수정 금지) |
| Phase 3 | ✅ done (2026-05-28) | `apps/web/app/plan/[plan_id]/page.tsx`, `components/plan/PlanCard.tsx`, `lib/api.ts`, `lib/types.ts` |
| Phase 4 | ✅ done (2026-05-28) | `agents/planning.run_planning_parallel_3`, `routers/plans.py` 4 endpoints, `_plan_store` dict, `schemas/output.compute_validation_warnings_phase4` |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 (read-only)

| Contract | 사용 위치 |
|---|---|
| `docs/contracts/agent_io_contract.md` | Rewriter input/output 구조 정합 |
| `docs/contracts/output_schema.md` | Body.revise_history + recommended_plan_index 신규 필드 정합 |
| `docs/contracts/mvp_non_goals.md` | NG1~NG10 정합성 확인 |
| `docs/contracts/llm_security_contract.md` | Rewriter 인라인 prompt PII 마스킹 / 인젝션 차단 |
| `eval/golden_set.md` | FC-001~005 케이스 (NG8 이관, 참조만) |

**Contract 변경은 본 phase에서 발생하지 않음** — agent_io_contract / output_schema는 *추가 필드*만 도입 (기존 필드 호환).

→ Body.revise_history + recommended_plan_index가 **신규 필드 추가**라면 contract-change Skill 호출 필요 여부 사전 점검.
→ 본 phase는 ADR-016 / ADR-017로 결정 사항 기록 + output_schema는 **Optional 필드 추가**이므로 contract-change 절차 불필요 판정 (Slice 1 self-validation에서 재확인).

## Skill 의존성

| Skill | 호출 시점 | 필수/선택 |
|---|---|---|
| `phase-start` v1.3.0 | entry (지금) | 필수 |
| `multi-llm-validation` | Slice 1 (M1 formal self) | **필수** (사용자 결정) |
| `qa-check` v1.2.0 | Slice 1~4 entry + final | 필수 (각 Slice 시작 + Slice 4 final) |
| `harness-audit` (audit_naming + audit_page_component) | Slice 1 entry + Slice 4 final | 필수 |
| `design-review` | Slice 4 (impl §B, PlanCard 무수정 정합 검증) | 필수 |
| `meta-retrospective` | Slice 4 | 필수 |
| `phase-complete` v1.2.0 (P-X2 도입 후) | Slice 4 final | 필수 — P-X2 첫 자동 게이트 트리거 |
| `contract-change` | (불필요 예상) | 조건부 (Optional 필드만 추가 시 skip) |
| `agent-io-check` | Slice 2 (Rewriter agent contract 도입) | **첫 사용 권장** — Phase 4.5 이후 정식 활성화 |

## 환경 / 외부

- **OpenAI API**: gpt-4o-mini (기본 Rewriter) + gpt-4o (Critic) — Phase 4와 동일
- **PowerShell 5.1**: 모든 scripts 호환 유지 (smoke_test_phase_4_5.ps1 + scenario_simulation.ps1)
- **pytest**: 93/93 baseline 유지 + 신규 7~10 케이스 추가 → 100~103/100~103 목표
- **next build**: 11 routes 유지 (page.tsx 수정만으로 추가 route 0)
