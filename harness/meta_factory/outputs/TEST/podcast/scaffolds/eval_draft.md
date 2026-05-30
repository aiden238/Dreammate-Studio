# eval_draft.md — golden_set + 채점차원 + 임계값 scaffold (팟캐스트)

> 위치: `harness/meta_factory/outputs/TEST/podcast/scaffolds/eval_draft.md`
> 기반: `meta_factory/templates/eval_template.md`
> 상태: Phase M1 S1 dry-run scaffold (active 아님 — 실 평가는 eval-run, golden_set 갱신은 contract-change 경유)
> 대상 예시: golden_set 케이스 1개(PE-002 인터뷰) + 채점 차원 + 임계값

---

## A. golden_set 케이스 (eval_template §A 채움)

```yaml
case_id: PE-002                      # 고정 ID — 한 번 부여 후 변경 금지 (재사용 금지)
name: "인터뷰 포맷 단발 에피소드 — 게스트 모드 기획안 3개 + 질문 리스트"
priority: P0                         # P0 필수 100%
input:
  user_message: "스타트업 창업자 게스트와 '실패에서 배운 것' 주제 인터뷰 에피소드 기획해줘"
  show_context: { format_default: interview, target: "예비 창업자", tone: "솔직/공감" }
expected_path:
  - intent (mode=single, missing_fields: 게스트명/길이)
  - planning (episode_plan_candidates x3, format=interview)
  - guest_brief (게스트 모드 — guest_seed 있으면 생성)
  - question (question_list, cliche_flag)
  - shownotes (shownotes + title_candidates)
  - critic (overall_verdict, dimensions 10)
expected_output:
  body_keys: [episode_plan_candidates, guest_brief, question_list, shownotes, critic]
  validation:
    - episode_plan_candidates 길이 == 3
    - 각 candidate 에 angle / segment_flow[] / opening_hook 존재
    - question_list 비어있지 않음 + 각 항목 cliche_flag 존재
    - critic.dimensions 에 opening_hook_strength / conversation_flow / question_quality / guest_fit 포함
  passing_criteria:
    - schema 준수 100%
    - critic.overall_score >= 임계 (eval-run §6)
notes:
  - 게스트 모드 +2 차원(question_quality/guest_fit) 동작 검증용
  - guest_seed 미제공 시 guest_brief 는 graceful skip (날조 금지 — llm_security)
```

---

## B. 채점 차원 (eval_template §B — 도메인별, Dreammate 8 → 팟캐스트 10)

```
intent_fit              # 동일                       (무조건 차원 — 항상 채점)
target_clarity          # 동일                       (무조건 차원)
opening_hook_strength   # 썸네일 후킹 → 오프닝 멘트/질문 후킹  (무조건 차원)
message_clarity         # 동일                       (무조건 차원)
conversation_flow       # 영상 flow → 오디오 대화 흐름 자연스러움 (무조건 차원)
recording_feasibility   # 녹음 현실성 (길이/포맷)         (무조건 차원)
brand_consistency       # 동일                       (무조건 차원)
differentiation         # 동일                       (무조건 차원)

# ★ M2 G-fix 적용 (G4 — eval_template §B applies_when). M1 은 조건부 차원을 notes(§GAP)로 우회 → applies_when 1급 표현:
question_quality:                     # ★ 조건부 — 질문 진부도/깊이
  applies_when: mode == guest         # 게스트 모드일 때만 채점. 미해당 시 이 케이스 평균 계산에서 제외(0점 끌어내리기 X)
guest_fit:                            # ★ 조건부 — 게스트-주제 적합성
  applies_when: mode == guest         # 게스트 모드일 때만 채점. 미해당(솔로/패널-무게스트) 시 평균에서 제외
# → 무조건 8차원 + 조건부 2차원(applies_when). 솔로 모드 케이스 평균 = 8차원 기준, 게스트 모드 = 10차원 기준 (적용 차원 수로 평균).
```

---

## C. 임계값 (eval_template §C / eval-run §6 정합)

| 지표 | 임계값 | 위반 시 |
|------|--------|---------|
| schema 준수율 | < 100% | 즉시 fail, rollback |
| 평균 점수 하락 | > 0.3 | fail, 사람 검토 |
| 비용 증가 | > 30% | cost-review 트리거 |
| latency 증가 | > 20% | 경고 |
| 차단 단어 검출 | > 0% | fail |

---

## 작성 가이드 점검 (eval_template §작성가이드)

1. ✅ case_id 고정 (PE-002) — 변경 금지, 추가 시 다음 번호.
2. ✅ priority P0 — 필수 100%.
3. ✅ schema 준수 100% 1차 게이트.
4. ✅ 채점 차원 도메인별 (10 — 조건부 2 포함).
5. ✅ 임계값 eval-run §6 정합.
6. ✅ mock-deterministic primary (CI 비용 0) + 실 LLM flag.
7. ✅ golden_set 갱신은 contract-change 경유.
8. ★ outputs/ 에 먼저, 실 실행은 eval-run (eval-run > harness-factory validation).

## ★ GAP 관찰 (G4)

채점 차원이 **조건부**(게스트 모드일 때만 question_quality/guest_fit) — eval_template §B 는 고정 N 차원 전제.
조건부 차원의 "해당 없음 시 채점 제외" 규칙을 template 이 직접 지원하지 않음 → notes 로 우회. S2 eval-run 연동 관찰점.

### ✅ M2 G-fix 해소 (G4, S3 re-validate)
- S2 가 `eval_template.md §B` 에 `applies_when` 속성을 추가(조건부 차원 + 미해당 시 평균 제외 규칙) → 위 §B 채점 차원에서 question_quality/guest_fit 를 **notes 우회 없이 `applies_when: mode == guest` 로 1급 표현**.
- 해소 판정: **addressed** — "해당 없음 시 채점 제외"가 template 규칙으로 명문화되어 적용 차원 수 기준 평균이 가능 (미해당 차원이 평균을 0점으로 끌어내리지 않음). M1 의 notes 우회가 schema 슬롯으로 대체됨.
