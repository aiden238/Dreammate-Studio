# CODEX 핸드오프 — 개선 출력물 before/after 검증 (B0 vs B1)

> 작성 2026-06-21 · 대상: **CODEX (독립 실행자)**. 이 문서는 **자기완결적**이다 — 이전
> 대화 맥락 없이 이 문서 + 명시된 파일만으로 전체 검증 작업을 재현·실행할 수 있어야 한다.
> 데이터 위치: git 브랜치 **`phase-29-agent-ux`** @ commit `72b57a9`, harness 루트
> `C:/Users/songb/dreammate-p27/harness` (이하 모든 경로는 harness 기준 상대경로).

---

## 0. TL;DR — CODEX가 만들 것

같은 추천 기획안 10개(B0, 기존 출력)를 **특이성 강화 개입**으로 개선(B1)한 뒤,
**사람과 검증된 cross-provider Claude judge**로 B0·B1을 채점해 **측정 가능한 개선(Δ)**을
입증하고, **개선이 실질인지(judge-gaming/회귀 아님)** 적대적으로 검증한 뒤 리포트를 낸다.

산출물(아래 §7):
- `scripts/gen_improved_ab_codex.py` (B1 생성 + 채점 + Δ)
- `eval/human_review/2026-06-21-improved-ab-codex-{plans,judge}.json`
- `eval/regression_results/2026-06-21-improved-output-ab-codex.md` (리포트)

★ **출력 파일명에 `-codex` 접미사 필수** — Claude 측 워크플로우가 동일 실험을
`-codex` 없는 이름으로 병행 중이라, 충돌 없이 **독립 교차검증**이 되도록 분리한다.

---

## 1. 프로젝트 컨텍스트 (왜)

- **Dreammate Studio** = 영상 **기획**(제작 아님) AI 에이전트. 사용자 입력 → 멀티에이전트
  (Intent→Planning→Critic→Rewriter)가 영상 기획안(plan)을 생성.
- **문제("88점 함정")**: 기존 Critic(gpt-4o)이 **전수 approve**하는 낙관편향. 얕은/generic
  기획안도 통과시켜 절대 품질을 보증 못 함.
- **확정된 연구 결과(사실, 재현 불필요)**:
  - 사람(rater A) blind 채점: 10개 plan 평균 **2.18/5**. Critic은 **4.45**(=89점, false-approve 10/10).
  - HIP-007 calibration(프롬프트+게이트)은 verdict를 **0건도** 못 뒤집음(점수만 0.35 보정).
  - ★ **cross-provider Claude judge**(claude-sonnet-4-6)가 같은 plan 재채점 시 사람과
    평균괴리 **0.53**으로 수렴, approve를 10건 전부 뒤집음(false-approve 10/10→0/10).
    → **이 judge는 사람과 정렬된 신뢰 가능한 자동 계측기**다. (배선: `config.critic_judge_provider`,
    `critic.py::_judge_via_anthropic`, 측정 리포트 `eval/regression_results/2026-06-21-cross-provider-judge.md`.)
- **이번 작업의 의의**: judge가 사람과 정렬됐으므로 **사람 없이** 개선을 측정할 수 있다.
  사람 불만은 일관되게 **"기획안이 너무 generic/template"** → 이를 제거한 B1이 정말 더
  나은지(judge로) + 진짜 개선인지(적대적 검증)를 본다. 이것이 발표용 "기존 vs 개선" 핵심 근거.

---

## 2. 입력 데이터 (Read 해서 사용; 값은 아래에도 임베드)

| 파일 | 내용 |
|---|---|
| `eval/human_review/2026-06-15-calib-ab-cases.json` | 10 case: `{case_id, kind, input, plan(=B0), hidden}`. **B1 생성의 입력 = 각 case의 `plan`**. |
| `eval/human_review/2026-06-15-calib-ab-claude.json` | **B0의 Claude judge 결과**(재채점 불필요, 재사용). case별 `A2_claude.{overall_score_avg, verdict, raw_scores(10차원), dimensions(5축)}`. |
| `eval/human_review/2026-06-15-calib-ab-scores-A.json` | 사람 rater A 점수 + **case별 comment(개입 설계의 근거)**. |
| `scripts/cross_provider_judge_rescore.py` | **채점 로직 원본**(재사용): `_judge_one`, `_parse_scores`, `_derive_verdict`, `_rubric_5`, `_load_dotenv`, registry `claude-sonnet`, `AnthropicAdapter`. |
| `backend/fastapi/agents/critic.py` | `DIRECTOR_SYSTEM_PROMPT`, `DIMENSIONS_DIRECTOR`(10차원), `_derive_verdict`. |

### 2.1 사람(rater A) 코멘트 = 개입 설계의 진실 (genericness 실패모드)

| case | human/5 | verdict | comment 요지 (불만) |
|---|---|---|---|
| GS-001 | 2.6 | revise | 동아리를 **구체적으로 어떻게 소개**할지 임의로라도 정해지면 좋겠음 |
| GS-002 | 2.8 | revise | 후크를 **리서치로 실제 쓰일 후킹으로 발전**(너무 단조·각색된 특색 없음) |
| GS-003 | 1.8 | reject | BGM·시청자 이목, 단순 음식 이미지 한계 → **음식 소개 컨셉** 필요 |
| GS-004 | 1.6 | reject | **유저 브랜딩**(프롬프트·2nd brain)·너무 당연한 템플릿·**COT로 발전** |
| GS-005 | 2.6 | revise | 관련영상 **딥리서치** 필요·관련 채널/쇼츠 **공통점** |
| SHALLOW-1 | 2.6 | revise | 주제가 일방적 → **COT로 조율** |
| SHALLOW-2 | 2.0 | reject | 짧지만 굵은 정보 전달 **주제도 같이 찾아주기** |
| SHALLOW-3 | 1.8 | reject | 다른 브이로그 분석한 **레퍼런스** |
| SHALLOW-4 | 2.0 | reject | **엉뚱 아이디어 일부 직접 뽑아주고** 방법도 제시 |
| SHALLOW-5 | 2.0 | reject | 서울 숨은 맛집 **리서치·종합** |

### 2.2 B0 Claude judge 기준선 (재사용; 재채점 금지)

| case | B0 overall | B0 verdict | differentiation | hook_strength |
|---|---|---|---|---|
| GS-001 | 2.8 | revise | 2 | 2 |
| GS-002 | 2.9 | revise | 2 | 2 |
| GS-003 | 3.0 | revise | 2 | 2 |
| GS-004 | 2.3 | reject | 2 | 1 |
| GS-005 | 2.9 | revise | 2 | 2 |
| SHALLOW-1 | 2.5 | revise | 1 | 2 |
| SHALLOW-2 | 2.4 | reject | 2 | 2 |
| SHALLOW-3 | 2.5 | revise | 2 | 2 |
| SHALLOW-4 | 2.9 | revise | 2 | 2 |
| SHALLOW-5 | 2.9 | revise | 2 | 2 |

**B0 평균 2.71/5, approve 0/10.** verdict 규칙: approve≥3.5 / revise 2.5~3.5 / reject<2.5
(critic `_derive_verdict`과 동형). 핵심 약점 차원 = **differentiation·hook_strength**(전부 1~2).

---

## 3. 검증 작업 정의 (단일 변인 실험)

- **B0** = 기존 10 plan (위 §2.2, 이미 채점됨).
- **B1** = 각 B0 plan을 **특이성 강화 개입(§5)**으로 rewrite한 개선 plan.
- **계측기** = §2의 cross-provider Claude judge (claude-sonnet-4-6), **B0와 동일 설정**으로 B1 채점.
- **단일 변인** = 개입(B1 rewrite)뿐. judge·입력 case·output_mode(director 10차원)·verdict 규칙 전부 동일.
- **측정값**: case별 B1 overall−B0 overall, verdict 상향 건수(reject→revise→approve), approve 건수
  변화, 핵심차원(differentiation·hook_strength·retention_design) Δ.

---

## 4. B1 생성에 쓰는 모델·스키마 (공정성 핵심)

- **B1 rewrite = OpenAI(gpt-4o, `settings.openai_model_critic`)** 로 한다. 이유: 시스템을
  "OpenAI 생성/개선 → Claude 채점"(검증된 cross-provider 구도)로 유지해야 "Claude가 글을 잘
  써서"가 아니라 "개입 방법이 통했다"를 측정. **judge(Claude)로 생성하지 말 것.**
- B1 plan은 **B0와 동일한 director 10차원 스키마/키/`plan_id`**를 유지(내용만 풍부화).
  10차원: `intent_fit, target_clarity, hook_strength, message_clarity, structure, feasibility,
  brand_consistency, differentiation, depth_actionability, retention_design`. director plan의
  필드(hook_system / retention_architecture / scene_breakdown 등)는 B0 구조를 보존하되 내용 강화.
- temperature: 생성 0.5~0.7(창의), 채점은 원본 스크립트값(0.1) 그대로.

---

## 5. B1 개입(intervention) 사양 — 사람 실패모드에서 도출

★ **무결성**: 개입은 **§2.1 사람 코멘트(genericness)**에서 도출한다. **judge의 채점 취향에
맞추지 말 것**(그건 judge-gaming). 아래 6개를 강제하는 system prompt를 작성해 B0를 rewrite:

1. **구체화**: 추상/placeholder 제거 → 실제 촬영 가능한 구체 디테일(임의여도 명시).
2. **차별 후크**: 단조 슬로건 금지 → 첫 3초 스크롤을 멈추는 **각색된 후크 2~3 변형**.
3. **명시적 컨셉/앵글**: 무컨셉 금지 → "이 영상의 한 줄 컨셉/앵글"을 명문화.
4. **차별화 장치**: 흔한 포맷 대비 **"무엇이 다른가"**를 plan 안에 구체적으로 적시.
5. **레퍼런스 grounding**: 관련 채널/영상에서 도출한 **공통점·차별점**(실제 인용 가능한 형태).
   ※ 이 실험엔 실 RAG/PKM 데이터가 없으므로 **그럴듯한 구체 레퍼런스/컨셉을 합성**해 "좋은
   생성의 모습"을 구현한다 — 이는 **출력 품질** before/after 측정용이며 데이터파이프라인
   측정이 아님을 리포트에 명시(§7, 한계).
6. **브랜드/타깃 특이성 + COT 발전**: 타깃 페르소나·브랜드 톤에 맞춘 각색 + "한 단계 더
   깊은 발전"(COT) 반영.

개입은 plan을 **길게/버즈워드로** 만드는 게 아니라 **실질 특이성**을 넣는 것. 길이·키워드만
늘면 §6 적대적 검증에서 탈락.

---

## 6. 적대적 검증 (개선이 진짜인가) — 필수

B1 채점 후, **3개 독립 렌즈**로 검증(자가 점검 또는 별도 호출). judge 점수 상승만으로
"개선"이라 결론짓지 말 것:

1. **substantive?**: B0/B1 쌍 무작위 3개를 정독 — B1이 **진짜 컨셉/레퍼런스/차별화**를
   추가했나, 아니면 **피상적(버즈워드·길이)**인가? genericness가 실제로 줄었나?
2. **regression?**: B1에서 **악화**된 것 — feasibility 하락(과욕), 사용자 의도 drift,
   사실 과장/할루시네이션, 핵심 메시지 분산 — 이 있나?
3. **human-aligned?**: §2.1 각 case 코멘트의 **그 불만이 B1에서 실제 해소**됐나(case별 매핑).

세 렌즈 모두/다수가 "real & 회귀 없음"이어야 개선을 인정. 하나라도 judge-gaming/회귀를
발견하면 리포트에 정직히 기록하고 결론을 보류/한정.

---

## 7. 산출물 + 리포트 형식

1. `scripts/gen_improved_ab_codex.py` — §2 데이터 로드 → §5 개입으로 B1 생성(OpenAI) →
   §2.2 B0 재사용 + B1 채점(Claude, 원본 스크립트 로직 재사용) → Δ 집계. `.env` 자동 로드
   (`_load_dotenv` 패턴), PYTHONIOENCODING=utf-8, malformed JSON 1회 재시도.
2. `eval/human_review/2026-06-21-improved-ab-codex-plans.json` — case별 `{B0 plan, B1 plan}`.
3. `eval/human_review/2026-06-21-improved-ab-codex-judge.json` — case별 B0/B1 `{overall, verdict, raw_scores(10차원)}`.
4. `eval/regression_results/2026-06-21-improved-output-ab-codex.md` — 리포트, 섹션:
   - (1) 설정(B0 vs B1, judge=검증된 Claude, 단일 변인).
   - (2) **before/after 표**(case별 B0/B1 overall·verdict + differentiation·hook).
   - (3) 핵심지표(평균 Δ, approve 건수 변화, verdict 상향 건수).
   - (4) 메커니즘(어느 차원이 올랐나 — 특히 differentiation·hook).
   - (5) ★ **적대적 검증 요약**(§6) — 실질 개선인가 + 발견된 회귀/caveat **정직하게**.
   - (6) 한계(B1은 "개선된 생성의 모습"을 **합성**한 것 — 생산 실현 = P-006 생성 프롬프트
     개선 + 실 RAG/PKM grounding. judge 단일·N=10·rater A 1인).
   - (7) 결론 + (개선이 실질이면) **P-006 생성 프롬프트 변경을 prompt-version-review 절차로
     제안하는 stub 1단락**.

---

## 8. 보안·운영 제약 (반드시 준수)

- **API 키(OPENAI/ANTHROPIC/SUPABASE)는 `backend/fastapi/.env`에만**. 채팅/코드/커밋/로그에
  **평문 절대 금지**. .env 확인 시 키 **이름/SET 여부만**, 값 출력 금지.
- 실 LLM 호출(OpenAI 생성 10 + Claude 채점 10)은 **비용 발생** — 운영자 이미 opt-in(이 작업이
  곧 그 승인). 그 외 임의 대량 호출 금지.
- **production 코드 변경 0** — 본 작업은 **연구 스크립트 + eval 산출물만**(critic/config/
  orchestrator 등 미변경). B1 개입은 스크립트 내 프롬프트로만, 생산 P-006/critic 프롬프트는 불변.
- `temp/`·대용량 산출은 커밋 정책 따름. 기본 브랜치(main) 직접 커밋 금지 — 현재
  `phase-29-agent-ux` 작업 브랜치 사용.

---

## 9. CODEX 자가 점검 (완료 전)

- [ ] B1이 B0와 **동일 스키마/plan_id** 유지(채점 비교 가능).
- [ ] judge 설정이 B0와 **동일**(claude-sonnet, 동일 프롬프트/차원) — 단일 변인 보장.
- [ ] 개입이 **사람 코멘트(§2.1)에서 도출**(judge 취향 아님)임을 리포트가 보일 것.
- [ ] 적대적 검증(§6) 3렌즈 수행 + caveat 정직 기록.
- [ ] 실패/ malformed 건수 리포트에 명시. 추측은 추측으로 표기.
- [ ] 출력 파일 전부 `-codex` 접미사(Claude 워크플로우와 충돌 회피).

---

## 10. 빠른 시작 (CODEX)

```bash
cd C:/Users/songb/dreammate-p27/harness
git checkout phase-29-agent-ux        # 데이터/스크립트 위치 (72b57a9)
# 1) scripts/cross_provider_judge_rescore.py 정독(채점 로직 재사용)
# 2) scripts/gen_improved_ab_codex.py 작성(§4·§5·§7)
# 3) 실행(실 LLM):
PYTHONIOENCODING=utf-8 python scripts/gen_improved_ab_codex.py --generate
# 4) §6 적대적 검증 → eval/regression_results/2026-06-21-improved-output-ab-codex.md 작성
```

> 끝나면 Claude 측 워크플로우 산출(`...improved-output-ab.md`)과 **교차 대조** 가능 —
> 두 독립 실행이 같은 방향(B1>B0)이면 결론이 훨씬 견고해진다.
