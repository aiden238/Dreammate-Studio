# Phase M0 Pre-Entry Multi-LLM Validation — Self (Claude Code)

> 검증 모델: Claude Code (자가, 지침 참조)
> 검증 일자: 2026-05-31
> 검증 유형: formal (★ 여덟 번째 정식 트리거 — Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째 + Phase 8 다섯째 + Phase 9 여섯째 + Phase 9.5 일곱째 + Phase M0 여덟째)
> 외부 검증: `2026-05-31_phase-M0-pre-entry_external.md` (별도 placeholder)
> Skill 의무 트리거: multi-llm-validation (formal 여덟 번째) — ★ meta-phase (런타임 변경 0, A9)

## 검증 대상

Phase M0 = **L3 Meta-Harness Factory skeleton** (proposal-first 메타 레이어). meta-phase — 제품 phase 아님. 사용자 결정 3건:
- **meta-phase (Phase M0, 3 Slice)** — PHASE_REGISTRY 제품 phase(10/11)와 번호 분리, archive/회고/P-X1 규율 유지.
- **harness-factory Skill 추가** (proposal-only, 키워드 scoping) — Slice 3.
- **proposal-first** — 생성물은 meta_factory/outputs/ 또는 meta/proposals/에 먼저 (자동 적용 X).

본 Slice 1 검증 항목 (V1~V6):
1. L3 Meta-Factory 도입 타당성 (기존 meta 문화 정합)
2. 런타임 변경 0 (A9 — FastAPI/Next.js/Supabase 0줄)
3. proposal-first (자동 적용 X)
4. meta-phase 격리 (제품 phase 오염 X)
5. harness-factory Skill 키워드 scoping (harness-audit/meta-retrospective 충돌 회피)
6. blueprint 실측 (golden_set 11, .claude/agents 부재, ADR-001~034, P-X1 47)

## 참조한 지침

- `harness/phases/active/phase-M0-meta-factory/{goals,scope,non_goals,assumptions,multi_slice_plan,notes}.md` (A9 게이트 + 키워드 scoping)
- `harness/meta/self_improvement_loop.md` (기존 5단계 메타 루프 — L3 정합 근거)
- `harness/AGENTS.md` + `harness/CLAUDE.md` (라우터 — blueprint routing_docs 근거, 읽기만)
- `harness/.claude/skills/INDEX.md` (Skill 체계 v1.2.0, 20 Skill — blueprint §5 + harness-factory 충돌 근거)
- `harness/backend/fastapi/orchestration/moa_orchestrator.py` (Supervisor 패턴 매핑 — generate_plan 중개, 읽기만)
- `harness/docs/contracts/agent_io_contract.md` (contract 구조 — contract_template/blueprint 근거, 읽기만)
- `harness/meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` (V형식 — 일곱 번째 formal)
- `harness/meta/skill_usage_log.md` + `harness/PROJECT_STATE.md` (현 누적 — meta-phase 등록 위치)
- `.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

> ★ baseline 실측 (entry 확인): HEAD = fff913e (Phase 9.5 done). pytest 339 + P-X1 **47** + PlanCard 35 + component_map 45 + Skill **20**. golden_set **11 케이스 (GS-001~GS-011)**. `.claude/agents/` **부재**. ADR **ADR-001~034** 누적 (다음 ADR-035). `meta_factory/` **신규** (충돌 0).

## 검증 결과 (V1~V6)

### V1. L3 Meta-Factory 도입 타당성 (기존 meta 문화 정합) — PASS

- **self-question**: `harness/meta_factory/` (L3 Meta-Harness Factory) 를 신규 도입하는 것이 기존 `meta/self_improvement_loop` + `harness-audit` + `meta-retrospective` 메타 문화와 정합하며, 새 추상 레이어가 아니라 기존 문화의 **상위 정식화**로 자리잡는가? YAGNI(아직 2nd 하네스 없음) 위험은 어떻게 완화되는가?
- **self-answer**:
  - **현 상태 (self_improvement_loop 정독)**: 프로젝트는 이미 메타 문화를 보유. ① `meta/self_improvement_loop.md` — 5단계 루프(회고 → 패턴 → 제안 → 검토 → 반영) + "자동 수정 금지, 항상 제안 → 검토 → 승인 → 반영" 원칙(§0/§7). ② `harness-audit` Skill — 정기 구조 감사(stub/contract 참조/Skill 충돌). ③ `meta-retrospective` Skill — Phase 종료 회고 + 개선 제안. ④ `meta/validations/` — multi-llm-validation 8회 누적. 즉 "하네스 자체를 점검·개선하는" L2-내부 메타 활동은 이미 존재.
  - **L3 정식화의 차별점**: 기존 메타 문화(self_improvement_loop)는 **현재 하네스(L2)를 개선**하는 데 초점(in-place 개선). L3 Meta-Factory 는 ⓐ 현재 하네스를 **blueprint 로 역정리**(온보딩·감사·교차검증 문서) + ⓑ 새 도메인 하네스 생성의 **입력/출력 구조 정의**(domain_brief / harness_blueprint schema) + ⓒ Agent/Skill/Contract/Eval/Phase 생성 전 **검증 기준**(validation_workflow). 즉 self_improvement_loop 가 "이 하네스를 고친다"면 L3 는 "하네스를 만드는 방법을 정의한다" — 한 단계 위 추상.
  - **정합 근거**: ① self_improvement_loop §0 "자동 수정 금지 + 제안 → 검토 → 승인 → 반영" 원칙을 L3 factory_contract 가 그대로 계승(proposal-first, V3). ② harness-audit 의 "구조 점검" 자산이 blueprint 역정리(L3)의 입력. ③ INDEX.md "Skill 신규/변경은 contract-change 절차" 가 L3 의 Skill scaffold 생성 규칙과 직결. → L3 는 단절적 신규가 아니라 기존 문화의 자연 확장.
  - **YAGNI 완화 (payoff deferred, skeleton-only)**: 2nd 하네스가 아직 없으므로 자동 generator 구현은 NG11 로 명시 배제. 본 phase 는 **skeleton·contract·validation 기준까지만**. 즉시 가치는 ① 현재 하네스 blueprint(2nd 하네스 무관, 온보딩/감사 문서) + ② 메타 문화 정식화(self_improvement_loop 의 상위 레이어 명문화). 투자 규모도 문서 phase(4~7h, 코드 0).
  - **한계 (정직)**: L3 의 "새 도메인 하네스 생성" payoff 는 2nd 하네스 착수 시점까지 deferred — 본 phase 단독 ROI 는 blueprint + 정식화로 한정. 이는 의식적 detour(notes §GPT 평가 caveat C1/C2)로 사용자 승인됨.
- **잠재 risk**:
  - L3 가 "추상 레이어를 위한 추상 레이어"로 그칠 위험 → skeleton-only + blueprint(즉시 가치) + payoff deferred 명시로 완화. ADR-035 §Trade-offs 에 의식적 detour 명시.
  - 기존 self_improvement_loop 와 L3 의 책임 중첩 → ADR-035 §References 에 "self_improvement_loop = L2 in-place 개선 / L3 = 하네스 생성·blueprint" 경계 명시.
- **권장**:
  - ADR-035 §Context 에 "기존 meta/self_improvement_loop(5단계 루프) + harness-audit + meta-retrospective 메타 문화 → L3 상위 정식화 필요" 명시.
  - ADR-035 §Constraints 에 "payoff deferred — skeleton·contract·validation 까지만, 자동 generator 아님 (NG11)" 명시.

### V2. 런타임 변경 0 (A9 — FastAPI/Next.js/Supabase 0줄) — PASS

- **self-question**: Phase M0 가 메타 레이어 추가만 수행하고 런타임(backend/fastapi/** + apps/web/** + db/migrations/**) 을 0줄 변경한다는 A9 게이트가 모든 작업 단위에서 구조적으로 보장되며, git diff 게이트로 자동 검증 가능한가?
- **self-answer**:
  - **scope 구조 (scope.md 정독)**: 본 phase 의 모든 산출물은 ⓐ `harness/meta_factory/**`(신규 문서/skeleton) + ⓑ `.claude/skills/harness-factory`(Slice 3) + INDEX(Slice 3) + ⓒ `docs/decisions/`(ADR) + ⓓ `meta/`(validations/proposals/retrospectives) + ⓔ `scripts/`(Slice 3 meta-phase 경량) + ⓕ state docs(meta-phase 등록). 어느 것도 런타임 코드 파일이 아님. blueprint 역정리는 moa_orchestrator.py 등을 **읽기만** (Supervisor 패턴 매핑 근거).
  - **A9 보장 구조**: non_goals NG1~NG3 + scope §forbidden 이 `backend/fastapi/**` / `apps/web/**`(PlanCard·component_map 포함) / `backend/fastapi/db/migrations/**` 를 절대 금지로 못박음. sub-agent SELF-VERIFICATION(P-X1) 가 매 Slice commit 직전 staged diff 를 검사. 본 Slice 1 의 editable 은 meta/validations + docs/decisions + meta_factory 5 문서 + skill_usage_log + PROJECT_STATE + phases/active 로 한정 — 런타임 0.
  - **자동 검증**: 사후 `git diff --cached --name-only | grep -E "backend/fastapi|apps/web|db/migrations"` = 0 lines 가 A9 자동 게이트. Phase 9.5 §SELF-VERIFICATION 와 동일 패턴. INDEX.md 예외(Slice 3)도 런타임 아님.
  - **회귀 0 근거**: 런타임 파일 미터치 → pytest 339 / tsc / build 회귀 불가능(코드 변경 0). 본 phase 는 baseline test 실행조차 불필요(런타임 무관) — Slice 3 smoke 에서 "런타임 회귀 0 + meta_factory 구조 존재" 만 경량 확인.
- **잠재 risk**:
  - blueprint 역정리 중 "정리 김에 기존 contract/runtime 손봄" 유혹 → NG7/NG1 + scope §회피 패턴으로 차단. 읽기만.
  - meta_factory 문서가 런타임 경로명을 인용(예: moa_orchestrator.py)하는 것은 텍스트 참조이지 변경 아님 — A9 무관.
- **권장**:
  - ADR-035 §Constraints 에 "런타임 변경 0 (A9) — FastAPI/Next/Supabase 0줄, git diff 자동 게이트" 명시.
  - 매 Slice §SELF-VERIFICATION 에 `backend/fastapi|apps/web|db/migrations` grep = 0 강제.

### V3. proposal-first (자동 적용 X) — PASS

- **self-question**: meta_factory 가 **자동 적용 도구가 아니라 proposal-first 도구**라는 원칙이 factory_contract 8 규칙 + outputs/proposals 배치 구조로 강제되며, 기존 self_improvement_loop §0 "자동 수정 금지" 원칙과 정합하는가?
- **self-answer**:
  - **proposal-first 정의 (non_goals §핵심 원칙)**: meta_factory 의 생성 결과(harness blueprint / agent·skill·contract scaffold / 개선 제안)는 자동으로 active 하네스에 반영되지 않고 ⓐ `meta_factory/outputs/generated_harnesses/` 또는 ⓑ `meta/proposals/` 에 **먼저** 둔다. 생성된 harness 는 validation_workflow 통과 전 active 로 간주하지 않는다.
  - **factory_contract 강제 (§5.2 8 규칙)**: 규칙 1(product runtime 직접 수정 금지) + 규칙 2(기존 harness 직접 변경 금지) + 규칙 3(생성 결과는 outputs/ 또는 proposals/에 먼저) + 규칙 7(validation_workflow 통과 전 active 아님) 이 proposal-first 를 contract 수준으로 못박음. 규칙 4(Skill 은 INDEX 충돌 규칙) + 규칙 5(contract 변경은 contract-change Skill) + 규칙 6(PROJECT_STATE 사용자 승인 없이 갱신 금지) 가 "직접 적용" 경로를 전부 절차로 우회.
  - **정합 근거**: self_improvement_loop §0 "자가개선은 자동 수정이 아니다. 항상 회고 → 패턴 → 제안 → 검토 → 승인 → 반영" + §7 "AI가 retrospective 결과만 보고 직접 contract/skill 변경 금지" 와 1:1 정합. L3 factory_contract 는 이 원칙을 "하네스 생성" 영역으로 확장한 것. 예외(self_improvement_loop §7: "쓰는 것은 가능, 적용하는 것은 금지")도 동일 — meta_factory 가 proposal 을 작성하는 것은 허용, 자동 반영은 금지.
  - **NG10 정합**: "meta_factory 결과물 기존 하네스 자동 반영" 은 NG10 으로 명시 배제. "자동 active 전환" 단어도 금지(금지 명시는 허용).
- **잠재 risk**:
  - "proposal 김에 바로 적용" 유혹 → factory_contract 규칙 3/7 + NG10 으로 차단. 본 phase 는 generated harness 0개(skeleton 만) → 적용 대상 자체가 없음.
  - proposal 과 active 의 경계 모호 → outputs/ vs active 디렉토리 물리 분리 + validation_workflow 게이트(Slice 2)로 명확화.
- **권장**:
  - README.md 에 ★ "Meta-Factory 는 자동 적용 도구가 아니라 proposal-first 도구" 명시(사용자 §5.1).
  - factory_contract 규칙 3 "생성 결과는 outputs/generated_harnesses/ 또는 meta/proposals/에 먼저 둔다" + 규칙 7 "validation_workflow 통과 전 active 아님" 명시.

### V4. meta-phase 격리 (제품 phase 오염 X) — PASS

- **self-question**: Phase M0 를 **meta-phase**(제품 phase 아님)로 등록하여 PHASE_REGISTRY/PROJECT_STATE 의 제품 phase(10/11) 번호 흐름을 오염시키지 않으면서, archive/회고/P-X1 규율은 동일하게 유지하는 것이 정합한가?
- **self-answer**:
  - **meta-phase 정의 (사용자 결정, goals.md)**: Phase M0 는 `phase-M0-meta-factory` 디렉토리 + `phase_m0_*` state 키로 제품 phase 와 **번호 분리**(M0 = Meta-Factory Prep). 제품 진전(Phase 10 MVP 통합 / Phase 11+) 흐름과 독립. 단 archive 이동 + retrospective + P-X1 §SELF-VERIFICATION + multi-llm-validation 규율은 제품 phase 와 동일 적용.
  - **격리 구조**: ⓐ state 키 `phase_m0_status` / `phase_m0_type: meta-phase` (제품 phase 아님 명시) — 제품 phase 키(`phase_10_*`)와 충돌 0. ⓑ `next_phase_status: pending_user_decision`(제품 phase 옵션 A/B)는 **제거하지 않고** Phase M0 가 그 위에 meta-phase 로 얹힘 — 즉 제품 로드맵은 보존, M0 는 병렬 detour 로 기록. ⓒ PROJECT_STATE active phase 섹션에 "Phase 9.5 done 위에 Phase M0" 로 등록(제품 phase 9.5 완료 보존).
  - **정합 근거**: ① Phase 5.5(mini-phase, legacy consolidation)가 제품 phase 사이에 끼어든 선례 — 번호 규율은 유지하되 성격(consolidation)을 명시한 패턴 계승. ② meta-phase 는 런타임 0(A9) → 제품 baseline(pytest 339) 불변 → 제품 phase 회귀 추적에 영향 0. ③ P-X1 streak 은 메타/제품 무관하게 §SELF-VERIFICATION 규율 누적(47 → 목표 50) — 격리되어도 규율 연속성 유지.
  - **오염 방지**: NG8(PROJECT_STATE 큰 폭 임의 수정 금지) — meta-phase 등록은 최소 갱신만(active phase 섹션 + migration_progress phase_m0_* 키). 제품 phase 9.5 done 블록 + confirmed_decisions(25) + 제품 로드맵은 불변.
- **잠재 risk**:
  - meta-phase 가 제품 phase 번호와 혼동(U3) → `phase-M0`(대문자 M + 0) 명명으로 시각적 분리 + `phase_m0_type: meta-phase` 키로 명시.
  - state docs 갱신이 제품 phase 흐름을 덮어씀 → 최소 갱신(active 섹션 + migration_progress) + next_phase_status 보존(제품 로드맵 유지).
- **권장**:
  - PROJECT_STATE active phase 에 "Phase M0 (meta-phase, 3 Slice, 런타임 0)" 를 Phase 9.5 done 위에 등록 + migration_progress `phase_m0_type: meta-phase` 키.
  - ADR-035 §Constraints 에 "meta-phase 격리 — 제품 phase(10/11) 번호 분리, archive/회고/P-X1 규율 유지" 명시.

### V5. harness-factory Skill 키워드 scoping (harness-audit/meta-retrospective 충돌 회피) — PASS

- **self-question**: Slice 3 에서 추가될 harness-factory Skill 의 트리거 키워드를 **scoped** ("harness blueprint, meta_factory, harness scaffold, 도메인 하네스 생성, harness-factory, agent/skill scaffold 설계") 로 한정하면, 기존 harness-audit / meta-retrospective / phase-start 의 키워드와 충돌(INDEX §5 "같은 키워드 둘 이상 = 충돌")을 회피할 수 있는가?
- **self-answer**:
  - **현 충돌 면 (INDEX 정독)**: ① harness-audit (#18) — "하네스 감사, 구조 점검, 전체 검토". ② meta-retrospective (#9) — "회고, 메타 개선, 반복 실패". ③ phase-start (#1) — "Phase 시작, 다음 phase, phase initiation". harness-factory 가 "하네스 개선" / bare "하네스 감사" / "phase 생성" 을 키워드로 가지면 즉시 충돌.
  - **scoping 전략 (non_goals §키워드 scoping)**: ⓐ **허용**(scoped): `harness blueprint` / `meta_factory` / `harness scaffold` / `도메인 하네스 생성` / `harness-factory` / `agent/skill scaffold 설계` — 모두 "새 하네스를 만든다/설계한다" 의미 영역, 기존 Skill 미소유. ⓑ **금지**(타 Skill 소유): `하네스 개선`/`메타 개선`/`회고`(→ meta-retrospective) + bare `하네스 감사`/`구조 점검`/`전체 검토`(→ harness-audit) + `phase 생성` 단독(→ phase-start).
  - **우선순위 (충돌 시)**: `harness-audit > harness-factory`(기존 하네스 점검이 새 하네스 생성보다 우선) + `contract-change > harness-factory`(Skill/contract 변경은 절차 우선) + `eval-run > harness-factory validation`(품질 평가 우선). 즉 경계 회색지대에서도 기존 Skill 이 상위.
  - **정합 근거**: ① INDEX §5 "같은 description 키워드 둘 이상 = 충돌 즉시 수정" 규율 + Skill 신규/변경 §1 "contract-change 절차 + §3 키워드 충돌 검토". harness-factory 는 "생성/설계" 동사 영역으로 분리되어 "감사/개선/회고" 동사 영역과 어휘적 비중첩. ② harness-factory 는 proposal-only(자동 적용 X) → harness-audit(점검) / meta-retrospective(개선 제안) 의 후행 단계가 아니라 별개 입구(새 하네스 생성). ③ 본 Slice 1 은 Skill 미작성 — scoping 설계 근거만 확정(실 등록은 Slice 3 harness-audit 충돌 검토 후).
  - **U1 검증 시점**: 실제 충돌 0 여부는 Slice 3 harness-audit Skill 의 키워드 충돌 검사로 최종 확정.
- **잠재 risk**:
  - "도메인 하네스 생성" 이 phase-start "다음 phase" 와 의미 인접 → harness-factory 는 "하네스(전체 구조)" 생성, phase-start 는 "phase(단일 단계)" 진입 — 대상 입자 크기 분리 + 우선순위 phase-start > harness-factory(절차) 명시.
  - 키워드 추가 유혹(scope creep)으로 "개선"/"감사" 흡수 → non_goals §금지 키워드 + Slice 3 충돌 검토로 차단.
- **권장**:
  - ADR-035 §Constraints + factory_contract 규칙 4 에 "harness-factory Skill 키워드 scoped (생성/설계 영역) — 하네스 개선/감사/회고 금지(타 Skill 소유)" 명시.
  - Slice 3 harness-audit Skill 로 harness-factory 키워드 충돌 0 검사 (U1 확정) + INDEX 우선순위 표 등록.

### V6. blueprint 실측 (golden_set 11, .claude/agents 부재, ADR-001~034, P-X1 47) — PASS

- **self-question**: 현재 하네스를 blueprint 로 역정리할 때(Slice 2) 추측이 아니라 **실측**(entry 확인 사실)을 단일 출처로 하며, 본 Slice 1 의 ADR-035 + validation 이 그 실측값(golden_set 11 / .claude/agents 부재 / ADR-001~034 / P-X1 47 / Skill 20 / MOA Supervisor)을 정확히 반영하는가?
- **self-answer**:
  - **실측 확인 (entry, R2)**: ① golden_set **11 케이스** (GS-001~GS-011, golden_set.md v1.0.0 §2 — Phase 9.5 에서 "47" 기재 정정 확정). ② `.claude/agents/` **부재** (glob 0 결과) → blueprint 부족점 "agent 자동 생성 없음 / Claude Code subagent 정의 디렉토리 미사용" 실측 근거. ③ ADR **ADR-001~034** 누적 (docs/decisions, phase_9_5_* 가 최신 ADR-033/034) → 다음 ADR-035. ④ P-X1 §SELF-VERIFICATION streak **47** (Phase 9.5 종료). ⑤ Skill **20개** (INDEX v1.2.0, 절차 14 + 검토/감사 6) → harness-factory 추가 시 21(Slice 3). ⑥ MOA orchestrator (`orchestration/moa_orchestrator.py::generate_plan`) = **Supervisor 패턴** (agent 간 직접 호출 금지, orchestrator 가 중개 — moa_policy §2 정합).
  - **architecture 매핑 실측 (moa_orchestrator 정독)**: ⓐ **Supervisor** = `generate_plan` 이 Intent → RAG → Planning → Critic → DB save 단계를 중개(agent 직접 호출 0). ⓑ **Fan-out/Fan-in** = `run_planning_parallel_3` + Critic `asyncio.gather` (3-plan + plan별 critic 병렬). ⓒ **Producer-Reviewer** = Planner(생성) → Critic(평가) → Rewriter(revise loop max 2). ⓓ **Pipeline** = Intent → RAG → Planning → Critic → Save → (Feedback). 모두 코드 실측 — architecture_patterns.md §Dreammate 매핑의 근거.
  - **blueprint 실측 원칙**: Slice 2 blueprint 는 위 실측값을 단일 출처로 역정리(추측 금지). 본 Slice 1 의 ADR-035 §Context + 본 validation §baseline 실측이 동일 수치를 명시 → Slice 2 와 drift 0.
  - **U4 검증 시점**: blueprint 역정리가 현재 하네스를 정확 반영하는지(실측 vs 문서 drift)는 Slice 2 blueprint 작성 시 최종 대조.
- **잠재 risk**:
  - entry plan 문서의 "47 케이스" 잔존 표기 → golden_set 11 로 정정 단일 출처 (Phase 9.5 정정 계승) + ADR-035 §Context 명시.
  - ADR 번호/P-X1 streak 등 수치 stale → 본 validation + ADR-035 가 실측 단일 출처, Slice 2 blueprint 가 이를 인용.
- **권장**:
  - ADR-035 §Context + References 에 실측값(golden_set 11 / .claude/agents 부재 / ADR-001~034 / P-X1 47 / Skill 20 / MOA Supervisor) 명시.
  - Slice 2 blueprint 는 실측 단일 출처(추측 금지) — golden_set 11 + .claude/agents 부재(부족점) + architecture 4 매핑.

## 종합 판정

**Phase M0 entry 허용 — 6/6 PASS (V1~V6)**

| ID | 항목 | 결과 | 후속 조치 |
|---|---|---|---|
| V1 | L3 Meta-Factory 도입 타당성 (기존 meta 문화 정합) | PASS | ADR-035 §Context (self_improvement_loop 상위 정식화) + §Constraints (payoff deferred, skeleton-only NG11) |
| V2 | 런타임 변경 0 (A9) | PASS | ADR-035 §Constraints (FastAPI/Next/Supabase 0줄 + git diff 게이트) + 매 Slice §SELF-VERIFICATION |
| V3 | proposal-first (자동 적용 X) | PASS | README ★ proposal-first 명시 + factory_contract 규칙 3/7 (outputs/proposals 먼저 + validation 전 active 아님) |
| V4 | meta-phase 격리 (제품 phase 오염 X) | PASS | PROJECT_STATE phase_m0_type: meta-phase + ADR-035 §Constraints (제품 phase 번호 분리, 규율 유지) |
| V5 | harness-factory Skill 키워드 scoping | PASS | ADR-035 §Constraints + factory_contract 규칙 4 (생성/설계 scoped, 개선/감사/회고 금지) — Slice 3 충돌 검토 (U1) |
| V6 | blueprint 실측 (golden_set 11 / .claude/agents 부재 / ADR-001~034 / P-X1 47) | PASS | ADR-035 §Context/References 실측값 명시 — Slice 2 blueprint 단일 출처 (U4) |

다음: Slice 2 sub-agent dispatch — generation_workflow + validation_workflow + templates(6) + blueprint(현재 하네스 실측 역정리) + outputs .gitkeep.

## 외부 검증 연계

self-validation 단일 모델 (Claude Code) 결과. 외부 검증 결과 (GPT/Gemini)는 `2026-05-31_phase-M0-pre-entry_external.md` placeholder 에 사용자가 외부 진행 후 채울 수 있음.

Phase M0 = L3 메타 레이어 도입(아키텍처 방향 결정) phase → 외부 검증 권장. 단 ★ meta-phase + 런타임 0 + proposal-first 로 위험이 낮고(런타임 회귀 불가능), Phase 4.5~9.5 패턴 계승으로 external placeholder 는 **사용자 외부 진행 권장** 형식 유지. self-validation V1~V6 PASS + self-strengthen V-form sub-pattern 가능성 명시. Phase M0 entry 진행 가능.

두 결과 차이 항목 발견 시:
- Phase M0 진행 중 `notes.md` 에 기록
- Slice 3 회고 §개선 제안 반영
- Critical 차이 (L3 도입 타당성 / proposal-first 경계 / Skill 키워드 충돌 등) 시 Slice 2 진입 전 사용자 알림

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 7 self: `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS — 네 번째 formal)
- Phase 8 self: `meta/validations/2026-05-29_phase-8-pre-entry_self.md` (V1~V7 PASS — 다섯 번째 formal)
- Phase 9 self: `meta/validations/2026-05-29_phase-9-pre-entry_self.md` (V1~V7 PASS — 여섯 번째 formal)
- Phase 9.5 self: `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` (V1~V7 PASS — 일곱 번째 formal)
- Phase M0 self: 본 문서 (V1~V6 PASS — ★ 여덟 번째 formal, 첫 meta-phase)
- Phase M0 external: `meta/validations/2026-05-31_phase-M0-pre-entry_external.md` (placeholder)

## Skill 트리거 기록

- **multi-llm-validation**: ★ 여덟 번째 formal 트리거 (Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째 + Phase 8 다섯째 + Phase 9 여섯째 + Phase 9.5 일곱째 + Phase M0 여덟째) → P-VALIDATION-FORMAL-001 정식 패턴 입증 강화 (8회 누적, 첫 meta-phase 적용)
- **phase-start**: 13번째 트리거 (Phase 1+2+3+4+4.5+6+5+5.5+7+8+9+9.5+M0)
- **qa-check**: meta-phase 경량 적용 (MVP 범위 위반 0 — 런타임 변경 0 + proposal-first 점검)
