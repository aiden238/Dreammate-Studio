# Contract Change Log — Phase 15 Slice 1 output_mode 3-tier + director 스키마 (additive)

> ID: CC-017
> Status: **decided + applied** (2026-06-03, Phase 15 Slice 1)
> Date: 2026-06-03
> Decision: `output_mode` 를 compact/rich/**director** 3-tier 로 일반화 + `Plan` director 슬롯 3종 additive. ★ compact/rich 경로 byte-identical (model_dump_for_mode 모드별 제외).
> Author: Claude (Phase 15 Slice 1)
> Related contracts: `docs/contracts/output_schema.md` (§8.1 v1.2.0 → **v1.3.0**) — agent_io_contract §4.3 "§8 P-006 body" 참조(본문 무변경, agent-io-check 정합)
> Related plan: `meta/proposals/2026-06-03_phase-15-director-mode-plan.md` (§2 enum / §3 director 스키마) + 제안서 2026-06-03_commercial-viral-mode-design.md §2.1
> Related CC: CC-012(rich 12슬롯), CC-014(rich gated wiring) — director 가 동형 계승
> Skill: contract-change + agent-io-check

---

## 1. 변경 요약
| 대상 | 변경 | 종류 |
|---|---|---|
| `output_schema.md` §8.1 | output_mode 3-tier 노트 + `Plan` director 슬롯(hook_system / retention_architecture / scene_breakdown[DirectorScene 5필드]) 등록. v1.2.0→**v1.3.0**. | **additive** (전부 Optional) |
| `schemas/output.py` | `DirectorScene` 모델 + `Plan` director 3슬롯 + `DIRECTOR_FIELDS` + `model_dump_for_mode(output_mode)`(model_dump_compact 일반화) + `envelope_to_response_dict` output_mode 분기 | **additive** |
| `config.py` | `output_mode: Literal[compact\|rich\|director]=compact` + `effective_output_mode()` 헬퍼 (rich_output_enabled backward-compat 매핑) | **additive** |
| `agent_io_contract.md` | **무변경** (§4.3 = output_schema §8 참조) | — |

## 2. 코드 영향 (additive — compact/rich byte-identical)
```
schemas/output.py:
  + DirectorScene(scene_intent/viewer_emotion/retention_device/why_this_works/fallback_scene)
  + Plan.hook_system / retention_architecture / scene_breakdown (전부 Optional default)
  + DIRECTOR_FIELDS frozenset
  + Plan.model_dump_for_mode(output_mode): compact(rich∪director 제외) / rich(director 제외) / director(전부)
  + Plan.model_dump_compact() = model_dump_for_mode("compact") 별칭 (Phase 13 호환, ★ 이제 director 도 제외)
  + envelope_to_response_dict(output_mode|rich_enabled): rich 경로도 model_dump_for_mode 로 director 제외(누수 0)
config.py: + output_mode Field + effective_output_mode()
★ rich_output_enabled 보존(삭제 X). 호출부(generate/orchestrator/planning/critic)는 S3 에서 output_mode 분기로 일반화.
```

## 3. 회귀 안전 근거 (behavior-preserving)
- **compact byte-identical**: director 필드 추가로 기존 model_dump_compact 가 director 키를 누수할 뻔했으나, model_dump_for_mode("compact")가 PLAN_RICH_FIELDS ∪ DIRECTOR_FIELDS 제외 → Phase 12 이전 7필드 출력 동일.
- **rich byte-identical**: ★ envelope_to_response_dict 의 rich 경로도 plan_candidates 를 model_dump_for_mode("rich")(director 제외)로 명시 직렬화 → Phase 13 rich(director 키 없음)와 동일. (이전엔 full dump → director 키 누수했을 것.)
- **backward-compat**: rich_output_enabled=True(output_mode 미지정) → effective "rich" → Phase 13/14 동작 보존. 호출부 미변경(S3).
- **소비자 무영향**: Critic/Rewriter/orchestrator/PlanCard 는 director 키 미참조(additive). director 채움은 S2(프롬프트)+S3(wiring).

## 4. 검증 결과
```
신규 test (test_director_schema.py, 14): DirectorScene default + model_dump_for_mode(compact/rich/director) +
  model_dump_compact 별칭 + effective_output_mode 매핑(5) + envelope_to_response_dict(backward-compat+director) + DIRECTOR_FIELDS drift.
의도 delta: test_output_rich_schema.test_rich_field_constants_match_model — rich = 전체-legacy-director (director 추가 반영).
pytest: 508 → 522 (508 + 신규 14, 기존 508 중 1 메타테스트 의도 갱신 / 런타임 회귀 0).
agent-io-check: PASS (발견 0) — Planner P-006 ↔ §8.1 v1.3.0 정합, director=missing-by-design(프롬프트 S2/gated), 소비자 회귀 0.
운영 .py: schemas/output.py + config.py (additive). 호출부/agents/apps 무변경. 키 0.
```

## 5. Rollback
- `output_schema.md` §8.1 v1.3.0 블록 + director JSON git revert → v1.2.0.
- `schemas/output.py` DirectorScene/director 슬롯/DIRECTOR_FIELDS/model_dump_for_mode 제거 (model_dump_compact 는 PLAN_RICH_FIELDS+BEAT 제외 원복).
- `config.py` output_mode/effective_output_mode 제거.
- additive — rollback 시 compact/rich 무영향. DB 마이그레이션 불필요(raw_llm_json jsonb 자동 수용).

## 6. 변경 이력
- 2026-06-03: Phase 15 S1 — output_mode 3-tier(director) + director 스키마 additive(CC-017). 다음 = S2(P-006 director 프롬프트 v1.2.0).
