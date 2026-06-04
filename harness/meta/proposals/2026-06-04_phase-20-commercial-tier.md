# Contract Change Proposal: commercial_viral tier — output_schema + prompt_registry (Phase 20 S1/S2)

- 제안일: 2026-06-04
- 제안자: Claude (Phase 20 S1/S2)
- 대상 contract: docs/contracts/output_schema.md (§8.1) + ai_system/prompts/prompt_registry.md (§7 P-006)
- 변경 종류: 신규 (additive, gated)
- 긴급도: 보통
- CC: **CC-026** (output_schema) + **CC-025** (prompt_registry)

## 변경 사유
Phase 20 = output_mode 4번째 tier `commercial_viral`. S1(스키마 코드) + S2(프롬프트 코드)가 추가한
commercial 슬롯을 contract 에 반영. director(CC-017/CC-018) 패턴 그대로 1-tier 위 확장. 전부 additive/gated/
OFF byte-identical.

## 변경 내용

### CC-026 — output_schema.md §8.1 (v1.4.0)
- `output_mode` 4-tier(compact<rich<director<**commercial_viral**).
- `Plan` commercial 슬롯 7종 additive Optional: market_context / audience_psychology / brand_positioning /
  commercial_conversion / platform_packaging / production_feasibility / measurement_plan.
- `scene_breakdown[]`(DirectorScene) 에 commercial 2필드 brand_signal / commercial_signal (→ 7필드 scene).
- 직렬화 `model_dump_for_mode`: compact/rich/director 는 COMMERCIAL_FIELDS 제외 + director scene 상업 2필드
  제외(5필드) → byte-identical; commercial_viral 만 전체. Pydantic = COMMERCIAL_FIELDS(7) + SCENE_COMMERCIAL_FIELDS(2).

### CC-025 — prompt_registry.md §7 P-006 (v1.3.0)
- P-006 v1.3.0 (commercial_viral, gated 공존) — v1.0.0/v1.1.0/v1.2.0/v1.3.0 = output_mode 4-tier 공존.
- COMMERCIAL_SYSTEM_PROMPT(10섹션) + §3.3 제약(보장 금지/기획 경계/추측 표기/일반론 금지).
- 구현: agents/planning.py COMMERCIAL_SYSTEM_PROMPT / _build_commercial_system_prompt_with_hint / COMMERCIAL_PROMPT_VERSION.
- ★ S2 시점 런타임 미연결(behavior-preserving) — wiring 은 S3.

## 영향 받는 영역
- [x] Output Schema (§8.1 Plan commercial 슬롯 + CommercialScene)
- [x] Prompt (P-006 v1.3.0)
- [ ] DB / Agent IO / 프론트 (S5) / 보안 — 무관(S1/S2 시점)
- [x] 평가(후속): golden5/human gate 는 §5.4 paid 활성 전(별도, non-goal)

## 영향 받는 파일
```
docs/contracts/output_schema.md (§8.1 v1.4.0)
ai_system/prompts/prompt_registry.md (§7 P-006 v1.3.0)
구현(기반): backend/fastapi/schemas/output.py(COMMERCIAL_FIELDS/SCENE_COMMERCIAL_FIELDS/Plan/DirectorScene/model_dump_for_mode)
           backend/fastapi/agents/planning.py(COMMERCIAL_SYSTEM_PROMPT/helper/VERSION)
           backend/fastapi/config.py(output_mode Literal 4-tier)
```

## Rollback
output_schema §8.1 v1.4.0 노트 + JSON commercial 슬롯 + prompt_registry P-006 v1.3.0 항목 제거(문서 only).
코드는 Phase 20 커밋 revert. additive — compact/rich/director byte-identical(회귀 0).

## 마이그레이션
- 불필요 (additive Optional, DB 무관, default=compact 불변).

## 승인 기준
director(CC-017/CC-018)와 동형 additive/gated 변형 — Phase 20 빌드 승인("나")에 포함. self-approved 범위
초과(신규 슬롯/프롬프트)이나 코드가 byte-identical 단위 검증(pytest 677 hermetic) 완료된 사후 docs-sync.

## 결정
- [x] 승인 (Phase 20 S1/S2 docs-sync)
- 결정자: 사용자(빌드 승인) / Claude(반영)
- 결정일: 2026-06-04
