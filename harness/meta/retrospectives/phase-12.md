# Phase 12 회고 — 검증 페이즈 (Validation — MVP 출력 품질·가치 실측)

> 종료일: 2026-06-02
> 유형: 검증/계획 phase (런타임 0 — 측정·문서만) — ★ behavior-preserving (운영 endpoint/agent/prompt/schema 0 수정, pytest 471 유지)
> 결과: ✅ 깊이 격차 정량 실측(compact 0.231 vs rich 1.000 = 4.3x, 6/6 편차 0) + 결론(단순함 = 모델 한계 아님, prompt/schema 설계) + golden_set 15→25 + depth_actionability 차원(CC-011) + S4 human review kit / ★ S4 사용자 실 채점 = deferred (사용자 2026-06-02 실 UI 격차 직접 확인으로 결론 확정)
> 트리거: phase-complete v1.2.0 §7

---

## 1. 무엇을 했나 (Entry + 5 Slice)

- **Entry**: phase entry 8파일(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) + multi-llm-validation self(11th, V1~V6). Phase 12 active + 깊이 격차 핵심 GAP 정의.
- **S1 (`8ad9594`)**: golden_set 15→**25** 확장(신규 ~10, 기존 15 회귀 보존, additive) + eval rubric 에 **depth_actionability** 평가 차원 정식 등록(`eval/video_planning_eval.md` §2.A.1) → contract-change **CC-011**(`docs/contract_changes/2026-06-02_phase-12-s1-golden-set-depth.md`). 측정 기반 확장.
- **S2+S3 (`ef165bb`)**: 깊이 격차 실측 — 같은 모델(gpt-4o-mini) compact(실 운영 `run_planning()` 그대로, 운영 코드 0 수정) vs rich(확장 측정-프롬프트), golden_set 도메인 대표 6, depth_actionability 13 feature(0/1 존재) 채점 → **compact 0.231 vs rich 1.000 = 4.3x, 6/6 편차 0**. compact 결핍 10/13 feature. (`eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md`)
- **S4 (`f991b0e`)**: human review kit — compact vs rich 실출력 3케이스 + 5차원 채점 시트(LLM-as-judge ↔ human 점수 대조 설계). (`eval/human_review/2026-06-02_phase-12-s4-review-kit.md`) ★ **사용자 실 채점은 deferred**(kit 준비 = acceptance).
- **S5 (`f3b25e8`)**: 검증 종합 + Phase 13 확장 우선순위 제안. (`phases/active/phase-12-validation/s5_synthesis_and_phase13_proposal.md`)
- **종료(본 회고)**: retrospective + closing_notes + archive 이동 + REGISTRY/PROJECT_STATE done. ★ 운영 코드 0 변경.

## 2. 핵심 결과

- **깊이 격차 = 실재하고 크다 (4.3배).** 같은 모델(gpt-4o-mini)인데 프롬프트만 바꿔 0.231 → 1.000. 6/6 케이스 완전 일관(편차 0) — 도메인 무관, 구조적 격차.
- **결론: 단순함은 모델 한계가 아니라 prompt + schema 설계의 결과.** (2026-06-02 라이브 데모 가설 → S2/S3 다수 표본으로 확정.)
- **결핍 10/13 feature** 중 다수(대사·자막·샷·썸네일·제목·레퍼런스·길이변형)는 **출력 스키마(`Plan`)에 슬롯 자체가 없어** 모델이 생성해도 담기지 않는다 → **스키마 확장**이 프롬프트 확장과 함께 필요 (= Phase 13 레버 정의).
- **golden_set 15→25** + **depth_actionability 차원(CC-011)** — 측정 기반(additive, 기존 회귀 보존). 깊이 측정의 정식 rubric 확보.
- **88점 함정 발견**: compact 출력이 Critic 88점을 받아도 depth(0.231)는 반영 안 됨 — Critic 평가 체계가 얕음을 감점하지 않음. Phase 13 S4(Critic depth 반영)의 근거.
- **pytest 471 유지** + 운영 코드 0 변경 + 키 0 — 검증이 운영 동작을 절대 바꾸지 않음(behavior-preserving).

## 3. 잘된 것

1. **가설 → 수치 확정의 정직한 사이클** — "단순함=모델 한계 아니라 설계 선택"이라는 라이브 데모 가설을, golden_set 6 도메인 표본 + 13 feature 구조 채점으로 0.231/1.000(4.3x, 편차 0)로 일반화. 데모(단일 표본)에 머물지 않고 측정으로 robust 화.
2. **운영 코드 0 수정으로 깊이 격차 측정** — compact 는 실 운영 `run_planning()`을 import 만(수정 0), rich 는 측정 전용 프롬프트(운영 prompt_registry/output_schema 0 반영). 검증이 측정 대상을 오염시키지 않음(P-CAPABILITY-DEFAULT-OFF-001 정신).
3. **결핍의 원인 분해** — 단순히 "얕다"가 아니라 feature별로 (a) compact 보유 3 / (b) 프롬프트만으로 채워지는 것(타깃·톤·후크변형) / (c) **스키마 슬롯 부재**(대사·자막·샷·썸네일 등)로 분해 → Phase 13 의 레버를 "프롬프트 + 스키마" 둘 다로 정확히 지목.
4. **정직한 캘리브레이션** — rich=1.00 은 "이만큼 가능"의 상한선이지 "최적"이 아님을 명시 + 구조 채점(존재 0/1)은 품질 아님을 한계로 기록 → human review(S4)로 보정 설계. 측정 과신 회피.
5. **S4 deferred 의 화해** — kit 준비를 acceptance 로, 실 채점을 deferred 로 분리. 사용자가 2026-06-02 실 UI(/generate)로 compact 출력 + Critic 88점이 depth 미반영임을 **직접 확인**했으므로 검증 결론은 이미 확정 — kit 은 optional 보정(LLM-as-judge 신뢰도 대조)으로 보존. 산출을 막지 않으면서 신뢰도 보강 경로 유지.

## 4. 아쉬운 것 / 한계

1. **S4 human review 실 채점 미완** — kit 까지가 Phase 12 산출(NG7). 사용자 실 채점 ↔ LLM-as-judge 대조 분석은 후속(Phase 13 S6 재측정과 묶거나 별도). 단, 사용자 실 UI 직접 확인으로 결론은 확정 — 채점은 자동 점수 신뢰도 보정 용도.
2. **구조 채점의 품질 미반영** — depth_actionability 13 feature 는 **존재 여부**(0/1)만 본다. "대사가 있어도 진부할 수 있음" — 품질 채점은 human review / LLM-as-judge 보강 대상. rich=1.0 의 의미 = 슬롯 충족이지 콘텐츠 우수성 아님.
3. **표본 6** — golden_set 25 중 대표 6. 일관성(편차 0)이 높아 방향성은 robust 하나, 전수(25) 실 LLM eval baseline(MO1)은 비용·범위로 축소 — Phase 13 S6 재측정에서 보강.
4. **cost 재조정 미실행** — rich = 출력 토큰 ↑ × 3안 = 비용 배수. cost_control_policy 재조정(B안 잔여 B-RES-1 연동)은 측정만 하고 정책 갱신은 Phase 13 S6 로 이관.
5. **B안(Phase 11) 정식화 잔여 미해소** — B-RES-1(cost 재조정)/B-RES-2(ADR)/B-RES-3(contract-change)는 추적 항목으로만 남김(비차단). Phase 13 dependencies 로 승계.

## 5. 패턴

- **P-VALIDATION-DEPTH-GAP-001 (신규 후보)** — 같은 모델·같은 비용 근방에서 **prompt/schema 설계만으로 출력 가치 격차를 정량 측정**(compact vs rich, feature 구조 채점 0/1 → depth 비율) → 확장 ROI·우선순위의 데이터 근거. 운영 코드 0 수정(측정 전용 프롬프트) + 정직한 캘리브레이션(상한선 명시·품질 미반영 한계). "모델 한계인가 설계 선택인가"를 수치로 분리.
- **P-BEHAVIOR-PRESERVING-001 update** — 검증 phase 에서도 운영 endpoint/agent/prompt/output_schema 0 수정 + eval = 측정 capability(runner 직접 호출, 운영 미경유). pytest 471 유지(신규 test 0 — 문서·eval 데이터만).
- **P-CAPABILITY-DEFAULT-OFF-001 update** — rich = 측정 전용(운영 0 반영), 실 LLM eval = 측정 1회(CI mock 게이트 유지). capability(측정) vs 발화(운영 반영) 분리 — 측정이 운영을 바꾸지 않음.
- **P-CONTRACT-FIRST-001 update** — CC-011(golden_set 25 + depth_actionability 차원 additive) 누적 12회.
- **P-X1-EFFECT-001 update** — Entry·S1~S5 sub-agent forbidden 검사 연속(운영 코드 0, behavior-preserving).

## 6. 다음 단계 — Phase 13 (Output Enrichment)

- **Phase 13 = 출력 확장(compact→rich)** — Phase 12 가 입증한 깊이 격차(0.231→잠재 1.0)를 **운영 출력에 반영**. ★ 이 프로젝트 **첫 의도적 출력 변경** phase — 그래서 **gated 단계 롤아웃 + additive 스키마**로 안전하게.
  - S1 스키마 확장(`Plan` 결핍 feature optional/additive 슬롯) / S2 프롬프트 확장(P-006 bump, prompt-version-review) / S3 gated wiring(`rich_output_enabled` default OFF) / S4 Critic depth 반영(88점 함정 해소) / S5 frontend 렌더링(/generate 화면 rich) / S6 cost 재조정 + 깊이 재측정(목표 ≥0.8) + 종료.
  - 롤아웃 = **gated**(flag default OFF → 검증 후 ON). 범위 = **풀**(backend + frontend). 제품 경계 = **기획 브리프**(완성 대본/제작 아님, product_boundary).
- **S4 human review 실 채점 + LLM-as-judge 신뢰도 대조** — Phase 12 kit 활용(Phase 13 S6 재측정과 묶음 가능).
- **B안 정식화 잔여(B-RES-1~3)** — Phase 13 S6 cost 재조정에 B-RES-1 흡수 + ADR/contract-change.

## 7. 메타 정합

- 검증 phase = "동작한다"(구조 정확성, Phase 1~11) → "충분히 깊은가"(출력 품질·가치)로 측정 축 전환. 추측이 아닌 데이터로 확장 우선순위 결정.
- behavior-preserving + 측정 전용 + 키 0 — 검증이 운영을 바꾸지 않음(제품 안정화 규율 유지).
- ★ Phase 1~12 = MVP 통합(Phase 10) + LLM Gateway(Phase 11) + 검증(Phase 12). 다음 = Phase 13 출력 확장(gated, additive, 첫 의도적 출력 변경).
