# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 **하네스 마이그레이션(Phase 0) 완료 + Phase 1 (MVP 기본 플로우) 완료 + Phase 2 (PWA 설계) 완료 + Phase 3 (PWA UI 구현) 완료**.
Next.js PWA 기본 화면 11 routes 빌드 + 4-layer 컴포넌트 4개 + Discovery wizard / Quick mode 분기 / Mode Branching middleware 모두 동작.
다음 단계는 Phase 4 FastAPI 백엔드 확장 (3-plan + Critic + SSE) 진입.

## 현재 Active Phase

**Phase 1. MVP 기본 플로우 ✅ done (2026-05-26)** — archive 이동 완료

**Phase 2. design.md 기반 PWA 설계 ✅ done (2026-05-27)** — archive 이동 완료

**Phase 3. Next.js PWA 기본 UI 구현 ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS / audit_naming + audit_page_component 0 drift / 변경성 4/5+1 WARN / P-X1 5/5 / component_map 6연속 0줄

**Phase 4. FastAPI 기본 백엔드 구현 (확장)** — 🔵 **active (2026-05-28 진입, GPT 검토 채택 4 Slices)**
- 진입 점검: phase-start v1.3.0 §6 4점검 통과 (audit_naming 0 drift)
- GPT 검토 채택: 6→4 Slices (revise loop / SSE / 4-layer 재정의 모두 Phase 4.5/5+ 이관)
- 핵심: contract endpoints 4개 + 3-plan parallel + multi-model 인터페이스 + Critic verdict 노출 + Phase 1 endpoint 회귀 0
- 사용자 결정 7개 모두 반영 (4-b: 3 parallel + multi-model / 5-a: Phase 1 endpoint Phase 8+ 제거 / 6-a: PlanCard 무수정)
- 첫 작업: Wave 1 Slice 1 — Foundation contract endpoints (`routers/plans.py` 4 endpoints)
- 다음 phase 선택: **Slice 4 retrospective에서** (옵션 A: Phase 4.5 / B: Phase 5 / C: 다른 우선순위)

## migration_progress

```yaml
current_sprint: completed
current_sprint_step: 6
total_steps_in_sprint: 6
last_completed_action: "Phase 4 entry: phase-start v1.3.0 §6 4점검 통과 + 9 entry files + audit_naming 0 drift. GPT 검토 채택 (6→4 Slices). 사용자 결정 7개 모두 반영 (4-b multi-model / 5-a Phase 8+ 제거 / 6-a PlanCard 무수정 등)"
next_action: "Wave 1 Slice 1 sub-agent dispatch — Foundation contract endpoints (routers/plans.py 4 endpoints + schemas/plans.py + ADR-014)"
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
phase_3_status: completed
phase_3_entry_date: 2026-05-28
phase_3_completion_date: 2026-05-28
phase_3_archive_location: phases/archive/phase-3-pwa-impl/
phase_3_total_slices_completed: 6  # Slice 1~6 모두 PASS
phase_3_total_waves: 5
phase_3_acceptance_passed: 10/10  # A1~A10
phase_3_changeability_simulation: 4/5 PASS + 1 WARN  # 시나리오 5 code phase 자연 증가
phase_3_design_review: 7 principles aligned (PASS, impl phase)
phase_3_audit_naming_final: 0 drift
phase_3_audit_page_component_final: 0 drift  # D5 신규 도구
phase_3_smoke_test: 7/7 PASS  # pytest 62/62 + audit×2 + build + tsc + lint + BUILD_ID
phase_3_simplicity_check: 5/5 PASS
phase_3_qa_check_v1_2_0: 11 categories applied (8 PASS / 3 skip - AI/cost/logs Phase 4+)
phase_3_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두 sub-agent §SELF-VERIFICATION PASS
phase_3_component_map_zero_lines_streak: 6  # Slice 1~6 모두 0줄, 조정 4번 강제 성공
phase_3_deviation_count: 0
phase_3_new_patterns:
  - P-X1-EFFECT-001  # P-X1 §SELF-VERIFICATION 5연속 효과 측정
  - P-THIN-VERTICAL-001  # Thin Vertical Slice 효과 (코드 phase entry 표준)
phase_3_mitigated_patterns:
  - P-AGENT-SCOPE-001  # Phase 2 발견 → Phase 3 P-X1 적용 후 0건 재발
phase_3_d5_completed: audit_page_component.ps1  # Slice 6 신규
phase_3_deferred_to_phase_4:
  - D2_QuickInputCard_alt_variants
  - D3_PlanCard_4layer_reconcile  # 조정 3번 — PlanComparisonCard와 함께 재정의
  - D4_PlanComparisonCard_detailed
phase_3_retrospective_proposals: proposed (Y-X1~Y-X3 + Phase 2 P-X2 재평가)
phase_4_status: active
phase_4_entry_date: 2026-05-28
phase_4_current_wave: 1
phase_4_current_slice: 1
phase_4_total_slices: 4  # GPT 검토 채택 (6→4)
phase_4_total_waves: 4  # all sequential (사용자 결정 2-a)
phase_4_completed_slices: []
phase_4_estimated_hours_total: 7-11  # Phase 3 50%
phase_4_user_decisions_applied:
  decision_1: a  # 4 Slices
  decision_2: a  # Sequential
  decision_3: c  # 다음 phase Slice 4 결정
  decision_4: b + multi-model  # 3 parallel + 모델 추가 가능 구조
  decision_5: a  # Phase 1 endpoint Phase 8+ 제거
  decision_6: a  # PlanCard 무수정
  decision_7: a  # 그대로 진입
  decision_8: deferred 명시
phase_4_deferred_in_advance:
  - D6_Critic_revise_loop_+_Rewriter  # Phase 4.5+
  - D7_SSE_Progress_streaming  # Phase 5+
  - D8_PlanComparisonCard_4layer  # Phase 5+
  - D3_PlanCard_4layer_redefinition  # Phase 5+
  - D4_PlanComparisonCard_detail  # Phase 5+
  - D2_QuickInputCard_alt_variants  # Phase 9
  - Phase_1_endpoint_removal  # Phase 8+
phase_4_p_x1_streak_target: 4  # 9 total (Phase 3 5 + Phase 4 4)
phase_4_component_map_zero_lines_target: 4  # 11+ total (Phase 3 7 + Phase 4 4)
phase_4_plan_card_zero_lines_target: 4  # 사용자 결정 6-a
total_commits: 39  # 38 + Phase 4 entry
last_updated: 2026-05-28
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
Phase 4 진입 준비:

1. (권장) Phase 3 회고 3 proposals 검토
   → meta/proposals/2026-05-28_phase-3-retrospective-proposals.md
   → Y-X1 (design_handoff §6.1 매핑표 spec/code 칸 분리) 검토
   → Y-X2 (audit_page_component 사용 가이드) 검토
   → Y-X3 (Sub-path 분리 패턴 표준 등록) 검토

2. Phase 2 P-X 후속 재평가 결과 적용
   → P-X1: ✅ applied + 5/5 효과 입증 (유지)
   → P-X2 (변경성 시뮬 phase-complete 게이트): 채택 권장 (Y-X1 통합)
   → P-X3 (design-review spec-only): Phase 11+ 재진입 시
   → P-X4 / P-X5: deferred 유지

3. Phase 4 진입 (phase-start 호출)
   → phases/active/phase-4-fastapi-extension/ 폴더 생성
   → 4점검 (assumptions / Simplest Slice / Surgical Scope / Verification)
   → Phase 1 backend baseline + Phase 3 frontend + Phase 2 design spec baseline 로드
   → 첫 작업 후보: 3-plan generate endpoint (P-006 plan_candidates 활성화)

4. Phase 4 deferred 처리 계획
   → D2 QuickInputCard alt variants (Phase 9 데이터 베이스)
   → D3 PlanCard 4-layer 정합 (조정 3번 — PlanComparisonCard 함께)
   → D4 PlanComparisonCard 상세 spec + 4-layer
   → D1 Step 2~7 wireframe (Phase 11+ 또는 Phase 4 직전 deferred)
```
