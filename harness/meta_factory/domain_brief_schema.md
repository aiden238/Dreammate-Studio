# domain_brief_schema.md — 도메인 입력 schema

> 위치: `harness/meta_factory/domain_brief_schema.md`
> 상태: Phase M0 Slice 1 — L3 Meta-Factory 의 **생성 입력** 구조
> 결정: ADR-035
> 참조: harness_blueprint_schema.md (생성 출력), factory_contract.md (8 규칙), generation_workflow.md (11단계, Slice 2)

---

## 0. 이 문서의 위치

domain_brief 는 새 하네스를 만들 때 사람이 작성하는 **입력 명세**다. "어떤 도메인의, 누구를 위한, 무엇을 만드는 하네스인가" 를 구조화한다. generation_workflow(Slice 2) 가 이 brief 를 입력으로 받아 harness_blueprint(출력)를 설계한다.

★ domain_brief 작성 = 사람의 일. meta_factory 는 brief 를 자동 생성하지 않는다 (proposal-first — 사람이 의도를 정의).

---

## 1. Schema 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `domain_name` | string | ✅ | 도메인 식별자 (snake_case, 예: `video_planning_ai`) |
| `domain_summary` | string | ✅ | 한 줄 정의 (이 하네스가 무엇을 하는가) |
| `target_users` | list[string] | ✅ | 대상 사용자 (예: 1인 크리에이터, 소규모 마케팅팀) |
| `primary_tasks` | list[string] | ✅ | 핵심 작업 (사용자가 이 하네스로 하는 일) |
| `output_artifacts` | list[string] | ✅ | 산출물 (예: 영상기획안, 카드, 리포트) |
| `runtime_type` | enum | ✅ | `docs_only` \| `product_saas` \| `internal_tool` \| `agent_workflow` |
| `risk_level` | enum | ✅ | `low` \| `medium` \| `high` (데이터/보안/비용 위험) |
| `required_contracts` | list[string] | ✅ | 필요한 contract (예: agent_io / output_schema / db_schema) |
| `required_evals` | list[string] | ✅ | 필요한 평가 (예: golden_set / regression / human_review) |
| `forbidden_scope` | list[string] | ✅ | 절대 금지 범위 (이 하네스가 하지 않는 것) |
| `preferred_architecture_patterns` | list[enum] | ✅ | architecture_patterns.md 6 패턴 중 선택 |

### 1.1 enum 정의

```
runtime_type:
  docs_only        # 문서/명세만 (런타임 코드 없음 — 예: Phase M0 자체)
  product_saas     # 제품 SaaS (FastAPI/Next/DB runtime — 예: Dreammate)
  internal_tool    # 내부 도구 (사내용, 제한 사용자)
  agent_workflow   # 에이전트 워크플로 (multi-agent orchestration 중심)

risk_level:
  low              # 데이터 노출/비용 위험 낮음, 사람 검토 선택
  medium           # 일부 PII/비용, 사람 검토 권장
  high             # 민감 데이터/높은 비용, 사람 검토 + security-review 필수

preferred_architecture_patterns: (architecture_patterns.md)
  pipeline | fan_out_fan_in | expert_pool | producer_reviewer | supervisor | hierarchical_delegation
```

---

## 2. YAML 예시 (Dreammate 역작성 샘플 — 참조용)

> 아래는 현재 Dreammate 하네스를 domain_brief 형식으로 역작성한 **참조 예시**다 (실 생성 입력 아님 — schema 사용법 시연).

```yaml
domain_name: video_planning_ai
domain_summary: "영상 제작이 아니라 영상기획을 돕는 AI 에이전트 (Discovery + Quick 하이브리드 UX)"
target_users:
  - 1인 크리에이터
  - 소규모 마케팅팀
primary_tasks:
  - 의도 분석 (Discovery 또는 Quick 자동 분기)
  - 영상기획안 3개 생성
  - Critic 검증 + revise (최대 2회)
  - 결과 저장 + 피드백
output_artifacts:
  - 영상기획안 (plan_candidates 3개)
  - Critic 평가 (canonical overall_score + dimensions)
  - 선택/피드백 기록
runtime_type: product_saas
risk_level: medium          # PII(사용자 입력/피드백) + LLM 비용
required_contracts:
  - agent_io_contract        # MOA 4 agent IO
  - output_schema            # Envelope/Plan/Critic
  - db_schema                # 4계층 + plans + feedback
  - llm_security             # PII 마스킹 + injection 차단
required_evals:
  - golden_set               # 11 케이스 회귀
  - regression_eval          # mock-deterministic
  - video_planning_eval      # 8차원 채점
  - human_review_rubric      # 사람 검토
forbidden_scope:
  - 영상 자동 편집           # MVP 영구 제외
  - 자동 promotion (사람 검토 없이)
  - Brand Memory 자동 추출 (Phase 10+)
preferred_architecture_patterns:
  - supervisor               # orchestrator 중개
  - fan_out_fan_in           # 3-plan parallel
  - producer_reviewer        # Planner → Critic → Rewriter
  - pipeline                 # Intent → RAG → Planning → Critic → Save
```

---

## 3. 작성 규칙

1. **forbidden_scope 는 필수** — "하지 않는 것" 을 명시해야 scope creep 을 차단한다 (non_goals 의 입력).
2. **risk_level: high → required_evals 에 human_review + security-review 강제** (factory_contract 규칙 8).
3. **runtime_type: docs_only → required_contracts/evals 최소** (런타임 contract 불필요).
4. **preferred_architecture_patterns 는 architecture_patterns.md 의 6 패턴에서만 선택** (임의 패턴 금지).
5. domain_brief 는 사람이 작성 (meta_factory 자동 생성 X) — proposal-first 정신.

---

## 4. 다음 단계

domain_brief 작성 → `generation_workflow.md` 11단계 (Slice 2) → `harness_blueprint_schema.md` 형식 blueprint 출력 → `validation_workflow.md` 6 검증 → outputs/generated_harnesses/ (active 아님, factory_contract 규칙 7).
