# Contract Change Log — Phase 13 Slice S4 Critic depth 차원 gated additive (P-007 v1.1.0 → v1.2.0, gated)

> ID: CC-015
> Status: **decided + applied** (2026-06-03, Phase 13 Slice S4)
> Date: 2026-06-03
> Decision: Critic(P-007)에 9번째 평가 차원 `depth_actionability`(0~5)를 **gated additive**로 추가한다.
>           `rich_output_enabled`(default **False**) ON 경로에서만 9차원(RICH_SYSTEM_PROMPT + DIMENSIONS_RICH,
>           **v1.2.0**)으로 평가해 얕은 plan(rich 슬롯 빈약)이 8차원 평균만으로 승인되던 "88점 함정"을 해소한다.
>           OFF(default)=기존 8차원(SYSTEM_PROMPT / DIMENSIONS / **v1.1.0**) **byte-identical**.
> Author: Claude (Phase 13 Slice S4)
> Related contracts: `docs/contracts/agent_io_contract.md` §5 (Critic — OFF 서술 불변 / ON gated 정합),
>                    `docs/contracts/output_schema.md` §9 `CriticEvaluation` (dimensions 자유 dict — 9키 additive)
> Related CC: CC-011 (depth_actionability rubric, eval), CC-012 (rich 스키마 슬롯), CC-013 (rich P-006 프롬프트),
>             CC-014 (rich gated wiring)
> Related phase: `phases/active/phase-13-output-enrichment/` (S4 — Critic depth 반영)
> Skill: prompt-version-review (P-007 semver + gated 활성) + contract-change (절차) + agent-io-check (PASS, 발견 0)

---

## 1. 변경 요약

| 대상 | 변경 | 종류 |
|---|---|---|
| `backend/fastapi/agents/critic.py` | `RICH_SYSTEM_PROMPT`(9차원, depth_actionability rubric anchors) + `DIMENSIONS_RICH = DIMENSIONS + ("depth_actionability",)` + `RICH_PROMPT_VERSION="v1.2.0"` 추가. `run_critic` 에 `settings.rich_output_enabled` 분기(ON=9차원 prompt/검증/평균, OFF=기존 8차원). `_derive_verdict` 에 `dimensions=DIMENSIONS`(기본값) 인자 추가. 기존 `SYSTEM_PROMPT`/`DIMENSIONS`/`PROMPT_VERSION`/`normalize_to_canonical` 본문 **무수정**. | **additive (gated 분기만)** |
| `backend/fastapi/schemas/output.py` | `CriticEvaluation.dimensions` 필드 description 에 Phase 13 S4 9번째 키 additive 명시(자유 dict — 스키마 위반 아님). 모델 구조 **무수정**. | **doc-only (additive 설명)** |
| `ai_system/prompts/prompt_registry.md` §8 P-007 | **v1.2.0 (gated, rich 9차원) 항목 추가** — Semver 블록 + Version 헤더. v1.1.0(active/OFF) 블록 보존. deprecate 아님(gated 공존). | **additive (minor bump, gated)** |

## 2. semver 판정 (prompt-version-review §2)

- **minor (v1.1.0 → v1.2.0, gated)** — 새 평가 차원(`depth_actionability`) + 신규 채점 지시(rubric anchors) 추가.
  output_schema `CriticEvaluation` 구조 호환(`dimensions` 자유 dict → 9번째 키 additive). major 아님. 모델 교체 없음(gpt-4o 동일).
- ★ gated 공존 — v1.1.0(active/OFF) 과 v1.2.0(gated/ON) 이 `rich_output_enabled` flag 로 공존. 표준 deactivate 미적용.

## 3. agent_io / output_schema contract 영향 (1줄 요약)

- **OFF(운영 default)**: Critic 8차원 0~5 → canonical 8키. agent_io §5 / output_schema §9 **0 변경** (Phase 13 이전과 동일).
- **ON(검증 후 전환)**: Critic 이 `depth_actionability` 를 추가 평가 → canonical `dimensions` 가 **9키**(additive Optional 자유 dict,
  스키마 위반 0). `overall_score`(0~1)는 9차원 평균/5.0 으로 산출 → 얕은 plan 의 종합 점수 하락(88점 함정 해소). agent-io-check **PASS(발견 0)**.

## 4. 코드 영향 (★ behavior-preserving — 분기·additive 만)

```
agents/critic.py    ± run_critic: rich_output_enabled 분기(ON=RICH_SYSTEM_PROMPT/DIMENSIONS_RICH/user="9차원"/_derive_verdict(dimensions=9),
                                  OFF=기존 SYSTEM_PROMPT/DIMENSIONS/"8차원"/_derive_verdict 기본). 검증·키보강·평균을 `_expected` 기준으로.
                    + RICH_SYSTEM_PROMPT / DIMENSIONS_RICH / RICH_PROMPT_VERSION="v1.2.0".
                    + _derive_verdict(scores, *, dimensions=DIMENSIONS) — 기본값 8차원 → OFF 호출 byte-identical.
schemas/output.py   ± CriticEvaluation.dimensions description 에 9번째 키 additive 명시 (모델 구조 무수정).
prompt_registry.md  + §8 P-007 v1.2.0 gated 블록 (Semver + Version 헤더). v1.1.0 active 보존.
★ 무수정: SYSTEM_PROMPT(8차원) / DIMENSIONS / PROMPT_VERSION(v1.1.0) / normalize_to_canonical 본문 / select_best_plan_index /
          planning / orchestrator / generate / routers / frontend(apps/web).
```

## 5. 회귀 안전 근거 (behavior-preserving)

- **gated default-off ★**: flag OFF(default)=8차원 경로. `run_critic` 의 OFF 분기 변수(_system_prompt/_expected/_user_intro)가
  전부 기존 상수·리터럴과 동일 → prompt·user message·검증 차원·평균·verdict 가 **byte-identical**.
- **`_derive_verdict` 기본값 ★**: 새 `dimensions` 인자의 default 가 기존 `DIMENSIONS`(8차원) → 기존 호출부(인자 생략) 동작 불변.
  ON 경로만 `dimensions=DIMENSIONS_RICH`(9차원)를 명시 → depth 가 평균·미달 카운트에 반영.
- **normalize_to_canonical 제네릭 ★**: helper 가 `scores.items()` 를 순회 → 9키도 추가 코드 없이 0–1 정규화. 본문 무수정.
- **schema 자유 dict ★**: `CriticEvaluation.dimensions: dict[str, float]` 가 고정 키가 아니라 9번째 키가 additive(extra='ignore' 와 무관, 정식 슬롯).
- **PROMPT_VERSION 불변 ★**: 모듈 상수 `PROMPT_VERSION="v1.1.0"` 유지 → test_prompt_registry_consistency / validation.checks detail 불변.
  rich 버전은 별도 `RICH_PROMPT_VERSION="v1.2.0"` 상수로 노출(OFF 경로 미사용).
- **증거**: 기존 **493 테스트 0 수정 / 0 fail**(OFF byte-identical) + 신규 **6 테스트**(ON 9차원 + 88점 함정 해소 단언) → **499 green**.

## 6. 88점 함정 해소 (S4 핵심 가치)

- Phase 12 실증: 얕은 compact plan(depth 0.231)이 8차원 평균만으로 **88점/승인** — Critic 이 깊이를 안 봤다.
- S4 ON: 동일 8차원 고득점(avg 4.375 ≈ 0.875)이라도 `depth_actionability` 가 낮으면(얕은 plan, 예 1) 9차원 평균이 하락(4.0)
  → 종합 점수 0.875 → 0.80. 깊이 페널티가 명시적으로 반영된다 (`test_critic_88_trap_resolved_shallow_plan_scores_lower`).
- ★ 제품 경계: 깊이 = "기획 브리프"의 구체성(촬영·편집 바로 착수 가능)이지 완성 대본 작성 여부가 아니다 (product_boundary).
- rubric 정합: `eval/video_planning_eval.md` §2.A.1 depth_actionability (CC-011, anchors 0.2/0.6/1.0).

## 7. 활성화 / Rollback

- **활성화**: env `RICH_OUTPUT_ENABLED=true` (S3 CC-014 와 동일 flag — rich 출력과 depth 평가가 한 flag 로 묶임).
  flag ON 전환 결정은 S6 depth 재측정(≥0.8) + 라이브 검증 후.
- **이전 버전**: v1.1.0 deactivate_at 미설정 (gated 공존 — 차단 안 함).
- **Rollback**: critic.py(rich 상수/분기) + output.py(description) + prompt_registry(v1.2.0 블록) + test_critic(신규 6) git revert.
  additive + gated 라 OFF default 면 revert 전후 런타임 동일.

## 8. 변경 이력

- 2026-06-03: Phase 13 S4 — Critic depth_actionability gated 9차원(P-007 v1.1.0 active / v1.2.0 gated). OFF=8차원 byte-identical(493 green),
  ON=9차원 + 88점 함정 해소(신규 6 test). agent-io-check PASS(발견 0). 다음: S5 (frontend — PlanCard rich conditional 렌더).
