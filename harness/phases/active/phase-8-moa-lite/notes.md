# Phase 8 — Notes

## Entry (2026-05-29)

- phase-start v1.3.0 §6 4점검 PASS (C1~C11, U1~U6)
- audit_naming PASS 0 drift
- Phase 7 baseline 완전 유지 (pytest 223 + smoke 13 + scenario_sim v3 15 + P-X1 31연속)
- 5 Slice 모두 sub-agent dispatch

### 사용자 결정 (2026-05-29)
- **Scope: 3개 모두** (A orchestrator + B SSE + C prompt_registry, 5 Slice, 12~16h)
- **Critic drift: Conservative adapter** — Phase 6 canonical(0–1) 불변, P-007 prompt(0–5) + 정규화 adapter 문서화 + v1.0.0→v1.1.0
- SSE 통합 기본값: in-memory progress_store 브릿지 (graceful, background task 미도입 — moa_policy §4 sync, async Phase 11+)

### Gap 분석 (entry 시점)
- Gap 1: orchestration이 plans_generate() 400줄 god-function에 인라인 (moa_policy §2 "orchestrator 중개" 위반)
- Gap 2: sse.py mock 4단계 + asyncio.sleep(0) — 실 generate와 decoupled
- Gap 3: prompt_registry P-007(0–5, 8 named dims) ↔ Phase 6 canonical(0–1 overall_score + dimensions) drift

### 핵심 원칙: Behavior-Preserving (★)
- orchestrator 추출은 동작 보존 리팩터 — Envelope byte-identical
- 기존 pytest 223 수정 0 PASS = 동작 불변 증거 (test 수정 필요 = 재작업)

### Skill 첫 정식 트리거 (2개)
- ai-architecture-review (Slice 1 — MOA orchestration 설계)
- prompt-version-review (Slice 1 분석 + Slice 4 적용 — P-007 semver)

## Slice 1~5 (작업 시 갱신)

### Slice 1 — Pre-Entry ✅ 완료 (2026-05-29, sub-agent)

- **validations**:
  - `meta/validations/2026-05-29_phase-8-pre-entry_self.md` — V1~V7 **7/7 PASS** (formal 다섯 번째 트리거)
    - V1 orchestrator 추출 behavior-preserving / V2 ProgressSink Null default / V3 SSE progress_store 브릿지 / V4 Critic conservative adapter / V5 prompt_registry semver 범위 / V6 단일 출처 정합 / V7 SSE best-effort
  - `meta/validations/2026-05-29_phase-8-pre-entry_external.md` — placeholder (외부 GPT/Gemini 진행 권장)
- **ai-architecture-review Skill ★ 첫 정식 트리거** — MOA orchestration 설계 검토 (4 agent 분리 + orchestrator 중개 moa_policy §2 정합 + cost/fallback policy 보존 + agent 격리 §7) → ADR-027 §ai-architecture-review 결과 통합. unused → active.
- **prompt-version-review Skill ★ 첫 정식 트리거 (분석 단계)** — P-007 Critic 0–5↔0–1 drift 분석 + conservative adapter + semver(v1.0.0→v1.1.0 minor) 계획 → ADR-029 통합. Slice 4 적용 예정. unused → active.
- **ADR 3건 신규**: ADR-027 (MOA orchestrator behavior-preserving + ProgressSink) + ADR-028 (SSE progress_store 브릿지, background task 미도입) + ADR-029 (prompt_registry semver, Critic conservative adapter — Phase 6 canonical 불변).
- **skill_usage_log**: phase-start 9→10 + qa-check +1 + multi-llm-validation 5→6 + **ai-architecture-review 0→1** + **prompt-version-review 0→1**.
- **PROJECT_STATE**: phase_8_* 키 추가 + active phase 전환 (Phase 8 active) + total_commits 70→71.

### Gap 정정 (코드 정독 결과 — self-validation §V4)

- entry 가정 "run_critic 이미 canonical 산출" → 실측: `run_critic`은 **0–5 deprecated 형식만** 산출, canonical은 `CriticEvaluation`이 Optional로 수용. canonical 우선순위는 `select_best_plan_index`에서만 작동.
- 영향: conservative adapter **필요성 정당화 강화** — Slice 4에서 `run_critic`에 0–5→0–1 정규화 adapter **추가** (dimensions = scores/5.0, overall_score = overall_score_avg/5.0) + 기존 0–5 deprecated 필드 병행 유지 → 회귀 0. ADR-029 반영.

### 다음: Slice 2 sub-agent (MOA Orchestrator 추출 behavior-preserving + ProgressSink)
