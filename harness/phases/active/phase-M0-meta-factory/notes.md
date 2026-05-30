# Phase M0 — Notes (Meta-Factory Prep)

## Entry (2026-05-31)

- phase-start v1.3.0 §6 4점검 PASS (C1~C9, U1~U4)
- audit_naming PASS 0 drift
- Phase 9.5 baseline 유지 (pytest 339 + P-X1 47 + PlanCard 35 + component_map 45 + Skill 20)
- 3 Slice 모두 sub-agent dispatch
- ★ 본 phase는 **meta-phase** (제품 phase 아님) — 런타임 변경 0 (A9 핵심)

### 사용자 결정 (2026-05-31) — 반영
- **meta-phase (Phase M0, 3 Slice)** — PHASE_REGISTRY 제품 phase(10/11)와 번호 분리, archive/회고/P-X1 규율 유지
- **harness-factory Skill 추가** (proposal-only, 키워드 scoping)
- **Phase 9.5 push 후 진입** (완료 — 9bb1c36..fff913e)

### GPT 제안 평가 결론 (타당 + 진행 가능)
- 타당: 기존 meta 문화 정합 + 프로젝트 규율(proposal-first/런타임 0/contract-change) 100% 일치 + 저위험 + 즉시 가치(blueprint)
- caveat: C1 로드맵 분기(제품 아닌 메타-툴링 투자) / C2 YAGNI(payoff deferred, skeleton-only로 완화) / C3 Skill 키워드 충돌(scoping) / C4 phase 통합(meta-phase 격리)
- 정제(R1~R3): Skill 키워드 scoping / blueprint 실측 / meta-phase 격리

### entry 확인 사실
- `.claude/agents/` **부재** → blueprint 부족점 "agent 자동 생성 없음" 실측 근거 확정
- `meta_factory/` 신규 (충돌 0)
- golden_set 11 케이스 (47 아님, Phase 9.5 발견) — blueprint §7 실측

### 핵심 제약 (★)
- A9: FastAPI/Next.js/Supabase 런타임 변경 0줄 (git diff 게이트)
- proposal-first: 생성물 outputs/ 또는 meta/proposals/에 먼저
- harness-factory Skill 키워드: "harness blueprint/meta_factory/harness scaffold/도메인 하네스 생성" (— "하네스 개선"/bare "하네스 감사" 금지)

### Skill 추가
- harness-factory (proposal-only, Slice 3) — INDEX #21, 우선순위 harness-audit > harness-factory

## Slice 1~3 (작업 시 갱신)

### Slice 1 ✅ (2026-05-31, sub-agent — Pre-Entry + meta_factory 핵심 contract)

산출물 (8 작업 단위):
1. `meta/validations/2026-05-31_phase-M0-pre-entry_self.md` — V1~V6 PASS (★ 여덟 번째 formal, 첫 meta-phase)
   - V1 L3 도입 타당성 (self_improvement_loop 상위 정식화) / V2 런타임 0 (A9) / V3 proposal-first / V4 meta-phase 격리 / V5 harness-factory 키워드 scoping / V6 blueprint 실측 (golden_set 11 / .claude/agents 부재 / ADR-001~034 / P-X1 47)
2. `meta/validations/2026-05-31_phase-M0-pre-entry_external.md` — placeholder (사용자 외부 진행 권장)
3. `docs/decisions/phase_M0_meta_factory.md` — ADR-035 (L3 Meta-Factory 도입, L1/L2/L3 + proposal-first + payoff deferred + skeleton-only)
4. `meta_factory/README.md` — L1/L2/L3 모델 + ★ proposal-first 명시
5. `meta_factory/factory_contract.md` — 8 절대 규칙 (런타임 미변경 + proposal-first)
6. `meta_factory/domain_brief_schema.md` + `harness_blueprint_schema.md` — 생성 입력/출력 구조
7. `meta_factory/architecture_patterns.md` — 6 패턴 + Dreammate 매핑 (Supervisor=moa_orchestrator / Fan-out=3-plan / Producer-Reviewer=Planner→Critic→Rewriter / Pipeline=Intent→RAG→Planning→Critic→Save)
8. skill_usage_log (phase-start 13 + multi-llm-validation formal 여덟 + qa-check) + PROJECT_STATE (meta-phase 등록) + entry commit

★ A9 런타임 변경 0: backend/fastapi 0 / apps/web 0 (PlanCard·component_map 0줄) / db/migrations 0.
SELF-VERIFICATION (P-X1): forbidden 0 / 런타임 0 / 기존 contract·AGENTS·CLAUDE·기존 Skill·eval·이전 ADR 0.
baseline 불변 (런타임 무관): pytest 339 + P-X1 47 + PlanCard 35 + component_map 45 + Skill 20.

다음: Slice 2 (generation_workflow + validation_workflow + templates 6 + 현재 하네스 blueprint 실측 역정리 + outputs .gitkeep).

### Slice 2 (예정)

### Slice 3 (예정)
