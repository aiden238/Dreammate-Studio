# output_schema.md — 영상기획 AI 에이전트 LLM 출력 스키마

> 위치: `docs/contracts/output_schema.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 참조: `ai_system/prompts/prompt_registry.md` (10개 prompt 정의)
> 참조: `docs/contracts/error_response_contract.md` (실패/검증 실패 응답)
> 참조: `docs/contracts/db_schema.md` (저장 대상 컬럼 매핑)

---

## 0. 이 문서의 위치

`prompt_registry.md`는 "어떤 프롬프트가 있는가"를 정의하고, 이 문서는 그 프롬프트가 **무엇을 반환해야 하는가**를 JSON 스키마로 고정한다. 두 파일은 항상 동기화된 상태여야 하며, 한쪽이 변경되면 다른 쪽도 같은 commit에서 갱신한다.

이 문서가 정의하는 대상:

1. 10개 prompt (P-001 ~ P-008, P-AUX-1, P-AUX-2)의 출력 JSON 구조
2. 모든 출력에 공통으로 부착되는 메타 envelope
3. 검증 규칙 (필드 길이, enum, 카드 수, 광고적 표현 검사 흐름)
4. 에러 응답 (`error_response_contract.md` 참조 형식)
5. 버전 관리 / 회귀 정책
6. 최종 완성 산출물(`final_outputs`)의 통합 JSON 구조 (legacy)

---

## 1. 설계 원칙

```
1. 모든 LLM 출력은 JSON 1개 객체로만 응답한다 (자연어 머리말/꼬리말 금지).
2. 출력 객체는 본문(body) + 메타(meta) + 검증결과(validation)의 3섹션으로 구성된다.
3. 모든 prompt 응답은 envelope 안에 들어가 agent_io_logs.output_payload로 저장된다.
4. enum 필드의 값은 이 문서에 정의된 것으로만 한정한다. 새 값 추가 시 minor bump.
5. 카드형 출력은 항상 "4 추천 + 1 직접입력 슬롯" 규약을 지킨다 (UI 단에서 5장 표시).
6. 검증 실패는 "에러 응답"이 아니라 "validation 섹션이 실패 표시인 정상 응답"이다.
7. 광고적 과장 표현 검사는 응답 생성 직후 1차 자동 검사 → Critic 단에서 2차 점수화.
8. semver: breaking change = major bump, 필드 추가 = minor, 설명 변경 = patch.
9. 한국어 출력은 NFC 정규화. 이모지 허용 (UI 표현용), 특수 unicode 차단.
10. 모든 텍스트 필드는 trim() + 양끝 따옴표 제거 후 저장.
```

---

## 2. 공통 Envelope

모든 prompt 응답은 다음 형태로 wrapping된다.

```json
{
  "meta": {
    "request_id": "uuid",
    "prompt_id": "P-001",
    "prompt_version": "v1.0.0",
    "model": "gpt-4o-mini",
    "generated_at": "2026-05-26T08:30:00Z",
    "locale": "ko-KR",
    "schema_version": "1.0.0"
  },
  "body": { /* prompt별 본문, 아래 §3~§12에서 정의 */ },
  "validation": {
    "passed": true,
    "checks": [
      { "name": "field_length", "status": "ok" },
      { "name": "ad_phrase_filter", "status": "ok" },
      { "name": "enum_values", "status": "ok" }
    ],
    "warnings": []
  }
}
```

필드 정의:

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `meta.request_id` | uuid v4 | yes | 클라이언트↔서버↔LLM 호출 추적 키. `agent_io_logs.log_id`와 분리. |
| `meta.prompt_id` | string | yes | `P-001` 등. `prompt_registry.md` 정의값. |
| `meta.prompt_version` | string | yes | semver. `v1.0.0` 형식. |
| `meta.model` | string | yes | `gpt-4o-mini` / `gpt-4o` / `claude-3-5-sonnet` 등. |
| `meta.generated_at` | ISO8601 UTC | yes | LLM 응답 수신 시각 (서버 기준). |
| `meta.locale` | string | yes | `ko-KR` 고정 (Phase 1). |
| `meta.schema_version` | string | yes | 이 문서 자체의 semver. |
| `body` | object | yes | 아래 prompt별 정의. |
| `validation.passed` | boolean | yes | 모든 check가 ok이면 true. |
| `validation.checks[]` | array | yes | 자동 검사 결과. |
| `validation.warnings[]` | array | no | passed=true여도 주의 사항이 있을 때. |

`passed=false`인 경우의 처리는 §15에서 정의.

---

## 3. P-001 · brand_direction_cards

Discovery Wizard Step 2. Brand 방향 카드 5장.

### 3.1 Body 스키마

```json
{
  "cards": [
    {
      "card_id": "string (uuid)",
      "kind": "ai_suggestion",
      "name": "string (8–14자, 명사형)",
      "description": "string (30–50자)",
      "fit_situation": "string (1줄)",
      "pros": "string (1줄)",
      "cautions": "string (1줄)",
      "confidence": 0.0
    }
  ],
  "user_input_slot": {
    "kind": "user_direct_input",
    "placeholder": "직접 브랜드 방향을 입력해주세요"
  }
}
```

### 3.2 검증 규칙

```
- cards 배열 길이 == 4 (AI 추천 4장)
- user_input_slot 1개 = UI 단에서 5번째 카드로 표시
- 모든 카드의 name 8–14자, description 30–50자
- 5장(4 AI + 1 input slot)의 의미 중첩 < 30% (cosine 유사도 사전 검사)
- confidence: 0.0 ~ 1.0, 평균 ≥ 0.5
- 광고적 표현 단어 차단 (§16 참조)
```

### 3.3 예시

```json
{
  "meta": { "...": "..." },
  "body": {
    "cards": [
      {
        "card_id": "b1f2-...",
        "kind": "ai_suggestion",
        "name": "성장 기록형",
        "description": "대학생이 시행착오를 겪으며 배우는 모습을 보여주는 방향",
        "fit_situation": "창업동아리·프로젝트 누적 기록",
        "pros": "진정성이 강하고 공감대를 만들기 쉽다",
        "cautions": "정보성 없이 일기처럼 보일 수 있다",
        "confidence": 0.78
      }
      /* 3장 더 */
    ],
    "user_input_slot": {
      "kind": "user_direct_input",
      "placeholder": "직접 브랜드 방향을 입력해주세요"
    }
  },
  "validation": { "passed": true, "checks": [], "warnings": [] }
}
```

→ DB 매핑: 사용자가 1장을 선택하면 `brands.direction_label`에 `name` 저장, 5장 전체는 `discovery_choices.presented_options`에 jsonb로 저장.

---

## 4. P-002 · domain_cards

Discovery Wizard Step 3. Domain 카드 5장 (선택된 Brand 안에서).

### 4.1 Body 스키마

P-001과 동일한 5장 카드 구조. `kind` enum도 동일.

```json
{
  "cards": [
    {
      "card_id": "string (uuid)",
      "kind": "ai_suggestion",
      "name": "string (6–14자)",
      "description": "string (30–50자)",
      "fit_situation": "string",
      "pros": "string",
      "cautions": "string",
      "confidence": 0.0
    }
  ],
  "user_input_slot": {
    "kind": "user_direct_input",
    "placeholder": "직접 주제 영역을 입력해주세요"
  }
}
```

### 4.2 검증 규칙

```
- cards 길이 == 4
- 각 카드는 선택된 Brand 방향과 의미적으로 연결됨 (Critic이 별도 검사 가능)
- 동일 user 안에서 이미 생성된 다른 brand의 domain과 80% 이상 동일하면 warning
```

→ DB 매핑: `domains.name`, `domains.description`. 5장은 `discovery_choices` 기록.

---

## 5. P-003 · series_cards

Discovery Wizard Step 4. Series 구조 카드 5장.

### 5.1 Body 스키마

```json
{
  "cards": [
    {
      "card_id": "string (uuid)",
      "kind": "ai_suggestion",
      "name": "string (10–18자)",
      "description": "string (30–60자)",
      "structure_type": "growth_record | experiment | community | review | informational | narrative | event_based | other",
      "cadence_hint": "string (예: \"주 1회\", \"월 2회\", \"이벤트 발생 시\")",
      "fit_situation": "string",
      "pros": "string",
      "cautions": "string",
      "confidence": 0.0
    }
  ],
  "user_input_slot": {
    "kind": "user_direct_input",
    "placeholder": "직접 시리즈 구조를 입력해주세요"
  }
}
```

### 5.2 검증 규칙

```
- cards 길이 == 4
- structure_type은 enum 안 (자유 입력 금지, "other"는 cautions에 사유 명시)
- 4장의 structure_type이 최소 3종류 이상 (다양성 보장)
- cadence_hint는 자유 텍스트지만 빈 문자열 금지
```

→ DB 매핑: `series.structure_type`, `series.cadence_hint`, `series.name`, `series.description`.

---

## 6. P-004 · target_and_tone_cards

Discovery Wizard Step 5. Target 5장 + Tone 5장 (단일 호출).

### 6.1 Body 스키마

```json
{
  "target_cards": [
    {
      "card_id": "string (uuid)",
      "kind": "ai_suggestion",
      "name": "string (8–14자)",
      "description": "string (1줄)",
      "pain_points": ["string", "string"],
      "watch_motivation": "string (1줄)",
      "fit_score_rationale": "string (왜 이 시리즈에 맞는지)",
      "confidence": 0.0
    }
  ],
  "target_input_slot": {
    "kind": "user_direct_input",
    "placeholder": "직접 타겟을 입력해주세요"
  },
  "tone_cards": [
    {
      "card_id": "string (uuid)",
      "kind": "ai_suggestion",
      "name": "string (예: \"현실적·솔직형\", \"유쾌·과장 자제형\")",
      "description": "string (1줄)",
      "example_sentences": ["string", "string"],
      "avoid_examples": ["string", "string"],
      "confidence": 0.0
    }
  ],
  "tone_input_slot": {
    "kind": "user_direct_input",
    "placeholder": "직접 톤을 입력해주세요"
  }
}
```

### 6.2 검증 규칙

```
- target_cards 길이 == 4, tone_cards 길이 == 4
- pain_points는 1~2개
- example_sentences 정확히 2개, avoid_examples 정확히 2개
- avoid_examples의 표현은 광고적 표현 사전과 교차 검사 → 위반 시 자동 재생성 1회
- tone과 brand_memory.preferred_tone 충돌 시 validation.warnings에 기록
```

→ DB 매핑: 선택된 target → `video_briefs.target`, 선택된 tone → `brands.tone` (jsonb의 `primary`).

---

## 7. P-005 · oneline_direction

Direction Summary. 한 줄 기획 방향.

### 7.1 Body 스키마

```json
{
  "one_line": "string (≤70자)",
  "components": {
    "target": "string",
    "message": "string",
    "format": "shorts_30s | reels_60s | shorts_60s | youtube_3m | youtube_8m | other",
    "length_sec": 30
  },
  "missing_info": ["string"],
  "confidence": 0.0,
  "rewrite_offered": false
}
```

### 7.2 검증 규칙

```
- one_line 길이 ≤ 70자, ≥ 20자
- one_line은 components.target + components.message + components.format을 포함하는 문장이어야 함
- missing_info는 0~3개 (Discovery Mode), 0~2개 (Quick Mode P-005q)
- format이 "other"인 경우 missing_info에 "영상 포맷 확정" 항목 자동 포함
- confidence ≥ 0.5 미만이면 rewrite_offered=true로 사용자에게 재진행 옵션 제공
- 광고적 표현 사전 위반 시 validation.passed=false 즉시 재생성
```

### 7.3 예시

```json
{
  "body": {
    "one_line": "창업에 관심 있는 대학생을 대상으로 동아리 운영 시행착오를 보여주는 30초 쇼츠 영상",
    "components": {
      "target": "창업에 관심 있는 대학생",
      "message": "동아리 운영 시행착오를 보여주는",
      "format": "shorts_30s",
      "length_sec": 30
    },
    "missing_info": [],
    "confidence": 0.87,
    "rewrite_offered": false
  }
}
```

→ DB 매핑: `video_projects.one_line_direction`. status는 `draft` → `generating`.

---

## 8. P-006 · plan_candidates (Planning Agent)

3개 기획안 카드. MOA Planning.

### 8.1 Body 스키마

> **v1.1.0 (2026-05-26 CC-001 적용)**: body 키 `plans` → `plan_candidates` 로 변경.
> DB 테이블명 (`plan_candidates`) + prompt_registry P-006 명명과 정합.
>
> **v1.2.0 (2026-06-02 Phase 13 S1, CC-012 적용)**: `Plan` rich 슬롯 12종 **additive**
> (전부 Optional). `Plan` +9 (target_audience / tone / hook_variants / shots / thumbnail /
> title_candidates / cta / references / length_variants) + `flow[]`(PlanFlowBeat) +3
> (visual / dialogue / caption). ★ rich 값은 `rich_output_enabled` flag **ON**(S3) 경로에서만
> 채워지고, **OFF(default)** 경로는 rich 키를 직렬화에서 제외 → 기존 7필드 출력 **byte-identical**.
> 근거: Phase 12 깊이 격차(compact depth 0.231 / rich 1.000, 결핍 10 feature 중 7개 슬롯 부재).
>
> **v1.3.0 (2026-06-03 Phase 15 S1, CC-017 적용)**: `output_mode` **3-tier**(compact<rich<**director**)
> 일반화 + `Plan` director 슬롯 3종 **additive** (전부 Optional): `hook_system`(재후크 설계) +
> `retention_architecture`(리텐션 구조) + `scene_breakdown[]`(DirectorScene 5필드: scene_intent/
> viewer_emotion/retention_device/why_this_works/fallback_scene). ★ director=**LLM-only**(데이터레이어
> 비의존). 직렬화는 `Plan.model_dump_for_mode(output_mode)` — compact(rich+director 제외)/rich(director
> 제외)/director(전부). **compact·rich 경로 byte-identical**(director 키 누수 0). 상업필드(market/
> audience/brand/conversion 등)는 제외=commercial_viral(PKM/RAG 후속). 기획 브리프 경계(촬영지시 아님).

```json
{
  "plan_candidates": [
    {
      "plan_id": "string (uuid)",
      "option_index": 0,
      "name": "string (10–16자)",
      "concept": "string (1–2줄)",
      "hook": "string (20–60자)",
      "flow": [
        {
          "beat_index": 0,
          "beat": "string",
          "duration_sec": 3,
          "purpose": "string",

          "visual": "string | null   // rich(v1.2.0): 화면/구도/연출 묘사",
          "dialogue": "string | null // rich(v1.2.0): 내레이션·대사",
          "caption": "string | null  // rich(v1.2.0): 자막 텍스트"
        }
      ],
      "pros": "string",
      "risks": "string",
      "approach_label": "narrative | informational | empathy | experiment | review | other",
      "rag_used": [
        { "source_id": "string", "title": "string", "used_reason": "string" }
      ],

      "target_audience": "string | null  // rich(v1.2.0): 타깃 시청자",
      "tone": "string | null             // rich(v1.2.0): 톤·무드",
      "hook_variants": ["string"],      // rich(v1.2.0): 후크 변형 (≤3, 기존 hook 외)
      "shots": ["string"],              // rich(v1.2.0): B-roll/샷 리스트
      "thumbnail": "string | null        // rich(v1.2.0): 썸네일 컨셉",
      "title_candidates": ["string"],   // rich(v1.2.0): 제목 후보 (≤5)
      "cta": "string | null              // rich(v1.2.0): Call-to-action",
      "references": ["string"],         // rich(v1.2.0): 창작 레퍼런스 (rag_used 와 구분, ≤5)
      "length_variants": ["string"],    // rich(v1.2.0): 길이 변형 (예: 30s/60s 컷)

      "hook_system": ["string"],        // director(v1.3.0): 첫 후크 + 재후크 지점 (≤5)
      "retention_architecture": "string | null  // director(v1.3.0): 리텐션 구조(이탈방지·호기심갭·페이싱)",
      "scene_breakdown": [              // director(v1.3.0): 씬 단위 분해 (기획 브리프 수준)
        {
          "scene_intent": "string",       // 이 씬의 기획 의도
          "viewer_emotion": "string",     // 의도하는 시청자 감정
          "retention_device": "string",   // 이탈 방지/호기심 장치
          "why_this_works": "string",     // 작동 근거 (일반론 금지)
          "fallback_scene": "string | null"  // 약할 때 대안 씬
        }
      ]
    }
  ]
}
```

> ★ **rich 슬롯은 전부 Optional/additive** — 미존재 시 `Plan` 은 기존 7필드(+rag_used)만으로 valid.
> Pydantic 모델 = `backend/fastapi/schemas/output.py` `Plan` / `PlanFlowBeat` (PLAN_RICH_FIELDS /
> BEAT_RICH_FIELDS 상수 + `Plan.model_dump_compact()` = OFF 경로 byte-identical 직렬화).

### 8.2 검증 규칙

```
- plan_candidates 길이 정확히 3 (Phase 4+), Phase 1 deviation은 1개 허용 (validation.warnings)
- option_index 0, 1, 2 각각 1번씩
- 3개의 approach_label이 서로 달라야 함 (의미적 중첩 < 30%)
- flow 배열 길이 3~6
- flow의 duration_sec 총합 == components.length_sec ± 10%
- hook 20~60자, 광고 카피톤 차단
- rag_used가 빈 배열인 경우 validation.warnings에 "no_rag_reference" 기록
- Brand Memory의 avoid_phrases 위반 시 즉시 재생성
- (v1.2.0, Phase 13 S1) rich 슬롯(target_audience/tone/hook_variants/shots/thumbnail/
  title_candidates/cta/references/length_variants/beat.visual/dialogue/caption)은 전부 Optional —
  미존재(None/[]) 시 검증 통과 (rich_output_enabled OFF 경로 compact 출력 회귀 0). rich 경로
  품질 검증은 S4 Critic depth_actionability 차원 + S6 depth 재측정에서.
```

### 8.3 RAG 참조 표기

`rag_used[]`는 P-006에서 실제 사용된 chunk만 기록. `rag_chunks.chunk_id`를 `source_id`로 사용.

→ DB 매핑: 3개 plan을 각각 `plan_options` row 3개로 저장 (option_index 0/1/2). `flow`는 `plan_options.flow` jsonb로 그대로 저장. `raw_llm_json`은 envelope 전체 보관.

---

## 9. P-007 · critic (Critic Agent)

품질 평가. plan 1개당 1번 호출.

> **Phase 6 ADR-018 (2026-05-29)**: Critic verdict canonical 결정.
> - canonical 필드: `overall_score: float [0.0~1.0]` + `dimensions: dict[str, float]`
> - deprecated 필드: `overall_score_avg`, `scores`, `eight_dim_scores` (Phase 9+ eval 후 제거)
> - 결정 근거: `docs/decisions/phase_6_critic_canonical.md`
>
> **Phase 9.5 ADR-034 (2026-05-31, CC-005)**: deprecated 0–5 Full 제거 완료.
> - `CriticEvaluation` 에서 deprecated 0–5 필드(`scores` / `overall_score_avg`) 제거 — canonical-only.
> - `select_best_plan_index` deprecated fallback(overall_score_avg / scores / eight_dim_scores +
>   `DeprecationWarning`) 제거 — canonical(overall_score → dimensions) 2 경로만.
> - `model_config extra='ignore'`: orchestrator/generate 가 normalize_to_canonical 산출 verdict dict
>   (run_critic 0–5 키 병행)를 `CriticEvaluation(**verdict)` 로 넘겨도 0–5 키 무시 → 회귀 0.
> - **run_critic 의 0–5 출력은 P-007 LLM-facing prompt contract 로 불변** (normalize_to_canonical 가
>   0–5→0–1 변환하는 canonical 생성 단일 경로). 결정 근거: `docs/decisions/phase_9_5_critic_deprecated_removal.md`.

### 9.1 Body 스키마 (Phase 6 canonical — Phase 9.5 canonical-only)

```json
{
  "overall_score": 0.85,
  "dimensions": {
    "intent_fit": 0.8,
    "target_clarity": 0.7,
    "hook_strength": 0.9,
    "message_clarity": 0.8,
    "structure": 0.7,
    "feasibility": 0.8,
    "brand_consistency": 0.9,
    "differentiation": 0.7
  },
  "overall_verdict": "approve | revise | reject",
  "blocking_issues": ["string"],

  /* --- Phase 1 호환 메타 (0–5 점수와 무관 — 잔존) --- */
  "target_plan_id": "string (uuid)?",
  "reasons": { /* 8-dim 문자열 dict */ },
  "suggestions": { /* 8-dim 문자열 dict */ },
  "revise_round": 0
}
```

> Phase 9.5 ADR-034: deprecated 0–5 필드(`scores`, `overall_score_avg`)는 제거되었다.
> 8-dim 점수는 canonical `dimensions`(0~1) 가 유일한 출처다.

### 9.1.1 canonical 필드 (Phase 6 ADR-018)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `overall_score` | float [0.0~1.0] | **canonical** | Critic 종합 점수 (정규화). dimensions 평균과 다를 수 있음 (Phase 9+ 가중치 도입 대비) |
| `dimensions` | dict[str, float] | **canonical** | 8-dim 점수 dict (정규화 0~1). 표준 키 8개는 §9.1.3 참조 |
| `overall_verdict` | Literal["approve", "revise", "reject"] | 필수 | 의사결정 카테고리 |
| `blocking_issues` | list[str] | Optional | 최대 3개 |

### 9.1.2 Deprecated 0–5 필드 — Phase 9.5 ADR-034 제거 완료

| 필드 | 상태 | 대체 |
|---|---|---|
| `overall_score_avg` | **제거** (Phase 9.5 ADR-034) | `overall_score` (0~1) |
| `scores` | **제거** (Phase 9.5 ADR-034) | `dimensions` (0~1 float) |
| `eight_dim_scores` | **제거** (Phase 9.5 ADR-034) | `dimensions` |
| `target_plan_id` | 잔존 (Phase 1 호환 메타 — plan_id echo, Optional) | — |
| `reasons`, `suggestions`, `revise_round` | 잔존 | — |

`CriticEvaluation` 은 `model_config extra='ignore'` 로 verdict dict 의 잔존 0–5 키를 무시한다 (회귀 0).
`select_best_plan_index` 는 canonical(overall_score → dimensions) 만 소비하며 더 이상 `DeprecationWarning`
을 발행하지 않는다. run_critic 의 0–5 출력은 P-007 LLM-facing prompt contract 로 불변.

### 9.1.3 dimensions 표준 키 8개

```
intent_fit / target_clarity / hook_strength / message_clarity /
structure / feasibility / brand_consistency / differentiation
```

Phase 9+ eval-run 정식화 시 별도 contract-change 절차로 키 확장 가능.

### 9.2 검증 규칙

```
- canonical: overall_score 0.0~1.0, dimensions 값 0.0~1.0
- reasons, suggestions의 키는 dimensions 의 키와 1:1 매칭 (8개)
- overall_verdict (canonical 기준 — run_critic 내부 0–5 산출은 P-007 LLM-facing, normalize_to_canonical 가 0–1 변환):
    approve:  overall_score ≥ 0.7
    revise:   0.5 ≤ overall_score < 0.7
    reject:   overall_score < 0.5  OR  광고적 표현 위반
- blocking_issues 최대 3개
- revise_round는 server-side에서 주입 (LLM은 항상 0 반환)
```

> run_critic 내부 verdict 산출 규칙(0–5 평균/미달 카운트 → approve/revise/reject)은 P-007 prompt contract
> (`agents/critic.py::_derive_verdict`) 로 불변. normalize_to_canonical 이 0–5→0–1 로 변환하여 canonical
> overall_score 를 생성한다.

### 9.3 revise 무한 루프 차단

`revise_round`는 server-side가 관리한다. `revise_round ≥ 2`에서 verdict가 다시 `revise`면 강제로 `approve`로 승격하거나 사용자에게 직접 검토 요청 (→ `agent_io_contract.md` §3.3).

→ DB 매핑: `quality_scores` 테이블에 그대로 매핑. `target_kind='plan_option'`, `target_id=target_plan_id`.

### 9.4 select_best_plan_index 우선순위 (Phase 6 ADR-018 + Phase 9.5 ADR-034)

`agents/critic.py::select_best_plan_index(verdicts) -> int | None` 의 score 추출 우선순위
(Phase 9.5 ADR-034 으로 deprecated 0–5 fallback 제거 — canonical 2 경로만):

```
1. overall_score (canonical)
2. dimensions 평균 (canonical fallback)
```

canonical(overall_score / dimensions) 부재 시 `None` (deprecated 0–5 키 overall_score_avg / scores /
eight_dim_scores 는 더 이상 fallback 으로 사용되지 않고 무시된다 — `DeprecationWarning` 미발행).
Tie-breaking: 동점 시 plan_index 가 더 작은 쪽 (deterministic).
모든 verdict 가 invalid 시 `None` 반환 (frontend wrapper highlight 생략).

---

## 9-A. Body 정식 등록 (Phase 6 Slice 2)

Phase 4.5 ADR-016 (revise loop) + ADR-017 (best-plan selection) 에서 도입된 필드를 Phase 6 contract 에 정식 등록.

### 9-A.1 Body.revise_history (Phase 4.5 ADR-016 + Phase 6 typing 강화 ADR-018)

```jsonc
"revise_history": [
  /* plan_candidates 와 동일 순서 (외부 list) */
  [
    /* attempt 0,1,2,... 순차 (내부 list) */
    {
      "attempt": 0,
      "action": "revise",
      "revised": true,
      "max_reached": false,
      "critic_warning": null,
      "rewriter_warning": null
    },
    { "attempt": 1, "action": "approve", "revised": false }
  ]
]
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `attempt` | int [0~max_revise] | 필수 | 0 = 초기 critic, 1+ = revise 후 재평가 |
| `action` | Literal["approve", "revise", "reject", "unknown"] | 필수 | Critic verdict (미정의 → "unknown" 폴백) |
| `revised` | bool | 필수 | 본 attempt 에서 Rewriter 호출 여부 |
| `max_reached` | bool | Optional | max_revise 도달 시 true |
| `critic_warning` | string | Optional | Critic 호출 실패 graceful 마커 |
| `rewriter_warning` | string | Optional | Rewriter 호출 실패 graceful 마커 |

Pydantic 모델: `backend/fastapi/schemas/output.py::ReviseAttempt` (extra="allow" — 미래 확장 메타 허용).

### 9-A.2 Body.recommended_plan_index (Phase 4.5 ADR-017, Z-X3)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `recommended_plan_index` | int [0~plan_count-1] \| null | Optional | Critic best-plan idx. 모든 verdict invalid / critic skip 시 null. Tie 발생 시 더 작은 index. Frontend wrapper highlight 용 (PlanCard.tsx 무수정 정책 — 사용자 결정 6-a 계승) |

### 9-A.3 Body.critic_evaluation (Phase 1 Slice 3 + Phase 6 canonical + Phase 9.5 canonical-only)

Phase 1 Slice 3 에서 도입. Phase 6 (§9.1) canonical fields (`overall_score`, `dimensions`) 추가.
Phase 9.5 (ADR-034) 에서 deprecated 0–5 필드(`scores`, `overall_score_avg`) 제거 — canonical-only.

---

## 10. P-008 · rewriter (Rewriter Agent)

Critic이 revise 판정한 plan을 개선.

### 10.1 Body 스키마

```json
{
  "improved_plan": {
    "plan_id": "string (원본과 동일한 uuid)",
    "option_index": 0,
    "name": "string",
    "concept": "string",
    "hook": "string",
    "flow": [
      { "beat_index": 0, "beat": "string", "duration_sec": 3, "purpose": "string" }
    ],
    "pros": "string",
    "risks": "string",
    "approach_label": "narrative | informational | empathy | experiment | review | other"
  },
  "changes_made": ["string"],
  "remaining_concerns": ["string"],
  "based_on_critic_id": "string (uuid of quality_scores row)"
}
```

### 10.2 검증 규칙

```
- improved_plan의 스키마는 P-006의 plan과 100% 동일
- plan_id는 원본 유지 (id 보존)
- changes_made는 최소 1개, 최대 10개
- Critic의 blocking_issues는 모두 해결 시도해야 함
- remaining_concerns가 비어있지 않으면 validation.warnings에 기록
- 광고적 표현, brand_memory.avoid_phrases 위반 시 자동 재생성 1회
```

→ DB 매핑: `revision_requests.rewriter_result`에 envelope 전체 보관. 사용자가 채택 시 `plan_options`의 원본 row를 UPDATE (raw_llm_json은 history로 별도 row 추가).

---

## 11. P-AUX-1 · intent_filter

영상기획 외 입력 차단.

### 11.1 Body 스키마

```json
{
  "decision": "allow | block | reframe_offer",
  "reason": "string",
  "reframe_suggestion": "string | null",
  "matched_categories": ["string"],
  "confidence": 0.0
}
```

### 11.2 검증 규칙

```
- decision은 3개 enum 중 하나
- decision == "reframe_offer"이면 reframe_suggestion이 null이 아니어야 함
- decision == "block"이면 reframe_suggestion = null
- decision == "allow"이면 reframe_suggestion = null
- matched_categories는 사전 정의된 카테고리에서만 (video_planning / general_coding / homework /
  daily_chat / political / search / test_input / event_content 등)
- confidence ≥ 0.6 미만이면 fallback은 "allow" (관대 기본값)
```

→ DB 매핑: `intent_filter_logs` 테이블. decision, reason 그대로 저장. reframe_suggestion은 사용자에게 노출하면 별도 클릭 이벤트로 기록.

---

## 12. P-AUX-2 · brand_memory_extractor

Brand Memory 자동 추출.

### 12.1 Body 스키마

```json
{
  "proposed_entries": [
    {
      "entry_type": "preferred_tone | avoid_phrase | preferred_phrase | success_pattern | rejection_pattern",
      "content": "string",
      "confidence": 0.0,
      "source_evidence": "string (어떤 선택/거절에서 도출했는지)",
      "conflicts_with_existing": false,
      "existing_entry_id": "string | null"
    }
  ],
  "session_summary": "string (≤200자, 이번 영상 세션의 한 줄 요약)"
}
```

### 12.2 검증 규칙

```
- proposed_entries 0~5개
- entry_type은 5개 enum 중 하나
- confidence 0~1
    1회성 결정    → ≤ 0.3
    2회 이상 반복 → ≥ 0.7
    명시적 선호  → ≥ 0.9
- conflicts_with_existing=true인 항목은 자동 적용 금지, 사용자 승인 필요
- session_summary는 200자 hard limit
```

→ DB 매핑: `brand_memory_entries`. 단 자동 INSERT는 confidence ≥ 0.7 + conflicts_with_existing=false 조건에서만. 그 외는 pending queue로 사용자 확인 대기.

---

## 13. 카드 5장 정책 (Discovery 공통)

```
원칙: "AI 추천 4장 + 사용자 직접 입력 1장 = 5장"

- LLM은 항상 4장만 생성한다 (5장째는 UI 단의 input slot)
- 4장의 의미적 유사도 < 30% (코사인 유사도 0.3 미만)
- 4장 모두 광고적 표현 사전 통과
- 사용자가 직접 입력 선택 시 discovery_choices.direct_input에 저장
- 사용자가 4장 모두 거절 시 자동 재생성 1회 → 그래도 거절 시 직접 입력 유도
```

UI 표시 순서 (apps/web/design.md §7 카드 그리드 참조):

```
[AI 카드 1] [AI 카드 2]
[AI 카드 3] [AI 카드 4]
[ + 직접 입력 카드   ]
```

---

## 14. 광고적 표현 차단 흐름

### 14.1 차단 대상 단어 사전

```
1차 차단 (즉시 재생성):
- "최고의", "최고", "단연 최고"
- "혁신적", "혁신적인", "혁명적"
- "획기적", "획기적인"
- "완벽한", "완벽"
- "1위", "넘버원"
- "압도적"
- "역대급" (단, 카운터 컨텍스트에서는 허용)

2차 경고 (warning만, 통과):
- "특별한", "특별"
- "놀라운"
- "엄청난"
```

### 14.2 검사 시점

```
1. LLM 응답 수신 직후 (envelope.validation.checks)
   → 1차 차단 단어 발견 시 자동 재생성 (최대 1회)
   → 재시도 후에도 위반 시 validation.passed=false 반환 + 사용자에게 에러 노출
2. Critic Agent (P-007)
   → brand_consistency 점수에 반영
3. final_outputs 저장 직전
   → 한 번 더 검사. 위반 시 final 저장 차단 + 운영자 알림.
```

### 14.3 예외

```
- 사용자가 직접 입력한 텍스트(direct_input)는 검사 대상이 아님 (자기 표현 존중)
- 단 사용자 직접 입력 텍스트가 LLM 출력에 그대로 인용되어 다시 들어오면 검사 대상
```

---

## 15. 검증 실패 시 처리

```
case A: validation.passed=true
  → 정상 처리. body 그대로 사용.

case B: validation.passed=false, validation.checks 중 retryable (ad_phrase, parse_error)
  → 서버가 자동 재시도 1회 (지수 백오프 적용)
  → 재시도 후 passed=true이면 정상 처리
  → 재시도 후에도 false이면 case C로 fallback

case C: validation.passed=false, 재시도 실패 또는 non-retryable
  → error_response_contract.md의 표준 에러 응답으로 변환
  → code: E-LLM-VAL-001 (검증 실패)
  → user_message: "AI 응답을 다듬는 중 문제가 생겼어요. 다시 시도해주세요."
  → 부분 결과가 있으면 partial_result 필드에 포함
```

→ 자세한 에러 응답 형식은 `error_response_contract.md` §3 참조.

---

## 16. 광고/금지 표현 단어 사전 관리

```
저장 위치: knowledge/llm_wiki/style_guide/ad_phrase_blocklist.md
업데이트 주체: 운영자 + Critic 누적 위반 통계 기반 자동 제안
업데이트 절차: contract-change Skill 절차 (PR + 회귀 평가)
prompt와 결합: 모든 P-001~P-008 system prompt에 자동 prefix
```

---

## 17. 최종 산출물 통합 JSON (legacy final_outputs)

`video_projects.status == 'final'` 시점에 모든 prompt 결과를 합쳐 만드는 패키지.

```json
{
  "video_id": "string",
  "plan_id": "string (selected_plans.selected_option_id)",
  "project_id": "string",
  "one_line_direction": "string",
  "target_analysis": {
    "primary_target": "string",
    "target_need": "string",
    "expected_reaction": "string"
  },
  "format": "shorts_30s | reels_60s | shorts_60s | youtube_3m | youtube_8m | other",
  "tone": "string (brand.tone.primary)",
  "hook_candidates": [
    { "id": "string", "hook": "string", "rationale": "string", "risk": "string" }
  ],
  "video_structure": [
    {
      "section": "intro | body | transition | ending",
      "time_range": "string",
      "content": "string",
      "visual_note": "string"
    }
  ],
  "shooting_notes": [
    { "type": "camera | location | prop | acting | editing", "note": "string" }
  ],
  "quality_review": {
    "intent_fit": 0,
    "target_clarity": 0,
    "hook_strength": 0,
    "message_clarity": 0,
    "structure": 0,
    "feasibility": 0,
    "brand_consistency": 0,
    "differentiation": 0,
    "overall_score": 0,
    "review_summary": "string"
  },
  "revision_suggestions": [
    { "issue": "string", "suggestion": "string", "priority": "high | medium | low" }
  ],
  "rag_references": [
    { "source_id": "string", "title": "string", "used_reason": "string" }
  ],
  "upload_caption": "string",
  "hashtags": ["string"],
  "community_hooks": "string"
}
```

→ DB 매핑: `final_outputs` 테이블 전체. `raw_payload`에 위 JSON을 그대로 보관.

---

## 18. 공통 enum 사전

```
mode: discovery | quick
format: shorts_30s | shorts_60s | reels_60s | youtube_3m | youtube_8m | other
structure_type: growth_record | experiment | community | review | informational | narrative | event_based | other
approach_label: narrative | informational | empathy | experiment | review | other
section: intro | body | transition | ending
shooting_note_type: camera | location | prop | acting | editing
priority: high | medium | low
critic_verdict: approve | revise | reject
intent_decision: allow | block | reframe_offer
entry_type: preferred_tone | avoid_phrase | preferred_phrase | success_pattern | rejection_pattern
source_kind: user_choice | user_feedback | final_output | manual
candidate_status: pending | filtered | evaluated | approved | promoted | rejected
event_type: like | dislike | reject | regenerate
```

새 enum 값 추가 시 minor bump + 모든 의존 prompt에 적용 여부 명시.

---

## 19. 버전 관리

### 19.1 semver

```
MAJOR: 기존 필드 제거, 필드 타입 변경, enum 값 제거
MINOR: 새 필드 추가 (옵셔널), 새 enum 값 추가
PATCH: 설명 수정, 검증 규칙 강화 (기존 통과 케이스 영향 없음)
```

### 19.2 회귀 평가

```
변경 시 절차:
1. eval/golden_set.md의 50개 시드 케이스를 새 스키마로 재실행
2. validation.passed 비율 ≥ 95% 유지 확인
3. Critic의 canonical overall_score (0~1) 평균 변화 ≤ ±0.3 확인 (Phase 9.5 ADR-034 — deprecated overall_score_avg 제거)
4. 실패 케이스가 있으면 prompt_registry.md와 함께 재조정
```

### 19.3 deprecation

```
- 필드 제거 예정 시: validation.warnings에 "deprecated: field_name" 1 phase 이상 누적
- enum 값 제거 시: 최소 2 phase deprecation 표시 후 제거
- breaking change는 한 commit에 prompt_registry + output_schema + db_schema 동시 갱신
```

---

## 20. Cross-reference 빠른 표

| Prompt | DB 저장 위치 | 의존 contract |
|---|---|---|
| P-001 | `discovery_choices`, `brands.direction_label` | db_schema.md §3.2, §5.1 |
| P-002 | `discovery_choices`, `domains` | db_schema.md §3.3, §5.1 |
| P-003 | `discovery_choices`, `series` | db_schema.md §3.4, §5.1 |
| P-004 | `discovery_choices`, `brands.tone`, `video_briefs.target` | db_schema.md §3.2, §4.1 |
| P-005 | `video_projects.one_line_direction` | db_schema.md §3.5 |
| P-006 | `plan_options` × 3 | db_schema.md §4.2 |
| P-007 | `quality_scores` | db_schema.md §4.5 |
| P-008 | `revision_requests.rewriter_result` | db_schema.md §4.6 |
| P-AUX-1 | `intent_filter_logs` | db_schema.md §5.3 |
| P-AUX-2 | `brand_memory_entries` (pending queue) | db_schema.md §6 |

모든 prompt 응답은 `agent_io_logs.output_payload`에 envelope 전체로 저장된다.

---

## 21. 확장 가능성 (Phase 2+)

```
- multi-locale: meta.locale에 "en-US", "ja-JP" 추가 + 단어 사전 분기
- voice mode: P-005에 voice_input_transcript 필드 추가 (옵셔널)
- multi-modal: P-006에 reference_image_urls 추가 (사용자가 영감 이미지 제공)
- 3개가 아닌 N개 plan: P-006 plans 길이 가변 (현재 hard 3)
- streaming output: envelope에 chunk_index, is_final 추가 → SSE 호환
- team workspace: meta에 workspace_id 추가
```

---

## 22. Open Questions

1. P-006의 `flow.duration_sec` 총합 허용 오차 (현재 ±10%) — 사용자 검증 결과에 따라 조정.
2. P-007의 `revise_round` 강제 승격 시 사용자 안내 문구 — UX 협의 필요.
3. P-AUX-2의 자동 INSERT 임계치 (현재 confidence 0.7) — 누적 데이터로 조정.
4. 카드 의미 중첩 30% 측정 — embedding 기반 vs 토큰 자카드 vs LLM-as-judge.
5. enum 값 "other"의 운영 정책 — 빈도 누적 시 정식 enum 승격 트리거.
6. `meta.schema_version`과 `prompt_version`의 호환성 매트릭스 별도 관리 필요 여부.
7. `direct_input` 사용자 텍스트가 LLM 재인용으로 들어올 때 광고 단어 검사 우회 정책.

---

## 23. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-1 초안. 10 prompt 전체 스키마, envelope, 검증 흐름, enum 사전.
v1.1.0 (2026-05-29, Phase 6 Slice 2):
  - §9 Critic canonical 결정 (overall_score [0~1] + dimensions: dict[str, float]) — ADR-018
  - §9.1.2 deprecated 필드 표 추가 (overall_score_avg / scores / eight_dim_scores)
  - §9.4 select_best_plan_index 우선순위 명시 (canonical → deprecated + DeprecationWarning)
  - §9-A Body 정식 등록: revise_history (ReviseAttempt typing 강화) + recommended_plan_index
    + critic_evaluation canonical 추가
  - semver minor bump: 신규 필드 (overall_score / dimensions) 추가 + Optional 호환 유지.
v1.2.0 (2026-05-31, Phase 9.5 Slice 4 — CC-005 / ADR-034):
  - §9 Critic deprecated 0–5 Full 제거 (canonical-only):
    - §9.1 Body 스키마에서 deprecated 필드(scores / overall_score_avg) 제거 — canonical(overall_score 0–1
      + dimensions) + Phase 1 호환 메타(target_plan_id / reasons / suggestions / revise_round) 만.
    - §9.1.2 deprecated 필드 표 → "Phase 9.5 ADR-034 제거 완료" 로 갱신 (scores / overall_score_avg /
      eight_dim_scores 제거, model_config extra='ignore' 로 회귀 0).
    - §9.4 select_best_plan_index 우선순위: deprecated fallback 3~5 단계 + DeprecationWarning 제거 →
      canonical 2 경로 (overall_score → dimensions).
    - §9.2 검증 규칙: canonical(0–1) 기준으로 정리. run_critic 0–5 산출 + normalize_to_canonical 변환은
      P-007 LLM-facing prompt contract 로 불변 명시.
  - semver minor bump: deprecated 필드 제거는 canonical-only 전환 (extra='ignore' + eval baseline 회귀 0).
```
