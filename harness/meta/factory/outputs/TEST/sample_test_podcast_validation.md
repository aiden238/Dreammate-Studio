# sample_test_podcast_validation.md — Phase M1 Slice S2 검증 리포트

> 위치: `harness/meta_factory/outputs/TEST/sample_test_podcast_validation.md`
> 상태: Phase M1 (Meta-Factory Sample Test) Slice S2 — validation (S1 산출 blueprint 평가)
> 입력(읽기 전용): `outputs/TEST/podcast/{harness_blueprint.md, _without_baseline.md, domain_brief.md, scaffolds/*}`
> machinery: `meta_factory/validation_workflow.md`(6검증) + `factory_contract.md` + `harness_blueprint_schema.md`
> Skill cross-ref: `.claude/skills/eval-run/SKILL.md`(검증5) + `.claude/skills/INDEX.md`(검증2)
> baseline: `meta_factory/blueprints/dreammate_current_harness_blueprint.md` §10 부족점 5
> ★ 목적: "성공" 이 아니라 **machinery 가 검증 가능한가 + GAP 발견**. fail/pending 은 정상 결과.
> ★ 런타임 0 (A9) — 실 LLM 호출 / 실측 점수 없음. 본 리포트는 blueprint 문서를 평가할 뿐.

---

## 0. 요약 (TL;DR)

| 항목 | 결과 |
|---|---|
| 6검증 분포 | **PASS 3 (검증1·2·6) / PENDING 1 (검증5, 정상) / GAP-flagged PASS 1 (검증3, drift 0 but 조건부축 부재) / GAP-flagged PASS 1 (검증4, with≫without 입증 but 소표본)** |
| with/without 6지표 | WITH 우세 5지표 / PENDING 1지표(품질·일관성 = 소표본) — 아래 §B |
| 5 gaps 재현 | 재현 5 / 부분 0 / 비재현 0 (전 부족점이 팟캐스트 dry-run 에서 재현됨) |
| GAP 총개수 | **8** (S1 G1~G6 재평가 + 신규 G7·G8) |
| blueprint validation 3필드 최종값 | trigger_validation=**pass** / contract_consistency=**pass** / with_without_skill_eval=**pass** |
| 금지 위반 | **0** — proposal-first 준수, outputs/TEST/ 외 변경 0 |

> ★ blueprint 가 6검증을 통과해도 **사용자 승인 전 active 아님** (factory_contract 규칙 7, generation_workflow 단계 11). S2 는 검증만 수행하며 active 전환을 하지 않는다.

---

## A. 6 검증 실행 (validation_workflow.md 그대로)

### 검증 1 — trigger validation → **PASS**

> 질문: 필요한 Skill/agent 가 의도 상황에 켜지고, 무관 상황에 안 켜지는가.

**(a) 켜져야 할 Skill 이 켜지는가 (description 키워드 매칭 dry-run)**

| 의도 작업 상황 | 켜져야 할 Skill | 트리거 키워드 매칭 | 결과 |
|---|---|---|---|
| contract/스키마 변경 | contract-change | "contract 변경"/"schema 변경" (blueprint §3) | ✅ 켜짐 |
| 평가 실행 (PE-001~ 회귀) | eval-run | "eval 실행"/"golden_set"/"regression" | ✅ 켜짐 |
| 7 agent IO drift 검사 | agent-io-check | "agent IO 점검"/"agent_io_contract"/"I/O 검증" | ✅ 켜짐 |
| phase 진입/종료 | phase-start / phase-complete | (재사용, blueprint §7 라우터 안내) | ✅ 켜짐 |
| 회고/개선 | meta-retrospective | (재사용) | ✅ 켜짐 |

**(b) 켜지면 안 되는 Skill (false trigger 0)**

- blueprint 는 **신규 Skill 0** (§3). 따라서 신규 키워드로 인한 false trigger 발생 경로 자체가 없음 → false trigger **0**.
- 일상 대화 / 범위 밖(오디오 녹음·TTS·RSS 업로드)은 어떤 Skill description 키워드와도 매칭되지 않음 → false trigger 0.

**(c) agent 트리거 ↔ architecture_pattern 정합 (supervisor)**

- 7 agent **전부** forbidden_actions 에 "다른 agent 직접 호출 (orchestrator 경유)" 명시 (blueprint §2, agent_draft §critic). → supervisor 패턴에서 "agent 직접 호출 트리거 부재" 요구(validation_workflow 검증1 절차 3) **충족**.
- 조건부 agent(guest_brief/question/shownotes)는 모드 분기 트리거인데, 이 분기는 orchestrator 가 소유 → agent 자율 트리거 없음 = supervisor 정합.

**판정 근거**: 켜져야 할 것 100% 트리거 (재사용 Skill 매칭 정상) AND 켜지면 안 될 것 0 false trigger (신규 0 → 신규 키워드 0) AND agent 트리거 supervisor 정합 → **PASS**.
> ⚠ 단서: dry-run 정적 검사(키워드 문자열 대조)로 판정. 실 Claude Code 자동 트리거 행위는 실행 미수행 → "정적 정합 PASS, 런타임 트리거 실측 미수행".

---

### 검증 2 — skill conflict check → **PASS** (단, S1 시연 충돌은 "회피된 충돌"로 기록)

> 질문: blueprint 제안 Skill 키워드가 기존 21 Skill description 키워드와 충돌하는가 (INDEX 규칙).

**(a) 채택 Skill 의 충돌 (실제 blueprint)**

- blueprint 가 **채택**한 Skill 은 전부 기존 21 Skill 재사용 (contract-change / eval-run / agent-io-check + 라우터 안내 절차 Skill). 신규 키워드 도입 0 → INDEX §사용원칙 5("같은 description 키워드 둘 이상 = 충돌") 위반 **0**.

**(b) S1 이 시연한 충돌 (skill_draft §A — 채택 안 함)**

- S1 은 `podcast-eval-run` 신규 Skill 을 **반례 시연**으로 제시했다. 그 키워드 vs 기존 `eval-run`:

| podcast-eval-run 키워드 | eval-run (#6) 소유 키워드 | 충돌 |
|---|---|---|
| "eval 실행" | "eval 실행" | ❌ **충돌 (동일)** |
| "golden_set" | "golden_set" | ❌ **충돌 (동일)** |
| "regression" | "regression" | ❌ **충돌 (동일)** |
| "품질 평가" | "품질 평가" | ❌ **충돌 (동일)** |

→ **4 키워드 100% 중첩**. machinery(INDEX 충돌 규칙 + factory_contract 규칙 4)가 이 충돌을 **정확히 검출**했고, S1 은 이를 근거로 채택을 거부했다. **= machinery 가 작동한 지점.**

**(c) 우선순위 표 편입**

- 채택 Skill 0 신규 → INDEX 우선순위 표 변경 불필요.
- (가정) 만약 podcast-eval-run 을 강행했다면 INDEX 우선순위 표에 편입 **불가** (eval-run 과 키워드가 동일하여 scoping 으로 분리 불가) → 채택 거부가 유일한 옳은 결론. machinery 가 이 판단을 강제.

**판정 근거**: 채택 Skill 키워드 충돌 **0** AND machinery 가 반례(podcast-eval-run 4중첩)를 정확히 검출하여 사전 차단 → **PASS** (신규 Skill 0 권장이 검증을 통과).

---

### 검증 3 — contract consistency → **PASS** (cross-ref drift 0, ★ 단 "조건부 산출" 축 부재 = GAP)

> 질문: prompt↔output / api↔front / db↔migration / agent_io↔agents[] cross-ref 가 정합하는가. 누락 항목 개수 집계.

**4 정합 축 점검** (blueprint §4.1 + contract_draft §3):

| # | 정합 축 | blueprint 상 정의 | 누락 |
|---|---|---|---|
| 1 | prompt_registry ↔ output_schema | prompt_ids(P-PODCAST-CRITIC-001 등 agent_draft) → EpisodePlan/GuestBrief/QuestionList/Shownotes/Critic 본문(§4 output_schema) | **0** (출력 본문 5종 전부 output_schema 에 매핑) |
| 2 | api_contract ↔ frontend·api client | blueprint §4.1 이 "* 후속 — API 계약은 phase 진행 시" 로 **명시적 deferral** 처리 | **0 (현 단계 비대상)** — 누락이 아니라 의도적 후속(phase 진행 시 생성) |
| 3 | db_schema ↔ migration | EpisodePlan(JSONB) ↔ episodes.plan_json / format enum ↔ episodes.format CHECK (contract_draft §3). migration 은 "런타임 미생성, 설계만"(blueprint §4.1) | **0 (설계 정합)** — 런타임 migration 미생성은 dry-run 정상 |
| 4 | agent_io ↔ agents[] IO | 7 agent inputs/outputs/forbidden_actions ↔ agent_io_contract (blueprint §2 + agent_draft critic 예시) | **0 drift** (critic: episode_plan_dict→overall_verdict/overall_score/dimensions 정합) |

**누락 항목 합계: 0** (축2·3 은 dry-run deferral 로 "현 단계 비대상" — 실 누락 아님).

**★ 관찰 (drift 0 이지만 machinery 한계 발견)**: contract_template 의 cross-ref 표에 **"조건부 산출"(conditional output) 축이 없다**. guest_brief/question/shownotes 는 게스트/모드 의존 조건부 agent 인데, "이 출력은 X 조건일 때만 산출된다"를 contract cross-ref 가 직접 표현하지 못함 (contract_draft §GAP 보강 = G3). → drift 는 없으나 **표현력 GAP** (D 섹션 G3).

**판정 근거**: 4 축 cross-ref 누락 **0** → **PASS**. 단 조건부 산출 축 부재는 GAP 로 별도 기록(설계 정합성에는 영향 없음, machinery 표현력 한계).

---

### 검증 4 — with-skill / without-skill comparison → **PASS** (with≫without 입증, ★ 품질·일관성 지표는 소표본 PENDING)

> 질문: machinery 적용 전(WITHOUT)/후(WITH) 결과가 어떻게 달라지는가 (누락률 / 품질 / 일관성). 상세 수치는 §B.

**3 지표 (validation_workflow 검증4 절차)**:

1. **누락률 (machinery 강제 절차 단계의 누락)** — WITH < WITHOUT **입증됨**:
   - WITHOUT 은 forbidden_scope 매핑(0/1=0), eval gate(0/1=0), contract cross-ref(4축 누락), 충돌 검토 절차(미수행)를 **전부 누락**.
   - WITH 은 forbidden_scope→non_goals 매핑, eval 임계값 게이트, 4축 cross-ref, 충돌 검토를 **전부 강제**. → 누락률 WITH ≪ WITHOUT (§B 지표 1·2·4·5 정량).
2. **품질 (산출물 품질 점수)** — **PENDING**: 실 LLM 산출물 점수는 검증 5 가 PENDING(실측 미수행)이므로 품질 점수 비교 불가. (구조 품질 proxy 는 §B 로 측정, 의미 품질 점수는 미측정.)
3. **일관성 (반복 실행 편차)** — **PENDING**: 반복 실행 실측이 없어 편차 비교 불가 (소표본, dry-run).

**YAGNI 차단 점검 (절차 3)**: 신규 Skill 0 권장이 정당한가? — WITH(재사용)이 WITHOUT(절차 부재) 대비 누락률을 명확히 낮추면서, 신규 Skill 추가 없이 달성. 즉 "신규 Skill 추가의 효용 ≤ 기존 재사용" 가설이 지지됨 (신규 Skill 강행 시 검증2 충돌 발생 = 음의 효용). → **신규 Skill 0 이 옳다**는 결론을 검증4 가 지지.

**판정 근거**: 누락률 지표에서 WITH ≪ WITHOUT 정량 입증(§B) → **PASS**. 단 품질·일관성 2지표는 실 산출물 부재로 **PENDING(소표본 정상)**. 정량 우열 단정 금지 — 누락률 차원만 결정적, 의미 품질은 미측정.

---

### 검증 5 — eval-run 연동 (★) → **PENDING (절차 적용 가능 / 실측 미수행)** [정상]

> 질문: eval-run §3~§6 절차가 팟캐스트 harness 에 **적용 가능한가**. ★ 실 LLM 호출/실측 점수 미수행 → PENDING 이 정상.
> 본 섹션은 eval-run §5 리포트 형식(요약 점수표 + 임계값 점검 + 결정)을 차용한다.

#### eval-run §3~§6 적용 가능성 (절차 cross-ref)

| eval-run 단계 | 팟캐스트 harness 적용 가능성 | 매핑 근거 |
|---|---|---|
| §3 실행 (golden_set 케이스 → 출력) | ✅ **적용 가능** | golden_set PE-001~ 케이스 정의됨(eval_draft PE-002 인터뷰 케이스 완비: input/expected_path/expected_output/passing_criteria). 비교 모드(신구) 사용 가능. |
| §4 채점 (schema 준수율 + 품질 차원 + 다양성) | ✅ **적용 가능** | schema 준수율 1차 게이트 + podcast_planning_eval 10차원 자동 채점(P-PODCAST-CRITIC-001) + 후보 3개 cosine similarity 다양성. |
| §5 결과 저장 (regression_results/{trigger}_{날짜}.md) | ✅ **적용 가능** | 동일 리포트 형식 차용 가능 (아래 형식표). |
| §6 임계값 판정 | ✅ **적용 가능** | blueprint §5.2 + eval_draft §C 가 eval-run §6 임계값과 **동일** (schema<100%→fail / 점수↓>0.3→fail / 비용>30%→cost-review / latency>20%→경고 / 차단단어>0%→fail). |

#### golden_set 케이스 매핑 가능성 → ✅ 가능

- PE-001~PE-005(솔로/인터뷰/패널/시리즈오프닝/단발) 케이스 구조가 eval-run §3 입력 형식과 정합. PE-002(인터뷰 게스트 모드)는 expected_output.validation 4항목 + passing_criteria(schema 100% / overall_score≥임계) 완비 → 채점 가능 형식.

#### 임계값 게이트 → phase 종료 차단 연결 가능성 → ✅ 가능

- blueprint §6 phase-P1.acceptance "golden_set 회귀 PASS / schema 준수 100%" + phase-P3.acceptance "eval-run 임계값 게이트 통과" → 임계값 위반이 phase 종료(acceptance 미충족)를 **차단**하는 경로 존재. 검증6 항목4(eval gate)와 연결됨.

#### eval-run §5 형식 리포트 (요약 점수표 — ★ 값은 [미측정] placeholder)

```markdown
# Eval Run: podcast-harness-S2-validation (★ 절차 적용성 점검 — 실측 미수행)
- 트리거: harness-factory validation (검증5)
- 케이스 수: PE-001~PE-005 (정의됨 / 실행 안 함)
- 비교 대상: WITH blueprint (WITHOUT 은 eval 형식 부재 → 비교 불가)

## 요약 점수
| 지표 | WITH(설계 가능) | 실측 |
|---|---|---|
| schema 준수율 | 100% 게이트 정의됨 | [미측정 — 실 LLM 미호출] |
| podcast_planning 평균(10차원) | 채점 차원 정의됨 | [미측정] |
| opening_hook_strength | 차원 정의됨 | [미측정] |
| 다양성 (cos sim) | 후보 3 다양성 측정 가능 | [미측정] |
| 평균 latency / 비용 | placeholder timeout 30000ms | [미측정] |

## 임계값 점검 (적용 가능 여부)
- schema 준수율 < 100% → fail : ✅ 게이트 정의됨 (미실행)
- 평균 점수 하락 > 0.3 → fail : ✅ 게이트 정의됨 (미실행)
- 비용 증가 > 30% → cost-review : ✅ 게이트 정의됨 (미실행)
- latency 증가 > 20% → 경고 : ✅ 게이트 정의됨 (미실행)
- 차단 단어 > 0% → fail : ✅ 게이트 정의됨 (미실행)

## 결정
PENDING — 절차/임계값/케이스 매핑 **전부 적용 가능**. 실 점수는 LLM 호출 없는 dry-run 이므로 미측정.
human_review_needed: 해당 없음 (실행 자체 미수행).
```

**우선순위 정합**: `eval-run > harness-factory validation` (INDEX) — 실 평가는 eval-run 절차 소유. 본 검증은 "적용 가능성"만 확인하고 실 평가를 eval-run 에 위임.

**판정 근거**: eval-run §3~§6 절차 + 임계값 게이트 + golden_set 케이스 매핑 **전부 적용 가능**하나, 실 LLM 호출/실측 점수는 dry-run 범위 밖 → **PENDING (절차 적용 가능 / 실측 미수행)** = 정상.

---

### 검증 6 — generated harness acceptance → **PASS** (5 체크리스트 전부 충족)

> 질문: 생성 harness 가 최소 수락 기준 5개를 만족하는가.

| # | 수락 체크 | 충족 | 근거 |
|---|---|---|---|
| 1 | 최소 파일 구조 (라우터+상태+contracts+phases+eval+skills) | ✅ | 라우터 AGENTS/CLAUDE(§7) + 상태 PROJECT_STATE(project_state_draft) + contracts 4(§4) + phases 5(§6) + eval 4(§5) + skills(재사용, §3). 6/6 디렉토리 대응. |
| 2 | forbidden_scope → non_goals + 라우터 금지 매핑 | ✅ | domain_brief.forbidden_scope 6 → phases[].non_goals(§6 각 phase) + phase_draft NG1~NG4. 라우터(CLAUDE 형식) 금지 행동(오디오 제작/TTS/배포)으로 전파. scope creep 차단 경로 존재. |
| 3 | phase 8 files 형식 + acceptance 존재 | ✅ | phase_draft 가 8 files(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) **전부** 채움. acceptance A1~A4(eval-run 임계값 연결) 존재. blueprint §6 은 goals/non_goals/acceptance 만(proposal 단계, §6 말미 명시 — 실 진입 시 8 files 생성). |
| 4 | eval gate → 종료/배포 차단 연결 | ✅ | 검증5 임계값 게이트 → phase-P1/P3 acceptance 차단 연결(§6). schema<100% / 점수↓>0.3 → fail = 종료 차단. |
| 5 | rollback·retrospective 경로 존재 | ✅ | phase_draft notes.md: rollback=Slice commit 단위 revert(P-X1) + retrospective=meta-retrospective(closing_notes). blueprint §6 phase-P4 security-review 게이트. |

**판정 근거**: 5 체크리스트 **전부 충족** → **PASS**. (blueprint §6 이 proposal 단계라 phase entry 8 files 를 goals/non_goals/acceptance 3개로 축약했으나, phase_draft 가 8 files 완본 예시를 제공 — 형식 충족 입증.)

---

## B. with/without 6지표 수치표 (★ 숫자/0·1)

> WITH = `harness_blueprint.md`, WITHOUT = `_without_baseline.md`. 측정 = 문서 정적 대조.

| # | 지표 | 측정 방법 | WITH | WITHOUT |
|---|---|---|---|---|
| 1 | 누락된 필수 파일 수 | acceptance 최소구조 6(라우터/상태/contracts/phases/eval/skills) 대비 누락 개수 | **0** | **6** |
| 2 | forbidden_scope 반영 | 비범위 명시 + non_goals/라우터 금지 매핑 (0/1) | **1** | **0** |
| 3 | Skill trigger 충돌 수 | 기존 21 Skill 키워드와 중첩 개수 | **0** | **0** |
| 4 | contract cross-ref 누락 수 | prompt↔output / api↔front / db↔migration / agent_io 누락 개수 | **0** | **4** |
| 5 | eval gate 존재 | 임계값 게이트가 종료/배포 차단으로 연결 (0/1) | **1** | **0** |
| 6 | proposal-first 위반 | active 자동 반영 시도 / outputs 외 변경 (0=위반없음) | **0** | **0** |

**각 칸 측정 근거 (1줄)**:
- **지표1**: WITH = 6 구조(§3~§7 + project_state_draft) 전부 존재 → 누락 0 / WITHOUT = 라우터·상태·contracts디렉토리·phases·eval-gate·skills 구조 6개 모두 부재(§ API 엔드포인트·prose 데이터모델만) → 누락 6.
- **지표2**: WITH = forbidden_scope 6항목→non_goals 매핑 명시(§6) → 1 / WITHOUT = "기타 고려사항"에 비용·모바일만, 비범위(non_goals) 개념 0 → 0.
- **지표3**: WITH = 신규 Skill 0(채택) → 충돌 0 / WITHOUT = trigger_keywords 자체를 정의하지 않음(기능 나열만, §5) → INDEX-form 충돌 측정 불가 = 0. (★ 단, WITHOUT 의 "질문 리스트 자동 생성/SEO 제목/이전 에피소드 참고" 같은 기능을 만약 Skill 로 만들면 충돌 검토 절차 자체가 없음 = 잠재 risk. 측정값은 0 이나 의미 차이는 §주 참조.)
- **지표4**: WITH = 4 cross-ref 축 정합(검증3, 누락 0) / WITHOUT = "프론트랑 백엔드가 합의만 하면 됨"(§6) = cross-ref 4축 전부 미정의 → 누락 4.
- **지표5**: WITH = 임계값 게이트→phase acceptance 차단 연결(§5.2+§6) → 1 / WITHOUT = "초기엔 좋아요/별로만"(§7), 게이트·임계값·차단 0 → 0.
- **지표6**: WITH = outputs/TEST/ 격리 + validation pending(active 아님 명시) → 위반 0 / WITHOUT = baseline 문서 자체가 어떤 active 경로도 건드리지 않음(naive 설계 문서) → 위반 0. (둘 다 0 = 정상; 단 WITH 은 규율로 0, WITHOUT 은 그냥 변경 행위 부재로 0.)

> **지표3 주**: WITH·WITHOUT 모두 수치 0 이지만 의미가 다르다 — WITH 은 충돌 검토를 **수행하고** 0(machinery 작동), WITHOUT 은 검토 절차 **부재로** 0(우연). machinery 의 가치는 "podcast-eval-run 같은 충돌을 사전 검출"(검증2 4중첩 검출)하는 데 있으며, 이는 WITHOUT 에 존재하지 않는다.

---

## C. 5 gaps 재현 표 (A6) — 현재 하네스 부족점이 팟캐스트 도메인에서도 재현되는가

> baseline = `blueprints/dreammate_current_harness_blueprint.md` §10 (L3 확장 시 부족점 5).

| # | M0 blueprint 부족점 (§10) | 팟캐스트 dry-run 재현 | 근거 |
|---|---|---|---|
| 1 | 하네스 생성 자동화 없음 (domain_brief→blueprint→validation 재현 절차/도구 부재) | **재현** | S1 은 generation_workflow 11단계를 **수작업으로** 적용해 blueprint 생성. 자동 생성 도구는 여전히 없음(NG11). 11단계 절차는 있으나 실 도구 부재 = §10 부족점1 그대로 재현. |
| 2 | `.claude/agents` 자동 생성 없음 (agent scaffold 선언적 생성 경로 부재) | **재현** | 7 agent 는 blueprint §2 YAML + agent_draft(critic 1개) 로 **수동** scaffold. `.claude/agents/` 디렉토리 자동 생성 0(NG12). agent_template 으로 형식만 정의됨 = 부족점2 재현. |
| 3 | trigger dry-run 테스트 부족 | **재현** | 검증1(trigger validation)을 **정적 키워드 대조**로만 수행. 실 Claude Code 자동 트리거 행위 실측 0 = 부족점3(사전 dry-run 검증 절차 부족) 재현. machinery 가 기준은 정의했으나 실 dry-run 도구는 여전히 없음. |
| 4 | with-skill/without-skill 비교 부족 | **재현 (부분 완화)** | 검증4 + §B 6지표로 **정량 비교 절차를 처음 적용**(완화). 단 품질·일관성 2지표는 실 산출물 부재로 PENDING = 비교 baseline 미비(부족점4) 재현. 절차는 정의됐으나 실 비교 표본 부족. |
| 5 | generated_harness acceptance 기준 부족 | **재현 (완화)** | 검증6 5 체크리스트로 acceptance 를 **명문 점검**(완화). 단 자동 점검 도구가 아니라 수동 체크 = 부족점5(자동 점검 부재) 재현. 기준은 명문화됨, 자동화는 없음. |

**재현 요약**: **재현 5 / 부분 0 / 비재현 0**. 5 부족점 전부 팟캐스트 도메인 dry-run 에서 재현됨. 단 부족점4·5 는 S2 절차 적용으로 **부분 완화**(절차는 작동, 도구·표본은 여전히 deferred). → M0 §10 의 "기준은 정의 / 도구·payoff 는 다음 phase deferred" 구조와 정합.

---

## D. GAP 목록 + 보완 제안 (★ 제안만 — 실 machinery 변경 금지)

### S1 보고 GAP (G1~G6) 검증 관점 재평가

| GAP | S1 관찰 | S2 검증 재평가 | machinery 보완 proposal (1줄) |
|---|---|---|---|
| **G1** expert_pool 판단 기준 모호 | 포맷별 특화 vs 단일 agent 파라미터화 기준 약함 | **유효 — 격상 권고**. assumptions.md(phase_draft) 가 "format 은 planning 파라미터로 충분"을 4-check 통과로 결론냈으나, 그 근거(언제 expert_pool 채택?)가 architecture_patterns 에 없어 판단이 **암묵적**. | `architecture_patterns.md` 에 "expert_pool vs 단일 agent 파라미터화 결정 기준"(특화도/비용/유지보수 임계) 추가 제안. |
| **G2** skill 신규 vs 재사용 결정트리 | 단계4 는 신규 생성 전제, 재사용 우월 시 가이드 부재 | **유효 — 검증4 가 입증**. 신규 강행 시 검증2 충돌(podcast-eval-run 4중첩) = 음의 효용 입증됨 → 재사용이 옳다는 결론을 machinery 가 지지하나, **결정트리 명문 없음**. | `generation_workflow.md` 단계4 에 "신규 Skill vs 기존 재사용 결정트리"(키워드 충돌 검사 → 충돌 시 재사용 강제) 추가 제안. |
| **G3** conditional_execution 슬롯 부재 | guest_brief/question/shownotes 조건부 실행을 agent_template 이 표현 못함 | **유효 — 검증3 에서 재확인**. contract cross-ref 표에도 "조건부 산출" 축 부재(contract_draft §GAP). agent inputs 주석으로 우회 중. | `agent_template.md` 에 `conditional_execution`(예: `condition: mode==guest`) 슬롯 + `contract_template.md` cross-ref 에 "조건부 산출" 행 추가 제안. |
| **G4** 조건부 eval 차원 미지원 | eval_template 고정 N 차원 전제, 모드 의존 +2(question_quality/guest_fit) 표현 못함 | **유효 — 검증5 에서 재확인**. eval_draft 가 notes 로 "해당 없음 시 채점 제외"를 우회 표기. 조건부 차원의 정식 채점 규칙 부재. | `eval_template.md` 채점 차원에 `applies_when`(조건부 차원 + 미해당 시 평균에서 제외) 규칙 추가 제안. |
| **G5** 제3자 PII 축 부재 | llm_security 사용자 PII 중심, 게스트(제3자) 인물정보 risk 누락. risk medium 충분한지 모호 | **유효 — 격상 권고**. project_state_draft 도 "게스트 제3자 PII 고려 시 high 재검토"(결정3)로 미해결 표기. domain_brief risk_level 판정이 제3자 PII 를 반영 못함. | `domain_brief_schema.md` risk_level 판정 기준에 "제3자(비사용자) PII 처리 → risk 등급 상향 트리거" 축 추가 제안. |
| **G6** data_model 필드 부재 | domain_brief_schema 에 데이터 계층 전용 필드 없음, primary_tasks/output_artifacts 로 우회 | **유효**. domain_brief §2(데이터 계층)가 schema 11필드 밖 **별도 섹션**으로 보강됨 = schema 가 데이터 모델을 1급 필드로 받지 못함을 방증. | `domain_brief_schema.md` 에 `data_model`(계층 구조 + 엔티티 + PII 표시) 선택 필드 추가 제안. |

### S2 신규 발견 GAP (G7·G8)

| GAP | S2 발견 | machinery 보완 proposal (1줄) |
|---|---|---|
| **G7** meta-phase/dry-run 상태 표현 부재 | project_state_template 이 단일 active 하네스 전제 → dry-run("active 아님, 제안 상태")을 표현하는 status 슬롯 없어 confirmed_decisions 에 "(제안)" 수동 표기로 우회(project_state_draft §GAP). | `project_state_template.md` 에 `harness_status` enum(active / dry-run-blueprint / proposal) 슬롯 추가 제안. |
| **G8** validation 필드가 PENDING 정상 케이스를 표현 못함 | harness_blueprint_schema 의 validation 3필드 enum = `pass\|fail\|pending` 뿐. 검증5(eval-run)는 "절차 적용 가능 but 실측 미수행"이 **정상 결과**인데, 이를 단순 pending 과 구분할 슬롯 없음. with_without 도 누락률=pass / 품질=pending 의 **혼합 상태**를 단일 값으로 압축해야 함. | `harness_blueprint_schema.md` validation enum 에 `pending-by-design`(실측 미수행이 정상) 또는 차원별 sub-status 추가 제안. |

**GAP 총개수: 8** (G1~G6 재평가 전부 유효 + 신규 G7·G8).
**핵심 3개**: **G2**(skill 재사용 결정트리 — 검증4 가 직접 입증) / **G3**(conditional_execution — agent+contract 양쪽 표현력 부족, 검증3 재확인) / **G5**(제3자 PII risk 격상 — 미해결 안전 risk, medium→high 재검토 여지).

---

## E. 판정 종합 (A7)

### 6검증 분포

```
PASS    : 검증1 (trigger validation)        — 정적 정합 / 런타임 트리거 실측은 미수행
PASS    : 검증2 (skill conflict check)      — 채택 충돌 0 + 반례(podcast-eval-run 4중첩) machinery 검출
PASS    : 검증3 (contract consistency)      — cross-ref drift 0 (조건부 산출 축 부재 = GAP G3)
PASS    : 검증4 (with-without comparison)   — 누락률 WITH≪WITHOUT 입증 / 품질·일관성 2지표 PENDING(소표본)
PENDING : 검증5 (eval-run 연동) ★           — 절차/임계값/케이스 매핑 전부 적용 가능 / 실측 미수행 = 정상
PASS    : 검증6 (acceptance)                — 5 체크리스트 전부 충족
```

**분포: PASS 5 / PENDING 1.** (PASS 중 검증3·4 는 GAP-flagged — drift·누락은 0 이나 표현력/표본 한계를 동반.)

### machinery 가 작동한 지점 (검증 가능성 입증)

1. **skill conflict 검출 (검증2)** — machinery 가 podcast-eval-run 신규 Skill 의 eval-run 키워드 4중첩을 **정확히 검출**, 채택을 사전 차단. 가장 강한 "machinery 작동" 증거.
2. **contract cross-ref 정합 (검증3)** — 4 정합 축으로 drift 0 을 체계적으로 점검.
3. **with-without 누락률 정량화 (검증4 + §B)** — 6지표로 WITH(누락 0/forbidden 1/gate 1)와 WITHOUT(누락 6/forbidden 0/gate 0)의 차이를 숫자로 표현.
4. **acceptance 체크리스트 (검증6)** — 최소 구조/forbidden 매핑/8 files/eval gate/rollback 경로 5개를 명문 점검.
5. **proposal-first 규율** — 6검증 PASS 에도 active 전환 안 함(규칙7), outputs/TEST/ 격리 유지.

### machinery 가 부족한 지점 (개선 입력)

1. **실측 부재 (검증5)** — 절차는 적용 가능하나 실 LLM 평가가 없어 품질·일관성(검증4) 결론 불가. **다음 개선: 실 eval-run 표본 1회 (mock-deterministic 라도)**.
2. **조건부 표현력 (G3/G4)** — agent_template/contract_template/eval_template 모두 "조건부 실행/산출/차원"을 1급으로 표현 못함. **다음 개선: conditional 슬롯 3개 (agent/contract/eval)**.
3. **결정 기준 명문 부재 (G1/G2)** — expert_pool 채택 기준 / 신규 vs 재사용 결정트리가 암묵적. **다음 개선: architecture_patterns + generation_workflow 단계4 결정 가이드**.
4. **안전 risk 판정 (G5)** — 제3자 PII 가 risk_level 판정에 반영 안 됨. **다음 개선: domain_brief_schema risk 격상 트리거**.
5. **meta-phase 상태 표현 (G7/G8)** — dry-run/pending-by-design 을 표현하는 슬롯 부재. **다음 개선: status enum 확장**.

### 방향성 결론 (정량 우열 단정 금지 — 소표본)

- **machinery 는 "검증할 수 있다"**: 6검증 중 5개가 PASS 판정을 내릴 만큼 명확한 기준을 제공했고, 특히 skill conflict(검증2)에서 실제 충돌을 사전 차단하는 **machinery 작동을 입증**했다.
- **단 "우월하다"고 단정하지 않는다**: 검증4 의 품질·일관성, 검증5 의 실측 점수가 모두 PENDING(소표본/실측 미수행)이므로, WITH 가 WITHOUT 대비 **누락률·구조 정합** 차원에서 우세함은 정량 입증되나 **의미 품질** 우열은 미확정.
- **8 GAP 이 다음 개선 입력**: 5 부족점 전 재현 + 8 GAP(특히 G2/G3/G5) 이 L3 Meta-Factory 의 다음 phase 보완 대상. dry-run 의 핵심 산출물은 "성공"이 아니라 이 **GAP 목록**이다.

---

## F. 다음 단계 / 위임

- 본 리포트는 검증만 수행 — blueprint 는 6검증 통과(PASS 5/PENDING 1)에도 **사용자 승인 전 active 아님** (factory_contract 규칙 7).
- 8 GAP 의 실 machinery 보완은 **proposal-only** (D 섹션 proposal 1줄씩) — 실 변경은 contract-change Skill 경유 + 사용자 승인 (★ S2 는 제안만, machinery 0줄 변경).
- 실 eval-run 표본(검증5 PENDING 해소)은 eval-run §3~§6 절차로 별도 위임 (`eval-run > harness-factory validation`).

---

이 검증 리포트는 meta_factory machinery(validation_workflow 6검증 + factory_contract 8규칙 + eval-run §3~§6 cross-ref + INDEX 충돌 규칙)를 적용하여 작성됨. 산출물은 문서(.md)만, 런타임/기존 하네스 0줄 변경 (A9).
