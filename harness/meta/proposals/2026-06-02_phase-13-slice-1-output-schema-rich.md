# Contract Change Proposal: Phase 13 Slice 1 — output_schema.md §8.1 Plan rich 슬롯 additive 확장

- 제안일: 2026-06-02
- 제안자: Claude Code (Phase 13 검증 세션 — 결과검증 + 제안서 작성 전용)
- 대상 contract: `docs/contracts/output_schema.md` (§8.1 Plan body) — agent_io_contract 정합 확인 동반
- 변경 종류: **수정 (★ additive — 전부 Optional, breaking change 아님)**
- 긴급도: 보통 (Phase 13 S1 의무, 후속 S2~S6 차단 의존)
- ID: CC-012 (예정 — Phase 12 CC-011 계승)
- 근거 phase 문서: `phases/active/phase-13-output-enrichment/{scope,acceptance,multi_slice_plan}.md` (메인 세션 작성 entry, commit aaf4641)
- ★ 본 제안서는 **계획만** — 실제 `output_schema.md` / `output.py` 편집은 승인 후 메인 세션에서.

---

## 변경 사유 (결과검증 기반)

Phase 12 깊이 격차 실측(`eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md`)이 확정:

1. **같은 모델(gpt-4o-mini)** 로 compact(운영) vs rich(확장 프롬프트) 측정 → **depth 0.231 → 1.000 (4.3x), 6/6 케이스 편차 0**.
2. `depth_actionability` 13 feature 중 compact 는 **3개만 보유**(beats_3plus / beat_visual / cta), **10개 결핍**.
3. 결핍 10개 중 **7개**(대사·자막·샷/B-roll·썸네일·제목후보·레퍼런스·길이변형)는 **`Plan` 스키마에 슬롯 자체가 없어**, 모델이 생성해도 응답 envelope 에 담기지 않는다.
4. → 확장 레버 = **프롬프트(S2) + 스키마(본 S1)**. 스키마 슬롯이 없으면 프롬프트만 확장해도 출력이 구조화되지 않음. **S1 이 S2/S5/S6 의 선행 의존.**

★ 안전 설계: 이 프로젝트 **첫 의도적 출력 변경**이므로 — **전부 Optional/additive** + 실제 채움은 S3 의 `rich_output_enabled` flag(default False) ON 경로에서만. flag OFF → 기존 7필드 직렬화 byte-identical(behavior-preserving, acceptance A5-PP).

---

## 결핍 feature → 슬롯 매핑 (깊이 격차 리포트 §3 기준)

| # | 결핍 feature | compact | 신규 슬롯 (위치) | 타입 (전부 Optional/additive) | 비고 |
|---|---|---|---|---|---|
| 1 | target_audience | 0.00 | `Plan.target_audience` | `str \| None = None` | 타깃 시청자 |
| 2 | tone | 0.00 | `Plan.tone` | `str \| None = None` | 톤·무드 |
| 3 | hook_variants | 0.00 (후크 1개뿐) | `Plan.hook_variants` | `list[str] = [] (max 3)` | ★ 기존 단일 `hook` 보존, 변형만 추가 |
| 4 | beat_dialogue | 0.00 (슬롯 없음) | `PlanFlowBeat.dialogue` | `str \| None = None` | 내레이션/대사 |
| 5 | beat_caption | 0.00 (슬롯 없음) | `PlanFlowBeat.caption` | `str \| None = None` | 자막 텍스트 |
| 6 | shots_broll | 0.00 (슬롯 없음) | `PlanFlowBeat.visual` + `Plan.shots` | `str \| None` + `list[str] = []` | 화면 묘사(beat별) + B-roll/샷 리스트(plan별) |
| 7 | thumbnail | 0.00 (슬롯 없음) | `Plan.thumbnail` | `str \| None = None` | 썸네일 컨셉 |
| 8 | title_candidates | 0.00 (슬롯 없음) | `Plan.title_candidates` | `list[str] = [] (max 5)` | 제목 후보 |
| 9 | references | 0.00 (슬롯 없음) | `Plan.references` | `list[str] = [] (max 5)` | ★ `rag_used`(RAG 출처)와 구분 — 창작 레퍼런스 |
| 10 | length_variants | 0.00 (슬롯 없음) | `Plan.length_variants` | `list[str] = []` | 길이 변형(예: 30s/60s 컷) |
| (보유) | beat_visual | 1.00 | `PlanFlowBeat.visual` (#6과 동일) | — | compact 는 `beat` 라벨로 암묵 보유 → `visual` 로 **명시화**(중복 주의, 아래 결정 1) |
| (보유) | cta | 1.00 | `Plan.cta` | `str \| None = None` | compact 는 `purpose` 로 암묵 보유 → `cta` 로 **명시화**(중복 주의, 아래 결정 2) |

→ 신규 슬롯: **`Plan` 9개** (target_audience, tone, hook_variants, shots, thumbnail, title_candidates, cta, references, length_variants) + **`PlanFlowBeat` 3개** (visual, dialogue, caption). 전부 Optional default None/[].

---

## 변경 내용 (before/after)

### Before — `output_schema.md` §8.1 Body 스키마

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
        { "beat_index": 0, "beat": "string", "duration_sec": 3, "purpose": "string" }
      ],
      "pros": "string",
      "risks": "string",
      "approach_label": "narrative | informational | empathy | experiment | review | other",
      "rag_used": [ { "source_id": "string", "title": "string", "used_reason": "string" } ]
    }
  ]
}
```

### After — §8.1 (★ rich 슬롯 전부 Optional/additive, flag ON 경로에서만 채워짐)

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
          "beat_index": 0, "beat": "string", "duration_sec": 3, "purpose": "string",
          "visual": "string | null (rich) — 화면/구도/연출 묘사",
          "dialogue": "string | null (rich) — 내레이션·대사",
          "caption": "string | null (rich) — 자막 텍스트"
        }
      ],
      "pros": "string",
      "risks": "string",
      "approach_label": "narrative | informational | empathy | experiment | review | other",
      "rag_used": [ { "source_id": "string", "title": "string", "used_reason": "string" } ],

      "target_audience": "string | null (rich) — 타깃 시청자",
      "tone": "string | null (rich) — 톤·무드",
      "hook_variants": ["string (rich, ≤3) — 후크 변형 (기존 hook 외 추가)"],
      "shots": ["string (rich) — B-roll/샷 리스트"],
      "thumbnail": "string | null (rich) — 썸네일 컨셉",
      "title_candidates": ["string (rich, ≤5) — 제목 후보"],
      "cta": "string | null (rich) — Call-to-action",
      "references": ["string (rich, ≤5) — 창작 레퍼런스 (rag_used 와 구분)"],
      "length_variants": ["string (rich) — 길이 변형 (예: 30s/60s 컷)"]
    }
  ]
}
```

> §8.1 헤더에 버전 노트 추가: `v1.2.0 (2026-06-XX Phase 13 S1 CC-012): rich 슬롯 12종 additive (전부 Optional). flag OFF 시 기존 7필드 byte-identical.`

### §8.2 검증 규칙 — 변경 최소 (additive 주석만)

기존 규칙(plan_candidates 3 / flow 3~6 / hook 자수 등) **전부 유지**. 다음 1줄만 추가:

```
- rich 슬롯(target_audience/tone/hook_variants/shots/thumbnail/title_candidates/cta/references/
  length_variants/beat.visual/dialogue/caption)은 전부 Optional — 미존재(None/[]) 시 검증 통과
  (rich_output_enabled OFF 경로의 compact 출력 회귀 0). rich 경로 품질 검증은 S4 Critic
  depth_actionability 차원 + S6 depth 재측정에서.
```

### 구현 측 (output.py) — 승인 후 메인 세션 적용 diff 미리보기

```python
# PlanFlowBeat 에 추가 (전부 Optional)
class PlanFlowBeat(BaseModel):
    beat_index: int = Field(..., ge=0)
    beat: str = Field(..., min_length=1)
    duration_sec: int = Field(..., ge=1)
    purpose: str = Field(..., min_length=1)
    # ── Phase 13 S1 rich (additive, Optional) ──
    visual: str | None = Field(default=None, description="rich: 화면/구도/연출 묘사")
    dialogue: str | None = Field(default=None, description="rich: 내레이션·대사")
    caption: str | None = Field(default=None, description="rich: 자막 텍스트")

# Plan 에 추가 (기존 7필드 + rag_used 보존, 아래 9개 전부 Optional)
class Plan(BaseModel):
    # ... 기존 필드 그대로 ...
    rag_used: list[dict[str, Any]] = Field(default_factory=list)
    # ── Phase 13 S1 rich (additive, Optional) ──
    target_audience: str | None = Field(default=None, description="rich: 타깃 시청자")
    tone: str | None = Field(default=None, description="rich: 톤·무드")
    hook_variants: list[str] = Field(default_factory=list, max_length=3, description="rich: 후크 변형")
    shots: list[str] = Field(default_factory=list, description="rich: B-roll/샷 리스트")
    thumbnail: str | None = Field(default=None, description="rich: 썸네일 컨셉")
    title_candidates: list[str] = Field(default_factory=list, max_length=5, description="rich: 제목 후보")
    cta: str | None = Field(default=None, description="rich: Call-to-action")
    references: list[str] = Field(default_factory=list, max_length=5, description="rich: 창작 레퍼런스")
    length_variants: list[str] = Field(default_factory=list, description="rich: 길이 변형")
```

★ Pydantic v2 Optional default → 기존 `Plan(**compact_dict)` / 직렬화 회귀 0 (rich 키 미존재 시 None/[] 기본값, `model_dump()` 에 키는 노출되나 값 None/[] — 아래 결정 3에서 직렬화 정책 확정).

---

## 영향 받는 영역 (자동 점검 결과)

- [x] **Output Schema** — `output_schema.md §8.1` Plan body (본 변경 핵심)
- [x] **Agent IO** — `agent_io_contract.md §4.3` 은 "§8 P-006 body" **참조만**(필드 미중복) → **본문 변경 불필요**, agent-io-check 로 정합 확인만 (Planning 출력이 확장 §8.1 과 일치하는지)
- [x] **Pydantic 모델** — `backend/fastapi/schemas/output.py` `Plan` + `PlanFlowBeat` (additive)
- [ ] **API 응답 형식** — 키는 추가되나 flag OFF 시 값 None/[] (S3 gated, 본 S1 범위 밖)
- [ ] **프론트 컴포넌트** — `PlanCard.tsx` / `lib/types.ts` rich 렌더는 **S5** (본 S1 범위 밖, conditional)
- [ ] **Prompt** — rich 슬롯 채우는 P-006 프롬프트 확장은 **S2** (prompt-version-review, 범위 밖)
- [ ] DB 스키마 / RAG / 보안 — 영향 없음 (`plan_options.raw_llm_json` jsonb 가 envelope 전체 보관 → 신규 키 자동 수용, 마이그레이션 불필요)
- [ ] **평가 / golden_set** — depth_actionability(CC-011) 가 이 슬롯들을 채점 (Phase 12 정의 완료) → 본 변경이 측정 대상 슬롯을 실제 구현

## 영향 받는 파일 목록

```
docs/contracts/output_schema.md                                  (§8.1 + §8.2 1줄 — 본 변경 대상)
backend/fastapi/schemas/output.py                                (Plan + PlanFlowBeat additive)
docs/contracts/agent_io_contract.md                             (변경 없음 — agent-io-check 정합 확인만)
docs/contract_changes/2026-06-XX_phase-13-output-schema-rich.md (CC-012 로그 — 신규)
backend/fastapi/tests/...                                        (rich Optional default + compact 직렬화 회귀 0 — 신규)
```

## Rollback 방안

- additive Optional 이므로 rollback 단순: `Plan`/`PlanFlowBeat` 신규 필드 제거 + §8.1 rich 블록 제거 → 기존 7필드 스키마로 즉시 복귀 (기존 데이터·소비자 무영향, rich 키는 `raw_llm_json` 에만 잔존하나 무해).
- flag(S3 `rich_output_enabled`) 가 default False 이므로, S1 만 머지되고 S2~ 미완이어도 운영 출력은 compact 그대로 (실질 rollback 불필요).

## 마이그레이션 필요 여부

- [ ] DB 마이그레이션 — **불필요** (`plan_options.flow` jsonb / `raw_llm_json` jsonb 가 신규 키 자동 수용)
- [ ] 기존 데이터 변환 — 불필요 (Optional, 과거 plan 은 None/[])
- [ ] 사용자 통지 — 불필요 (flag OFF default, 출력 불변)
- [ ] 외부 API 클라이언트 통지 — 불필요 (additive, 기존 키 불변)

---

## ★ 결정 필요 사항 (사용자 승인 시 함께 확정)

1. **`PlanFlowBeat.visual` 중복 여부** — compact 의 `beat`(비트 라벨)가 이미 화면 묘사를 암묵 포함(depth 리포트 beat_visual=1.00). `visual` 을 별도 슬롯으로 두면 명시적이나 `beat` 와 의미 중복 가능.
   - (a) **추천**: `visual` 추가하되 "연출/카메라/구도 등 `beat` 보다 구체적 화면 지시" 로 역할 분리.
   - (b) `visual` 생략, `beat` 만 사용(슬롯 11개로 축소).
2. **`Plan.cta` 중복 여부** — compact 는 마지막 beat 의 `purpose` 로 CTA 를 암묵 표현(depth cta=1.00). 명시 `cta` 슬롯 추가 vs purpose 재사용.
   - (a) **추천**: `cta` 추가(plan 단위 명시 CTA — purpose 와 별개).
   - (b) 생략.
3. **직렬화 정책** — rich 슬롯이 None/[] 일 때 `model_dump()` 에 키를 **노출할지(현 기본)** vs **`exclude_none`/`exclude_defaults` 로 숨길지**. 후자면 flag OFF 출력이 기존과 **완전 byte-identical**(키 추가도 없음) → A5-PP 더 강하게 보장. **추천: flag OFF 경로(compact)는 `exclude` 로 rich 키 미노출 → byte-identical, flag ON 경로만 rich 키 직렬화.** (S3 wiring 과 연동 — S1 에서는 정책만 합의, 구현은 S3.)
4. **타입 단순(str/list[str]) vs 구조화(sub-model)** — 예: `length_variants` 를 `[{label, length_sec, note}]` 객체로? S1 은 **단순 타입(str/list[str])** 으로 최소화(프론트 S5 mirror 단순), 구조화는 후속 phase 백로그. **추천: 단순 타입.**

---

## 승인 기준

- 본 변경 = **새 필드 12개 추가 + 영향 파일 3개 이상** → **사용자 승인 필요** (자기 단독 결정 범위 아님).
- breaking change 아님(전부 Optional/additive) → breaking 특별 절차(7일 deactivation 등) 불요.
- 보안/비용 contract 미변경 → security-review/cost-review 추가 트리거 불요 (cost 는 rich **운영 활성** 시점인 **S6** 에서 cost-review).

## 결정

- [x] **승인 + applied** (추천안 — rich 슬롯 12종 전부)
- 결정자: 사용자 (songbyeongcheol)
- 결정일: 2026-06-02
- 메모: 결정 **1(a) visual 추가**(beat 보다 구체적 화면 지시로 역할 분리) / **2(a) cta 추가**(plan 단위 명시 CTA) / **3 직렬화 = compact 경로 rich 키 exclude → byte-identical** (`Plan.model_dump_compact()` capability = S1 / OFF 경로 호출 wiring = S3) / **4 단순 타입(str/list[str])** — 구조화 sub-model 은 후속 백로그.
- ★ **반영 완료 (2026-06-02, 검증 세션에서 직접)**: `output_schema.md` §8.1 v1.2.0 + `schemas/output.py` Plan/PlanFlowBeat rich 12 + 상수 + model_dump_compact() + CC-012 로그 + agent-io-check PASS + 신규 test 10 → **pytest 481 (471+10) green**. commit 대기.

---

## 승인 후 반영 절차 (메인 세션 — contract-change §5)

1. `docs/contracts/output_schema.md` §8.1/§8.2 실제 편집 (After 블록).
2. `backend/fastapi/schemas/output.py` `Plan`/`PlanFlowBeat` additive 필드 추가.
3. `docs/contract_changes/2026-06-XX_phase-13-output-schema-rich.md` CC-012 로그 작성.
4. **agent-io-check** Skill — Planning 출력(P-006)이 확장 §8.1 과 정합 + Critic/Rewriter/orchestrator 소비 회귀 0 확인.
5. tests 추가 — ① rich 슬롯 Optional default(None/[]) ② 기존 compact `Plan(**dict)` 직렬화 회귀 0 ③ (결정 3 채택 시) compact 경로 exclude byte-identical.
6. 본 제안서에 "approved" + 결정일 기록 → `PROJECT_STATE.md` last_contract_change 갱신.
7. → S2(프롬프트 P-006 bump)로 진행 (rich 슬롯을 채우는 프롬프트).

## acceptance 연결 (phase-13/acceptance.md)

- **A1** 스키마 확장(additive, 기존 7필드 회귀 0) ← 본 제안 §변경내용 + 결정 3.
- **A2** output_schema contract-change(additive) + CC 로그 ← §승인 후 반영 1·3.
- **A5-PP** flag OFF byte-identical ← 결정 3(exclude 직렬화) + S3.
- **MG2** contract-change additive/behavior-preserving ← 본 제안 전체.
