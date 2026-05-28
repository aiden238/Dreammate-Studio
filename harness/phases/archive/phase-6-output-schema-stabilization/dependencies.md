# Phase 6 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 0~3 | ✅ done | (기본 의존, 참조 제한) |
| Phase 4 | ✅ done | `/plans/{plan_id}/generate` endpoint + 3-plan + multi-model + Critic verdict 1차 |
| Phase 4.5 | ✅ done | `agents/rewriter.py`, `agents/critic.select_best_plan_index`, `Body.revise_history`, `Body.recommended_plan_index`, 4가지 fallback (`overall_score_avg`, `overall_score`, `scores`, `dimensions`/`eight_dim_scores`) |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 (Phase 6는 직접 수정)

| Contract | 의존 |
|---|---|
| `docs/contracts/output_schema.md` | **수정 대상** (canonical revise_history + recommended_plan_index 정식 등록) |
| `docs/contracts/agent_io_contract.md` | **수정 대상** (P-008 Rewriter schema 정식 등록) |
| `docs/contracts/api_contract.md` | 참조 (Optional 수정) |
| `docs/contracts/mvp_non_goals.md` | 참조만 |
| `docs/contracts/llm_security_contract.md` | 참조만 |

## Skill 의존성

| Skill | 호출 시점 | 필수/선택 |
|---|---|---|
| `phase-start` v1.3.0 | entry (지금) | 필수 |
| `contract-change` | **Slice 2** (output_schema + agent_io_contract 수정) | **필수** |
| `multi-llm-validation` | Slice 1 (formal self V1~V5) | 필수 (Phase 5 진입 전 baseline) |
| `qa-check` v1.2.0 | Slice 1~4 (entry + final) | 필수 |
| `harness-audit` (audit_naming + audit_page_component) | Slice 1 + 4 | 필수 |
| `design-review` | Slice 4 (impl §B) | 필수 |
| `agent-io-check` | **첫 정식 트리거** (Slice 2 contract 변경 후) | **필수** |
| `prompt-version-review` | (불호출) | Phase 7+ |
| `meta-retrospective` | Slice 4 | 필수 |
| `phase-complete` v1.2.0 | Slice 4 final (P-X2 두 번째 자동 게이트) | 필수 |

## 환경 / 외부

- **OpenAI API**: 변화 없음 (gpt-4o-mini / gpt-4o)
- **PowerShell 5.1**: schema_stress_test.ps1 + smoke_test_phase_6.ps1 호환
- **pytest**: 109/109 → 115~117/115~117 목표 (+5~7 schema stress)
- **next build**: 11 routes 유지
- **tsc**: 0 errors (types.ts CriticVerdict 추가 후에도)
