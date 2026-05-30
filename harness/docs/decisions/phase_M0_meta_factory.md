# ADR-035 — Phase M0 L3 Meta-Harness Factory 도입 (proposal-first skeleton)

> Date: 2026-05-31
> Status: Accepted
> Phase: M0 (Meta-Factory Prep — ★ meta-phase, 제품 phase 아님)
> Slice: 1 (본 ADR 결정 + meta_factory 핵심 contract 문서) / Slice 2~3 (workflow + blueprint + templates + Skill)
> Related: self_improvement_loop.md (L2 in-place 메타 루프 — L3 가 상위 정식화), INDEX.md (Skill 체계 — harness-factory scoping 근거), ADR-024 (RAG scope evolution — payoff deferred 선례), ADR-033 (eval-run harness — 메타 자산 확장 선례)
> Skill: multi-llm-validation (★ formal 여덟 번째 — V1~V6 PASS, 첫 meta-phase)
> ★ 런타임 변경 0 (A9 — FastAPI/Next.js/Supabase 0줄)

## Context

영상기획 AI 에이전트 프로젝트(Phase 0~9.5 누적)는 이미 **메타 문화**를 보유한다. 그러나 이 메타 문화는 현재 하네스(L2)를 **내부에서 개선(in-place)** 하는 데 초점이며, "하네스를 만드는 방법" 자체를 정의하는 상위 레이어는 부재하다.

### 3계층 모델 (L1/L2/L3)

```
L1 Product Runtime        : FastAPI / Next.js / Supabase / RAG / SSE / MOA runtime
L2 Implementation Harness : AGENTS/CLAUDE/PROJECT_STATE/contracts/phases/eval/skills (현재)
L3 Meta-Harness Factory   : harness blueprint 생성 / agent·skill·contract·eval scaffold 설계 /
                            trigger validation / with-without skill 비교 / 기존 하네스 개선 제안 (신규)
```

### 기존 메타 문화 (실측)

- `meta/self_improvement_loop.md` — 5단계 루프(회고 → 패턴 추출 → 제안 → 검토/승인 → 반영) + §0/§7 "자동 수정 금지, 항상 제안 → 검토 → 승인 → 반영" 원칙.
- `harness-audit` Skill (#18) — 정기 구조 감사 (stub 잔존 / 깨진 contract 참조 / Skill 키워드 충돌 / 미사용 Skill).
- `meta-retrospective` Skill (#9) — Phase 종료 회고 + 개선 제안 (항상 제안 → 검토 → 승인 → 반영).
- `meta/validations/` — multi-llm-validation **8회 누적** (formal 7 + informal 1).

### 실측 baseline (entry 확인 — Slice 2 blueprint 단일 출처)

- HEAD = `fff913e` (Phase 9.5 done). pytest **339** + P-X1 §SELF-VERIFICATION streak **47** + PlanCard 35 + component_map 45.
- Skill **20개** (INDEX v1.2.0 — 절차 핵심 14 + 검토/감사 6) → harness-factory 추가 시 21 (Slice 3).
- golden_set **11 케이스** (GS-001~GS-011, golden_set.md v1.0.0 §2 — entry plan 일부 "47" 기재는 정정. 케이스 확대는 Phase 10+).
- `.claude/agents/` **부재** → blueprint 부족점 "agent 자동 생성 / Claude Code subagent 정의 디렉토리 미사용" 실측 근거.
- ADR **ADR-001~034** 누적 (docs/decisions, 최신 ADR-033/034) → 본 ADR = ADR-035.
- MOA orchestrator (`backend/fastapi/orchestration/moa_orchestrator.py::generate_plan`) = **Supervisor 패턴** (agent 직접 호출 금지, orchestrator 중개 — moa_policy §2 정합).

### Gap

- 현재 하네스가 어떤 구조(agent/skill/contract/eval/phase/routing)로 이뤄졌는지 **단일 blueprint 문서 부재** → 온보딩·감사·교차검증 시 산재한 문서를 일일이 추적해야 함.
- 새 도메인 하네스를 만들 때의 **입력/출력 구조 + 검증 기준 부재** → 즉흥적 생성 위험 (Skill 키워드 충돌 / contract 누락 / 미검증 active 전환).
- self_improvement_loop 의 "제안 → 검토 → 승인 → 반영" 원칙이 "하네스 생성" 영역으로 확장된 정식 문서 부재.

## Decision

`harness/meta_factory/` (L3 Meta-Harness Factory) **skeleton + contract + validation 기준**을 도입한다. ★ **자동 generator 구현이 아니라 skeleton·contract·validation 정의까지만** (NG11).

### 1. meta_factory/ skeleton 구조

```
harness/meta_factory/
├── README.md                       # L1/L2/L3 모델 + ★ proposal-first 명시
├── factory_contract.md             # 8 절대 규칙 (런타임 미변경 + proposal-first)
├── domain_brief_schema.md          # 생성 입력 schema (도메인 정의)
├── harness_blueprint_schema.md     # 생성 출력 schema (하네스 청사진)
├── architecture_patterns.md        # 6 패턴 + Dreammate 매핑
├── generation_workflow.md          # 11단계 생성 절차 (Slice 2)
├── validation_workflow.md          # 6 검증 절차 (Slice 2)
├── templates/                      # 6 scaffold 템플릿 (Slice 2)
│   └── {agent,skill,contract,eval,phase,project_state}_template.md
├── blueprints/                     # 현재 하네스 실측 역정리 (Slice 2)
│   └── dreammate_current_harness_blueprint.md
└── outputs/                        # 생성물 격리 (proposal-first)
    ├── generated_harnesses/.gitkeep
    └── improvement_reports/.gitkeep
```

본 Slice 1 = README + factory_contract + domain_brief_schema + harness_blueprint_schema + architecture_patterns (핵심 5 contract 문서) + ADR-035 + validations. workflow/templates/blueprint = Slice 2. harness-factory Skill + INDEX 등록 = Slice 3.

### 2. L3 책임 (5 기능)

1. **harness blueprint 생성** — 현재/신규 하네스를 청사진 문서로 정리 (역정리 + 정방향 생성).
2. **agent·skill·contract·eval scaffold 설계** — 6 scaffold 템플릿 기반 (자동 편집 아님 — 템플릿 제공).
3. **trigger validation** — Skill 키워드 충돌 / agent 트리거 정합 검증 (validation_workflow).
4. **with-without skill 비교** — Skill 추가의 효용을 비교 검토 (eval-run 연동).
5. **기존 하네스 개선 제안** — improvement_reports 로 proposal-first 제출 (self_improvement_loop 상위).

### 3. proposal-first 원칙 (★)

meta_factory 는 **자동 적용 도구가 아니라 proposal-first 도구**. 생성 결과는 `meta_factory/outputs/generated_harnesses/` 또는 `meta/proposals/` 에 **먼저** 둔다. 생성된 harness 는 validation_workflow 통과 전 active 로 간주하지 않는다. self_improvement_loop §0/§7 "자동 수정 금지" 원칙을 "하네스 생성" 영역으로 계승.

## Constraints

- **런타임 변경 0 (A9)** — FastAPI(`backend/fastapi/**`) / Next.js(`apps/web/**`, PlanCard·component_map 포함) / Supabase(`db/migrations/**`) 0줄. git diff 자동 게이트(`grep -E "backend/fastapi|apps/web|db/migrations"` = 0). meta_factory 는 문서/skeleton 레이어 — 런타임 무관.
- **proposal-first** — 생성물은 outputs/ 또는 meta/proposals/ 에 먼저. validation_workflow 통과 전 active 아님. 자동 적용 경로 전면 차단 (NG10).
- **meta-phase 격리** — Phase M0 는 제품 phase(Phase 10/11)와 번호 분리(`phase-M0`, `phase_m0_*` state 키, `phase_m0_type: meta-phase`). 제품 로드맵(next_phase_status) 보존. archive/회고/P-X1/multi-llm-validation 규율은 제품 phase 와 동일 유지.
- **payoff deferred — skeleton·contract·validation 까지만 (NG11)** — 자동 generator 작성 X (코드 0), `.claude/agents/` 자동 생성 X(NG12), 타 도메인 하네스 실제 생성 X(NG13). 즉시 가치는 ① 현재 하네스 blueprint(온보딩/감사 문서, 2nd 하네스 무관) + ② 메타 문화 정식화. 생성 payoff 는 2nd 하네스 착수 시점까지 이연.
- **harness-factory Skill 키워드 scoped** — 허용: `harness blueprint`/`meta_factory`/`harness scaffold`/`도메인 하네스 생성`/`agent·skill scaffold 설계`. 금지(타 Skill 소유): `하네스 개선`/`메타 개선`/`회고`(meta-retrospective) + bare `하네스 감사`/`구조 점검`/`전체 검토`(harness-audit) + `phase 생성` 단독(phase-start). 우선순위 `harness-audit > harness-factory`, `contract-change > harness-factory`, `eval-run > harness-factory validation`. (Slice 3 등록 + 충돌 검토.)

## Trade-offs

- **메타-툴링 투자 vs 제품 진전 (의식적 detour)**: Phase M0 는 제품 기능을 0줄 진전시키지 않는다. 대신 메타 레이어(L3)에 4~7h 를 투자. 사용자 결정(notes §GPT 평가 caveat C1/C2)으로 의식적 detour 로 승인됨. YAGNI 위험은 ① skeleton-only(자동 generator 아님) + ② blueprint(즉시 가치) + ③ payoff deferred 명시로 완화.
- **추상 레이어 도입 vs 단순성**: L3 는 추가 추상 레이어다. 그러나 기존 self_improvement_loop + harness-audit + meta-retrospective 문화의 **자연 확장**(단절적 신규 아님) — self_improvement_loop = L2 in-place 개선 / L3 = 하네스 생성·blueprint 로 책임 경계 분리.
- **proposal-first 의 적용 지연 vs 안전성**: proposal-first 는 자동 적용을 막아 안전하지만 적용까지 사람 검토 단계를 요구. self_improvement_loop §11 Open Question 4(자동 수정 금지가 적용 지연을 일으킬 위험)와 동일 트레이드오프 — 메타 레이어에서는 안전성을 우선.

## References

- `meta/self_improvement_loop.md` (5단계 루프 + §0/§7 자동 수정 금지 — L3 가 상위 정식화. 책임 경계: self_improvement_loop = L2 in-place 개선 / L3 = 하네스 생성·blueprint)
- `.claude/skills/INDEX.md` (Skill 체계 v1.2.0, 20 Skill — harness-factory 키워드 scoping + Skill 신규/변경 절차 근거)
- `meta/validations/2026-05-31_phase-M0-pre-entry_self.md` (V1~V6 PASS — L3 도입 타당성/런타임0/proposal-first/meta-phase/Skill scoping/blueprint 실측)
- `backend/fastapi/orchestration/moa_orchestrator.py` (Supervisor 패턴 실측 — architecture_patterns Dreammate 매핑 근거, 읽기만)
- 실측 baseline: golden_set 11 / `.claude/agents` 부재 / ADR-001~034 / P-X1 47 / Skill 20 / MOA Supervisor (Slice 2 blueprint 단일 출처)
- ADR-024 (RAG scope evolution — payoff deferred + skeleton-first 선례) / ADR-033 (eval-run harness — 메타 자산 확장 선례)
