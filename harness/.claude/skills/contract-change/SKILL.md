---
name: contract-change
description: |
  docs/contracts/ 안의 어떤 파일이라도 수정해야 할 때 사용한다.
  contracts는 직접 편집하지 않고 항상 제안 → 검토 → 승인 → 반영 절차를 거친다.
  API 변경, DB 스키마 변경, output_schema 변경, agent_io 변경, breaking change,
  contracts 수정, 정책 변경 시 트리거. Skill 파일 자체의 변경도 이 절차를 따른다.
applies_to: [agents, claude]
phase: [all]
related_contracts:
  - docs/contracts/
related_state:
  - meta/proposals/
  - docs/contract_changes/
  - docs/decisions/
version: v1.0.0
---

# contract-change

`docs/contracts/` 안 어떤 파일도 직접 편집하지 않는다. 모든 변경은 제안 → 검토 → 승인 → 반영 4단계를 거친다.

## 적용 범위

다음 파일 변경 시 무조건 트리거:

```
docs/contracts/*.md
ai_system/prompts/prompt_registry.md         (prompt-version-review와 함께)
apps/web/design.md                            (대규모 변경 시)
docs/decisions/*.md                           (신규 작성은 OK, 기존 ADR 수정 시)
.skills/*/SKILL.md                            (Skill도 contract처럼 취급)
```

다음은 적용 안 됨:

```
PROJECT_STATE.md, PHASE_REGISTRY.md      # 상태 파일 (상시 갱신)
phases/active/*/notes.md                  # 진행 메모
agent_io_logs, candidate_knowledge 등     # 데이터
src/, apps/web/components/*               # 코드
```

## 절차

### 1. STOP — 직접 편집 시도 차단

contract 파일을 수정하라는 요청이 오면 **무조건 일단 멈춘다.** 즉시 사용자에게 알린다:

```
이 변경은 contract에 영향을 주는 변경입니다.
직접 수정 대신 contract-change 절차를 따라 제안서를 먼저 만들겠습니다.
```

긴급한 경우라도 절차는 똑같이 거친다. (긴급 우회 모드 없음.)

### 2. 변경 제안서 작성

`meta/proposals/{YYYY-MM-DD}-{slug}.md` 파일을 새로 만든다.

#### 제안서 템플릿

```markdown
# Contract Change Proposal: {짧은 제목}

- 제안일: {YYYY-MM-DD}
- 제안자: {사용자 또는 Claude/Codex 식별}
- 대상 contract: docs/contracts/{filename}.md
- 변경 종류: [신규 / 수정 / 삭제 / breaking change]
- 긴급도: [낮음 / 보통 / 높음]

## 변경 사유
{왜 필요한지 2–4줄}

## 변경 내용 (diff 또는 before/after)

### Before
```
{원본 발췌}
```

### After
```
{변경안 발췌}
```

## 영향 받는 영역

- [ ] API 응답 형식
- [ ] DB 스키마
- [ ] Agent IO
- [ ] Output Schema
- [ ] 프론트 컴포넌트
- [ ] Prompt
- [ ] RAG 파이프라인
- [ ] 평가 / golden_set
- [ ] 보안 / 권한

## 영향 받는 파일 목록

```
{경로 나열}
```

## Rollback 방안
{되돌릴 수 있는지, 되돌리려면 어떻게 하는지}

## 마이그레이션 필요 여부
- [ ] DB 마이그레이션
- [ ] 기존 데이터 변환
- [ ] 사용자 통지
- [ ] 외부 API 클라이언트 통지

## 승인 기준
- 자기 단독 결정: 사소한 wording, 오탈자, 명세 명확화
- 사용자 승인 필요: 의미 변경, 영향 범위 확장, breaking change
- 추가 검토 필요: 보안 / 비용 / 외부 인터페이스 영향

## 결정
- [ ] 승인 / 반려 / 수정 후 재검토
- 결정자:
- 결정일:
- 메모:
```

### 3. 영향도 자동 점검

제안서 작성 직후, 다음을 자동 점검:

| 변경 유형 | 자동 점검 항목 |
|---|---|
| API 스키마 | output_schema.md, agent_io_contract.md, frontend 컴포넌트 import |
| DB 스키마 | RLS 정책, 마이그레이션 파일, ORM 모델 |
| output_schema | Pydantic 모델, TypeScript 타입, agent prompt 출력 형식 |
| agent_io | prompt_registry의 P-XXX 출력 형식, orchestration 흐름 |
| prompt_registry | prompt-version-review Skill 절차 추가 트리거 |
| privacy / security | security-review Skill 추가 트리거 |
| rate_limit | cost-review Skill 추가 트리거 |

점검 결과는 제안서 "영향 받는 영역" 체크박스에 반영.

### 4. 승인 요청

승인 기준에 따라 다음 중 하나:

#### 4-1. 자기 단독 결정 가능 (사소한 변경)

다음에만 해당:
- 오탈자, 띄어쓰기, 마크다운 포맷
- 주석/설명 추가 (의미 변경 없음)
- 외부에 안 드러나는 internal 코멘트

→ 제안서에 "self-approved" 표시 후 5단계로.

#### 4-2. 사용자 승인 필요

다음 전부 해당:
- 의미 변경
- 새 필드 추가/삭제
- 정책 임계값 변경
- 영향 받는 파일 3개 이상

→ 사용자에게 제안서 보여주고 명시적 승인 대기. "이대로 진행할까?" 한 줄로 확인.

#### 4-3. 추가 검토 필요

다음에만 해당:
- 보안 contract 변경 → security-review Skill 추가 통과
- 비용 정책 변경 → cost-review Skill 추가 통과
- 외부 API 영향 → migration-readiness 평가 추가

→ 추가 Skill 트리거 후 결과 포함해서 4-2 절차.

### 5. 반영

승인 후:

1. `docs/contracts/{file}.md` 실제 편집
2. `docs/decisions/` 새 ADR 작성 (의미 변경이라면)
3. `docs/contract_changes/{YYYY-MM-DD}-{slug}.md`에 변경 로그 기록
4. `meta/proposals/`의 원본 제안서에 "approved" + 결정일 추가
5. 영향 받는 코드/문서 동기화 작업 자동 trigger (별도 Phase로 분기)

### 6. 로그

변경 후 항상 다음을 갱신:

```
PROJECT_STATE.md          : last_contract_change 필드
PHASE_REGISTRY.md         : 영향 받는 Phase에 메모
agent_io_logs (영향 시)   : 새 prompt_version으로 분기
```

## breaking change 특별 절차

contract 변경이 backward-compatibility를 깨면:

1. 제안서 헤더에 `**BREAKING CHANGE**` 명시
2. 영향 받는 모든 외부 인터페이스 나열
3. 마이그레이션 기간 명시 (최소 7일)
4. 구버전 deactivation 일정 명시
5. 사용자 통지 방안 (있다면)

## 자주 발생하는 실수

1. **"빠르게 고치고 나중에 문서화"**: 절대 안 됨. 작은 변경도 절차 통과.
2. **제안서 없이 contracts/ 직접 편집 후 사후 보고**: contract-change 위반. 즉시 rollback.
3. **여러 변경을 한 제안서에 묶기**: 영향도 추적 불가. 분할 권장.
4. **rollback 방안 안 적기**: 모든 제안서 필수 항목.
5. **영향 받는 영역 체크박스 누락**: 점검 자체가 안 됐다는 신호.

## 종료 조건

- 변경 반영 + 로그 갱신 완료 → 정상 종료
- 사용자 반려 → 제안서에 반려 사유 기록 후 종료
- 영향도 점검에서 추가 Skill 트리거 필요 → 해당 Skill로 위임 후 결과 받아 재개

## 금지 사항

- `meta/proposals/`를 거치지 않은 contract 수정.
- 다른 Skill이 contract-change를 우회해서 contracts/를 직접 수정하는 경로.
- 승인 받지 않은 상태에서 "preview" 명목으로 실제 파일 수정.
- 자기 단독 결정 범위를 임의로 확장.
