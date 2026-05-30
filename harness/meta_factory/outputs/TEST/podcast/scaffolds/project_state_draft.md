# project_state_draft.md — PROJECT_STATE scaffold (팟캐스트)

> 위치: `harness/meta_factory/outputs/TEST/podcast/scaffolds/project_state_draft.md`
> 기반: `meta_factory/templates/project_state_template.md`
> 상태: Phase M1 S1 dry-run scaffold (active 아님 — ★ PROJECT_STATE 는 사용자 승인 없이 갱신 금지, 규칙 6)

---

## 채운 scaffold (project_state_template placeholder → 팟캐스트)

```markdown
# PROJECT_STATE

## 현재 상태
팟캐스트 에피소드 기획 AI 하네스는 dry-run blueprint 단계다. domain_brief + harness_blueprint +
6 scaffold 가 outputs/TEST/podcast/ 에 격리 생성되었고, validation 6검증(S2)은 미수행(pending).
active 런타임 없음 — 설계 청사진만 존재.

## 현재 Active Phase
**🟡 (dry-run) phase-P1-mvp-planning 설계됨** — intent+planning+critic+rewriter MVP. ★ 아직 active 진입 전(사용자 승인 게이트).

## confirmed_decisions          # 사용자 확정 결정 누적 (★ dry-run 이므로 제안 상태)
```
1. domain_name: podcast_episode_planning_ai (제안)
2. runtime_type: product_saas (제안)
3. risk_level: medium — 게스트 제3자 PII 고려 시 high 재검토 여지 (GAP G5, 제안)
4. architecture_pattern: supervisor 주 + fan_out_fan_in/producer_reviewer/pipeline 보조; expert_pool 미채택 (제안)
5. 신규 Skill 0 — 기존 21 Skill 재사용 (제안, S2 with-without 검증)
6. forbidden_scope: 오디오 제작/TTS/게스트 섭외/배포/자동 promotion/Show Memory (제안)
```

## migration_progress
\`\`\`yaml
harness_status: dry-run-blueprint   # ★ M2 G-fix 적용 (G7 — project_state_template enum: active|dry-run-blueprint|proposal). 이 하네스의 1급 상태 = 생성·검증 dry-run 산출 (active 아님, outputs/ 격리). M1 의 custom 키 podcast_harness_status / confirmed_decisions "(제안)" 수동표기를 표준 enum 슬롯으로 대체. 생략 시 = active(backward-compat).
current_sprint: "phase-M1-slice-S1"
current_sprint_step: "generation dry-run (without baseline + with blueprint + 6 scaffold)"
total_steps_in_sprint: 6
last_completed_action: "harness_blueprint + 6 scaffold 작성 (outputs/TEST/podcast/)"
next_action: "S2 — validation_workflow 6검증 + with/without 6지표 비교 + 5 gap 재현"
blocker: null
phase_M1_status: active        # meta-phase (sample test)
podcast_harness_status: dry-run-blueprint   # (M1 원본 custom 키 — 보존. 표준 슬롯은 위 harness_status)
\`\`\`

## baseline
- dry-run — 런타임 test 0 (설계 단계). 회귀 0 기준은 S2 validation 결과로 정립.
- ★ 본 PROJECT_STATE 는 outputs/TEST/ 격리본 — 실 PROJECT_STATE.md 는 변경 0 (규칙 6).
```

---

## 작성 가이드 점검 (project_state_template §작성가이드)

1. ✅ migration_progress yaml — current_sprint/last_completed_action/next_action/blocker 최신화.
2. ✅ confirmed_decisions 누적 — domain_brief 선택(runtime_type/risk_level/forbidden_scope) 포함 (단 dry-run → "제안" 표기).
3. ✅ active phase 1개 원칙 — phase-P1 만 (나머지 planned).
4. ✅ baseline 명시 — dry-run 이므로 test 0 + S2 에서 정립.
5. ★ 사용자 승인 게이트 — 본 draft 는 outputs/TEST/ 격리본. 실 PROJECT_STATE.md 0줄 변경 (factory_contract 규칙 6 준수).
6. archive 경로 — 해당 단계 아님(dry-run).

## ★ GAP 관찰

project_state_template 은 단일 active 하네스 전제. dry-run("active 아님, 제안 상태")을 표현하는 status 값
(dry-run-blueprint / 제안 표기)이 template 에 명시적 슬롯 없음 → confirmed_decisions 에 "(제안)" 수동 표기로 우회.
S2 관찰점(meta-phase 의 상태 표현).

### ✅ M2 G-fix 해소 (G7, S3 re-validate)
- S2 가 `project_state_template.md` migration_progress 에 `harness_status` enum(active / dry-run-blueprint / proposal) 슬롯을 추가 → 위 migration_progress 에 표준 `harness_status: dry-run-blueprint` 적용.
- 해소 판정: **addressed** — 하네스 상태가 1급 enum 으로 표현됨. confirmed_decisions 의 "(제안)" 수동 표기와 custom 키(podcast_harness_status) 우회를 표준 슬롯이 대체. `dry-run-blueprint`/`proposal` 은 active 아님 → outputs/ 격리 + 승인 전 active 전환 금지(규칙 5·6) 와 정합. 생략 시 active(backward-compat).
