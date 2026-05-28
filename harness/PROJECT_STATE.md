# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 **하네스 마이그레이션(Phase 0) + Phase 1~4 + Phase 4.5 모두 완료, Phase 6 ★ active (entry 2026-05-29)**.
Next.js PWA 11 routes + FastAPI 4 contract endpoints + 3-plan parallel + multi-model 인터페이스 + Critic verdict + revise loop (max 2) + recommended_plan_index 모두 동작.
**🟢 Phase 6 진행 중 — Output Schema + Agent IO Stabilization** (Phase 5 DB/Auth 진입 전 contract 안정화, 8~10h, 4 Slice 모두 sub-agent)

## 현재 Active Phase

**Phase 1. MVP 기본 플로우 ✅ done (2026-05-26)** — archive 이동 완료

**Phase 2. design.md 기반 PWA 설계 ✅ done (2026-05-27)** — archive 이동 완료

**Phase 3. Next.js PWA 기본 UI 구현 ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS / audit_naming + audit_page_component 0 drift / 변경성 4/5+1 WARN / P-X1 5/5 / component_map 6연속 0줄

**Phase 4. FastAPI 기본 백엔드 구현 (확장) ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS / audit_naming + audit_page_component 0 drift (D-1 Slice 4 해소) / 변경성 4/5+1 WARN (Phase 3 결과 유지, Phase 4 +0 영향)
- **P-X1 9연속 PASS (Phase 3 5 + Phase 4 4) + component_map 15연속 0줄 + PlanCard 4연속 0줄** ★
- GPT 검토 채택 효과: 6→4 Slices (▼33%), 18~26h → 6~8h (▼66%)
- smoke_test_phase_4 8/8 PASS
- 신규 패턴: P-GPT-REVIEW-001 + P-X1-EFFECT-001 update (9연속)

**Phase 4.5. Critic Revise Loop + Rewriter + Z-X3 Best-Plan + P-X2 ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M3 3/3 PASS / audit_naming + audit_page_component 0 drift × 2 / 변경성 시뮬 5/5 PASS (P-X2 첫 자동 게이트) / smoke_test_phase_4_5 9/9 PASS / pytest 109/109 (+16 신규)
- **P-X1 13연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4) + PlanCard 9연속 0줄 + component_map 19연속 0줄** ★
- **multi-llm-validation formal 첫 트리거** (Claude Code 자가 검증 V1~V4 PASS + 외부 placeholder 분리)
- **P-X2 자동 게이트 첫 작동** (scenario_simulation.ps1 5/5 PASS via phase-complete v1.2.0 §1.6)
- 신규 패턴: P-X2-EFFECT-001 + P-VALIDATION-FORMAL-001 + P-X1-EFFECT-001 update (13연속)
- Sub-agent 4/4 (모두 sub-agent dispatch) + Slice 4 close (final)

**Phase 6. Output Schema + Agent IO Stabilization 🟢 active (entry 2026-05-29)** — mini-phase 8~10h, 4 Slice 모두 sub-agent
- 8 entry files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) 작성 완료
- assumptions.md §6 4-check PASS (audit_naming 0 drift entry, simplest slice CriticEvaluation canonical 1 모델)
- Slice 1 (Pre-Entry) sub-agent 진행 중 — validations self V1~V5 PASS + external placeholder + contract gap analysis
- GPT 검토안 7.5/10 채택 + 6→4 Slice 압축 (P-GPT-REVIEW-001 정신 계승)
- 사용자 결정: Phase 6 선행 → Phase 5 순차 진행 ("플랜을 세워서 순차적으로")

## 이전 결정 (옵션 B 변형: Phase 6 선행)

사용자 결정 (2026-05-29): 옵션 A/B/C 중 **옵션 B 변형 채택** → Phase 6 선행 → Phase 5 순차 진행.
- Phase 6 = Output Schema + Agent IO Stabilization (8~10h, mini-phase)
- Phase 5 = DB/Auth (Phase 6 종료 후 진입, formal external validation 의무)
- GPT 검토안 7.5/10 채택 (Critic canonical / Rewriter contract / fallback 축소 / frontend 정합)
- 6→4 Slice 압축 (P-GPT-REVIEW-001 정신)

## migration_progress

```yaml
current_sprint: phase-6-slice-1
current_sprint_step: 1
total_steps_in_sprint: 4
last_completed_action: "Phase 6 entry — 8 entry files (4-check PASS, audit_naming 0 drift) + GPT 검토안 7.5/10 채택 + 6→4 Slice 압축"
next_action: "Slice 1 commit 후 Slice 2 sub-agent dispatch (contract-change + Critic canonical + Rewriter contract)"
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
phase_4_status: completed
phase_4_entry_date: 2026-05-28
phase_4_completion_date: 2026-05-28
phase_4_archive_location: phases/archive/phase-4-fastapi-extension/
phase_4_total_slices: 4  # GPT 검토 채택 (6→4)
phase_4_total_waves: 4  # all sequential (사용자 결정 2-a)
phase_4_completed_slices: 4  # Slice 1~4 모두 PASS
phase_4_estimated_hours_total: 7-11  # acceptance.md
phase_4_actual_hours: ~6-8  # 실측 (원안 18-26h 대비 ▼66%)
phase_4_acceptance_passed: 10/10  # A1~A10
phase_4_changeability_simulation: 4/5 PASS + 1 WARN  # Phase 3 결과 유지, Phase 4 +0 영향
phase_4_changeability_aux_scenarios: 3/3 PASS  # 보조 시나리오 6/7/8 (Phase 1 제거 / 3→5 plan / multi-provider)
phase_4_design_review: 7 principles aligned (PASS, impl phase, PlanCard 무수정 정합)
phase_4_audit_naming_final: 0 drift
phase_4_audit_page_component_final: 0 drift  # D-1 Slice 4 해소
phase_4_smoke_test: 8/8 PASS  # smoke_test_phase_4.ps1 신규
phase_4_simplicity_check: 5/5 PASS
phase_4_qa_check_v1_2_0: 11 categories applied (9 PASS / 2 skip - 관측성 Phase 5+ / RAG 본격 Phase 7+)
phase_4_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_4_p_x1_cumulative_streak: 9  # Phase 3 5 + Phase 4 4 ★
phase_4_component_map_zero_lines_streak: 15  # Phase 2 6 + Phase 3 5 + Phase 4 4 ★
phase_4_plan_card_zero_lines_streak: 4  # Phase 4 전체 (사용자 결정 6-a) ★
phase_4_deviation_count: 1  # D-1 audit drift (intended → Slice 4 해소)
phase_4_user_decisions_applied:
  decision_1: a  # 4 Slices
  decision_2: a  # Sequential
  decision_3: c  # 다음 phase Slice 4 결정 (옵션 A/B/C 명시)
  decision_4: b + multi-model  # 3 parallel + 모델 추가 가능 구조
  decision_5: a  # Phase 1 endpoint Phase 8+ 제거
  decision_6: a  # PlanCard 무수정 (4연속 0줄 PASS)
  decision_7: a  # 그대로 진입
  decision_8: deferred 명시 (D6/D7/D8/D3/D4/D2/Phase 1 endpoint 제거)
phase_4_new_patterns:
  - P-GPT-REVIEW-001  # 외부 LLM 검토 채택 효과 (6→4 Slices, ▼66% 시간)
  - P-X1-EFFECT-001 (update 9연속)  # P-X1 9연속 PASS — Phase 3 + Phase 4 누적
phase_4_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 9연속 누적 입증 (Phase 3 5 + Phase 4 4)
phase_4_d1_completed: audit_page_component_phase4_dynamic_route_normalize  # Slice 4 D-1 해소
phase_4_deferred_to_next:
  - D6_Critic_revise_loop_+_Rewriter  # Phase 4.5+ 또는 Phase 6
  - D7_SSE_Progress_streaming  # Phase 5+
  - D8_PlanComparisonCard_4layer  # Phase 5+
  - D3_PlanCard_4layer_redefinition  # Phase 5+ (D4와 함께, 조정 3번)
  - D4_PlanComparisonCard_detail  # Phase 5+
  - D2_QuickInputCard_alt_variants  # Phase 9
  - Phase_1_endpoint_removal  # Phase 8+
phase_4_retrospective_proposals: proposed (Z-X1~Z-X3 + Phase 2 P-X2 재평가, awaiting user review)
phase_4_5_status: completed
phase_4_5_entry_date: 2026-05-28
phase_4_5_completion_date: 2026-05-28
phase_4_5_archive_location: phases/archive/phase-4.5-critic-revise-loop/
phase_4_5_total_slices: 4  # 모두 sub-agent
phase_4_5_completed_slices: 4  # Slice 1~4 모두 PASS
phase_4_5_estimated_hours_total: 12-16
phase_4_5_actual_hours: ~12-14  # Z-X3/P-X2 추가에도 ▼20% 절감
phase_4_5_assumptions_check: PASS  # 4-check 통과 (entry)
phase_4_5_acceptance_passed: 10/10  # A1~A10
phase_4_5_meta_acceptance_passed: 3/3  # M1~M3
phase_4_5_pytest_result: 109/109  # Phase 4 baseline 93 + Phase 4.5 신규 16
phase_4_5_smoke_test: 9/9 PASS  # smoke_test_phase_4_5.ps1 신규
phase_4_5_scenario_simulation: 5/5 PASS (auto-gate)  # P-X2 첫 자동 게이트 트리거 ★
phase_4_5_audit_naming_final: 0 drift  # Slice 1 + Slice 4
phase_4_5_audit_page_component_final: 0 drift  # Slice 1 + Slice 4
phase_4_5_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_4_5_p_x1_cumulative_streak: 13  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 ★
phase_4_5_component_map_zero_lines_streak: 19  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 ★
phase_4_5_plan_card_zero_lines_streak: 9  # Phase 4 4 + Phase 4.5 5 ★
phase_4_5_deviation_count: 0
phase_4_5_user_decisions_applied:
  z_x3_include: yes  # Best-Plan Selection 본 scope 포함
  p_x2_adopt: yes  # phase-complete v1.2.0 §1.6 자동 게이트
  multi_llm_validation_formal: yes  # Claude Code 자가 검증, 외부 placeholder 분리
  all_slices_sub_agent: yes  # 4개 모두 sub-agent dispatch
phase_4_5_new_patterns:
  - P-X2-EFFECT-001  # 변경성 시뮬 자동 게이트 첫 트리거 (▼99% 시간)
  - P-VALIDATION-FORMAL-001  # multi-llm-validation formal self + 외부 분리 패턴
  - P-X1-EFFECT-001 (update 13연속)  # P-X1 13연속 PASS 누적 입증
phase_4_5_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 13연속 누적 입증 (Phase 3 5 + Phase 4 4 + Phase 4.5 4)
phase_4_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안에 직접 기록 (mini-phase)
phase_6_status: in_progress
phase_6_entry_date: 2026-05-29
phase_6_total_slices: 4  # 모두 sub-agent
phase_6_completed_slices: 0
phase_6_estimated_hours_total: 8-10
phase_6_assumptions_check: PASS  # 4-check 통과 (entry)
phase_6_user_decisions_applied:
  next_phase_choice: phase_6_first_then_phase_5  # GPT 검토안 채택 (옵션 B 변형 — Phase 6 선행 → Phase 5)
  slice_compression: 6_to_4  # P-GPT-REVIEW-001 정신
  all_slices_sub_agent: yes
  multi_llm_validation_formal: yes  # 두 번째 트리거
  prompt_registry_defer_phase_7_plus: yes  # NG8
  critic_fallback_keep_with_deprecation: yes  # NG12
total_commits: 49  # 48 + Slice 1 entry (Phase 6)
last_updated: 2026-05-29
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
다음 phase 진입 준비 (🟡 pending_user_decision — Phase 4.5 종료, 다음 옵션 A/B/C):

1. (필수) Phase 4.5 회고 + closing_notes 검토
   → meta/retrospectives/phase-4.5.md (개선 제안 §1~4)
   → phases/archive/phase-4.5-critic-revise-loop/closing_notes.md (다음 phase 옵션 A/B/C 명시)
   → 신규 패턴: P-X2-EFFECT-001 + P-VALIDATION-FORMAL-001 + P-X1-EFFECT-001 update (13연속)

2. Phase 4 회고 권장 사항 재평가 (Phase 4.5 채택 결과 반영)
   → Z-X1 (audit_page_component dynamic route 정규화): deferred 유지 (Phase 5+ 새 dynamic route 추가 시 검토)
   → Z-X2 (multi-provider client factory): deferred 유지 (Phase 21+ 검토)
   → Z-X3 (Critic best-plan): ✅ Phase 4.5에서 채택 완료
   → P-X2 (변경성 시뮬 자동 게이트): ✅ Phase 4.5에서 채택 + 첫 자동 작동 완료

3. (권장) multi-llm-validation Skill formal external
   → Phase 4.5 패턴 계승: self.md + external.md 2 파일 작성
   → 옵션 A (Phase 5 DB/Auth) 진입 시 external 의무
   → V1~V4 cross-check 권장

4. 사용자 결정 (다음 phase 옵션 A/B/C)
   → 옵션 A: Phase 5 DB/Auth (Supabase + RLS + SSE, 15~20h) — formal external 의무
   → 옵션 B: Phase 6 Output Schema 안정화 (Phase 4.5 산출물 stress test + Critic verdict 단일 표준)
   → 옵션 C: Phase 9 결과 저장 + 피드백 / Phase 11+ 안정화 등 사용자 시점 재평가

5. 다음 phase 진입 (phase-start v1.3.0 호출 — 옵션 채택 후)
   → phases/active/<chosen-phase>/ 폴더 생성
   → 4점검 (assumptions / Simplest Slice / Surgical Scope / Verification)
   → Phase 4.5 backend (revise loop + best-plan) + frontend (wrapper UI) baseline 로드
   → 첫 작업: 채택 옵션에 따라

6. 다음 phase deferred 처리 계획 (옵션별)
   → 옵션 A: D7 (SSE Progress) + plan_store DB migration
   → 옵션 B: Critic verdict 4-fallback → 단일 표준 통합 + revise effect eval
   → 옵션 C: 사용자 시점 재평가
```
