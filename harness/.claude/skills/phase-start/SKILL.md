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
version: v1.1.0
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

### 6. Phase 진입 4점검 (v1.1.0 추가)

스코프가 확정된 직후, **작업 단위 선정 전에** 다음 4가지를 명시적으로 점검·기록한다.
결과는 `phases/active/{phase-name}/assumptions.md`에 작성한다.

#### 6.1 Assumptions (가정)

```
- 이번 Phase에서 확정한 가정은 무엇인가?
- 불확실한 부분은 무엇인가?
```

확정 가정 예시:
- 외부 의존성 (Supabase, OpenAI) 가용성
- 사용자가 제공한 결정 (모델 선택, 데이터 흐름)
- contract에 명시된 인터페이스

불확실 항목 예시:
- 실측 LLM 응답시간 (30–60초 가정이지만 미검증)
- pgvector 검색 정확도 (실데이터 없음)
- 사용자 입력 패턴 (가설만 있음)

**불확실 항목은 명시적으로 기록해야 phase-complete 시 회고 가능.**

#### 6.2 Simplest Slice (최소 작동 단위)

```
- 이 Phase에서 작동 확인 가능한 가장 작은 단위는 무엇인가?
- 이보다 더 줄일 수 있는가?
```

원칙:
- "더 줄일 수 있는가?" 질문을 **3회 반복**해야 한다
- 최종 답이 "더 못 줄임"일 때까지 압축
- UI 없이도 흐름 증명 가능하면 UI 미포함
- DB 저장 없이도 흐름 증명 가능하면 DB 미포함 (in-memory)

예시 (Phase 1):
- 1차 답: "입력 → 4 Agent → 저장"
- 2차 답: "입력 → Intent + Planning → return (저장 X)"
- 3차 답: "curl POST /generate → JSON 1개 반환" ← **이것이 Simplest Slice**

Simplest Slice가 동작하면 → 점진적으로 확장 (UI, DB, Critic 등).

#### 6.3 Surgical Scope (수술적 범위)

```
- 수정 가능한 파일 목록은 무엇인가?
- 수정 금지 파일은 무엇인가?
```

| 분류 | 정의 | 예시 (Phase 1) |
|---|---|---|
| **editable** | 이 Phase에서 신규 생성/수정 가능 | `apps/web/`, `backend/fastapi/` |
| **read-only** | 참조만, 수정 시 contract-change 필수 | `docs/contracts/`, `ai_system/prompts/` |
| **forbidden** | 다른 Phase 영역, 절대 접근 금지 | `phases/archive/`, 미래 Phase 코드 |

수정 가능 목록은 `phases/active/{phase-name}/scope.md`의 "예상 파일 변경 목록"과 일치해야 한다.
**범위 밖 파일을 건드릴 필요가 생기면 → scope creep 신호, 즉시 사용자에게 알림.**

#### 6.4 Verification (검증)

```
- 성공 기준은 무엇인가?
- 어떤 테스트로 확인할 것인가?
```

성공 기준은 `acceptance.md`의 A1~An과 1:1 매핑. 각 기준에 대해:

| 검증 항목 | 검증 방법 | 자동/수동 |
|---|---|---|
| 흐름 동작 | curl + JSON schema validation | 자동 |
| Intent Filter | golden_set GS-001~003 케이스 | 자동 |
| UI 진입 | localhost:3000 manual 확인 | 수동 |

**자동화 가능한 것은 자동화** — 수동 검증만 있는 acceptance는 회귀 위험.

### 7. 첫 작업 단위 선정

`goals.md`를 작업 단위로 분해해서 첫 단위를 제시:

- 1회 세션에서 완료 가능한 크기 (1–4시간 작업)
- 명확한 산출물이 있어야 함 (파일 / 함수 / 문서)
- acceptance.md의 한 줄 이상에 매핑돼야 함
- §6.2 Simplest Slice에서 도출한 단위를 **그대로 사용** (재정의 금지)

### 8. PHASE_REGISTRY 갱신

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
5. **4점검 생략**: §6 Assumptions/Simplest Slice/Surgical Scope/Verification 누락 시 후반 scope creep 발생률 ↑.
6. **Simplest Slice 압축 부족**: "더 줄일 수 있는가?" 1회만 묻고 멈춤. 3회 반복 필수.

## 변경 이력

- v1.0.0 (Phase 0): GPT 골격 + 우리 절차 통합
- v1.1.0 (Phase 1 진입 전, 2026-05-26): §6 Phase 진입 4점검 추가
  (Assumptions / Simplest Slice / Surgical Scope / Verification)
