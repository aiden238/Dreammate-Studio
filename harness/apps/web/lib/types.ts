/**
 * Phase 1 Slice 6 — backend FastAPI 응답 envelope 매칭 타입
 *
 * 참조: harness/backend/fastapi/schemas/output.py
 *       output_schema.md §2 (meta / body / validation 3섹션 envelope)
 *
 * Phase 1 단순화:
 *   - body.plans 길이 1개 (vs contract 3개)
 *   - rag_used 빈 배열
 *   - approach_label 단일 값
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
  // Phase 1 Slice 6 시점에서는 rag_used 가 빈 배열이지만,
  // 구조는 후속 Slice (4 RAG fallback)에서 채워지도록 열어둔다.
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

export interface Body {
  plans: Plan[]; // 1..3 (Phase 1: 1개)
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
 * Slice 2 이후 error_response_contract.md 정합 envelope.
 * Slice 1 시점에는 활성되지 않을 수 있어 옵셔널 fallback 처리 필요.
 */
export interface ErrorEnvelope {
  ok: false;
  error: {
    code: string; // e.g. "INV-001"
    message: string; // 개발자용
    user_message?: string; // 사용자 표시용
    retry_allowed?: boolean;
    user_action?: string;
    request_id?: string;
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
