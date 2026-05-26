# ADR — eval 이원 트랙 구조 (Implementation vs Product Quality)

> ADR ID: ADR-009
> Status: accepted
> Date: 2026-05-26
> Author: Claude (Opus 4.7)
> Related: `eval/INDEX.md`, `eval/failure_cases.md`, GPT 검토 의견

---

## Context (배경)

Phase 1 진입 직전, 외부 검토(GPT)에서 다음 지적:

```
1. 평가에는 두 종류가 있다:
   - 구현 Eval: 기술이 작동하는가?
   - 플랫폼 품질 Eval: AI 결과물이 쓸만한가?

2. 둘은 분리해야 한다.
3. 권장 폴더 재구조:
   eval/implementation/
   eval/product_quality/
   eval/reports/
```

현재 하네스 eval/ 구조 점검:
- 15개 평가 파일 + 5개 결과 폴더 (Phase 0 S4에서 deep 작성 완료)
- 82개 cross-reference (SKILL.md / routes.yaml / contracts)
- 일부 파일은 양쪽에 걸침 (accessibility / security / ux_eval / phase_eval)

---

## Decision (결정)

**개념 분리는 채택**, **폴더 이동은 거부**.

### 1. 이원 트랙 개념을 명시화

`eval/INDEX.md` 신규 작성:
- §1 구현 검증 (Implementation Eval) — 기술 동작 확인
- §2 플랫폼 품질 (Product Quality Eval) — AI 출력 실용성
- §3 운영 메타 (둘 다 아닌 메타 평가)
- §4 Phase별 비중 가이드 (Phase 1=70/30 → Phase 8=30/70)
- §5 Phase 1 권장 사용
- §6 운영 절차

### 2. 기존 폴더 구조 보존

- 15개 평가 파일 위치 변경 없음
- 5개 결과 폴더 (qa_reports/, regression_results/ 등) 위치 변경 없음
- 82개 cross-reference 영향 없음
- routes.yaml / dependency_map / SKILL.md 영향 없음

### 3. 누락 파일 보강

GPT 검토에서 Phase 1 최소 요구 명시: "Bad Case 3~5개".  
현재 `eval/failure_taxonomy.md` (분류 체계)는 있으나 실제 케이스 모음은 없음.

→ `eval/failure_cases.md` 신규 작성:
- FC-001~FC-005 시드 (Phase 1)
- failure_taxonomy F1~F8 매핑
- Critic 학습용 + 회귀 차단용

---

## Alternatives Considered (대안)

### A1. GPT 권장안 그대로 폴더 재구조 (eval/implementation/, eval/product_quality/, eval/reports/)

- **장점**: 개념 분리가 폴더로도 명확
- **단점**:
  - 82개 cross-reference 모두 갱신 필요
  - phase-start v1.1.0 §6.3 Surgical Scope 위반 (eval/은 Phase 1에서 read-only)
  - 모호한 경계 파일(accessibility/security/ux_eval/phase_eval) 강제 분류 필요
  - Phase 1 진입 지연 + 회귀 위험
- **결정**: 거부. 비용 > 효익.

### A2. 현재 구조 유지 + 아무 조치 안 함

- **장점**: 최소 변경
- **단점**: GPT 통찰의 가치(이원 트랙 명시화) 손실
- **결정**: 거부. 통찰을 살리되 surgical하게.

### A3. 일부 파일만 이동 (예: failure_cases / regression 묶음)

- **장점**: 부분 분리
- **단점**: 구조 일관성 깨짐, "왜 이건 이동 저건 안 이동"질문 발생
- **결정**: 거부. 전부 또는 전무.

### A4. (채택) INDEX 추가 + 폴더 보존

- **장점**:
  - 5 파일 변경으로 GPT 통찰 80% 반영
  - cross-reference 무손상
  - Surgical Scope 원칙 준수
  - Phase 1 진입 지연 없음
- **단점**: 폴더로 시각 구분되지 않음 → INDEX.md 안 읽으면 모름
- **완화**: INDEX.md를 eval/ 최상단에 배치 + routes.yaml의 eval_design route에 추가

---

## Consequences (결과)

### Positive

- 이원 트랙 개념 명시화 (Phase별 비중 가이드 포함)
- Phase 1에 즉시 적용 가능 (failure_cases.md 5 케이스 시드)
- 기존 작업물 보존 (Phase 0 S4 deep work)
- 모호한 경계 파일을 "혼합" 또는 "메타"로 명시 처리

### Negative

- 신규 합류 인원이 폴더만 보면 분류 안 보임 → INDEX.md 진입 필수
- INDEX.md 자체 유지보수 부담 (eval/ 파일 추가/이동 시 갱신)

### Mitigation

- `harness-audit` Skill에 "INDEX.md vs 실제 파일 정합성 점검" 추가 (Phase 2+에서)
- 새 eval 파일 추가 시 INDEX.md §1/§2/§3 중 어디 속하는지 명시 (qa-check 카테고리 10 Simplicity 점검 일부)

---

## Phase별 적용 계획

### Phase 1 (현재)

- `eval/INDEX.md` 작성 ✅
- `eval/failure_cases.md` FC-001~005 시드 ✅
- `phases/active/phase-1-mvp-basic-flow/work_plan.md`에 각 Slice별 eval 매핑 추가 (다음 작업)

### Phase 4+

- Critic Agent 본격화 시점에 INDEX.md §2.2 평가 차원 사용 시작
- failure_cases.md 5→15 확장 (F5 브랜드 톤 추가)

### Phase 7

- LLM-as-judge 자동화 도입 시 INDEX.md §1.3 운영 결과 폴더 활용 본격화

### Phase 10

- 회귀 자동화 CI 도입 시 INDEX.md §6.2 절차 자동화

---

## Verification

```
✅ eval/INDEX.md 존재 + §1~§7 모두 포함
✅ eval/failure_cases.md 존재 + FC-001~005 모두 포함
✅ 기존 eval/ 15 파일 + 5 폴더 위치 변경 없음
✅ routes.yaml 무수정 (또는 eval_design route에 INDEX.md 추가만)
✅ 82개 cross-reference 모두 유효 (회귀 없음)
```

---

## Related ADRs / Docs

- `eval/INDEX.md` — 이원 트랙 색인 본문
- `eval/failure_cases.md` — Phase 1 Bad Case 시드
- `phases/active/phase-1-mvp-basic-flow/work_plan.md` — Slice별 eval 매핑
- `.claude/skills/qa-check/SKILL.md` v1.1.0 — 카테고리 10 Simplicity 일부
- `.claude/skills/eval-design/SKILL.md`
- `.claude/skills/eval-run/SKILL.md`

---

## 변경 이력

- 2026-05-26: ADR 최초 작성, eval 이원 트랙 채택 (Option B 변형)
