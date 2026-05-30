# Phase 9 Pre-Entry Multi-LLM Validation — External

> 검증 모델: (예: GPT-4o, Gemini-1.5-Pro 등) — **사용자가 외부에서 진행 후 작성**
> 검증 일자: (기록 시 채울 것)
> 검증 유형: formal — self-validation과 짝 (여섯 번째 정식 트리거)
> 본 문서: **placeholder** (외부 검증 결과 추가 대기)
> 보안/데이터 모델 영향: **MEDIUM~HIGH** (피드백 reason PII 신규 저장 surface + 실 plans vs idealized 4계층 정합 + normalize wiring) → 외부 검토 **권장**
> Skill 의무 트리거: **security-review (두 번째 정식 — 피드백 PII)** + multi-llm-validation (formal 여섯 번째)

## 작성 가이드

Phase 4.5/6/5/5.5/7/8 external placeholder 패턴 계승. 다음 항목을 외부 LLM (GPT/Gemini 등)에 다음 자료와 함께 제시한 후 결과를 기록.

### 외부 LLM에 제공할 자료

1. `harness/phases/active/phase-9-result-feedback/goals.md`
2. `harness/phases/active/phase-9-result-feedback/scope.md`
3. `harness/phases/active/phase-9-result-feedback/non_goals.md`
4. `harness/phases/active/phase-9-result-feedback/assumptions.md`
5. `harness/phases/active/phase-9-result-feedback/multi_slice_plan.md`
6. `harness/phases/active/phase-9-result-feedback/notes.md`
7. 본 self-validation 문서 (`2026-05-29_phase-9-pre-entry_self.md`)
8. `harness/meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` (security-review 두 번째 정식 — T1~T6)
9. `harness/docs/decisions/phase_9_feedback_selection.md` (ADR-030 — feedback/selection persistence)
10. `harness/docs/decisions/phase_9_brand_memory_prep.md` (ADR-031 — Brand Memory 준비 + P-AUX-2 설계)
11. `harness/docs/decisions/phase_9_critic_canonical_wiring.md` (ADR-032 — normalize_to_canonical wiring)
12. `harness/docs/contracts/db_schema.md` (§3.6 plans 실 테이블 + §4.3 selected_plans + §5.2 feedback_events + §6 brand_memory_entries + §7.2 candidate_knowledge)
13. `harness/docs/contracts/llm_security_contract.md` (§3.2 PII 마스킹 + §8 E-SEC-006)
14. `harness/ai_system/prompts/prompt_registry.md` (P-AUX-2 brand_memory_extractor 명세 — 활성 Phase 9+)
15. `harness/backend/fastapi/agents/critic.py` (`normalize_to_canonical` helper — additive 비강제 주입)
16. `harness/backend/fastapi/db/repositories/plans_repo.py` (graceful 패턴 — selection/feedback repo 모델)
17. (선택) `harness/.claude/skills/security-review/SKILL.md` (영역 1~10 절차)
18. (선택) `harness/.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

### 외부 LLM에 물을 질문 (V1~V7)

1. **V1 selection/feedback 영속 (실 plans 정합)**:
   - 결과 저장을 db_schema §4.3 idealized `selected_plans`(selected_option_id → plan_options)가 아니라 실 `plans` 테이블 정합(plan_id + selected_option_index 0–2 + plan_candidates JSONB)으로 구현하는 것이 합리적인가?
   - 4계층 full linkage(plan_options 테이블)를 Phase 11+로 미루는 결정(NG2)이 데이터 모델 건전성에 문제 없는가?
   - selected_option_index 0–2 + plan_id 가 선택 plan 식별에 충분한가?

2. **V2 normalize_to_canonical wiring (canonical 추가 + 0–5 병행)**:
   - critic step 에 canonical(0–1) 추가 + deprecated(0–5) 병행 유지가 회귀 0인가?
   - schemas/output.py CriticEvaluation 불변(이미 Optional canonical) 전제가 옳은가?
   - "wiring 김에 0–5 제거"를 Phase 9.5 eval(NG3)로 미루는 결정이 합리적인가?
   - 의도된 critic_evaluation delta(baseline assertion 최소 갱신, Phase 8 Slice 4 패턴) 경계가 적절한가?

3. **V3 Brand Memory 준비 경계 (agent 미구현 Phase 10+)**:
   - schema + ADR + 적재 경로만 준비하고 P-AUX-2 agent 는 구현하지 않는 경계(사용자 결정 5)가 명확한가?
   - P-AUX-2 설계 명세(input/output/활성화 조건)만 ADR 에 남기고 실행 0인 것이 적절한가?
   - feedback → candidate_knowledge 적재를 pending 까지만(자동 승격 X — NG12)로 제한하는 것이 옳은가?

4. **V4 피드백 reason text PII (저장 전 마스킹 vs 조회 시)**:
   - 자유 입력 피드백 reason 의 PII(이메일/전화 등)를 저장 전 마스킹 vs 조회 시 마스킹 — 어느 쪽이 안전한가?
   - LLM 호출 없이 직접 DB 저장되는 신규 surface 에 llm_security §3.2 baseline 적용이 충분한가?
   - 한국어/영어 혼용 PII 정규식 false negative 대응 권장(라이브러리/시점)?

5. **V5 repo graceful (PlansRepo 패턴)**:
   - SelectionRepo/FeedbackRepo/BrandMemoryRepo graceful(Supabase or in-memory) 패턴이 적절한가?
   - in-memory fallback 시 RLS user 격리 미적용(mock 환경)이 보안 위험인가?

6. **V6 피드백 UI wrapper (PlanCard·component_map 0줄)**:
   - 선택 버튼 + 반려 이유 입력을 page.tsx inline wrapper 로 추가(신규 component X)하는 것이 유지보수성에 문제 없는가?
   - component_map 0줄 유지를 위해 component 추출을 막는 것이 과도한가?

7. **V7 feedback → candidate_knowledge 적재 (Phase 7 pending 정합)**:
   - feedback/selection → candidate(source_kind pending) 적재가 Phase 7 5단계 pending 진입점과 정합한가?
   - 자동 승격(NG12) 차단 + quality_filter 전 PII 누출(security-review §T5) 방어가 충분한가?

### 결과 기록 형식 (Phase 4.5/6/5/7/8 패턴 계승)

```
## V1. (외부 LLM 응답)
- 일치 / 차이 / 추가 risk:
- 권장 조치:

## V2. ...
## V3. ...
## V4. ...
## V5. ...
## V6. ...
## V7. ...

## 종합 판정 (외부 LLM)
- Phase 9 entry 허용 / 보류 / 차단:
- 차이 항목이 있을 때 Phase 9 notes.md 갱신 필요 여부:
- Slice 2 schema/repo (실 plans 정합) 영향 여부:
- Slice 3 normalize wiring 영향 여부:
- Slice 4 Brand Memory 적재 경로 영향 여부:
```

### Security-focused 추가 질문 (선택)

`meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` (security-review 두 번째 정식) 본문에 대해 외부 LLM 견해:

- **S1 피드백 reason PII**: 저장 전 마스킹 시점 + false negative 대응 권장?
- **S2 reject 사유 저장**: 민감 정보(불만/감정 등) 저장 retention 정책 권장?
- **S3 RLS user 격리**: feedback_events.user_id = auth.uid() 정책 우회 surface?
- **S4 GET /plans/{id}/feedback 권한**: 본인 plan 만 조회 — 우회 가능 경로?
- **S5 feedback → candidate PII 누출**: RAG 승격 전 quality_filter 가 PII 차단에 충분한가?

---

**현재 상태**: placeholder — 사용자가 외부 GPT/Gemini 검증 후 결과 추가 예정.

Phase 9 는 self-validation V1~V7 PASS + security-review Skill 두 번째 정식 트리거 (피드백 PII T1~T6) 결과로 entry 진행. 외부 검증 결과는 추후 추가되어도 본 phase 진행에 영향 X (단, 차이 항목 발견 시 notes.md 또는 Slice 6 회고에 반영).

**보안/데이터 모델 영향이 있는 phase**이므로 사용자 외부 진행 **권장**. 외부 검토 결과 Critical 차이(피드백 PII 저장 안전성 / normalize wiring 회귀 / Brand Memory 경계 등) 발견 시 Slice 2 진입 전 사용자 알림 + 차단 검토.

**의무 작성 시점**: Phase 9 Slice 1 entry (현 시점, placeholder). Phase 9 종료 시점에 본 placeholder 가 채워지지 않으면 multi-llm-validation formal external 의무 위반 — 다음 phase entry 4-check 에서 차단.

**self-strengthen 패턴 가능성**: Phase 5.5 에서 Phase 4.5/6/5 external placeholder 에 self-strengthen V-form(Claude Code 자가 검토 형식 — V1~V_n self-question + self-answer + 합의 추정)으로 강화한 사례가 있음. Phase 9 external 도 사용자 외부 진행 전에 self-strengthen V-form 추가 가능 (단, 본 Slice 1 에서는 외부 진행 자체 우선 권장).

## Cross-reference (이전 Phase validations)

- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 5 external: `meta/validations/2026-05-29_phase-5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 7 external: `meta/validations/2026-05-29_phase-7-pre-entry_external.md` (placeholder)
- Phase 8 external: `meta/validations/2026-05-29_phase-8-pre-entry_external.md` (placeholder)
- Phase 9 self: `meta/validations/2026-05-29_phase-9-pre-entry_self.md` (V1~V7 PASS — 여섯 번째 formal)
- Phase 9 external: 본 문서 (placeholder)
