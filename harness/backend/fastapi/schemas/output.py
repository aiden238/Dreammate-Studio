"""Output schemas — output_schema.md v1.0 envelope.

준수 사항:
  - meta / body / validation 3섹션 envelope (§2)
  - body.plans 배열 (P-006, §8)
  - JSON 1개 객체만 응답 (자연어 머리말/꼬리말 금지)

Phase 1 Slice 1 단순화 (Deviation from contract, documented):
  - plans 길이: 1개 (vs contract 3개) → validation.warnings에 표기
  - rag_used: 빈 배열 (Slice 4에서 채움)
  - approach_label: 단일 값 허용

Slice 2 추가:
  - ErrorEnvelope (error_response_contract.md §1 정합) 활성화
  - Intent 차단 시 INV-001 코드로 반환

Slice 3 추가:
  - CriticScores / CriticEvaluation (output_schema.md §9 정합)
  - body.critic_evaluation 필드 활성화 (Phase 1: 평가만, revise 없음)

Slice 4 추가:
  - body.rag_references (RAGReference 배열) — rag_data_contract.md §5.5 정합
  - validation.warnings에서 "phase_1_no_rag" 제거
  - validation.checks에 "rag_retrieval" 항목 추가 (status=ok/warn)

Slice 5 추가:
  - Meta.project_id (Optional) — Supabase 저장 성공 시 video_projects.id, 실패/skip 시 None
  - validation.checks에 "db_persistence" 항목 추가 (status=ok/warn)
  - DB 실패는 사용자 차단 금지 (graceful 정책 — Slice 4 RAG 와 동일)

Phase 6 Slice 2 추가 (ADR-018 / ADR-019):
  - ReviseAttempt Pydantic 모델 — typing 검증 + frontend mirror 용 standalone export
    (attempt / action / revised / max_reached / critic_warning / rewriter_warning)
    Note: Body.revise_history 직렬화는 dict 유지 (Phase 4.5 응답 호환성 — None 키 미노출).
          Pydantic 모델은 stress test / frontend type generation 에 사용.
  - CriticEvaluation canonical 필드 추가 (overall_score: float [0~1], dimensions: dict[str, float])
    - 기존 Phase 1 필드 (target_plan_id / scores / overall_score_avg) 는 deprecated 표시,
      backward-compat 위해 Optional 로 유지 (Phase 9+ eval 후 제거 예정).

Phase 9.5 Slice 4 변경 (ADR-034 — deprecated 0–5 Full 제거):
  - CriticEvaluation 에서 deprecated 0–5 필드(scores / overall_score_avg) 제거.
    canonical(overall_score 0–1 + dimensions) 만 유지. target_plan_id / reasons /
    suggestions 는 Phase 1 호환 메타로 잔존 (0–5 점수와 무관).
  - model_config extra='ignore' 명시 — orchestrator 가 normalize_to_canonical 산출
    verdict dict(run_critic 0–5 키 scores / overall_score_avg 병행)를 CriticEvaluation(**verdict)
    로 넘겨도 deprecated 0–5 키를 무시하고 canonical 만 추출 → 회귀 0.
  - run_critic 의 0–5 출력(scores + overall_score_avg) 은 P-007 prompt contract 로 불변
    (LLM-facing). CriticScores 모델도 run_critic 산출 typing 용으로 유지.

Phase 13 Slice 1 추가 (CC-012 — output_schema rich 슬롯 additive):
  - Plan rich 9종(PLAN_RICH_FIELDS: target_audience / tone / hook_variants / shots /
    thumbnail / title_candidates / cta / references / length_variants) +
    PlanFlowBeat rich 3종(BEAT_RICH_FIELDS: visual / dialogue / caption) 추가.
  - ★ 전부 Optional default None/[] → 기존 7필드(+rag_used)·소비자 회귀 0 (additive).
  - rich 값은 flag ON(rich_output_enabled, S3) 경로에서만 채워진다. OFF 경로는
    Plan.model_dump_compact() 가 rich 키를 제외 → compact 출력 byte-identical (A5-PP).
  - 깊이 격차 근거: eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md
    (compact depth 0.231 / rich 1.000 — 결핍 10 feature 중 7개가 스키마 슬롯 부재).
"""

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

# Slice 4: RAGReference 는 rag/types.py가 단일 출처 (순환 import 회피용 lazy ref X —
# rag/types.py는 schemas를 import하지 않으므로 안전).
from ..rag.types import RAGReference


# ─── Meta ─────────────────────────────────────────────────────────────

class Meta(BaseModel):
    """envelope meta (output_schema.md §2)."""

    request_id: str = Field(..., description="uuid v4")
    prompt_id: str = Field(
        ...,
        description="P-001 ~ P-008 / P-AUX-1 / P-AUX-2 / P-PHASE1-COMBINED (Phase 1 임시)",
    )
    prompt_version: str = Field(
        ...,
        description="semver e.g. v1.0.0",
    )
    model: str = Field(..., description="LLM 모델명")
    generated_at: str = Field(..., description="ISO8601 UTC")
    locale: str = Field(default="ko-KR")
    schema_version: str = Field(default="1.0.0", description="output_schema.md semver")
    project_id: str | None = Field(
        default=None,
        description=(
            "Slice 5: Supabase video_projects.id (저장 성공 시 uuid). "
            "DB 미연결 / 저장 실패 시 None — 사용자 응답은 정상 200 유지 (graceful 정책)."
        ),
    )

    @classmethod
    def make(
        cls,
        *,
        prompt_id: str,
        prompt_version: str,
        model: str,
        locale: str = "ko-KR",
        request_id: str | None = None,
        project_id: str | None = None,
    ) -> "Meta":
        """기본값으로 Meta 생성.

        Slice 5: request_id를 외부에서 주입 가능 (DB save 시 video_projects.request_id와 일치시키기 위함).
        project_id 는 DB 저장 성공 시에만 채워진다 (skip/fail 시 None).
        """
        return cls(
            request_id=request_id or str(uuid4()),
            prompt_id=prompt_id,
            prompt_version=prompt_version,
            model=model,
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            locale=locale,
            project_id=project_id,
        )


# ─── Body (Plans) ─────────────────────────────────────────────────────

class PlanFlowBeat(BaseModel):
    """plan.flow의 한 비트 (output_schema.md §8.1).

    Phase 13 S1 (CC-012, additive): rich 슬롯 3종(visual/dialogue/caption) 추가.
      - 전부 Optional default None → 기존 4필드(beat_index/beat/duration_sec/purpose)
        직렬화·소비자 회귀 0. rich 값은 flag ON(rich_output_enabled, S3) 경로에서만 채워짐.
    """

    beat_index: int = Field(..., ge=0)
    beat: str = Field(..., min_length=1)
    duration_sec: int = Field(..., ge=1)
    purpose: str = Field(..., min_length=1)
    # ── Phase 13 S1 rich (additive, Optional — flag ON 경로에서만 채워짐) ──
    visual: str | None = Field(
        default=None,
        description="rich(Phase 13): 화면/구도/연출 묘사 (beat 라벨보다 구체적 화면 지시).",
    )
    dialogue: str | None = Field(
        default=None,
        description="rich(Phase 13): 내레이션·대사.",
    )
    caption: str | None = Field(
        default=None,
        description="rich(Phase 13): 자막 텍스트.",
    )


# ── Phase 13 S1 (CC-012): rich 슬롯 이름 집합 ──
# S3 gated wiring(rich_output_enabled OFF 경로)이 model_dump_compact() 를 호출하여
# 이 필드들을 직렬화에서 제외 → 기존 compact 출력 byte-identical (acceptance A5-PP).
PLAN_RICH_FIELDS: frozenset[str] = frozenset(
    {
        "target_audience",
        "tone",
        "hook_variants",
        "shots",
        "thumbnail",
        "title_candidates",
        "cta",
        "references",
        "length_variants",
    }
)
BEAT_RICH_FIELDS: frozenset[str] = frozenset({"visual", "dialogue", "caption"})


class Plan(BaseModel):
    """plan_candidate 1개 (output_schema.md §8.1).

    Phase 1: approach_label 단일 값 허용 (3개 plan 미생성).

    Phase 13 S1 (CC-012, additive): rich 슬롯 9종 추가 (PLAN_RICH_FIELDS) +
      PlanFlowBeat rich 3종(BEAT_RICH_FIELDS). 전부 Optional default None/[] →
      기존 7필드(name/concept/hook/flow/pros/risks/approach_label) + rag_used 직렬화·
      소비자(orchestrator/Critic/Rewriter/PlanCard) 회귀 0. rich 값은 flag ON
      (rich_output_enabled, S3) 경로에서만 채워지고, OFF 경로는 model_dump_compact()
      로 rich 키를 제외해 byte-identical 유지.
    """

    plan_id: str = Field(..., description="uuid")
    option_index: int = Field(..., ge=0, le=2)
    name: str = Field(..., min_length=1, max_length=20)
    concept: str = Field(..., min_length=1)
    hook: str = Field(..., min_length=10, max_length=80)
    flow: list[PlanFlowBeat] = Field(..., min_length=2, max_length=8)
    pros: str = Field(default="")
    risks: str = Field(default="")
    approach_label: Literal[
        "narrative",
        "informational",
        "empathy",
        "experiment",
        "review",
        "other",
    ] = "informational"
    rag_used: list[dict[str, Any]] = Field(default_factory=list)

    # ── Phase 13 S1 rich (additive, Optional — flag ON 경로에서만 채워짐) ──
    target_audience: str | None = Field(
        default=None, description="rich(Phase 13): 타깃 시청자."
    )
    tone: str | None = Field(default=None, description="rich(Phase 13): 톤·무드.")
    hook_variants: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="rich(Phase 13): 후크 변형 (기존 단일 hook 외 추가, ≤3).",
    )
    shots: list[str] = Field(
        default_factory=list, description="rich(Phase 13): B-roll/샷 리스트."
    )
    thumbnail: str | None = Field(
        default=None, description="rich(Phase 13): 썸네일 컨셉."
    )
    title_candidates: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="rich(Phase 13): 제목 후보 (≤5).",
    )
    cta: str | None = Field(
        default=None, description="rich(Phase 13): Call-to-action."
    )
    references: list[str] = Field(
        default_factory=list,
        max_length=5,
        description="rich(Phase 13): 창작 레퍼런스 (rag_used = RAG 출처와 구분, ≤5).",
    )
    length_variants: list[str] = Field(
        default_factory=list,
        description="rich(Phase 13): 길이 변형 (예: 30s/60s 컷).",
    )

    def model_dump_compact(self, **kwargs: Any) -> dict[str, Any]:
        """Phase 13 S1 (CC-012, 결정 3): rich 슬롯을 제외한 compact 직렬화.

        S3 gated wiring 의 OFF 경로(rich_output_enabled=False)가 이 메서드로 직렬화하면
        Phase 12 이전의 7필드(+rag_used) 출력과 byte-identical 하다 (acceptance A5-PP).
        flow 의 beat rich 3종(visual/dialogue/caption)도 함께 제외한다.

        ★ S1 은 이 capability 만 제공·검증한다 — 실제 호출(OFF 경로 분기)은 S3.
        """
        exclude: dict[str, Any] = {name: True for name in PLAN_RICH_FIELDS}
        exclude["flow"] = {"__all__": {name: True for name in BEAT_RICH_FIELDS}}
        return self.model_dump(exclude=exclude, **kwargs)


class CriticScores(BaseModel):
    """Critic 8 차원 점수 (output_schema.md §9.1)."""

    intent_fit: int = Field(..., ge=0, le=5)
    target_clarity: int = Field(..., ge=0, le=5)
    hook_strength: int = Field(..., ge=0, le=5)
    message_clarity: int = Field(..., ge=0, le=5)
    structure: int = Field(..., ge=0, le=5)
    feasibility: int = Field(..., ge=0, le=5)
    brand_consistency: int = Field(..., ge=0, le=5)
    differentiation: int = Field(..., ge=0, le=5)


class CriticEvaluation(BaseModel):
    """Critic 평가 결과 (output_schema.md §9.1 + Phase 6 canonical ADR-018).

    Phase 1: revise_round 항상 0 (revise 호출 없음).
    overall_verdict는 평가만 노출 (Phase 4+에서 revise 트리거로 사용).

    Phase 6 (ADR-018) canonical 필드:
      - overall_score: float [0.0~1.0] (정규화된 종합 점수) — canonical
      - dimensions: dict[str, float] — 8-dim 점수 dict — canonical

    Phase 1 호환 메타 (0–5 점수와 무관 — 잔존):
      - target_plan_id / reasons / suggestions

    Phase 9.5 Slice 4 (ADR-034): deprecated 0–5 필드(scores / overall_score_avg) 제거 완료.
      orchestrator 가 normalize_to_canonical 산출 verdict dict(0–5 키 병행)를 그대로
      CriticEvaluation(**verdict) 로 넘겨도 model_config extra='ignore' 가 0–5 키를 무시하고
      canonical 만 추출한다 (회귀 0). run_critic 의 0–5 출력은 LLM-facing P-007 contract 로 불변.
    """

    model_config = {"extra": "ignore"}  # ADR-034: verdict dict 의 deprecated 0–5 키(scores /
    # overall_score_avg) 를 무시 (Pydantic v2 default 이나 명시) → CriticEvaluation(**verdict) 회귀 0.

    # Phase 6 canonical (ADR-018) — 신규 필드
    overall_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Phase 6 canonical (ADR-018): Critic 종합 점수 (정규화 0.0~1.0). "
            "Phase 9+ 에서 dimensions 가중치 도입 시 단순 평균이 아닌 weighted score 로 확장."
        ),
    )
    dimensions: dict[str, float] = Field(
        default_factory=dict,
        description=(
            "Phase 6 canonical (ADR-018): 8-dim 점수 dict[str, float] "
            "(예: {'hook_strength': 0.8, 'target_clarity': 0.7, ...}). "
            "정규화 0.0~1.0 (Phase 9.5 ADR-034 으로 0~5 정수 scores 필드는 제거됨)."
        ),
    )

    # Phase 1 호환 메타 (0–5 점수와 무관 — 잔존)
    target_plan_id: str | None = Field(
        default=None,
        description="Phase 1 호환 (output_schema.md §9.1) — plan_id echo back.",
    )
    reasons: dict[str, str] = Field(default_factory=dict)
    suggestions: dict[str, str] = Field(default_factory=dict)
    overall_verdict: Literal["approve", "revise", "reject"]
    blocking_issues: list[str] = Field(default_factory=list, max_length=3)
    revise_round: int = Field(default=0, ge=0)


# ─── Phase 6 Slice 2: ReviseAttempt (ADR-018 typing 강화) ─────────────

class ReviseAttempt(BaseModel):
    """Phase 4.5 Slice 2 revise loop attempt log — Phase 6 typing 강화 (ADR-018).

    routers/plans.py 의 `_critic_revise_for_plan` 가 attempt 별로 dict 를 누적하던 것을
    Phase 6 에서 Pydantic 모델로 강화. backward-compat 위해 Body.revise_history 가
    list[list[ReviseAttempt]] 로 변경되어도 Pydantic v2 가 dict → 모델 자동 변환하므로
    routers 변경 없이 호환된다 (회귀 0).

    Fields:
      - attempt: int [0~max_revise]. 0 = 초기 critic, 1+ = revise 후 재평가.
      - action: Literal — Critic verdict. "unknown" 은 Critic 이 미정의 값 반환 시 폴백.
      - revised: bool — 본 attempt 에서 Rewriter 호출 여부.
      - max_reached: Optional[bool] — max_revise 도달 시 True.
      - critic_warning: Optional[str] — Critic 호출 실패 graceful 마커.
      - rewriter_warning: Optional[str] — Rewriter 호출 실패 graceful 마커.
    """

    attempt: int = Field(..., ge=0)
    action: Literal["approve", "revise", "reject", "unknown"]
    revised: bool
    max_reached: bool | None = None
    critic_warning: str | None = None
    rewriter_warning: str | None = None

    model_config = {"extra": "allow"}  # 미래 확장 메타 허용 (typing drift 방지)


class Body(BaseModel):
    """envelope body — Phase 1 Slice 4 + Phase 4 Slice 2 + Phase 4.5 Slice 2 구조.

    Slice 1 (Phase 1): plans 길이 1 (vs contract 3). validation.warnings에 phase_1_single_plan.
    Slice 3 (Phase 1): critic_evaluation 활성화 (revise 없음).
    Slice 4 (Phase 1): rag_references 활성화 (fallback 시 빈 배열).
    Slice 2 (Phase 4): plan_candidates max_length=3 enforce 활성 (3-plan 본격).
                       Phase 1 호환 위해 min_length=1 유지 (Phase 1 endpoint 1-plan).
    Slice 2 (Phase 4.5): revise_history Optional 추가 — plan별 revise attempt log.
                          외부 list = plan index, 내부 list = attempt 순차 dict.
                          Optional 필드 추가이므로 회귀 0 (output_schema.md 호환).
    """

    plan_candidates: list[Plan] = Field(..., min_length=1, max_length=3)
    critic_evaluation: CriticEvaluation | None = Field(
        default=None,
        description="Phase 1 Slice 3: 평가만 (revise 없음). Phase 4+에서 list로 확장.",
    )
    rag_references: list[RAGReference] = Field(
        default_factory=list,
        description=(
            "Phase 1 Slice 4: RAG 검색 결과 (fallback 시 빈 배열). "
            "rag_data_contract.md §5.5 정합 — chunk_id / title / similarity 등 메타 포함."
        ),
    )
    revise_history: list[list[dict[str, Any]]] | None = Field(
        default=None,
        description=(
            "Phase 4.5 Slice 2 (ADR-016) / Phase 6 typing canonical 명시 (ADR-018): "
            "plan별 revise attempt log. "
            "외부 list = plan index (plan_candidates 와 동일 순서), "
            "내부 list = attempt 0,1,2,... 순차 dict "
            "(canonical Pydantic 모델 = `ReviseAttempt` — typing 검증 + frontend mirror 용 export. "
            "Body 직렬화는 dict 유지 — JSON 응답 키 호환성 (None 키 미노출, Phase 4.5 호환)). "
            "loop 비활성 또는 Phase 4 이하 호출 시 None."
        ),
    )
    recommended_plan_index: int | None = Field(
        default=None,
        description=(
            "Phase 4.5 Slice 3 (Z-X3): Critic 8-dim 기준 best-plan index "
            "(`plan_candidates` 순서 0~2). 모든 verdict 가 invalid 또는 "
            "critic skip 시 None. Tie 발생 시 더 작은 index 선택 (deterministic). "
            "Frontend wrapper(`/plan/[plan_id]/page.tsx`) highlight 에 사용 — "
            "PlanCard.tsx 무수정 정책 유지 (사용자 결정 6-a 계승)."
        ),
    )


# ─── Phase 4 Slice 2: validation.warnings 동적 계산 helper ────────────

def compute_validation_warnings_phase4(
    plans_count: int,
    *,
    rag_used_fallback: bool,
    critic_present: bool,
    has_revise_loop: bool = False,
) -> list[str]:
    """Phase 4 Slice 2: validation.warnings 동적 계산.

    Rules:
      - plans_count < 3 → phase_1_single_plan (Phase 1 endpoint 또는 부분 실패 시 유지)
      - plans_count == 3 → phase_1_single_plan 제거
      - rag_used_fallback == True → phase_1_no_rag (Slice 4에서 일반적으로 해소되었지만 Phase 4 reuse)
      - critic_present == False → phase_1_no_critic
      - has_revise_loop == False AND plans_count == 3 → phase_4_no_revise_loop 추가
        (Phase 4는 revise loop deferred — Phase 4.5+ 이관)

    Args:
        plans_count: 생성된 plan 개수 (1~3).
        rag_used_fallback: RAG fallback 사용 여부.
        critic_present: Critic 평가 결과 포함 여부.
        has_revise_loop: revise loop 동작 여부 (Phase 4는 항상 False).

    Returns:
        warning 키 list (output_schema.md §8.2 정합).
    """
    warnings: list[str] = []
    if plans_count < 3:
        warnings.append("phase_1_single_plan")
    if rag_used_fallback:
        warnings.append("phase_1_no_rag")
    if not critic_present:
        warnings.append("phase_1_no_critic")
    if not has_revise_loop and plans_count == 3:
        # Phase 4: revise loop 미동작 (Phase 4.5+ deferred).
        warnings.append("phase_4_no_revise_loop")
    return warnings


# ─── Validation ───────────────────────────────────────────────────────

class ValidationCheck(BaseModel):
    name: str
    status: Literal["ok", "warn", "fail"] = "ok"
    detail: str | None = None


class Validation(BaseModel):
    passed: bool
    checks: list[ValidationCheck]
    warnings: list[str] = Field(default_factory=list)

    @field_validator("passed")
    @classmethod
    def passed_must_match_checks(cls, v: bool, info: Any) -> bool:
        # passed=True인 경우 모든 check가 ok여야 함
        # (Pydantic v2에서는 model_validator 권장이나 Slice 1은 단순 check만)
        return v


# ─── Envelope ─────────────────────────────────────────────────────────

class Envelope(BaseModel):
    """전체 응답 envelope (output_schema.md §2)."""

    meta: Meta
    body: Body
    validation: Validation


# ─── Error Envelope (Slice 2 활성화) ──────────────────────────────────

class ErrorBody(BaseModel):
    """error_response_contract.md §3.2 핵심 필드 (Phase 1 Slice 2 최소셋).

    Phase 1은 code / message / user_message / retry_allowed 4 필드만 사용.
    contract 풀 필드(category, user_action, request_id, occurred_at, partial_result 등)는
    Slice 5+ 에서 점진 확장 예정.
    """

    code: str = Field(..., description="E-{CATEGORY}-{NNN} 형식 (예: INV-001)")
    message: str = Field(..., description="기술 메시지 (로그/디버그용)")
    user_message: str = Field(..., description="한국어 friendly 사용자 메시지")
    retry_allowed: bool = Field(
        default=False,
        description="동일 입력으로 재시도해도 의미가 있는지 여부",
    )


class ErrorMeta(BaseModel):
    """ErrorEnvelope.meta — 추적용 최소 메타."""

    request_id: str = Field(..., description="uuid v4")
    generated_at: str = Field(..., description="ISO8601 UTC")

    @classmethod
    def make(cls) -> "ErrorMeta":
        return cls(
            request_id=str(uuid4()),
            generated_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )


class ErrorEnvelope(BaseModel):
    """오류 응답 envelope (error_response_contract.md §1 정합).

    Phase 1 Slice 2: INV-001 (Intent 차단) 부터 사용 시작.
    """

    ok: bool = False
    error: ErrorBody
    meta: ErrorMeta


# ─── Phase 13 Slice S3 — gated 직렬화 헬퍼 (additive) ─────────────────

def envelope_to_response_dict(
    envelope: "Envelope", plans: list["Plan"], *, rich_enabled: bool
) -> dict:
    """Envelope → 응답 dict. rich_enabled=False 면 plan_candidates 를 model_dump_compact()
    로 직렬화해 rich 슬롯 제외(Phase 13 이전과 byte-identical, A5-PP). True 면 full(rich 포함).
    plans 는 envelope.body.plan_candidates 와 동일 순서의 Plan 객체 리스트."""
    d = envelope.model_dump(mode="json")
    if not rich_enabled:
        d["body"]["plan_candidates"] = [p.model_dump_compact(mode="json") for p in plans]
    return d
