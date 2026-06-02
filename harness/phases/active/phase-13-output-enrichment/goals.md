# Phase 13 — Goals (출력 확장 / Output Enrichment — compact→rich)

> Phase: phase-13-output-enrichment
> 유형: **제품 phase (런타임 有 — ★ 이 프로젝트 첫 의도적 출력 변경)** — 그래서 **gated 단계 롤아웃 + additive 스키마**로 안전하게 (flag OFF 시 compact byte-identical, behavior-preserving)
> 진입일: 2026-06-02 (entry 작성 — phase-start 정식 진입)
> 결정 근거: Phase 12 검증 결론(깊이 격차 4.3x 실측 — `eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md` + `phases/archive/phase-12-validation/s5_synthesis_and_phase13_proposal.md`) + 사용자 확정(롤아웃=gated / 범위=풀)

## 한 줄 정의

Phase 12 가 입증했다 — MVP 출력의 단순함은 **모델 한계가 아니라 prompt/schema 설계 선택**이다(같은 모델 gpt-4o-mini, depth 0.231 → 1.000 = 4.3x, 6/6 편차 0). Phase 13 은 그 격차를 **운영 출력에 실제로 반영**한다: compact 7필드 → rich(후크 변형·타임코드·화면·대사·자막·샷·썸네일·제목·CTA·레퍼런스·길이변형·타깃·톤). ★ 이 프로젝트 **첫 의도적 출력 변경** phase — 그래서 **gated 단계 롤아웃**(flag default OFF → 검증 후 ON) + **additive 스키마**(전부 Optional, 기존 소비자 회귀 0)로 안전하게. ★ 제품 경계 유지: 확장본도 **"기획 브리프"**(촬영·편집 가이드)지 완성 대본/영상 제작 아님(product_boundary).

## ★ 핵심 = 깊이 격차를 "운영 출력"에 반영 (Phase 12 → Phase 13)

```
Phase 12 (측정):  compact 0.231  vs  rich 1.000 (4.3x) — 측정 전용 프롬프트로 입증
                  결핍 10/13 feature, 다수가 출력 스키마(Plan) 슬롯 부재
                          ↓
Phase 13 (반영):  결핍 feature 를 Plan 스키마 슬롯(optional/additive) + 프롬프트(P-006 bump)로 추가
                  → 운영 출력 depth 0.231 → 목표 ≥0.8 (rich 경로)
                  ★ 단, gated — rich_output_enabled=False 면 compact 100% 동일(byte-identical)
                    → 검증 후 flag ON (default ON 즉시 전환은 별도 결정, NG)
```

## 측정 목표 (MO1~MO3)

| ID | 측정 목표 | 산출 | Slice |
|---|---|---|---|
| **MO1** | **depth 재측정: 0.231 → ≥0.8** — golden_set depth_actionability(CC-011) 재측정으로 rich 경로가 목표 깊이 달성 확인 | depth 재측정 리포트 | S6 |
| **MO2** | **flag OFF 회귀 0 (byte-identical)** — `rich_output_enabled=False` 면 기존 compact 출력 100% 동일(Envelope byte-identical) | OFF 경로 회귀 test + pytest green | S3·S6 |
| **MO3** | **Critic depth 반영** — depth_actionability 차원 추가로 얕은 출력이 더는 88점을 못 받음(88점 함정 해소) | Critic 점수 분포(compact vs rich) | S4 |

## 핵심 목표 (G1~G6)

| ID | 목표 | Slice |
|---|---|---|
| **G1** | **스키마 확장(additive)** — `Plan` 에 결핍 feature 슬롯 추가: hook_variants[], beat(PlanFlowBeat)에 visual/dialogue/caption, shots[], thumbnail, title_candidates[], cta, references[], length_variants, target_audience, tone. ★ **전부 Optional default None/[]** → 기존 7필드·기존 소비자 회귀 0. output_schema contract-change(CC) + agent-io-check | S1 |
| **G2** | **프롬프트 확장(P-006 bump)** — planning `SYSTEM_PROMPT`(+ 3-plan hint)를 rich 슬롯 채우도록 확장 → **prompt-version-review 경유 P-006 semver bump**(예 v1.1.0) + golden_set 회귀. ★ gated — 신규 rich 프롬프트는 flag ON 경로 전용, 기존 compact 프롬프트 보존 | S2 |
| **G3** | **gated wiring(default OFF)** — config `rich_output_enabled`(default **False**) + generate/orchestrator 경로 gated 분기(ON→rich prompt/schema 채움, OFF→기존 compact 100% 동일). behavior-preserving when OFF + 테스트(ON/OFF) | S3 |
| **G4** | **Critic depth 반영(additive)** — Critic 평가에 depth_actionability 차원 추가(기존 점수 체계 additive — 얕으면 감점, 88점 함정 해소) + prompt-version-review(Critic prompt bump) + gated 정합 | S4 |
| **G5** | **frontend rich 렌더링(conditional)** — `apps/web` PlanCard(+ lib/types·api)에 rich 필드 표시(후크 변형/타임코드·화면·대사·자막/샷/썸네일/제목/길이변형) → design-review. ★ rich 데이터 있을 때만(conditional, 기존 compact 렌더 회귀 0) | S5 |
| **G6** | **cost 재조정 + 검증 + 종료** — cost_control_policy 재조정(rich 토큰 ↑ × 3안, B안 잔여 B-RES-1 통합) + golden_set depth 재측정(목표 ≥0.8) + flag ON 라이브 데모 + phase-complete | S6 |

## 메타 목표 (MG1~MG3)

| ID | 목표 |
|---|---|
| **MG1** | multi-llm-validation self-form (12th) — Phase 13 진입 타당성 (gated 롤아웃 / additive 스키마 / 첫 출력 변경 안전성) V1~V6 |
| **MG2** | contract-change — output_schema(Plan rich 슬롯 additive) + prompt_registry(P-006 bump) (★ additive, behavior-preserving) |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 — flag OFF byte-identical(behavior-preserving) + 키 0 |

## 측정 목표 요약 (acceptance 게이트)

- **depth 0.231 → ≥0.8** (rich 경로 재측정, MO1·S6).
- **flag OFF 회귀 0** — `rich_output_enabled=False` 면 compact byte-identical (MO2·S3·S6, behavior-preserving).
- **/generate 화면 rich** — frontend 가 rich 필드를 conditional 렌더 (G5·S5, flag ON 경로).
- **P-006 bump** (prompt-version-review) + **output_schema additive**(기존 회귀 0) + **Critic depth 반영**(88점 함정 해소).

## 사용자 가치 (Why)

- **출력 가치 실현**: Phase 12 가 "할 수 있다"(4.3x 잠재)를 입증 — Phase 13 이 그것을 운영 출력로 **실현**한다. 사용자가 받는 기획안이 후크 변형·타임코드·대사·샷·썸네일까지 담은 **실행 가능한 기획 브리프**가 된다.
- **안전한 첫 출력 변경**: 이 프로젝트가 처음으로 운영 출력을 의도적으로 바꾼다 — gated(flag OFF default) + additive(전부 Optional)로 **언제든 OFF 면 기존 그대로**. 검증 후 단계적으로 ON.
- **88점 함정 해소**: Critic 이 depth 를 평가에 넣어 얕은 출력을 더는 고득점 주지 않음 → 품질 게이트가 깊이를 본다.
- **제품 경계 유지**: 깊이를 더하되 **기획 브리프** 경계를 넘지 않음 — 완성 대본/영상 제작 아님(product_boundary 영구 준수).

## ★ 절대 금지 (non_goals.md 상세)

완성 대본/영상 제작(product boundary 영구 non-goal) / 모델 tier 상향(2차 레버 — prompt/schema 확장 후 재측정 뒤) / staging 배포(Phase 14+) / **flag default ON 즉시 전환**(검증 후 별도 결정) / 스키마 breaking change(전부 additive Optional) / 실 키 평문 커밋.
