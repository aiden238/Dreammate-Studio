# ADR-029 — Phase 8 prompt_registry semver 정식화 (Critic Conservative Adapter)

> Date: 2026-05-29
> Status: Accepted
> Phase: 8 (MOA Lite 본격)
> Slice: 4 (구현) / Slice 1 (본 ADR 결정 + 분석)
> Related: ADR-018 (phase_6_critic_canonical — Phase 6 canonical, **불변** 정합 대상),
>          ADR-019 (phase_6_rewriter_contract — Rewriter v1.1.0 패턴 참조),
>          ADR-027 (phase_8_moa_orchestrator — orchestrator 중개)
> Skill: **prompt-version-review ★ 첫 정식 트리거** (본문 §prompt-version-review 결과)
> 사용자 결정 (2026-05-29): Critic drift = **Conservative adapter** (Phase 6 canonical 불변)

## Context

`ai_system/prompts/prompt_registry.md`의 P-007 (Critic Agent)과 Phase 6 canonical(ADR-018) 사이에 점수 표현 drift가 존재한다:

| 위치 | 점수 표현 |
|---|---|
| **prompt_registry P-007 v1.0.0** | `scores` = 8 named dims × **0–5 정수** (intent_fit / target_clarity / hook_strength / message_clarity / structure / feasibility / brand_consistency / differentiation) |
| **Phase 6 canonical (ADR-018, output_schema §9, CriticEvaluation)** | `overall_score` = float **[0.0~1.0]** + `dimensions` = dict[str, float] **(정규화 0~1)** |

**현 코드 실측** (`agents/critic.py` 정독):

- `run_critic`은 LLM에게 **0–5 정수 8 dims**를 요청(`SYSTEM_PROMPT`)하고 `norm_scores`(0–5 clamp) + `overall_score_avg`(0–5 평균) + `overall_verdict` 산출 → **deprecated 0–5 형식** 반환. canonical(`overall_score` 0–1, `dimensions`)을 **산출하지 않음**.
- `routers/plans.py`는 `CriticEvaluation(**first_verdict)` 호출 — `CriticEvaluation`은 ADR-018에서 canonical + deprecated 필드 **모두 Optional** 강등 → 0–5 형식도 수용 (회귀 0).
- `select_best_plan_index`만 canonical(`overall_score` → `dimensions`) 우선, deprecated(`overall_score_avg` → `scores`) fallback + `DeprecationWarning`.

> **Gap 정정** (self-validation §V4): notes.md/task는 "run_critic 이미 canonical 산출"이라 했으나, 실측 결과 run_critic은 **0–5 deprecated 형식만** 산출하고 canonical은 Optional로 수용될 뿐이다. 이는 conservative adapter의 **필요성을 정당화**한다 — 코드가 canonical을 산출하도록 정규화 adapter를 추가해야 함.

추가로 prompt_registry는 P-001~P-008 + AUX의 semver가 각 prompt에 `Version: v1.0.0` 표기만 있고, **단일 출처 정합 정책**(agent 파일 상수 ↔ registry)이 test로 강제되지 않는다.

## Decision

### 1. Critic conservative adapter (사용자 결정 — Phase 6 canonical 불변)

- **Phase 6 canonical 불변**: `CriticEvaluation`의 `overall_score` [0~1] + `dimensions` dict[str, float] (ADR-018) **변경 0**. output_schema.md §9 불변 (NG5).
- **P-007 prompt 0–5 유지**: LLM-facing prompt 텍스트(0–5 정수 8 dims)는 그대로 (LLM 평가 일관성 — 0–5가 LLM에게 직관적). prompt 텍스트 변경 0.
- **코드 0–1 정규화 adapter 추가** (Slice 4): `run_critic`에 0–5 → 0–1 정규화 adapter 명시 추가.

> **Slice 4 구현 정정**: 아래 코드 예시는 `run_critic` 본문 주입 형태이나, 실제 구현은
> 더 보수적인 **순수 helper `normalize_to_canonical`** (run_critic 미강제 주입 → 회귀 0)로
> 채택했다. 상세는 본 문서 하단 **§Amendment (Slice 4, 2026-05-29)** 참조.

```python
# Slice 4 — run_critic 내 정규화 adapter (기존 0–5 deprecated 필드 병행 유지)
dimensions = {k: norm_scores[k] / 5.0 for k in DIMENSIONS}   # 0–1 canonical
overall_score = overall_score_avg / 5.0                       # 0–1 canonical
result = {
    # Phase 6 canonical (ADR-018) — 신규 산출
    "overall_score": round(overall_score, 4),
    "dimensions": dimensions,
    # Phase 1~4.5 deprecated (병행 유지 — 회귀 0)
    "scores": norm_scores,                  # 0–5
    "overall_score_avg": avg,               # 0–5
    "overall_verdict": verdict,
    "blocking_issues": blocking_issues,
    ...
}
```

- **회귀 0**: deprecated 0–5 필드(`scores`, `overall_score_avg`) **병행 유지** → `CriticEvaluation` Optional 호환 + 기존 `test_critic` 동작 불변. canonical 필드는 **추가**(기존 필드 제거 0).
- **P-007 v1.0.0 → v1.1.0** (Slice 4 적용): prompt 텍스트 불변 + 내부 정규화 표현 개선 = **minor bump** (output schema 미변경 → major 아님). `critic.py::PROMPT_VERSION = "v1.1.0"` + registry P-007 v1.1.0 동시 갱신.

### 2. prompt_registry semver 정식화 (P-001~P-008 + AUX + P-EVAL-1)

- **범위**: P-001~P-008 (8 core) + P-AUX-1 (intent_filter) + P-AUX-2 (brand_memory_extractor) + P-EVAL-1 (candidate_knowledge_evaluator) = **11 prompt**. 각 `(id, version)` 쌍 정식 등록 + active/deprecated 표시 + deactivate_at 정책 baseline (P-EVAL-1 §semver 블록을 모범으로 일관 확장).
- **정식화 ≠ A/B 실행**: 본 Phase 8은 semver 부여 + 단일 출처 정합 + P-007 v1.1.0만. golden_set 회귀(prompt-version-review §4) + A/B 50:50 라우팅(§5 major)은 **Phase 9+/11+** (NG3 — A/B는 100세션 누적 후, NG7 — eval-run Phase 9+).
- **variant 정책**: P-005q (Quick Mode 변형) 등 sub-variant는 부모 prompt version 상속 (별도 version 미부여) — registry §추가 메모.

### 3. prompt_id/version 단일 출처 정합

- **registry = 단일 진실 출처 (SoT)**. 각 agent 파일 모듈 상수(`PROMPT_ID` / `PROMPT_VERSION`, planning은 `PARALLEL_3_PROMPT_ID/VERSION`)는 SoT 미러.
- `test_prompt_registry_consistency.py`(Slice 4 신규)가 agent 파일 상수 ↔ registry `(id, version)` 일치 검증 → drift 0 게이트. **명시적 매핑 dict**(`EXPECTED = {"P-007": "v1.1.0", "P-001": "v1.0.0", ...}`) 비교 권장 (registry.md 텍스트 파싱 fragile 회피).
- registry ↔ agent 상수 ↔ agent_io_contract 3중 정합 — Slice 4 agent-io-check Skill로 마무리.

## §prompt-version-review 결과 (★ 첫 정식 트리거 — 분석 단계)

`.claude/skills/prompt-version-review/SKILL.md` 절차(7단계) 적용. P-007 Critic drift 분석 + semver 계획 (Slice 1 분석 → Slice 4 적용).

### 1. contract-change 절차 우선 (SKILL.md §1)

prompt_registry.md는 contract → Slice 4에서 `contract-change` Skill로 변경 제안서 작성 (대상: `ai_system/prompts/prompt_registry.md` + `docs/contracts/agent_io_contract.md`, 영향: Prompt 체크 + Critic v1.1.0 adapter).

### 2. semver 부여 (SKILL.md §2)

| 변경 | 종류 | 판정 |
|---|---|---|
| P-007 0–5 prompt 텍스트 불변 + 내부 0–1 정규화 adapter 추가 (output schema 미변경) | **minor** (v1.0.0 → v1.1.0) | "출력 구조 유지하면서 내부 표현 개선" (SKILL.md §2 minor 정의 정합) |
| P-001~P-006, P-008, AUX, P-EVAL-1 정식 등록 (텍스트 불변) | **patch/유지** (v1.0.0) | 정식화만 — 텍스트 변경 0 |

P-007이 minor인 근거: output schema(`CriticEvaluation` canonical)는 ADR-018에서 이미 정의됨 — 본 변경은 prompt 텍스트가 아닌 **코드 정규화 표현 개선** + 기존 deprecated 필드 병행 유지 → 호환성 깨짐 0 → major 아님.

### 4. golden_set 회귀 평가 (SKILL.md §4) — Phase 9+ 이관

- P-007은 SKILL.md §4 기준 "최소 10케이스" 회귀 평가 필요하나, **golden_set 기반 회귀 + eval-run Skill 정식화는 Phase 9+** (NG7). 본 Phase 8은 **정합 test(`test_prompt_registry_consistency`)만**.
- 회귀 안전 근거: 0–5 deprecated 필드 병행 유지 → 기존 `test_critic` 동작 불변 (회귀 0). 정규화 adapter는 canonical 필드 **추가**일 뿐 기존 산출 변경 0.
- **비교 지표** (SKILL.md §4 — Phase 9+ 적용 예정): schema 준수율 100% / Critic 평균 점수 ±0.3 / 다양성 / latency / 토큰 — golden_set eval-run 정식화 시.

### 5. 활성화 (SKILL.md §5) — minor 절차

minor bump이므로 SKILL.md §5 patch/minor 절차: registry v1.1.0 active 표시 + v1.0.0 deprecated note + prompt_registry_log baseline + agent_io_logs prompt_version 분기. A/B 단계적 활성화(§5 major)는 불필요 (minor).

### 6/7. 모니터링 / Rollback (SKILL.md §6/§7) — baseline

운영 모니터링(+24h schema 파싱 / +72h Critic 점수 / +7d feedback / +14d 비용)은 Phase 11+ cost-review/eval 동반 시 활성. rollback 경로(PROMPT_ACTIVE_VERSION 즉시 이전 + meta-retrospective)는 baseline 명시.

### 출력 요약

```
[prompt-version-review 결과 — P-007 Critic]
대상      : P-007 critic (v1.0.0 → v1.1.0)
변경 종류 : 내부 0–5 → 0–1 정규화 adapter 추가 (prompt 텍스트 불변, output schema 불변)
semver    : minor (출력 구조 유지 + 내부 표현 개선)
회귀 계획 : Phase 8 = 정합 test (test_prompt_registry_consistency) / golden_set 회귀 = Phase 9+ (NG7)
회귀 안전 : 0–5 deprecated 필드 병행 유지 → 기존 test_critic 불변 (회귀 0)
Phase 6 canonical : 불변 (ADR-018 — NG5 사용자 결정)
후속      : contract-change (Slice 4 — registry + agent_io_contract) + agent-io-check (3중 정합)
```

## Constraints

- **Phase 6 ADR-018 불변** — `CriticEvaluation` canonical(overall_score 0~1 + dimensions) + output_schema.md §9 변경 0 (NG5 사용자 결정).
- **회귀 0** — deprecated 0–5 필드(scores / overall_score_avg) 병행 유지 → `test_critic` 등 baseline test 수정 0 PASS (canonical 필드는 추가일 뿐).
- **A/B 실행 Phase 11+** — semver 정식화만, 50:50 라우팅은 100세션 누적 후 (NG3). golden_set 회귀 자동화는 Phase 9+ eval-run (NG7).
- **prompt 텍스트 불변** — P-007 0–5 prompt(LLM-facing) 변경 0. 정규화는 코드 레이어만.
- **단일 출처 정합** — registry SoT + agent 상수 미러 + consistency test (매핑 dict). registry ↔ agent ↔ contract 3중 정합.
- **multi-provider 미구현** — prompt semver는 정식화하되 provider 교체(gpt-4o-mini ↔ Claude 등)는 Phase 21+ (NG12, 단어 수준 금지 Anthropic/Claude API).
- **PlanCard.tsx 0줄 / component_map.md 0줄 ★** (backend-only phase).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| conservative adapter (Phase 6 canonical 불변) | 회귀 0 + Phase 6 ADR-018 안정성 보존 + 사용자 결정 | canonical 0–5 재정의 — ADR-018 변경 + frontend/DB 영향 (NG5) |
| P-007 prompt 0–5 유지 (LLM-facing) | LLM에게 0–5 직관적 + prompt 회귀 0 | prompt를 0–1로 변경 — LLM 평가 분포 변동 + golden_set 재평가 필요 |
| 코드 0–1 정규화 adapter (deprecated 병행) | canonical 산출 + 회귀 0 (deprecated 병행) | 0–5 필드 제거 — 회귀 위험 ↑ (Phase 9+ eval 후 제거 — ADR-018 §Migration) |
| P-007 minor (v1.1.0) | output schema 불변 + 내부 표현 개선 (SKILL.md §2) | major (v2.0.0) — 호환성 깨짐 아님 (과잉 bump) |
| 정합 test만 (golden_set Phase 9+) | 12~16h 무리 0 + 회귀 안전 (deprecated 병행) | golden_set 회귀 — eval-run 정식화 필요 (Phase 9+ — NG7) |
| 매핑 dict 비교 (consistency test) | registry.md 파싱 fragile 회피 + 명시적 | 텍스트 파싱 — 마크다운 포맷 변경 시 test 깨짐 |

## Verification

- `pytest backend/fastapi/tests/test_prompt_registry_consistency.py` (신규):
  - `test_agent_prompt_constants_match_registry` (각 agent 파일 PROMPT_ID/VERSION ↔ registry 매핑 dict)
  - `test_critic_prompt_version_v1_1_0` (critic.py PROMPT_VERSION == "v1.1.0")
  - `test_critic_adapter_0_5_to_0_1` (P-007 v1.1.0 adapter — 0–5 입력 → 0–1 dimensions + overall_score)
  - `test_deprecated_fields_preserved` (scores 0–5 + overall_score_avg 병행 유지 → 회귀 0)
- **agent-io-check Skill** (Slice 4) — agent_io_contract ↔ 구현 drift 0 (registry ↔ agent 상수 ↔ contract 3중 정합).
- **기존 `test_critic` 수정 0 PASS** ★ (canonical 추가 + deprecated 병행 → 회귀 0).
- **`git diff --cached --stat | grep -E "PlanCard|component_map|output_schema"` = 0 lines** ★ (Phase 6 canonical 불변 + backend-only).

## Amendment (Slice 4, 2026-05-29)

Slice 1 분석 시 ADR Decision §1 의 코드 예시는 `run_critic` 본문에서 canonical 필드를
직접 산출(주입)하는 형태로 기술했다. **Slice 4 구현에서는 더 보수적인 형태를 채택**한다
(사용자 결정 "Conservative adapter" + Slice 1 Gap 정정 정합):

- **adapter 는 code-side 순수 helper** — `agents/critic.py::normalize_to_canonical(verdict) -> dict`.
  0–5 → 0–1 정규화(`dimensions = scores/5.0`, `overall_score = overall_score_avg/5.0`)를
  **비파괴 사본**으로 산출한다. 이미 canonical(overall_score)이 있으면 보존한다.
- **`run_critic` 파이프라인 출력 의미 불변** — helper 는 additive 이며 `run_critic` 반환에
  **강제 주입하지 않는다**. 따라서 기존 0–5 deprecated 형식 산출이 그대로 유지되어
  **baseline test 회귀 0** (canonical 소비는 기존대로 `select_best_plan_index` 우선순위에서).
  → Decision §1 의 "run_critic 내 정규화 adapter" 예시보다 **회귀 면에서 더 안전**한 선택이며,
    canonical 정합(Phase 6 ADR-018)은 normalize_to_canonical helper + select_best_plan_index 로 충족.
- **version bump 의 test 영향은 정확히 2개 baseline assertion** (의도된 delta):
  - `tests/test_critic.py` — `PROMPT_VERSION == "v1.1.0"` (+ 주석)
  - `tests/test_e2e_slice1.py` — `critic_check["detail"] == "P-007@v1.1.0"` (+ 주석)
  detail 문자열은 `critic.PROMPT_VERSION` 에서 파생되므로 상수 bump 만으로 전파된다.
  이는 Phase 6 Rewriter 선례(P-008 v1.0.0 → v1.1.0 시 test_rewriter version assert 갱신)와 동일한
  "의도된 version bump 의 최소 반영"이며, Slice 2 behavior-preserving "test 수정 0"과 구분된다.
- **Phase 6 canonical schema 불변** — `CriticEvaluation`(overall_score 0–1 + dimensions) +
  `output_schema.md` §9 변경 0 (NG5). schemas/output.py 0줄.

## References

- `docs/decisions/phase_6_critic_canonical.md` (ADR-018 — Phase 6 canonical, **불변** 정합 대상)
- `docs/decisions/phase_6_rewriter_contract.md` (ADR-019 — Rewriter v1.0.0 → v1.1.0 패턴 참조)
- `ai_system/prompts/prompt_registry.md` (P-007 Critic 0–5 8 dims + §13 변경 관리 — Slice 4 갱신 대상)
- `docs/contracts/output_schema.md` §9 (CriticEvaluation canonical — 불변)
- `docs/contracts/agent_io_contract.md` (orchestrator 중개 + Critic v1.1.0 adapter — Slice 4 수정)
- `backend/fastapi/agents/critic.py` (`run_critic` 현 0–5 산출 + PROMPT_VERSION v1.0.0 → Slice 4 v1.1.0 + adapter)
- `backend/fastapi/schemas/output.py` (`CriticEvaluation` canonical + deprecated Optional)
- `meta/validations/2026-05-29_phase-8-pre-entry_self.md` §V4 (conservative adapter + gap 정정), §V5 (semver 범위), §V6 (단일 출처 정합)
- `.claude/skills/prompt-version-review/SKILL.md` (★ 첫 정식 트리거 — 7단계 절차)
- `phases/active/phase-8-moa-lite/{goals,scope,non_goals,acceptance,assumptions}.md` (NG3 A/B / NG5 canonical 재정의 / NG7 eval-run / NG12 multi-provider)
