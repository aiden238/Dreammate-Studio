# Proposal: Commercial Viral Strategy Mode (output_mode 4-tier) 설계

> 날짜: 2026-06-03
> 유형: **설계 제안 (proposal-only)** — ★ 코드/contract/endpoint/schema **0 변경**. 본 문서는 제안서일 뿐.
> 작성 근거: 사용자 기획(상업/전략급 기획 브리프 모드) + Claude 구조 검토(9개 지정 문서 실측)
> 대상 phase: **잠정(provisional)** — director(P15 잠정) → PKM/RAG 데이터레이어(P16~17 잠정) → commercial_viral(P18~19 잠정). ★ 확정 아님, 검증 후 재우선순위.
> 절차: contract-change / prompt-version-review / eval-design / ai-architecture-review / multi-llm-validation 경유 (실 구현 시).
> 상태: **★ PARKED (미래 방향 / future direction)** — 지금 짓는 다음 빌드 아님. 선행조건 미충족 시 전부 보류.
> 포맷 참고: `meta/proposals/2026-05-31_llm-gateway-design.md`

---

## 0. ★★ 상태: PARKED / 선행조건 / provisional 페이즈 (최상위 FRAMING — 메인 세션 객관 판정)

본 proposal 은 **PARKED 미래 방향(future direction)** 이다 — *지금 짓는 다음 빌드가 아니다*.

### 0.1 왜 지금 빌드 아님인가 (객관 판정)

```
① MVP 실사용 미검증: Phase 12까지는 "구조적 깊이"(compact 0.231 / rich 1.000 격차 정량화)만
   확보. 실제 사용자가 결과물을 쓰고 만족했다는 라이브 신호 0.
② 기본 위저드 흐름 미완: 랜딩 `/` 만 실동작, /new/* 는 mock. 위저드↔백엔드 실연결 미완.
③ Phase 13 rich 실사용 미검증: rich(P-006 v1.1.0, gated)는 코드/스키마만 존재, flag OFF default.
   rich 출력이 실제로 "바로 쓸 수 있는 깊이"인지 라이브 검증 미수행(S6 depth 재측정도 mock 한계).
```

→ MVP 핵심(위저드 실연결 + rich 실사용 + human review)이 검증되기 전에 **commercial_viral 같은 최상위 tier 를 짓는 것은 "확장 전 검증(validate-before-expand)" 원칙 위반**이다. 따라서 본 문서는 방향만 고정하고 **착수를 보류**한다.

### 0.2 선행조건 (precondition — 이 셋 통과 전 commercial_viral 빌드 착수 금지)

```
(a) Phase 13 rich 실사용 검증     : rich(flag ON) 출력을 실 LLM + 실 사용자/운영자 검토로
                                    depth_actionability ≥ 0.8 재확인 (mock 아닌 라이브).
(b) 위저드 ↔ 백엔드 실연결        : /new/* mock 제거, Discovery/Quick 흐름이 실제 backend
                                    (/plans/{id}/generate 등)에 연결되어 end-to-end 동작.
(c) human review 검증            : human_review_rubric §2.6 depth + 품질 5차원으로 실제 산출물을
                                    사람이 채점, compact vs rich 우위가 사람 눈으로 확인됨.
```

★ 위 (a)(b)(c) 중 하나라도 미충족이면 본 proposal 의 어떤 단계도 착수하지 않는다(§7 게이트).

### 0.3 페이즈 번호는 잠정(provisional)

- 본 문서의 모든 Phase 번호(P15 director / P16~17 데이터레이어 / P18~19 commercial_viral)는 **provisional** 이다 — 확정 아님.
- 선행조건 통과 후 **재우선순위(re-prioritize)** 한다. 그 시점의 실사용 데이터가 "director 가 먼저 필요한가, 아니면 다른 축인가"를 결정한다.
- 프로젝트 원칙 "확장 전 검증(validate-before-expand)" 과 정합 — 검증 신호 없이 tier 를 늘리지 않는다.

---

## 1. 요약 / 목표 / 비목표

### 1.1 요약

`output_mode` 를 **4-tier** 로 확장한다: `compact` / `rich` / `director` / `commercial_viral`. 최상위 `commercial_viral` 은 **상업·전략급 기획 브리프** 모드로, 시장 맥락·시청자 심리·브랜드 포지셔닝·후크 시스템·리텐션 설계·전환 설계까지 담는다. 단 이것은 **"기획 브리프"** 이지 영상 제작물·완성 대본·조회수 보장 도구가 아니다(§리스크 보정1·2).

### 1.2 목표

```
- output_mode enum 을 4-tier 로 정식화 (compact < rich < director < commercial_viral 깊이 순).
- commercial_viral 전용 additive Optional 슬롯(10종 + scene 7필드)을 제안 (전부 OFF/compact byte-identical).
- 상업/전략 기획에 필요한 평가 차원(Critic) + eval rubric + golden_set 케이스를 제안.
- commercial_viral 의 대폭 증가하는 토큰/비용을 premium/gated tier 로 격리하는 정책 제안.
- 모든 제안은 검증 게이트(§7) 뒤에 둔다 — 선행조건 미충족 시 보류.
```

### 1.3 비목표 (non-goals)

```
- ★ default ON 금지: commercial_viral 은 어떤 경우에도 default 가 아니다. 검증 게이트 통과 +
  명시적 flag + (권장) paid/opt-in 에서만 활성.
- ★ "100만 조회수 / viral 보장" 아님 (리스크 보정1) — 패턴·근거 기반 전략급 브리프 + 사람 검증.
- ★ 영상 제작 미포함 (product_boundary 유지, 리스크 보정2): scene_breakdown 등은 기획 브리프
  수준만 — 자동 편집/TTS/BGM/자막합성/업로드는 영구 제외(mvp_non_goals 정합).
- 본 proposal 은 구현이 아니다 — 코드/contract 0 수정, 전부 "제안".
```

---

## 2. output_schema 제안 (additive Optional — OFF/compact byte-identical)

> ★ 현 자산: `output_schema.md §8.1` 의 `Plan`(v1.2.0, Phase 13 rich 12슬롯 additive) + `backend/fastapi/schemas/output.py` 의 `PLAN_RICH_FIELDS` / `BEAT_RICH_FIELDS` frozenset + `Plan.model_dump_compact()`(rich 키 제외 직렬화) + `envelope_to_response_dict(..., rich_enabled)`. 본 제안은 이 패턴을 그대로 계승·확장한다.

### 2.1 output_mode enum (제안)

`output_mode` 를 다음 4-tier enum 으로 정식화 제안 (현재 코드에는 `rich_output_enabled` boolean flag 만 존재 — 향후 enum 으로 일반화):

```
output_mode: compact | rich | director | commercial_viral
             (깊이/비용 오름차순. default = compact, 불변.)
```

| tier | 깊이 | 슬롯 |
|---|---|---|
| `compact` | 골격 | 기존 7필드(name/concept/hook/flow/pros/risks/approach_label) + rag_used (불변, byte-identical) |
| `rich` | 제작 착수 가능 | + Phase 13 rich 12슬롯 (PLAN_RICH_FIELDS 9 + BEAT_RICH_FIELDS 3) |
| `director` | **중간 깊이** | rich + commercial 슬롯 일부(예: hook_system / retention_architecture / scene_breakdown 의 일부 필드만) — 연출·구성 강화 수준, 시장/브랜드 전략 미포함 |
| `commercial_viral` | 전략급 | director + commercial_viral 전체 10슬롯 + scene 7필드 |

> ★ director = rich 와 commercial_viral 사이의 **중간 깊이** — 연출/리텐션 설계까지는 가되 시장맥락·브랜드 포지셔닝·전환 설계 등 상업 전략 슬롯은 빼서 비용·복잡도를 낮춘 중간 tier. 정확한 슬롯 분배(어느 필드가 director 까지인지)는 §7 검증 후 별도 확정.

### 2.2 commercial_viral additive Optional 슬롯 (10종, 전부 Optional)

`Plan` 에 additive Optional 로 추가 제안 (전부 None/[] default → 미존재 시 valid, COMMERCIAL_FIELDS frozenset 으로 묶어 model_dump_compact 확장 시 제외):

| 슬롯 | 타입 | 1줄 설명 |
|---|---|---|
| `market_context` | str \| null | 시장/카테고리 맥락 — 현재 트렌드·경쟁 콘텐츠 지형 (★ v1 LLM-only 추측 한계, 보정3) |
| `audience_psychology` | str \| null | 타깃 시청자의 동기·불안·욕구 등 심리 동인 (★ 보정3 동일) |
| `brand_positioning` | str \| null | 이 콘텐츠가 브랜드를 어디에 위치시키는가 (차별점·인식) |
| `hook_system` | list[str] | 후크 "시스템" — 첫 후크 + 재후크(re-hook) 지점 설계 (단발 hook_variants 와 구분) |
| `retention_architecture` | str \| null | 리텐션 구조 — 이탈 방지 장치·호기심 갭·페이싱 설계 |
| `scene_breakdown` | list[CommercialScene] | 씬 단위 분해 (★ 기획 브리프 수준만 — 제작 실행 미포함, 보정2). §2.3 7필드 |
| `commercial_conversion` | str \| null | 상업 전환 설계 — 시청→행동(구매/구독/방문) 유도 경로 |
| `platform_packaging` | str \| null | 플랫폼별 패키징 — 제목/썸네일/설명/해시태그 전략 (기획 수준, 보정2) |
| `production_feasibility` | str \| null | 제작 실현성 평가 — 1인/저예산 실행 가능성 + 대안 (기획 브리프 수준, 보정2) |
| `measurement_plan` | str \| null | 측정 계획 — 무엇을(지표) 어떻게 볼지 (★ 조회수 보장 아님, 사후 학습용, 보정1) |

> ★ 전부 Optional default None/[] → commercial_viral OFF(또는 compact/rich) 경로에서 미직렬화 → 기존 출력 **byte-identical**. `Plan` 은 이 슬롯들이 전부 없어도 valid (additive).

### 2.3 scene_breakdown 내 CommercialScene 7필드 (제안)

`scene_breakdown[]` 의 각 씬은 다음 7필드를 가진다 (전부 기획 브리프 수준 — 제작 지시 아님, 보정2):

| 필드 | 타입 | 1줄 설명 |
|---|---|---|
| `scene_intent` | str | 이 씬의 기획 의도 (왜 존재하는가) |
| `viewer_emotion` | str | 이 씬에서 시청자가 느끼길 의도하는 감정 |
| `retention_device` | str | 이 씬의 이탈 방지/호기심 유지 장치 |
| `brand_signal` | str \| null | 이 씬이 전달하는 브랜드 신호 (있을 때) |
| `commercial_signal` | str \| null | 이 씬의 상업 신호 (전환 의도, 있을 때) |
| `fallback_scene` | str \| null | 이 씬이 약할 때의 대안 씬 (A/B 성격) |
| `why_this_works` | str | 이 씬이 작동하는 근거 (★ 일반론 금지 — 패턴/맥락 기반, §3) |

### 2.4 byte-identical 보장 메커니즘 (제안)

```python
# 제안 (현 PLAN_RICH_FIELDS / BEAT_RICH_FIELDS 패턴 계승)
COMMERCIAL_FIELDS: frozenset[str] = frozenset({
    "market_context", "audience_psychology", "brand_positioning", "hook_system",
    "retention_architecture", "scene_breakdown", "commercial_conversion",
    "platform_packaging", "production_feasibility", "measurement_plan",
})

# model_dump_compact() 확장 제안: output_mode 에 따라 제외 집합을 단계적으로 합집합
#   compact          → exclude = PLAN_RICH_FIELDS ∪ COMMERCIAL_FIELDS (+ beat rich/commercial)
#   rich             → exclude = COMMERCIAL_FIELDS (+ scene commercial 필드)
#   director         → exclude = COMMERCIAL_FIELDS 중 상업전략 슬롯만 (중간 깊이)
#   commercial_viral → exclude = {} (전체 직렬화)
```

→ ★ OFF/compact 경로는 COMMERCIAL_FIELDS 가 제외되어 Phase 13 이전(및 현재 compact)과 **byte-identical**. 회귀 0. (현 `envelope_to_response_dict(..., rich_enabled)` 를 `output_mode` 분기로 일반화하는 것도 동반 제안.)

---

## 3. prompt_registry P-006 제안 (mode 분기, gated 공존)

> ★ 현 자산: `prompt_registry.md §7 P-006` 는 v1.0.0(compact, active) + v1.1.0(rich, gated — Phase 13 S2)이 `rich_output_enabled` flag 로 **gated 공존**(deprecate 아님). 본 제안은 동일 패턴으로 commercial_viral 변형을 추가한다.

### 3.1 P-006 v1.2.0 (commercial_viral, gated 공존 — 제안)

- **버전**: P-006 v1.2.0 (semver minor — additive 슬롯 + 신규 규칙·선택 필드, envelope 구조 동일).
- **gated 공존**: v1.0.0(compact) / v1.1.0(rich) / v1.2.0(commercial_viral) 세 버전이 `output_mode` 로 공존. compact 경로 v1.0.0 은 계속 active(byte-identical), commercial_viral 경로만 v1.2.0. ★ 표준 deprecate+deactivate 미적용(어느 버전 차단할지는 검증 후 별도 결정 — Phase 13 패턴 계승).
- `meta.prompt_version` 분기(compact v1.0.0 / rich v1.1.0 / commercial_viral v1.2.0)는 gated wiring.

### 3.2 commercial_viral 프롬프트 = 10섹션 (제안)

commercial_viral system prompt 는 다음 10섹션 구조 제안 (각 §2.2 슬롯에 대응):

```
1. 시장 맥락(market_context)        6. 씬 분해(scene_breakdown, 7필드)
2. 시청자 심리(audience_psychology)  7. 상업 전환(commercial_conversion)
3. 브랜드 포지셔닝(brand_positioning) 8. 플랫폼 패키징(platform_packaging)
4. 후크 시스템(hook_system)          9. 제작 실현성(production_feasibility)
5. 리텐션 설계(retention_architecture) 10. 측정 계획(measurement_plan)
```

### 3.3 프롬프트 제약 (필수 — 제안)

```
- ★ 기획 경계 명시: "이것은 촬영·편집·전환을 위한 '전략 기획 브리프'이지 완성 대본·
  영상 제작물·자동 업로드 도구가 아니다"(product_boundary). 완성 대본 전체 작성 금지.
- ★ 일반론 금지 / 근거 명시: 모든 전략 주장은 "왜 작동하는가(why_this_works)"를 패턴·맥락
  기반으로 1줄 이상 제시. "이렇게 하면 잘 됩니다" 류 막연한 일반론 금지.
- ★ 조회수 보장 금지(보정1): "100만 조회수", "무조건 viral" 등 보장 표현 금지.
  기존 광고 과장 표현 차단(§14 output_schema) 규칙 계승 + 보장 표현 추가 차단.
- v1.0.0/v1.1.0 계승 규칙: JSON만, flow 2~8 비트, RAG 복제 금지, Brand Memory avoid_phrases 금지.
- ★ market_context/audience_psychology/trend 은 실데이터 없으면 LLM 추측임을 응답에 표기
  (confidence 또는 별도 마커) — v1 LLM-only 한계 명시(보정3).
```

### 3.4 절차

- 본 변경은 **prompt-version-review Skill** 경유 (semver 부여 + golden_set 회귀 + gated 활성). 구현 상수는 `agents/planning.py` 에 `COMMERCIAL_SYSTEM_PROMPT` / `COMMERCIAL_PROMPT_VERSION` 추가 제안 (현 `RICH_SYSTEM_PROMPT` / `RICH_PROMPT_VERSION` 패턴 계승).

---

## 4. critic P-007 제안 (신규 차원 8종, gated)

> ★ 현 자산: `agents/critic.py` 는 8차원(DIMENSIONS) + Phase 13 S4 의 9번째 `depth_actionability`(DIMENSIONS_RICH, gated — `rich_output_enabled` ON 경로 전용). `CriticEvaluation.dimensions` 는 자유 dict 라 키 추가가 additive(스키마 위반 아님). 본 제안은 동일 gated 패턴으로 commercial_viral 차원을 추가한다.

### 4.1 commercial_viral 신규 차원 8종 (제안, 각 1줄)

| 차원 | 1줄 설명 |
|---|---|
| `viral_potential` | 공유·확산 유발 요소(놀라움·공감·유용성)가 설계되어 있는가 (★ 보장 아닌 잠재력 평가) |
| `retention_design` | 이탈 방지·재후크·페이싱이 구조적으로 설계되었는가 |
| `brand_memory` | 시청 후 브랜드가 기억에 남는 신호(brand_signal)가 일관되게 박혀 있는가 |
| `commercial_conversion` | 시청→행동(구매/구독/방문) 전환 경로가 자연스럽게 설계되었는가 |
| `non_genericity` | 일반론·뻔한 패턴이 아닌, 이 맥락 특화 전략인가 (§3 일반론 금지 정합) |
| `execution_feasibility` | 1인/저예산으로 이 전략 브리프를 실제 실행 가능한가 (제작 실현성) |
| `platform_fit` | 타깃 플랫폼(쇼츠/릴스/유튜브)의 특성에 패키징이 맞는가 |
| `shareability` | 시청자가 "남에게 보내고 싶은" 트리거가 있는가 (viral_potential 의 공유 측면) |

### 4.2 gated 정책 (제안)

```
- ★ gated: output_mode == commercial_viral 일 때만 위 8차원이 dimensions 에 추가됨.
  compact/rich(8/9차원)는 OFF 불변 — byte-identical.
- DIMENSIONS_COMMERCIAL = DIMENSIONS_RICH + (위 8차원)  → 총 17차원 (commercial_viral ON 경로 전용).
  CriticEvaluation.dimensions 자유 dict → 17 키 additive(스키마 위반 아님). OFF 경로는 8/9 키 유지.
- P-007 v1.3.0 (semver minor — additive 차원 + 신규 채점 지시).
  OFF=v1.1.0(8차원, active) / rich=v1.2.0(9차원, gated) / commercial_viral=v1.3.0(17차원, gated) 공존.
- _derive_verdict 의 dimensions 인자 패턴(현 critic.py)을 그대로 사용 — 차원 집합만 교체, verdict 식 구조 동일.
- ★ "88점 함정" 확장 방어: 얕은 상업 브리프(슬롯 빈약)가 17차원 평균만으로 승인되지 않도록
  non_genericity / commercial_conversion 등에 anchor 기반 채점 (rubric §5).
```

### 4.3 절차

- **prompt-version-review** (P-007 v1.3.0 — golden_set commercial 케이스 회귀) + **contract-change**(output_schema CriticEvaluation 차원 노트, additive).

---

## 5. eval rubric 제안 (commercial 차원 + golden 5 + human review 확장)

> ★ 현 자산: `eval/video_planning_eval.md §2`(8차원) + §2.A.1 `depth_actionability`(별도 0~1 축, real LLM/human 전용 — mock 미채점). `golden_set.md`(GS-001~025). `human_review_rubric.md §2`(5차원) + §2.6 depth(0~1). 본 제안은 동일 패턴으로 commercial 축을 additive 추가한다.

### 5.1 video_planning_eval §2.B commercial_viral 차원 (제안, additive)

- §2 의 8차원 + §2.A.1 depth 는 **무변경**. 신규 **§2.B** 로 commercial_viral 8차원(§4.1)을 additive 추가.
- ★ §2.A.1 과 동일하게 **별도 축** — §2 의 8차원 평균(overall_score_avg) 산식에 미포함. mock-deterministic 러너 미채점(real LLM / human 전용 — 골격만 합성하는 mock 은 상업 전략을 의미있게 채점 불가).
- 각 차원 0~1 실수 스케일 + anchor(0.2 얕음 / 0.6 보통 / 1.0 전략급) 제안.

### 5.2 golden_set 신규 5케이스 (제안, 상업/브랜드 도메인)

기존 GS-001~025 보존 + 신규 5케이스 additive 제안 (채번은 추가 시점 채번 — 예시는 GS-COMM-* placeholder):

| 예시 ID | 도메인 / 시나리오 | 검증 핵심 |
|---|---|---|
| GS-COMM-1 | 소상공인 브랜드 런칭 쇼츠 (commercial_viral) | 10슬롯 전부 채워짐 + scene 7필드 + 조회수 보장 표현 0 |
| GS-COMM-2 | D2C 제품 전환 영상 (commercial_conversion 중심) | commercial_conversion + measurement_plan 정합, 일반론 0 |
| GS-COMM-3 | 개인 브랜드 포지셔닝 시리즈 | brand_positioning + brand_signal 일관성 |
| GS-COMM-4 | 플랫폼 분기 (동일 기획 → 쇼츠/릴스/유튜브 패키징) | platform_packaging / platform_fit 분기 정합 |
| GS-COMM-5 | director vs commercial_viral 깊이 대비 | tier 별 슬롯 채움 차이 + byte-identical(compact OFF) 회귀 |

- ★ 전부 additive — 기존 케이스·우선순위 무변경. 우선순위는 추가 시 P1 권장 (상업 tier 는 핵심 흐름 아님).

### 5.3 human_review_rubric §2.7 commercial_strategy (제안)

- §2.1~2.6 무변경 + 신규 **§2.7 commercial_strategy**(0~1 축) additive — 운영자가 상업 전략 브리프의 실효성을 사람 눈으로 채점. human_avg(0~5 5차원 평균)에는 미포함(별도 0~1 기록, §2.6 depth 패턴 동일).

### 5.4 검증 게이트 (★ 실사용 전 필수 — 제안)

```
commercial_viral 실사용(flag ON, paid 노출) 전 통과 필수:
  ① golden5 (GS-COMM-1~5) real LLM 회귀 통과 (mock 아님)
  ② human review: 상업 브리프 ≥ N건을 운영자가 §2.7 + depth 로 채점, compact/rich 대비 우위 확인
  ③ §0.2 선행조건 (a)(b)(c) 전부 충족
→ 미달 시 commercial_viral 활성 금지 (default OFF 유지).
```

---

## 6. cost_control 제안 (premium/gated 분리, tier 게이트)

> ★ 현 자산: `cost_control_policy.md §13`(rich 출력 cost — 출력 토큰 3~5배, gated) + §14(rich + 다중-provider 동시 ON 합산 주의) + §11 alias 표(tier×mode). 본 제안은 동일 패턴으로 commercial_viral 을 격리한다.

### 6.1 commercial_viral = 토큰 대폭 증가 (제안)

```
- commercial_viral 은 10슬롯 + scene 7필드 × N씬 + 10섹션 프롬프트 → 출력 토큰이 rich(3~5배)보다
  추가로 증가. 대략 compact 대비 한 자릿수 후반~십수 배 추정(데모 후 실측 필요).
- 3-plan 경로면 × 3안. Critic 17차원(§4)이면 Critic 입력(rich 본문)·출력(차원 8개 추가)도 증가.
```

### 6.2 premium / gated 분리 + tier 게이트 (제안)

```
- ★ gated: output_mode == commercial_viral 활성은 명시적 flag + (필수) paid tier + opt-in.
  free tier 는 compact(또는 rich)까지만 — 일일 $0.10 상한(§4) 보호.
- ★ premium 분리: commercial_viral 호출당/세션당 상한을 §2/§3 본 상한에서 분리한 premium 상한으로
  별도 관리 (rich §13.3 상향 패턴 계승, 추가 상향).
- ★ 운영자 승인 게이트(선택): 초기에는 운영자 승인/베타 화이트리스트에서만 활성 권장.
- ★ 다중-provider + rich + commercial 동시 ON 합산 주의(§14 계승): provider 단가(5~7배) ×
  rich 토큰(3~5배) × commercial 슬롯 증가 → 세션 상한 급속 도달. 선제 차단(§7) + cost-review 필수.
```

### 6.3 절차

- **contract-change** (cost_control_policy 신규 §15 commercial_viral cost — additive, gated). 정밀 단가는 실측 후 별도 재조정.

---

## 7. 단계화 (provisional) + 의존성 + 검증 게이트

> ★ 모든 Phase 번호는 잠정(§0.3). 선행조건(§0.2) 미충족 시 **전부 보류**.

### 7.1 단계 (provisional)

```
[선행]  Phase 13 rich 실사용 검증 + 위저드↔백엔드 실연결 + human review (§0.2 a/b/c)
          ↓ (게이트 통과 전 아래 전부 보류)
P15?   director (중간 깊이 tier)        — rich 와 commercial 사이. 비용·복잡도 낮은 중간 검증.
          ↓
P16~17? PKM/RAG 데이터레이어            — market_context/audience_psychology/trend 의 실데이터 공급.
          ↓ (★ 의존: 2026-06-03_pkm-rag-orchestrator-design.md)
P18~19? commercial_viral               — 전략급 tier. 데이터레이어 위에서만 의미.
```

### 7.2 의존성 (★ 명시)

```
- commercial_viral 의 market_context / audience_psychology / trend 슬롯은 실데이터(PKM/RAG + Trend)
  없이는 LLM 추측에 그친다(보정3). 따라서 **데이터레이어(P16~17)가 commercial_viral(P18~19)의 선행**.
- ★ 상호참조: `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md` (PKM/RAG + Trend
  오케스트레이터 설계 — 별도 sibling 제안). 해당 데이터레이어가 없으면 commercial_viral 의
  market/audience/trend 슬롯은 **v1 LLM-only 한계**(추측 표기, §3.3)로만 운영.
- director(P15)는 데이터레이어 비의존(연출/리텐션 중심) → 먼저 검증 가능.
```

### 7.3 검증 게이트 + default OFF (★ 각 단계)

```
- 각 단계는 진입 전 직전 단계 + golden_set + human review 통과 필수 (validate-before-expand).
- ★ commercial_viral 은 §5.4 게이트(golden5 + human + 선행조건 a/b/c) 통과 전 활성 금지.
- 모든 tier 는 default OFF (compact default 불변). 어떤 단계도 default ON 으로 승격하지 않는다.
- ★ 선행조건(§0.2) 미충족 시 P15~P19 전부 보류 — 본 proposal 은 PARKED 유지.
```

---

## 8. 리스크 / 오픈이슈

### 8.1 리스크 보정 (★ 사용자 지정 — 본 proposal 의 핵심 방어)

| # | 리스크 | 보정 |
|---|---|---|
| 보정1 | "100만 조회수 / viral 보장"으로 오해 | ★ **보장 아님** — 패턴·근거 기반 **전략급 브리프 + 사람 검증**. 조회수 보장 불가 명시. 프롬프트에서 보장 표현 차단(§3.3), measurement_plan 은 사후 학습용(보장 지표 아님). |
| 보정2 | scene_breakdown / production_feasibility / platform_packaging 이 "영상 제작"으로 확대 | ★ **기획 브리프 수준만** — 제작 실행(편집/TTS/BGM/자막합성/업로드) 미포함. product_boundary 유지(영구 제외). 씬 7필드는 "기획 의도/감정/근거"이지 촬영 지시 아님. |
| 보정3 | market_context / audience_psychology / trend 이 LLM 추측을 사실처럼 제시 | ★ 실데이터(PKM/RAG + Trend) 없으면 **LLM 추측** — 응답에 추측 표기(§3.3). `2026-06-03_pkm-rag-orchestrator-design.md` 데이터레이어 의존(§7.2 상호참조). **v1 LLM-only 한계** 명시. |

### 8.2 그 외 리스크 / 방어

| 리스크 | 방어 |
|---|---|
| commercial_viral 슬롯이 default 로 누수 | output_mode default=compact 불변 + COMMERCIAL_FIELDS model_dump_compact 제외 → OFF byte-identical. gated + paid/opt-in. |
| 17차원 Critic 의 "88점 함정" 확대 | non_genericity / commercial_conversion anchor 채점(§4.2). golden5 + human 게이트(§5.4). |
| 토큰/비용 폭증 | premium 상한 분리 + tier 게이트 + 합산 주의(§6). 선제 차단 + cost-review. |
| product_boundary 침범(제작 확대) | 보정2 + 프롬프트 기획경계 명시(§3.3) + execution_feasibility 차원이 "기획 실현성"으로 한정. |
| 데이터레이어 미비 상태 조기 착수 | §7.2 의존성 게이트 — 데이터레이어(P16~17) 없으면 market/audience/trend 는 추측 한계로만, commercial_viral 전체 착수는 §0.2 선행조건 뒤. |
| 페이즈 번호 고정으로 오해 | §0.3 provisional 명시 — 검증 후 재우선순위. |

### 8.3 오픈이슈

```
1. director tier 의 정확한 슬롯 경계 (어느 commercial 필드까지 director 인가) — §7 검증 후 확정.
2. output_mode 를 boolean flag(현 rich_output_enabled)에서 enum 으로 일반화하는 마이그레이션 경로
   (additive — 기존 flag 와 공존/흡수 방식).
3. scene_breakdown 의 N씬 상한 (토큰/비용 vs 깊이) — 데모 후 실측.
4. commercial_viral Critic 17차원의 가중치 — 동일 가중 vs 상업 핵심(conversion/viral) 가중.
5. measurement_plan 의 사후 측정 연동 (agent_io_logs / 외부 분석) — 보장 아닌 학습 루프 설계.
6. PKM/RAG 데이터레이어 미비 시 market/audience/trend 의 "추측 표기" UX (사용자에게 어떻게 노출).
7. golden_set commercial 케이스 채번 정책 (GS-COMM-* prefix vs 단순 증가).
```

---

## 9. 변경 범위 / 변경하지 않을 범위

### 9.1 변경 범위 (실구현 시 — ★ 본 proposal 은 미수정, 전부 제안)

```
- output_schema.md / schemas/output.py: output_mode enum + COMMERCIAL_FIELDS + Plan/CommercialScene
  additive Optional 슬롯 + model_dump_compact 확장 (additive, byte-identical 보장).
- prompt_registry.md / agents/planning.py: P-006 v1.2.0 commercial_viral 변형 (gated 공존).
- agents/critic.py: DIMENSIONS_COMMERCIAL + P-007 v1.3.0 (gated, 17차원 ON 경로 전용).
- eval/*: video_planning_eval §2.B + golden_set 5케이스 + human_review_rubric §2.7 (additive).
- cost_control_policy.md: §15 commercial_viral cost (gated, additive).
- config.py: output_mode 게이트 (현 rich_output_enabled 패턴 계승, additive Field).
```

### 9.2 ★ 변경하지 않을 범위 (보장)

```
- compact default 불변 — 모든 추가는 Optional/gated, OFF 경로 byte-identical (회귀 0).
- 기존 7필드(+rag_used) + Phase 13 rich 12슬롯 + 8/9차원 Critic — 전부 불변.
- product_boundary: 영상 제작(편집/TTS/BGM/자막/업로드) 영구 제외 (보정2).
- MOA 4 agent 불변 (commercial_viral = 기존 Planner/Critic 의 mode 확장, 새 agent 아님).
- pytest 영향 0 (본 proposal 은 문서 1개 — 코드/contract 0 수정).
- 키/.env 0 (LLM 호출 없음, 실데이터 의존은 별도 데이터레이어 proposal).
```

---

## 10. 다음 단계 (승인 시)

```
1. 본 proposal 은 PARKED 유지 — §0.2 선행조건(a/b/c) 충족 전 착수 금지.
2. 선행조건 통과 후: ai-architecture-review + multi-llm-validation (큰 tier 확장 결정).
3. director(P15 잠정) 먼저 — 데이터레이어 비의존, 중간 깊이로 검증.
4. PKM/RAG 데이터레이어(P16~17 잠정, sibling proposal) → commercial_viral(P18~19 잠정).
5. 각 단계 contract-change / prompt-version-review / eval-design + 검증 게이트(§7.3).
```

---

> ★ 요약: 본 문서는 **PARKED 미래 방향** 이다. output_mode 4-tier(compact/rich/director/commercial_viral) + commercial_viral 10슬롯 + scene 7필드 + Critic 17차원 + golden5 + human 을 **전부 additive Optional / gated / default OFF / byte-identical** 로 제안한다. 보장 아님(보정1) · 기획 브리프 수준(보정2) · 데이터레이어 의존(보정3). 선행조건(rich 실사용 + 위저드 실연결 + human review) 통과 전 착수 금지. 코드/contract 0 수정 — 전부 "제안".
