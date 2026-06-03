# Phase 15 — Scope (director 모드, gated/additive)

> ★ director = output_mode 3-tier(compact<rich<director) 중간 깊이. rich 슬롯 + 연출/리텐션 슬롯. LLM-only. OFF/compact/rich byte-identical. 제안서 2026-06-03_commercial-viral-mode-design.md 기반.

## 현 자산 (계승)
- `config.rich_output_enabled: bool` (Phase 13 S3) + `Plan`(v1.2.0, rich 12슬롯) + `PLAN_RICH_FIELDS`/`BEAT_RICH_FIELDS` + `Plan.model_dump_compact()` + `envelope_to_response_dict(..., rich_enabled)` + `RICH_SYSTEM_PROMPT`/`RICH_PROMPT_VERSION`(P-006 v1.1.0) + critic `DIMENSIONS_RICH`(9, P-007 v1.2.0 gated).
- Phase 14 위저드 실연결(generate 경로 = output_mode 자동 상속 예정).

## 포함 (In-Scope) — Entry + S1~S6
### Entry (본 문서)
- `phases/active/phase-15-director-mode/` 8 entry + `meta/validations/2026-06-03_phase-15-pre-entry_self.md`(self 14th) + PHASE_REGISTRY/PROJECT_STATE active.

### S1 — output_mode enum + director 스키마 (contract-change + agent-io-check)
- `config.py`: `output_mode: Literal["compact","rich","director"] = "compact"` (additive). ★ backward-compat — `rich_output_enabled=True` → effective "rich" 매핑(기존 동작 보존), output_mode 명시 시 우선.
- `schemas/output.py` `Plan`: director 슬롯 additive — `hook_system: list[str]`, `retention_architecture: str|None`, `scene_breakdown: list[DirectorScene]`. `DirectorScene`(scene_intent/viewer_emotion/retention_device/why_this_works/fallback_scene?). `DIRECTOR_FIELDS` frozenset. `model_dump_compact` → 모드별 제외(compact: rich∪director / rich: director / director: 없음).
- `output_schema.md` §8.1 director 슬롯 등록 (contract-change, additive) + agent-io-check.
- tests: 모드별 직렬화(compact/rich byte-identical + director 포함) + Optional default.

### S2 — P-006 director 프롬프트 (prompt-version-review)
- `agents/planning.py` `DIRECTOR_SYSTEM_PROMPT` + `DIRECTOR_PROMPT_VERSION="v1.2.0"` + `_build_director_system_prompt_with_hint` (rich + director 슬롯 채움, 브리프 경계). 기존 compact/rich 보존.
- `prompt_registry.md` §7 P-006 v1.2.0(director, gated 공존 — v1.0.0 compact/v1.1.0 rich/v1.2.0 director).
- tests + CC 로그.

### S3 — gated wiring (output_mode 분기)
- `generate.py` + `orchestration/moa_orchestrator.py` + `routers/plans.py`: `rich_enabled` boolean 분기 → `output_mode` 분기로 일반화. compact/rich byte-identical(기존), director → director prompt+schema. planning 프롬프트 선택(compact/rich/director).
- tests: 3-mode 분기 + OFF/rich byte-identical 회귀.

### S4 — Critic director 차원 (prompt-version-review)
- `agents/critic.py`: `DIMENSIONS_DIRECTOR = DIMENSIONS_RICH + ["retention_design"]` (director 모드 gated). P-007 v1.3.0. `run_critic` output_mode 분기(compact 8 / rich 9 / director 10).
- tests: director 차원 + 얕은 director 감점.

### S5 — frontend PlanCard director 조건부
- `apps/web/components/PlanCard.tsx` + `lib/types.ts`: director 슬롯 조건부 섹션(hook_system / retention_architecture / scene_breakdown). rich 위 additive — 값 있을 때만.
- design-review(모바일/카드/제작UI 미포함).

### S6 — cost + 검증 + 종료
- `cost_control_policy.md` director cost(rich↔commercial_viral 중간) additive(contract-change).
- director depth 측정(`eval/regression_results/phase-15-*`) + flag director 라이브 데모(실 LLM) + phase-complete.

## contract-change 대상
- `output_schema.md`(director 슬롯 — S1) + `prompt_registry.md`(P-006 v1.2.0 — S2 / P-007 v1.3.0 — S4) + `cost_control_policy.md`(director cost — S6). ★ 전부 additive/gated.

## ★ 변경 허용 / 금지
```
editable:
  Entry: phases/active/phase-15-director-mode/** + validation self + REGISTRY + STATE
  S1: config.py + schemas/output.py(director additive) + output_schema.md(CC) + tests
  S2: agents/planning.py(director prompt) + prompt_registry.md P-006 v1.2.0 + tests
  S3: generate.py + moa_orchestrator.py + routers/plans.py(output_mode 분기) + tests
  S4: agents/critic.py(director 차원) + prompt_registry.md P-007 v1.3.0 + tests
  S5: apps/web/components/PlanCard.tsx + lib/types.ts (director 조건부)
  S6: cost_control_policy.md + eval/regression_results/phase-15-* + retrospective + close
forbidden:
  ★ compact/rich 경로 동작 변경 (byte-identical 유지 — 기존 rich_output_enabled 보존)
  ★ commercial_viral 슬롯(market/audience/brand/conversion/platform/measurement) — PKM/RAG 후 (non-goal)
  ★ PKM/RAG 데이터레이어 (로드맵 ③)
  ★ default ON 전환 / 완성 대본·영상 제작 (product_boundary)
  ★ 실 키 평문 commit
```
