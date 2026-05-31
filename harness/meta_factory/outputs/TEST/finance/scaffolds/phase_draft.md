# phase_draft — phase-F0-foundation (scaffold, 8 entry files)

> 위치: `harness/meta_factory/outputs/TEST/finance/scaffolds/phase_draft.md`
> 상태: Phase M3 Slice S1 — phase scaffold dry-run
> 형식: `meta_factory/templates/phase_template.md` (8 entry files)
> ★ phase 등록은 사용자 승인 후 (proposal-first). 본 scaffold 는 설계 초안 — active phases/ 아님.

---

## 0. 사용 template

generation_workflow 단계 7 산출. phase_template.md 8 entry files 형식으로 첫 phase(F0-foundation) 초안. ★ domain_brief.forbidden_scope → non_goals 매핑(특히 도메인 자체 금지 = 규제).

---

## phase-F0-foundation (8 entry files 초안)

### goals.md
```markdown
# phase-F0-foundation — Goals
- 데이터 계층 설계 (User → Household → FinancialGoal → Plan → Allocation)
- output_schema / db_schema / agent_io_contract / llm_security 초안
- ★ 제3자 PII 엔티티(dependents/beneficiary) 마스킹 설계 (risk high)
- 비자문 디스클레이머 필드 설계 (forbidden_scope 도메인 금지 정합)
```

### scope.md
```markdown
# phase-F0-foundation — Scope
## 포함 (In-Scope)
| 파일/영역 | 작업 |
|---|---|
| docs/contracts/output_schema.md | 신규 (FinancialPlan/DebtPlan/InsuranceReview/Critic) |
| docs/contracts/db_schema.md | 신규 (5계층 + dependents/beneficiary/debts) |
| docs/contracts/llm_security.md | 신규 (금융 PII + 제3자 PII + 자문 발화 차단) |
## ★ 절대 수정 금지 (forbidden)
- backend/fastapi/** (런타임 — A9)
- 투자 알고리즘/실 금융 로직 구현 (forbidden_scope — 설계만)
```

### non_goals.md          # ★ forbidden_scope 매핑
```markdown
# phase-F0-foundation — Non-Goals
| ID | 항목 | 사유 |
|---|---|---|
| NG1 | 투자 자문/권유 | ★ 도메인 자체 금지 (규제) — forbidden_scope |
| NG2 | 원금 보장/수익률 약속 | ★ 도메인 자체 금지 — forbidden_scope |
| NG3 | 특정 금융상품/종목 추천 | ★ 도메인 자체 금지 — forbidden_scope |
| NG4 | 세무/법률 자문 | ★ 도메인 자체 금지 — forbidden_scope |
| NG5 | 실제 거래/계좌 연동 | 외부 액션 — forbidden_scope |
| NG6 | 부채/보험 모듈 (F2) | 후속 phase — scope creep 차단 |
```

### dependencies.md
```markdown
# phase-F0-foundation — Dependencies
- 선행 phase: 없음 (첫 phase)
- 외부 의존: 없음 (런타임 미생성 — 설계만)
- 후속: F1-mvp-planning 이 본 contract 초안에 의존
```

### acceptance.md         # ★ eval-run 임계값 연결
```markdown
# phase-F0-foundation — Acceptance
| ID | 기준 | 검증 방법 |
|---|---|---|
| A1 | 4 contract 초안 존재 | 파일 점검 |
| A2 | db_schema ↔ output_schema cross-ref 0 drift | agent-io-check / 수동 cross-ref |
| A3 | dependents/beneficiary 마스킹 설계 명시 | security-review (★ risk high 강제) |
| A4 | 비자문 디스클레이머 필드 정의 | output_schema 점검 + advisory_boundary 게이트 설계 |
```

### assumptions.md
```markdown
# phase-F0-foundation — Assumptions
- runtime_type product_saas 가정 (Dreammate 동형) — 4-check: 검증 가능 ✅
- risk high 확정 (G5 트리거) → security-review 강제 — 4-check: 근거 명확 ✅
- 단일 planning agent 파라미터화 (G1 결정) — 4-check: §1.2 4축 근거 ✅
```

### multi_slice_plan.md
```markdown
# phase-F0-foundation — Multi-Slice Plan
## Wave 구조
- Slice 1 [output_schema + db_schema] → Slice 2 [agent_io + llm_security] → Slice 3 [cross-ref 검증]
## 충돌 매트릭스
| Slice | docs/contracts | eval/ |
|---|---|---|
| S1 | output_schema, db_schema | — |
| S2 | agent_io, llm_security | — |
| S3 | (읽기 검증) | golden_set 초안 |
```

### notes.md
```markdown
# phase-F0-foundation — Notes
## Entry (dry-run)
- 본 phase 는 dry-run blueprint 산출 (harness_status: dry-run-blueprint, G7) — 실 진입은 사용자 승인 후.
## Rollback / Retrospective (validation_workflow 검증 6)
- rollback: contract 초안은 git revert 로 되돌림 (런타임 0 변경 → 안전).
- retrospective: phase 종료 시 meta-retrospective Skill (제3자 PII·자문 경계 설계 회고).
```

---

## 작성가이드 점검 (phase_template §작성가이드)

1. ✅ non_goals.md 필수 — forbidden_scope 7항(특히 도메인 금지 4항)을 NG1~NG6 매핑. scope creep + 규제 차단.
2. ✅ acceptance.md 필수 — A3 에 security-review(risk high 강제), A4 에 advisory_boundary 게이트 연결.
3. ✅ scope.md forbidden — 런타임/실 금융 로직 침범 금지 (A9 + P-AGENT-SCOPE-001).
4. ✅ multi_slice_plan 충돌 매트릭스 — Slice 간 파일 충돌 0.
5. ✅ assumptions 4-check — G1/G5 결정 근거 점검.
6. ✅ rollback·retrospective 경로 (검증 6) — notes 에 명시.

## ★ 메모 (이질 도메인 phase 구조)

- **팟캐스트(M1) 대비**: 동일한 8 entry files 골격. 차이는 non_goals 가 **규제성 도메인 금지(투자자문/원금보장)**를 NG 로 받는다는 점 — phase_template 이 "scope creep 차단"과 "규제 금지"를 같은 non_goals 표로 수용함을 확인(NEW-G9 후보: 두 종류 구분 필드 부재).
- 5 phase(F0~F4) 전체 흐름은 blueprint §6 참조. 본 scaffold 는 첫 phase 만 8 files 로 시연.

---

이 scaffold 는 phase_template 을 이질 도메인(재무)에 적용 (dry-run, active phases/ 아님 — 사용자 승인 전).
