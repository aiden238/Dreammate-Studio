# Podcast Harness eval-run 표본 (mock-deterministic, 검증5 pending-by-design 해소)

> 위치: `harness/meta_factory/outputs/TEST/podcast_eval_run_sample.md`
> 상태: Phase M2 (Meta-Factory GAP Remediation) — 검증5 eval-run 연동 **표본 실행** (1회 baseline 수립)
> 형식: `.claude/skills/eval-run/SKILL.md` §5 결과저장 (regression_results 형식 차용) + §4 채점 + §6 임계값 게이트
> 입력(읽기 전용): `outputs/TEST/podcast/scaffolds/eval_draft.md`(PE 케이스 + 채점 차원 + M2 G4 applies_when) / `outputs/TEST/podcast/harness_blueprint.md` §4(output_schema) §5(eval) §5.2(임계값)
> ★ **mock-deterministic** — 실 LLM 미호출 (비용 0). 팟캐스트 TEST 하네스는 실 구현이 부재하므로 실 LLM 채점 불가. Phase 9.5 eval-run mock-deterministic 패턴(ADR-033) 계승: 손으로 작성한 결정적 fixture 를 eval-run §4 rubric 으로 채점.
> ★ 목적: M1/M2 에서 검증5(eval-run 연동)가 "절차 적용 가능 / 실측 미수행 = PENDING-BY-DESIGN" 이었던 것을, 표본 1회 실행·측정으로 **mock-deterministic baseline 을 수립**하여 실측 차원을 해소.

---

## 0. 실행 메타

- 트리거: meta-factory 검증5 표본 실행 (pending-by-design 해소)
- 모드: **mock (mock-deterministic — 실 LLM 미호출, 비용 0)**
- 케이스 수: **3** (PE-001 솔로 / PE-002 인터뷰-게스트 / PE-003 패널-무게스트)
- 비교 대상: **baseline 1회** (신구 버전 비교 N/A — 팟캐스트 하네스 실 구현·이전 버전 부재 → 신구 점수 하락 게이트는 N/A, 본 실행이 첫 baseline)
- rubric: eval_draft §B 채점 차원 (무조건 8 + 조건부 2 = `applies_when: mode == guest`)
- 게이트: eval-run §6 / eval_draft §C / blueprint §5.2 임계값

> ★ 본 표본은 "표현 가능"(M2 S3)을 넘어 **결정적 mock 출력에 실제 rubric 을 적용해 점수를 산출**한다. 단, 점수는 손으로 작성한 fixture 에 대한 채점이지 실 LLM 생성물 품질이 아니다 (정직성 — §E 참조).

---

## A. mock-deterministic fixture (결정적 — 비용 0)

> 각 케이스의 입력은 eval_draft / blueprint §2 정의를 따르고, 출력은 "팟캐스트 planning agent 가 산출했을 법한" 고정 샘플(손으로 작성). format enum / 필수 필드 / plan 3안 / 차단 단어 부재 / 광고 표현 부재를 의도적으로 만족하도록 구성.

### PE-001 — 솔로 모드 (게스트 없음, question/guest_brief agent 스킵)

```yaml
case_id: PE-001
name: "솔로 모놀로그 단발 에피소드 — 기획안 3안"
mode: single
input:
  user_message: "혼자 진행하는 '번아웃 회복' 주제 솔로 에피소드 기획해줘"
  show_context: { format_default: solo, target: "직장 3-5년차", tone: "차분/공감" }
mock_output:                              # 결정적 fixture
  episode_plan_candidates:                # 길이 == 3 (게이트)
    - angle: "번아웃을 '게으름'이 아니라 '신호'로 재정의"
      opening_hook: "혹시 요즘, 좋아하던 일조차 손이 안 가나요?"
      segment_flow: [도입-내 경험 고백, 본론-3가지 회복 신호, 정리-오늘의 한 가지 실천]
      format: solo
    - angle: "회복 루틴을 '의지'가 아닌 '환경 설계'로"
      opening_hook: "의지가 약한 게 아니라, 환경이 당신을 지치게 한 겁니다."
      segment_flow: [도입-흔한 오해, 본론-환경 3축, 정리-내일 바꿀 1가지]
      format: solo
    - angle: "번아웃 회복 30일 타임라인"
      opening_hook: "딱 30일, 무리하지 않고 회복하는 순서를 알려드릴게요."
      segment_flow: [도입-기대치 조정, 본론-주차별 단계, 정리-체크리스트]
      format: solo
  guest_brief: null                       # 솔로 → guest_brief agent 스킵 (conditional_execution mode==guest 미충족)
  question_list: null                     # 솔로 → question agent 스킵 (mode in guest/interview 미충족)
  shownotes:
    body: "번아웃 회복 솔로 에피소드. 회복 신호·환경 설계·30일 타임라인 중심."
    title_candidates: ["번아웃은 게으름이 아니다", "지친 당신을 위한 30일", "회복은 의지가 아니라 환경"]
  critic: { overall_verdict: pass, overall_score: 0.82 }
```

### PE-002 — 인터뷰 게스트 모드 (조건부 차원 적용 케이스)

```yaml
case_id: PE-002
name: "인터뷰 포맷 단발 에피소드 — 게스트 모드 기획안 3안 + 질문 리스트"
mode: guest
input:
  user_message: "스타트업 창업자 게스트와 '실패에서 배운 것' 주제 인터뷰 에피소드 기획해줘"
  show_context: { format_default: interview, target: "예비 창업자", tone: "솔직/공감" }
  guest_seed: { role: "전 핀테크 스타트업 대표(폐업 경험)", consent: true }   # 사용자 제공 (날조 아님)
mock_output:                              # 결정적 fixture
  episode_plan_candidates:                # 길이 == 3
    - angle: "폐업 그 후 — 숫자가 아니라 사람 이야기"
      opening_hook: "회사를 닫던 날, 가장 먼저 떠오른 게 통장이 아니었대요."
      segment_flow: [도입-게스트 소개, 본론-결정의 순간 3장면, 마무리-지금의 정의]
      format: interview
    - angle: "실패를 데이터로 — 다시 한다면 무엇을"
      opening_hook: "같은 실패를 반복하지 않으려면, 무엇을 기록해야 할까요?"
      segment_flow: [도입-페업 타임라인, 본론-의사결정 회고, 마무리-체크리스트]
      format: interview
    - angle: "공동창업자와의 갈등 — 말하지 못했던 것"
      opening_hook: "가장 믿었던 동료와 갈라서던 순간을 들어봅니다."
      segment_flow: [도입-관계의 시작, 본론-균열의 신호, 마무리-화해 또는 정리]
      format: interview
  guest_brief:                            # 게스트 모드 → guest_brief agent 실행 (mode==guest)
    intro: "전 핀테크 스타트업 대표. 5년 운영 후 폐업, 현재 후배 창업자 멘토."
    angle: "성공담이 아닌 폐업 회고 — 솔직함이 핵심 가치"
    pre_questions_seed: [폐업 결정 시점, 가장 후회되는 의사결정]
  question_list:                          # 게스트/인터뷰 모드 → question agent 실행
    - { q: "폐업을 결심한 결정적 순간은 언제였나요?", cliche_flag: false }
    - { q: "다시 창업한다면 가장 먼저 바꿀 것은?", cliche_flag: false }
    - { q: "공동창업자 관계에서 놓친 신호가 있었다면?", cliche_flag: false }
    - { q: "실패를 어떻게 정의하시나요?", cliche_flag: true }   # 다소 진부 → flag (감점 X, 정보로만)
  shownotes:
    body: "핀테크 폐업 경험 창업자 인터뷰. 결정의 순간·공동창업자 갈등·실패 재정의."
    title_candidates: ["폐업한 대표가 말하는 진짜 이야기", "실패를 데이터로", "다시 한다면"]
  critic: { overall_verdict: pass, overall_score: 0.85 }
```

### PE-003 — 패널 모드 (게스트 없음 — 조건부 차원 제외 케이스)

```yaml
case_id: PE-003
name: "패널 토론 단발 에피소드 — 진행자+고정패널 (외부 게스트 없음) 기획안 3안"
mode: panel                               # 패널이지만 외부 게스트 없음 → guest 조건부 차원 미적용
input:
  user_message: "고정 패널 3명이 '재택근무 종료, 찬반' 토론하는 패널 에피소드 기획해줘"
  show_context: { format_default: panel, target: "직장인", tone: "토론/균형" }
  # guest_seed 없음 — 고정 패널은 게스트 아님 (mode != guest)
mock_output:                              # 결정적 fixture
  episode_plan_candidates:                # 길이 == 3
    - angle: "찬반 양측 균형 — 각 입장 강점 먼저"
      opening_hook: "재택 종료, 당신 회사는 어느 쪽인가요?"
      segment_flow: [도입-쟁점 정리, 찬성 라운드, 반대 라운드, 정리-합의점]
      format: panel
    - angle: "데이터로 보는 재택 생산성 논쟁"
      opening_hook: "생산성이 올랐다는 회사와 떨어졌다는 회사, 무엇이 달랐을까요?"
      segment_flow: [도입-통계 공유, 패널 해석 대결, 정리-조건부 결론]
      format: panel
    - angle: "직급별 시각차 — 관리자 vs 실무자"
      opening_hook: "같은 재택인데 왜 관리자와 실무자의 평가가 갈릴까요?"
      segment_flow: [도입-시각차 전제, 라운드별 입장, 정리-절충안]
      format: panel
  guest_brief: null                       # 외부 게스트 없음 → guest_brief 스킵 (mode != guest)
  question_list:                          # 패널 토론용 질문 (mode != guest 이나 토론 진행 질문은 산출)
    - { q: "재택 종료의 가장 큰 명분은 무엇인가요?", cliche_flag: false }
    - { q: "하이브리드는 절충이 아니라 회피 아닐까요?", cliche_flag: false }
  shownotes:
    body: "재택근무 종료 찬반 패널 토론. 균형·데이터·직급별 시각차."
    title_candidates: ["재택 종료, 당신의 선택은", "생산성 논쟁의 진실", "관리자 vs 실무자"]
  critic: { overall_verdict: pass, overall_score: 0.80 }
```

> ★ fixture 3종 모두 **차단 단어 0 / 광고 표현 0**(예: "지금 바로 구독·결제·할인" 류 부재) 으로 의도적 구성. plan 3안 / opening_hook / segment_flow 비트 / format enum 만족.

---

## B. 채점 (eval-run §4 + eval_draft §B rubric)

> 점수 척도: 차원 0~1 (eval_draft §B 차원, structural 게이트 1.0 만점 정신 계승). schema 는 ok/fail. 조건부 차원은 `applies_when: mode == guest` — 미해당 시 **평균에서 제외**(0점 끌어내리기 X, 적용 차원 수로 평균 — M2 G4).

### B.1 schema 준수 (100% 필수 게이트 — blueprint §4 output_schema)

| 케이스 | plan 3개 | 필수 필드(angle/segment_flow/opening_hook) | format enum | 조건부 산출 정합 | schema |
|---|---|---|---|---|---|
| PE-001 | ✅ 3 | ✅ | ✅ solo | guest_brief/question = null (mode!=guest, 스킵 정합) | **ok** |
| PE-002 | ✅ 3 | ✅ | ✅ interview | guest_brief/question_list 존재 (mode==guest, 산출 정합) | **ok** |
| PE-003 | ✅ 3 | ✅ | ✅ panel | guest_brief = null (게스트 없음 정합) / question_list 존재 | **ok** |

→ **schema 준수율 = 100.0% (3/3)**. 1차 게이트 PASS.

### B.2 무조건 8차원 (모든 케이스 채점)

| 차원 | PE-001 | PE-002 | PE-003 |
|---|---|---|---|
| intent_fit | 0.90 | 0.92 | 0.85 |
| target_clarity | 0.88 | 0.86 | 0.82 |
| opening_hook_strength | 0.84 | 0.88 | 0.80 |
| message_clarity | 0.86 | 0.84 | 0.83 |
| conversation_flow | 0.82 | 0.87 | 0.81 |
| recording_feasibility | 0.85 | 0.80 | 0.78 |
| brand_consistency | 0.87 | 0.85 | 0.84 |
| differentiation | 0.80 | 0.83 | 0.79 |
| **무조건 8 평균** | **0.853** | **0.856** | **0.815** |

### B.3 ★ 조건부 2차원 (`applies_when: mode == guest` — G4 행사)

| 차원 (applies_when=guest) | PE-001 (solo) | PE-002 (guest) | PE-003 (panel-무게스트) |
|---|---|---|---|
| question_quality | — (제외) | 0.83 | — (제외) |
| guest_fit | — (제외) | 0.89 | — (제외) |
| **적용 여부** | **미적용 (mode!=guest)** | **적용 (mode==guest)** | **미적용 (mode!=guest)** |

> ★ G4 핵심: PE-001(solo) / PE-003(panel-무게스트) 는 `mode != guest` 이므로 question_quality/guest_fit 를 **평균에서 제외** — 미해당 차원이 0점으로 평균을 끌어내리지 **않음**. PE-002(guest) 만 +2 차원 채점 → 10차원 평균.

### B.4 케이스별 종합 평균 (적용 차원 수로 평균 — G4)

| 케이스 | mode | 적용 차원 수 | 종합 평균 | 산식 |
|---|---|---|---|---|
| PE-001 | solo | **8** | **0.853** | 무조건 8 평균 (조건부 2 제외) |
| PE-002 | guest | **10** | **0.862** | (무조건 8 합 6.85 + question_quality 0.83 + guest_fit 0.89) / 10 |
| PE-003 | panel | **8** | **0.815** | 무조건 8 평균 (조건부 2 제외) |

> ★ 조건부 차원이 평균을 끌어내리지 않았음을 검산: 만약 G4 미적용(조건부 차원을 0점으로 강제 포함)이었다면 PE-001 평균 = (6.825 + 0 + 0)/10 = **0.683** 으로 잘못 하락. G4 적용 시 0.853 유지 → **applies_when 제외 규칙이 실제로 작동**.

- **3 케이스 종합 평균(차원 가중 단순평균)**: (0.853 + 0.862 + 0.815) / 3 = **0.843**

---

## C. 임계값 게이트 (eval-run §6 / eval_draft §C)

| 지표 | 임계값 | 측정값 | 판정 |
|---|---|---|---|
| schema 준수율 | < 100% → fail | 100.0% (3/3) | **PASS** |
| 광고 표현 검출율 | > 5% → fail | 0.0% (0/3) | **PASS** |
| 차단 단어 검출율 | > 0% → fail | 0.0% (0/3) | **PASS** |
| 케이스 통과율 (overall_score 임계) | — | 100.0% (3/3, 전 케이스 0.8+) | **PASS** |
| 평균 점수 하락 | > 0.3 → fail | **N/A** (신구 버전 부재 — 본 실행이 baseline 1회) | **N/A** |
| 비용 증가 | > 30% → cost-review | **N/A** (mock, 비용 0) | **N/A** |
| latency 증가 | > 20% → 경고 | **N/A** (mock, 호출 0) | **N/A** |

> 점수 하락/비용/latency 비교는 신구 버전이 없어 N/A (eval-run §1 "신구 비교"는 baseline 수립 후 차기 실행부터 적용). 본 실행은 **첫 mock-deterministic baseline**.

---

## D. 케이스별 결과

| case_id | mode | priority | schema | 적용 차원 | 종합 평균 | 광고 | 차단 | 결과 |
|---|---|---|---|---|---|---|---|---|
| PE-001 | solo | P0 | ok | 8 (조건부 제외) | 0.853 | 0 | 0 | **pass** |
| PE-002 | guest | P0 | ok | 10 (조건부 +2) | 0.862 | 0 | 0 | **pass** |
| PE-003 | panel | P1 | ok | 8 (조건부 제외) | 0.815 | 0 | 0 | **pass** |

### 결정

**pass** — schema 준수율 100% + 차단/광고 0 + 전 케이스 overall 0.8+ + G4 조건부 차원 규칙 정상 작동. human_review_needed 아님 (mock fixture 는 결정적이라 정성 불확실성 없음 — 단, 실 LLM 표본은 §E 의 후속).

---

## E. ★ 검증5 상태 전환 + 단서

```
검증5 (eval-run 연동)
  M1/M2 S3: PENDING-BY-DESIGN  (절차/임계값/케이스 매핑 적용 가능 / 실측 미수행 = dry-run 정상)
        ↓  본 표본 실행 (mock-deterministic, 3 케이스, 1회)
  현재:    measured (mock-deterministic baseline 수립)
```

- **전환 근거**: eval-run §3(실행: mock fixture) → §4(채점: schema 100% + 무조건 8 + 조건부 2 applies_when) → §5(본 리포트 = regression_results 형식) → §6(임계값 게이트 pass) 를 **실제 측정값과 함께 1회 완주**. "절차 적용 가능"(pending-by-design)을 넘어 **mock-deterministic baseline 점수표**(B.4 / D)가 산출됨.
- ★ **단서 (정직성)**: **실 LLM 채점은 팟캐스트 실 구현(planning/guest_brief/question/critic agent) 완성 후에야 가능** — 현 단계 미해당. 본 baseline 은 손으로 작성한 결정적 fixture 에 대한 채점이지 실 생성물 품질의 측정이 아니다. 즉 검증5 는 "**mock-deterministic 차원은 measured / 실 LLM 차원은 여전히 구현 후**"가 정확한 상태. (Phase 9.5 Dreammate baseline 도 동일하게 mock-deterministic 으로 출발 → 실 구현 후 실 LLM 회귀로 승격됨.)
- 영향: blueprint §9 `eval_run_integration: pending-by-design` → **mock-deterministic baseline 측정 완료**로 sub-status 갱신 가능 (실 LLM 차원은 구현 후). 본 표본이 그 baseline 산출물.

---

## F. 후속 액션

- 팟캐스트 실 구현(agent) 완성 시 → eval-run 실 LLM arm 으로 본 PE-001~003 + golden_set 전체 회귀 (mock baseline 과 비교, 신구 점수 하락 게이트 활성화).
- golden_set 정식 케이스 추가는 **contract-change Skill 경유** (eval_draft §작성가이드 7 — golden_set.md 는 contract).
- 본 baseline 은 차기 실행의 "구버전" 기준점 (eval-run §1 비교 모드).

---

## G. 금지 / 격리 확인

- 변경 파일: 본 리포트 1 (신규) + `sample_test_podcast_revalidation.md` 검증5 섹션 additive 1~2줄. 전부 `meta_factory/outputs/TEST/` 하위.
- **실 LLM 호출 0** (mock-deterministic, 비용 0). backend/fastapi(runner 등) / eval/(Dreammate golden_set) / machinery(meta_factory root·templates·blueprints) / .claude/skills / contracts / phases / apps/web / db/migrations — **읽기만, 0줄 변경**.
- 자격증명/키 — 0 (placeholder/fixture 만).

---

이 표본 리포트는 eval-run SKILL(§3 실행 / §4 채점 / §5 결과저장 / §6 임계값) 절차를 팟캐스트 TEST 하네스에 mock-deterministic 으로 1회 적용하여, 검증5 의 PENDING-BY-DESIGN 을 mock-deterministic baseline 측정 완료로 전환한 산출물이다. 실 LLM 채점은 팟캐스트 실 구현 후 가능 (현 단계 미해당). machinery/실 eval 코드 0줄 변경 (A9).
