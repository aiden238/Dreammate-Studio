---
name: phase-start
description: |
  새 Phase를 시작하거나 재개할 때 사용한다. 어떤 문서를 어떤 순서로 읽고
  현재 phase의 scope, non-goals, 의존성을 확인하는 절차를 수행한다.
  트리거: "Phase X 시작", "다음 phase", "phase 진입", "phase initiation",
  "새 phase", "phase 시작해줘", "이번 phase는".
applies_to: [agents, claude]
phase: [all]
related_contracts:
  - docs/contracts/mvp_non_goals.md
related_state:
  - PROJECT_STATE.md
  - PHASE_REGISTRY.md
  - phases/active/
version: v1.0.0
---

# phase-start

새 Phase를 시작하거나 중단된 Phase를 재개할 때, 작업 컨텍스트를 완전하게 구성하기 위한 절차.

## 언제 트리거되는가

- 사용자가 "Phase 3 시작하자", "다음 phase로 넘어가자" 같이 명시적으로 요청
- 이전 Phase가 phase-complete를 통과하고 다음으로 넘어갈 때
- 중단된 Phase를 재개할 때 ("어디까지 했지?")
- 새 세션에서 작업 컨텍스트가 비어있을 때

## 절차

### 1. 상태 파일 확인

순서대로 읽는다:

1. `PROJECT_STATE.md` — 현재 프로젝트 전체 상태, 마지막 마일스톤
2. `PHASE_REGISTRY.md` — 모든 Phase 목록과 상태 (`pending` / `active` / `done` / `archived`)
3. 가장 최근 `active` 또는 다음 `pending` Phase를 식별

> active가 둘 이상이면 안 됨. 발견되면 즉시 사용자에게 알리고 정리 요청.

### 2. Phase 폴더 확인

`phases/active/{phase-name}/` 안에서 다음 파일을 확인한다:

```
goals.md             # 이 Phase의 목표 (필수)
scope.md             # 작업 범위 (필수)
non_goals.md         # 명시적 제외 항목 (필수)
dependencies.md      # 이전 Phase 의존성
acceptance.md        # 완료 기준
notes.md             # 진행 메모 (없으면 생성)
```

누락 파일이 있으면:
- `goals.md`, `scope.md`, `non_goals.md`가 없으면 **작업 중단**, 사용자에게 작성 요청.
- 나머지는 진행 중 작성 가능.

### 3. 관련 Contract 로드

Phase 종류에 따라 다음 contract 우선 로드:

| Phase 종류 | 필수 로드 contracts |
|---|---|
| 프론트 작업 | `apps/web/design.md`, `output_schema.md` |
| 백엔드 API | `api_contract.md`, `db_schema.md` |
| AI 파이프라인 | `agent_io_contract.md`, `output_schema.md`, `prompt_registry.md` |
| RAG 관련 | `privacy_contract.md`, `llm_security_contract.md` + rag-update Skill |
| 보안/인프라 | `llm_security_contract.md`, `rate_limit_policy.md` |
| 평가/품질 | `eval/golden_set.md`, `eval/human_review_rubric.md` |

전체를 다 로드하지 않는다. **현재 Phase에 직접 관련된 것만.**

### 4. 의존성 확인

`dependencies.md`에 명시된 이전 Phase가 모두 `done` 상태인지 확인.
하나라도 미완이면:
- 사용자에게 알림
- 강제 진행할지, 의존 Phase 먼저 마칠지 선택지 제시

### 5. Scope / Non-Goals 명시화

세션 시작 시 다음을 한 번 요약해 사용자에게 보여준다:

```
Phase: {phase-name}
목표: {goals.md 요약 1–2줄}
포함: {scope.md 요약}
제외: {non_goals.md 항목들}
완료 기준: {acceptance.md 요약}
```

이 요약은 작업 도중 scope creep을 막는 기준이 된다.

### 6. 첫 작업 단위 선정

`goals.md`를 작업 단위로 분해해서 첫 단위를 제시:

- 1회 세션에서 완료 가능한 크기 (1–4시간 작업)
- 명확한 산출물이 있어야 함 (파일 / 함수 / 문서)
- acceptance.md의 한 줄 이상에 매핑돼야 함

### 7. PHASE_REGISTRY 갱신

이 Phase가 처음 활성화되는 경우:

```
phase-name: status pending → active
phase-name: started_at: {timestamp}
```

PROJECT_STATE.md의 `current_phase` 필드도 갱신.

## 출력 형식

phase-start 트리거 시 다음 블록을 사용자에게 제시:

```
[Phase 시작 요약]
Phase: 04-mvp-frontend-discovery
목표: Discovery Wizard 5단계 카드 흐름 구현
포함: 카드 컴포넌트, wizard 라우팅, choice_logs 저장
제외: Quick Mode (Phase 06), Project Memory UI (Phase 11)
의존: 03-mvp-auth ✅ done
완료 기준:
  - Discovery 7단계 완주 시나리오 통과
  - choice_logs 테이블에 모든 클릭 기록
  - 모바일 360px에서 한 손 조작 가능
첫 작업 제안: ChoiceOptionCard 컴포넌트 구현 (apps/web/components/discovery/)
```

## 금지 사항

- contracts를 직접 수정하지 않는다. 필요 시 contract-change Skill 트리거.
- Phase 폴더가 없는데 임의로 만들지 않는다. 사용자에게 phase 등록 요청.
- non-goals에 있는 항목을 "조금만"이라도 건드리지 않는다.
- 이전 Phase의 acceptance 미달 상태로 다음 Phase 진입을 시도하지 않는다.

## 종료 조건

phase-start의 종료는 다음 중 하나:
- 첫 작업 단위가 선정되고 사용자가 진행 동의 → 일반 작업 모드로 전환
- 의존성 미충족 또는 필수 파일 누락 → 작업 중단, 사용자 입력 대기

## 자주 발생하는 실수

1. **PROJECT_STATE 안 읽고 시작**: "어디까지 했지?" 질문에 추측으로 답함 → 반드시 PROJECT_STATE 먼저.
2. **contracts 전체 로드**: 컨텍스트 낭비. 현재 Phase 관련만.
3. **active phase 둘 이상 방치**: 즉시 정리.
4. **scope creep**: 사용자가 "이것도 같이"라고 할 때 non-goals 확인 없이 수락.
