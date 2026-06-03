# Phase 15 — Acceptance (A1~A9 + 게이트)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | **output_mode enum 일반화(additive, backward-compat)** — `output_mode: compact\|rich\|director` default compact + 기존 `rich_output_enabled` 동작 보존(매핑) | config diff + 매핑 test (rich_output_enabled=True → rich) | S1 |
| **A2** | **director 스키마 슬롯(additive)** — `Plan` +hook_system/retention_architecture/scene_breakdown(DirectorScene), 전부 Optional + DIRECTOR_FIELDS | output.py diff + output_schema CC + agent-io-check PASS | S1 |
| **A3-PP** | **compact/rich byte-identical(behavior-preserving)** — compact/rich 경로 직렬화 기존과 100% 동일(director 키 제외) | model_dump 모드별 test + pytest 508 회귀 0 | S1·S3 |
| **A4** | **P-006 director 프롬프트 + 버전(gated 공존)** — DIRECTOR_SYSTEM_PROMPT + v1.2.0, compact/rich 보존 | prompt_registry P-006 v1.2.0 + prompt-version-review + CC | S2 |
| **A5** | **gated wiring(output_mode 분기)** — generate/orchestrator/plans 가 compact/rich/director 분기, OFF/rich byte-identical | 3-mode 분기 test + 회귀 | S3 |
| **A6** | **Critic director 차원(gated)** — DIMENSIONS_DIRECTOR(+retention_design) director 모드만, P-007 v1.3.0, 얕은 director 감점 | critic 점수 분포 test + prompt-version-review | S4 |
| **A7** | **frontend director 조건부 렌더** — PlanCard director 섹션(hook_system/retention/scene), rich 회귀 0 | tsc + build + design-review | S5 |
| **A8** | **director depth 측정 + cost** — director 경로 depth(연출/리텐션) 측정 + cost_control director additive | `eval/regression_results/phase-15-*` + cost_control diff | S6 |
| **A9** | **키 0** — director 라이브 데모 키 평문 commit 0 | `git diff \| grep sk-/AIza` 0 | S6 |

## ★ behavior-preserving 게이트 (A3-PP — 핵심)
```
compact (default) / rich (rich_output_enabled=True 또는 output_mode=rich) 경로 = 기존과 byte-identical:
  - output_mode enum 도입은 additive — rich_output_enabled 매핑으로 Phase 13/14 동작 보존
  - DIRECTOR_FIELDS 는 compact/rich 직렬화에서 제외 (model_dump 모드별 exclude)
검증: pytest 508 green (기존 수정 0) + compact/rich 직렬화 회귀 test
```

## ★ output_mode 일반화 게이트 (A1 — flag→enum, 제안서 open issue #2)
```
현 rich_output_enabled: bool → output_mode: Literal[compact|rich|director] = compact
backward-compat: rich_output_enabled=True 이고 output_mode 미지정 → effective "rich" (기존 ON 경로 보존)
                 output_mode 명시 시 우선. 둘 다 OFF/미지정 → compact.
```

## qa-check (release gate)
- 제품 phase — MVP 범위(기획 브리프, product_boundary — scene_breakdown 은 기획 의도/감정/근거) + output_schema/agent_io 정합 + compact/rich byte-identical + director gated OFF default + 키 0.
