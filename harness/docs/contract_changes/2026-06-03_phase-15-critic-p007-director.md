# Contract Change Log — Phase 15 Slice 4 Critic director 차원 retention_design (P-007 v1.2.0 → v1.3.0, gated)

> ID: CC-019
> Status: **decided + applied** (2026-06-03, Phase 15 Slice 4)
> Date: 2026-06-03
> Decision: Critic 에 director 10번째 차원 `retention_design` 추가 (rich 9차원 + retention). ★ minor bump, gated — `output_mode=director` 경로 전용. compact(8)/rich(9) byte-identical.
> Author: Claude (Phase 15 Slice 4)
> Related contracts: `ai_system/prompts/prompt_registry.md` §8 P-007 (+v1.3.0 director) — `docs/contracts/output_schema.md` §9 CriticEvaluation.dimensions(자유 dict, additive)
> Related CC: CC-015(rich depth_actionability 9차원 — 동형 패턴), CC-017(director 스키마)
> Skill: prompt-version-review + contract-change + agent-io-check

---

## 1. 변경 요약
| 대상 | 변경 | 종류 |
|---|---|---|
| `agents/critic.py` | `DIMENSIONS_DIRECTOR`(=DIMENSIONS_RICH + retention_design, 10) + `DIRECTOR_SYSTEM_PROMPT`(RICH 프롬프트 프로그램적 확장) + `DIRECTOR_PROMPT_VERSION="v1.3.0"` + run_critic output_mode 분기(8/9/10) | additive (gated) |
| `prompt_registry.md` §8 P-007 | v1.3.0 director(10차원) 블록 추가. v1.1.0(8)/v1.2.0(9) 보존. | additive (minor) |

## 2. semver 판정
- **minor (v1.2.0 → v1.3.0)** — additive 차원(retention_design) + 신규 채점 지시. verdict 식 구조 동일(N-dim avg). output_schema 미변경(CriticEvaluation.dimensions 자유 dict → 10번째 키 additive).

## 3. 코드 영향 (gated — compact/rich byte-identical)
```
agents/critic.py:
  + DIMENSIONS_DIRECTOR = DIMENSIONS_RICH + ("retention_design",)   # 10차원
  + DIRECTOR_SYSTEM_PROMPT = RICH_SYSTEM_PROMPT 프로그램적 확장(retention_design 10번째 + 10차원/10개키 표기)
  + DIRECTOR_PROMPT_VERSION = "v1.3.0"
  run_critic: output_mode 분기 — director→(DIRECTOR_SYSTEM_PROMPT, DIMENSIONS_DIRECTOR, 10차원)
              / rich→(RICH, DIMENSIONS_RICH, 9) / compact→(SYSTEM_PROMPT, DIMENSIONS, 8)
  ★ compact/rich 경로 분기·상수·프롬프트 불변 → byte-identical (effective_output_mode 매핑).
```

## 4. 회귀 안전 근거
- **gated**: director 차원/프롬프트는 `output_mode=director` 경로 전용. compact(8)/rich(9) 불변(effective_output_mode 가 rich_output_enabled=True→rich 매핑 — Phase 13 동작 보존).
- **canonical 0–1(ADR-018) 불변**: normalize_to_canonical/verdict 식 구조 동일, 차원 집합만 교체.
- **dimensions 자유 dict**: 10번째 키 additive(스키마 위반 아님). OFF/rich 경로는 8/9 키.
- **"88점 함정" 확장 방어**: 얕은 director(hook_system/retention/scene 빈약)는 retention_design 저점 → 평균 하락.

## 5. golden_set 회귀
```
pytest: 531 → 531 + 신규(critic director). compact/rich critic 회귀 0(byte-identical).
director retention_design 의 실 LLM 채점·anchor 검증은 S6(실 LLM) — mock 은 구조(10차원 파싱) 검증.
agent-io-check: PASS — Critic(P-007) dimensions additive(10), 소비자(select_best_plan_index/normalize) 회귀 0.
```

## 6. Rollback
- `prompt_registry.md` §8 v1.3.0 블록 revert. `critic.py` DIMENSIONS_DIRECTOR/DIRECTOR_SYSTEM_PROMPT/DIRECTOR_PROMPT_VERSION + run_critic director 분기 제거(rich/compact 2-way 복귀).
- gated → rollback 시 compact/rich 무영향.

## 7. 변경 이력
- 2026-06-03: Phase 15 S4 — P-007 v1.2.0 → v1.3.0 (director 10차원 retention_design, minor, gated). 다음 = S5(frontend PlanCard director).
