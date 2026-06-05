---
name: qa-check
description: |
  Phase 완료 직전 또는 배포 직전 기본 품질 게이트를 통과시킬 때 사용한다.
  MVP 범위 위반 확인, API/스키마 정합성, 에러 처리, 모바일 화면, 저장/재시도
  흐름, 비용/로그 정상성을 한 번에 점검한다. release-gate 기능 흡수.
  키워드: "QA 검사", "release gate", "배포 전", "최종 점검", "MVP 점검",
  "smoke test", "regression 통과 확인".
applies_to: [agents]
phase: [phase-9, phase-10, phase-11, before-release]
related_contracts:
  - docs/contracts/mvp_non_goals.md
  - docs/contracts/output_schema.md
  - docs/contracts/api_contract.md
  - apps/web/design.md
related_state:
  - eval/regression_results/
version: v1.3.0
---

# qa-check

배포 / Phase 종료 전 게이트. 통과해야만 다음 단계 진행.

## 트리거 조건

- Phase 종료 직전 (phase-complete 1단계 acceptance 확인 후)
- 배포 직전 (staging → prod)
- 사용자가 "배포해도 돼?" 또는 "QA 한 번 보자"

## 점검 카테고리 12개 (v1.3.0)

각 카테고리는 pass/fail/skip 중 하나로 판정.

### 1. MVP 범위 점검

`docs/contracts/mvp_non_goals.md`의 항목들이 작업물에 들어왔는지 확인:

```
- 자동 영상 편집      → 안 들어왔는지
- TTS / BGM 생성     → 안 들어왔는지
- 결제 / billing      → 안 들어왔는지
- 팀 협업             → 안 들어왔는지
- Expo Mobile App     → 안 들어왔는지
- Spring Boot 의존    → 안 들어왔는지 (Phase 21 전이면)
```

들어왔으면 fail. scope creep 발견 → contract-change Skill로 위임 또는 제거.

### 2. API 응답 형식 점검

각 endpoint를 한 번씩 실제 호출:

```
- 응답이 output_schema와 일치하는가?
- 에러 응답이 정의된 형식인가?
- 상태 코드가 적절한가?
- 필수 필드가 모두 있는가?
- 인증 필요한 endpoint가 인증 없이 응답하지 않는가?
```

자동화: contract test 도구로 schema validation.

### 3. 에러 상태 점검

design.md의 `State & Error Rules`에 명시된 상태가 모두 구현됐는지:

```
- Empty State
- Loading State
- Streaming State (생성 중)
- Partial Result State
- Error State + 다음 액션 제공
- Retry State
- Save Success State
- Memory Updated State
```

빈 로딩 스피너만 30초 노출 같은 안티패턴 없는지 확인.

### 4. 모바일 화면 점검

iPhone SE(375px), iPhone 14(390px), Galaxy S22(360px) 기준:

```
- 가로 스크롤 발생 안 함
- 터치 영역 44×44px 이상
- 한 손 조작 가능 (CTA 하단)
- 카드가 한 화면에 적정 수 배치
- safe-area inset 적용
- 키보드 올라와도 입력창 가림 없음
```

수동 검사 + 자동화(Playwright viewport 테스트).

### 5. 저장 / 재시도 흐름

```
- 사용자 입력이 도중에 끊겨도 임시 저장되는가?
- 네트워크 끊김 후 재연결 시 자동 동기화되는가?
- LLM 호출 실패 시 재시도 버튼 동작?
- 부분 결과가 보존되는가?
- 사용자가 명시적으로 저장 안 했어도 draft로 남는가?
```

### 6. AI 호출 정상성

```
- 4-agent 파이프라인이 끝까지 진행되는가?
- 30–60초 안에 첫 결과 노출?
- Critic 점수가 모든 차원에 들어왔는가?
- prompt_version이 agent_io_logs에 기록되는가?
- 실패 시 어느 단계에서 실패했는지 알 수 있는가?
```

### 7. 비용 / Rate Limit

```
- 1 세션당 LLM 호출 수가 예상 범위 안인가?
- agent_io_logs.cost_usd 합계가 임계값 이하?
- 같은 사용자가 1분 안에 N번 이상 호출 시 차단되는가?
- 비용 폭주 알람이 작동하는가?
```

비정상이면 cost-review Skill 트리거.

### 8. 로그 / 관측성

```
- request_id, user_id, project_id가 모든 로그에 포함?
- agent_io_logs에 input/output 보존?
- prompt_version, model 정보 기록?
- 에러 발생 시 stack trace + context 충분?
```

### 9. 보안 기본 점검

```
- RLS 정책 동작 확인 (다른 사용자 데이터 노출 없는지)
- prompt injection 시도 입력 차단 동작?
- 개인정보가 응답에 포함되는 케이스 없는지?
- API key가 클라이언트로 노출 안 되는지?
```

심층 보안은 security-review Skill로.

### 10. Simplicity Check (v1.1.0 추가)

이 Phase에서 구현된 코드/문서가 **최소 범위 원칙**을 지켰는지 점검:

```
- [ ] 요청받지 않은 기능이 들어가지 않았는가?
- [ ] 단일 사용 추상화가 생기지 않았는가?
- [ ] Phase 1에서 Phase 2~3 기능을 미리 구현하지 않았는가?
- [ ] 200줄짜리 구현이 50줄로 줄어들 수 있지 않은가?
- [ ] 기존 문서/코드의 unrelated formatting을 바꾸지 않았는가?
```

각 항목 fail 시 처리:

| 항목 | fail 처리 |
|---|---|
| 요청받지 않은 기능 | 즉시 제거 (scope creep) |
| 단일 사용 추상화 | inline 화 또는 다음 사용처 명시 |
| 미래 Phase 선구현 | 다음 Phase로 이관 또는 제거 |
| 200줄→50줄 가능 | 리팩토링 또는 사유 기록 |
| unrelated formatting | git revert |

**판정 기준**:
- 5개 모두 통과 → Simplicity pass
- 1–2개 fail → 사용자 확인 후 보류 또는 정리
- 3개 이상 fail → 구현 자체가 scope creep, 강제 정리 필요

심층 패턴 검토는 `meta-retrospective` Skill로 위임.

### 11. Contract Drift (v1.2.0 추가)

`harness-audit` Skill §6.5 `scripts/audit_naming.ps1` 자동 실행 → contract / code / frontend 간 핵심 명명 일관성 확인.

**실행**:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File scripts/audit_naming.ps1
```

**판정**:
- 종료 코드 0, "0 drift detected" → **pass**
- 종료 코드 1, drift 발견 → **fail (critical)**
- whitelist 후보 신규 발견 (역사 보존 영역의 의도된 명명) → **warn** (NAMING_POLICY 갱신 권장)

**Fail 처리**:
1. drift 위치 확인 (audit 출력)
2. `contract-change` Skill 발동 — 어느 쪽이 canonical인지 결정 후 일괄 변경
3. 또는 NAMING_POLICY whitelist 보강 (의도된 예외)
4. 재실행 → pass 확인 후 phase-complete 게이트 통과

**배경**: P-DRIFT-001 (meta/patterns.md) — Phase 1 회고 P3 적용으로 매 Phase 종료 시 자동 게이트화.

### 12. 운영 도달성 (Operational Reachability) — HIP-008 S1 (v1.3.0 추가)

★ 배경 (`meta/audits/2026-06-05.md` §A/B/C): "코드 완성도 高 / 실사용 中" — flag default OFF, 홈/네비 미완, migration 미적용, in-memory 영속 등으로 **만든 기능이 사용자에게 도달하지 못한 채 누적**. 기존 done 기준(pytest green + flag-OFF byte-identical)이 관대해 "동작 ≠ 도달"을 못 걸렀다. 본 카테고리가 그 게이트.

이 Phase 산출물에 대해:

```
- [ ] 사용자 진입 경로가 있는가? (홈/네비에서 클릭으로 도달 — 링크 없는 기능 = fail)
- [ ] default 설정으로 동작하는가? OFF(gated)라면 ON 경로·조건이 문서화됐는가?
- [ ] 영속이 필요한 데이터가 재시작 후 보존되는가? (in-memory only = warn + 이월 명시)
- [ ] 운영 의존(migration / SQL function / secret)이 있으면 적용 절차가 명시됐는가? (미적용 = warn)
- [ ] 라이브 1회 도달 데모(헤드리스 한계 시 유닛 + 도달 경로 입증)가 있는가?
```

**판정**:
- 진입 경로 0 (사용자가 발견 불가) AND 명시적 이월(NG) 없음 → **fail**
- flag OFF 인데 ON 경로/조건 미문서 → **fail**
- 영속/운영 의존 미명시 → **warn** (이월 backlog 등록 필수)

★ **"behavior-preserving + 테스트 green" 만으로 done 처리 금지** — 도달성 항목을 충족하거나, 충족 못 하면 **명시적 이월(NG 번호 + backlog)**로 기록해야 phase-complete 게이트 통과. (phase-complete 가 qa-check 를 호출하므로 본 항목이 phase 종료 acceptance 에 자동 포함.)

## 절차

### 1. 11개 카테고리 순차 점검

각 카테고리에 대해 pass/fail/skip 기록.

```
| # | 카테고리 | 결과 | 메모 |
|---|---|---|---|
| 1 | MVP 범위 | pass | - |
| 2 | API 응답 형식 | fail | /generate가 schema 안 맞음 |
| ... | ... | ... | ... |
| 10 | Simplicity Check | pass | 5개 모두 통과 |
| 11 | Contract Drift | pass | audit_naming 0 drift |
```

### 2. 실패 항목 처리

```
fail가 0개         → 다음 단계 진행 OK
fail가 1–2개       → 사용자 결정 (보류 vs 진행)
fail가 3개 이상    → 진행 차단, fix phase 필요
fail가 Critical    → 무조건 차단 (보안, 데이터, MVP 범위 위반)
```

Critical 항목: 카테고리 1, 8(보안 부분), 9(전체), 10(Simplicity 3 fail 이상), 11(audit_naming drift 1건이라도).

### 3. smoke test 실행

전체 시스템 통과 시나리오 1개라도 끝까지 돌아가는지:

```
1. 신규 회원 가입
2. 첫 Brand 생성 (Discovery)
3. Domain → Series 생성
4. 첫 영상 기획 생성
5. 3개 기획안 비교 → 1개 선택
6. Final Output 확인
7. Quick Mode로 두 번째 영상 추가
```

이 시나리오가 막힘없이 끝까지 가야 함.

### 4. 결과 보고

`eval/qa_reports/{trigger}_{YYYY-MM-DD-HHMM}.md`:

```markdown
# QA Check Report

- 트리거: {phase-complete / pre-release}
- 실행일: {YYYY-MM-DD HH:MM}
- 결과: {ALL PASS / N FAIL / BLOCKED}

## 카테고리별 결과
{9개 카테고리 표}

## smoke test
{각 단계 결과}

## 차단 항목
{있는 경우 나열}

## 권장 다음 액션
{진행 OK / 특정 fix 후 재검사 / 새 phase}
```

## 자주 발생하는 실수

1. **smoke test 생략하고 단위 테스트만 통과로 판정**: 통합 흐름 깨짐.
2. **MVP 범위 점검 형식적**: "들어왔겠지" 추측. 실제 코드 grep 필요.
3. **에러 상태 1–2개 점검하고 나머지 skip**: 누락된 상태가 운영에서 노출.
4. **모바일 점검을 시뮬레이터만**: 실기기 또는 실제 viewport로 확인.
5. **fail인데 "별로 안 중요해 보임"으로 보류**: 누적되면 게이트 의미 상실.
6. **Simplicity Check 생략**: 카테고리 10은 phase-complete 직전 가장 빠지기 쉽지만 가장 효과 큼.

## 변경 이력

- v1.0.0 (Phase 0): 9 카테고리 + smoke test
- v1.1.0 (Phase 1 진입 전, 2026-05-26): 카테고리 10 Simplicity Check 추가
- v1.2.0 (2026-05-27 Phase 1 회고 P3 적용): 카테고리 11 Contract Drift 추가 (`scripts/audit_naming.ps1` 자동 게이트, P-DRIFT-001 대응)
- v1.3.0 (2026-06-05 HIP-008 S1): 카테고리 12 운영 도달성(Operational Reachability) 추가 — "동작 ≠ 도달" 게이트. done 정의에 사용자 진입 경로 + flag ON 경로 + 영속/운영 의존 명시 또는 이월 강제. meta/audits/2026-06-05.md §A/B/C 대응.

## 다른 Skill과의 관계

```
phase-complete   : qa-check를 1단계 일부로 호출
cost-review      : 카테고리 7 fail 시 위임
security-review  : 카테고리 9 fail 시 위임
bug-triage       : 발견된 실패가 새 버그면 분류
contract-change  : 카테고리 1 위반 시 contract 재검토 또는 제거
```

## 종료 조건

- 모든 카테고리 pass + smoke test 통과 → 정상 종료, 다음 단계 진행 권한
- 일부 fail + 사용자 결정 → 결정 기록 후 종료
- Critical fail → 차단, 후속 작업 위임 후 종료
