# Contract Change Log — CC-025 / CC-026: commercial_viral tier (Phase 20 S1/S2)

- 반영일: 2026-06-04
- 제안서: `meta/proposals/2026-06-04_phase-20-commercial-tier.md`
- 상태: approved → 반영 완료

## CC-026 — output_schema.md §8.1 (v1.4.0)
- `output_mode` 4-tier(compact<rich<director<commercial_viral) + Plan commercial 7슬롯(market_context/
  audience_psychology/brand_positioning/commercial_conversion/platform_packaging/production_feasibility/
  measurement_plan) + scene 2필드(brand_signal/commercial_signal) additive Optional.
- 직렬화 byte-identical: compact/rich/director 는 COMMERCIAL 제외(누수 0), director scene 5필드 유지.

## CC-025 — prompt_registry.md §7 P-006 (v1.3.0)
- P-006 v1.3.0 commercial_viral 변형(gated 공존, 4-tier) + System(10섹션) + §3.3 제약(보장금지/기획경계/
  추측표기/일반론금지) + Semver 항목 + 구현 포인터(COMMERCIAL_SYSTEM_PROMPT/helper/VERSION).

## 정합 확인 (docs↔code)
| 코드 | contract |
|---|---|
| schemas/output.py COMMERCIAL_FIELDS(7)+SCENE_COMMERCIAL_FIELDS(2)+model_dump_for_mode 4-tier | output_schema §8.1 v1.4.0 ✅ |
| config.py output_mode Literal +commercial_viral | output_schema §8.1 / prompt_registry ✅ |
| agents/planning.py COMMERCIAL_SYSTEM_PROMPT/helper/COMMERCIAL_PROMPT_VERSION=v1.3.0 | prompt_registry P-006 v1.3.0 ✅ |

## Rollback
문서 항목 제거(additive). 코드 revert. compact/rich/director byte-identical(회귀 0).

## CC-027 — prompt_registry.md §8 P-007 (v1.4.0, Phase 20 S4)
- P-007 v1.4.0 commercial_viral 17차원 — director 10차원 + 상업 7(viral_potential/brand_memory/
  commercial_conversion/non_genericity/execution_feasibility/platform_fit/shareability). retention_design 은
  director(v1.3.0)에 이미 있어 중복 제외(10+7=17). gated 공존, compact/rich/director(8/9/10) byte-identical.
- 구현: critic.py DIMENSIONS_COMMERCIAL(17) + COMMERCIAL_SYSTEM_PROMPT(director 프롬프트 프로그램적 +7) +
  COMMERCIAL_PROMPT_VERSION=v1.4.0 + run_critic mode 분기 + max_tokens 2800(commercial만).
- 정합: test_critic_commercial + test_prompt_registry_consistency green.

## 비고
- cost_control §15 commercial cost = S6.
