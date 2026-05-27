# Proposal Batch — Phase 1 Retrospective 결과 (P1~P4)

> 출처: `meta/retrospectives/phase-1.md` §개선 제안
> 작성일: 2026-05-26
> 상태: pending review (사용자 승인 대기)
> 적용 절차: contract-change Skill (Skill SKILL.md 변경 → 절차 통과)

---

## 채택 권장 제안 4개 (P1~P4)

### P1 — harness-audit Skill에 "contract 명명 cross-check" 추가 (우선순위: 높음)

**근거**: CC-001 (`plan_options` / `plans` / `plan_candidates` 3-way drift)이 Phase 1 진입 점검에서 자동 검출되지 않음. Surgical Scope만으로는 contract 간 일관성 검증 불가.

**변경 대상**:
- `.claude/skills/harness-audit/SKILL.md` v1.0.0 → v1.1.0
- `scripts/audit_naming.ps1` (or .py) 신규 작성

**구현 안**:
- 핵심 명명 집합 정의 (예: plan_candidates, video_projects, agent_io_logs)
- 모든 .py/.ts/.md grep → 출현 위치 매트릭스 생성
- 동일 개념 다른 이름 사용 시 WARN
- whitelist 관리 가능

**예상 영향**: harness-audit 실행 시간 +30초, drift 사후 발견율 ↓
**위험**: false positive (동음이의어) — whitelist로 완화

---

### P2 — phase-start v1.2.0 §6.1 Assumptions에 "contract cross-reference 점검" 추가 (우선순위: 높음)

**근거**: §6.1 Assumptions 작성 시 "외부 contract와 일치"라고 막연히 기록함. 실제 drift 가능성을 explicitly 명시해야 함.

**변경 대상**:
- `.claude/skills/phase-start/SKILL.md` v1.1.0 → v1.2.0

**변경 내용** (§6.1에 추가):
```markdown
- 본 Phase scope에 직간접 영향 contract 간 핵심 명명 일관성 검증 결과
  - 자동: harness-audit Skill의 audit_naming 단계 실행 결과
  - 매뉴얼: 발견된 drift는 §1.2 불확실 U-X로 기록 + contract-change 절차로 처리
```

**예상 영향**: phase 진입 작업 +5~10분
**위험**: 없음

---

### P3 — qa-check 카테고리 11 "Contract Drift" 추가 (우선순위: 보통)

**근거**: Phase 종료 시점에 다시 자동 검사 → 점진적 drift 방지.

**변경 대상**:
- `.claude/skills/qa-check/SKILL.md` v1.1.0 → v1.2.0

**변경 내용**:
- 카테고리 11 신설 — harness-audit 의 audit_naming 결과를 인용 (단순 게이트)
- pass: 0 drift / warn: whitelist 후보 발견 / fail: 신규 drift 발견

**예상 영향**: qa-check 실행 시간 소폭 증가
**위험**: 없음

---

### P4 — phase-complete 절차에 자동 smoke test 통합 (우선순위: 보통)

**근거**: `scripts/smoke_test_phase_1.ps1`이 자동 가능한 끝-to-끝 검증으로 5/5 PASS 달성. 매 Phase 종료 시 매뉴얼 인스트럭션만 두지 말고 자동 실행이 게이트로 작동해야 함.

**변경 대상**:
- `.claude/skills/phase-complete/SKILL.md`

**변경 내용**:
- 절차 5단계(verification)에 `scripts/smoke_test_phase_{N}.ps1` 자동 실행 + 결과 첨부 단계 추가
- Phase 1 baseline 스크립트 참고

**예상 영향**: phase-complete 실행 시간 +1~2분
**위험**: 없음 (스크립트가 graceful — 환경 미설정 시 SKIP 표시)

---

## 미채택 / 보류 제안

### P5 — tech_stack_contract.md에 "Python 패키지명 충돌 방지" 가이드 (우선순위: 낮음)
- 1회 발생, 해결 적용됨 → 가이드만 추가하면 충분. 다음 회고에서 재발 시 우선순위 재평가.

### P6 — assumptions.md §1.2 불확실 항목 자동 트래킹 표 (우선순위: 낮음)
- 관리 비용 vs 이득 균형 검토 필요. P2 적용 후 운영 데이터 누적 후 재평가.

---

## 의존 / 적용 순서

```
P1 (audit_naming 도구 작성) ─┐
                            ├─→ P2 (phase-start v1.2.0 §6.1)
                            ├─→ P3 (qa-check v1.2.0 카테고리 11)
                            └─→ P4 (phase-complete smoke test 통합)
```

P1이 인프라 — 먼저 작성. P2/P3/P4는 P1 도구를 호출하는 절차.

---

## 사용자 검토 요청

```yaml
status: pending_user_review
expected_decision: 2026-05-27 (Phase 2 진입 전)
decision_options:
  - accept_all: P1~P4 모두 채택, contract-change 절차 발동
  - accept_priority: P1 + P2만 우선 채택, P3/P4 백로그
  - reject_with_reason: 채택 거부 + 사유
  - defer: Phase 2 진입 후 재검토
```

---

## 변경 이력

- 2026-05-26: Phase 1 회고 결과 4 제안 배치 작성
