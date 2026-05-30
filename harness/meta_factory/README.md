# meta_factory — L3 Meta-Harness Factory

> 위치: `harness/meta_factory/`
> 상태: Phase M0 (Meta-Factory Prep, ★ meta-phase) Slice 1 도입 — skeleton + contract
> 결정: ADR-035 (phase_M0_meta_factory.md)
> ★ 런타임 변경 0 (A9) — FastAPI/Next.js/Supabase 0줄. 문서/skeleton/proposal 레이어.

---

## 0. 한 줄 정의

현재 Dreammate-Studio 구현 하네스(L2)를 유지하면서, 상위에 **하네스를 설계·역정리·검증하는 메타 레이어(L3)** 를 둔다. ① 현재 하네스를 blueprint 로 역정리하고 ② 새 도메인 하네스 생성의 입력/출력 구조를 정의하며 ③ Agent/Skill/Contract/Eval/Phase 생성 전 검증 기준을 만든다. **자동 generator 구현이 아니라 skeleton·contract·validation 정의까지만** (payoff deferred).

---

## 1. 3계층 모델 (L1 / L2 / L3)

### L1 — Product Runtime

실제 제품이 동작하는 런타임 레이어.

- FastAPI (backend) / Next.js (frontend PWA) / Supabase (PostgreSQL + pgvector)
- RAG / SSE Progress / MOA runtime (Intent → Planning → Critic → Rewriter)
- ★ meta_factory 는 이 레이어를 **직접 수정하지 않는다** (A9 — 0줄).

### L2 — Implementation Harness

현재 프로젝트가 운용하는 구현 하네스 (지금 이 저장소).

- 라우터: `AGENTS.md` (구현/QA 모델) / `CLAUDE.md` (기획/설계 모델)
- 상태: `PROJECT_STATE.md` / `PHASE_REGISTRY.md`
- 계약: `docs/contracts/**` (api / output_schema / agent_io / db_schema / llm_security ...)
- 운영: `phases/**` (active/archive) / `eval/**` (golden_set / rubric) / `.claude/skills/**` (21 Skill — Phase M0에서 harness-factory #21 추가)
- 메타: `meta/self_improvement_loop.md` (5단계 루프) / `meta/retrospectives` / `meta/validations`

### L3 — Meta-Harness Factory (이 디렉토리, 신규)

L2 하네스를 **설계·역정리·검증·개선 제안**하는 메타 레이어.

- **harness blueprint 생성** — 현재/신규 하네스를 청사진 문서로 정리
- **agent·skill·contract·eval scaffold 설계** — 6 scaffold 템플릿 기반 (자동 편집 아님)
- **trigger validation** — Skill 키워드 충돌 / agent 트리거 정합 검증
- **with-without skill 비교** — Skill 추가의 효용을 비교 검토 (eval-run 연동)
- **기존 하네스 개선 제안** — improvement_reports 로 proposal-first 제출

> **책임 경계**: `meta/self_improvement_loop.md` = L2 하네스를 **내부에서 개선(in-place)**. L3 meta_factory = **하네스를 만드는 방법 + 청사진 + 검증 기준**을 정의. L3 는 self_improvement_loop 의 "제안 → 검토 → 승인 → 반영" 원칙을 "하네스 생성" 영역으로 상위 정식화한 것.

---

## 2. ★ proposal-first 도구 (자동 적용 도구 아님)

> **Meta-Factory 는 자동 적용 도구가 아니라 proposal-first 도구다.**

- 생성 결과(harness blueprint / scaffold / 개선 제안)는 **자동으로 active 하네스에 반영되지 않는다**.
- 생성물은 `meta_factory/outputs/generated_harnesses/` 또는 `meta/proposals/` 에 **먼저** 둔다.
- 생성된 harness 는 `validation_workflow.md` 통과 전 active 로 간주하지 않는다.
- 기존 self_improvement_loop §0/§7 "자가개선은 자동 수정이 아니다 — 항상 제안 → 검토 → 승인 → 반영" 원칙을 계승.
- 상세 규칙은 `factory_contract.md` (8 절대 규칙).

---

## 3. 디렉토리 구조

```
meta_factory/
├── README.md                       # 본 문서 (L1/L2/L3 + proposal-first)
├── factory_contract.md             # 8 절대 규칙 (런타임 미변경 + proposal-first)
├── domain_brief_schema.md          # 생성 입력 schema (도메인 정의)
├── harness_blueprint_schema.md     # 생성 출력 schema (하네스 청사진)
├── architecture_patterns.md        # 6 패턴 + Dreammate 매핑
├── generation_workflow.md          # 11단계 생성 절차          (Slice 2)
├── validation_workflow.md          # 6 검증 절차                (Slice 2)
├── templates/                      # 6 scaffold 템플릿          (Slice 2)
│   └── {agent,skill,contract,eval,phase,project_state}_template.md
├── blueprints/                     # 현재 하네스 실측 역정리     (Slice 2)
│   └── dreammate_current_harness_blueprint.md
└── outputs/                        # 생성물 격리 (proposal-first)
    ├── generated_harnesses/        # 생성된 하네스 (active 아님)
    └── improvement_reports/        # 개선 제안 리포트
```

> 본 Slice 1 = README + factory_contract + 2 schema + architecture_patterns. workflow/templates/blueprint = Slice 2. harness-factory Skill + INDEX 등록 = Slice 3.

---

## 4. 진입점 (어떻게 쓰나)

| 목적 | 입력 | 절차 | 출력 |
|---|---|---|---|
| 현재 하네스 이해 | (없음) | `blueprints/dreammate_current_harness_blueprint.md` 정독 | 온보딩·감사 문서 |
| 새 도메인 하네스 설계 | `domain_brief_schema.md` 작성 | `generation_workflow.md` 11단계 + `validation_workflow.md` 6 검증 | `harness_blueprint_schema.md` 형식 blueprint → outputs/generated_harnesses/ |
| 기존 하네스 개선 | (관찰) | self_improvement_loop + harness-audit → proposal | outputs/improvement_reports/ 또는 meta/proposals/ |

Skill 진입은 `harness-factory` (proposal-only, 키워드 scoped — Slice 3). 키워드: `harness blueprint`, `meta_factory`, `harness scaffold`, `도메인 하네스 생성`, `agent·skill scaffold 설계`.

---

## 5. 제약 (요약 — 상세는 factory_contract.md)

- ★ 런타임(L1) 변경 0 (A9) — FastAPI/Next/Supabase 0줄.
- 기존 하네스(L2) 직접 변경 금지 — proposal-first.
- 생성 결과는 outputs/ 또는 meta/proposals/ 에 먼저.
- Skill 추가/변경은 INDEX 충돌 규칙 + contract-change Skill 절차.
- payoff deferred — skeleton·contract·validation 까지만 (자동 generator 아님).

---

## 6. 모델별 사용 지침 (Claude / Codex)

`harness-factory` Skill 은 `applies_to: [claude]` (기획·설계 모델 전용). Codex 등 구현/QA 모델(`AGENTS.md` 라우터)은 이 Skill 을 자동 인지하지 못할 수 있으므로 다음을 따른다.

### Claude (CLAUDE.md 라우터)
- `harness-factory` Skill 키워드("harness blueprint", "meta_factory", "harness scaffold", "도메인 하네스 생성")로 자동 트리거 → generation_workflow + validation_workflow 진행.

### Codex (AGENTS.md 라우터)
- `harness-factory` Skill 미인지 → meta_factory 문서를 **직접 순서대로 읽고** 수행:
  `README.md → factory_contract.md → generation_workflow.md → validation_workflow.md`
- ★ **product runtime(L1) 변경 없이** outputs/ 에 문서 산출물만 생성 (proposal-first).
- 기존 harness(L2 — AGENTS/CLAUDE/PROJECT_STATE/contracts/Skill) 직접 변경 금지. 생성물은 `outputs/generated_harnesses/` 또는 `meta/proposals/` 에 먼저.

> 현 단계 결정: harness-factory 는 **claude 전용 유지**(안전한 선택). Codex 적극 활성(applies_to [agents, claude]) 은 dry-run 검증 후 별도 phase 에서 재검토.
