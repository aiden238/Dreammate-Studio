# validation_workflow.md — 하네스 검증 6 절차

> 위치: `harness/meta_factory/validation_workflow.md`
> 상태: Phase M0 (Meta-Factory Prep, ★ meta-phase) Slice 2 — 생성 하네스 검증 기준
> 결정: ADR-035
> 참조: generation_workflow.md (단계 9 에서 본 절차 호출), harness_blueprint_schema.md (validation 필드), factory_contract.md (규칙 4/5/7), `.claude/skills/eval-run/SKILL.md` (★ §5 eval-run 연동 — §3~§6 cross-ref), `.claude/skills/INDEX.md` (Skill 충돌 규칙 + 우선순위 표)
> ★ 런타임 변경 0 (A9) — 본 검증은 blueprint 를 평가할 뿐 L1/L2 를 수정하지 않는다.

---

## 0. 이 문서의 위치

`validation_workflow.md` 는 generation_workflow(단계 9)가 산출한 blueprint 를 **6 검증**으로 평가한다. 생성된 harness 는 6 검증을 통과하기 전까지 **active 로 간주하지 않는다** (factory_contract 규칙 7). 검증은 통과/실패가 아니라 **각 차원의 pass / fail / pending** 으로 기록한다.

★ 본 절차는 기존 운영 Skill 과 명시적으로 연결된다:
- 검증 5 (eval-run 연동)는 **`eval-run` Skill §3~§6** 절차를 그대로 cross-ref 한다 (별도 평가 체계를 새로 만들지 않음).
- 검증 2 (skill conflict)는 **`.claude/skills/INDEX.md`** 의 "같은 description 키워드 둘 이상 = 충돌" 규칙 + 우선순위 표를 따른다.
- 검증 3 (contract consistency)는 **`contract-change` Skill** 의 정합성 점검 정신을 따른다.

---

## 1. 6 검증 개요

```
1. trigger validation        — 필요 Skill 이 켜지는가 / 켜지면 안 되는 Skill 이 안 켜지는가
2. skill conflict check      — description keyword 충돌 / 우선순위 표 편입 가능
3. contract consistency      — contract ↔ 구현/형제 contract cross-ref 정합
4. with-skill / without-skill comparison — 적용 전/후 결과 (누락률 / 품질 / 일관성)
5. eval-run 연동 (★)         — golden_set 회귀 / schema 준수율 / 평균 점수 / 비용·latency / human_review_needed
6. generated harness acceptance — 최소 파일 구조 / 금지 범위 / phase 구조 / eval gate / rollback·retrospective 경로
```

> blueprint.validation 의 3 필드(trigger_validation / contract_consistency / with_without_skill_eval)는 검증 1·3·4 에 대응. 검증 2·5·6 은 본 절차에서 추가 기록.

---

## 2. 검증 상세

### 검증 1 — trigger validation

> **질문: 필요한 Skill 이 켜지는가? 켜지면 안 되는 Skill 이 안 켜지는가?**

- **대상**: blueprint.skills[].trigger_keywords + agents[] 트리거.
- **절차**:
  1. 각 의도된 작업 상황(예: "contract 변경", "평가 실행", "phase 진입")에 대해 **켜져야 할 Skill** 이 description 키워드 매칭으로 트리거되는지 dry-run 확인.
  2. 각 무관한 상황(예: 일상 대화, 범위 밖 요청)에 대해 **켜지면 안 되는 Skill** 이 트리거되지 **않는지** 확인 (false trigger 0).
  3. agent 트리거(분기 조건)가 architecture_pattern 과 정합하는지 확인 (예: supervisor 패턴 → agent 직접 호출 트리거 부재).
- **판정**: 켜져야 할 것 100% 트리거 AND 켜지면 안 될 것 0 false trigger → pass.
- **기록**: blueprint.validation.trigger_validation = pass / fail / pending.

### 검증 2 — skill conflict check

> **질문: description 키워드가 충돌하는가? 우선순위 표에 편입 가능한가?**

- **대상**: blueprint.skills[] + 기존/형제 Skill 키워드.
- **절차** (`INDEX.md` Skill 충돌 규칙 정합):
  1. **키워드 중첩 검사**: 같은 description 키워드가 둘 이상 Skill 에 있으면 충돌 — 즉시 수정 (INDEX §사용 원칙 5).
  2. **scoping 확인**: 신규 Skill 키워드가 기존 Skill 의 소유 키워드를 침범하지 않는지 (scoped 키워드 권장).
  3. **우선순위 표 편입**: 두 Skill 이 동시 매칭될 수 있으면 우선순위 표(INDEX §우선순위 충돌 해결)에 관계를 추가 가능한지 확인 (예: `audit > factory`, `contract-change > 다른 절차`).
- **판정**: 키워드 충돌 0 AND 우선순위 표 편입 가능 → pass.
- **기록**: 충돌 항목 + 우선순위 관계를 검증 리포트에 명시.

### 검증 3 — contract consistency

> **질문: contract ↔ 구현/형제 contract 의 cross-reference 가 정합하는가?**

- **대상**: blueprint.contracts[] + agents IO + output 형식.
- **절차** (3 정합 축 — `contract-change` 정신):
  1. **prompt_registry ↔ output_schema**: prompt 가 산출하는 출력 본문이 output_schema 에 정의되어 있는가.
  2. **api_contract ↔ frontend·api client**: API 응답 필드가 프론트엔드 타입/클라이언트와 1:1 매핑되는가.
  3. **db_schema ↔ migration**: DB 스키마(테이블/컬럼/JSONB)가 migration 과 일치하는가.
  - + agent_io ↔ agents[] IO 정합 (입력/출력/forbidden_actions).
- **판정**: 3 축 + agent_io 모두 cross-ref 일치 → pass.
- **기록**: blueprint.validation.contract_consistency = pass / fail / pending. drift 발견 시 항목 명시 (sub-agent 분산 작성 drift 사후 발견 위험 = 기존 P-DRIFT-001 정합).

### 검증 4 — with-skill / without-skill comparison

> **질문: Skill 적용 전/후 결과가 어떻게 달라지는가? (누락률 / 품질 / 일관성)**

- **대상**: blueprint.skills[] 의 효용.
- **절차**:
  1. 동일 입력 케이스에 대해 **Skill 미적용(without)** 결과와 **Skill 적용(with)** 결과를 비교.
  2. 3 지표 측정:
     - **누락률**: Skill 이 강제하는 절차 단계(예: 충돌 검토 / 회귀 평가 / 승인 게이트)의 누락 빈도 — with < without 기대.
     - **품질**: 산출물 품질 점수(검증 5 eval-run 차원 활용) — with ≥ without 기대.
     - **일관성**: 반복 실행 시 결과 편차 — with 가 더 낮은 편차 기대.
  3. Skill 추가가 효용을 입증하지 못하면(with ≈ without) Skill 도입 재검토 (YAGNI 차단).
- **판정**: with 가 without 대비 누락률↓ / 품질≥ / 일관성↑ → pass.
- **기록**: blueprint.validation.with_without_skill_eval = pass / fail / pending.

### 검증 5 — eval-run 연동 (★)

> **질문: 생성 하네스의 eval 이 `eval-run` Skill 절차로 평가 가능하고 임계값을 만족하는가?**
> ★ 본 검증은 **`eval-run` Skill §3~§6** 을 cross-ref 한다 — meta_factory 는 별도 평가 체계를 만들지 않는다.

- **대상**: blueprint.evals[] + 산출물 샘플.
- **절차** (`eval-run` SKILL.md cross-ref):
  1. **§3 실행**: golden_set 케이스를 모델에 입력해 출력 수집 (신구 비교 시 비교 모드).
  2. **§4 채점**: schema 준수율(100% 필수) + 품질 차원 자동 채점 + 다양성(cosine similarity).
  3. **§5 결과 저장**: `eval/regression_results/{trigger}_{YYYY-MM-DD-HHMM}.md` 형식 — 요약 점수 표(schema 준수율 / 평균 점수 / 비용 / latency / 토큰) + 케이스별 결과 + 임계값 점검 + 결정(pass / fail / human_review_needed).
  4. **§6 임계값 판정**:
     - schema 준수율 < 100% → 즉시 fail, rollback.
     - 평균 점수 하락 > 0.3 → fail, 사람 검토.
     - 비용 증가 > 30% → cost-review 트리거.
     - latency 증가 > 20% → 경고.
     - 차단 단어 검출 > 0% → fail.
- **연동 차원 (★ 5)**: golden_set 회귀 / schema 준수율 / 평균 점수 변화 / 비용·latency / human_review_needed.
- **판정**: §6 임계값 위반 0 → pass. 위반 시 eval-run §6 의 자동 차단 + 후속 Skill 위임 절차를 따른다.
- **기록**: eval-run §5 형식 리포트 경로 + 결정(pass / fail / human_review_needed) 명시.
- **우선순위**: `eval-run > harness-factory validation` (INDEX 우선순위 표) — 평가 실행 자체는 eval-run 절차가 상위.

### 검증 6 — generated harness acceptance

> **질문: 생성 하네스가 최소 수락 기준을 만족하는가?**

- **대상**: 생성 harness 전체 구조.
- **수락 체크리스트**:
  1. **최소 파일 구조**: 라우터(AGENTS/CLAUDE 형식) + 상태(PROJECT_STATE 형식) + contracts + phases + eval + skills 디렉토리 존재.
  2. **금지 범위 명확**: domain_brief.forbidden_scope → phases[].non_goals + 라우터 금지 행동에 매핑됨 (scope creep 차단).
  3. **phase 구조**: phase entry 8 files(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) 형식 + acceptance 기준 존재.
  4. **eval gate**: 검증 5 의 임계값 게이트가 phase 종료/배포 전 차단 기준으로 연결됨.
  5. **rollback·retrospective 경로**: 실패 시 되돌림(rollback) 경로 + 종료 후 회고(retrospective) 경로가 정의됨 (기존 rollback_policy / meta-retrospective 정신 정합).
- **판정**: 5 항목 모두 충족 → pass.
- **기록**: 미충족 항목을 outputs/improvement_reports/ 에 보완 제안으로 명시.

---

## 3. 검증 ↔ Skill / 우선순위 매핑

| 검증 | 핵심 질문 | 연동 Skill / 문서 | blueprint 필드 |
|---|---|---|---|
| 1 trigger validation | 필요 Skill 켜지는가 | INDEX (트리거 매칭) | trigger_validation |
| 2 skill conflict | 키워드 충돌 0 | INDEX (충돌 규칙 + 우선순위 표) | — |
| 3 contract consistency | cross-ref 정합 | contract-change | contract_consistency |
| 4 with-without comparison | Skill 효용 | (누락률/품질/일관성) | with_without_skill_eval |
| 5 eval-run 연동 ★ | 임계값 만족 | **eval-run §3~§6** | — (eval-run 리포트) |
| 6 acceptance | 최소 기준 충족 | rollback_policy / meta-retrospective | — |

**우선순위 (INDEX 정합)**: `eval-run > harness-factory validation`, `contract-change > harness-factory`, `harness-audit > harness-factory`. 즉 검증 5 의 실 평가는 eval-run 이, 검증 3 의 실 contract 반영은 contract-change 가 상위 절차를 소유한다.

---

## 4. 판정 종합

```
6 검증 전부 pass         → blueprint.validation 3 필드 pass + 사용자 승인 게이트(generation_workflow 단계 11)로 인계
하나라도 fail            → blueprint 는 active 아님 (factory_contract 규칙 7) — outputs/ 에 머무르며 보완
human_review_needed (검증 5) → 사람 검토 완료 후 재판정
```

- 검증 결과는 blueprint 와 함께 `outputs/generated_harnesses/` 에 보관.
- 보완 제안은 `outputs/improvement_reports/` 또는 `meta/proposals/` 에 기록 (proposal-first).
- ★ 어떤 검증 결과도 기존 하네스(L2)/런타임(L1)을 자동 수정하지 않는다 (A9 + factory_contract 규칙 1/2).

---

## 5. 다음 단계

6 검증 전부 pass → `generation_workflow.md` 단계 11 (사용자 승인) → (승인 시) active 전환. 검증 5 의 eval-run 연동 상세는 `.claude/skills/eval-run/SKILL.md` §3~§6, Skill 충돌 규칙은 `.claude/skills/INDEX.md` 를 본다.
