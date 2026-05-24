---
name: agent-io-check
description: |
  AI 파이프라인 구현/변경 시 agent_io_contract와 실 구현 사이의 정합성을
  검증한다. 새 agent 추가, 기존 agent 입출력 변경, output_schema.md 갱신
  직후 회귀 검사를 수행한다. contract와 구현 사이의 drift를 조기에 잡는다.
  키워드: "agent IO 점검", "I/O 검증", "agent_io_contract", "agent input output check",
  "agent 입출력 확인", "agent contract drift".
applies_to: [agents]
phase: [phase-6, phase-7, phase-8, ongoing]
related_contracts:
  - docs/contracts/agent_io_contract.md
  - docs/contracts/output_schema.md
related_state:
  - ai_system/agents/
  - ai_system/prompts/prompt_registry.md
version: v1.0.0
---

# agent-io-check

AI 파이프라인의 각 agent(Intent / Planner / Critic / Rewriter 등) 입출력이 `agent_io_contract.md`의 명세와 실제 구현·prompt에서 일치하는지 검증하기 위한 절차.

## 트리거 조건

- `ai_system/agents/*.md` 또는 그 구현체(Python/TS)가 변경됨
- 새 agent를 추가 (Intent/Planner/Critic/Rewriter 외)
- `docs/contracts/output_schema.md` 변경 후 영향 받는 agent를 식별해야 함
- `agent_io_contract.md` 변경 후 회귀 검사가 필요함
- `prompt_registry.md`의 P-XXX prompt가 P-001~P-008 범위에서 입출력 필드 추가/제거됨
- Phase 6/7/8 작업 중 "agent IO 점검" 류 요청이 발생

## 사용하지 않는 경우

```
- prompt 본문만 변경되고 입출력 스키마는 그대로 → prompt-version-review로 충분
- DB schema만 변경 → contract-change가 우선
- 평가 차원 변경 → eval-design 또는 eval-run
- 단순 버그 재현 → bug-triage가 먼저
```

## 절차

### 1. 컨트랙트 로드

다음 순서로 읽는다:

1. `docs/contracts/agent_io_contract.md` — 각 agent의 input/output 스키마, 필수/선택 필드
2. `docs/contracts/output_schema.md` — Planner 최종 출력 등 사용자 가시 schema
3. `ai_system/agents/{agent}.md` — agent별 책임 명세 (있다면)

`agent_io_contract.md`가 미정인 필드는 placeholder marker(`[STUB]`, `[PHASE-X]`)를 기준으로 분류한다.

### 2. 구현체 / Prompt 매핑

| Agent | 우선 비교 대상 |
|---|---|
| Intent | P-001, P-002 의 input/output JSON 예시 |
| Planner | P-005, P-006 (3 후보 생성) |
| Critic | P-007 (점수표·revise 트리거) |
| Rewriter | P-008 (revise 결과 schema) |
| 기타 보조 | P-AUX-* 영역 |

`prompt_registry.md`에서 해당 P-XXX의 input/output 섹션을 확보한다.

### 3. 차이 식별

다음 세 카테고리로 분류한다:

```
match     : contract와 구현이 일치
extra     : 구현에만 존재 (contract에 없는 필드)
missing   : contract에만 존재 (구현에 없는 필드)
type_diff : 같은 이름인데 타입/형식이 다름
```

`type_diff`는 가장 위험하다 — 런타임 오류를 유발.

### 4. 의사결정

발견된 차이별로 다음 중 하나를 선택:

- **contract가 진실** → 구현 수정 작업 항목으로 등록 (bug-triage 또는 다음 Phase 작업)
- **구현이 진실** → contract-change Skill 절차로 `agent_io_contract.md` 갱신 제안
- **양쪽 다 잘못** → contract-change로 새 안 작성 후 양쪽 모두 갱신

판단 근거를 보고서에 명시한다. 절대 임의로 한쪽을 바꾸지 않는다.

### 5. 보고서 작성

`docs/bug_reports/agent_io_check_{date}.md` 또는 `docs/contract_changes/proposals/agent_io_{date}.md`에 결과 정리. 발견된 항목이 0이면 `logs/checks/agent_io_{date}.log`에 PASS만 남긴다.

### 6. 후속 Skill 트리거

- contract 변경이 필요하면 → `contract-change`
- prompt 변경이 동반되면 → `prompt-version-review`
- golden_set 회귀가 필요하면 → `eval-run`

## 출력 형식

```
[agent-io-check 결과]
대상 agent : Planner (P-005, P-006)
contract   : agent_io_contract.md §3.2
구현/prompt: prompt_registry.md P-006

일치     : 7 필드
extra    : 1 필드  (구현: plan_options[].risk_score → contract 없음)
missing  : 0 필드
type_diff: 1 필드  (plan_options[].duration_sec: contract=int, prompt=string)

판단:
- risk_score: contract에 추가 (가치 있는 시그널) → contract-change
- duration_sec: contract가 진실(int) → prompt 수정 작업 등록

후속: contract-change Skill 트리거 (proposals/agent_io_2026-05-24.md 작성됨)
```

## 금지 사항

- contract를 직접 수정 (반드시 `contract-change` 절차)
- agent 구현 코드를 이 Skill에서 수정 (작업 항목 등록만)
- 차이 발견을 무시하고 PASS 처리
- `type_diff`를 "유사하니까 같다"로 임의 판단

## 자주 발생하는 실수

1. **prompt 본문만 비교**: prompt input/output 섹션과 contract를 직접 비교해야 함. 본문 문장만 보고 OK 처리하지 말 것.
2. **선택 필드 누락**: contract의 optional 필드를 구현이 안 만들면 OK처럼 보이나 downstream agent가 의존할 수 있음. 명시적 확인 필요.
3. **type_diff를 표면적으로 일치 처리**: 문자열 "30" vs int 30은 type_diff. 무시 금지.
4. **여러 agent 동시 점검**: 한 번에 한 agent만. 여러 개면 별도 보고서.

## 종료 조건

- 모든 발견 항목이 분류되고 후속 Skill 또는 작업 항목으로 라우팅됨
- 보고서가 `docs/bug_reports/` 또는 `docs/contract_changes/proposals/`에 저장됨
- 발견 0건일 때 `logs/checks/`에 PASS 로그 기록됨
