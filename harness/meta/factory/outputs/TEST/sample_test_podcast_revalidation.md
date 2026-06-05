# sample_test_podcast_revalidation.md — Phase M2 Slice S3 재검증 리포트

> 위치: `harness/meta_factory/outputs/TEST/sample_test_podcast_revalidation.md`
> 상태: Phase M2 (Meta-Factory GAP Remediation) Slice S3 — re-validate (S1·S2 machinery 개선의 M1 TEST 재적용)
> 입력(읽기 전용 machinery, S1·S2 반영본): `generation_workflow.md`(G2) / `architecture_patterns.md`(G1) / `domain_brief_schema.md`(G5·G6) / `templates/agent_template.md`(G3) / `templates/contract_template.md`(G3) / `templates/eval_template.md`(G4) / `templates/project_state_template.md`(G7) / `harness_blueprint_schema.md`(G8)
> 입력(M1 산출물, before 기준): `outputs/TEST/podcast/{domain_brief, harness_blueprint, _without_baseline}.md` + `scaffolds/*`
> before 검증 리포트: `outputs/TEST/sample_test_podcast_validation.md` (§D GAP 8 + §A 6검증)
> 적용 시연(additive): `outputs/TEST/podcast/{domain_brief, harness_blueprint}.md` + `scaffolds/{agent_draft, contract_draft, eval_draft, project_state_draft}.md` §M2 블록
> ★ 목적: "8 GAP 이 개선 machinery 로 실제 해소/표현 가능해졌는가" 입증 (before/after). 런타임 0 (A9) — 문서만.
> ★ machinery 문서는 **읽기만** (재변경 0). 본 S3 는 M1 TEST 산출물에만 additive 적용.

---

## 0. 요약 (TL;DR)

| 항목 | 결과 |
|---|---|
| 8 GAP 해소 판정 | **addressed 7 (G1·G2·G3·G4·G6·G7·G8) / expressible 1 (G5 — 안전 risk 상향이 schema 축으로 표현·도출 가능, 실 등급변경은 사용자 승인 사항)** / partial 0 / open 0 |
| 6검증 재판정 | **PASS 5 (검증1·2·3·4·6) / PENDING-BY-DESIGN 1 (검증5)** — 검증3 GAP-flag 해소, 검증5 정상 미측정이 명시 표현됨 |
| 핵심 변화 | 검증3 "조건부 산출 축 부재 GAP" → **해소** (G3 contract 조건부 산출 열) / 검증5 단순 PENDING → **PENDING-BY-DESIGN** 으로 "정상 미측정" 명시 (G8) |
| backward-compat | ✅ M1 blueprint(구 machinery 산출) 개선 machinery 하에서도 valid — 전부 additive(기존 필드·구조 보존 + 새 슬롯 선택). 6검증 여전히 적용 가능 |
| improvement backlog | **8 → 0** (전 GAP addressed/expressible, open 0) |
| 금지 위반 | **0** — machinery 문서 0줄 변경 / 변경 전부 outputs/TEST/ 하위 / 자격증명 0 |

> ★ 8 GAP 이 전부 해소(addressed) 또는 표현가능(expressible)으로 판정되며 open(미해소) 0. 단 정량 우열·실 품질은 여전히 미측정(검증5 PENDING-BY-DESIGN) — "표현·판정 가능해졌다"가 결론이지 "실측 우월"이 아니다.

---

## A. 개선 슬롯 적용 요약 (additive 시연)

M1 팟캐스트 산출물에 S1·S2 machinery 의 새 슬롯을 **추가 적용**(기존 내용 삭제 0, "M2 G-fix 적용" 주석 표시). 각 GAP 이 이제 표현 가능함을 보이는 최소 예시.

| 파일 | 적용 슬롯 (GAP) | 위치 |
|---|---|---|
| `podcast/harness_blueprint.md` | **conditional_execution**(G3, guest_brief/question/shownotes 3 agent) + **pending-by-design** sub-status(G8, validation §9) + §M2 요약 | §2 agents[] / §9 validation / §M2 |
| `podcast/domain_brief.md` | **data_model** 필드(G6, hierarchy/entities/pii) + **제3자 PII risk 상향 트리거**(G5, §M2) | YAML data_model / §M2 |
| `scaffolds/agent_draft.md` | **conditional_execution**(G3, guest_brief 조건부 agent 예시) + ✅ 해소 노트 | 채운 scaffold §M2 / GAP 노트 |
| `scaffolds/contract_draft.md` | **"조건부 산출" cross-ref 열**(G3, GuestBrief/QuestionList/Shownotes) + ✅ 해소 노트 | §3 cross-ref / GAP 노트 |
| `scaffolds/eval_draft.md` | **applies_when** 차원(G4, question_quality/guest_fit) + ✅ 해소 노트 | §B 채점 차원 / GAP 노트 |
| `scaffolds/project_state_draft.md` | **harness_status: dry-run-blueprint** enum(G7) + ✅ 해소 노트 | migration_progress / GAP 노트 |

> ★ 전부 additive — M1 원본 흔적(예: critic 무조건 실행, risk medium 원본값, podcast_harness_status custom 키)을 남기고 표준 슬롯을 병기. backward-compat 보존(§D).

---

## B. 8 GAP before/after 표 (★ 핵심 산출)

> before = M1 §D + M1 산출물 표현 / 개선 machinery = S1·S2 가 어느 파일에 무엇을 추가했는가 / after = M2 재적용 후 표현 / 해소 판정 = addressed | expressible | partial | open.

| GAP | M1 상태 (before) | 개선 machinery (어느 파일에 무엇) | M2 재적용 후 (after) | 해소 판정 |
|---|---|---|---|---|
| **G1** expert_pool vs 단일 agent 파라미터화 | 채택 기준 약함 — assumptions 가 "format 은 파라미터로 충분"을 4-check 으로 **암묵** 결론 (판단 근거 부재) | `architecture_patterns.md §2.1` — "expert_pool vs 단일 agent 파라미터화 결정 기준"(특화도/유형수/독립진화/유지보수 우선 + 비용 N배 임계) 추가 | blueprint §1.1 expert_pool 미채택 / phase_draft assumptions "format=파라미터" 결론이 §2.1 4축으로 **사전 판단 가능** (특화도=입력변수 수준 + 포맷 수 소수 → 단일 agent) | **addressed** |
| **G2** skill 신규 vs 재사용 결정트리 | 단계4 가 신규 생성 전제 — 재사용 우월 시 가이드 부재 (검증4 가 음의 효용 입증했으나 결정트리 명문 없음) | `generation_workflow.md §4.1` — "신규 Skill vs 기존 재사용 결정트리"(키워드 추출 → 충돌 검사 → 충돌 시 재사용 강제 / 무충돌+고유가치 시 신규 / 무충돌+가치미입증 시 YAGNI 차단) 추가 | skill_draft 의 podcast-eval-run 4중첩 → §4.1 트리 "충돌 발견 → 재사용 강제"로 **사전 분기 가능**. "신규 0 권장"이 절차 결론으로 명문화 | **addressed** |
| **G3** conditional_execution / 조건부 산출 표현 부재 | guest_brief/question/shownotes 조건부 실행을 agent inputs 주석(`?`)으로 우회 + contract cross-ref 에 "조건부 산출" 축 부재(검증3) | `agent_template.md` — `conditional_execution.condition` 슬롯 / `contract_template.md §3` — cross-ref "조건부 산출(conditional output)" 열 (양쪽 정합) | blueprint §2 3 agent + agent_draft guest_brief 예시에 `condition: mode==guest` 1급 표현 / contract_draft §3 에 GuestBrief/QuestionList/Shownotes 조건부 산출 열 → **execution(agent)·output(contract) 양축 해소** | **addressed** |
| **G4** eval 조건부 차원 미지원 | eval_template 고정 N 차원 전제 — 모드 의존 +2(question_quality/guest_fit)를 notes 로 우회 | `eval_template.md §B` — 채점 차원에 `applies_when` 속성(조건부 차원 + 미해당 시 평균 제외, 적용 차원 수로 평균) 추가 | eval_draft §B 에서 question_quality/guest_fit 를 `applies_when: mode==guest` 로 표현. 솔로=8차원/게스트=10차원 평균 → notes 우회 제거 | **addressed** |
| **G5** 제3자(게스트) PII risk 미반영 | risk `medium` 고정 — 게스트 제3자 PII 위험 미반영. project_state_draft 가 "high 재검토 여지" **수동** 표기로 미해결 | `domain_brief_schema.md §1.1` — risk_level 상향 트리거 "제3자(비사용자) PII 처리 → 등급 상향(medium→high 재검토)" 축 추가 (`data_model.pii` 제3자 표시와 연결) | domain_brief §M2: `data_model.pii.Guest` = 제3자 PII 표시 → 트리거 발동 → **medium→high 상향 후보로 명시 판정 가능**. (원본 medium 보존, 상향 도출이 schema 축으로 표현됨; 실 등급변경은 사용자 승인) | **expressible** |
| **G6** data_model schema 밖 우회 | domain_brief §2 가 데이터 계층을 schema 11필드 **밖** 별도 prose 섹션으로 서술 | `domain_brief_schema.md §1.2` — `data_model` 선택 필드(hierarchy / entities / pii) 추가 | domain_brief YAML 에 `data_model` 블록(User→…→Episode hierarchy + 8 entities + Guest 제3자 PII) → 데이터 계층이 **schema 안 1급 필드**로 수용 | **addressed** |
| **G7** dry-run 상태 표현 부재 | project_state_template 단일 active 전제 — dry-run 을 confirmed_decisions "(제안)" + custom 키(podcast_harness_status)로 수동 우회 | `project_state_template.md` — migration_progress 에 `harness_status` enum(active / dry-run-blueprint / proposal) 슬롯 추가 | project_state_draft migration_progress 에 표준 `harness_status: dry-run-blueprint` 적용 → "(제안)" 수동표기·custom 키 우회를 표준 enum 이 대체 (active 아님 = 규칙 5·6 정합) | **addressed** |
| **G8** validation pending 단일값 | validation enum=`pass\|fail\|pending` 뿐 — "정상 미측정"(검증5)과 "혼합 상태"(검증4 누락률 pass/품질 pending)를 단일값으로 압축 | `harness_blueprint_schema.md §3.1 Validation` — enum 에 `pending-by-design` 추가 + 차원별 sub-status (누락률=pass / 품질=pending-by-design) | blueprint §9: `with_without_skill_eval: pass / pending-by-design(품질·일관성)` + `eval_run_integration: pending-by-design` 슬롯 → "실측 미수행이 정상"이 단순 pending 과 **구별 표현** | **addressed** |

**해소 분포: addressed 7 / expressible 1 / partial 0 / open 0.**

> G5 가 expressible 인 이유: machinery 가 "제3자 PII → 등급 상향" 트리거를 **표현·도출 가능**하게 했고 dry-run 에서 medium→high 상향 후보를 명시 판정했으나, 실제 risk 등급 변경(=security-review 강제 등 후속 게이트 발동)은 사용자 승인 결정 사항이라 dry-run 에서 "확정 변경"까지는 하지 않는다. 안전 판정 축은 해소(부재→존재), 등급 확정은 승인 게이트. → addressed 에 준하는 expressible.

---

## C. 6검증 재판정 (M1 GAP-flag 해소 확인)

> before(M1) → after(M2 개선 machinery 재판정). 각 PASS/FAIL/PENDING/PENDING-BY-DESIGN/GAP.

### 검증 1 — trigger validation : PASS → **PASS** (G2 강화)
- before: 정적 정합 PASS(재사용 Skill 100% 트리거 + 신규 0 → false trigger 0). 런타임 트리거 실측 미수행 단서.
- after: 동일 PASS. **G2 결정트리**(generation_workflow §4.1)가 "신규 Skill 후보를 트리거 키워드 충돌 검사로 사전 분기" 하므로 트리거 정합이 절차로 강화됨(신규 0 = 충돌 0 = false trigger 0 의 근거가 명문화).
- before→after: 정적 정합 PASS 유지 + 신규 Skill 결정이 절차(결정트리)로 강화.

### 검증 2 — skill conflict check : PASS → **PASS** (G2 절차화)
- before: 채택 충돌 0 + 반례(podcast-eval-run eval-run 4중첩) machinery 검출 → 채택 거부.
- after: 동일 PASS. **G2 결정트리**가 그 검출·거부를 "충돌 발견 → 재사용 강제" 분기로 **절차화** — M1 은 사후 반례였으나 M2 는 단계4 진입 전 사전 차단 가능.
- before→after: 충돌 검출 PASS 유지 + 검출→거부가 결정트리 사전 분기로 승격.

### 검증 3 — contract consistency : PASS (★ 조건부 산출 축 부재 = GAP) → **PASS (GAP 해소)**
- before: 4 cross-ref 축 drift 0 = PASS. 단 contract_template cross-ref 에 "조건부 산출" 축 부재 = 표현력 GAP(G3) 별도 기록.
- after: **G3 해소** — contract_template §3 에 "조건부 산출(conditional output)" 열 추가 → contract_draft §3 가 GuestBrief/QuestionList/Shownotes 의 조건부 산출(mode==guest 등)을 1급 표현. agent 측 conditional_execution 과 정합. **drift 0 PASS 유지 + GAP-flag 제거.**
- before→after: PASS(drift 0) 유지, "조건부 산출 축 부재 GAP" → **해소**(G3 열로 표현 가능).

### 검증 4 — with-without comparison : PASS (품질·일관성 PENDING) → **PASS (품질·일관성 = PENDING-BY-DESIGN)**
- before: 누락률 WITH≪WITHOUT 정량 입증 = PASS. 품질·일관성 2지표는 실 산출물 부재로 PENDING(소표본).
- after: 누락률 PASS 유지(개선 슬롯이 표현은 개선하나 실측 표본은 여전히 미수행). **G8** 로 품질·일관성을 단순 PENDING 이 아니라 `pending-by-design`(dry-run 실측 미수행 = 정상)으로 명시 구별. **실측 우열 단정은 여전히 금지** — 표현 개선이지 실측 수행 아님(정상).
- before→after: 누락률 PASS 유지 / 품질·일관성 PENDING → **PENDING-BY-DESIGN**(정상 미측정 명시). 실측은 여전히 미수행(정상).

### 검증 5 — eval-run 연동 : PENDING → **PENDING-BY-DESIGN** (★ 핵심 변화)
- before: eval-run §3~§6 절차/임계값/케이스 매핑 전부 적용 가능 / 실 LLM 호출·실측 점수 미수행 → 단순 **PENDING**(정상이라 주석으로 설명).
- after: **G8** 로 `pending-by-design` enum 이 추가되어, "절차 적용 가능 / 실측만 미수행 = dry-run 범위상 정상"이 단순 미완(pending)과 **구별되어 명시 표현**됨. blueprint §9 `eval_run_integration: pending-by-design` 슬롯. + **G4 applies_when** 으로 조건부 차원 채점 규칙이 명문화되어 eval 절차 적용성이 더 견고.
- before→after: PENDING → **PENDING-BY-DESIGN** — "정상 미측정"이 enum 으로 1급 표현. 실 점수는 여전히 미측정(정상, eval-run 위임).
- ★ **표본 실행 완료 (additive)**: 검증5 eval-run 표본 1회 실행 (`outputs/TEST/podcast_eval_run_sample.md`, mock-deterministic, PE-001 솔로/PE-002 게스트/PE-003 패널 3 케이스) → schema 100% / 차단·광고 0 / G4 applies_when 정상 작동(솔로·패널 조건부 차원 제외, 게스트 10차원). **pending-by-design 의 실측 차원 mock-deterministic baseline 수립**. 실 LLM 채점은 팟캐스트 실 구현 후 가능(현 단계 미해당) — mock 차원 measured / 실 LLM 차원 구현 후.

### 검증 6 — generated harness acceptance : PASS → **PASS** (G7 보강)
- before: 5 체크리스트(최소구조/forbidden 매핑/8 files/eval gate/rollback) 전부 충족 = PASS.
- after: 동일 PASS. **G7 harness_status** enum 으로 dry-run 상태(active 아님)가 1급 표현되어, "acceptance 통과 ≠ active" 의 상태 구분이 더 명확(체크리스트 정합 영향 없음, 표현력 보강).
- before→after: 5 체크리스트 PASS 유지 + dry-run/active 상태 구분이 harness_status 로 명시.

**6검증 분포: PASS 5 (검증1·2·3·4·6) / PENDING-BY-DESIGN 1 (검증5).**
- before 대비 변화: 검증3 GAP-flag **제거**(PASS 유지) / 검증5 PENDING → **PENDING-BY-DESIGN** / 검증4 품질·일관성 PENDING → PENDING-BY-DESIGN. 검증1·2·6 PASS 유지.

---

## D. backward-compat 확인

- **M1 podcast blueprint(구 machinery 산출)는 개선 machinery 하에서도 valid** — 8 변경이 전부 **additive**(신규 선택 슬롯/열/enum 값 추가, 기존 필드·구조 삭제·재명명 0). M1 원본 표현(critic 무조건 실행 = conditional_execution 슬롯 생략 / risk medium 원본값 / podcast_harness_status custom 키 / validation pass)이 그대로 valid 하며, 새 슬롯은 미기재 시 backward-compat 기본값(conditional_execution 생략=항상 실행 / applies_when 없음=무조건 차원 / harness_status 생략=active / data_model 생략=primary_tasks 우회)으로 동작.
- **validation_workflow 6검증 여전히 적용 가능** — 검증 절차 자체(4 정합 축 점검 / 충돌 키워드 대조 / 6지표 비교 / acceptance 5체크 / eval-run §3~§6 매핑)는 변경 0. 새 슬롯은 검증을 **더 정밀하게** 표현할 뿐(조건부 산출 열·pending-by-design·applies_when), 기존 판정 의미(pass/fail/pending)는 보존. → M1 산출물·검증 둘 다 재실행 시 동일 PASS 분포 + GAP-flag 만 해소.

---

## E. 종합 (백로그 8→0 판정)

### improvement backlog 판정
```
G1 expert_pool 결정 기준        → addressed   (architecture_patterns §2.1)
G2 skill 재사용 결정트리        → addressed   (generation_workflow §4.1)
G3 conditional_execution/산출   → addressed   (agent_template + contract_template §3)
G4 eval applies_when            → addressed   (eval_template §B)
G5 제3자 PII risk 상향          → expressible (domain_brief_schema §1.1 — 판정 축 해소, 등급확정은 승인)
G6 data_model 필드              → addressed   (domain_brief_schema §1.2)
G7 harness_status enum          → addressed   (project_state_template)
G8 pending-by-design            → addressed   (harness_blueprint_schema §3.1)
```
**백로그 8 → 0** (addressed 7 + expressible 1, open 0). 8 GAP 전부 개선 machinery 로 **해소 또는 표현 가능**해짐이 before/after 로 입증됨.

### machinery 작동 입증 (S3 관점)
- **표현력 GAP 해소(G3/G4/G6/G7/G8)**: agent/contract/eval/project_state/blueprint 5 종 산출물이 M1 에서 주석·prose·수동표기로 **우회**하던 5 차원(조건부 실행/조건부 산출/조건부 채점/데이터 계층/dry-run 상태/정상 미측정)을 **1급 슬롯**으로 표현하게 됨.
- **결정 기준 명문화(G1/G2)**: expert_pool 채택·신규 Skill 결정이 암묵 판단에서 architecture_patterns §2.1 / generation_workflow §4.1 의 **사전 결정 절차**로 승격.
- **안전 판정 축(G5)**: 제3자 PII 가 risk_level 판정에 반영되어 medium→high 상향이 schema 축으로 도출 가능(부재→존재).

### 한계 (정직)
- **실측은 여전히 미수행**: 검증5 PENDING-BY-DESIGN, 검증4 품질·일관성 PENDING-BY-DESIGN — 개선은 "표현·판정 가능"을 입증할 뿐 실 LLM 평가 점수·반복 편차는 미측정(dry-run 정상). 정량 우열 단정 금지.
- **G5 등급 확정은 승인 사항**: 상향 판정 축은 해소됐으나 medium→high 실 변경은 사용자 승인 게이트(security-review 강제 발동) — dry-run 에서 표현까지만.
- 본 S3 의 산출물은 "성공 선언"이 아니라 **8 GAP 이 machinery 로 해소/표현 가능해졌음의 before/after 입증**이다.

---

## F. 금지 / 격리 확인

- machinery 문서(generation_workflow / architecture_patterns / domain_brief_schema / templates/* / harness_blueprint_schema) — **읽기만, 0줄 변경**.
- 변경 파일 전부 `meta_factory/outputs/TEST/podcast/**` 하위 (신규 본 리포트 1 + additive 6). `사진/`(untracked) 무시.
- backend/fastapi, apps/web, db/migrations, docs/contracts, AGENTS/CLAUDE, .claude/skills, meta_factory root machinery·templates·blueprints, outputs/{generated_harnesses,improvement_reports}, eval, phases, 이전 ADR — **변경 0**.
- 자격증명/키 — 0 (placeholder 만).

---

이 재검증 리포트는 S1·S2 가 meta_factory machinery 에 반영한 8 GAP 개선(읽기 전용)을 M1 팟캐스트 TEST 산출물에 additive 재적용하여 작성됨. machinery 0줄 변경, 산출물은 문서(.md)만, 런타임/기존 하네스 0줄 변경 (A9).
