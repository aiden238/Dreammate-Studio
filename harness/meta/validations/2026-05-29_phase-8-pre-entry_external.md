# Phase 8 Pre-Entry Multi-LLM Validation — External

> 검증 모델: (예: GPT-4o, Gemini-1.5-Pro 등) — **사용자가 외부에서 진행 후 작성**
> 검증 일자: (기록 시 채울 것)
> 검증 유형: formal — self-validation과 짝 (다섯 번째 정식 트리거)
> 본 문서: **placeholder** (외부 검증 결과 추가 대기)
> Architecture refactor 영향: **HIGH** (god-function 추출 behavior-preserving + SSE 브릿지 + Critic adapter + prompt semver 첫 정식) → 외부 검토 **권장**
> Skill 의무 트리거: **ai-architecture-review (★ 첫 정식)** + **prompt-version-review (★ 첫 정식)** + multi-llm-validation (formal 다섯 번째)

## 작성 가이드

Phase 4.5/6/5/5.5/7 external placeholder 패턴 계승. 다음 항목을 외부 LLM (GPT/Gemini 등)에 다음 자료와 함께 제시한 후 결과를 기록.

### 외부 LLM에 제공할 자료

1. `harness/phases/active/phase-8-moa-lite/goals.md`
2. `harness/phases/active/phase-8-moa-lite/scope.md`
3. `harness/phases/active/phase-8-moa-lite/non_goals.md`
4. `harness/phases/active/phase-8-moa-lite/dependencies.md`
5. `harness/phases/active/phase-8-moa-lite/acceptance.md`
6. `harness/phases/active/phase-8-moa-lite/assumptions.md`
7. `harness/phases/active/phase-8-moa-lite/multi_slice_plan.md`
8. `harness/phases/active/phase-8-moa-lite/notes.md`
9. 본 self-validation 문서 (`2026-05-29_phase-8-pre-entry_self.md`)
10. `harness/docs/decisions/phase_8_moa_orchestrator.md` (ADR-027 — ai-architecture-review Skill 첫 정식 결과)
11. `harness/docs/decisions/phase_8_sse_progress_integration.md` (ADR-028 — SSE progress_store 브릿지)
12. `harness/docs/decisions/phase_8_prompt_registry_semver.md` (ADR-029 — prompt-version-review Skill 첫 정식 결과)
13. `harness/ai_system/orchestration/moa_policy.md` (§2 orchestrator 중개 + §4 동기/비동기)
14. `harness/ai_system/prompts/prompt_registry.md` (P-007 Critic 0–5 8 dims, 현 상태 — Slice 4 갱신 예정)
15. `harness/docs/contracts/output_schema.md` (Phase 6 CriticEvaluation canonical — 불변)
16. `harness/docs/decisions/phase_6_critic_canonical.md` (ADR-018 — 정합 대상, 불변)
17. `harness/backend/fastapi/routers/plans.py` (`plans_generate()` god-function — 추출 대상)
18. `harness/backend/fastapi/routers/sse.py` (mock 4단계 — 브릿지 대상)
19. `harness/backend/fastapi/agents/critic.py` (`run_critic` 현 0–5 산출 — adapter 대상)
20. (선택) `harness/.claude/skills/ai-architecture-review/SKILL.md` (7단계 절차)
21. (선택) `harness/.claude/skills/prompt-version-review/SKILL.md` (7단계 절차)
22. (선택) `harness/.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

### 외부 LLM에 묻을 질문 (V1~V7)

1. **V1 orchestrator 추출 behavior-preserving 원칙**:
   - 400줄 god-function을 service layer로 추출할 때 "기존 pytest 223 수정 0 + Envelope byte-identical"이 동작 불변의 충분 증거인가?
   - graceful 처리 / 에러 코드 / validation.checks 순서 100% 보존 가능한가? 누락 위험 지점은?
   - pure move(로직 개선 0) 원칙이 실제로 지켜질 수 있는가, scope creep 방지책은?
   - 다른 프로젝트의 god-function 추출 사례에서 흔한 회귀 패턴은?

2. **V2 ProgressSink 인터페이스 (Null default 회귀 0)**:
   - ProgressSink Protocol + NullProgressSink default 패턴이 회귀 0을 보장하는가?
   - emit 삽입 지점(stage 경계 5곳)이 stage 실 완료 시점과 정합한가?
   - Store/Null 분리(추출 Slice 2 / 통합 Slice 3)가 책임 분리로 적절한가?
   - `**meta` 자유 인자 vs 고정 schema — 어느 쪽이 안전?

3. **V3 SSE progress_store 브릿지 (graceful, background task 미도입)**:
   - in-memory progress_store 브릿지가 background task 없이 single-process에서 동작 가능한가?
   - graceful fallback(store empty → mock)이 기존 test_sse 보존에 충분한가?
   - clear on complete + maxlen이 메모리 누수 방지에 충분한가, TTL 필요?
   - background task(asyncio.create_task/Celery) 도입을 Phase 11+로 미루는 결정이 합리적인가?

4. **V4 Critic conservative adapter (Phase 6 canonical 불변)**:
   - Phase 6 canonical(0–1)을 변경하지 않고 P-007 prompt(0–5) 유지 + 코드 정규화 adapter가 적절한가?
   - run_critic이 현재 0–5 deprecated 형식을 산출하는 상황에서 0–5→0–1 adapter 추가(기존 0–5 병행 유지)가 회귀 0인가?
   - P-007 v1.0.0→v1.1.0이 minor bump로 올바른가 (output schema 미변경)?
   - canonical을 즉시 0–5로 되돌리는 대안 vs conservative adapter — 어느 쪽이 안전?

5. **V5 prompt_registry semver 정식화 범위**:
   - P-001~P-008 + AUX + P-EVAL-1 (11 prompt) semver 정식화가 12~16h에 무리 없는가?
   - golden_set 회귀 + A/B 실행을 Phase 9+/11+로 미루고 정합 test만 하는 것이 합리적인가?
   - P-005q 같은 variant의 version 정책(부모 상속)이 적절한가?
   - 다른 prompt 운영 시스템에서 semver 부여 시점·범위 권장?

6. **V6 prompt_id/version 단일 출처 정합**:
   - registry = SoT + agent 파일 상수 미러 + consistency test 패턴이 drift 0을 보장하는가?
   - registry.md 텍스트 파싱 vs 명시적 매핑 dict — 어느 쪽이 fragile하지 않은가?
   - registry ↔ agent 상수 ↔ agent_io_contract 3중 정합이 과도한가, 적정한가?

7. **V7 SSE 실시간 concurrency best-effort (single process)**:
   - 동기 blocking generate 중 GET /progress가 progress_store를 실시간 read하는 것이 best-effort로 충분한가?
   - multi-worker 환경에서 in-memory 미공유 → mock fallback이 UX에 허용 가능한가?
   - "실시간" UX 기대 vs best-effort 현실 gap을 어떻게 사용자에게 노출?
   - full async streaming을 Phase 11+로 미루는 결정이 합리적인가?

### 결과 기록 형식 (Phase 4.5/6/5/7 패턴 계승)

```
## V1. (외부 LLM 응답)
- 일치 / 차이 / 추가 risk:
- 권장 조치:

## V2. ...
## V3. ...
## V4. ...
## V5. ...
## V6. ...
## V7. ...

## 종합 판정 (외부 LLM)
- Phase 8 entry 허용 / 보류 / 차단:
- 차이 항목이 있을 때 Phase 8 notes.md 갱신 필요 여부:
- Slice 2 orchestrator 추출 behavior-preserving 영향 여부:
- Slice 3 SSE progress_store 브릿지 영향 여부:
- Slice 4 Critic adapter / prompt semver 영향 여부:
```

### Architecture-focused 추가 질문 (선택)

`docs/decisions/phase_8_moa_orchestrator.md` (ADR-027 — ai-architecture-review Skill 첫 정식) 본문에 대해 외부 LLM 견해:

- **A1 4 agent 분리**: Intent/Planning/Critic/Rewriter 분리 + orchestrator 중개(moa_policy §2)가 정합한가?
- **A2 cost/fallback policy 정합**: 추출 후 cost_control_policy / fallback_policy 준수 보존되는가?
- **A3 agent 격리**: moa_policy §7 컨텍스트 격리가 orchestrator 추출 시 유지되는가?
- **A4 helper 공유**: `_not_found_response` / `_error_envelope_response`를 orchestrator/router 공유 — 위치 권장?
- **A5 Envelope 조립 위치**: orchestrator가 Envelope 조립까지 책임 vs router 분담 — 권장?

---

**현재 상태**: placeholder — 사용자가 외부 GPT/Gemini 검증 후 결과 추가 예정.

Phase 8은 self-validation V1~V7 PASS + ai-architecture-review Skill 첫 정식 트리거 (ADR-027) + prompt-version-review Skill 첫 정식 트리거 (ADR-029) 결과로 entry 진행. 외부 검증 결과는 추후 추가되어도 본 phase 진행에 영향 X (단, 차이 항목 발견 시 notes.md 또는 Slice 5 회고에 반영).

**Architecture refactor 영향이 큰 phase**이므로 사용자 외부 진행 **권장**. 외부 검토 결과 Critical 차이 발견 시 Slice 2 진입 전 사용자 알림 + 차단 검토.

**의무 작성 시점**: Phase 8 Slice 1 entry (현 시점, placeholder). Phase 8 종료 시점에 본 placeholder가 채워지지 않으면 multi-llm-validation formal external 의무 위반 — 다음 phase entry 4-check에서 차단.

**self-strengthen 패턴 가능성**: Phase 5.5에서 Phase 4.5/6/5 external placeholder에 self-strengthen V-form (Claude Code 자가 검토 형식 — V1~V_n self-question + self-answer + 합의 추정)으로 강화한 사례가 있음. Phase 8 external도 사용자 외부 진행 전에 self-strengthen V-form 추가 가능 (단, 본 Slice 1에서는 외부 진행 자체 우선 권장).

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 5 external: `meta/validations/2026-05-29_phase-5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 7 self: `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS — 네 번째 formal)
- Phase 7 external: `meta/validations/2026-05-29_phase-7-pre-entry_external.md` (placeholder)
- Phase 8 self: `meta/validations/2026-05-29_phase-8-pre-entry_self.md` (V1~V7 PASS — 다섯 번째 formal)
- Phase 8 external: 본 문서 (placeholder)
