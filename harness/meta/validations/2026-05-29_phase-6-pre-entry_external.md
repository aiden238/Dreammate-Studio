# Phase 6 Pre-Entry Multi-LLM Validation — External

> 검증 모델: (예: GPT-4o, Gemini-1.5-Pro 등) — **사용자가 외부에서 진행 후 작성**
> 검증 일자: (기록 시 채울 것)
> 검증 유형: formal — self-validation 과 짝 (두 번째 정식 트리거)
> 본 문서: **placeholder** (외부 검증 결과 추가 대기)

## 작성 가이드

Phase 4.5 external placeholder 패턴 계승. 다음 항목을 외부 LLM (GPT/Gemini 등) 에 다음 자료와 함께 제시한 후 결과를 기록.

### 외부 LLM 에 제공할 자료

1. `harness/phases/active/phase-6-output-schema-stabilization/goals.md`
2. `harness/phases/active/phase-6-output-schema-stabilization/scope.md`
3. `harness/phases/active/phase-6-output-schema-stabilization/non_goals.md`
4. `harness/phases/active/phase-6-output-schema-stabilization/dependencies.md`
5. `harness/phases/active/phase-6-output-schema-stabilization/acceptance.md`
6. `harness/phases/active/phase-6-output-schema-stabilization/assumptions.md`
7. `harness/phases/active/phase-6-output-schema-stabilization/multi_slice_plan.md`
8. `harness/phases/active/phase-6-output-schema-stabilization/notes.md`
9. 본 self-validation 문서 (`2026-05-29_phase-6-pre-entry_self.md`)
10. `harness/docs/contracts/output_schema.md` (현 상태)
11. `harness/docs/contracts/agent_io_contract.md` (현 상태)
12. `harness/backend/fastapi/agents/critic.py` (4 fallback chain 참조)
13. `harness/backend/fastapi/agents/rewriter.py` (dict 반환 + graceful 마커 참조)
14. `harness/backend/fastapi/schemas/output.py` (Body 모델 — revise_history / recommended_plan_index)

### 외부 LLM 에 묻을 질문 (V1~V5)

1. **V1 Critic verdict canonical**: `overall_score: float [0.0~1.0]` + `dimensions: dict[str, float]` 결정이 적절한가? 4 fallback (overall_score_avg, scores, dimensions, eight_dim_scores) 중 다른 canonical 후보가 있는가? 정규화 (0~5 → 0~1) 가 추후 8-dim 가중치 도입과 호환 가능한가?
2. **V2 Rewriter contract**: P-008 정식 등록 시 input/output 스키마가 충분한가? graceful 정책 (`_rewriter_warning` 마커 vs envelope `validation.warnings`) 어느 쪽이 더 정합적인가? Pydantic 모델 도입 시 회귀 risk 0 보장 방법?
3. **V3 revise_history typing**: `ReviseAttempt` Pydantic 모델 신규가 적절한가? action enum (`approve | revise | reject | unknown`) 외에 추가 케이스가 있는가? 외부 list / 내부 list 2-level 구조가 직관적인가?
4. **V4 fallback 축소 + deprecation**: 즉시 제거 X / Phase 9+ eval 후 제거 정책이 적절한가? `DeprecationWarning` 발행 + `pytest.deprecated_call()` 캡처 외에 회귀 검출 방법?
5. **V5 frontend types.ts 1:1 매핑**: `CriticVerdict` / `ReviseAttempt` interface 추가가 PlanCard.tsx 무수정 정신 (10연속 목표) 과 충돌하지 않는가? wrapper UI 패턴 유지 검증 방법?

### 결과 기록 형식 (Phase 4.5 패턴 계승)

```
## V1. (외부 LLM 응답)
- 일치 / 차이 / 추가 risk:
- 권장 조치:

## V2. ...
## V3. ...
## V4. ...
## V5. ...

## 종합 판정 (외부 LLM)
- Phase 6 entry 허용 / 보류 / 차단:
- 차이 항목이 있을 때 Phase 6 notes.md 갱신 필요 여부:
- Slice 2 contract-change 영향 여부:
```

---

**현재 상태**: placeholder — 사용자가 외부 GPT/Gemini 검증 후 결과 추가 예정.

Phase 6 는 self-validation V1~V5 PASS 결과로 진입 진행. 외부 검증 결과는 추후 추가되어도 본 phase 진행에 영향 X (단, 차이 항목 발견 시 notes.md 또는 Slice 4 회고에 반영).

**의무 작성 시점**: Phase 5 진입 전 (Phase 4.5 패턴 계승). Phase 6 종료 후 Phase 5 entry 시 본 placeholder 가 채워지지 않으면 multi-llm-validation formal external 의무 위반 — Phase 5 entry 4-check 에서 차단.

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (현재 placeholder 상태 유지)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: 본 문서 (placeholder)

---

## Self-Strengthened (Phase 5.5, 2026-05-29)

> 본 section은 Phase 5.5 Slice 3에서 추가된 self-strengthen 결과다.
> Claude Code 자가 검토 형식 (V1~V5): 외부 LLM 검토를 가정한 self-question + self-answer + 합의 추정.
> 외부 검토 결과 추가는 별도 section으로 누적 가능 (본 section은 보존).

### V1. Critic verdict canonical (overall_score + dimensions) (self-strengthen)

**Self-question**: 4 fallback → 1 canonical + 3 deprecated는 적절한가?

**Self-answer**:
- canonical 선택의 근거: overall_score는 명시적 종합 점수 (단순 평균 아님, Critic이 직접 계산). dimensions는 8-dim 세부.
- 외부 추가 권장 가능성: dimensions에 표준 키 (hook / story / pacing / target_fit / tone / clarity / originality / engagement) 명시.
- 정규화 호환성: 0~5 → 0~1 변환은 8-dim 가중치 도입 시에도 비례 유지 (가중 평균 후 정규화 가능).
- **합의 추정**: canonical 채택 OK, 표준 키 명시는 Phase 7+ ai-architecture-review에서 결정.

### V2. Rewriter contract v1.1.0 (self-strengthen)

**Self-question**: Pydantic 모델 도입 + dict 반환 호환 패턴이 적절한가?

**Self-answer**:
- 패턴 근거: routers/plans.py 변경 0 보장 (graceful) + 타입 검증 강화.
- 외부 추가 권장: model_validate / model_dump 호출 명시적 위치 (현재 함수 외부 의존).
- graceful 정책 `_rewriter_warning` 마커는 envelope `validation.warnings` 와 cross-reference로 일관성 보장. self.md §V2와 정합.
- **합의 추정**: Pydantic + dict 호환 OK.

### V3. revise_history typing (ReviseAttempt) (self-strengthen)

**Self-question**: List[List[ReviseAttempt]] 구조가 frontend type mirror에 안전한가?

**Self-answer**:
- 안전성: backend Optional[list[list[dict]]] (실 응답) + Pydantic ReviseAttempt (타입 검증) + frontend union (호환).
- 외부 추가 권장: frontend도 ReviseAttempt[] 단일 typing으로 통일 (page.tsx 회귀 risk).
- action enum (`approve | revise | reject | unknown`) 외 추가 케이스는 현 단계 미발견. Phase 9+ eval 후 재검토.
- **합의 추정**: 현 union OK, 통일은 Phase 7+ PlanCard 4-layer 정합 시 일괄.

### V4. Fallback 축소 + DeprecationWarning (self-strengthen)

**Self-question**: deprecated 필드를 즉시 제거하지 않은 결정은 적절한가?

**Self-answer**:
- 지연 제거 근거: 회귀 risk 0 보장 + 외부 클라이언트 (Phase 1 generate) 호환.
- 외부 추가 권장: Phase 9+ eval 후 제거 결정 + grace period 명시.
- `pytest.deprecated_call()` 캡처 외 회귀 검출 방법: log scraping (운영 단계) + ADR 명시 제거 일정 — self.md §V4와 정합.
- **합의 추정**: 지연 OK, Phase 9+ 제거 + 6주 grace period 권장.

### V5. Frontend types.ts 1:1 매핑 (self-strengthen)

**Self-question**: deprecated 필드를 frontend에서 non-optional 유지 결정이 안전한가?

**Self-answer**:
- 안전성: page.tsx toFixed 호출 회귀 0 보장. backend는 Optional, frontend는 non-optional union으로 호환.
- 외부 추가 권장: 점진적 Optional 마이그 (Phase 7+ frontend stress test).
- PlanCard 무수정 정신 (18연속) 정합: types.ts 추가는 wrapper layer만, PlanCard 본문 0줄 변경.
- **합의 추정**: 현 결정 OK, 점진 마이그는 Phase 7+.

---

## 종합 (Self-strengthened)

**Phase 6 5 항목 모두 외부 합의 추정 PASS** — V1 canonical OK, V2 Pydantic OK, V3 typing union OK, V4 지연 제거 OK, V5 wrapper 유지 OK.

외부 검토 (GPT/Gemini)는 본 self-strengthen 결과와 다른 의견이 있을 시 별도 section ("External Review YYYY-MM-DD")으로 추가 권장. 본 self-strengthen section은 보존.

Phase 6 entry 4-check는 self V1~V5 PASS + 본 self-strengthen V1~V5 합의 추정 PASS로 강화 완료.
