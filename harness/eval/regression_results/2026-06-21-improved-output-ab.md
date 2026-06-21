# 특이성 강화 개입(B1) before/after 리포트 — 2026-06-21

- 실험: 동일 추천 기획안 10개(정상 5 + 얕은입력 5, `output_mode=director`, 10차원)에 대해 **B0(기존 생성) → B1(특이성 강화 rewrite)** 개입 후, 검증된 동일 judge 로 재채점하여 측정가능한 개선(Δ)을 입증.
- 산출 JSON: `C:/Users/songb/dreammate-p27/harness/eval/human_review/2026-06-21-b1-specificity-rescore.json`
- 보조 표: `C:/Users/songb/dreammate-p27/harness/eval/regression_results/_improved_ab_table.md`
- 생성/채점 스크립트: `C:/Users/songb/dreammate-p27/harness/scripts/b1_specificity_rewrite.py`, `C:/Users/songb/dreammate-p27/harness/scripts/b1_rescore_failed.py`

> **한줄 결과:** B0 평균 2.71 → B1 평균 3.04 (Δ=+0.33), approve 0→0, verdict 상향 2건(reject→revise), 실패 0.

---

## 1. 설정 (단일 변인 = 특이성 강화 개입)

| 항목 | B0 (기존) | B1 (개입) |
|---|---|---|
| 입력 | 동일 10케이스 (정상5+얕은5) | **동일** (변경 없음) |
| 개입 | 없음 (기존 생성 그대로) | specificity_amplification rewrite (rewriter=gpt-4o, temp=0.4) |
| judge | claude-sonnet-4-6 (검증된 human-aligned 계측기) | **동일** claude-sonnet-4-6 |
| judge temp | 0.1 | **0.1 (동일)** |
| output_mode / 스키마 / 산식 | director / 15슬롯 / `_parse_scores`·`_derive_verdict`·`_rubric_5` | **byte-identical 재사용** |

- **계측기 신뢰 근거:** 동일 case 에 대해 사람(rater A) 평균 2.18/5 vs Claude judge B0 평균 2.71/5 — 평균괴리 0.53 으로 수렴. 기존 critic(gpt-4o)은 4.45(=89점, false-approve 10/10 "88점 함정")였으므로, 본 실험의 채점 계측기는 **사람 정렬된 Claude judge** 를 단일 사용.
- **단일 변인 보장:** judge·입력·output_mode·스키마·temp·채점 산식 모두 동일. 변한 것은 오직 B1 의 plan 본문(특이성 강화 rewrite) 하나.
- **B0 무결성:** B0 점수는 `2026-06-15-calib-ab-claude.json` 재사용. 재계산한 B0 평균 2.71·verdict(approve0/revise8/reject2)가 기지값과 case_id 단위로 정확히 일치.
- **개입 도출 원칙:** 개선 항목은 judge 의 채점 취향이 아니라 **사람이 지적한 genericness 실패모드**(후크 단조로움·각색 부재·딥리서치 레퍼런스 부재·컨셉/브랜드 특이성·COT 발전)에서 도출.

---

## 2. before/after 표 (case별)

| case_id | kind | B0 overall | B1 overall | Δ | B0→B1 verdict | differentiation B0→B1 | hook_strength B0→B1 |
|---|---|---|---|---|---|---|---|
| GS-001 | normal | 2.80 | 3.10 | **+0.30** | revise → revise | 2→2 | 2→3 |
| GS-002 | normal | 2.90 | 3.00 | +0.10 | revise → revise | 2→2 | 2→3 |
| GS-003 | normal | 3.00 | 3.30 | **+0.30** | revise → revise | 2→**3** | 2→**4** |
| GS-004 | normal | 2.30 | 3.00 | **+0.70** | **reject → revise** | 2→2 | 1→2 |
| GS-005 | normal | 2.90 | 3.30 | **+0.40** | revise → revise | 2→2 | 2→3 |
| SHALLOW-1 | shallow | 2.50 | 2.90 | **+0.40** | revise → revise | 1→2 | 2→2 |
| SHALLOW-2 | shallow | 2.40 | 3.20 | **+0.80** | **reject → revise** | 2→2 | 2→3 |
| SHALLOW-3 | shallow | 2.50 | 3.00 | **+0.50** | revise → revise | 2→2 | 2→2 |
| SHALLOW-4 | shallow | 2.90 | 2.90 | **0.00** | revise → revise | 2→2 | 2→2 |
| SHALLOW-5 | shallow | 2.90 | 2.70 | **−0.20** | revise → revise | 2→2 | 2→3 |
| **평균** | | **2.71** | **3.04** | **+0.33** | | 1.9→2.1 | 1.9→2.7 |

---

## 3. 핵심 지표

| 지표 | B0 | B1 | 변화 |
|---|---|---|---|
| overall 평균 | 2.71 | 3.04 | **Δ +0.33** |
| approve 건수 | 0 | 0 | **변화 없음 (상한 미돌파)** |
| revise 건수 | 8 | 10 | +2 |
| reject 건수 | 2 | 0 | −2 |
| verdict 상향(reject→revise) | — | — | **2건 (GS-004, SHALLOW-2)** |
| 순(net) 악화 case | — | — | **1건 (SHALLOW-5, Δ−0.2)** |
| 실패(JSON 파싱 등) | — | — | **0** |

- 개선은 **하한(reject) 탈출에 집중**되었고, **승인 상한(approve)은 한 건도 돌파하지 못함** → 10건 전부 여전히 비승인(revise) 상태.

---

## 4. 메커니즘 (어느 차원이 올랐나)

차원별 평균 Δ (raw 0~5):

| 차원 | Δ | 해석 |
|---|---|---|
| **hook_strength** | **+0.80** | 가장 큰 개선. 사람 불만 1순위였던 "후크 단조로움"(GS-002)·각색 부재가 측정상 가장 크게 해소 |
| brand_consistency | +0.60 | 브랜드 앵글/톤 명시화 — 단 GS-004 의 점수 상승 대부분을 이 축이 단독 견인 |
| message_clarity | +0.60 | 메시지 구체화 |
| intent_fit | +0.40 | (얕은 케이스에서는 의도 발명 신호로도 해석 — §5 참조) |
| target_clarity | +0.40 | 타깃 "예:" 명시화 |
| **differentiation** | **+0.20** | **가장 둔함.** 10건 중 8건 불변 — 진짜 차별화 장치는 거의 추가되지 않음 |
| structure / retention_design / depth_actionability | +0.10 | 미미 |
| feasibility | +0.00 | 불변 |

**floor 축(4개) 성공기준(평균 +0.5) 충족 여부:** hook_strength(+0.8) **충족**, target_clarity(+0.4)·differentiation(+0.2)·retention_design(+0.1) **미달**. → build_spec 의 "4개 floor 축 평균 +0.5" 기준은 hook 만 통과. 단 overall Δ>0(+0.33)·verdict 상향 ≥1(=2) 기준은 충족.

**요지:** Δ는 **표면 특이성(구체적 후크·고유명·브랜드 앵글)** 에 응답하는 축에 집중되었고, **개념 원본성(differentiation)** 축은 거의 움직이지 않았다. 두 건의 verdict 상향 모두 differentiation 이 평면(=2)인 상태에서 발생 — GS-004 는 brand_consistency 1→4 가, SHALLOW-2 는 message_clarity +2/depth +1 이 단독 견인. 이는 **재구상(re-conception)이 아니라 특이성 rewrite 의 시그니처**다.

---

## 5. ★ 적대적 검증 요약 (4관점 전원 "개선 진짜" 판정 — 단 무료 점심 아님)

4개 독립 검증자(substantive / regression / human-aligned / 회귀) 전원 `real=true`. 결론: **개선은 실재하나, "얕은 종류의 진짜"(구체성/특이성)이지 "깊은 종류의 진짜"(새 컨셉/원본성)는 아니다.** judge-gaming 은 아니지만 schema-conformance 에 부분적으로 편승.

### 5.1 실질 개선 증거 (judge-gaming 아님)
- **버즈워드 삽입 없음:** '차별화된/딥리서치/COT/브랜드 특이성' 같은 메타 키워드 채우기 거의 0.
- **분량 가장 아님:** B1/B0 char 비율 1.08~1.19x(과팽창 아님). 단 숫자·고유명 토큰은 plan 당 19~40개로 실제 증가 → 점수 상승을 설명.
- **실제 구체 텍스트:** GS-003 hook = "을지로 노가리골목의 … 9천원에 줄 서는 이유는?"(구체 장소·요리명·숫자 2개) + 비교 채널(맛있는 녀석들/윤식당)에 각각 명시적 차별점. SHALLOW-2 는 실제 메커니즘("카페인은 아데노신 수용체를 차단")+실채널 레퍼런스(AsapSCIENCE/Kurzgesagt) 추가 → message_clarity +2/depth +1 이 실콘텐츠로 뒷받침됨.

### 5.2 정직하게 보고하는 회귀 / caveat
- **순 악화 1건 — SHALLOW-5 (Δ−0.2, 유일한 음수):** target_clarity −1·depth_actionability −1·retention_design −1 동시 하락. 원인: 단일 맛집 → '서울 숨은 맛집 3곳'(60초)으로 확장하며 핵심 메시지 분산 + 항목당 깊이 저하. target 은 placeholder 그대로. → 사람이 요청한 "맛집 리스트 리서치"는 미충족이며 plan 이 오히려 나빠짐.
- **순 동률이나 두 축 희생 — SHALLOW-4 (Δ0.0):** target_clarity −1·brand_consistency −1 을 message_clarity/depth 상승으로 상쇄. 명료성을 타깃 정밀도·브랜드 일관성으로 지불.
- **differentiation 정체:** 평균 +0.2, 8/10 불변. 최저 점수 축인데 rewrite 가 실질 차별화 장치를 거의 추가하지 못함.
- **할루시네이션(체계적):** GS-003 '30년 전통·9천원', SHALLOW-5 '30년간 사랑받은 간장새우'(서로 다른 케이스에 같은 허구 디테일 재사용), SHALLOW-2 '아데노신 수용체 차단' — 얕은 입력에 없던 구체 사실을 창작. 모든 references 가 `추정/예시:`로 자인됨 = 구체값이 소스가 아니라 발명임을 시스템이 라벨로 인정. (정직성 측면: 허위를 **단정하지 않고 라벨링**한 것은 데이터 경계 정직성 보존이나, 점수 상승 동력이 미검증 디테일이라는 점은 회귀.)
- **의도 drift(얕은 케이스):** shallow 5건 전부 intent_fit 동률 또는 +1. underspecified 입력에서 intent_fit 상승은 rewriter 가 의도를 발명한 신호. SHALLOW-3 은 범용 브리프가 원본에 없던 '을지로 노가리골목 카페'로 drift.
- **placeholder 잔존:** `예:`·`추정/예시:` 라벨이 B1(GS-002, SHALLOW-3/4/5)에 그대로 남았는데 judge 는 구조를 보상 → 형식/분량 주도 점수 상승의 전형적 실패모드와 인접.
- **approve 0→0:** 10건 전부 비승인 유지. 상승은 운영 결과(승인 가능 여부)를 바꾸지 못함.

### 5.3 사람 불만 대응 매핑 (rater A 코멘트 기준)

| case | 사람 요청 | 대응 |
|---|---|---|
| GS-003 | 음식 소개에 컨셈 부여 | **RESOLVED** (을지로 컨셉+요리명, hook+2/diff+1) |
| SHALLOW-2 | 짧고 굵은 정보 + 주제 발굴 | **RESOLVED** (커피-집중력 과학 주제, msg+2) |
| GS-001 | 동아리 구체 소개(임의라도) | PARTIAL (가정 구체값 채움) |
| GS-002 | 리서치 기반 후크 발전 | PARTIAL (후크 강화하나 각색 차별성 미달) |
| GS-004 | 2nd브레인 유저 브랜딩 + COT 대화 | **PARTIAL/핵심 미충족** (brand +3 은 일반 폴리시, 유저특화 브랜딩·COT 메커니즘 부재) |
| GS-005 | 관련 영상 딥리서치·공통점 | PARTIAL (채널명 추가하나 `추정/예시`=시뮬레이션) |
| SHALLOW-3 | 타 브이로그 분석 레퍼런스 | PARTIAL (레퍼런스 추가하나 fabricated) |
| SHALLOW-1 | COT 로 일방성 조율 | **UNRESOLVED** (대화/COT 메커니즘 없음) |
| SHALLOW-4 | 엉뚱 아이디어 직접 추출+실행법 | **UNRESOLVED + 회귀** (구체 아이디어 미표면화, 2축 하락) |
| SHALLOW-5 | 숨은 맛집 리스트 리서치 | **UNRESOLVED + 회귀** (리서치 리스트 없음, Δ−0.2) |

집계: RESOLVED 2 / PARTIAL 5 / UNRESOLVED 3(이 중 2건 회귀). **rewrite 가 흉내낼 수 없는 3대 요청** — (1) COT 대화 수렴, (2) 진짜 딥리서치/실레퍼런스, (3) 2nd-brain 유저특화 브랜딩 — 은 미충족.

---

## 6. 한계

- **B1 은 "개선된 생성의 모습"을 후처리로 합성한 것** — production 생성기 자체의 개선이 아님. 생산 실현에는 **P-006 생성 프롬프트 개선 + RAG/PKM grounding** 이 필요. differentiation 이 +0.2 로 가장 둔한 것은 RAG/PKM 미연결(실데이터 없이 `예:`로 합성된 차별화 장치를 judge 가 보수적으로 평가)이 단일 변인으로 격리되어 드러난 것 — **이 자체가 유효한 측정 신호**(진짜 차별화·리텐션 설계는 실제 딥리서치 데이터 연결을 요함).
- **B0 plan 본문 미보존:** 두 파일 모두 B0 는 점수/raw_scores 만 저장, B1 만 plan 본문 보유. **B0 vs B1 직접 genericness word-diff 불가** — B0 genericness 는 축별 점수 이동으로 추론.
- **judge 단일·동일 모델 패밀리:** rewriter=gpt-4o, judge=claude-sonnet-4-6. 독립 사람 재채점 없음 → judge 자기일관성 기여 가능성 배제 못함. (단 B0 단계에서 사람-Claude 괴리 0.53 검증은 유효.)
- **N=10·단일 실행·temp 0.1:** Δ0.33 의 분산 추정 없음 — run-to-run 노이즈 가능성 배제 못함. rater A 1인.
- **측정도구 보정 confound:** 10건 중 5건이 1차 judge 출력 절단(max_tokens=2000)으로 실패 → max_tokens 만 4000 으로 상향(산식·프롬프트·temp·registry byte-identical)하고 B1 plan 동일 rewriter 재생성하여 재채점. **절단 해소는 측정 버짓 한계 보정이지 B1 품질 문제 아님**이나, 재구조(rescued) 5건은 비재구조 5건과 미세 confound.
- **무결성 가드:** production 코드(`backend/fastapi/**`) 0 변경(git clean). `planning.py` DIRECTOR_SYSTEM_PROMPT·`critic.py` DIMENSIONS_DIRECTOR·`cross_provider_judge_rescore.py` 무수정 — rewriter 개입은 스크립트 내 상수로만 격리. 스키마 가드(15슬롯·flow·hook_system≥2·scene_breakdown≥2 등) 10건 전부 통과.

---

## 7. 결론 및 생산 반영 권고

**결론:** 사람이 지적한 genericness 실패모드 중 **표면층(후크·타깃 명료성·구체 고유명)** 은 검증된 동일 계측기로 **측정가능하게 개선**되었다(overall Δ+0.33, hook_strength +0.8, reject 2건 → revise 상향, 가밍 의심 0). 그러나 **개념층(differentiation)** genericness 는 거의 해소되지 않았고(+0.2, 8/10 불변), approve 는 0→0 으로 운영 결과를 바꾸지 못했으며, 일부(SHALLOW-4/5)는 다른 축을 희생하며 회귀했다. 즉 **B1 은 "더 구체적인" 기획안을 사지만 "더 차별화된" 제품은 사지 못한다.** 후크·구체성은 후처리 rewrite 로 개선 가능하나, 진짜 차별화·리텐션·COT·딥리서치는 **실데이터 grounding(RAG/PKM) 없이는 불가**함을 Δ가 시사한다.

**생산 반영 권고:** **조건부 YES.** 개선은 실질이나 후처리 합성이므로 production 코드를 직접 바꾸지 않는다. 대신 본 실험에서 통계적으로 유효했던 개입(후크 각색·고유명/숫자 구체화·타깃 "예:" 명시)을 **P-006 생성 프롬프트(`planning.py` DIRECTOR_SYSTEM_PROMPT) 변경안**으로 `prompt-version-review` 절차에 회부한다 — 단 (a) 할루시네이션 가드(미검증 구체값은 `추정/예시:` 라벨 강제, 단정 금지), (b) over-expansion 가드(SHALLOW-5 식 단일→다중 확장으로 깊이 희생 방지), (c) differentiation 은 프롬프트가 아니라 **RAG/PKM grounding 트랙(별도)** 으로 분리 추진을 전제로 한다. 본 변경안은 동일 Claude judge + 사람 rater A 재채점으로 회귀 게이트를 재통과해야 머지한다.

> **prompt-version-review stub:** P-006 `DIRECTOR_SYSTEM_PROMPT` v(next) 후보 — diff = {후크 각색 지시 + 고유명/숫자 구체화 요구 + 타깃 "예:" 명시 + 미검증 사실 `추정/예시:` 라벨 강제 + 단일주제 확장 금지}. 근거 = 2026-06-21 B1 A/B(Δ+0.33, hook +0.8, gaming 0). 게이트 = 동일 judge Δ>0 ∧ verdict 비퇴행 ∧ 할루시네이션 단정 0 ∧ rater A spot 재채점 평균 비퇴행. differentiation/RAG 는 본 stub 범위 외(별도 grounding 트랙).
