# Phase 9 Pre-Entry Multi-LLM Validation — Self (Claude Code)

> 검증 모델: Claude Code (자가, 지침 참조)
> 검증 일자: 2026-05-29
> 검증 유형: formal (여섯 번째 정식 트리거 — Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째 + Phase 8 다섯째 + Phase 9 여섯째)
> 외부 검증: `2026-05-29_phase-9-pre-entry_external.md` (별도 placeholder)
> Skill 의무 트리거: **security-review (두 번째 정식 — 피드백 PII)** + multi-llm-validation (formal 여섯 번째)

## 검증 대상

1. selection/feedback 영속 (실 `plans` 테이블 정합 — plan_id + selected_option_index 0–2 + plan_candidates JSONB)
2. normalize_to_canonical wiring (critic step canonical 추가, deprecated 0–5 병행 회귀 0)
3. Brand Memory 준비 경계 (schema + ADR + 적재 경로만, P-AUX-2 agent 미구현 Phase 10+)
4. 피드백 reason text PII (자유 입력 이메일/전화 등 — 저장 전 마스킹 vs 조회 시)
5. repo graceful (Supabase 실패 시 in-memory — PlansRepo 패턴)
6. 피드백 UI wrapper (page.tsx inline, PlanCard·component_map 0줄)
7. feedback → candidate_knowledge 적재 (Phase 7 5단계 pending 정합, 자동 승격 X)

## 참조한 지침

- `harness/CLAUDE.md` § AI 구조, 메타 개선, 큰 결정
- `harness/AGENTS.md` (구현/QA 모델 라우터 — selection/feedback repo + endpoint 대상)
- `harness/docs/contracts/db_schema.md` (§3.6 plans 실 테이블 + §4.2 plan_options idealized + §4.3 selected_plans + §5.2 feedback_events + §6 brand_memory_entries + §7.2 candidate_knowledge source_kind)
- `harness/docs/contracts/llm_security_contract.md` (§3.2 PII 검출+마스킹 + §4.4 잔존 + §8 E-SEC-006)
- `harness/ai_system/prompts/prompt_registry.md` (P-AUX-2 brand_memory_extractor — input/output/활성 정책 Phase 9+ 명세만)
- `harness/backend/fastapi/agents/critic.py` (`normalize_to_canonical` helper — additive 비강제 주입 / `run_critic` 0–5 산출 / `select_best_plan_index` canonical 우선)
- `harness/backend/fastapi/db/repositories/plans_repo.py` (graceful Supabase or in-memory 패턴 — selection/feedback repo 모델)
- `harness/backend/fastapi/schemas/output.py` (Phase 6 CriticEvaluation canonical Optional — 불변 대상)
- `harness/meta/patterns.md` (P-GRACEFUL-001, P-CONTRACT-FIRST-001, P-X1-EFFECT-001, P-VALIDATION-FORMAL-001, P-SECURITY-REVIEW-001, P-RAG-5STAGE-001)
- Phase 8 closing_notes / retrospectives/phase-8.md (Phase 9 진입 체크리스트 — §1 normalize wiring / §5 brand_memory ADR / §6 revise eval)
- Phase 9 entry files (goals/scope/non_goals/assumptions/multi_slice_plan/notes)
- `.claude/skills/security-review/SKILL.md` (두 번째 정식 — 영역 1~10 절차)
- `.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)
- `.claude/skills/contract-change/SKILL.md` (db_schema.md Slice 2 변경 절차)

## 검증 결과 (V1~V7)

### V1. selection/feedback 영속 (실 `plans` 테이블 정합) — PASS

- **self-question**: 결과 저장(plan 선택)을 db_schema.md §4.3 `selected_plans`(selected_option_id → plan_options.option_id, video_id PK)가 아니라 실 `plans` 테이블 정합(plan_id + selected_option_index 0–2 + plan_candidates JSONB 참조)으로 구현하는 것이 정합하며, 4계층 미연결(NG2) 영향이 차단되는가?
- **self-answer**:
  - **현 상태 (db_schema 정독)**: §3.6 `plans` 테이블은 Phase 5 Slice 2 실 영속화 테이블 — `id`(PK) + `plan_candidates`(JSONB 3-plan) + `recommended_plan_index`(0~2) + `critic_evaluation`(JSONB) 보유. §4.2 `plan_options`(option_id PK, video_id FK, option_index 0–2) + §4.3 `selected_plans`(selected_option_id → plan_options) 는 4계층 **idealized** 정의로 `0001~0004` migration 미반영.
  - **정합 결정**: Phase 9 selection 은 실 `plans` 테이블에 정합 — `selected_plans`(신규)는 `plan_id`(plans.id 참조) + `selected_option_index`(0–2, plan_candidates JSONB 배열 인덱스) + `selection_reason`. db_schema §4.3 의 `selected_option_id → plan_options.option_id`(idealized)는 **Phase 11+ 4계층 full linkage**(NG2)로 명시 분리. plan_options 테이블 신규 생성 안 함 (NG2).
  - **회귀 0 근거**: 실 `plans` 테이블 + plan_candidates JSONB 는 Phase 5/7 baseline 그대로. Phase 9 신규 테이블(selected_plans/feedback_events/brand_memory_entries)은 **추가(additive)** — 기존 plans/plan_candidates 컬럼 0 변경 → Phase 8 baseline(pytest 249) 회귀 0.
  - **option_index 충분성**: 사용자는 3-plan 중 1개 선택 → option_index 0–2 + plan_id 로 선택 plan 식별 충분. plan 내용 자체는 plan_candidates[option_index] 로 조회 (NG2 4계층 미연결 무관).
- **잠재 risk**:
  - db_schema §4.3 idealized `selected_plans`(selected_option_id) ↔ Phase 9 실 `selected_plans`(selected_option_index) 명칭 충돌 → contract-change(Slice 2)에서 "실 plans 정합 vs Phase 11+ 4계층" 명확 분리 필요.
  - option_index 범위 검증(0–2) 누락 시 plan_candidates 배열 out-of-range.
- **권장**:
  - ADR-030 §Constraints 에 "실 plans 테이블 정합(plan_id + selected_option_index 0–2 + plan_candidates JSONB 참조), idealized plan_options/selected_plans(selected_option_id)는 Phase 11+ NG2" 명시.
  - Slice 2 contract-change 로 db_schema §4.3 에 Phase 9 실 정합 vs Phase 11+ idealized 구분 추가 + `check (selected_option_index between 0 and 2)`.
  - Slice 2 `test_selection_feedback.py` 에 option_index 0/1/2 + out-of-range 거부 케이스.

### V2. normalize_to_canonical wiring (canonical 추가, deprecated 0–5 병행 회귀 0) — PASS

- **self-question**: Phase 8 에 존재하지만 pipeline 미연결인 `normalize_to_canonical` helper 를 orchestrator critic step 에 연결할 때, critic_evaluation 에 canonical(overall_score 0–1 + dimensions) **추가**하되 deprecated 0–5(scores/overall_score_avg) **병행 유지**가 회귀 0인가? schemas/output.py 가 불변인가?
- **self-answer**:
  - **현 상태 (critic.py 정독)**: `normalize_to_canonical(verdict)`는 **비파괴 사본** 반환 — `out = dict(verdict)` 후 `scores`(0–5)가 있으면 `dimensions[k] = scores[k]/5.0` + `overall_score = overall_score_avg/5.0` 를 `setdefault`/조건부 추가. **기존 0–5 필드(scores/overall_score_avg)는 그대로 보존**. helper 는 additive 코드 유틸이며 `run_critic` 반환에 강제 주입하지 않음(docstring 명시).
  - **wiring 설계**: orchestrator critic step 에서 `verdict = normalize_to_canonical(run_critic(...))` 로 감싸 critic_evaluation 에 canonical 0–1 + dimensions 를 **추가** 저장. deprecated 0–5(scores/overall_score_avg)는 verdict 사본에 그대로 유지 → DB 저장 + Envelope 노출 시 병행.
  - **회귀 0 근거**: ① `CriticEvaluation`(schemas/output.py)은 Phase 6 ADR-018 에서 canonical + deprecated **모두 Optional** → canonical 추가도, deprecated 유지도 schema 변경 0. ② `select_best_plan_index` 는 canonical(overall_score → dimensions) 우선 + deprecated fallback → wiring 후 canonical 이 채워지면 deprecated fallback DeprecationWarning 경로 미진입(동작 동일 결과). ③ schemas/output.py CriticEvaluation 모델 **불변** (이미 Optional canonical 필드 보유 — Phase 6).
  - **의도된 delta 경계**: wiring 으로 critic_evaluation 구조에 canonical 키가 추가되면, critic_evaluation **구조를 직접 assert** 하는 baseline test 가 있으면 = 의도된 delta(Phase 8 Slice 4 version-bump 선례) → 해당 assertion만 최소 갱신. 그 외 baseline test 수정 0. "wiring 김에 0–5 제거"는 NG3 위반.
- **잠재 risk**:
  - critic_evaluation dict 키 추가로 깨지는 baseline test 수(의도된 delta 경계) — Slice 3 pytest 에서 확정(U1).
  - canonical overall_score(dimensions 평균/5.0)와 best-plan 정확도 변화 — Phase 9.5 eval(U6).
  - normalize helper 가 dimensions 를 `setdefault` 하므로 이미 canonical 있는 verdict 와 충돌 없음(보존 우선).
- **권장**:
  - ADR-032 §Decision 에 "verdict = normalize_to_canonical(run_critic(...)) → critic_evaluation canonical 0–1 + dimensions 추가, deprecated 0–5 병행 유지, schemas/output.py 불변" 명시.
  - ADR-032 §Constraints 에 "의도된 critic_evaluation delta 만 최소 baseline assertion 갱신(Phase 8 Slice 4 패턴), 0–5 제거는 Phase 9.5 eval NG3" 명시.
  - Slice 3 `test_critic_canonical_wiring.py` 에 canonical 0–1 저장 + deprecated 0–5 병행 + 회귀 0 케이스.

### V3. Brand Memory 준비 경계 (agent 미구현 Phase 10+) — PASS

- **self-question**: Brand Memory 를 Phase 9 에서 schema + ADR + 적재 경로만 **준비**하고 P-AUX-2 brand_memory_extractor agent 는 구현하지 않는 경계(사용자 결정 5)가 명확히 강제되며, scope creep("피드백 김에 자동 추출도")을 차단하는가?
- **self-answer**:
  - **사용자 결정 5 (Phase 5.5/7 누적 confirm)**: Brand Memory 자동 추출은 Phase 9 이후(Phase 10+ — MVP 운영 + 데이터 누적 후). Phase 9 = 준비만.
  - **준비 범위 (4가지)**: ① `brand_memory_entries` schema(db_schema §6 이미 정의 — Slice 2 migration 0005 에 등록) + ② `BrandMemoryRepo`(graceful, 수동/준비용 entry CRUD — 자동 추출 X) + ③ feedback/selection → candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending') 적재 경로(Slice 4) + ④ P-AUX-2 설계 명세 ADR(input: video_session_log + current_brand_memory / output: proposed_entries / 활성화 조건 Phase 10+).
  - **경계 강제**: P-AUX-2 는 prompt_registry 에 명세만 존재(Version v1.0.0, "실 구현 Phase 9+ — NG2, registry 명세만 보존"). Phase 9 는 **agent 파일 미생성** + orchestration 미연결 + 자동 추출 호출 0. ADR-031 은 설계 참조(input/output/활성화 조건)만 — `brand_memory_extractor 실행`/`자동 추출 활성` 단어 금지(NG1).
  - **회귀 0**: BrandMemoryRepo 는 graceful(PlansRepo 패턴) 신규 — 기존 코드 0 변경. candidate 적재는 status='pending' 까지만(자동 승격 X — NG12, Phase 7 5단계 정합).
- **잠재 risk**:
  - "피드백 적재 경로 김에 P-AUX-2 자동 추출 trigger" scope creep(NG1) → ADR-031 §Constraints 에 agent 미구현 명시 + Slice 4 적재는 pending 까지만.
  - candidate 적재가 Phase 7 5단계 pending 과 정합하지 않으면 RAG 오염(V7 연계).
- **권장**:
  - ADR-031 §Decision 에 "Phase 9 = 준비만(schema + BrandMemoryRepo + 적재 경로 + P-AUX-2 설계 명세), agent 미구현 + 자동 추출 활성화 Phase 10+ (NG1)" + §Constraints 에 "적재는 pending 까지 자동 승격 X (NG12)" 명시.
  - ADR-031 §P-AUX-2 설계 에 input(video_session_log + current_brand_memory) / output(proposed_entries) / 활성화 조건(MVP 운영 + 데이터 누적) — registry 명세 참조(실행 X).
  - Slice 4 `test_brand_memory_prep.py` 에 BrandMemoryRepo graceful CRUD + feedback→candidate 적재(pending) 케이스 (자동 추출 호출 0 검증).

### V4. 피드백 reason text PII (저장 전 마스킹 vs 조회 시) — PASS

- **self-question**: 피드백 reason / reject 사유는 **자유 입력 text** → 이메일/전화 등 PII 가 들어올 수 있다. llm_security §3.2 baseline(LLM 호출 전 마스킹) 외에 DB 저장 단계 신규 surface 가 생기는데, 저장 전 마스킹 vs 조회 시 마스킹 중 어느 시점이 정합하며 Phase 9 범위가 명확한가?
- **self-answer**:
  - **신규 surface**: Phase 1~8 PII 마스킹 baseline 은 LLM 호출 직전(Step 1.2 §3.2) + LLM 응답(Step 2.4 §4.4) 대상. 피드백 reason 은 **LLM 호출 없이 직접 DB 저장**되는 신규 자유 입력 경로 → 기존 hook 미적용 surface. security-review(Slice 1) 두 번째 정식 트리거 정당화.
  - **시점 결정 (security-review §T1)**: **저장 전 마스킹** 권장 — feedback_repo INSERT 직전 §3.2 직접 식별자 패턴(전화/이메일/주민/카드/IP) 재검사 + 마스킹(case B 패턴 — 마스킹 후 저장 + warnings 기록). 조회 시 마스킹은 raw PII 가 DB 에 잔존하므로 retention 의무 증가 → 저장 전 우선. Phase 5 T6 에서 "DB 저장 전 재검사 도입 시점 = Phase 9+" 로 이관된 항목의 실현.
  - **Phase 9 범위**: 저장 전 마스킹 hook(feedback reason) baseline 적용 + security-review 권장 + ADR-030 §Constraints PII 참조. 정교한 한국어 PII 라이브러리/동의 절차는 Phase 11+(privacy_contract). E-SEC-006 매핑 baseline.
  - **회귀 0**: 기존 intent/Step1 PII 마스킹 baseline 불변 + 피드백 reason 마스킹은 신규 경로 추가 → 기존 회귀 0.
- **잠재 risk**:
  - 정규식 PII 검출 false negative(한국어/영어 혼용) — 완전 차단 불가, baseline 의존(security-review §자주 실수 2).
  - 저장 전 마스킹이 사용자 의도(예: 본인 연락처 의도 입력)와 충돌 — case A(자기 정보) vs case B(타인) 구분은 baseline.
- **권장**:
  - security-review(Slice 1) §T1 에 "피드백 reason 저장 전 §3.2 패턴 마스킹 + warnings 기록(pii_masked) + E-SEC-006" 명시.
  - ADR-030 §Constraints 에 "feedback reason text 는 llm_security §3.2 PII 마스킹 baseline 저장 전 적용(Phase 5 T6 실현)" 참조.
  - Slice 3 endpoint 에서 feedback reason 마스킹 경로 연결 + (선택) test.

### V5. repo graceful (PlansRepo 패턴) — PASS

- **self-question**: SelectionRepo / FeedbackRepo / BrandMemoryRepo 를 PlansRepo graceful 패턴(Supabase 실패 시 in-memory dict fallback, raise 금지)으로 구현하는 것이 Phase 5 baseline 과 정합하며 회귀 0인가?
- **self-answer**:
  - **PlansRepo 패턴 (정독)**: `__init__(supabase_client, in_memory_store)` + `_use_supabase()` gate + try/except 후 `logger.warning(...falling back to in-memory)` + in-memory dict fallback. raise 금지(P-GRACEFUL-001 — Phase 1~7 6회 입증).
  - **selection/feedback/brand_memory repo 적용**: 동일 패턴. SelectionRepo.select(plan_id, option_index, reason) / get / FeedbackRepo.record(target, event_type, reason) / list / BrandMemoryRepo.create/list. Supabase 미설정(URL/Key) 시 in-memory → mock 환경 unit test(C10) 통과.
  - **회귀 0**: 신규 repo 3종 — 기존 PlansRepo + db/client 0 변경. db/__init__.py export 추가(additive). Phase 5 graceful baseline 그대로 계승.
  - **biz 정합**: feedback_events.user_id / selected_plans 는 auth_user_id 정합(RLS Slice 2) — PlansRepo 의 auth_user_id 패턴 계승.
- **잠재 risk**:
  - in-memory fallback 시 RLS user 격리 미적용(mock 환경) → 실 Supabase 에서만 RLS 강제(security-review §T3).
  - repo 3종 중복 코드 — graceful 패턴 반복(허용, 명확성 우선).
- **권장**:
  - ADR-030 §Decision 에 "SelectionRepo/FeedbackRepo graceful PlansRepo 패턴(Supabase or in-memory)" + ADR-031 에 BrandMemoryRepo 동일.
  - Slice 2 `test_selection_feedback.py` 에 graceful CRUD(Supabase mock + in-memory fallback 양쪽).
  - db/{client,plans_repo,migrations 0001~0004} 불변 — repo 3종 + 0005 migration 만 신규(Slice 2 forbidden 정합).

### V6. 피드백 UI wrapper (PlanCard·component_map 0줄) — PASS

- **self-question**: 선택 버튼 + 반려 이유 입력 UI 를 `apps/web/app/plan/[plan_id]/page.tsx` inline wrapper 로 추가하면서 신규 component 를 만들지 않아 `component_map.md` 0줄 + PlanCard.tsx 0줄을 유지할 수 있는가?
- **self-answer**:
  - **wrapper 정신 계승**: Phase 4.5 recommended_plan_index highlight + Phase 5 AuthGuard 모두 PlanCard 무수정(page.tsx wrapper). Phase 9 피드백 UI 도 동일 — 선택 버튼 + 반려 이유 입력(textarea)을 page.tsx 에 inline JSX 로 추가(PlanCard 외부).
  - **component_map 0줄**: 신규 component 파일을 만들지 않음 → component_map.md 등록 0줄. inline UI 는 page.tsx 내 로컬 마크업(별도 component 추출 X — NG7). PlanCard.tsx 24연속 + component_map 34연속 무수정(Phase 8 baseline) 계승 → 42/35 목표.
  - **api/types 정합**: lib/api.ts(selectPlan/sendFeedback fetch credentials include) + lib/types.ts(Select/Feedback type) 는 wrapper 지원 — component 아님(component_map 무관).
  - **회귀 0**: PlanCard.tsx + component_map.md 0줄 → next build 11 routes + tsc + lint 회귀 0(Slice 5 검증).
- **잠재 risk**:
  - inline UI 가 복잡해지면 component 추출 유혹(NG6/NG7) → page.tsx inline 강제(신규 component 안 만듦).
  - 피드백 상태 관리(선택/반려 toggle)가 page.tsx 비대 — 허용(wrapper 정신, 신규 component X).
- **권장**:
  - ADR-030 §References 또는 notes 에 "피드백 UI = page.tsx inline wrapper(PlanCard·component_map 0줄 — Phase 4.5/5 wrapper 계승)" 참조(Slice 5 구현).
  - Slice 5 사후 `git diff --stat | grep -E "PlanCard|component_map"` = 0 lines 검증(P-X1).
  - Slice 5 next build + tsc 0 + lint clean.

### V7. feedback → candidate_knowledge 적재 (Phase 7 5단계 pending 정합) — PASS

- **self-question**: 피드백/선택을 candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending')로 적재하는 경로가 Phase 7 RAG 5단계 파이프라인의 pending 진입점과 정합하며, 자동 승격(NG12)을 차단하고 PII 누출(quality_filter 전)을 막는가?
- **self-answer**:
  - **Phase 7 5단계 (정독)**: candidate_knowledge status 전이 `pending → filtered → evaluated → approved → promoted`(↘ rejected). source_kind enum 'user_choice'|'user_feedback'|'final_output'|'manual'(db_schema §7.2 이미 정의). pending 진입 후 quality_filter(P-EVAL-1) 통과해야 다음 단계.
  - **적재 경로 (Slice 4)**: `rag/feedback_to_candidate.py` — feedback/selection → candidate_knowledge(source_kind='user_feedback'/'user_choice', status='pending', source_id) INSERT 만. **자동 승격 X**(NG12 — pending 까지만). 이후 승격은 rag-update Skill(Phase 11+ 두 번째 트리거).
  - **PII 누출 차단**: candidate content 는 feedback reason 기반 → V4 저장 전 마스킹 적용 후 적재 + Phase 7 quality_filter(layer 5 promoted INSERT 직전 PII 잔존 검사 — llm_security §RAG). pending 단계는 RAG 노출 전이므로 다른 user 영향 0(security-review §T5).
  - **회귀 0**: feedback_to_candidate.py 신규 + rag/{promotion,retrieval} 불변(Phase 7 baseline — 적재 경로만 신규, Slice 4 forbidden 정합). graceful(Supabase 실패 시 skip).
- **잠재 risk**:
  - pending 적재가 자동 승격으로 오해 → NG12 명시 + 적재는 status='pending' 고정.
  - feedback reason PII 가 마스킹 전 candidate 진입 → V4 저장 전 마스킹 + quality_filter 이중 방어(security-review §T5).
- **권장**:
  - ADR-031 §Decision 에 "feedback/selection → candidate_knowledge(source_kind, status='pending') 적재 경로 — 자동 승격 X(NG12), Phase 7 5단계 pending 정합" 명시.
  - security-review §T5 에 "feedback → candidate 적재 시 저장 전 마스킹 + quality_filter 전 PII 누출 차단" 명시.
  - Slice 4 `test_brand_memory_prep.py` 에 feedback→candidate 적재(pending + source_kind) + 자동 승격 0 케이스.

## 종합 판정

**Phase 9 entry 허용 — 7/7 PASS (V1~V7)**

| ID | 항목 | 결과 | 후속 조치 |
|---|---|---|---|
| V1 | selection/feedback 영속 (실 plans 정합) | PASS | ADR-030 §Constraints (plan_id + selected_option_index 0–2, idealized plan_options Phase 11+ NG2) |
| V2 | normalize_to_canonical wiring (canonical 추가 + 0–5 병행) | PASS | ADR-032 §Decision/§Constraints (canonical 추가 + deprecated 병행 + schemas/output.py 불변, 의도 delta 최소) |
| V3 | Brand Memory 준비 경계 (agent 미구현) | PASS | ADR-031 §Decision/§Constraints (준비만 + P-AUX-2 설계 명세 + Phase 10+ NG1 + pending NG12) |
| V4 | 피드백 reason PII (저장 전 마스킹) | PASS | security-review §T1 + ADR-030 §Constraints (§3.2 저장 전 마스킹 + E-SEC-006) |
| V5 | repo graceful (PlansRepo 패턴) | PASS | ADR-030/031 §Decision (Supabase or in-memory graceful) |
| V6 | 피드백 UI wrapper (PlanCard·component_map 0줄) | PASS | ADR-030 §References (page.tsx inline wrapper — Phase 4.5/5 계승) |
| V7 | feedback→candidate 적재 (Phase 7 pending 정합) | PASS | ADR-031 §Decision + security-review §T5 (source_kind pending + 자동 승격 X NG12) |

다음: Slice 2 sub-agent dispatch — Schema 0005(selected_plans + feedback_events + brand_memory_entries + RLS) + Repo 3종 graceful + contract-change(db_schema.md).

## 외부 검증 연계

self-validation 단일 모델 (Claude Code) 결과. 외부 검증 결과 (GPT/Gemini)는 `2026-05-29_phase-9-pre-entry_external.md` placeholder 에 사용자가 외부 진행 후 채울 수 있음.

Phase 9 는 보안 영향(피드백 reason PII 신규 저장 surface) + 데이터 모델 정합(실 plans vs idealized 4계층) 결정이 큰 phase → 외부 검증 권장. 단 Phase 4.5/6/5/5.5/7/8 패턴 계승으로 external placeholder 는 **사용자 외부 진행 권장** 형식 유지. self-validation V1~V7 PASS + self-strengthen V-form sub-pattern 가능성 명시. Phase 9 entry 진행 가능.

두 결과 차이 항목 발견 시:
- Phase 9 진행 중 `notes.md` 에 기록
- Slice 6 회고 §개선 제안 반영
- Critical 차이 (피드백 PII 저장 안전성 / normalize wiring 회귀 / Brand Memory 경계 변경 등) 시 Slice 2 진입 전 사용자 알림

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 7 self: `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS — 네 번째 formal)
- Phase 8 self: `meta/validations/2026-05-29_phase-8-pre-entry_self.md` (V1~V7 PASS — 다섯 번째 formal)
- Phase 9 self: 본 문서 (V1~V7 PASS — 여섯 번째 formal)
- Phase 9 external: `meta/validations/2026-05-29_phase-9-pre-entry_external.md` (placeholder)

## Skill 트리거 기록

- **multi-llm-validation**: 여섯 번째 formal 트리거 (Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째 + Phase 8 다섯째 + Phase 9 여섯째) → P-VALIDATION-FORMAL-001 정식 패턴 입증 강화 (6회 누적)
- **security-review**: 두 번째 정식 트리거 (Phase 5 첫 정식 + 두 번째 final 에 이은 — 피드백 reason PII + reject 사유 + RLS user 격리 + GET 피드백 권한 — T1~T6) → P-SECURITY-REVIEW-001 강화
- **phase-start**: 11번째 트리거 (Phase 1+2+3+4+4.5+6+5+5.5+7+8+9)
