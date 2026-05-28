/**
 * Phase 1 Slice 7 — FastAPI 백엔드 호출 wrapper
 *
 * 참조: harness/backend/fastapi/routers/generate.py (POST /api/v1/generate)
 *       harness/backend/fastapi/schemas/output.py (Envelope)
 *       docs/contracts/error_response_contract.md (ErrorEnvelope)
 *
 * 처리 형식 (3종):
 *   1. 200 OK + Envelope        → ok:true
 *   2. 4xx/5xx + ErrorEnvelope  → ok:false, ErrorEnvelope 반환 (코드 보존)
 *   3. 4xx + FastAPI default {"detail":"..."}
 *       → INV-001 추정 (Slice 1→2 전환 잔재) 또는 일반 검증 실패로 합성
 *   4. 네트워크 실패            → NET-000 합성
 *
 * Slice 7 추가:
 *   - 항상 ErrorEnvelope 정규 형식으로 반환 (FastAPI detail 도 합성)
 *   - errorCode 노출 (ErrorCard 가 매핑할 수 있도록)
 */

import type {
  Envelope,
  ErrorEnvelope,
  FastAPIDetailError,
  MultiPlanEnvelope,
  PlanResource,
  PlanStartResponse,
  WizardStepResponse,
} from "./types";
import { isEnvelope, isErrorEnvelope, isFastAPIDetailError } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface GenerateRequest {
  input: string;
  locale?: string;
}

export type GenerateResult =
  | { ok: true; status: number; envelope: Envelope }
  | {
      ok: false;
      status: number;
      /** 정규화된 ErrorEnvelope (FastAPI detail / 네트워크 실패도 모두 이 형식). */
      error: ErrorEnvelope;
      /** ErrorCard 가 표시할 사용자 메시지 (user_message 우선, 합성 fallback). */
      userMessage: string;
      /** 코드 단축 alias. ErrorCard / errors.ts 가 분기에 사용. */
      errorCode: string;
      retryAllowed: boolean;
    };

/**
 * POST /api/v1/generate
 *
 * 성공: 200 + Envelope
 * 실패: 4xx/5xx + ErrorEnvelope 또는 FastAPI default {"detail":...}
 * 네트워크 오류: 캐치해서 status=0 + 임시 ErrorEnvelope 합성
 */
export async function generate(
  body: GenerateRequest,
): Promise<GenerateResult> {
  const url = `${API_BASE_URL}/api/v1/generate`;
  const payload: GenerateRequest = {
    input: body.input,
    locale: body.locale ?? "ko-KR",
  };

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (networkErr) {
    const message =
      networkErr instanceof Error ? networkErr.message : String(networkErr);
    const fakeError: ErrorEnvelope = {
      ok: false,
      error: {
        code: "NET-000",
        message,
        user_message:
          "서버에 연결하지 못했어요. 잠시 후 다시 시도해주세요.",
        retry_allowed: true,
      },
    };
    return {
      ok: false,
      status: 0,
      error: fakeError,
      userMessage: fakeError.error.user_message!,
      errorCode: fakeError.error.code,
      retryAllowed: true,
    };
  }

  let parsed: unknown = null;
  try {
    parsed = await response.json();
  } catch {
    // 응답이 JSON이 아닐 경우
    parsed = null;
  }

  if (response.ok && isEnvelope(parsed)) {
    return { ok: true, status: response.status, envelope: parsed };
  }

  // ── 에러 처리 ─────────────────────────────────────────────────────
  if (isErrorEnvelope(parsed)) {
    const code = String(parsed.error.code ?? "UNK-000");
    return {
      ok: false,
      status: response.status,
      error: parsed,
      userMessage:
        (parsed.error.user_message as string | undefined) ??
        (parsed.error.message as string | undefined) ??
        "요청을 처리하지 못했어요.",
      errorCode: code,
      retryAllowed:
        parsed.error.retry_allowed === undefined
          ? inferRetryAllowedFromCode(code)
          : Boolean(parsed.error.retry_allowed),
    };
  }

  if (isFastAPIDetailError(parsed)) {
    const detailMessage = extractFastAPIDetailMessage(parsed);
    // Slice 1 잔재 또는 입력 형식 위반 → INV-* 합성
    const synthCode = response.status === 422 ? "INV-001" : "E-INV-008";
    const synth: ErrorEnvelope = {
      ok: false,
      error: {
        code: synthCode,
        message: `FastAPI default (status=${response.status})`,
        user_message: detailMessage,
        retry_allowed: false,
      },
    };
    return {
      ok: false,
      status: response.status,
      error: synth,
      userMessage: detailMessage,
      errorCode: synthCode,
      retryAllowed: false,
    };
  }

  // 알 수 없는 응답 형식
  const fallback: ErrorEnvelope = {
    ok: false,
    error: {
      code: "UNK-000",
      message: `Unexpected response (status=${response.status})`,
      user_message: "알 수 없는 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
      retry_allowed: true,
    },
  };
  return {
    ok: false,
    status: response.status,
    error: fallback,
    userMessage: fallback.error.user_message!,
    errorCode: fallback.error.code,
    retryAllowed: true,
  };
}

/**
 * retry_allowed 가 응답에서 누락된 경우 코드로 추론.
 * INV / SEC 는 사용자 액션 필요 → false, 그 외는 true.
 */
function inferRetryAllowedFromCode(code: string): boolean {
  if (code.startsWith("INV-") || code.startsWith("E-INV-")) return false;
  if (code.startsWith("E-SEC-")) return false;
  return true;
}

function extractFastAPIDetailMessage(err: FastAPIDetailError): string {
  if (typeof err.detail === "string") return err.detail;
  if (Array.isArray(err.detail) && err.detail.length > 0) {
    const first = err.detail[0];
    if (first && typeof first.msg === "string") return first.msg;
  }
  return "요청을 처리하지 못했어요.";
}

// ═══════════════════════════════════════════════════════════════════════
// Phase 4 Slice 3 — Multi-plan endpoint wrappers
// ═══════════════════════════════════════════════════════════════════════
//
// 참조: harness/backend/fastapi/routers/plans.py (4 endpoints)
//       harness/backend/fastapi/schemas/plans.py (request/response 정합)
//       harness/docs/contracts/api_contract.md §8
//
// 정책:
//   - 4 endpoints: start / wizard / generate / get
//   - generateMultiPlan 만 success/error union (ErrorEnvelope) 반환
//     (Phase 1 generate()와 동일한 패턴)
//   - 나머지 3개는 단순 throw on error (Slice 3 frontend는 generate에만 의존)

/**
 * generateMultiPlan 의 정규화 결과. Phase 1 `generate()` 와 동일한 형태.
 */
export type GenerateMultiPlanResult =
  | { ok: true; status: number; envelope: MultiPlanEnvelope }
  | {
      ok: false;
      status: number;
      error: ErrorEnvelope;
      userMessage: string;
      errorCode: string;
      retryAllowed: boolean;
    };

/**
 * POST /api/v1/plans/start
 * 새 plan_id 발급. Phase 4 Slice 3 frontend는 직접 호출하지 않을 수도 있으나
 * Slice 4 smoke / 향후 wizard 진입점에서 사용.
 */
export async function startPlan(
  initialInput?: string,
  locale: string = "ko-KR",
): Promise<PlanStartResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/start`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ user_input: initialInput, locale }),
  });
  if (!response.ok) {
    throw new Error(`startPlan failed: HTTP ${response.status}`);
  }
  return response.json() as Promise<PlanStartResponse>;
}

/**
 * POST /api/v1/plans/{plan_id}/wizard/{step}
 * Phase 4 Slice 3는 직접 호출하지 않으나, Slice 4 smoke / Phase 5+ wizard 본격에서 사용.
 */
export async function wizardStep(
  planId: string,
  step: string,
  data: {
    selected_card_id?: string;
    user_input?: string;
    extra?: Record<string, unknown>;
  } = {},
): Promise<WizardStepResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(
    planId,
  )}/wizard/${encodeURIComponent(step)}`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`wizardStep failed: HTTP ${response.status}`);
  }
  return response.json() as Promise<WizardStepResponse>;
}

/**
 * POST /api/v1/plans/{plan_id}/generate
 * 3-plan 생성 (Intent → RAG → 3-plan parallel → Critic → DB save → Envelope).
 * Phase 1 `generate()` 와 동일한 정규화 패턴 (success / error union).
 */
export async function generateMultiPlan(
  planId: string,
  body: { use_rag?: boolean; use_critic?: boolean } = {},
): Promise<GenerateMultiPlanResult> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(
    planId,
  )}/generate`;
  const payload = {
    use_rag: body.use_rag ?? true,
    use_critic: body.use_critic ?? true,
  };

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (networkErr) {
    const message =
      networkErr instanceof Error ? networkErr.message : String(networkErr);
    const fakeError: ErrorEnvelope = {
      ok: false,
      error: {
        code: "NET-000",
        message,
        user_message: "서버에 연결하지 못했어요. 잠시 후 다시 시도해주세요.",
        retry_allowed: true,
      },
    };
    return {
      ok: false,
      status: 0,
      error: fakeError,
      userMessage: fakeError.error.user_message!,
      errorCode: fakeError.error.code,
      retryAllowed: true,
    };
  }

  let parsed: unknown = null;
  try {
    parsed = await response.json();
  } catch {
    parsed = null;
  }

  if (response.ok && isEnvelope(parsed)) {
    return {
      ok: true,
      status: response.status,
      envelope: parsed as MultiPlanEnvelope,
    };
  }

  if (isErrorEnvelope(parsed)) {
    const code = String(parsed.error.code ?? "UNK-000");
    return {
      ok: false,
      status: response.status,
      error: parsed,
      userMessage:
        (parsed.error.user_message as string | undefined) ??
        (parsed.error.message as string | undefined) ??
        "요청을 처리하지 못했어요.",
      errorCode: code,
      retryAllowed:
        parsed.error.retry_allowed === undefined
          ? inferRetryAllowedFromCode(code)
          : Boolean(parsed.error.retry_allowed),
    };
  }

  if (isFastAPIDetailError(parsed)) {
    const detailMessage = extractFastAPIDetailMessage(parsed);
    const synthCode = response.status === 422 ? "INV-001" : "E-INV-008";
    const synth: ErrorEnvelope = {
      ok: false,
      error: {
        code: synthCode,
        message: `FastAPI default (status=${response.status})`,
        user_message: detailMessage,
        retry_allowed: false,
      },
    };
    return {
      ok: false,
      status: response.status,
      error: synth,
      userMessage: detailMessage,
      errorCode: synthCode,
      retryAllowed: false,
    };
  }

  const fallback: ErrorEnvelope = {
    ok: false,
    error: {
      code: "UNK-000",
      message: `Unexpected response (status=${response.status})`,
      user_message:
        "알 수 없는 오류가 발생했어요. 잠시 후 다시 시도해주세요.",
      retry_allowed: true,
    },
  };
  return {
    ok: false,
    status: response.status,
    error: fallback,
    userMessage: fallback.error.user_message!,
    errorCode: fallback.error.code,
    retryAllowed: true,
  };
}

/**
 * GET /api/v1/plans/{plan_id}
 * 저장된 plan resource 조회. envelope 가 null 이면 미생성 상태.
 */
export async function getPlan(planId: string): Promise<PlanResource> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(planId)}`;
  const response = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`getPlan failed: HTTP ${response.status}`);
  }
  return response.json() as Promise<PlanResource>;
}
