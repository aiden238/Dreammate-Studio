# phase_eval.md — Phase 종료 평가

> 위치: `eval/phase_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `PHASE_REGISTRY.md` (Phase 정의 + active phase)
> 참조: `phases/active/{current-phase}/acceptance.md` (Phase별 acceptance)
> 참조: `meta/retrospectives/` (Phase 회고 누적)
> Skill 연동: `phase-complete`, `phase-review`

---

## 1. 목적

각 Phase의 종료 시점에 "이 Phase가 정말로 끝났는가"를 정량 평가한다. acceptance 충족 여부 + 다음 Phase의 의존성 준비도 + 회고 항목의 3 축으로 측정한다. 본 평가가 pass되어야 phase-complete Skill이 Phase를 close하고 다음 Phase를 active로 전환한다.

---

## 2. 평가 차원 (5 개)

### 2.1 acceptance_coverage — Acceptance 충족도

```
정의: phases/active/{phase}/acceptance.md의 항목 충족 비율.
측정:
  - 각 acceptance 항목 checkbox 통과 여부
  - 통과 = 산출물 존재 + 검증 통과
  - 비통과 = 산출물 없음 또는 검증 실패
임계: 100%
0점: < 80%
5점: 100%
주의: acceptance를 사후에 낮추는 변경 금지 (contract-change Skill 절차).
```

### 2.2 contract_consistency — Contract 정합성

```
정의: 본 Phase에서 도입/수정된 contract와 종속 산출물의 정합.
측정:
  - 새 contract의 cross-reference 일관 (양방향)
  - 의존 산출물의 인용이 모두 유효 (broken link 0)
  - enum / 필드명이 모든 산출물에서 동일
임계: 100%
0점: broken link 1개 이상
5점: 100%
```

### 2.3 regression_status — 회귀 상태

```
정의: 본 Phase 종료 시점의 회귀 평가 결과.
측정 (regression_eval.md):
  - 마지막 회귀 verdict == pass
  - P0 케이스 100%
  - cost_drift / latency_drift 정상
임계: 통과
0점: 회귀 fail
5점: 회귀 pass + 새 케이스 추가
```

### 2.4 next_phase_readiness — 다음 Phase 의존성 준비도

```
정의: 다음 Phase의 prerequisites가 충족되는가.
측정:
  - 다음 Phase phases/{next}/prerequisites.md 항목 체크
  - 본 Phase 산출물이 다음 Phase 입력으로 정합
임계: 100%
0점: < 80%
5점: 100%
주의: 다음 Phase prerequisites가 미정의면 본 차원 결측 (해당 Phase에서 정의 누락 fail).
```

### 2.5 retrospective_quality — 회고 품질

```
정의: meta-retrospective Skill의 산출물 품질.
측정:
  - well/missed/learned/next 4 섹션 모두 작성
  - 정량 데이터 포함 (회귀 결과, 비용, 사용자 피드백 등)
  - action items 명시 (다음 Phase에 반영할 변경)
임계: 4 섹션 모두 + action items ≥ 3
0점: 회고 미작성
5점: 4 섹션 + action ≥ 5 + 정량 근거
```

---

## 3. 입력 / 출력 형식

### 3.1 입력

```yaml
phase_id: "phase-0-migration"
acceptance_path: "phases/active/phase-0-migration/acceptance.md"
contracts_touched:
  - "docs/contracts/output_schema.md"
  - "docs/contracts/agent_io_contract.md"
regression_run_id: "uuid (latest)"
retrospective_path: "meta/retrospectives/2026-05-26-phase-0.md"
next_phase: "phase-1-data"
next_prerequisites_path: "phases/phase-1-data/prerequisites.md"
```

### 3.2 출력

```yaml
phase_id: "phase-0-migration"
verdict: pass | fail
scores:
  acceptance_coverage: 0~5
  contract_consistency: 0~5
  regression_status: 0~5
  next_phase_readiness: 0~5
  retrospective_quality: 0~5
phase_eval_avg: 0~5
blockers:
  - { dim: "...", desc: "..." }
action_items_carried:               # 다음 Phase로 이월
  - "..."
closed_at: ISO8601
closed_by: user_id
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| acceptance_coverage | 자동 (acceptance.md checkbox 파싱) | 운영자 1차 (검증 결과 확인) |
| contract_consistency | 자동 (link checker + grep) | 운영자 보조 |
| regression_status | 자동 (eval/regression_results/) | — |
| next_phase_readiness | 자동 + 운영자 확인 | 운영자 주도 |
| retrospective_quality | 자동 (섹션 존재 검사) | 운영자 주도 (품질 판단) |

---

## 5. 임계값

```
모든 차원 ≥ 4 AND acceptance_coverage == 5: pass
1 차원이라도 < 4: fail (Phase close 차단)

특수 게이트:
- acceptance_coverage < 5 (= 100% 미만): 즉시 차단
- contract_consistency < 5: 즉시 차단 (broken link 1개라도)
- regression_status < 3 (fail): 즉시 차단
- retrospective 미작성: 자동 차단 (phase-complete Skill이 retrospective 먼저 트리거)
```

---

## 6. Phase 종료 절차

### 6.1 phase-complete Skill 흐름

```
1. 운영자가 phase-complete Skill 호출
2. Skill이 본 phase_eval 자동 실행:
   - acceptance.md 파싱 + checkbox 카운트
   - contracts 정합성 검사
   - 최신 회귀 결과 확인
   - prerequisites.md 매칭
3. retrospective 미작성 시 meta-retrospective Skill 우선 호출
4. 모든 차원 ≥ 4 시 verdict=pass
5. 통과 시:
   - PHASE_REGISTRY.md 갱신 (current → completed, next → active)
   - phases/active/{phase}/ → phases/completed/{phase}/ 이동
   - HANDOFF.md 갱신
6. 실패 시:
   - blockers를 phases/active/{phase}/blockers.md에 기록
   - 운영자 액션 안내
```

### 6.2 phase-review Skill 흐름

```
phase-complete 직후 또는 별도 시점에 phase-review Skill로 사후 검토:
1. closed 된 Phase의 회고를 다시 읽고 패턴 추출
2. 다음 Phase prerequisites에 반영할 항목 도출
3. meta/patterns.md에 누적 패턴 INSERT
```

---

## 7. 관련 contract / Skill 연결

```
contract:
  - PHASE_REGISTRY.md (Phase 정의)
  - phases/active/{phase}/acceptance.md
  - phases/{next}/prerequisites.md

Skill:
  - phase-complete (Phase 종료 시점 자동 호출)
  - phase-review (사후 검토)
  - meta-retrospective (회고 작성)
  - contract-change (acceptance 변경 시)

연관 파일:
  - meta/retrospectives/ (회고 보관)
  - meta/patterns.md (누적 패턴)
```

---

## 8. Open Questions

1. acceptance 사후 변경 정책 — 정말 100% 불가능한가, 운영 데이터로 조정 필요한 경우.
2. 회귀 fail 상태에서 Phase 종료 허용 vs 강제 — 현재 강제 차단, 핫픽스 예외 필요한가.
3. retrospective_quality 자동 채점 — 섹션 존재 외에 정량 데이터 검사 가능한가.
4. action_items 이월 추적 — 다음 Phase에서 완료 여부 자동 확인.
5. Phase rollback 절차 — 종료 후 잘못 종료된 경우 (Phase 0 → 1 → 0 복귀).
6. Phase 병합 / 분할 정책 — 진행 중 새 Phase 추가가 필요해진 경우.
