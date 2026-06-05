# architecture_patterns.md — 6 아키텍처 패턴 + Dreammate 매핑

> 위치: `harness/meta/factory/architecture_patterns.md`
> 상태: Phase M0 Slice 1 — agent/orchestration 구조 패턴 카탈로그
> 결정: ADR-035
> 참조: harness_blueprint_schema.md (architecture_pattern 필드), domain_brief_schema.md (preferred_architecture_patterns), backend/fastapi/orchestration/moa_orchestrator.py (Supervisor 실측, 읽기만)

---

## 0. 이 문서의 위치

새 하네스(또는 역정리 blueprint)의 `architecture_pattern` 필드는 아래 6 패턴에서 선택한다. 각 패턴은 정의 + 선택 기준 + 트레이드오프를 갖는다. 하나의 하네스가 여러 패턴을 조합할 수 있다 (주 패턴 + 보조 패턴). 임의 패턴은 금지 — 6 패턴 + 조합만 허용한다.

---

## 1. 6 패턴

### 패턴 1 — Pipeline (파이프라인)

- **정의**: 입력이 정해진 단계를 순차로 통과한다. 각 단계의 출력이 다음 단계의 입력. 단방향.
- **선택 기준**: 작업이 명확한 선형 순서를 가지고 단계 간 의존이 단방향일 때.
- **트레이드오프**: 단순/추적 용이. 단 한 단계가 막히면 전체 정지 (graceful skip 으로 완화).

### 패턴 2 — Fan-out / Fan-in (분배·취합)

- **정의**: 하나의 입력을 여러 worker 에 동시 분배(fan-out)하고 결과를 취합(fan-in)한다. 병렬.
- **선택 기준**: 독립적으로 병렬 처리 가능한 작업이 N개일 때 (지연 단축 / 다양성 확보).
- **트레이드오프**: 처리량/다양성 향상. 단 비용 N배 + 취합 로직 복잡 + 부분 실패 처리 필요.

### 패턴 3 — Expert Pool (전문가 풀)

- **정의**: 작업 유형에 따라 특화된 전문가 agent 중 적합한 것을 선택(라우팅)해 처리한다.
- **선택 기준**: 작업이 이질적 유형으로 나뉘고 각 유형에 특화 전문가가 효과적일 때.
- **트레이드오프**: 전문성 향상. 단 라우팅 결정 비용 + 전문가 수만큼 유지보수 부담.

### 패턴 4 — Producer-Reviewer (생성-검토)

- **정의**: producer 가 산출물을 만들고 reviewer 가 평가하여 revise 를 요청한다. 개선 루프(횟수 상한).
- **선택 기준**: 산출물 품질이 중요하고 자동 평가/개선 기준이 정의될 때.
- **트레이드오프**: 품질 향상. 단 revise 루프 비용 + 무한 루프 위험(상한 필수).

### 패턴 5 — Supervisor (감독자 중개)

- **정의**: supervisor(orchestrator)가 모든 단계를 중개한다. agent 간 직접 호출 금지 — 항상 supervisor 경유.
- **선택 기준**: agent 격리/추적/정책 일관 적용이 중요하고 단계가 여러 개일 때.
- **트레이드오프**: 격리/추적/정책 일관. 단 supervisor 가 단일 책임 집중점(god-function 위험 — service layer 분리로 완화).

### 패턴 6 — Hierarchical Delegation (계층 위임)

- **정의**: 상위 agent 가 작업을 하위 agent 에 위임하고, 하위가 다시 더 하위에 위임하는 트리 구조.
- **선택 기준**: 작업이 재귀적으로 분해되고 단계별 추상 수준이 다를 때 (복잡 작업 분할 정복).
- **트레이드오프**: 복잡 작업 분할 정복. 단 위임 깊이가 깊어지면 추적/비용/지연 급증.

---

## 2. 선택 기준 요약

| 패턴 | 핵심 질문 | 적합 | 부적합 |
|---|---|---|---|
| 1 Pipeline | 단계가 선형인가? | 명확한 순차 흐름 | 분기/병렬 많음 |
| 2 Fan-out/Fan-in | 병렬 가능 작업 N개인가? | 독립 병렬 + 다양성 | 강한 단계 의존 |
| 3 Expert Pool | 작업 유형이 이질적인가? | 특화 전문가 효과 | 단일 균질 작업 |
| 4 Producer-Reviewer | 품질 검토 루프 필요한가? | 품질 중요 + 평가 기준 정의 | 1회성/저위험 |
| 5 Supervisor | agent 격리/추적 중요한가? | 다단계 + 정책 일관 | 단일 단계 |
| 6 Hierarchical Delegation | 재귀 분해되는가? | 복잡 작업 분할 정복 | 단순/평면 작업 |

### 2.1 expert_pool vs 단일 agent 파라미터화 결정 기준 (★ G1, M1 근거)

> 포맷/유형별 처리가 필요할 때 **expert_pool(패턴 3)** 로 전문가 agent 를 나눌지, **단일 agent + 파라미터화**(하나의 agent 가 포맷을 파라미터로 받아 분기)할지의 결정 기준. M1 팟캐스트 dry-run 에서 암묵적이었던 판단을 명문화한다.

| 축 | expert_pool 채택 | 단일 agent 파라미터화 채택 |
|---|---|---|
| 유형별 특화도 | **高** (포맷마다 로직·프롬프트·평가가 크게 다름) | 低~中 (포맷 차이가 입력 변수 수준) |
| 포맷/유형 수 | **多** (전문가 분리가 라우팅 비용을 정당화) | 少 (분기 1~소수, 공통 로직이 우세) |
| 독립 진화 필요성 | **각 expert 독립 진화 필요** (포맷별로 따로 개선·평가) | 공통 로직 우세 → 한 곳에서 함께 진화 |
| 유지보수 우선순위 | 전문성 > 단순성 | **단순성 우선** (분기 파라미터로 충분) |

- **비용·유지보수 임계 1줄**: expert N개 = 프롬프트 N벌 + 평가 N벌 + 라우팅 결정 1벌 = **관리 비용 약 N배**. 특화 효용이 이 N배 비용을 넘지 못하면 단일 agent 파라미터화가 옳다.
- **근거 (M1)**: 팟캐스트 포맷(솔로/인터뷰/패널)은 특화도가 입력 변수 수준(공통 기획 로직 우세) + 포맷 수 소수 → expert_pool 대신 **planning agent 파라미터화**로 결론. 본 기준이 그 결정을 사후가 아닌 사전 판단으로 가능하게 한다.

---

## 3. Dreammate 매핑 (실측 — moa_orchestrator.py)

현재 Dreammate 하네스는 4 패턴을 **조합**한다 (`backend/fastapi/orchestration/moa_orchestrator.py::generate_plan` 실측).

```
Supervisor: moa_orchestrator.py (generate_plan 중개)
Fan-out/Fan-in: 3-plan parallel (asyncio.gather)
Producer-Reviewer: Planner → Critic → Rewriter (revise loop)
Pipeline: Intent → RAG → Planning → Critic → Save → Feedback
```

### 3.1 매핑 상세

| 패턴 | Dreammate 구현 | 실측 근거 |
|---|---|---|
| **Supervisor** (주) | `generate_plan` 이 Intent → RAG → Planning → Critic → DB save 단계를 **중개**. agent 간 직접 호출 0 — orchestrator 경유 | moa_policy §2 "agent 간 직접 호출 금지, 오케스트레이터가 항상 중개" + moa_orchestrator docstring |
| **Fan-out/Fan-in** | `run_planning_parallel_3` (3-plan 동시 생성) + plan별 Critic `asyncio.gather` (병렬 평가) → 결과 취합 후 best-plan 선택 | moa_orchestrator §3 (3-plan parallel) + §5 (`asyncio.gather(_critic_revise_for_plan...)`) |
| **Producer-Reviewer** | Planner(생성) → Critic(평가, overall_verdict) → verdict=revise 시 Rewriter(개선) → 재평가. 최대 `critic_max_revise`(기본 2) 회 차단 | moa_orchestrator §5 (`_critic_revise_for_plan` revise loop, max 2) |
| **Pipeline** | Intent → RAG → Planning → Critic → DB save → (Feedback). 단방향 + graceful skip (RAG/Critic/Rewriter/DB 실패 시 흡수) | moa_orchestrator §1~§7 (순차 step + graceful) |

### 3.2 조합 효과

- **Supervisor + Pipeline**: orchestrator 가 선형 파이프라인을 중개 → agent 격리 + 추적 + graceful 정책 일관 적용.
- **Fan-out/Fan-in (3-plan)**: 다양성(3개 후보 → 사용자 1개 선택) + multi-model 인터페이스.
- **Producer-Reviewer (revise)**: 품질 향상 (Critic canonical 평가 + Rewriter 개선, max 2 무한 루프 차단).

> Dreammate 는 Expert Pool / Hierarchical Delegation 을 사용하지 않는다 (4 agent 균질 파이프라인 — 재귀 위임/유형 라우팅 불필요).

---

## 4. 작성 규칙

1. blueprint 의 `architecture_pattern` 은 6 패턴(또는 조합)에서만 선택. 임의 패턴 금지.
2. **Supervisor 선택 시 agents[].forbidden_actions 에 "직접 호출 금지" 명시** (격리가 패턴의 핵심).
3. **Producer-Reviewer 선택 시 revise 횟수 상한 명시** (무한 루프 차단).
4. **Fan-out/Fan-in 선택 시 부분 실패 처리(graceful) + 비용 N배 명시**.
5. 여러 패턴 조합 가능 — 주 패턴 1 + 보조 패턴 list (Dreammate = supervisor 주 + fan_out_fan_in/producer_reviewer/pipeline 보조).
