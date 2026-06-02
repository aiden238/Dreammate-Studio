# Contract Change Log — Phase 13 Slice 1 output_schema rich 슬롯 확장 (compact → rich, additive)

> ID: CC-012
> Status: **decided + applied** (2026-06-02, Phase 13 Slice 1)
> Date: 2026-06-02
> Decision: Phase 12 깊이 격차(compact 0.231 / rich 1.000, 4.3x) 반영 1단계 — `Plan` 결핍 feature 슬롯을 **additive(전부 Optional)** 로 확장. rich 값은 `rich_output_enabled` flag ON(S3) 경로에서만 채워지고, OFF(default) 경로는 byte-identical.
> Author: Claude (Phase 13 Slice 1 — 검증 세션에서 직접 적용)
> Related contracts: `docs/contracts/output_schema.md` (§8.1 Plan body — v1.1.0 → **v1.2.0**), `docs/contracts/agent_io_contract.md` (§4.3 "§8 P-006 body" 참조 — **본문 무변경**, agent-io-check 정합만)
> Related proposal: `meta/proposals/2026-06-02_phase-13-slice-1-output-schema-rich.md` (승인 2026-06-02, 결정 1a/2a/3-exclude/4-simple)
> Related CC: CC-011 (`2026-06-02_phase-12-s1-golden-set-depth.md` — depth_actionability 차원 = 본 슬롯들의 채점 기준)
> Related phase: `phases/active/phase-13-output-enrichment/` (acceptance A1/A2/A5-PP/MG2)
> Skill: contract-change (절차) + agent-io-check (정합)

---

## 1. 변경 요약

| 대상 | 변경 | 종류 |
|---|---|---|
| `docs/contracts/output_schema.md` §8.1 | `Plan` rich 9종(target_audience/tone/hook_variants/shots/thumbnail/title_candidates/cta/references/length_variants) + `flow[]`(PlanFlowBeat) rich 3종(visual/dialogue/caption) 등록. v1.1.0 → **v1.2.0** 버전 노트. | **additive** (전부 Optional, 기존 7필드 무변경) |
| `docs/contracts/output_schema.md` §8.2 | rich 슬롯 전부 Optional — 미존재 시 검증 통과 1줄 추가. 기존 규칙(3안/flow 3~6/hook 자수/rag_used 등) 무변경. | **additive** |
| `backend/fastapi/schemas/output.py` `Plan` / `PlanFlowBeat` | rich 12 필드(전부 Optional default None/[]) + `PLAN_RICH_FIELDS`/`BEAT_RICH_FIELDS` 상수 + `Plan.model_dump_compact()` (OFF 경로 byte-identical 직렬화 capability). | **additive** |
| `docs/contracts/agent_io_contract.md` | **무변경** — §4.3 이 output_schema §8 을 참조만 (필드 미중복). agent-io-check 로 Planning(P-006) 출력 정합 확인만. | — |

## 2. 코드 영향

```
backend/fastapi/schemas/output.py  — additive:
  PlanFlowBeat: +visual / +dialogue / +caption (전부 str|None = None).
  Plan: +target_audience / +tone(str|None) + hook_variants(≤3) / shots / title_candidates(≤5) /
        references(≤5) / length_variants (list[str]=[]) + thumbnail / cta(str|None).
  + PLAN_RICH_FIELDS / BEAT_RICH_FIELDS frozenset 상수.
  + Plan.model_dump_compact() — rich 키 제외 직렬화 (S3 OFF 경로가 호출 예정, S1 은 capability 제공만).

backend/fastapi/orchestration/moa_orchestrator.py  — 무변경.
  ★ Plan(...) 생성(L205/L319)이 named 7필드만 전달 → rich 필드는 기본값(None/[]) → 출력 키만 추가될 뿐
    값은 전부 None/[]. rich 를 실제로 채우는 분기는 S3(gated wiring).
backend/fastapi/routers/generate.py · plans.py  — 무변경 (S3 에서 OFF 경로 model_dump_compact 분기).
backend/fastapi/agents/{planning,critic,rewriter}.py  — 무변경 (rich 프롬프트는 S2 / depth 차원은 S4).
apps/web/**  — 무변경 (rich conditional 렌더는 S5).
```

## 3. 회귀 안전 근거 (behavior-preserving)

- **additive Optional ★**: rich 12 필드 전부 default None/[] → 기존 `Plan(**compact_dict)` 인스턴스화·
  기존 7필드(+rag_used) 직렬화 회귀 0. Pydantic extra='ignore' default 라 dict 에 rich 키 부재도 무해.
- **소비자 무영향 ★**: orchestrator/Critic/Rewriter/PlanCard 는 기존 필드만 읽음. rich 키 추가는
  이들 로직에 미치는 영향 0 (읽지 않는 키).
- **byte-identical capability ★**: `Plan.model_dump_compact()` 가 PLAN_RICH_FIELDS + flow 의
  BEAT_RICH_FIELDS 를 exclude → Phase 12 이전 7필드(+rag_used) 출력과 완전 동일. S3 의 OFF 경로가
  이를 호출하면 acceptance A5-PP(flag OFF byte-identical) 충족. ★ S1 은 capability + 테스트만, 실 wiring 은 S3.
- **S1 단독 출력 변화(정직한 기재)**: S3 wiring 전(S1 만 머지된 상태)에는 orchestrator 가 평소대로
  `model_dump(mode="json")` 를 쓰므로 envelope 의 각 plan 에 rich 키 12종이 **값 None/[]** 로 노출된다
  (기존 7필드 값은 불변 — additive). 운영 의미 변화는 S3 의 gated 분기에서 통제(OFF=compact 출력).
- **테스트 영향**: 기존 471 중 plan 키 셋을 엄격 비교하는 단언 없음(body 레벨·dimensions 키 비교만 존재 →
  영향 0). 신규 테스트는 §4 참조.

## 4. 검증 결과

```
신규 test (backend/fastapi/tests/test_output_rich_schema.py):
  - rich 12 필드 Optional default(None/[]) 인스턴스화.
  - compact Plan.model_dump_compact() == 기존 7필드(+rag_used) dict (rich 키 0개, flow 에 beat rich 키 0개) — byte-identical.
  - rich 채운 Plan: model_dump 에 rich 값 보존 / model_dump_compact 에서는 제외.
  - max_length 가드(hook_variants ≤3 / title_candidates ≤5 / references ≤5).
  - Body(plan_candidates=[compact plan]) 검증 통과 (소비자 회귀 0).
pytest backend/fastapi/tests/: 471 → 471 + 신규 PASS (기존 471 수정 0).
agent-io-check: Planning(P-006) 출력 ↔ output_schema §8.1 v1.2.0 정합 / Critic·Rewriter·orchestrator 소비 회귀 0.
운영 코드 변경: schemas/output.py (additive) 만. orchestration/routers/agents/apps 무변경.
키 commit: 0.
```

## 5. Rollback

- `output_schema.md`: §8.1 v1.2.0 rich 블록 + 버전 노트 + §8.2 1줄 git revert → v1.1.0(7필드) 복귀.
- `schemas/output.py`: PlanFlowBeat/Plan rich 필드 + 상수 + model_dump_compact() 제거 → 기존 스키마 복귀.
- additive 라 복귀 시 기존 데이터·소비자 무영향 (rich 키는 raw_llm_json jsonb 에만 잔존하나 무해).
- DB 마이그레이션 불필요 (`plan_options.flow` / `raw_llm_json` jsonb 가 신규 키 자동 수용).

## 6. 변경 이력

- 2026-06-02: Phase 13 Slice 1 — output_schema §8.1 v1.1.0 → v1.2.0 (Plan rich 9 + beat rich 3, 전부
  Optional additive) + `Plan.model_dump_compact()`(A5-PP capability) + 상수 2종. 근거: Phase 12 깊이 격차
  리포트(결핍 10 feature 중 7개 슬롯 부재) + 승인 제안서(결정 1a visual / 2a cta / 3 exclude / 4 단순타입).
  다음: S2(planning rich 프롬프트 + P-006 v1.1.0 bump, prompt-version-review).
