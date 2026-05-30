# Phase 9 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 5 | ✅ done | `db/client.py` get_supabase + `PlansRepo` graceful 패턴 (selection/feedback repo 모델) + 0001~0003 migration + RLS + Auth (auth_user_id) |
| Phase 6 | ✅ done | CriticEvaluation canonical (overall_score 0–1 + dimensions) — normalize wiring 정합 대상 |
| Phase 7 | ✅ done | `candidate_knowledge` 테이블 + source_kind (피드백 적재 경로) + 0004 migration |
| Phase 8 | ✅ done | **`orchestration/moa_orchestrator.py` (critic step — normalize wiring 위치)** + `normalize_to_canonical` helper (critic.py) + thin adapter plans.py |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 + 수정

| Contract | 사용 |
|---|---|
| `docs/contracts/db_schema.md` | **수정 대상** (Slice 2 contract-change) — §5 feedback_events / §4.3 selected_plans 실 plans 테이블 정합 + brand_memory prep |
| `docs/contracts/output_schema.md` | **참조만** — CriticEvaluation canonical 불변 (NG3) |
| `docs/contracts/agent_io_contract.md` | **참조만** — Phase 8 v1.2.0 Critic adapter |
| `docs/contracts/llm_security_contract.md` | **참조** — 피드백 reason text PII (security-review §M2) |
| `ai_system/prompts/prompt_registry.md` | **참조** — P-AUX-2 brand_memory_extractor (ADR-031 설계 근거) |

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `multi-llm-validation` | Slice 1 (formal self) | 필수 |
| **`security-review`** | **Slice 1 두 번째 정식** (피드백 PII + reject 사유) | **필수** |
| `contract-change` | Slice 2 (db_schema.md feedback/selection) | 필수 |
| `agent-io-check` | Slice 3 (normalize wiring 후 critic 정합) + Slice 6 | 필수 |
| `qa-check` v1.2.0 | Slice 1 + 6 | 필수 |
| `harness-audit` | Slice 1 + 6 | 필수 |
| `design-review` | Slice 5 (피드백 UI) + Slice 6 | 필수 |
| `meta-retrospective` | Slice 6 | 필수 |
| `phase-complete` v1.2.0 | Slice 6 (P-X2 일곱 번째 자동 게이트) | 필수 |

## 환경 / 외부

- Supabase / OpenAI — Phase 5~8 baseline (graceful)
- pytest: 249/249 → 275~290 (+26~40 신규: selection/feedback + canonical wiring + brand_memory prep + api)
- next build / tsc / lint: 피드백 UI wrapper 후 회귀 0 (11 routes 유지, page.tsx inline)
- **normalize wiring 검증**: critic_evaluation에 canonical 0–1 추가 — 의도된 delta assertion만 최소 갱신 (Phase 8 Slice 4 패턴), schemas/output.py 불변
