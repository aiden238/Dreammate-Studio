---
name: phase-complete
description: |
  Phase 종료 시 정리, 문서 동기화, 상태 갱신, 회고 트리거를 수행한다.
  acceptance 기준 충족 확인, PROJECT_STATE/PHASE_REGISTRY 갱신, 변경된 contract와
  코드 일치성 점검, archive 이동, meta-retrospective 호출까지 한 번에 처리한다.
  docs-sync 기능을 흡수했다.
  키워드: "Phase 종료", "phase 완료", "phase complete", "archive",
  "이번 phase 정리", "phase wrap up", "phase 종료 절차".
applies_to: [agents, claude]
phase: [all]
related_state:
  - PROJECT_STATE.md
  - PHASE_REGISTRY.md
  - phases/active/
  - phases/archive/
version: v1.1.0
---

# phase-complete

Phase가 끝나면 다음 Phase로 정리되지 않은 상태가 흘러가지 않도록, 종료 시점의 정리 절차를 강제한다.

## 트리거 조건

- 사용자가 "Phase X 끝났어", "다음 phase로 넘어가자"
- acceptance.md의 모든 기준이 통과됐다고 판단되는 시점
- 또는 Phase를 중단/포기하는 시점

## 절차

### 1. acceptance 확인

`phases/active/{phase-name}/acceptance.md`의 모든 항목을 확인:

```
- [x] / [ ] 체크 상태
- 각 항목의 근거 (테스트 통과, 결과 파일, 사용자 확인 등)
```

미통과 항목 있으면:
- 강제 종료할지, 미통과 항목을 다음 Phase로 이월할지 사용자에게 선택지 제시
- 어느 쪽이든 `phases/active/{phase-name}/closing_notes.md`에 사유 기록

### 1.5 자동 smoke test (v1.1.0 추가)

Phase별 자동 smoke 스크립트가 존재하면 실행하고 결과를 첨부:

```powershell
# 예: Phase 1
powershell -ExecutionPolicy Bypass -NoProfile -File scripts/smoke_test_phase_1.ps1
```

**판정**:
- 종료 코드 0 → pass, 결과를 `eval/qa_reports/phase-{N}-smoke-test-automated_{date}.md` 에 첨부 (이미 있으면 갱신)
- 종료 코드 1 → fail, **즉시 작업 중단**. fix 후 재실행 또는 `closing_notes.md`에 보류 사유 명시 후 사용자 결정.

**스크립트 부재 시**:
- 자동 스크립트가 없으면 본 단계는 skip
- 단, Phase 종료 commit 직전에 `scripts/smoke_test_phase_{N}.ps1` 신규 작성 권장 (다음 Phase 회귀 baseline)

**근거**: Phase 1 회고 P4 (`meta/retrospectives/phase-1.md`) — 매 Phase 종료 시 자동 게이트화로 회귀 차단.

### 2. 산출물 정리

이번 Phase에서 만든 것 목록화:

```
## 코드 변경
{git diff 요약 또는 변경된 파일 목록}

## 새로 만든 문서
{phases/, contracts/, decisions/ 신규 파일}

## 변경된 contracts
{contract-change Skill 통과 항목들}

## eval 결과
{golden_set 통과율, 회귀 평가 결과}

## 메트릭
{비용, 토큰, latency 등 측정값}
```

### 3. docs-sync (구 docs-sync Skill 흡수)

코드와 문서의 정합성 점검:

| 코드 영역 | 동기화 대상 contract |
|---|---|
| `apps/web/components/` | `apps/web/design.md`의 컴포넌트 목록 |
| `apps/web/pages/` | `apps/web/design.md`의 IA |
| `backend/api/routes/` | `docs/contracts/api_contract.md` |
| `backend/db/migrations/` | `docs/contracts/db_schema.md` |
| `ai_system/agents/` | `docs/contracts/agent_io_contract.md` |
| `ai_system/prompts/` | `ai_system/prompts/prompt_registry.md` |

코드 변경이 contract와 어긋나면:
- contract-change Skill 트리거하여 contract를 따라가게 하거나
- 코드를 contract에 맞추거나
- 한쪽 결정 후 다음 phase에서 처리

**중요**: contract를 직접 수정하지 않는다. 항상 contract-change Skill로.

### 4. 상태 파일 갱신

```
PROJECT_STATE.md:
  current_phase     : {next or null}
  last_phase_done   : {this-phase}
  last_phase_date   : {YYYY-MM-DD}
  open_issues       : {남은 항목 목록}
  next_actions      : {권장 다음 phase 또는 작업}

PHASE_REGISTRY.md:
  {this-phase}.status     : active → done (또는 abandoned)
  {this-phase}.completed_at : {timestamp}
  {this-phase}.notes        : {핵심 메모 1–2줄}
```

### 5. archive 이동

`done` 상태인 phase는 `phases/archive/{YYYY-QQ}/`로 이동.

```
phases/active/{phase-name}/  →  phases/archive/2025-Q4/{phase-name}/
```

이동 후 active 폴더는 다음 Phase가 들어올 수 있게 비워둠.

`abandoned` 상태:
- `phases/abandoned/`로 이동
- closing_notes.md 필수

### 6. eval 결과 보관

이번 Phase에서 돌린 평가 결과를 영구 보관:

```
eval/regression_results/{phase-name}_{YYYY-MM-DD}.md
eval/cost_snapshots/{phase-name}_{YYYY-MM-DD}.md
eval/latency_snapshots/{phase-name}_{YYYY-MM-DD}.md
```

### 7. meta-retrospective 트리거

Phase 종료는 항상 회고 트리거. meta-retrospective Skill에 위임.

회고 시드 정보:
- acceptance 미통과 항목
- 예상 소요 vs 실제 소요
- 발견된 contract 갈등
- 발견된 보안/비용 이슈
- 다음 Phase에 가져갈 학습

### 8. 다음 Phase 안내

종료 후 사용자에게 다음 액션 제시:

```
[Phase 종료 완료]
Phase: {phase-name}
결과: {요약}
산출물: {핵심 결과물 링크}
회고: meta/retrospectives/{phase-name}.md

다음 권장:
- {next-phase-name} 시작 (phase-start Skill로)
- 또는 {특정 이슈} 먼저 해결
```

## docs-sync 세부 점검

phase-complete의 핵심 부분이라 별도 명시:

### API 동기화

```
backend/api/routes/*.py 의 endpoint 목록
↕
docs/contracts/api_contract.md 의 endpoint 목록

차이 발견 시:
- 코드에만 있음 → contract 미반영 (contract-change 필요)
- contract에만 있음 → 구현 누락 (다음 phase 이슈)
```

### DB 동기화

```
backend/db/migrations/ 의 최신 마이그레이션
↕
docs/contracts/db_schema.md

차이 발견 시:
- 마이그레이션 적용은 됐는데 schema 문서 미갱신 → contract-change
- schema에 있는데 마이그레이션 없음 → 다음 phase 이슈
```

### 컴포넌트 동기화

```
apps/web/components/ 의 export 목록
↕
apps/web/design.md 의 Component System 섹션

차이 발견 시:
- 코드에만 있는 컴포넌트 → design.md 누락
- design.md에만 있는 컴포넌트 → 구현 누락
```

### Agent IO 동기화

```
ai_system/agents/*/{schemas,prompts} 
↕
docs/contracts/agent_io_contract.md + ai_system/prompts/prompt_registry.md

차이 발견 시 → contract-change 또는 prompt-version-review
```

## 자주 발생하는 실수

1. **acceptance 절반 통과 상태로 종료**: 미통과 항목이 다음 phase에 이월되지 않고 사라짐.
2. **archive 이동 누락**: active 폴더에 done phase가 쌓여 phase-start가 헷갈림.
3. **PROJECT_STATE.md 갱신 누락**: 다음 세션이 어디서 시작할지 모름.
4. **meta-retrospective 건너뛰기**: 같은 실수 반복.
5. **docs-sync 안 하고 다음 phase로**: 코드-문서 갭이 쌓여 한꺼번에 정리 시 부담.
6. **자동 smoke test 건너뛰기 (v1.1.0)**: §1.5 자동 스크립트가 있는데 manual instructions만 보고 통과 처리 → 실제 회귀 미발견.

## 변경 이력

- v1.0.0 (Phase 0 S5): 8단계 절차 정형화
- v1.1.0 (2026-05-27 Phase 1 회고 P4 적용): §1.5 자동 smoke test 단계 추가 (scripts/smoke_test_phase_{N}.ps1)

## 종료 조건

- 모든 8단계 완료 → 정상 종료, 다음 Phase 준비됨
- acceptance 미통과 + 사용자가 강제 종료 결정 → closing_notes 기록 후 종료
- docs-sync에서 큰 갭 발견 → docs-sync 작업을 별도 mini-phase로 분리

## 금지 사항

- acceptance 미확인 상태로 archive 이동
- meta-retrospective 호출 없이 종료
- contracts 직접 수정으로 docs-sync 처리
