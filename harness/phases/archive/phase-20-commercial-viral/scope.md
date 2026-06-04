# Phase 20 — Scope

## 포함 (build)
- **S1 schema**: `output_mode` Literal 에 `commercial_viral` 추가 + `COMMERCIAL_FIELDS` frozenset(10슬롯) + `CommercialScene`(7필드) + `scene_breakdown` 등 Plan additive Optional 슬롯 + `model_dump_for_mode()` 확장(compact/rich/director 에서 COMMERCIAL 제외 → byte-identical). [단위 test]
- **S2 prompt**: `agents/planning.py` `COMMERCIAL_SYSTEM_PROMPT` + `COMMERCIAL_PROMPT_VERSION`(P-006 v1.3.0, gated 공존) — 10섹션 + §3.3 제약(기획경계/일반론금지/보장표현금지/추측표기). prompt-version-review.
- **S3 wiring**: `effective_output_mode`=commercial_viral 경로에서 planning 이 commercial 프롬프트 사용 + Plan 직렬화 commercial 슬롯 채움. gated(OFF=director 이하 byte-identical).
- **S4 critic**: `DIMENSIONS_COMMERCIAL`(17차원 = DIMENSIONS_RICH 9 + 상업 8) gated, P-007 v1.3.0. OFF=8/9차원 불변.
- **S5 frontend**: commercial_viral 출력(10슬롯 + scene 7필드) 렌더(기존 rich/director 카드 확장, additive).
- **S6**: 라이브 검증(commercial_viral API end-to-end) + cost_control §15 + phase-complete.

## 예상 파일 변경
```
editable:
  backend/fastapi/config.py (output_mode Literal + effective_output_mode 자연 확장)
  backend/fastapi/schemas/output.py (COMMERCIAL_FIELDS + CommercialScene + Plan 슬롯 + model_dump_for_mode)
  backend/fastapi/agents/planning.py (COMMERCIAL_SYSTEM_PROMPT/VERSION + mode 분기)
  backend/fastapi/agents/critic.py (DIMENSIONS_COMMERCIAL gated)
  backend/fastapi/orchestration/moa_orchestrator.py (commercial mode wiring)
  apps/web/* (commercial 출력 렌더 — S5)
  tests/* + phases/active/phase-20-* + meta/* + PROJECT_STATE/REGISTRY
read-only(→contract-change):
  docs/contracts/output_schema.md (Plan commercial 슬롯 + CommercialScene)
  ai_system/prompts/prompt_registry.md (P-006 v1.3.0 / P-007 v1.3.0)
  docs/contracts/cost_control_policy.md (§15 commercial cost)
forbidden:
  product_boundary 침범(영상 제작) / 새 MOA agent / commercial_viral default ON / archive
```

## 검증
- 각 슬라이스 behavior-preserving: 기존 pytest 668 green + scenario_sim 36/36 + audit 0.
- S1: model_dump_for_mode 4-tier 단위 test + compact/rich/director byte-identical(기존 키 불변).
- S6: 라이브 commercial_viral 생성(슬롯 채움 + 보장표현 0 + 추측표기) + OFF byte-identical 재확인.
