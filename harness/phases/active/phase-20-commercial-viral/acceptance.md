# Phase 20 — Acceptance

```
A1. S1 schema — output_mode Literal 4-tier(+commercial_viral) + COMMERCIAL_FIELDS(10) + CommercialScene(7)
    + Plan additive Optional 슬롯 + model_dump_for_mode 확장. ★ compact/rich/director 직렬화 키 불변
    (COMMERCIAL 제외) = byte-identical. [단위 test: 4-tier dump + 기존 668 green]
A2. S2 prompt — COMMERCIAL_SYSTEM_PROMPT(10섹션) + COMMERCIAL_PROMPT_VERSION(P-006 v1.3.0, gated 공존).
    §3.3 제약 포함(기획경계/일반론금지/★보장표현금지/★추측표기). [prompt-version-review + 단위]
A3. S3 wiring — effective_output_mode=commercial_viral → planning commercial 프롬프트 + Plan commercial 슬롯
    채움. gated: OFF(director 이하)=byte-identical. [단위 + 기존 green]
A4. S4 critic — DIMENSIONS_COMMERCIAL(17차원) gated, P-007 v1.3.0. OFF=8/9차원 불변. [단위]
A5. S5 frontend — commercial_viral 출력(10슬롯 + scene 7필드) 렌더(additive, rich/director 카드 무변경). [typecheck/lint]
A6. behavior-preserving — 전 슬라이스 기존 pytest 668 green + scenario_sim 36/36 + audit 0 + 키 0.
A7. ★ 라이브 검증 — commercial_viral 실 생성: 10슬롯 채움 + scene 7필드 + 보장표현 0 + 추측표기 +
    OFF byte-identical 재확인. [real LLM, opt-in]
A8. contract-change — output_schema(commercial 슬롯+CommercialScene) + prompt_registry(P-006/P-007 v1.3.0)
    + cost_control(§15) docs-sync(CC). 
A9. phase-complete — gates + 회고 + archive + REGISTRY/STATE.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A3/A4 | 단위 test(model_dump_for_mode 4-tier + commercial mode wiring + 17차원 gated) |
| A2 | 프롬프트 상수 + 버전 + 제약 문구 존재 단위 검사 |
| A6 | pytest 668 baseline + scenario_sim 36 + audit 0 |
| A7 | 라이브 commercial_viral 생성(슬롯/보장표현/추측표기) |
