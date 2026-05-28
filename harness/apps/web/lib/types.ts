/**
 * Phase 1 Slice 7 — backend FastAPI 응답 envelope 매칭 타입
 *
 * 참조: harness/backend/fastapi/schemas/output.py
 *       output_schema.md §2 (meta / body / validation 3섹션 envelope)
 *       output_schema.md §8.1 (Plan), §8.2 (CriticEvaluation), §8.3 (RAGReference)
 *
 * Slice 7 확장:
 *   - CriticEvaluation / RAGReference 타입 추가 (Slice 3/4 백엔드 응답 매칭)
 *   - Meta.project_id 옵셔널 (Slice 5 — DB graceful failure 시 null)
 *   - Slice 6 backward compatibility 유지 (critic_evaluation/rag_references 옵셔널)
 */

// ─── Meta ─────────────────────────────────────────────────────────────

export interface Meta {
  request_id: string; // uuid v4
  prompt_id: string; // P-001 ... P-008 / P-AUX-* / P-PHASE1-COMBINED
  prompt_version: string; // semver e.g. "v1.0.0"
  model: string; // LLM 모델명
  generated_at: string; // ISO8601 UTC
  locale: string; // "ko-KR"
  schema_version: string; // "1.0.0"
  /**
   * Slice 5: Supabase 저장 결과. 저장 실패 시 null (graceful).
   */
  project_id?: string | null;
}

// ─── Body (Plans) ─────────────────────────────────────────────────────

export interface PlanFlowBeat {
  beat_index: number;
  beat: string;
  duration_sec: number;
  purpose: string;
}

export type ApproachLabel =
  | "narrative"
  | "informational"
  | "empathy"
  | "experiment"
  | "review"
  | "other";

export interface RagUsedEntry {
  source_id?: string;
  title?: string;
  used_reason?: string;
  [key: string]: unknown;
}

export interface Plan {
  plan_id: string; // uuid
  option_index: number; // 0..2
  name: string; // 1..20자
  concept: string;
  hook: string; // 10..80자
  flow: PlanFlowBeat[]; // 2..8 비트
  pros: string;
  risks: string;
  approach_label: ApproachLabel;
  rag_used: RagUsedEntry[];
}

// ─── Critic Evaluation (Slice 3) ──────────────────────────────────────

/**
 * 8차원 평가 점수. 각 차원 0.0 ~ 5.0.
 *
 * 참조: output_schema.md §8.2 (CriticEvaluation), eval/video_planning_eval.md
 */
export interface CriticScores {
  intent_fit: number;
  target_clarity: number;
  hook_strength: number;
  message_clarity: number;
  structure: number;
  feasibility: number;
  brand_consistency: number;
  differentiation: number;
}

export type CriticVerdict = "approve" | "revise" | "reject";

export interface CriticEvaluation {
  target_plan_id: string;
  scores: CriticScores;
  reasons: Record<string, string>;
  suggestions: Record<string, string>;
  overall_score_avg: number;
  overall_verdict: CriticVerdict;
  blocking_issues: string[];
  revise_round: number;
}

// ─── RAG Reference (Slice 4) ──────────────────────────────────────────

/**
 * Planner 가 실제 참조한 RAG 청크.
 *
 * 참조: output_schema.md §8.3, rag_data_contract.md
 */
export interface RAGReference {
  source_id: string;
  title: string;
  snippet: string;
  used_reason?: string;
  similarity: number;
  metadata?: Record<string, unknown>;
}

// ─── Body ─────────────────────────────────────────────────────────────

export interface Body {
  plan_candidates: Plan[]; // 1..3 (Phase 1: 1개) — CC-001 Option B 적용 (2026-05-26)
  /**
   * Slice 3 이후. Slice 1/2 응답은 미포함 가능 → 옵셔널.
   */
  critic_evaluation?: CriticEvaluation | null;
  /**
   * Slice 4 이후. RAG fallback 또는 미연결 시 빈 배열.
   */
  rag_references?: RAGReference[];
}

// ─── Validation ───────────────────────────────────────────────────────

export interface ValidationCheck {
  name: string;
  status: "ok" | "warn" | "fail";
  detail: string | null;
}

export interface Validation {
  passed: boolean;
  checks: ValidationCheck[];
  warnings: string[];
}

// ─── Envelope ─────────────────────────────────────────────────────────

export interface Envelope {
  meta: Meta;
  body: Body;
  validation: Validation;
}

// ─── Error responses ──────────────────────────────────────────────────

/**
 * error_response_contract.md §3.1 정합 envelope.
 */
export interface ErrorEnvelope {
  ok: false;
  error: {
    code: string; // e.g. "INV-001", "E-LLM-001"
    message: string; // 개발자용
    user_message?: string; // 사용자 표시용
    retry_allowed?: boolean;
    user_action?: string;
    request_id?: string;
    category?: string;
    retry_after?: number;
    [key: string]: unknown;
  };
  meta?: Partial<Meta> & { [key: string]: unknown };
}

/**
 * Slice 1 시점의 FastAPI 기본 형식.
 * `{"detail": "..."}` 또는 `{"detail": [{...}]}` 형태.
 */
export interface FastAPIDetailError {
  detail:
    | string
    | Array<{
        loc?: (string | number)[];
        msg?: string;
        type?: string;
        [key: string]: unknown;
      }>;
}

export type ApiErrorResponse = ErrorEnvelope | FastAPIDetailError;

// ─── Type guards ──────────────────────────────────────────────────────

export function isEnvelope(value: unknown): value is Envelope {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.meta === "object" &&
    typeof v.body === "object" &&
    typeof v.validation === "object"
  );
}

export function isErrorEnvelope(value: unknown): value is ErrorEnvelope {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return v.ok === false && typeof v.error === "object" && v.error !== null;
}

export function isFastAPIDetailError(
  value: unknown,
): value is FastAPIDetailError {
  if (typeof value !== "object" || value === null) return false;
  return "detail" in (value as Record<string, unknown>);
}

// ─── Phase 4 Slice 3 — Multi-plan endpoint 타입 ────────────────────────
//
// 참조: harness/backend/fastapi/schemas/output.py (Envelope/Body 정합)
//       harness/backend/fastapi/schemas/plans.py  (PlanStartResponse / PlanResource 정합)
//
// 본 타입들은 기존 Phase 1 `Envelope`/`Body` 타입과 호환 (alias 수준).
// Phase 4 endpoint(`/api/v1/plans/{id}/generate`)는 `plan_candidates.length === 3`을
// 활성화한다. critic_evaluation / rag_references 는 Phase 4에서 모두 포함.

/**
 * Phase 4 envelope. 구조적으로 Phase 1 Envelope와 동일하지만,
 * - body.plan_candidates 가 length 1~3 활성 (Phase 1은 항상 1)
 * - body.critic_evaluation / rag_references 가 항상 채워짐 (Phase 1은 nullable)
 *
 * critic 호출 실패 시에는 graceful 로 null 가능.
 */
export type MultiPlanEnvelope = Envelope;

/**
 * GET /api/v1/plans/{plan_id} 응답.
 * - status: "created" | "wizard_in_progress" | "generated" | "selected"
 * - envelope: generate 완료 후 채워짐 (length 3 Envelope). 미생성 상태 = null.
 */
export interface PlanResource {
  plan_id: string;
  status: "created" | "wizard_in_progress" | "generated" | "selected" | string;
  created_at: string;
  updated_at: string;
  envelope: MultiPlanEnvelope | null;
}

/**
 * POST /api/v1/plans/start 응답.
 */
export interface PlanStartResponse {
  plan_id: string;
  created_at: string;
  locale: string;
}

/**
 * POST /api/v1/plans/{id}/wizard/{step} 응답.
 */
export interface WizardStepResponse {
  plan_id: string;
  step: string;
  accepted: boolean;
  next_step: string | null;
}
