# Contract Change Log — Phase 13 Slice S3 rich 출력 gated wiring (config flag + 직렬화 분기)

> ID: CC-014
> Status: **decided + applied** (2026-06-03, Phase 13 Slice S3)
> Date: 2026-06-03
> Decision: `rich_output_enabled`(default **False**) flag 로 S1 rich 스키마(CC-012) + S2 rich 프롬프트(CC-013)
>           를 라이브 응답 경로(/generate + /plans/{id}/generate)에 연결한다. **OFF=compact byte-identical**
>           (Phase 13 이전과 동일 — 기존 486 테스트가 게이트), **ON=rich**(확장 스키마 + RICH_SYSTEM_PROMPT).
> Author: Claude (Phase 13 Slice S3)
> Related contracts: `docs/contracts/agent_io_contract.md` (P-006 v1.0.0/v1.1.0 gated), `docs/contracts/api_contract.md` (응답 body.plan_candidates rich 슬롯 — flag ON 경로에서만)
> Related CC: CC-012 (rich 스키마 슬롯), CC-013 (rich P-006 v1.1.0 프롬프트)
> Related phase: `phases/active/phase-13-output-enrichment/` (acceptance A4 — gated wiring)
> Skill: contract-change (절차) — agent_io/api 영향은 gated(default OFF)라 OFF 경로 무영향.

---

## 1. 변경 요약

| 대상 | 변경 | 종류 |
|---|---|---|
| `backend/fastapi/config.py` | `rich_output_enabled: bool = False` Field 추가 (env `RICH_OUTPUT_ENABLED`). `multi_provider_plans_enabled` 근처. 기존 Field 무수정. | **additive (gated default-off)** |
| `backend/fastapi/schemas/output.py` | `envelope_to_response_dict(envelope, plans, *, rich_enabled)` module 헬퍼 추가 — OFF 면 `Plan.model_dump_compact()` 로 rich 제외, ON 이면 full. 기존 모델 무수정. | **additive** |
| `backend/fastapi/agents/planning.py` | `run_planning` / `_run_planning_single` / `_run_planning_single_via_gateway` 에 `settings.rich_output_enabled` 분기 추가 (ON=RICH 프롬프트, OFF=기존 compact). 기존 상수/헬퍼 무수정. | **additive (분기만)** |
| `backend/fastapi/routers/generate.py` | Plan/PlanFlowBeat 구성에 rich 키 **additive read**(`plan_raw.get(...)`) + 직렬화 분기(OFF=`JSONResponse(compact)`+deprecation header, ON=`return envelope`). | **additive** |
| `backend/fastapi/orchestration/moa_orchestrator.py` | Plan 구성 2곳(초기 + revise 재구성)에 rich additive read + `plan_entry["envelope"]` 직렬화를 `envelope_to_response_dict(...)` 로 분기. Envelope/Critic/조립 순서 무수정. | **additive** |
| `backend/fastapi/routers/plans.py` | thin adapter `plans_generate` 에 OFF live-POST 직렬화 분기 추가 — OFF 면 stored compact dict 를 `JSONResponse` 로 반환(POST 라우트는 response_model 미지정이라 rich Optional 슬롯이 새는 것을 차단). ON 이면 Envelope 그대로. | **additive** |

## 2. ★ OFF byte-identical 보증 (FORBIDDEN 게이트)

- **핵심**: `rich_output_enabled=False`(default) 면 응답 plan_candidates 에 rich 슬롯(plan 9 + beat 3 = 12)이
  **없다**. S1 의 검증된 `Plan.model_dump_compact()` 가 제외 → Phase 13 이전(7필드+rag_used / beat 4필드)과 동일.
- **두 경로 모두 차단**:
  - `/generate`: `response_model=Envelope` 가 rich Optional 슬롯을 직렬화하므로, OFF 는 `return envelope` 대신
    `envelope_to_response_dict(rich_enabled=False)` → `JSONResponse` (deprecation header 보존, status 200).
  - `/plans/{id}/generate`: POST 라우트는 **response_model 미지정** → `Envelope` 모델을 그대로 반환하면
    jsonable_encoder 가 rich Optional(None/[])까지 직렬화하여 새므로, OFF 는 adapter 가 stored compact dict 를
    `JSONResponse` 로 반환. GET /plans/{id} 도 동일 compact stored dict 를 읽음.
- **증거**: 기존 **486 테스트 0 수정 / 0 fail** (OFF default 라 기존 응답 불변). + 신규 7 테스트가 OFF 응답의
  rich 슬롯 부재(`test_*_off_excludes_rich`) 와 ON 응답의 rich 슬롯 존재(`test_*_on_includes_rich`)를 직접 단정.

## 3. agent_io / api contract 영향 (1줄 요약)

- **OFF(운영 default)**: agent_io / api 응답 **0 변경** (compact = Phase 13 이전). contract 본문 영향 없음.
- **ON(검증 후 전환)**: P-006 출력이 rich 슬롯을 채우고(agent_io — v1.1.0 gated), api 응답 body.plan_candidates 에
  rich 슬롯이 노출된다(CC-012 additive Optional 이라 소비자 회귀 0). flag ON 전환은 S6 depth 재측정 후 별도 결정.

## 4. 코드 영향 (★ behavior-preserving — 분기·additive read 만)

```
config.py            + rich_output_enabled (default False).
schemas/output.py    + envelope_to_response_dict() (model_dump_compact 재사용). 기존 모델 무수정.
agents/planning.py   ± run_planning / _run_planning_single / _run_planning_single_via_gateway 에 rich 프롬프트 분기.
routers/generate.py  ± Plan rich additive read + 직렬화 분기(OFF JSONResponse compact+header / ON envelope).
orchestration/moa_orchestrator.py  ± Plan 2곳 rich additive read(초기+revise 재구성) + plan_entry["envelope"] 직렬화 분기.
routers/plans.py     ± plans_generate OFF live-POST → stored compact JSONResponse (rich 슬롯 누수 차단).
★ 무수정: compact SYSTEM_PROMPT / Plan 7필드 / Critic / Rewriter / Envelope 조립 순서 / validation.checks 순서·warnings.
```

## 5. 회귀 안전 근거

- **gated default-off**: flag OFF 면 신규 분기는 전부 기존 동작과 동일 path 선택 (compact 프롬프트 + compact 직렬화).
- **additive read 안전**: rich 키는 `plan_raw.get(...)` 으로만 읽으며, OFF 프롬프트는 그 키를 생성하지 않아 default(None/[]).
  직렬화 분기가 OFF 면 model_dump_compact() 가 제외 → 빈 rich 값조차 응답에 나타나지 않음.
- **revise 왕복 rich 보존**: orchestrator revise 재구성 Plan 이 `current_plan_dict.get(...) or plan_model.<rich>` 로
  rich 슬롯을 유지 (ON 경로에서 Rewriter 왕복 중 rich 유실 방지). OFF 에선 어차피 제외되므로 무영향.
- **multi_provider**: `_run_planning_single_via_gateway` 도 일관성 위해 rich 분기 추가하되, 이 경로는 별 게이트
  (`multi_provider_plans_enabled`, default OFF)라 통상 미호출 — late `get_settings()` 로 조회.

## 6. 활성화 / Rollback

- **활성화**: env `RICH_OUTPUT_ENABLED=true`. flag ON 전환 결정은 S6 depth 재측정(≥0.8) + 라이브 검증 후.
- **Rollback**: 6개 파일 git revert (+ 신규 test). additive + gated 라 OFF default 면 revert 전후 런타임 동일.

## 7. 변경 이력

- 2026-06-03: Phase 13 S3 — config `rich_output_enabled`(default False) + 직렬화/프롬프트 gated 분기.
  OFF=compact byte-identical(486 green), ON=rich(신규 7 test). 다음: S4 (라이브 ON depth/cost 재측정 + frontend 표시).
