# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 **하네스 마이그레이션(Phase 0) 완료**.
GPT 155-파일 하네스 골격 + 자체 18-파일 깊은 콘텐츠 + S0~S5 6 Sprint 작업으로 운영 가능한 하네스 완성.
다음 단계는 Phase 1 MVP 기본 플로우 진입 준비.

## 현재 Active Phase

**Phase 1. MVP 기본 플로우 ✅ done (2026-05-26)** — archive 이동 완료

**Phase 2. design.md 기반 PWA 설계 ✅ done (2026-05-27)** — archive 이동 완료

**Phase 3. Next.js PWA 기본 UI 구현 (Discovery + Quick 분기)** — 🔵 **pending_entry (진입 대기, 2026-05-27 이후)**
- 진입 전 필수: meta/proposals/2026-05-27_phase-2-retrospective-proposals.md **P-X1** 검토 (sub-agent enforcement 강화 — 코드 phase 진입 전 필수)
- Phase 2 산출물: design_system 4 + ADR 2 + flow specs 4 + wireframes 4 + design_handoff + page_map + component_map = 17 신규/수정
- Phase 2 변경성 시뮬레이션: 5/5 PASS (acceptance A9)
- Phase 2 archive: `phases/archive/phase-2-pwa-design/` (참조 가능, 기본 미참조)
- Phase 1 archive: `phases/archive/phase-1-mvp-basic-flow/` (참조 가능, 기본 미참조)
- Phase 0 archive: `phases/archive/phase-0-migration/` (참조 금지)

## migration_progress

```yaml
current_sprint: completed
current_sprint_step: 6
total_steps_in_sprint: 6
last_completed_action: "Phase 2 종료 절차 완료: Slice 6 final QA (qa-check v1.2.0 11 카테고리 PASS + Simplicity 5/5 + Contract Drift 0) + design-review (7 원칙 정합 PASS) + 변경성 시뮬레이션 5/5 PASS + meta-retrospective (P-AGENT-SCOPE-001 + P-DESIGN-LAYERED-001 신규 패턴 등록) + 5 proposals (P-X1~P-X5) + archive 이동"
next_action: "Phase 3 진입 — 진입 전 P-X1 검토 → phase-start v1.2.0 (또는 P-X1 적용 시 v1.3.0)로 시작"
blocker: null
phase_0_status: completed
phase_0_completion_date: 2026-05-26
phase_1_status: completed
phase_1_completion_date: 2026-05-26
phase_1_archive_location: phases/archive/phase-1-mvp-basic-flow/
phase_1_retrospective_proposals: accepted_all + applied (P1~P4)
phase_2_status: completed
phase_2_completion_date: 2026-05-27
phase_2_archive_location: phases/archive/phase-2-pwa-design/
phase_2_retrospective_proposals: proposed (P-X1~P-X5, awaiting user review)
phase_2_total_slices_completed: 6  # Slice 1~6 모두 PASS
phase_2_total_waves: 5
phase_2_acceptance_passed: 10/10  # A1~A10
phase_2_changeability_simulation: 5/5 PASS
phase_2_design_review: 7 principles aligned (PASS)
phase_2_audit_naming_final: 0 drift
phase_2_simplicity_check: 5/5 PASS
phase_2_qa_check_v1_2_0: 11 categories applied (5 PASS / 6 skip - spec phase)
phase_2_new_patterns:
  - P-AGENT-SCOPE-001  # sub-agent forbidden 영역 침범 (Wave 3 Slice 3)
  - P-DESIGN-LAYERED-001  # 4-layer 4 + Variants 3 minimal 정책 효과
phase_2_deferred_to_phase_3:
  - Step_2_to_7_wireframe_detail
  - QuickInputCard_variants
  - PlanCard_4layer_reconcile
  - audit_page_component_script
phase_2_deferred_to_phase_4:
  - PlanComparisonCard_detailed
phase_3_status: pending_entry
phase_3_estimated_scope: "Next.js PWA UI 구현 (Phase 2 spec 기반) — 4-layer 4 컴포넌트 current variant + /new middleware + Discovery Step 1 + Quick Mode + Direction Approval"
phase_3_pre_entry_required: "Review meta/proposals/2026-05-27_phase-2-retrospective-proposals.md P-X1 (sub-agent forbidden enforcement)"
total_commits: 30  # ~f50bc74 + Phase 2 Slice 6 commit
last_updated: 2026-05-27
```

## 확정 방향

### 제품 / UX
- 영상 제작 AI가 아닌 **영상기획 AI 에이전트**
- 4계층 데이터 모델: User → Brand → Domain → Series → Video Project
- Hybrid UX: **Discovery Wizard** (신규/콜드스타트, 5단계 카드) + **Quick Mode** (같은 Series 추가)
- Discovery 단계당 카드 5장 (4장 추천 + 1장 "직접 입력")
- 한 호출당 plan 후보 **3개** 생성 → 사용자가 1개 선택
- Intent Filter (영상기획 외 입력 차단)

### 기술 스택
- **MVP**: Next.js 14 PWA + FastAPI + Supabase(PostgreSQL + pgvector)
- **LLM**: gpt-4o-mini 기본, gpt-4o 일부 (Critic 등)
- **Phase 21+**: Expo React Native, Spring Boot, Custom RAG
- 영상 자동 편집 / TTS / BGM / 자동 업로드 → MVP 제외 (영구)

### AI 시스템
- **MOA Lite**: Intent → Planner → Critic → Rewriter
- **Critic revise 최대 2회** (무한 루프 차단)
- **RAG Lite**: candidate_knowledge 5단계 승격 (pending → filtered → evaluated → approved → promoted)
- **prompt-version-review**: semver + golden_set 회귀 + A/B (major 시 10%→50%→100%)
- PII 마스킹 + 프롬프트 인젝션 차단 (Step 1, Step 2 자동 검사)

### 운영
- Brand Memory 자동 추출 + 사용자 검토 가능
- 광고적 표현 차단 단어 검사 ("최고의", "혁신적인" 등)
- 30–60초 생성 대기 시 4단계 progress stepper + 부분 결과 즉시 노출

## confirmed_decisions (25)

```
[ 1] Discovery + Quick 하이브리드 UX (1.6x 비용 수용)
[ 2] Mode 자동 분기: 신규/Brand 없음 → Discovery, 기존 Series → Quick
[ 3] Discovery 단계당 카드 5장 (4추천 + 1직접입력)
[ 4] 3개 plan 후보 생성 (P-006 plan_candidates)
[ 5] Critic revise 최대 2회 (무한 루프 차단)
[ 6] 4계층 데이터 모델 (Brand/Domain/Series/VideoProject)
[ 7] Intent Filter (영상기획 외 입력 차단)
[ 8] Brand Memory 자동 추출 + 사용자 검토 가능
[ 9] 광고적 표현 차단 단어 검사
[10] 30–60초 생성 대기 시 4단계 progress + 부분 결과 노출
[11] Skill 14 → 20 (이번 세션, GPT 흡수 후)
[12] Skill 폴더: .claude/skills/ 단일 + applies_to 태그
     (v1.2.0 변경: .agents/.claude 분리 → 단일.
      이유: Claude Code Skill 자동 트리거는 .claude/skills/만 인식)
[13] 22 Phase 등록 (1~10 MVP, 11~20 안정화, 21~30 확장)
[14] Phase 0 = 마이그레이션 자체 (지금 active)
[15] context-compact가 모든 Skill 위 최우선
[16] multi-llm-validation 워크플로 (Claude/GPT/Gemini 교대)
[17] agent.html은 토큰 최적화 압축 레이어 (안정화 후 빌드)
[18] RAG candidate_knowledge 5단계 승격 파이프라인
[19] PII 마스킹 + 프롬프트 인젝션 차단 (자동 검사 2단계)
[20] prompt 변경 semver + 회귀 + A/B (major 시 10%→50%→100%)
[21] agent_html_spec v1.1.0 갱신 — v1.2.0 단일 폴더 결정으로 불필요해짐
[22] placeholder marker 표준 형식 (16개 stub 일관 적용)
[23] Sprint별 git commit + sanity script (시작/종료)
[24] PROJECT_STATE.migration_progress 필드로 부분 완료 감지
[25] Claude Code / Codex / Copilot Code 분담 (multi-llm-validation 활용)
```

## 주요 리스크

- `output_schema.md` 불명확 → Sprint S3에서 깊은 작성 (300줄+)
- Golden Set 부족 → Sprint S4에서 시드 10케이스 작성
- LLM 보안 contract 9줄 stub → Sprint S3 우선 보강
- 사용자 데이터 승격 정책 미흡 → Phase 7+ (rag-update Skill 절차로 강제)
- 9줄 stub 16개 (docs/contracts/) → Sprint S3에서 8 보강 + 8 placeholder marker

## 다음 액션

```
Phase 3 진입 준비:

1. (필수) Phase 2 회고 5 proposals 검토
   → meta/proposals/2026-05-27_phase-2-retrospective-proposals.md
   → P-X1 (sub-agent enforcement 강화) 채택 권장 — Phase 3 진입 전 필수
   → P-X2 / P-X3 채택 검토
   → P-X4 / P-X5 deferred 적정성 확인

2. (P-X1 채택 시) phase-start SKILL.md v1.2.0 → v1.3.0 갱신
   → §6.3 Surgical Scope에 sub-agent 자기 검증 절차 추가
   → multi_slice_plan template 갱신

3. Phase 3 진입 (phase-start 호출)
   → phases/active/phase-3-pwa-impl/ 폴더 생성
   → 4점검 (assumptions / Simplest Slice / Surgical Scope / Verification)
   → Phase 2 산출물 17 + Phase 1 archive 3 = 20 baseline 문서 로드
   → 첫 작업: Tailwind config tokens.md 매핑 (시나리오 1 자동 반영 보장)

4. Phase 3 deferred 처리 계획
   → D1 Step 2~7 wireframe / D2 QuickInputCard variants / D3 PlanCard 4-layer
   / D5 audit_page_component.ps1
```
