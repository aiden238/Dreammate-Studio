# Contract Change Log — Phase 15 Slice 2 P-006 director 프롬프트 (v1.1.0 → v1.2.0, gated)

> ID: CC-018
> Status: **decided + applied** (2026-06-03, Phase 15 Slice 2)
> Date: 2026-06-03
> Decision: planning P-006 에 director SYSTEM_PROMPT(v1.2.0) 추가 — rich + 연출/리텐션 슬롯(S1 director). ★ minor bump (additive 슬롯 + 신규 규칙, envelope 구조 동일). compact(v1.0.0)/rich(v1.1.0) 보존, `output_mode` 로 공존.
> Author: Claude (Phase 15 Slice 2)
> Related contracts: `ai_system/prompts/prompt_registry.md` §7 P-006 (+v1.2.0 director)
> Related CC: CC-017(director 스키마, 본 프롬프트가 채우는 대상), CC-013(rich P-006 v1.1.0 — 동형 패턴)
> Skill: prompt-version-review + contract-change

---

## 1. 변경 요약
| 대상 | 변경 | 종류 |
|---|---|---|
| `prompt_registry.md` §7 P-006 | v1.2.0 director 블록(Version/Output schema/Semver gated) 추가. v1.0.0/v1.1.0 보존. | additive (minor bump) |
| `agents/planning.py` | `DIRECTOR_SYSTEM_PROMPT` + `_build_director_system_prompt_with_hint()` + `DIRECTOR_PROMPT_VERSION="v1.2.0"`. 기존 compact/rich 상수·헬퍼·버전 무변경. | additive |

## 2. semver 판정
- **minor (v1.1.0 → v1.2.0)** — rich + director 슬롯(연출/리텐션) 채우는 신규 프롬프트 변형. output envelope 구조(`{"plan":{...}}`) 동일. 모델 동일(gpt-4o-mini). major 아님(스키마 additive Optional, CC-017).

## 3. 코드 영향 (★ behavior-preserving — 런타임 미연결)
```
agents/planning.py: + DIRECTOR_SYSTEM_PROMPT(rich 12 + director 3슬롯 지시 + 브리프 경계 + 보장 금지)
                    + _build_director_system_prompt_with_hint (output_mode=director 경로용, S3 호출)
                    + DIRECTOR_PROMPT_VERSION
  ★ 기존 SYSTEM_PROMPT/RICH_SYSTEM_PROMPT/PROMPT_VERSION/RICH_PROMPT_VERSION 무변경.
  ★ director 상수/헬퍼는 S2 시점 호출처 0 (run_planning* 모두 compact/rich 경로) → 런타임 출력 불변.
orchestration/routers/agents(critic 등) 무변경 (director 프롬프트 선택 = S3 gated wiring).
```

## 4. 회귀 안전 근거
- **gated 공존**: v1.0.0/v1.1.0/v1.2.0 이 `output_mode` 로 공존. compact(default)=v1.0.0 byte-identical. deactivate 미적용.
- **런타임 미연결**: director 상수/헬퍼/버전 신설, 호출처 0(S3 wiring 전) → 모든 생성 경로 여전히 compact/rich → 출력·토큰·latency 불변.
- **mock 회귀 불변**: eval-run mock 러너는 프롬프트 미호출 → P-006 변경 무관.
- director rich 출력 depth(연출/리텐션) 실측은 S3 wiring 후 S6(실 LLM).

## 5. golden_set 회귀 (S2 시점)
```
schema 준수율 100% (director 출력도 output_schema §8.1 v1.3.0 additive Optional 에 valid).
런타임 영향 0 — director 프롬프트 미연결 → compact/rich 경로만 → 신구 출력 차이 측정 불가(=불변).
pytest: 522 → 522 + 신규(director prompt) green.
정량 대조(depth/토큰)는 S3 wiring 후 S6.
```

## 6. Rollback
- `prompt_registry.md` §7 v1.2.0 director 블록 + Semver 단락 revert.
- `planning.py` DIRECTOR_SYSTEM_PROMPT / _build_director_system_prompt_with_hint / DIRECTOR_PROMPT_VERSION 제거.
- additive + 미연결 → rollback 시 런타임 영향 0.

## 7. 변경 이력
- 2026-06-03: Phase 15 S2 — P-006 v1.1.0 → v1.2.0 (director, minor, gated). 다음 = S3 (config output_mode 분기 wiring).
