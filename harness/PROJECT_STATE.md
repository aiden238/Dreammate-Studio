# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 **하네스 마이그레이션(Phase 0) + Phase 1~4 + Phase 4.5 + Phase 6 + Phase 5 + Phase 5.5 + Phase 7 완료**.
Next.js PWA **12 routes** (+/login) + FastAPI 14 endpoints (Phase 1~5 누적, /auth/* + /sse/* 신규) + 3-plan parallel + multi-model 인터페이스 + Critic canonical (overall_score + dimensions) + revise loop (max 2) + Rewriter v1.1.0 + recommended_plan_index + **Supabase 영속화 + JWT httpOnly cookie + RLS 정책 + SSE Progress 4단계** + **RAG Lite (candidate_knowledge 5단계 MVP 전부 + pgvector retrieval + LLM Wiki 보조)** 모두 동작.
**Phase 7 ✅ done (2026-05-29)** — RAG Lite (candidate_knowledge 5단계 MVP 전부, ADR-025/026, large phase 5 Slice 실측 ~13~14h).
**🟢 Phase 8 active (2026-05-29)** — MOA Lite 본격 (orchestrator 추출 + SSE worker 통합 + prompt_registry 정식화, 12~16h, 5 Slice 모두 sub-agent). Slice 1 entry 완료.

## 현재 Active Phase

**🟢 Phase 8. MOA Lite 본격 — active (2026-05-29)** — orchestrator 추출 (behavior-preserving) + SSE Progress worker 통합 + prompt_registry semver 정식화. **Slice 1 entry 완료** (8 entry files + 4-check PASS + audit_naming 0 drift + ai-architecture-review/prompt-version-review 첫 정식 + ADR-027/028/029).

- 한 줄 정의: `plans_generate()` 400줄 god-function의 MOA orchestration을 service layer orchestrator로 추출(behavior-preserving) + SSE Progress 실 stage 연동 + prompt_registry P-001~P-008 + AUX semver 정식화.
- **5 Slice 모두 sub-agent dispatch**:
  - Slice 1 [Pre-Entry — validations + ai-architecture-review + prompt-version-review(분석) + ADR-027/028/029] ✅ 완료
  - Slice 2 [MOA Orchestrator 추출 (behavior-preserving) + ProgressSink] (다음)
  - Slice 3 [SSE Progress worker 통합 — progress_store 브릿지]
  - Slice 4 [prompt_registry 정식화 — contract-change + prompt-version-review 적용]
  - Slice 5 [Close]
- **사용자 결정 3건 반영 (2026-05-29)**:
  - Scope: 3개 모두 (A orchestrator + B SSE + C prompt_registry, 5 Slice, 12~16h)
  - Critic drift: **Conservative adapter** — Phase 6 canonical(0–1) 불변 (ADR-018 보존) + P-007 prompt(0–5) 유지 + 코드 0–1 정규화 adapter + P-007 v1.0.0→v1.1.0
  - SSE: in-memory progress_store 브릿지 (graceful, background task 미도입 — moa_policy §4 sync, async Phase 11+)
- **★ behavior-preserving 정신**: orchestrator 추출 = Envelope byte-identical + 기존 pytest 223 수정 0 (회귀 0 = 동작 불변 증거)
- **첫 정식 트리거 2개**: ai-architecture-review (MOA orchestration 설계 → ADR-027) + prompt-version-review (P-007 Critic semver → ADR-029)
- ADR-027 (MOA orchestrator) + ADR-028 (SSE progress integration) + ADR-029 (prompt_registry semver) 신규.
- PlanCard.tsx 0줄 + component_map.md 0줄 유지 (backend-only phase) ★.

**Phase 7 ✅ done (2026-05-29)** 이하 옵션 (Phase 8 채택, 나머지는 후속 phase 이관):
- **B. Phase 9 — 결과 저장 + 피드백** (6~10h): plan 선택/수정/반려 누적, Brand Memory 자동 추출 ADR 신규, per-user rate-limit + audit-log
- **C. Phase 9.5+ — eval-run Skill 정식화** (4~6h): golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 5회 해소) + Critic deprecated 4 fallback 완전 제거 + 간이 RAG eval_rubric 정식
- **D. 다른 우선순위** (Phase 11+): 사용자 데이터 자동 promotion (rag-update Skill 두 번째) / Supabase SQL function `match_approved_knowledge` 정의 (운영 단계 필수) / Phase 1 legacy rag 실 통합 / cost-review Skill

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

**Phase 6. Output Schema + Agent IO Stabilization ✅ done (2026-05-29)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M3 3/3 PASS / audit_naming + audit_page_component 0 drift × 2 / scenario_simulation 5/5 (P-X2 두 번째 자동 게이트) / schema_stress_test 5/5 (P-X2 v2 신규) / smoke_test_phase_6 10/10 PASS / pytest 144/144 (+35 신규)
- **P-X1 17연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4) + PlanCard 12연속 0줄 + component_map 22연속 0줄** ★
- **Critic verdict canonical 결정** (overall_score + dimensions, ADR-018) + **Rewriter v1.0.0 → v1.1.0** (Pydantic + graceful, ADR-019)
- **contract-change Skill 첫 본격 실 변경 통과** (output_schema + agent_io_contract + api_contract 3 contract + 회귀 0)
- **agent-io-check Skill 첫 정식 트리거** (Rewriter v1.1.0 + Critic canonical 정합 PASS)
- **multi-llm-validation formal 두 번째 트리거** (V1~V5 PASS, P-VALIDATION-FORMAL-001 두 번째 입증 → 정식 패턴 확정)
- 신규 패턴: P-CRITIC-CANONICAL-001 + P-CONTRACT-FIRST-001 (신규 후보) + P-X1-EFFECT-001 update (17연속) + P-VALIDATION-FORMAL-001 update (두 번째)
- Sub-agent 4/4 (모두 sub-agent dispatch) + Slice 4 close (final)
- GPT 검토안 6→4 Slice 압축 (▼33%) + 시간 8~12h → 실측 ~8h (▼20%, P-GPT-REVIEW-001 두 번째 적용)

**Phase 5. DB / Auth / RLS / SSE ✅ done (2026-05-29)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M4 4/4 PASS / audit_naming 0 drift × 2 / audit_page_component 2 intended drift WARN (Slice 3 AuthGuard + /login route 신규) / scenario_simulation v2 10/10 (P-X2 세 번째 자동 게이트) / schema_stress_test 5/5 (Phase 6 v2 유지) / smoke_test_phase_5 12/12 (11 PASS + 1 WARN intended) / pytest 170/170 (+26 신규)
- **P-X1 22연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5) + PlanCard 17연속 0줄 + component_map 27연속 0줄** ★
- **Supabase + 4계층 schema migration + plans_repo** (Slice 2 — db_schema.md contract + ADR-020)
- **Auth + JWT (httpOnly cookie) + Frontend Login + AuthGuard wrapper** (Slice 3)
- **RLS 정책 (auth.uid() + 4 정책 + 2-hop subquery) + SSE Progress 4단계 D7** (Slice 4 — ADR-021/022)
- **security-review Skill 첫 정식 + 두 번째 final** (Slice 1 entry T1~T6 + Slice 5 verification)
- **contract-change Skill 두 번째 본격 실 변경 통과** (db_schema.md 신규)
- **multi-llm-validation formal 세 번째 트리거** (V1~V6 PASS, P-VALIDATION-FORMAL-001 정식 패턴 확정 — 3회 누적)
- **agent-io-check Skill 두 번째 회귀 검증** (Phase 6 baseline 유지 PASS)
- 4 ADR 신규 (ADR-020 Supabase + ADR-021 RLS + ADR-022 SSE)
- 신규 패턴: P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 (신규 후보) + P-X1-EFFECT-001 update (22연속) + P-VALIDATION-FORMAL-001 update (세 번째 정식 확정)
- Sub-agent 5/5 (모두 sub-agent dispatch) + Slice 5 close (final)
- graceful fallback 일관 적용 — Supabase 미설정 시 in-memory dict 회귀 0
- 실측 시간 ~14-16h (추정 15~20h 내)

**Phase 5.5. Legacy DB Consolidation + Validation Strengthening + Phase 7 Prep ✅ done (2026-05-29)** — archive 이동 완료
- A1~A8 8/8 PASS + M1~M2 2/2 PASS / audit_naming 0 drift / audit_page_component 2 intended drift WARN (Phase 5 baseline 유지) / scenario_simulation v2 10/10 (P-X2 네 번째 자동 게이트) / schema_stress 5/5 / smoke_test_phase_5 12/12 / pytest 170→172 (+2 legacy deprecation 검증)
- **P-X1 26연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4) + PlanCard 18연속 0줄 + component_map 28연속 0줄** ★
- **Legacy DB 옵션 A 채택** (ADR-023 — 공존 + deprecated note + 지연 통합) + **ADR-024 Phase 7 RAG scope evolution** (5단계 MVP + 확대 지점 A~F)
- **External validation × 3 self-strengthen** — V-form 합의 추정 PASS (Phase 4.5/6/5)
- **Brand Memory Phase 9+ confirmation** (NG2 + ADR-024 cross-ref)
- **legacy backward-compat 100% 유지** (Phase 1 baseline 보호 + Phase 5 baseline 보호 동시 달성)
- 신규 패턴: P-LEGACY-CONSOLIDATION-001 신규 후보 + P-X1-EFFECT-001 update (26연속) + P-VALIDATION-FORMAL-001 update (self-strengthen V-form sub-pattern)
- Sub-agent 4/4 (모두 sub-agent dispatch) + Slice 4 close (final)
- mini-phase consolidation 패턴 효과 입증 (실측 ~4-5h, 추정 4~6h 내)

**Phase 7. RAG Lite (candidate_knowledge 5단계 MVP 전부) ✅ done (2026-05-29)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M4 4/4 PASS / audit_naming 0 drift / audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) / scenario_simulation v3 15/15 (P-X2 다섯 번째 자동 게이트) / schema_stress 5/5 / smoke_test_phase_7 13/13 (12 PASS + 1 WARN intended) / pytest 172 → 223/223 (+51 신규)
- **P-X1 31연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5) + PlanCard 19연속 0줄 + component_map 29연속 0줄** ★
- **5단계 파이프라인 전부 MVP 구현** (사용자 결정 4 Phase 5.5 명시 — ADR-024 §5단계 MVP) — pending → filtered → evaluated → approved → promoted + hybrid 승인 (자동 ≥0.8 / 수동 0.6~0.8 / 거부 <0.6) + promotion_history JSONB
- **pgvector retrieval** (cosine + top-k=5 + threshold=0.7) + **OpenAI text-embedding-3-small** + **chunking 512 tokens + overlap 50** + **LLM Wiki vs RAG 분리 (RAG > LLM Wiki 우선순위)**
- **rag-design Skill ★ 첫 정식 트리거** (Slice 1, ADR-025 RAG architecture)
- **rag-update Skill ★ 첫 정식 트리거** (Slice 4, 5단계 승격 절차)
- **contract-change Skill 본격 세 번째** (rag_data_contract.md §18 신규 — 5단계 stage enum + promotion_history + retrieval 정책)
- **multi-llm-validation formal 네 번째 트리거** (V1~V7 PASS — ADR-024 / chunk 512 / top-k=5 threshold=0.7 / embedding / graceful / LLM Wiki vs RAG / hybrid)
- **agent-io-check Skill 세 번째 회귀 검증** (agents/rag.py Phase 1 baseline 호환 + Phase 7 통합 wrapper, Critic/Rewriter 회귀 0)
- 2 ADR 신규 (ADR-025 RAG architecture + ADR-026 5단계 promotion logic)
- 신규 패턴: P-RAG-5STAGE-001 (5단계 transition + hybrid 승인) + P-RAG-GRACEFUL-001 (5종 marker + RAG > LLM Wiki) + P-X1-EFFECT-001 update (31연속) + P-VALIDATION-FORMAL-001 update (네 번째) + P-LEGACY-CONSOLIDATION-001 update (누적 2회 — Phase 1 legacy rag ↔ Phase 7 신규 공존)
- Sub-agent 5/5 (모두 sub-agent dispatch) + Slice 5 close (final)
- graceful 5종 marker 표준화 (rag_unavailable / rag_no_results / llm_wiki_unavailable / embedding_failed / supabase_unconfigured) — P-GRACEFUL-001 (Phase 1) 정신 5번째 입증
- Phase 1 legacy rag/{retriever, fallback}.py + Phase 7 rag/retrieval.py 공존 (P-LEGACY-CONSOLIDATION-001 누적 2회 — Phase 11+ Custom RAG 시점 자연 통합)
- 실측 시간 ~13~14h (추정 12~16h 내)

**🟡 Next: pending_user_decision** — Phase 8 MOA / Phase 9 저장-피드백 / Phase 9.5+ eval / Phase 11+ (사용자 결정 대기)

## 이전 결정 (옵션 B 변형: Phase 6 선행)

사용자 결정 (2026-05-29): 옵션 A/B/C 중 **옵션 B 변형 채택** → Phase 6 선행 → Phase 5 순차 진행.
- Phase 6 = Output Schema + Agent IO Stabilization (8~10h, mini-phase)
- Phase 5 = DB/Auth (Phase 6 종료 후 진입, formal external validation 의무)
- GPT 검토안 7.5/10 채택 (Critic canonical / Rewriter contract / fallback 축소 / frontend 정합)
- 6→4 Slice 압축 (P-GPT-REVIEW-001 정신)

## migration_progress

```yaml
current_sprint: "phase-8-slice-1"
current_sprint_step: phase_8_slice_1_entry_completed
total_steps_in_sprint: 5
last_completed_action: "Phase 8 entry — 8 entry files + 4-check PASS + audit_naming 0 drift + ai-architecture-review/prompt-version-review 첫 정식 + ADR-027/028/029"
next_action: "Slice 2 sub-agent (MOA Orchestrator 추출 behavior-preserving)"
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
phase_6_status: completed
phase_6_entry_date: 2026-05-29
phase_6_completion_date: 2026-05-29
phase_6_archive_location: phases/archive/phase-6-output-schema-stabilization/
phase_6_total_slices: 4  # 모두 sub-agent
phase_6_completed_slices: 4  # Slice 1~4 모두 PASS
phase_6_estimated_hours_total: 8-10
phase_6_actual_hours: ~8  # GPT 정신 계승 ▼20% (8~12h → ~8h)
phase_6_assumptions_check: PASS  # 4-check 통과 (entry)
phase_6_acceptance_passed: 10/10  # A1~A10
phase_6_meta_acceptance_passed: 3/3  # M1~M3
phase_6_pytest_result: 144/144  # Phase 4.5 baseline 109 + Phase 6 신규 35
phase_6_smoke_test: 10/10 PASS  # smoke_test_phase_6.ps1 신규
phase_6_scenario_simulation: 5/5 PASS (auto-gate, 두 번째)  # P-X2 두 번째 자동 게이트
phase_6_schema_stress_test: 5/5 PASS (P-X2 v2 신규)  # schema_stress_test.ps1 신규
phase_6_audit_naming_final: 0 drift  # Slice 1 + Slice 4
phase_6_audit_page_component_final: 0 drift  # Slice 1 + Slice 4
phase_6_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_6_p_x1_cumulative_streak: 17  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 ★
phase_6_component_map_zero_lines_streak: 22  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 ★
phase_6_plan_card_zero_lines_streak: 12  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 ★
phase_6_deviation_count: 0
phase_6_user_decisions_applied:
  next_phase_choice: phase_6_first_then_phase_5  # GPT 검토안 채택 (옵션 B 변형 — Phase 6 선행 → Phase 5)
  slice_compression: 6_to_4  # P-GPT-REVIEW-001 정신
  all_slices_sub_agent: yes
  multi_llm_validation_formal: yes  # 두 번째 트리거
  prompt_registry_defer_phase_7_plus: yes  # NG8
  critic_fallback_keep_with_deprecation: yes  # NG12
phase_6_skills_first_trigger:
  - agent_io_check  # 첫 정식 트리거 (Slice 4)
  - contract_change_formal  # 첫 본격 실 변경 (Slice 2 — output_schema + agent_io_contract + api_contract 3 contract + ADR-018/019)
  - multi_llm_validation_formal_second  # 두 번째 트리거 (Slice 1 V1~V5)
  - phase_complete_v1_2_0_second  # P-X2 자동 게이트 두 번째 트리거 (Slice 4)
phase_6_contracts_changed:
  - output_schema.md  # §9 CriticEvaluation canonical + §10 Body.revise_history Optional
  - agent_io_contract.md  # §6 Rewriter v1.0.0 → v1.1.0
  - api_contract.md  # §8.3 응답 필드 정식 등록
phase_6_adr_created:
  - ADR-018  # Critic verdict canonical (phase_6_critic_canonical.md)
  - ADR-019  # Rewriter contract v1.1.0 (phase_6_rewriter_contract.md)
phase_6_new_patterns:
  - P-CRITIC-CANONICAL-001  # 다중 fallback → canonical + deprecated 단계적 축소
  - P-CONTRACT-FIRST-001  # DB 진입 전 mini-phase로 contract 안정화 (신규 후보)
  - P-X1-EFFECT-001 (update 17연속)  # P-X1 17연속 PASS 누적 입증
  - P-VALIDATION-FORMAL-001 (update 두 번째)  # 두 번째 트리거로 정식 패턴 확정
phase_6_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 17연속 누적 입증 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4)
phase_6_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안에 직접 기록 (mini-phase)
phase_6_deferred_to_next:
  - external_validation_fill  # Phase 5 entry 직전 사용자가 외부에서 채움
  - security_review_first_trigger  # Phase 5 entry
  - scenario_simulation_v2  # Phase 5 Slice 1 (DB/Auth 5 시나리오 추가)
  - prompt_registry_p_007_p_008_formal  # Phase 7+ (NG8)
  - critic_fallback_full_removal  # Phase 9+ eval-run 정식화 후
  - revise_effect_eval  # Phase 9+ eval-design (Phase 4.5 D6 effect 계속 deferred)
phase_5_status: completed
phase_5_entry_date: 2026-05-29
phase_5_completion_date: 2026-05-29
phase_5_archive_location: phases/archive/phase-5-db-auth/
phase_5_total_slices: 5  # 모두 sub-agent
phase_5_completed_slices: 5  # Slice 1~5 모두 PASS
phase_5_estimated_hours_total: 15-20
phase_5_actual_hours: ~14-16
phase_5_assumptions_check: PASS  # 4-check 통과 (entry, audit_naming 0 drift)
phase_5_acceptance_passed: 10/10  # A1~A10
phase_5_meta_acceptance_passed: 4/4  # M1~M4
phase_5_pytest_result: 170/170  # Phase 6 144 baseline + Phase 5 신규 26 (test_db 9 + test_auth 9 + test_rls 4 + test_sse 4)
phase_5_smoke_test: 12/12 (11 PASS + 1 WARN intended)  # smoke_test_phase_5.ps1 신규
phase_5_scenario_simulation_v2: 10/10 PASS (auto-gate, 세 번째)  # P-X2 세 번째 자동 게이트
phase_5_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_5_audit_naming_final: 0 drift  # Slice 1 + Slice 5
phase_5_audit_page_component_final: 2 intended drift WARN  # Slice 3 AuthGuard + /login route 신규, phase-complete v1.2.0 §1.6 허용
phase_5_audit_page_component_intended_drift:
  - AuthGuard  # Slice 3 신규 component (wrapper 패턴)
  - /login  # Slice 3 신규 route
phase_5_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두
phase_5_p_x1_cumulative_streak: 22  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 ★
phase_5_component_map_zero_lines_streak: 27  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 ★
phase_5_plan_card_zero_lines_streak: 17  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 ★
phase_5_deviation_count: 0
phase_5_user_decisions_applied:
  next_phase_order: phase_6_first_then_phase_5  # GPT 검토안 채택 + 사용자 명시
  all_slices_sub_agent: yes  # 5개 모두 sub-agent dispatch
  security_review_first_trigger: yes  # ★ 첫 정식 (Slice 1) + 두 번째 final (Slice 5)
  multi_llm_validation_formal: yes  # 세 번째 트리거 (Slice 1, V1~V6 PASS)
  external_validation_placeholder: yes  # Phase 4.5/6 패턴 계승
  supabase_adoption: yes  # ADR-020
  scenario_simulation_v2: yes  # 5 → 10 scenarios (Slice 1, 10/10 Slice 5)
phase_5_skills_first_trigger:
  - security_review_first_and_second  # 첫 정식 (Slice 1) + 두 번째 final (Slice 5)
  - contract_change_second_formal  # 두 번째 본격 실 변경 (Slice 2 db_schema.md 신규)
  - multi_llm_validation_formal_third  # 세 번째 트리거 (Slice 1 V1~V6) — 정식 패턴 확정
  - phase_complete_v1_2_0_third  # P-X2 자동 게이트 세 번째 트리거 (Slice 5)
  - agent_io_check_second  # 두 번째 회귀 검증 (Slice 5)
phase_5_contracts_changed:
  - db_schema.md  # 신규 (DB schema 첫 정식 contract — 4계층 + plans + users + JSONB)
phase_5_adr_created:
  - ADR-020  # Supabase 채택 (phase_5_supabase_adoption.md, Slice 1)
  - ADR-021  # RLS Policy (phase_5_rls_policy.md, Slice 4)
  - ADR-022  # SSE Progress (phase_5_sse_progress.md, Slice 4)
phase_5_new_patterns:
  - P-RLS-001  # RLS 정책 + 인증/익명 분리
  - P-SSE-001  # SSE 4단계 progress + Origin + cookie
  - P-SECURITY-REVIEW-001  # security-review 2-trigger 패턴 (신규 후보)
  - P-X1-EFFECT-001 (update 22연속)  # large + 보안 phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update 세 번째)  # 정식 패턴 확정 (3회 누적)
phase_5_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 22연속 누적 입증
phase_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 (Phase 6+ legacy 통합 외 5개)
phase_5_deferred_to_next:
  - legacy_db_integration  # Phase 6+ (개선 제안 §1)
  - testclient_cookies_migrate  # Phase 6+ (개선 제안 §2)
  - emailstr_dependency  # Phase 6+ (개선 제안 §3)
  - sse_worker_real_integration  # Phase 8+ MOA Lite (개선 제안 §4)
  - per_user_rate_limit_and_audit_log  # Phase 9+ (개선 제안 §5)
  - pgtap_rls_auto_verification  # Phase 9+ (개선 제안 §6)
  - refresh_token_rotation  # Phase 21+ MFA
phase_5_5_status: completed
phase_5_5_entry_date: 2026-05-29
phase_5_5_completion_date: 2026-05-29
phase_5_5_archive_location: phases/archive/phase-5.5-legacy-db-consolidation/
phase_5_5_total_slices: 4
phase_5_5_completed_slices: 4  # Slice 1~4 모두 PASS
phase_5_5_estimated_hours_total: 4-6
phase_5_5_actual_hours: ~4-5  # consolidation mini-phase 압축 효과
phase_5_5_assumptions_check: PASS
phase_5_5_acceptance_passed: 8/8  # A1~A8
phase_5_5_meta_acceptance_passed: 2/2  # M1~M2
phase_5_5_pytest_result: 172/172  # Phase 5 170 baseline + Phase 5.5 신규 2 (legacy deprecation 검증)
phase_5_5_smoke_test: 12/12 (11 PASS + 1 WARN intended)  # Phase 5 smoke 재실행
phase_5_5_scenario_simulation_v2: 10/10 PASS (auto-gate, 네 번째)  # P-X2 네 번째 자동 게이트
phase_5_5_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_5_5_audit_naming_final: 0 drift
phase_5_5_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 유지 (AuthGuard + /login), phase-complete v1.2.0 §1.6 허용
phase_5_5_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 신규 (baseline 유지)
  - /login  # Phase 5 Slice 3 신규 (baseline 유지)
phase_5_5_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_5_5_p_x1_cumulative_streak: 26  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 ★
phase_5_5_component_map_zero_lines_streak: 28  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 ★
phase_5_5_plan_card_zero_lines_streak: 18  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 ★
phase_5_5_deviation_count: 0
phase_5_5_legacy_backward_compat: 100  # Phase 1 baseline 보호 + Phase 5 baseline 보호 동시 달성
phase_5_5_user_decisions_applied:
  legacy_db_consolidation: yes  # 결정 1 (옵션 A 채택, ADR-023)
  external_validation_strengthen: yes  # 결정 2 (self-strengthen V-form × 3, V-form 합의 추정 PASS)
  phase_7_rag_lite_keep: yes  # 결정 3 (ADR-024)
  candidate_knowledge_5stage_mvp_all: yes  # 결정 4 (ADR-024 §5단계 MVP, 12~16h)
  brand_memory_phase_9_plus: yes  # 결정 5 (NG2 + ADR-024 cross-ref)
  all_slices_sub_agent: yes  # 4 Slice 모두 sub-agent dispatch
phase_5_5_skills_first_trigger:
  - phase_complete_v1_2_0_fourth  # P-X2 자동 게이트 네 번째 트리거 (Slice 4)
phase_5_5_adrs:
  - ADR-023  # Legacy DB consolidation 옵션 A (phase_5_5_legacy_db_consolidation.md)
  - ADR-024  # Phase 7 RAG scope evolution (phase_7_rag_scope_evolution.md)
phase_5_5_new_patterns:
  - P-LEGACY-CONSOLIDATION-001  # 다중 layer 공존 시 옵션 A (신규 후보)
  - P-X1-EFFECT-001 (update 26연속)  # consolidation mini-phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update self-strengthen V-form sub-pattern)
phase_5_5_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 26연속 누적 입증
phase_5_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~3
phase_5_5_deferred_to_next:
  - legacy_real_integration  # Phase 7+ RAG 통합 후 mini-phase (Phase 7.5? 권장)
  - external_validation_real_external_review  # 사용자 외부 GPT/Gemini (Phase 7+ 진입 전 권장)
  - adr_024_expansion_a_to_f_early_activation  # Phase 11+ 분기별 검토
  - brand_memory_auto_extract_adr  # Phase 9+ MVP 본격 운영 후
phase_7_status: completed
phase_7_entry_date: 2026-05-29
phase_7_completion_date: 2026-05-29
phase_7_archive_location: phases/archive/phase-7-rag-lite/
phase_7_total_slices: 5
phase_7_completed_slices: 5  # Slice 1~5 모두 PASS
phase_7_estimated_hours_total: 12-16  # ADR-024 추정
phase_7_actual_hours: ~13-14  # large phase 단일일 다중 sub-agent
phase_7_assumptions_check: PASS  # 4-check 통과 (C1~C11, U1~U6, audit_naming 0 drift)
phase_7_acceptance_passed: 10/10  # A1~A10
phase_7_meta_acceptance_passed: 4/4  # M1~M4
phase_7_pytest_result: 223/223  # Phase 5.5 172 baseline + Phase 7 신규 51 (promotion 10 + quality_filter 8 + eval_rubric 5 + chunking 7 + embedding 5 + retrieval 7 + integration 9)
phase_7_smoke_test: 13/13 (12 PASS + 1 WARN intended)  # smoke_test_phase_7.ps1 신규
phase_7_scenario_simulation_v3: 15/15 PASS (auto-gate, 다섯 번째)  # P-X2 다섯 번째 자동 게이트
phase_7_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_7_audit_naming_final: 0 drift  # Slice 5
phase_7_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 계승 (AuthGuard + /login)
phase_7_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 신규 (baseline 계승)
  - /login  # Phase 5 Slice 3 신규 (baseline 계승)
phase_7_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두
phase_7_p_x1_cumulative_streak: 31  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 ★
phase_7_component_map_zero_lines_streak: 29  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 ★
phase_7_plan_card_zero_lines_streak: 19  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 ★
phase_7_deviation_count: 0
phase_7_user_decisions_applied:
  rag_lite_scope_keep: yes  # 사용자 결정 3 (Phase 5.5 명시 — ADR-024 §확대 지점 별도 phase)
  candidate_knowledge_5stage_mvp_all: yes  # 사용자 결정 4 (Phase 5.5 명시 — ADR-024 §5단계 MVP)
  brand_memory_phase_9_plus_keep: yes  # 사용자 결정 5 (NG1 + ADR-024 §Brand Memory cross-reference)
  all_slices_sub_agent: yes  # 5 Slice 모두 sub-agent dispatch
  rag_design_first_trigger: yes  # Slice 1 ★ 첫 정식
  rag_update_first_trigger: yes  # Slice 4 ★ 첫 정식 완료
  multi_llm_validation_formal_4th: yes  # Slice 1 V1~V7 PASS
phase_7_skills_first_trigger:
  - rag_design_first_formal  # ★ 첫 정식 (Slice 1, ADR-025 결과)
  - rag_update_first_formal  # ★ 첫 정식 (Slice 4, initial promotion procedure)
  - contract_change_third_formal  # 세 번째 본격 (Slice 2 rag_data_contract.md §18)
  - multi_llm_validation_formal_fourth  # 네 번째 트리거 (Slice 1 V1~V7)
  - phase_complete_v1_2_0_fifth  # P-X2 자동 게이트 다섯 번째 트리거 (Slice 5)
  - agent_io_check_third  # 세 번째 회귀 검증 (Slice 5)
phase_7_contracts_changed:
  - rag_data_contract.md  # §18 신규 (5단계 stage enum + promotion_history + retrieval 정책)
phase_7_adrs:
  - ADR-025  # Phase 7 RAG architecture (phase_7_rag_architecture.md, rag-design Skill 첫 정식)
  - ADR-026  # Phase 7 5단계 promotion logic (phase_7_promotion_logic.md)
phase_7_new_patterns:
  - P-RAG-5STAGE-001  # 5단계 transition + hybrid 승인 + promotion_history (신규 후보)
  - P-RAG-GRACEFUL-001  # 5종 marker + RAG > LLM Wiki 우선순위 (신규 후보)
  - P-X1-EFFECT-001 (update 31연속)  # large RAG phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update 네 번째)  # 네 번째 입증 — RAG architecture V7
  - P-LEGACY-CONSOLIDATION-001 (update 누적 2회)  # Phase 1 legacy rag ↔ Phase 7 신규 공존 — 정식 채택 임박
phase_7_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 31연속 누적 입증
phase_7_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~6
phase_7_deferred_to_next:
  - chunking_tiktoken  # Phase 9+ (개선 제안 §1)
  - supabase_sql_function_match_approved_knowledge  # 운영 단계 필수 (개선 제안 §2)
  - phase_1_legacy_rag_real_consolidation  # Phase 11+ Custom RAG (개선 제안 §3)
  - rag_update_skill_second_trigger  # Phase 11+ 사용자 데이터 자동 promotion (개선 제안 §4)
  - brand_memory_auto_extract_adr  # Phase 9+ MVP 본격 운영 후 (개선 제안 §5)
  - rag_eval_rubric_formal_via_golden_set  # Phase 9+ eval-run Skill 정식화 (개선 제안 §6)
phase_8_status: in_progress
phase_8_entry_date: 2026-05-29
phase_8_total_slices: 5
phase_8_completed_slices: 0  # Slice 1 entry 완료 (구현 Slice 2~5 대기)
phase_8_estimated_hours_total: 12-16
phase_8_assumptions_check: PASS  # 4-check 통과 (C1~C11, U1~U6, audit_naming 0 drift)
phase_8_user_decisions_applied:
  scope_all_3_pillars: yes  # A orchestrator + B SSE + C prompt_registry (5 Slice)
  critic_conservative_adapter: yes  # Phase 6 canonical 불변 (ADR-018 보존) + P-007 v1.1.0
  sse_progress_store_bridge: yes  # background task 미도입 (moa_policy §4 sync)
  all_slices_sub_agent: yes  # 5 Slice 모두 sub-agent dispatch
  ai_architecture_review_first_trigger: yes  # Slice 1 ★ 첫 정식
  prompt_version_review_first_trigger: yes  # Slice 1 분석 + Slice 4 적용 ★ 첫 정식
phase_8_adrs: [ADR-027, ADR-028, ADR-029]  # MOA orchestrator + SSE progress integration + prompt_registry semver
total_commits: 71  # 70 + Phase 8 Slice 1 entry (=71)
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
Phase 7 (RAG Lite — candidate_knowledge 5단계 MVP 전부) — ✅ done (2026-05-29).
🟡 pending_user_decision — 다음 phase 사용자 결정 대기.

다음 phase 옵션:

A. Phase 8 — MOA Lite 본격 (12~16h)
   - Intent / Planner / Critic / Rewriter 완전 분리
   - agents/* 모두 재구조화 (Phase 1 baseline + Phase 6 canonical + Phase 7 wrapper 공존 → 정리)
   - SSE Progress worker 통합 (Phase 5 Slice 4 mock → 실 worker callback)
   - prompt_registry P-007/P-008 정식화 (NG8 누적 3회 defer 해소)
   - ai-architecture-review Skill ★ 첫 정식 baseline

B. Phase 9 — 결과 저장 + 피드백 (6~10h)
   - 사용자 plan 선택 / 수정 / 반려 누적
   - Phase 5 plans_repo + RLS + Phase 7 RAG 활용
   - Brand Memory 자동 추출 ADR 신규 (Phase 7 개선 제안 §5, 사용자 결정 5 누적 2회 confirm)
   - per-user rate-limit + audit-log (Phase 5 §개선 제안 §5 흡수)

C. Phase 9.5+ — eval-run Skill 정식화 (4~6h)
   - golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 5회 deferred 해소)
   - Critic deprecated 4 fallback 완전 제거 (Phase 6 ADR-018 다음 단계)
   - 간이 RAG eval_rubric → golden_set 기반 정식 (Phase 7 개선 제안 §6)
   - eval-design + eval-run Skill 첫 정식 트리거 baseline

D. 다른 우선순위 (Phase 11+)
   - 사용자 데이터 자동 promotion (ADR-024 §A, Phase 7 개선 제안 §4 + rag-update Skill 두 번째 트리거)
   - Supabase SQL function `match_approved_knowledge` 정의 (Phase 7 개선 제안 §2 — 운영 단계 필수)
   - Phase 1 legacy rag/{retriever, fallback}.py 실 통합 (Phase 7 개선 제안 §3 — Phase 11+ Custom RAG)
   - cost-review Skill 정식화

확대 지점 (ADR-024 §확대 지점, 다른 phase 확장 경로):
   → Phase 11+ 사용자 데이터 자동 promotion (rag-update Skill 두 번째)
   → Phase 21+ Custom RAG / Graph RAG
   → Phase 11+ Hybrid retrieval (BM25 + vector)
   → Phase 8+ Multi-modal RAG (제한)
   → Phase 9+ Re-ranking model

Phase 7 deferred 처리 계획:
   → Phase 8+: MOA Lite 본격 + SSE worker 통합 + prompt_registry 정식화 + ai-architecture-review 첫 정식
   → Phase 9+: 결과 저장 + 피드백 + Brand Memory 자동 추출 ADR + per-user rate-limit + audit-log
   → Phase 9.5+: eval-run Skill 정식화 + revise effect eval + Critic 4 fallback 완전 제거 + RAG eval_rubric 정식
   → Phase 11+: 사용자 데이터 자동 promotion (rag-update 두 번째) + Phase 1 legacy rag 실 통합 + Custom RAG / Graph RAG / Hybrid retrieval
   → 운영 단계 필수: Supabase SQL function `match_approved_knowledge` 정의 (Phase 8+/9+ 운영 시작 직전)
```
