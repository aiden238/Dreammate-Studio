# agent_template.md — agent scaffold 템플릿

> 위치: `harness/meta_factory/templates/agent_template.md`
> 상태: Phase M0 Slice 2 — 생성 하네스의 agent 정의 scaffold
> 결정: ADR-035
> 정합: `docs/contracts/agent_io_contract.md` (agent 단위 입력/출력/실행 정책), harness_blueprint_schema.md §3.1 Agent
> ★ 본 파일은 placeholder + 작성 가이드. 실제 agent 코드(런타임)는 생성하지 않는다 (A9).

---

## 사용법

generation_workflow 단계 3(agent 후보 생성)에서 blueprint.agents[] 의 각 항목을 이 형식으로 작성한다. `{{...}}` placeholder 를 채우고, 작성 가이드(주석)를 따른다. agent_io_contract 형식과 정합해야 한다.

---

## Template (placeholder)

```yaml
# ── agent: {{agent_name}} ──────────────────────────────────────────
name: {{agent_name}}                 # snake_case 식별자 (예: intent, planning, critic)
responsibility: "{{한 줄 책임}}"      # 이 agent 가 무엇을 책임지는가 (1줄)
inputs:                              # 입력 (envelope 필드 / 이전 agent 출력)
  - {{input_1}}                      # 예: user_message, locale
  - {{input_2}}                      # 예: rag_context (이전 단계 출력)
outputs:                             # 출력 (output_schema 필드)
  - {{output_1}}                     # 예: intent_ok, reason
  - {{output_2}}                     # 예: plan_candidates
forbidden_actions:                   # ★ 필수 — 이 agent 가 하지 않는 것 (격리)
  - {{forbidden_1}}                  # 예: 다른 agent 직접 호출 (supervisor 패턴 시 필수)
  - {{forbidden_2}}                  # 예: RAG 직접 의존 / contract 직접 변경
prompt_ids:                          # 사용 prompt (prompt_registry 식별자)
  - {{P-XXX}}
execution_policy:
  timeout_ms: {{timeout}}            # 시간 초과 → silent fail 금지 (에러 응답 + 부분 결과)
  max_retries: {{n}}
  graceful_on_failure: {{true|false}}  # 실패 시 사용자 차단 0 (P-GRACEFUL-001 정신)
```

---

## 작성 가이드

1. **forbidden_actions 는 필수** (harness_blueprint_schema §3.1) — agent 격리가 architecture_pattern(특히 supervisor)의 핵심. supervisor 패턴이면 "agent 간 직접 호출 금지 — 오케스트레이터 경유" 명시.
2. **inputs/outputs 는 agent_io_contract 와 정합** — 입력 envelope + output_schema 본문 필드를 인용. 임의 필드 금지.
3. **idempotent 설계** — 같은 input → 같은 output (캐시 활용, agent_io_contract §1).
4. **graceful 실패** — 외부 의존(LLM/RAG/DB) 실패 시 차단 0 + validation.warnings 자기설명 (P-GRACEFUL-001 정신 계승).
5. **producer_reviewer 조합** — reviewer agent 는 revise 횟수 상한을 명시 (무한 루프 차단).
6. ★ **런타임 0** — 본 scaffold 는 agent 정의(설계)만. 실제 agent 구현 코드는 사용자 승인 후 별도 phase 에서 작성한다 (factory_contract 규칙 1).

---

## Dreammate 예시 (참조)

```yaml
name: critic
responsibility: "plan 평가 (canonical overall_score + dimensions)"
inputs: [plan_dict]
outputs: [overall_verdict, overall_score, dimensions]
forbidden_actions:
  - plan 직접 수정 (Rewriter 가 담당)
  - 다른 agent 직접 호출 (orchestrator 경유)
prompt_ids: [P-007]
execution_policy:
  timeout_ms: 30000
  max_retries: 2
  graceful_on_failure: true   # critic 실패 시 graceful skip → plan 생성 차단 X
```
