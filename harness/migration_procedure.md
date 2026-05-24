# Harness Migration Procedure

> **목적**: GPT가 생성한 155-파일 하네스(골격 우수, 내용 빈약)와 우리 18-파일 deliverables(내용 깊지만 골격 부재)를 병합한다.
> **전략**: GPT 폴더 구조 + 라우팅을 골격으로 채택, 우리 깊은 contracts/skills를 콘텐츠로 이식.
> **수행 주체**: Claude Code(주력) + Codex(대량 작업) 교대.
> **버전**: v1.0.0 (이 문서도 contract-change Skill 적용 대상)

---

## 0. Quick Reference

```
GPT 하네스 위치   : /tmp/gpt_harness/video_planning_agent_full_harness_md_and_skills/
우리 deliverables : /mnt/user-data/outputs/
최종 하네스 위치  : (사용자가 결정, 예: ~/projects/video-planning-agent/)

이식 후 예상 줄 수: 약 9,000–12,000줄
이식 후 예상 파일: 약 160–170개
```

---

## 1. 사전 점검 (Pre-flight)

이식 시작 전 반드시 확인:

### 1-1. 백업
```
✅ GPT 하네스 원본 보관 (zip 그대로 보존)
✅ 우리 deliverables 보관 (/mnt/user-data/outputs/ 그대로)
✅ 작업 폴더는 별도 (병합 도중 충돌 발생 시 rollback 가능하게)
```

### 1-2. 충돌 미리 식별
```
🚨 우리 design.md 688줄 vs GPT design.md 163줄 → Discovery+Quick 분기 부재
🚨 우리 db_schema.md 580줄 vs GPT db_schema.md 80줄 → 12+ 테이블 차이
🚨 우리 prompt_registry.md 628줄 vs GPT 8줄 → 사실상 대체
🚨 25 Skill vs 14 Skill → 매핑 필요 (Section 3)
🚨 GPT에 apps/mobile, backend/spring 미리 존재 → MVP scope 위반
```

### 1-3. 미결정 항목 (Sprint S0 진입 전 강제 결정)

다음 항목은 **Sprint S0 첫 작업 전 반드시 확정**. 미결정 상태로 진입 시 작업 중단.

```
🔴 결정 마감 = Sprint S0 시작 전
  - HARNESS_ROOT 최종 경로 (절대경로, 예: ~/projects/video-planning-agent/)
  - 기존 폴더 덮어쓰기 vs 새 폴더 (충돌 시 어느 쪽 우선)

✅ 이미 확정
  - .agents/.claude 분리 유지 (이전 결정 변경)
  - Skill 총 개수 = 20개
  - agent.html 폴더 위치 = tools/agent-html/

🟡 결정 마감 = Sprint S3 시작 전
  - 우선 보강 8 contract 중 첫 작업 순서
  - placeholder marker 적용 범위 (전 16개인지, 일부만 보강 후 placeholder인지)

🟢 결정 마감 = Sprint S5 시작 전
  - Phase 0 acceptance 최종 항목 (11.7절 참고)
```

**위 미결정 항목은 Section 11.1에서 보강 결정 제시.**

---

## 2. Skill 25 ↔ 14 비교 분석

### 2-1. GPT의 25 Skill 역할 (인덱스)

#### `.agents/skills/` (15개, 구현형 모델용)

| # | Skill | 명목상 역할 (1줄 purpose) |
|---|---|---|
| 1 | agent-io-check | Agent IO 계약 준수 점검 |
| 2 | bug-triage | 버그 분류·재현·심각도 판정 |
| 3 | contract-change | contracts 변경 제안서 작성 |
| 4 | cost-review | LLM 호출 비용·토큰 검토 |
| 5 | design-review | apps/web/design.md 기준 검토 |
| 6 | docs-sync | 코드-문서 동기화 |
| 7 | eval-run | golden_set 등 평가 실행 |
| 8 | meta-retrospective | 회고 작성 |
| 9 | phase-complete | Phase 종료 정리 |
| 10 | phase-start | Phase 시작 컨텍스트 구성 |
| 11 | product-scope-review | MVP 범위 위반 점검 |
| 12 | qa-check | QA 게이트 점검 |
| 13 | rag-update | RAG 지식 추가/승격 |
| 14 | release-gate | 배포 직전 최종 점검 |
| 15 | security-review | 보안 점검 |

#### `.claude/skills/` (10개, 기획/설계형 모델용)

| # | Skill | 명목상 역할 |
|---|---|---|
| 16 | ai-architecture-review | AI 시스템 아키텍처 검토 |
| 17 | docs-design | 문서 구조 설계 |
| 18 | eval-design | 평가 체계 설계 (≠ eval-run) |
| 19 | frontend-design-review | 프론트 디자인 설계 검토 |
| 20 | harness-audit | 하네스 전체 감사 |
| 21 | meta-retrospective | 회고 작성 (★ .agents 중복) |
| 22 | phase-review | Phase 진행 중 검토 |
| 23 | planning-phase-create | 새 Phase 계획 생성 |
| 24 | product-scope-review | MVP 범위 점검 (★ .agents 중복) |
| 25 | rag-design | RAG 시스템 설계 (≠ rag-update) |

**중복 발견**: meta-retrospective, product-scope-review가 양쪽 폴더에 있음 → 충돌. 한쪽 제거 필요.

### 2-2. 우리 14 Skill 역할

| # | Skill | 역할 | 줄 수 |
|---|---|---|---|
| 1 | phase-start | Phase 진입 컨텍스트 구성 | 150 |
| 2 | phase-complete | Phase 종료 + **docs-sync 흡수** | 221 |
| 3 | contract-change | contracts/skills 변경 제안 절차 | 223 |
| 4 | bug-triage | 9 카테고리 분류 + 심각도 | 195 |
| 5 | rag-update | 5단계 승격 파이프라인 | 232 |
| 6 | eval-run | 5종 평가 실행 + 임계값 | 233 |
| 7 | qa-check | 9 카테고리 점검 + **release-gate 흡수** | 234 |
| 8 | cost-review | 5 단위 분석 + 4 시나리오 | 273 |
| 9 | meta-retrospective | 4종 회고 + 5 Whys | 246 |
| 10 | design-review | 13 카테고리 점검 | 224 |
| 11 | security-review | 10 영역 점검 + 인젝션 테스트 | 271 |
| 12 | prompt-version-review | semver + 회귀 + A/B | 222 |
| 13 | multi-llm-validation | 3 모델 교차검증 워크플로 | 252 |
| 14 | context-compact | 세션 압축 + handoff | 270 |

### 2-3. 겹침 매트릭스 (가장 중요한 표)

| GPT Skill | 우리 매칭 Skill | 매핑 결정 | 이유 |
|---|---|---|---|
| **A1. agent-io-check** | 없음 | 🆕 **GPT 유지** | agent-io 단독 점검은 가치 있음. 우리는 phase-complete의 docs-sync에 일부만 포함. 별도 유지가 명확. |
| A2. bug-triage | ✅ bug-triage | 🔄 **우리로 교체** | 우리 9 카테고리가 GPT 1줄보다 깊음 |
| A3. contract-change | ✅ contract-change | 🔄 **우리로 교체** | 우리 절차가 4-1/4-2/4-3 분기 등 완성 |
| A4. cost-review | ✅ cost-review | 🔄 **우리로 교체** | 우리 5 단위 + 4 시나리오 완성 |
| A5. design-review | ✅ design-review | 🔄 **우리로 교체** | 우리 13 카테고리 완성, GPT는 stub |
| A6. docs-sync | (phase-complete에 흡수) | 🔄 **우리 결정 유지** | 별도 운영하면 phase-complete와 중복 호출됨 |
| A7. eval-run | ✅ eval-run | 🔄 **우리로 교체** | 우리 5종 평가 + 임계값 완성 |
| A8. meta-retrospective | ✅ meta-retrospective | 🔄 **우리로 교체 + .claude만 유지** | 회고는 분석 작업이므로 .claude 적합 |
| A9. phase-complete | ✅ phase-complete | 🔄 **우리로 교체** | 우리 8단계 + docs-sync 흡수 |
| A10. phase-start | ✅ phase-start | 🔄 **우리로 교체** | 우리 7단계 절차 완성 |
| **A11. product-scope-review** | (qa-check 카테고리1) | ⛔ **흡수·폐기** | qa-check.카테고리1 = MVP 범위 점검과 100% 동일 |
| A12. qa-check | ✅ qa-check | 🔄 **우리로 교체** | 우리 9 카테고리 + release-gate 흡수 |
| A13. rag-update | ✅ rag-update | 🔄 **우리로 교체** | 우리 5단계 파이프라인 완성 |
| A14. release-gate | (qa-check에 흡수) | ⛔ **흡수·폐기** | qa-check와 트리거·절차 거의 동일 |
| A15. security-review | ✅ security-review | 🔄 **우리로 교체** | 우리 10 영역 완성 |
| **C16. ai-architecture-review** | 없음 | 🆕 **GPT 유지** | AI 구조 단독 검토는 가치 있음. 재작성 필요. |
| C17. docs-design | 없음 | ⛔ **폐기** | 너무 광범위. contract-change로 충분. |
| **C18. eval-design** | 없음 | 🆕 **GPT 유지** | 평가 체계 *설계* (≠ 실행). 재작성 필요. |
| C19. frontend-design-review | (design-review에 흡수) | ⛔ **흡수·폐기** | design-review가 프론트 검토 포함 |
| **C20. harness-audit** | (meta-retrospective Type 4) | 🆕 **GPT 유지 + 차별화** | 하네스 단독 감사는 회고 type 4보다 빈도 다름. 별도 유지. |
| C21. meta-retrospective | ✅ meta-retrospective | 🔄 **우리로 교체** | 우리 246줄 vs GPT 29줄 템플릿 |
| **C22. phase-review** | 없음 | 🆕 **GPT 유지** | Phase 진행 중 검토 (≠ start/complete). 재작성 필요. |
| C23. planning-phase-create | (phase-start에 흡수 검토) | ⚠️ **재검토** | phase-start와 차별화 어렵지만 새 Phase 생성은 더 무거운 작업 |
| C24. product-scope-review | (qa-check 카테고리1) | ⛔ **흡수·폐기** | A11과 동일 사유 |
| **C25. rag-design** | 없음 | 🆕 **GPT 유지** | RAG *설계* (≠ 운영 갱신). 재작성 필요. |
| 없음 | ✅ prompt-version-review | ➕ **우리 추가** | GPT 부재. agents+claude 양쪽 적용. |
| 없음 | ✅ multi-llm-validation | ➕ **우리 추가** | GPT 부재. .claude 적용. |
| 없음 | ✅ context-compact | ➕ **우리 추가** | GPT 부재. .claude 적용. |

### 2-4. 최종 Skill 목록 (병합 후)

#### `.agents/skills/` — 11개

```
✅ 우리 버전 이식 (10개):
  1. phase-start
  2. phase-complete (docs-sync 흡수)
  3. contract-change
  4. bug-triage
  5. rag-update
  6. eval-run
  7. qa-check (release-gate 흡수)
  8. cost-review
  9. security-review
  10. prompt-version-review     ← 신규

🆕 GPT에서 가져와 재작성 (1개):
  11. agent-io-check

⛔ 폐기 (3개):
  docs-sync (#A6, phase-complete에 흡수)
  product-scope-review (#A11, qa-check에 흡수)
  release-gate (#A14, qa-check에 흡수)
  meta-retrospective (#A8, .claude로만 이전)
```

#### `.claude/skills/` — 9개

```
✅ 우리 버전 이식 (4개):
  1. design-review
  2. meta-retrospective
  3. multi-llm-validation        ← 신규
  4. context-compact             ← 신규

🆕 GPT에서 가져와 재작성 (5개):
  5. ai-architecture-review
  6. eval-design
  7. harness-audit
  8. phase-review
  9. rag-design

⛔ 폐기 (4개):
  docs-design (#C17, contract-change로 충분)
  frontend-design-review (#C19, design-review에 흡수)
  product-scope-review (#C24, qa-check에 흡수)
  planning-phase-create (#C23, phase-start로 흡수 검토 — 추후 결정)

⚠️ 보류:
  planning-phase-create는 일단 .claude/skills/에 빈 파일로 두고
  실제 새 Phase 생성 빈도 측정 후 phase-start 흡수 여부 결정
```

#### 합계

```
.agents/ 11개 + .claude/ 9개 = 20개
(원래 GPT 25, 우리 14 → 병합 20)

폐기: 7개 (GPT 중복/흡수 대상)
신규: 8개 (우리 3 + GPT 5 재작성)
대체: 14개 (우리 깊은 버전으로 교체)
```

---

## 3. 파일별 결정 매트릭스

### 3-1. 최상위 라우팅 파일

| 파일 | 결정 | 조치 |
|---|---|---|
| `00_START_HERE.md` | ✅ 채택 | GPT 그대로. Discovery+Quick 분기 1줄 추가 |
| `CLAUDE.md` | ✅ 채택 + 갱신 | 우리 Skill 13~14 라우팅 추가 |
| `AGENTS.md` | ✅ 채택 + 갱신 | prompt-version-review 라우팅 추가 |
| `HANDOFF.md` | ✅ 채택 | multi-llm-validation 연동 메모 추가 |
| `PROJECT_STATE.md` | ✅ 채택 + 갱신 | 우리 결정 사항 반영 (Discovery+Quick, 14→20 Skill) |
| `PHASE_REGISTRY.md` | ✅ 채택 + 갱신 | Phase 2~3에 Discovery+Quick 분기 반영 |
| `00_gap_assessment.md` | ✅ 보존 (참고용) | 갱신 안 함. 역사적 기록. |
| `10_CLAUDE_CROSS_VALIDATION_PROMPT.md` | ✅ 채택 + 갱신 | multi-llm-validation Skill과 통합 |
| `instruction_index/catalog.yaml` | ✅ 채택 + 갱신 | 우리 contracts 추가 |
| `instruction_index/routes.yaml` | ✅ 채택 + 갱신 | 13~14 Skill 라우팅 추가 |
| `instruction_index/dependency_map.yaml` | ✅ 채택 + 갱신 | 우리 contracts 의존성 추가 |
| `instruction_index/priority_rules.md` | ✅ 채택 | 그대로 |

### 3-2. Core Contracts

| 파일 | 결정 | 조치 |
|---|---|---|
| `docs/contracts/db_schema.md` | 🔄 교체 | GPT 80줄 → 우리 580줄 |
| `docs/contracts/output_schema.md` | ⚠️ 통합 | GPT 73줄 기반 + 우리 명세 보강. 차기 세션 작성. |
| `docs/contracts/api_contract.md` | ⚠️ 보강 | GPT 54줄 → 우리 깊은 버전 (차기 세션) |
| `docs/contracts/agent_io_contract.md` | ⚠️ 보강 | GPT 69줄 → 우리 깊은 버전 (차기 세션) |
| `docs/contracts/mvp_non_goals.md` | ✅ 채택 | GPT 24줄 적정. 큰 변경 없음. |

### 3-3. Stub Contracts (9줄 짜리 16개)

```
🟡 placeholder marker로 변환 (실제 작성은 phase별로 미룸):

accessibility_contract.md     → "Phase 9에서 작성" marker
backend_boundary.md           → 채택 (간결 의도적)
data_contract.md              → 채택 (간결 의도적)
data_retention_policy.md      → "Phase 4 (auth) 작성" marker
env_contract.md               → 채택 (간결 의도적)
error_response_contract.md    → 🔴 우선 보강 (Phase 1 필수)
event_log_contract.md         → "Phase 4 작성" marker
frontend_boundary.md          → 채택 (간결 의도적)
frontend_design_contract.md   → 🔴 우리 design.md로 보강
llm_security_contract.md      → 🔴 우선 보강 (security-review 의존)
privacy_contract.md           → "Phase 4 작성" marker
product_boundary.md           → 채택 (간결 의도적)
rag_data_contract.md          → 🔴 우선 보강 (Phase 7 필수)
rate_limit_policy.md          → 🔴 우선 보강 (cost-review 의존)
tech_stack_contract.md        → 채택
user_consent_contract.md      → "Phase 4 작성" marker
```

`marker` 형식 (placeholder 파일):

```markdown
# {contract-name}

## 상태

🚧 Placeholder (Phase X에서 작성 예정)

## 작성 트리거

이 contract는 다음 시점에 작성된다:
- Phase {X} 진입 시 phase-start Skill이 contract-change Skill을 호출
- 또는 관련 Skill ({skill-name})이 처음 트리거될 때

## 잠정 원칙 (Phase {X} 전까지)

{1–3줄로 기본 원칙만}

## 미정 항목

- 항목 1
- 항목 2
```

이렇게 두면 "9줄 stub인데 가짜 깊이 있어 보이는" 문제 해결.

### 3-4. Frontend Design

| 파일 | 결정 | 조치 |
|---|---|---|
| `apps/web/design.md` | 🔄 교체 | GPT 163줄 → 우리 688줄 (Discovery+Quick) |
| `apps/web/page_map.md` | ✅ 채택 + 갱신 | GPT 12줄 골격 + 우리 design.md §6 페이지 매핑 |
| `apps/web/component_map.md` | ✅ 채택 + 갱신 | GPT 17줄 골격 + 우리 design.md §7 컴포넌트 매핑 |
| `apps/mobile/design.md` | 🟡 placeholder | "Phase 21+ Expo migration" marker로 |
| `apps/mobile/README.md` | 🟡 placeholder | 동일 |

### 3-5. Backend

| 파일 | 결정 | 조치 |
|---|---|---|
| `backend/fastapi/README.md` | ✅ 보강 | 의존성, 실행 방법, 디렉터리 구조 추가 |
| `backend/spring/README.md` | 🟡 placeholder | "Phase 21+" marker로 |

### 3-6. AI System

| 파일 | 결정 | 조치 |
|---|---|---|
| `ai_system/architecture.md` | ✅ 보강 | MOA Lite (Intent/Planner/Critic/Rewriter) 다이어그램 추가 |
| `ai_system/orchestration/flow.md` | ✅ 보강 | 우리 prompt_registry의 P-001~P-008 흐름과 정합 |
| `ai_system/orchestration/moa_policy.md` | ✅ 보강 | Critic revise 최대 2회 등 우리 절차 반영 |
| `ai_system/orchestration/cost_control_policy.md` | ✅ 보강 | 우리 cost-review Skill 임계값 반영 |
| `ai_system/orchestration/fallback_policy.md` | ✅ 보강 | 실패 시 부분 결과 보존 절차 |
| `ai_system/orchestration/service_boundary.md` | ✅ 채택 | 현재 골격 적정 |
| `ai_system/prompts/prompt_registry.md` | 🔄 교체 | GPT 8줄 → 우리 628줄 |
| `ai_system/agents/{6개}.md` | ✅ 보강 | 각각 우리 prompt P-001~P-008과 정합 |
| `ai_system/memory/*.md` | ✅ 보강 | brand_memory_entries, candidate_knowledge 5단계 반영 |

### 3-7. Knowledge / RAG

| 파일 | 결정 | 조치 |
|---|---|---|
| `knowledge/rag/promotion_rule.md` | 🔄 교체 | 우리 rag-update Skill의 5단계 파이프라인으로 |
| `knowledge/rag/retrieval_policy.md` | ✅ 보강 | top_k, isolation, brand_id 필터 추가 |
| `knowledge/rag/quality_filter.md` | ✅ 보강 | 우리 rag-update Step 2 자동 검사 항목 |
| `knowledge/rag/metadata_schema.md` | ✅ 보강 | source_kind enum 등 우리 db_schema와 정합 |
| `knowledge/rag/chunking_policy.md` | ✅ 보강 | 500–800 토큰 + 100 overlap |
| `knowledge/rag/custom_rag_plan.md` | ✅ 채택 | Phase 21+ 확장 계획 |
| `knowledge/rag/sdk_rag_policy.md` | ✅ 채택 | placeholder |
| `knowledge/rag/sources.md` | 🟡 placeholder | "Phase 7 작성" marker |
| `knowledge/llm_wiki/{6개}.md` | 🟡 placeholder | "Phase 7 작성" marker |
| `knowledge/datasets/{4개}.md` | 🟡 placeholder | "Phase 7+" marker |

### 3-8. Eval

| 파일 | 결정 | 조치 |
|---|---|---|
| `eval/golden_set.md` | 🔄 교체 + 시드 | 우리 eval-run Skill 케이스 선정 기준 + 시드 10케이스 작성 |
| `eval/video_planning_eval.md` | ✅ 보강 | 우리 8 차원 + Critic P-007 정합 |
| `eval/hook_quality_eval.md` | ✅ 보강 | 3초 시선 유지 등 우리 design.md §5 기준 |
| `eval/human_review_rubric.md` | ✅ 보강 | 5점 척도 + 표준편차 |
| `eval/design_review_checklist.md` | 🔄 교체 | 우리 design-review Skill 13 카테고리 (Skill 본문 안) |
| `eval/security_eval.md` | 🔄 교체 | 우리 security-review Skill 10 영역 (Skill 본문 안) |
| `eval/failure_taxonomy.md` | 🔄 교체 | 우리 bug-triage Skill 9 카테고리 |
| `eval/regression_eval.md` | ✅ 보강 | 우리 prompt-version-review 4단계 |
| `eval/confidence_score.md` | ✅ 보강 | output_schema의 confidence 필드 정의 |
| `eval/accessibility_checklist.md` | ✅ 보강 | 우리 design-review 카테고리 11 |
| `eval/brand_consistency_eval.md` | ✅ 보강 | 8 차원 중 brand_consistency |
| `eval/execution_feasibility_eval.md` | ✅ 보강 | 8 차원 중 feasibility |
| `eval/target_fit_eval.md` | ✅ 보강 | 8 차원 중 target_clarity |
| `eval/ux_eval.md` | ✅ 보강 | UX 정성 평가 절차 |
| `eval/phase_eval.md` | ✅ 보강 | Phase별 acceptance 측정 절차 |

### 3-9. Product

| 파일 | 결정 | 조치 |
|---|---|---|
| `product/vision.md` | ✅ 보강 | 영상기획 (≠ 제작) 비전 |
| `product/positioning.md` | ✅ 보강 | 경쟁사 대비 포지셔닝 |
| `product/mvp_scope.md` | ✅ 보강 | 우리 design.md §17와 정합 |
| `product/target_users.md` | ✅ 보강 | 페르소나 3종 |
| `product/user_scenarios.md` | ✅ 보강 | Discovery + Quick 양 시나리오 |
| `product/pricing_model.md` | 🟡 placeholder | "Phase 11+ 작성" marker |
| `product/roadmap.md` | ✅ 보강 | PHASE_REGISTRY와 정합 |

### 3-10. Phases

| 파일 | 결정 | 조치 |
|---|---|---|
| `phases/active/phase_1_mvp_basic_flow.md` | ✅ 보강 | acceptance 항목 명세, Discovery+Quick 흐름 반영 |
| `phases/planned/expo_migration_plan.md` | ✅ 채택 | Phase 21+ |
| `phases/planned/java_migration_plan.md` | ✅ 채택 | Phase 21+ |
| `phases/planned/moa_expansion_plan.md` | ✅ 채택 | Phase 11+ |
| `phases/planned/observability_expansion_plan.md` | ✅ 채택 | Phase 12+ |
| `phases/planned/pwa_mvp_plan.md` | ✅ 보강 | Discovery+Quick 분기 반영 |
| `phases/planned/rag_customization_plan.md` | ✅ 채택 | Phase 21+ |

### 3-11. Meta / Logs

| 파일 | 결정 | 조치 |
|---|---|---|
| `meta/error_taxonomy.md` | 🔄 교체 | 우리 bug-triage 9 카테고리 |
| `meta/guardrails.md` | ✅ 채택 + 보강 | 우리 Skill의 금지 사항 종합 |
| `meta/harness_improvement_proposals.md` | ✅ 채택 | meta/proposals/ 인덱스 역할 |
| `meta/human_review_policy.md` | ✅ 보강 | rag-update Step 3 사람 검토 절차 |
| `meta/lessons_learned.md` | ✅ 채택 | meta-retrospective 누적 |
| `meta/meta_summary.md` | ✅ 채택 | 메타 활동 요약 |
| `meta/rollback_policy.md` | ✅ 보강 | 우리 rag-update / prompt-version-review의 rollback 절차 |
| `meta/self_improvement_loop.md` | ✅ 채택 | 우리 meta-retrospective Type 1~4와 정합 |
| `logs/decision_log.md` | ✅ 채택 | 운영 시작 후 누적 |
| `logs/eval_log.md` | ✅ 채택 | eval-run 산출물 누적 |
| `logs/handoff_log.md` | ✅ 채택 | multi-llm-validation 산출물 누적 |
| `logs/log_index.md` | ✅ 채택 | logs/ 인덱스 |

### 3-12. Packages (Monorepo)

| 폴더 | 결정 |
|---|---|
| `packages/api-client/` | ✅ 보강 README (Phase 4에서 구현) |
| `packages/shared-types/` | ✅ 보강 README (Phase 1부터 사용) |
| `packages/shared-utils/` | ✅ 보강 README (Phase 4에서 구현) |

### 3-13. Tests

| 파일 | 결정 | 조치 |
|---|---|---|
| `tests/regression_checklist.md` | ✅ 보강 | 우리 qa-check smoke test 시나리오 + golden_set 정합 |
| `tests/smoke_test_checklist.md` | ✅ 보강 | 우리 qa-check 9 카테고리 |
| `tests/test_index.md` | ✅ 채택 | 테스트 인덱스 |

### 3-14. 우리 deliverables 중 신규 위치

| 우리 산출물 | 최종 위치 |
|---|---|
| `agent_html_spec.md` | `tools/agent_html_spec.md` (신규) |
| (다음 세션 산출물들) | 각 contracts/ 위치 |

---

## 4. 이식 순서 (5 Sprint)

### Sprint S0: 라우팅 + 상태 (1 세션, Claude Code 단독)

```
순서:
  1. GPT 하네스 전체를 작업 폴더로 복제
  2. 00_START_HERE.md 갱신 (Discovery+Quick 1줄 추가)
  3. PROJECT_STATE.md 갱신 (우리 결정 반영)
  4. PHASE_REGISTRY.md 갱신 (Phase 2~3 Discovery+Quick 분기)
  5. CLAUDE.md, AGENTS.md 갱신 (신규 Skill 라우팅)
  6. instruction_index/catalog.yaml, routes.yaml, dependency_map.yaml 갱신

산출물 검증:
  ✅ instruction_index/routes.yaml에 prompt-version-review, 
     multi-llm-validation, context-compact 라우팅 존재
  ✅ PHASE_REGISTRY에 Discovery+Quick 분기가 Phase 2~3에 등록
  ✅ PROJECT_STATE의 current_phase가 active
```

### Sprint S1: 우리 Core 3개 이식 (1 세션, Claude Code)

```
순서:
  1. apps/web/design.md GPT 163줄 → 우리 688줄 교체
  2. docs/contracts/db_schema.md GPT 80줄 → 우리 580줄 교체
  3. ai_system/prompts/prompt_registry.md GPT 8줄 → 우리 628줄 교체
  4. apps/web/page_map.md, component_map.md 갱신 (design.md와 정합)

산출물 검증:
  ✅ design.md §6, §7과 page_map, component_map 정합
  ✅ db_schema의 candidate_knowledge 5단계 status 명시
  ✅ prompt_registry P-001~P-008 + P-AUX 전부 존재
  ✅ instruction_index/dependency_map.yaml에 의존성 추가
```

### Sprint S2: Skill 25 → 20 정리 (1~2 세션, Claude Code + Codex 교대)

```
순서 (Claude Code 주력):
  1. .agents/skills/ 폐기 4개 삭제 
     (docs-sync, product-scope-review, release-gate, meta-retrospective)
  2. .claude/skills/ 폐기 4개 삭제
     (docs-design, frontend-design-review, product-scope-review, planning-phase-create)
  3. 우리 14 Skill을 적절한 폴더에 배치 (단순 복사 작업, Codex 적합)
  4. agent-io-check, ai-architecture-review, eval-design, 
     harness-audit, phase-review, rag-design 6개 GPT 신규 Skill 재작성
     (각 우리 Skill 템플릿 형식 따라 깊게 - Claude Code)

산출물 검증:
  ✅ .agents/skills/ 11개, .claude/skills/ 9개 = 20개
  ✅ 각 SKILL.md가 우리 형식 (YAML frontmatter + 절차 + 금지)
  ✅ description 키워드 충돌 검사 (INDEX.md 작성)
  ✅ applies_to 태그 모든 Skill에 존재
```

### Sprint S3: 핵심 Contract 보강 (1~2 세션, Claude Code)

```
순서:
  1. docs/contracts/output_schema.md (GPT 73줄 → 300줄 깊은 버전)
  2. docs/contracts/agent_io_contract.md (GPT 69줄 → 350줄)
  3. docs/contracts/api_contract.md (GPT 54줄 → 400줄)
  4. docs/contracts/error_response_contract.md (9줄 → 보강)
  5. docs/contracts/llm_security_contract.md (9줄 → 보강)
  6. docs/contracts/rate_limit_policy.md (9줄 → 보강)
  7. docs/contracts/rag_data_contract.md (9줄 → 보강)
  8. docs/contracts/frontend_design_contract.md (9줄 → 보강)
  
  나머지 9줄 contracts는 placeholder marker로 변환 (Codex 일괄 작업)

산출물 검증:
  ✅ 핵심 8 contracts가 200줄 이상
  ✅ 다른 9줄 stub은 placeholder marker 명시
  ✅ Skill들이 참조하는 contract가 모두 존재
```

### Sprint S4: eval, knowledge, ai_system 보강 (1~2 세션, Codex 주력)

```
순서:
  1. eval/golden_set.md (15줄 → 250줄, 시드 10케이스 - Claude Code)
  2. eval/{14개 3줄 파일} 보강 (Codex 일괄)
  3. knowledge/rag/{8개 3줄 파일} 보강 (Codex)
  4. knowledge/llm_wiki/{6개} placeholder marker (Codex)
  5. ai_system/agents/{6개 9줄 파일} 보강 (Claude Code)
  6. ai_system/orchestration/{5개} 보강 (Claude Code)
  7. ai_system/memory/{5개} 보강 (Claude Code)

산출물 검증:
  ✅ golden_set 케이스 10개 이상
  ✅ 모든 eval 파일이 30줄 이상 또는 placeholder marker
  ✅ ai_system/agents가 각각 prompt_registry의 P-XXX와 매핑
```

### Sprint S5: 보조 파일 + 최종 검증 (1 세션)

```
순서:
  1. product/{7개} 보강
  2. phases/active/phase_1_mvp_basic_flow.md 갱신
  3. phases/planned/{6개} 갱신
  4. meta/{9개} 보강
  5. tests/{3개} 보강
  6. packages/{3개 README} 보강
  7. tools/agent_html_spec.md 신규 추가

최종 검증:
  ✅ harness-audit Skill 1회 실행 (전체 감사)
  ✅ instruction_index/routes.yaml에 모든 작업 유형 매핑
  ✅ 9줄 stub이 0개 (모두 placeholder marker 또는 보강 완료)
  ✅ 모든 Skill의 related_contracts가 실재
  ✅ PHASE_REGISTRY에 Phase 1 acceptance가 5개 이상 구체적 항목
```

---

## 5. Claude Code vs Codex 작업 분배

### Claude Code (주력) — 추론 + 명세 일관성

```
✅ 적합 작업:
  - 신규 Skill 작성 (agent-io-check, ai-architecture-review 등 6개)
  - 깊은 Contract 작성 (output_schema, agent_io, api)
  - design.md → page_map/component_map 정합 작업
  - prompt_registry → ai_system/agents 매핑
  - 의존성 분석 (instruction_index/dependency_map)
  - harness-audit 최종 실행

작업 단위: 1 세션당 2~5 파일 (깊이 위주)
```

### Codex (보조) — 빠른 일괄 작업

```
✅ 적합 작업:
  - 우리 14 Skill 파일 단순 복사·배치
  - 9줄 stub 16개를 placeholder marker로 일괄 변환
  - 3줄 eval 파일들 일괄 보강 (템플릿 따라)
  - YAML frontmatter 일괄 추가
  - 깨진 링크 검사
  - frontmatter 형식 통일

작업 단위: 1 세션당 10~30 파일 (양 위주)
```

### Copilot Code (보조 2) — Claude 계열

```
✅ 적합 작업:
  - Claude Code가 만든 Skill의 검토
  - meta-retrospective 작성 (회고는 Claude 계열 강점)
  - multi-llm-validation 워크플로 실제 실행 (3 모델 중 1)
  - 보안 영역 보수적 검토

작업 단위: 라운드 로빈 (3rd round마다)
```

### 교대 룰

```
Round 1: Claude Code (Sprint S0, S1)
Round 2: Codex (Sprint S2의 단순 복사 부분)
Round 3: Claude Code (Sprint S2의 신규 Skill 작성)
Round 4: Codex (Sprint S3의 placeholder 일괄 작업)
Round 5: Claude Code (Sprint S3의 깊은 contract)
Round 6: Copilot Code (Sprint S4의 검토)
Round 7: Codex (Sprint S5의 일괄 보강)
Round 8: Claude Code (최종 harness-audit)

큰 결정은 multi-llm-validation Skill로 3 모델 동시 검토.
```

---

## 6. 검증 체크포인트

각 Sprint 종료 시 다음 통과:

### S0 후
```
[ ] PROJECT_STATE.md의 confirmed_decisions에 우리 결정 25개 명시
[ ] PHASE_REGISTRY.md의 Phase 2~3가 Discovery+Quick 반영
[ ] CLAUDE.md, AGENTS.md에 신규 Skill 3개 라우팅 추가
[ ] instruction_index/routes.yaml 갱신 검증
```

### S1 후
```
[ ] apps/web/design.md가 688줄 (우리 버전 그대로)
[ ] docs/contracts/db_schema.md가 580줄
[ ] ai_system/prompts/prompt_registry.md가 628줄
[ ] page_map, component_map이 design.md §6, §7과 정합
```

### S2 후
```
[ ] Skill 총 개수 = 20
[ ] 각 Skill에 YAML frontmatter (name, description, applies_to, version)
[ ] description 키워드 충돌 없음 (수동 검사)
[ ] phase-start, contract-change, rag-update가 우리 깊은 버전
[ ] agent-io-check, ai-architecture-review 등 6개 신규 Skill 작성 완료
```

### S3 후
```
[ ] output_schema.md ≥ 300줄
[ ] agent_io_contract.md ≥ 350줄
[ ] api_contract.md ≥ 400줄
[ ] 9줄 stub 중 보강 8개 + placeholder 8개
[ ] 모든 Skill의 related_contracts 파일이 실존
```

### S4 후
```
[ ] eval/golden_set.md 케이스 ≥ 10
[ ] eval/ 모든 파일 ≥ 30줄
[ ] ai_system/agents/ 모든 정의 prompt_registry와 매핑
[ ] ai_system/orchestration/ 모든 정책 cost-review와 정합
```

### S5 후
```
[ ] harness-audit Skill 실행 결과: 0 critical, 0 high issue
[ ] product/, meta/, tests/, packages/ 모두 placeholder 외 보강
[ ] tools/agent_html_spec.md 위치 확정
[ ] 9줄 stub = 0개
```

---

## 7. Rollback 방안

각 Sprint마다 git commit 단위 분리:

```
Sprint S0 → commit "harness: integrate GPT skeleton + routing decisions"
Sprint S1 → commit "harness: replace core 3 contracts with deep versions"
Sprint S2 → commit "harness: consolidate skills 25→20"
Sprint S3 → commit "harness: deepen 8 priority contracts"
Sprint S4 → commit "harness: enrich eval/knowledge/ai_system"
Sprint S5 → commit "harness: complete migration, final audit"
```

각 commit 후 새 작업 시작 전 검증 체크포인트 통과 확인. 실패 시 직전 commit으로 reset.

---

## 8. 충돌 해결

이식 도중 발생 가능한 충돌:

### 충돌 1: Mobile/Spring 폴더 처리

```
GPT: apps/mobile/, backend/spring/ 미리 존재
우리: Phase 21+ 제외 결정

해결: 폴더는 유지하되 모든 파일을 placeholder marker로 변환.
      Phase 21+ 진입 시 작성 트리거.
```

### 충돌 2: design.md 흐름 차이

```
GPT: 단일 흐름 (입력 → 의도 분석 → 한 줄 방향 승인 → 생성 → 검증)
우리: 하이브리드 (Discovery wizard 7단계 vs Quick mode 짧은 흐름)

해결: 우리 design.md 688줄로 교체. 단, GPT의 "한 줄 방향 승인" 단계가
      우리 design.md의 P-005 (oneline_direction)와 동일함을 확인.
      어떤 흐름이든 한 줄 방향 승인 단계 통과.
```

### 충돌 3: Skill 폴더 분리 vs 단일

```
GPT: .agents/.claude 분리
우리 (이전 세션 결정): 단일 .skills/ + applies_to 태그

해결: GPT 분리 채택 (이번 세션에서 결정 변경).
      이유: description 매칭 시 모델별 분리가 더 명확.
      applies_to 태그는 부가 정보로 frontmatter에 유지.
```

### 충돌 4: 30 Phase vs 우리 미정의

```
GPT: 22개 Phase 등록 (1~10 MVP, 11~20 안정화, 21~30 확장)
우리: 미정의

해결: GPT 골격 채택. 단, Phase 2~3에 Discovery+Quick 분기 명시.
      "30개는 지도 역할"이라는 GPT 본인 원칙 준수 — active 1개만 깊게.
```

### 충돌 5: meta-retrospective 위치 (양 폴더 중복)

```
GPT: .agents/.claude 양쪽에 존재 (중복)

해결: .claude만 유지. 회고는 분석 작업이므로 .claude 적합.
      .agents에서 트리거 필요 시 cross-reference로 처리.
```

### 충돌 6: product-scope-review 위치 (양 폴더 중복)

```
GPT: .agents/.claude 양쪽에 존재 (중복)

해결: 둘 다 제거. qa-check 카테고리 1 (MVP 범위)로 흡수.
```

---

## 9. 산출물 정의 (이식 완료 후)

### 9-1. 최종 폴더 구조

```
{harness-root}/
├── 00_START_HERE.md
├── 00_gap_assessment.md           (역사적 기록)
├── 10_CLAUDE_CROSS_VALIDATION_PROMPT.md
├── AGENTS.md
├── CLAUDE.md
├── HANDOFF.md
├── PHASE_REGISTRY.md
├── PROJECT_STATE.md
├── .agents/skills/{11개}/SKILL.md
├── .claude/skills/{9개}/SKILL.md
├── ai_system/
│   ├── agents/{6개}.md           (보강)
│   ├── architecture.md            (보강)
│   ├── memory/{5개}.md            (보강)
│   ├── orchestration/{5개}.md     (보강)
│   └── prompts/prompt_registry.md (우리 628줄)
├── apps/
│   ├── mobile/                    (placeholder)
│   └── web/
│       ├── design.md              (우리 688줄)
│       ├── page_map.md            (보강)
│       └── component_map.md       (보강)
├── backend/
│   ├── fastapi/README.md          (보강)
│   └── spring/README.md           (placeholder)
├── docs/
│   ├── contracts/{21개}.md        (8개 깊은 + 13개 placeholder)
│   └── decisions/{7개}.md         (보강)
├── eval/{15개}.md                 (보강 + golden_set 시드 10)
├── instruction_index/{4개}        (갱신)
├── knowledge/
│   ├── datasets/                  (placeholder)
│   ├── llm_wiki/                  (placeholder)
│   └── rag/{8개}.md               (보강)
├── logs/{4개}.md                  (운영 시작 후 누적)
├── meta/{9개}.md                  (보강)
├── packages/{3개 README}          (보강)
├── phases/
│   ├── active/phase_1_*.md        (갱신)
│   └── planned/{6개}.md           (갱신)
├── product/{7개}.md               (보강)
├── tests/{3개}.md                 (보강)
└── tools/
    └── agent_html_spec.md         (우리 789줄)
```

### 9-2. 최종 메트릭

```
총 파일 수    : ~165–170
총 줄 수      : ~10,000–12,000
Skill 수      : 20 (.agents 11 + .claude 9)
9줄 stub      : 0 (모두 보강 또는 placeholder marker)
Critical 누락 : 0
```

### 9-3. 다음 단계 (이식 완료 후)

```
1. tools/agent-html/ Claude Code 빌드 (별도 세션)
2. Phase 1 실제 코드 작업 시작 (Next.js, FastAPI)
3. 첫 Skill 실 트리거 발생 → meta-retrospective 1차 회고
4. 1주 운영 후 토큰 절약 효과 측정
```

---

## 10. 이 문서의 사용법

### Claude Code 위임 시

이 문서 통째로 첨부 + 다음 한 줄 지시:

```
이 문서의 Sprint S0를 수행한다. 산출물은 검증 체크포인트 통과해야 한다.
완료 후 verification 결과를 보고한다.
```

### Codex 위임 시

이 문서 + 해당 Sprint 섹션만 발췌 + 다음 지시:

```
{해당 Sprint의 Codex 적합 작업}만 수행한다.
파일별 결정 매트릭스를 정확히 따른다.
완료 후 파일 목록과 줄 수를 보고한다.
```

### 이 문서 자체 변경

```
이 migration_procedure.md도 contract이다.
변경 시 contract-change Skill 절차를 따른다.
meta/proposals/에 변경 제안서 작성.
```

---

## 11. v1.1.0 보강 사항

이 섹션은 v1.0.0 작성 직후 검토에서 발견된 7개 갭 보강. 본문(섹션 1~10)을 supplement한다.

### 11.1. HARNESS_ROOT 결정 가이드 (G1)

Sprint S0 진입 전 확정.

#### 권장 결정 트리

```
질문 1: 기존에 작업하던 하네스 폴더가 있는가?
  Yes → HARNESS_ROOT = 기존 폴더
        백업: cp -r {기존} {기존}.backup.{YYYYMMDD}
        작업 폴더: HARNESS_ROOT 자체
  No  → 질문 2

질문 2: 캡스톤(SSAK-LOG)과 같은 디렉터리 트리에 둘 것인가?
  Yes → HARNESS_ROOT = ~/projects/video-planning-agent/
        ❌ 캡스톤과 형제 폴더로 (혼동 방지)
  No  → HARNESS_ROOT = ~/dev/video-planning-agent/  (또는 사용자 선호)

질문 3: 기존 git repo가 있는가?
  Yes → 같은 repo에 추가하지 말고 별도 repo로 (다른 라이프사이클)
  No  → git init 으로 새 repo 생성
```

#### S0 시작 첫 단계 (HARNESS_ROOT 결정 후)

```bash
# 1. 폴더 셋업
export HARNESS_ROOT="${HOME}/projects/video-planning-agent"
mkdir -p "$HARNESS_ROOT" && cd "$HARNESS_ROOT"
git init
git checkout -b main

# 2. GPT 하네스 복제
unzip {gpt_harness.zip} -d .
# 또는: cp -r {gpt_harness_path}/. .

# 3. 우리 deliverables 별도 폴더에 보관 (충돌 회피)
mkdir -p .migration_source
cp -r {our_outputs}/. .migration_source/

# 4. 초기 커밋
git add -A
git commit -m "harness: initial GPT skeleton + migration source"
```

이후 본문 Sprint S0 절차로 진입.

---

### 11.2. 누락된 폴더 7개 추가 (G2)

우리 Skill들이 참조하는 폴더 중 GPT 하네스에 없는 것. **Sprint S0에서 빈 폴더 + `.gitkeep` + 인덱스 파일로 추가**.

| 폴더 | 사용 Skill | 추가 시점 | 인덱스 파일 |
|---|---|---|---|
| `meta/handoffs/` | context-compact, multi-llm-validation | S0 | `meta/handoffs/README.md` |
| `meta/validations/` | multi-llm-validation | S0 | `meta/validations/README.md` |
| `meta/proposals/` | contract-change, meta-retrospective | S0 | `meta/proposals/README.md` |
| `meta/patterns.md` | meta-retrospective | S0 | (단일 파일) |
| `meta/skill_usage_log.md` | meta-retrospective | S0 | (단일 파일) |
| `meta/security_metrics.md` | security-review | S5 | (단일 파일) |
| `docs/contract_changes/` | contract-change | S0 | `docs/contract_changes/README.md` |
| `eval/regression_results/` | eval-run, prompt-version-review | S0 | `eval/regression_results/README.md` |
| `eval/cost_snapshots/` | cost-review | S0 | `eval/cost_snapshots/README.md` |
| `eval/qa_reports/` | qa-check | S0 | `eval/qa_reports/README.md` |
| `eval/design_reviews/` | design-review | S0 | `eval/design_reviews/README.md` |
| `eval/security_reviews/` | security-review | S0 | `eval/security_reviews/README.md` |
| `docs/bug_reports/` | bug-triage | S0 | `docs/bug_reports/README.md` |
| `meta/retrospectives/` | meta-retrospective | S0 | `meta/retrospectives/README.md` |

#### 각 README.md 표준 형식

```markdown
# {folder-name}

## 목적

{이 폴더의 역할 1줄}

## 생성 주체

이 폴더의 파일은 {Skill-name} Skill에 의해 생성된다.

## 파일 명명 규칙

{YYYY-MM-DD}-{slug}.md  (예: 2026-01-13-fix-output-schema.md)

## 보존 정책

- 즉시 보존
- 30일 후 archive 후보 (단, meta-retrospective가 결정)

## 인덱스

(자동 갱신은 phase-complete Skill에 의해)
```

S0에서 14개 폴더/파일 일괄 추가.

---

### 11.3. Placeholder Marker 표준 형식 (G3)

본문 3-3에서 한 번 언급된 형식을 **모든 placeholder에 적용**. 9줄 stub 16개 중 placeholder로 분류된 모든 파일은 이 형식으로 강제 변환.

#### 표준 형식

```markdown
# {contract-name}

> 🚧 PLACEHOLDER · Created: {YYYY-MM-DD} · Status: stub

## 작성 트리거

이 contract는 다음 시점에 작성된다:
- **Phase**: {Phase 번호} 진입 시
- **Skill**: {관련 Skill 이름} 첫 트리거 시
- **사유**: {왜 그때까지 미작성인지}

## 잠정 원칙 (작성 전까지)

{1–3줄. 운영 안 막히게 최소 원칙.}

## 작성 시 포함할 것 (미리 정의)

- [ ] {항목 1}
- [ ] {항목 2}
- [ ] {항목 3}

## 참조

작성 시 다음을 참조한다:
- {관련 contract 1}
- {관련 contract 2}

## 메모

(빈 줄. 작성자가 채움.)
```

#### 적용 대상 (Sprint S3 placeholder 8개)

```
accessibility_contract.md     → Phase 9 진입 시
data_retention_policy.md      → Phase 4 (auth) 진입 시
event_log_contract.md         → Phase 4 진입 시
privacy_contract.md           → Phase 4 진입 시
user_consent_contract.md      → Phase 4 진입 시
backend_boundary.md           → Phase 4 진입 시 (placeholder 유지)
data_contract.md              → Phase 4 진입 시
frontend_boundary.md          → Phase 2 진입 시
env_contract.md               → Phase 4 진입 시
product_boundary.md           → Phase 1 진입 시 (간결 의도)
tech_stack_contract.md        → Phase 1 진입 시 (간결 의도)
```

#### Codex 위임 시 지시 형식

```
다음 16개 contract 파일 중 8개(보강 대상 제외)를 11.3의 표준 형식으로 변환:
- [목록]
각 파일의 "작성 트리거", "잠정 원칙", "작성 시 포함할 것"은 우리 Skill의 related_contracts 참조 정보를 기반으로 채운다.
```

---

### 11.4. Sprint별 Sanity Check (G4)

각 Sprint **시작 전**과 **종료 후** 자동 점검. 통과 못하면 진입/완료 안 됨.

#### 시작 전 sanity (모든 Sprint 공통)

```bash
# sanity_start.sh
set -e
echo "=== Sprint $1 Start Check ==="

# 1. HARNESS_ROOT 설정 확인
test -n "$HARNESS_ROOT" || { echo "❌ HARNESS_ROOT not set"; exit 1; }
test -d "$HARNESS_ROOT" || { echo "❌ HARNESS_ROOT not found"; exit 1; }
cd "$HARNESS_ROOT"

# 2. git 상태 clean (이전 작업 미커밋 방지)
test -z "$(git status --porcelain)" || { echo "❌ uncommitted changes"; exit 1; }

# 3. 이전 Sprint commit 존재 확인 (S0 제외)
if [ "$1" != "S0" ]; then
  PREV=$(prev_sprint $1)  # S0 → none, S1 → S0, ...
  git log --oneline | grep -q "harness: $PREV" || { echo "❌ Sprint $PREV not committed"; exit 1; }
fi

# 4. 필수 파일 존재 (Sprint별 다름)
case "$1" in
  S0) test -f PROJECT_STATE.md ;;
  S1) test -f .migration_source/design.md ;;
  S2) test -d .migration_source/skills ;;
  ...
esac

echo "✅ Sanity OK, Sprint $1 can start"
```

#### 종료 후 sanity (Sprint별)

각 Sprint의 검증 체크포인트(섹션 6)를 자동화:

```bash
# sanity_end_S1.sh
echo "=== Sprint S1 End Check ==="

# design.md 줄 수
LINES=$(wc -l < apps/web/design.md)
test $LINES -ge 680 || { echo "❌ design.md only $LINES lines"; exit 1; }

# db_schema 핵심 테이블 존재
grep -q "candidate_knowledge" docs/contracts/db_schema.md || exit 1
grep -q "brand_memory_entries" docs/contracts/db_schema.md || exit 1
grep -q "plan_options" docs/contracts/db_schema.md || exit 1

# prompt_registry 핵심 prompt 존재
grep -q "P-001" ai_system/prompts/prompt_registry.md || exit 1
grep -q "P-008" ai_system/prompts/prompt_registry.md || exit 1
grep -q "P-AUX" ai_system/prompts/prompt_registry.md || exit 1

echo "✅ Sprint S1 verified"
```

#### Claude Code 위임 시 지시

```
Sprint $X 시작 전 sanity_start.sh $X 실행.
종료 후 sanity_end_$X.sh 실행.
둘 다 통과한 후에만 commit + 다음 Sprint 진입.
실패 시 즉시 사용자에게 보고.
```

스크립트 작성은 Sprint S0의 마지막 단계로 포함.

---

### 11.5. 부분 완료 감지 + 재진입 (G4 후속)

Sprint 중간에 세션이 끊겼을 때 다음 세션이 어디서 시작할지.

#### 상태 파일

`PROJECT_STATE.md`의 `migration_progress` 필드:

```yaml
migration_progress:
  current_sprint: S2
  current_sprint_step: 3
  total_steps_in_sprint: 4
  last_completed_action: "agent-io-check SKILL.md 작성 완료"
  next_action: "ai-architecture-review SKILL.md 작성"
  blocker: null
  last_updated: 2026-01-13T15:30:00Z
```

#### 매 작업 단위 후 갱신

Claude Code는 매 작업 단위 끝나면 이 필드 갱신. 세션 끊겨도 다음 세션이 `current_sprint_step`부터 재개 가능.

#### 재진입 시 절차

```
1. PROJECT_STATE.md의 migration_progress 읽기
2. last_completed_action까지 실제 파일 시스템에 반영됐는지 검증
3. 반영 안 됐으면 last_completed_action까지 rollback (git reset)
4. next_action부터 진행
```

이 절차는 context-compact Skill의 핸드오프 패키지에도 포함.

---

### 11.6. agent_html_spec 정합 갱신 (G5)

기존 `agent_html_spec.md`는 단일 `.skills/` 폴더 가정으로 작성됨. 이번 결정(`.agents/.claude/ 분리`)과 충돌. **이식 완료 후 spec v1.1.0 갱신 필요**.

#### 갱신 항목

```
agent_html_spec.md §2 Screen 4 (Decisions):
  - "skills 폴더" 참조를 ".agents/skills/ + .claude/skills/"로 변경

agent_html_spec.md §3-2 데이터 의존:
  - Screen 2 (Phases)의 Skills 통계 항목에 폴더 구분 추가
  - skills_usage 표시 시 agents/claude 분리해서

agent_html_spec.md §5-2 안전 가드 화이트리스트:
  - ".skills/*/SKILL.md" → ".agents/skills/*/SKILL.md, .claude/skills/*/SKILL.md"

agent_html_spec.md §3-2 JSON Manifest:
  - skills_manifest.json에 applies_to 필드 추가 (불필요해진 부분이지만 metadata로)
```

#### 갱신 시점

```
- Sprint S2 완료 후 (Skill 폴더 구조 확정 시)
- 또는 agent.html MVP 빌드 직전 (Claude Code 위임 시 함께)

방법: contract-change Skill 절차로 spec 갱신 → meta/proposals/ 등록
```

---

### 11.7. 신규 충돌 3개 (G6) — 충돌 7, 8, 9

본문 섹션 8의 충돌 1~6에 추가.

#### 충돌 7: Critic Agent revise 정책

```
GPT: ai_system/orchestration/moa_policy.md 9줄 stub
우리: Critic revise 최대 2회 (cost-review Skill에서 무한 루프 차단 항목)

해결: Sprint S4에서 moa_policy.md 보강 시 우리 규칙 명시.
      "Critic이 revise 권장 시 Rewriter 호출 1회, 그래도 부족하면 
       partial result로 사용자에게 노출, 추가 revise는 사용자 요청 시에만"
      cost-review Skill의 시나리오 2 (Critic 무한 revise 루프)와 정합.
```

#### 충돌 8: /generate endpoint 응답 형식

```
GPT: api_contract.md /generate 응답이 단일 plan
우리: prompt P-006이 3개 plan_candidates 생성

해결: api_contract.md 보강 시 응답을 plans 배열로 변경.
      ```json
      {
        "plan_options": [
          { "id": "...", "concept": "...", ... },
          { "id": "...", "concept": "...", ... },
          { "id": "...", "concept": "...", ... }
        ],
        "recommended_index": 0,
        "session_id": "..."
      }
      ```
      추가로 /select-plan endpoint 신설 (사용자가 1개 선택 시).
      Sprint S3의 api_contract.md 깊은 작성 시 반영.
```

#### 충돌 9: agent_html_spec과 본 문서의 결정 불일치 (G5와 중복 명시)

```
GPT 하네스 결정: .agents/.claude 분리 채택
agent_html_spec.md (v1.0.0): 단일 .skills/ 폴더 가정

해결: 11.6절 참조. Sprint S2 후 agent_html_spec.md v1.1.0 갱신.
```

---

### 11.8. Phase 0 Acceptance 명시 (G7)

이 마이그레이션 작업 자체가 **Phase 0 (하네스 초기화)**다. PHASE_REGISTRY에서 active로 등록 + acceptance 정의.

#### Phase 0 acceptance.md (S0에서 생성)

```markdown
# Phase 0. 하네스 초기화 (Migration)

## Goal

GPT 골격 + 우리 콘텐츠 병합하여 운영 가능한 하네스 완성.

## Scope

migration_procedure.md v1.1.0의 Sprint S0~S5 전체 실행.

## Non-Goals

- 영상 에이전트 본체 코드 작성 (Phase 1+)
- agent.html 빌드 (Phase 0 종료 후)
- 캡스톤 SSAK-LOG 관련 작업

## Acceptance

- [ ] Sprint S0 완료 (라우팅 + 상태 + 폴더 추가)
- [ ] Sprint S1 완료 (Core 3 contract 이식: design, db_schema, prompt_registry)
- [ ] Sprint S2 완료 (Skill 20개 정리)
- [ ] Sprint S3 완료 (핵심 8 contract 보강 + placeholder 8)
- [ ] Sprint S4 완료 (eval, knowledge, ai_system 보강)
- [ ] Sprint S5 완료 (보조 파일 + 최종 audit)
- [ ] harness-audit Skill 1회 실행, 0 critical / 0 high
- [ ] 9줄 stub 파일 0개
- [ ] 모든 Skill의 related_contracts 파일이 실존
- [ ] PROJECT_STATE.migration_progress = "completed"
- [ ] tools/agent_html_spec.md v1.1.0으로 갱신

## Done Definition

위 11개 acceptance 모두 통과 + git log에 Sprint S0~S5 6개 commit 존재.

## 예상 소요

- 세션 수: 6~9
- Claude Code: 4~5
- Codex: 3~4
- Copilot: 1~2 (검토용)

## 의존성

없음 (이 프로젝트의 첫 Phase)

## 다음 Phase

Phase 1. MVP 기본 플로우 (Next.js + FastAPI 실 코드 작업 시작)
```

#### PHASE_REGISTRY 갱신

```
| 0 | 하네스 초기화 (Migration) | active | GPT 골격 + 우리 콘텐츠 병합 |
| 1 | MVP 기본 플로우 | pending | (Phase 0 완료 후 진입) |
```

Phase 1을 active에서 pending으로 변경.

---

### 11.9. 종합 v1.1.0 영향 요약

v1.0.0 대비 변경 사항:

```
✅ 추가
  - 폴더 14개 (meta/, eval/, docs/ 하위)
  - placeholder marker 표준 (16개 파일 적용)
  - sanity check 스크립트 2종 (start/end)
  - PROJECT_STATE.migration_progress 필드
  - Phase 0 acceptance.md (11 acceptance)
  - 충돌 7, 8, 9 사전 해결책

🔄 변경
  - 1-3 섹션: HARNESS_ROOT 결정 마감 시점 명시
  - agent_html_spec.md 갱신 필요 (S2 후)
  - Phase 1 → pending (Phase 0 active)

⚠️ 영향
  - Sprint S0 작업량 증가 (폴더 14개 추가 + sanity 스크립트)
  - Sprint S3 placeholder 작업 일관성 강화
  - 다음 세션 재진입 정확도 향상
```

#### Sprint별 추가 작업 시간 추정

```
S0: +30분 (폴더 추가 + sanity 스크립트 작성)
S1: +5분 (sanity 적용)
S2: +10분 (sanity + Skill 충돌 검사)
S3: +20분 (placeholder marker 16개 일관 적용)
S4: +5분 (sanity)
S5: +15분 (Phase 0 acceptance 검증 + agent_html_spec v1.1.0 갱신)

총 추가: ~85분 (가치 대비 충분)
```

---

```
v1.0.0 (2026-01-XX): 초안 작성 (Claude 채팅 세션)
v1.1.0 (2026-01-XX): 7개 갭 보강
  - HARNESS_ROOT 결정 마감 시점 명시
  - 누락 폴더 7개 추가 (meta/handoffs 등)
  - placeholder marker 표준 형식 명세
  - Sprint별 sanity check 스크립트
  - 부분 완료 감지 + 재진입 절차
  - agent_html_spec 정합 갱신 (.agents/.claude 결정 반영)
  - 신규 충돌 3개 (Critic revise, /generate 응답, agent_html_spec)
  - Phase 0 acceptance 명시
v1.2.0 (2026-05-24): Skill 구조 결정 변경 (Sprint S0 진입 시점)
  - 충돌 3 재해결: .agents/.claude 분리 → .claude/skills/ 단일 + applies_to 태그
  - 근거: Claude Code Skill 자동 트리거는 .claude/skills/만 인식.
          분리 시 .agents/skills/ 11개가 자동 트리거 안 됨.
          applies_to: [agents|claude|both] 태그로 모델 분리 기능 동등 제공.
  - 영향:
    · Sprint S2 작업 변경: 모든 20 Skill을 .claude/skills/로 통합 배치
    · GPT의 .agents/skills/ 폴더는 S2에서 삭제
    · agent_html_spec.md v1.1.0 갱신 (§11.6) 불필요 → 단일 폴더 전제 유지
    · _staging/skills/INDEX.md 원래 설계 의도와 정합 회복
  - 호환성:
    · Claude Code: 모든 Skill 자동 트리거 ✅
    · Codex: AGENTS.md 경로 라우팅으로 reference 로드 ✅
    · Copilot Code: 동일 ✅
```
