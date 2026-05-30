# Phase 8 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 1 | ✅ done | `agents/{intent,planning,critic,rewriter,rag}.py` baseline + prompt_registry 8 prompts |
| Phase 4 | ✅ done | `routers/plans.py` god-function (추출 대상) + 3-plan parallel |
| Phase 4.5 | ✅ done | Critic revise loop + Rewriter + best-plan |
| Phase 5 | ✅ done | **`routers/sse.py` mock 4단계** (실 worker 통합 대상) + Auth/RLS |
| Phase 6 | ✅ done | **Critic canonical (overall_score 0–1 + dimensions)** — adapter 정합 대상 (불변) + Rewriter v1.1.0 |
| Phase 7 | ✅ done | `agents/rag.py` RAG Lite 통합 + graceful 5종 marker |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 + 수정

| Contract | 사용 |
|---|---|
| `ai_system/orchestration/moa_policy.md` | **참조 + 선택 수정** — §2 orchestrator 중개 (실 구현 cross-ref) |
| `ai_system/prompts/prompt_registry.md` | **수정 대상** (Slice 4 — semver 정식화) |
| `docs/contracts/agent_io_contract.md` | **수정 대상** (Slice 4 — orchestrator + Critic v1.1.0) |
| `docs/contracts/output_schema.md` | **참조만** — Phase 6 canonical 불변 (NG5) |
| `docs/contracts/api_contract.md` | **참조만** — SSE endpoint 기존 |
| `ai_system/orchestration/{flow,fallback_policy,cost_control_policy}.md` | **참조만** |

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `multi-llm-validation` | Slice 1 (formal self V형식) | 필수 |
| **`ai-architecture-review`** | **Slice 1 ★ 첫 정식** (MOA orchestration 설계) | **필수** |
| **`prompt-version-review`** | **Slice 1 분석 + Slice 4 적용 ★ 첫 정식** (P-007 semver) | **필수** |
| `contract-change` | Slice 4 (agent_io_contract + prompt_registry) | 필수 |
| `agent-io-check` | Slice 2 + Slice 4 + Slice 5 (orchestrator + prompt 정합) | 필수 |
| `qa-check` v1.2.0 | Slice 1 + 5 | 필수 |
| `harness-audit` | Slice 1 + 5 | 필수 |
| `design-review` | Slice 5 (frontend 변경 0 회귀) | 필수 |
| `meta-retrospective` | Slice 5 | 필수 |
| `phase-complete` v1.2.0 | Slice 5 (P-X2 여섯 번째 자동 게이트) | 필수 |

## 환경 / 외부

- 변경 없음 (OpenAI gpt-4o-mini / gpt-4o, Supabase pgvector — Phase 7 baseline)
- pytest: 223/223 → 245~255/245~255 (+22~32 신규: orchestrator + sse_integration + prompt_consistency)
- next build / tsc / lint: 회귀 0 (frontend 변경 0)
- **behavior-preserving 검증**: 기존 test_plans / test_e2e_slice1 등 generate 관련 테스트가 orchestrator 추출 후에도 수정 없이 PASS (핵심 게이트)
