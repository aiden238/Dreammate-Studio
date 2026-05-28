# Phase 6 Pre-Entry Multi-LLM Validation — Self (Claude Code)

> 검증 모델: Claude Code (자가, 지침 참조)
> 검증 일자: 2026-05-29
> 검증 유형: formal (두 번째 정식 트리거 — Phase 4.5 첫 + Phase 6 둘째)
> 외부 검증: `2026-05-29_phase-6-pre-entry_external.md` (별도 placeholder)

## 검증 대상

1. Critic verdict canonical 결정 (overall_score + dimensions vs 4가지 fallback)
2. Rewriter input/output contract 정식 등록 (P-008)
3. revise_history typing 강화 (List[dict] → List[ReviseAttempt])
4. fallback 축소 + deprecation note 정책
5. frontend types.ts ↔ backend schema 1:1 매핑

## 참조한 지침

- `harness/CLAUDE.md` § AI 구조 / 메타 개선 / 큰 결정
- `harness/AGENTS.md` (구현/QA 모델 라우터)
- `harness/docs/contracts/agent_io_contract.md` (현 상태 — Rewriter P-008 미등록)
- `harness/docs/contracts/output_schema.md` (현 상태 — Critic verdict 4 fallback / revise_history / recommended_plan_index 미명시)
- `harness/docs/contracts/mvp_non_goals.md`
- `harness/meta/patterns.md` (P-X1-EFFECT-001, P-X2-EFFECT-001, P-VALIDATION-FORMAL-001, P-GPT-REVIEW-001, P-GRACEFUL-001)
- Phase 4.5 archive `closing_notes.md` (Slice 3 sub-agent 보고: "여러 verdict 점수 구조 fallback" 명시)
- Phase 4 회고 proposals `meta/proposals/2026-05-28_phase-4-retrospective-proposals.md` §Z-X3
- Phase 6 entry files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes)
- 실 구현 참조: `backend/fastapi/agents/critic.py` (4 fallback chain: overall_score_avg → overall_score → scores → dimensions/eight_dim_scores)
- 실 구현 참조: `backend/fastapi/agents/rewriter.py` (dict 반환 패턴 + graceful `_rewriter_warning`)
- 실 구현 참조: `backend/fastapi/schemas/output.py` (Body.revise_history Optional[list[list[dict]]] / recommended_plan_index Optional[int])

## 검증 결과

### V1. Critic verdict canonical 결정 — PASS

- **현 구조** (Phase 4.5 baseline):
  - `agents/critic.py` 의 `run_critic` 출력: `overall_score_avg: float (0~5)` + `scores: dict[str,int]` (8 dim 정수 0~5)
  - `select_best_plan_index` fallback chain: `overall_score_avg` → `overall_score` → `scores` → `dimensions` → `eight_dim_scores` (4 fallback)
- **canonical 결정**: **`overall_score: float [0.0~1.0]` (정규화) + `dimensions: dict[str, float]`** 우선
  - 단순 평균이 아닌 명시적 `overall_score` 필드 (Critic이 직접 계산)
  - `dimensions` 는 8-dim 점수 dict (e.g., `{"hook_strength": 0.8, "target_clarity": 0.7, ...}`)
  - **호환성 주의**: 현 critic.py 의 `overall_score_avg` 는 0~5 float, canonical 안은 0~1 (정규화). 정규화 변환 (`avg/5.0`) 을 Slice 2 에서 명시.
- **fallback 축소** (Phase 6 정신 — NG12):
  - `overall_score` 만 우선, 나머지 (overall_score_avg, scores 평균, dimensions, eight_dim_scores) 는 `DeprecationWarning` 발행 + 임시 호환
  - 실 제거는 Phase 9+ eval-run Skill 정식화 후 (golden_set 회귀 검증 통과 시)
- **잠재 risk**:
  - 기존 critic.py 가 `overall_score` 키를 직접 안 갖는다는 점 → backward-compat 위해 fallback 의 `dimensions` 평균 → `overall_score` 변환 단계 추가 필요 (Slice 2 에서 명시)
  - 정규화 (0~5 → 0~1) 시점에 통계 비교 baseline (Phase 4.5 pytest 109/109) 회귀 0 확인 의무
- **권장**: ADR-018 (`docs/decisions/phase_6_critic_canonical.md`) 신규에 정규화 식 + fallback 전환 표 명시

### V2. Rewriter input/output contract — PASS

- **현 구조** (Phase 4.5 baseline):
  - `agents/rewriter.py` 의 `run_rewriter(plan, critic_verdict, *, model, client) -> dict`
  - 출력: 개선된 plan dict (원본 키 구조 유지, LLM 실패 시 `_rewriter_warning` 마커 + 원본 plan return — graceful)
  - prompt body 인라인 (NG7 → NG8 갱신: Phase 6+ 이관, Phase 7+ prompt_registry 정식화 후 본문 분리)
- **contract 정식 등록**: `agent_io_contract.md` §P-008 Rewriter 신규 (semver 1.0.0):
  - Input: `target_plan` (Plan 구조) + `critic_result` (CriticEvaluation 구조) + (선택) `selected_context` + `brand_memory`
  - Output: 개선된 `improved_plan` (Plan 100% 동일 구조) + `changes_made[]` + `remaining_concerns[]` + `_rewriter_warning?` (graceful 마커)
  - Failure: graceful — 원본 plan + `_rewriter_warning` 발행
  - 모델: gpt-4o-mini, temperature 0.4 (현 코드 일치), max_tokens 1500, max_retries 0 (revise loop 자체가 max 2)
- **prompt body 정식 작성은 Phase 7+ 이관** (NG8):
  - Phase 6 에서는 semver / io / rollback 골격만 contract 에 등록 + 본문은 인라인 유지
  - 단일 함수만 사용하므로 drift 위험 낮음
- **잠재 risk**:
  - Rewriter Pydantic 모델 도입 시 회귀 0 유지 의무 (현 dict 반환 → Pydantic model_dump() 변환 검증 필요)
  - graceful 마커 (`_rewriter_warning`) 가 Pydantic 모델에 명시되어야 하는가 vs envelope `validation.warnings` 로 이관 — Slice 2 결정
- **권장**: ADR-019 (`docs/decisions/phase_6_rewriter_contract.md`) 신규에 P-008 io + graceful 정책 + Pydantic 변환 호환 가이드

### V3. revise_history typing 강화 — PASS

- **현 구조** (Phase 4.5 baseline, schemas/output.py):
  ```python
  revise_history: list[list[dict[str, Any]]] | None = Field(default=None, ...)
  ```
  - 외부 list = plan_candidates 와 동일 plan index
  - 내부 list = attempt 순차 dict (예: `{attempt, action, revised, max_reached?, critic_warning?}`)
- **강화 (Phase 6)**: `ReviseAttempt` Pydantic 모델 신규
  - 필드: `attempt: int` (0~2) / `action: Literal["approve","revise","reject","unknown"]` / `revised: bool` / `max_reached: Optional[bool]` / `critic_warning: Optional[str]`
  - `Body.revise_history: Optional[list[list[ReviseAttempt]]]` typing
- **action enum drift 대응**:
  - Critic 이 미정의 action 반환 시 → "unknown" 폴백 (graceful)
  - 추후 새 action 추가 시 minor bump (output_schema.md §19.1 정합)
- **잠재 risk**:
  - 기존 dict-based revise_history 가 직렬화된 응답에 남아있을 경우 — Body.model_validate() 가 dict → ReviseAttempt 자동 변환되어야 함 (Pydantic v2 기본 동작 OK)
- **권장**: ADR-018 에 ReviseAttempt 모델 포함 (Critic canonical 과 같은 ADR 로 묶음) — typing 강화는 Critic 결정의 자연 follow-up

### V4. fallback 축소 + deprecation 정책 — PASS

- **현 fallback chain** (`select_best_plan_index` 4 fallback): `overall_score_avg` → `overall_score` → `scores` (8-dim 평균) → `dimensions/eight_dim_scores`
- **Phase 6 정책** (NG12 정합):
  - **`overall_score` + `dimensions` 만 우선** (canonical)
  - 나머지 fallback 은 `try/except` 블록으로 임시 호환 + `warnings.warn(DeprecationWarning, "<key> is deprecated; use overall_score + dimensions")` 발행
  - **즉시 제거 X** — Phase 9+ eval-run Skill 정식화 시 golden_set 회귀 통과 후 완전 제거 (개별 contract-change 절차)
- **테스트 의무**:
  - `tests/test_critic.py` 에 `pytest.deprecated_call()` 캡처 케이스 추가 (deprecation 무시 방지 — 회귀 검출 늦음 위험 완화)
- **잠재 risk**:
  - Pydantic `warnings.warn` 호출이 logger 와 충돌 (logging.captureWarnings vs warnings.simplefilter) — Slice 2 에서 단일 채널로 통일 권장
- **권장**: ADR-018 에 fallback 폐기 일정 명시 (Phase 9+ eval 통과 시점)

### V5. Frontend types.ts ↔ backend 1:1 매핑 — PASS

- **현 frontend `lib/types.ts`** (Phase 4.5 baseline):
  - `Body.recommended_plan_index: number | null | undefined` (Optional 추가 완료)
  - `Body.revise_history: any[][] | null | undefined` (현재 weak typing)
- **canonical 도입 (Phase 6 Slice 3)**:
  - `CriticVerdict` interface: `overall_score: number` + `dimensions: Record<string, number>` + 기존 키 (overall_verdict, blocking_issues 등)
  - `ReviseAttempt` interface: `attempt: number` + `action: "approve"|"revise"|"reject"|"unknown"` + `revised: boolean` + `max_reached?: boolean` + `critic_warning?: string`
  - `Body.revise_history?: ReviseAttempt[][]`
- **tsc 0 errors 유지**:
  - 모든 신규 필드는 Optional 또는 default
  - PlanCard.tsx 무수정 (10연속 목표) — types.ts 변경이 PlanCard prop 추가/수정으로 새지 않도록 wrapper UI 정신 유지
- **dimensions dict 직렬화 호환**:
  - Python `dict[str, float]` ↔ JSON object ↔ TypeScript `Record<string, number>` 직렬화 round-trip 검증 필수
  - schema_stress_test.ps1 (Slice 3 신규) 에 tsc round-trip 케이스 포함
- **잠재 risk**:
  - `recommended_plan_index: number | null` 과 backend `Optional[int]` 의 null vs undefined 호환 — Pydantic v2 default `None` ↔ JSON `null` 직렬화 검증 필요
- **권장**: schema_stress_test.ps1 에 `pytest test_schema_stress` + `tsc --noEmit` 동시 실행 의무

## 종합 판정

**Phase 6 entry 허용 — 5/5 PASS (V1~V5)**

다음: Slice 2 sub-agent dispatch — contract-change Skill 의무 호출 + Critic canonical + Rewriter contract + ADR-018/019.

## Contract gap analysis (현 상태 vs Phase 6 목표)

| 항목 | docs/contracts | 실 backend | 차이 | Slice 2 작업 |
|---|---|---|---|---|
| Critic verdict 구조 | `overall_score_avg` (§9.1) 명시, `overall_score` canonical X | 4 fallback (overall_score_avg → overall_score → scores → dimensions/eight_dim_scores) | Phase 6 canonical 결정 + contract 명시 필요 | output_schema.md §9 canonical 갱신 |
| revise_history | 미명시 (Phase 4.5 ADR-016) | `Optional[list[list[dict]]]` | contract 정식 등록 + `ReviseAttempt` typing | output_schema.md §body / §revise 신규 |
| recommended_plan_index | 미명시 (Phase 4.5 ADR-017) | `Optional[int]` | contract 정식 등록 | output_schema.md §body 신규 |
| Rewriter (P-008) | `agent_io_contract.md` §6 Rewriter Agent 존재 — input/output 스키마는 있으나 dict 반환 / graceful 정책 명시 X | `agents/rewriter.py` dict 반환 + `_rewriter_warning` graceful | agent_io_contract.md §6 강화 + Pydantic 모델 명시 | agent_io_contract.md §6 갱신 + ADR-019 |
| select_best_plan_index | 미명시 (코드만) | 4 fallback chain | fallback 축소 + deprecation note | output_schema.md §9 또는 §11 신규 |

> 참고: `agent_io_contract.md` §6 Rewriter Agent 가 v1.0.0 (2026-05-26) 에 이미 존재 — Phase 6 작업은 "신규 등록" 이 아니라 "Phase 4.5 구현 결과 (graceful, Pydantic 미도입) 와의 정합 강화" 임. ADR-019 는 강화 사유 명시.

## 외부 검증 연계

self-validation 단일 모델 (Claude Code) 결과. 외부 검증 결과 (GPT/Gemini) 는 `2026-05-29_phase-6-pre-entry_external.md` placeholder 에 사용자가 외부 진행 후 채울 수 있음.

Phase 5 진입 전 의무 작성 (Phase 4.5 패턴 계승). Phase 4.5 external placeholder 가 미작성이라 Phase 6 도 같은 형식으로 분리 작성.

두 결과 차이 항목 발견 시:
- Phase 6 진행 중 `notes.md` 에 기록
- Slice 4 회고 §개선 제안 반영
- Critical 차이 (canonical 결정 자체 변경) 시 Slice 2 진입 전 사용자 알림
