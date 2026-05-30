# Contract Change Log — Phase 8 Slice 4 prompt_registry semver + Critic v1.1.0 adapter

> ID: CC-003
> Status: **decided + applied** (2026-05-29, Phase 8 Slice 4)
> Date: 2026-05-29
> Decision: Conservative adapter (사용자 결정 — Phase 6 canonical 불변) — ADR-029 선행 승인 기반
> Author: Claude (Phase 8 Slice 4 sub-agent)
> Related contracts: `ai_system/prompts/prompt_registry.md`, `docs/contracts/agent_io_contract.md`
> Related ADR: ADR-029 (`docs/decisions/phase_8_prompt_registry_semver.md`) + §Amendment
> Proposal: `meta/proposals/2026-05-29_phase-8-slice-4-prompt-registry-semver.md`
> Skill: prompt-version-review (semver) + contract-change (절차) + agent-io-check (drift 검증)

---

## 1. 변경 요약

| 대상 | 변경 |
|---|---|
| `prompt_registry.md` | P-001~P-008 + P-AUX-1/2 + P-EVAL-1 각 항목에 `#### Semver / 활성 정책` 명시. P-007 v1.0.0 → v1.1.0 + §0–5↔0–1 adapter. P-008 v1.0.0 → v1.1.0 (registry 표기 정정, 코드는 이미 v1.1.0). §13 Semver 정식화 + §14 #2 갱신. |
| `agent_io_contract.md` | §5 Critic v1.1.0 adapter (code-side 0–5↔0–1, Phase 6 canonical 정합) + §8 orchestrator 중개(ADR-027) + §20 v1.2.0 entry. |
| `moa_policy.md` | §2 moa_orchestrator.py 실 구현 cross-reference. |
| ADR-029 | §Amendment (adapter = code-side normalize_to_canonical helper, run_critic 미강제 → 회귀 0). |

## 2. 코드 영향 (additive only)

```
backend/fastapi/agents/critic.py    — PROMPT_VERSION v1.0.0 → v1.1.0 + normalize_to_canonical helper 신규
backend/fastapi/tests/test_critic.py        — version assert 1줄 + 주석 (의도된 delta)
backend/fastapi/tests/test_e2e_slice1.py    — critic detail assert 1줄 + 주석 (의도된 delta)
backend/fastapi/tests/test_prompt_registry_consistency.py  — 신규 (단일 출처 정합 + adapter 검증)
```

## 3. 회귀 안전 근거

- LLM-facing P-007 prompt(0–5) 불변, Phase 6 canonical(`CriticEvaluation` 0–1, output_schema §9) 불변 (NG5).
- `normalize_to_canonical` 은 additive helper — `run_critic` 반환에 강제 주입 X → 출력 의미 불변.
- deprecated 0–5 필드(scores / overall_score_avg) 병행 유지 → backward-compat 100%.
- version bump 의 test 영향은 정확히 2개 baseline assertion (detail 문자열은 critic.PROMPT_VERSION 파생).

## 4. 검증 결과

```
pytest backend/fastapi/tests/: 238 → 244 PASS (test_prompt_registry_consistency +6).
test_critic / test_e2e_slice1: 2 version-string assertion(+주석) 갱신 외 변경 0.
schemas/output.py: 0줄. PlanCard.tsx / component_map.md: 0줄.
agent-io-check: agent_io_contract §5 ↔ critic.py (v1.1.0 + normalize_to_canonical) drift 0.
```

## 5. Rollback

- 문서 변경은 git revert. critic.py 상수 복원 + helper 제거 시 회귀 0 (additive).

## 6. 변경 이력

- 2026-05-29: 제안서 작성(meta/proposals) + ADR-029 §Amendment + contracts 반영 + 검증 (Slice 4).
