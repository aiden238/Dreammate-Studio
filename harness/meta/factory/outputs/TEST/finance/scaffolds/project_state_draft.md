# project_state_draft — personal_finance_planning_harness (scaffold, ★ G7 harness_status)

> 위치: `harness/meta_factory/outputs/TEST/finance/scaffolds/project_state_draft.md`
> 상태: Phase M3 Slice S1 — PROJECT_STATE scaffold dry-run
> 형식: `meta_factory/templates/project_state_template.md` 개선본 (harness_status enum)
> ★ PROJECT_STATE 는 사용자 승인 없이 갱신하지 않는다 (factory_contract 규칙 6). 본 scaffold 는 설계 초안 — active PROJECT_STATE.md 아님.

---

## 0. 사용 template

generation_workflow 단계 8 산출. project_state_template.md(migration_progress yaml + confirmed_decisions)로 생성 하네스 상태 문서 초안. ★ **G7 harness_status: dry-run-blueprint** 슬롯 행사.

---

## (초안) PROJECT_STATE — personal_finance_planning_harness

```markdown
# PROJECT_STATE (생성 하네스 — dry-run blueprint)

## 현재 상태
개인 재무 플래닝 AI 하네스의 **생성 dry-run blueprint**. M3(이질 도메인 dry-run) Slice S1 에서 generation_workflow 11단계로 설계됨. ★ active 하네스가 아니라 outputs/TEST/finance/ 에 격리된 검증용 산출.

## 현재 Active Phase
**(active phase 없음 — dry-run blueprint)** — 실 phase 진입은 사용자 승인 후 별도.

## confirmed_decisions
```
1. runtime_type: product_saas (FastAPI/Next/DB 가정 — Dreammate 동형)
2. risk_level: high (★ G5 제3자 PII 트리거 — 부양가족/수익자 + 금융 민감정보 → medium→high 상향)
3. architecture: supervisor 주 + fan_out_fan_in/producer_reviewer/pipeline 보조 (★ G1 — expert_pool 미채택, 단일 planning 파라미터화)
4. skills: 신규 0 / 재사용 강제 (★ G2 — security-review high 강제 포함)
5. forbidden_scope: 투자자문/원금보장/상품추천/세무·법률자문 (★ 도메인 자체 금지 — 규제)
```

## migration_progress
\`\`\`yaml
harness_status: dry-run-blueprint        # ★ G7 — 이 하네스의 1급 상태 (active 아님)
                                         #   active            : 실 운용 (기본값)
                                         #   dry-run-blueprint : ★ 본 케이스 — 생성·검증 dry-run 산출 (outputs/ 격리, 사용자 승인 전 active 전환 금지)
                                         #   proposal          : 승인 대기 제안
current_sprint: "phase-M3-slice-S1"
current_sprint_step: "S1 finance harness generation"
total_steps_in_sprint: 2                 # S1 generation + S2 validation
last_completed_action: "generation_workflow 11단계 적용 → domain_brief + blueprint + 6 scaffold (이질 도메인)"
next_action: "S2 — validation_workflow 6검증 + with/without 비교 (별도 slice)"
blocker: null
phase_M3_status: active                  # meta-phase (dry-run)
phase_F0_status: planned                 # 실 재무 하네스 phase (사용자 승인 후)
\`\`\`

## baseline
- ★ 본 하네스는 dry-run-blueprint → 실 test/eval baseline 없음 (validation 은 S2 가 pending/pending-by-design 으로 수행).
- 기존 Dreammate baseline(pytest/P-X1/Skill)은 본 dry-run 과 무관 불변 (런타임 0 변경 — factory_contract 규칙 1).
```

---

## 작성가이드 점검 (project_state_template §작성가이드)

1. ✅ migration_progress yaml — current_sprint/last_completed/next_action/blocker 최신.
2. ✅ confirmed_decisions 누적 — domain_brief 선택(runtime_type/risk_level high/forbidden_scope) 포함.
3. ✅ **harness_status enum (G7)** — `dry-run-blueprint` 명시. confirmed_decisions 에 "(제안)" 수동 표기하던 우회를 status 슬롯으로 대체. dry-run-blueprint = active 아님 → outputs/ 격리 + 사용자 승인 전 active 전환 금지 (규칙 5·6 정합).
4. ✅ baseline 명시 — dry-run 이므로 실 baseline 없음(validation S2).
5. ✅ 사용자 승인 게이트 (규칙 6) — 본 초안은 outputs/TEST/finance/ 에만, active PROJECT_STATE.md 미갱신.

## ★ G7 적용 메모

- **팟캐스트(M1/M2) 대비**: 동일하게 dry-run-blueprint 상태. 재무는 추가로 `phase_F0_status: planned`(실 phase 는 승인 후)로 dry-run blueprint ↔ 실 phase 분리를 명시 → harness_status 가 "생성물 격리 상태"를 1급으로 표현함을 이질 도메인에서 재확인.
- harness_status 슬롯이 없었다면 risk high·규제 도메인 하네스가 outputs/ 격리임을 confirmed_decisions 주석으로만 표기해야 했을 것 — G7 이 격리 의도를 구조적으로 보존.

---

이 scaffold 는 project_state_template 개선본(G7 harness_status)을 이질 도메인(재무)에 적용 (dry-run, active PROJECT_STATE.md 아님 — 규칙 6).
