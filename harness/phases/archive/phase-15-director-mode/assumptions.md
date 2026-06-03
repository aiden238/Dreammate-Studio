# Phase 15 — 진입 4점검 (Assumptions / Simplest Slice / Surgical Scope / Verification)

## 1. Assumptions
### 1.1 확정 가정
- director = rich↔commercial_viral 중간 tier(제안서 §2.1) — 데이터레이어 **비의존**(LLM-only) → 지금 빌드 가능.
- director 슬롯 경계(제안서 open issue #1 확정): **hook_system + retention_architecture + scene_breakdown(director-subset: scene_intent/viewer_emotion/retention_device/why_this_works/fallback_scene)**. 상업필드(brand_signal/commercial_signal/market/audience/brand/conversion/platform/measurement) = commercial_viral(NG1).
- output_mode enum 일반화(open issue #2): `rich_output_enabled` 흡수/매핑(backward-compat) — Phase 13/14 동작 보존.
- gated/additive → compact/rich OFF 경로 byte-identical(Phase 13 P-GATED-OUTPUT-CHANGE-001 계승).
- audit_naming: S1 output_schema 변경 시 `scripts/audit_naming.ps1` 실행 후 기록(현 entry=계획).

### 1.2 불확실 항목 (phase-complete 시 검증)
- U-1: director depth(연출/리텐션) 를 mock-deterministic eval 이 의미있게 채점 불가 → 실 LLM/human(로드맵 ②). 본 phase 는 구조 측정 + 라이브 데모.
- U-2: scene_breakdown N씬 상한(토큰 vs 깊이) — 데모 후 실측(제안서 open issue #3 일부).
- U-3: output_mode enum ↔ 기존 rich_output_enabled 공존 매핑의 모든 경로(generate/plans/orchestrator) 회귀 0 — S3 test 로 확인.

## 2. Simplest Slice (3회 압축)
- 1차: "output_mode 3-tier 전부(enum+스키마+프롬프트+wiring+critic+frontend+cost)"
- 2차: "director 스키마 슬롯 + model_dump 모드별 제외(compact/rich byte-identical 입증) — 백엔드 직렬화만"
- 3차: "**output_mode enum + DIRECTOR_FIELDS + model_dump_compact 모드별 제외 + test** (compact/rich byte-identical, director 포함) — 프롬프트/생성 없이 직렬화 계약만"
→ ★ Simplest Slice = **S1**(enum + director 슬롯 + 모드별 직렬화 + byte-identical test). 프롬프트(S2)·wiring(S3)·critic(S4)는 그 위에 점증.

## 3. Surgical Scope
| 분류 | 파일 |
|---|---|
| editable | S1 config.py/schemas/output.py + output_schema.md(CC) / S2 agents/planning.py + prompt_registry.md(P-006) / S3 generate.py·moa_orchestrator.py·routers/plans.py / S4 agents/critic.py + prompt_registry.md(P-007) / S5 PlanCard.tsx·lib/types.ts / S6 cost_control_policy.md·eval·retrospective |
| read-only (contract-change) | output_schema.md · prompt_registry.md · cost_control_policy.md · agent_io_contract.md |
| forbidden | ★ compact/rich 경로 동작 변경(byte-identical) · commercial_viral 슬롯(NG1) · PKM/RAG(NG2) · phases/archive/** |

★ 모든 sub-agent prompt 에 P-X1 §SELF-VERIFICATION(git diff --stat ↔ editable/forbidden).

## 4. Verification (acceptance 매핑)
- A1/A2/A3-PP → S1 pytest(모드별 직렬화 + 매핑 + 508 회귀 0).
- A4 → S2 prompt-version-review. A5 → S3 3-mode 분기 + rich byte-identical. A6 → S4 critic director 차원.
- A7 → S5 tsc/build/design-review. A8/A9 → S6 depth 측정 + cost + 라이브 + 키 0 + close.
