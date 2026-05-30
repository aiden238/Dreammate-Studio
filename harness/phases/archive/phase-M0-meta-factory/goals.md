# Phase M0 — Goals (Meta-Factory Prep)

> Phase: phase-M0-meta-factory
> 유형: **meta-phase** (제품 phase 아님 — L3 Meta-Harness Factory skeleton)
> 진입일: 2026-05-31
> 예상 시간: 4~7h (3 Slice 모두 sub-agent dispatch)
> ★ 런타임 변경 0 (FastAPI/Next.js/Supabase 0줄) — proposal-first 메타 레이어

## 한 줄 정의

현재 Dreammate-Studio 구현 하네스(L2)를 유지하면서, 상위에 **`harness/meta_factory/` (L3 Meta-Harness Factory) skeleton + contract + validation 기준**을 추가하여, ① 현재 하네스를 blueprint로 역정리하고 ② 새 도메인 하네스 생성의 입력/출력 구조를 정의하며 ③ Skill/Agent/Contract/Eval/Phase 생성 전 검증 기준을 만든다. **자동 generator 구현이 아니라 skeleton·contract·validation 정의까지만**.

## 3계층 모델 (L1/L2/L3)

```
L1 Product Runtime    : FastAPI / Next.js / Supabase / RAG / SSE / MOA runtime
L2 Implementation Harness : AGENTS/CLAUDE/PROJECT_STATE/contracts/phases/eval/skills (현재)
L3 Meta-Harness Factory   : harness blueprint 생성 / agent·skill·contract·eval scaffold 설계 /
                            trigger validation / with-without skill 비교 / 개선 제안 (신규)
```

## 핵심 목표 (G1~G7)

| ID | 목표 | 검증 |
|---|---|---|
| **G1** | `meta_factory/` 기본 구조 생성 (README + 6 contract/workflow md + templates 6 + blueprints + outputs) | A1, A4 |
| **G2** | `factory_contract.md` — proposal-first + 런타임 미변경 8 규칙 | A3 |
| **G3** | `domain_brief_schema.md` + `harness_blueprint_schema.md` — 생성 입력/출력 구조 | A4 |
| **G4** | `architecture_patterns.md` — 6 패턴 + Dreammate 매핑 (Supervisor=orchestrator 등) | A5 |
| **G5** | `validation_workflow.md` — trigger validation + skill conflict + with/without 비교 + eval-run 연동 | A6 |
| **G6** | `dreammate_current_harness_blueprint.md` — 현재 하네스 **실측** 역정리 + L3 부족점 | A7 |
| **G7** | `harness-factory` Skill (proposal-only) + INDEX #21 등록 + 키워드 충돌 검토 | A8 |

## 메타 목표 (M1~M3)

| ID | 목표 |
|---|---|
| **M1** | multi-llm-validation formal self 여덟 번째 (L3 도입 타당성) + external placeholder |
| **M2** | contract-change Skill (INDEX.md Skill 등록 — Skill도 contract처럼 취급) |
| **M3** | P-X1 §SELF-VERIFICATION **50연속 PASS** (Phase 9.5:47 + M0:3) |

## 사용자 가치 (Why)

- **메타 하네스 정식화**: 기존 `meta/self_improvement_loop` + `harness-audit` 문화를 L3로 상위 정식화
- **즉시 가치**: 현재 하네스 blueprint = 온보딩·감사·교차검증 문서 (2nd 하네스 무관)
- **확장 기반**: 추후 다른 도메인 하네스 생성/개선 시 입력·검증 기준 확보 (payoff deferred, skeleton-only)

## ★ 절대 금지 (non_goals.md 상세)

런타임 코드(FastAPI/Next/Supabase) 변경 / 기존 contracts·AGENTS·CLAUDE·PROJECT_STATE 직접 변경 / 기존 Skill 대량 변경 / 자동 generator 코드 / `.claude/agents/` 자동 생성 / 실제 타 도메인 하네스 생성 / P-AUX-2 / generated harness 자동 active 전환 — 모두 다음 phase 이관.
