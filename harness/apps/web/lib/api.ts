/**
 * Phase 1 Slice 6 — FastAPI 백엔드 호출 wrapper
 *
 * 참조: harness/backend/fastapi/routers/generate.py (POST /api/v1/generate)
 *       harness/backend/fastapi/schemas/output.py (Envelope)
 *       docs/contracts/error_response_contract.md (ErrorEnvelope)
 *
 * Slice 6 동안 백엔드는 Slice 1→2 전환 중이라 두 응답 형식을 모두 처리한다:
 *   - Slice 1: FastAPI 기본 HTTPException {"detail": "..."} (HTTP 422)
 *   - Slice 2: ErrorEnvelope {ok:false, error:{code,...}}     (HTTP 422)
 */

import type {
  ApiErrorResponse,
  Envelope,
  ErrorEnvelope,
  FastAPIDetailError,
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
      error: ApiErrorResponse;
      userMessage: string;
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
    return {
      ok: false,
      status: response.status,
      error: parsed,
      userMessage:
        (parsed.error.user_message as string | undefined) ??
        (parsed.error.message as string | undefined) ??
        "요청을 처리하지 못했어요.",
      retryAllowed: Boolean(parsed.error.retry_allowed),
    };
  }

  if (isFastAPIDetailError(parsed)) {
    const detailMessage = extractFastAPIDetailMessage(parsed);
    return {
      ok: false,
      status: response.status,
      error: parsed,
      userMessage: detailMessage,
      // FastAPI HTTPException은 보통 입력 검증 실패 → 재시도 의미 없음.
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
    retryAllowed: true,
  };
}

function extractFastAPIDetailMessage(err: FastAPIDetailError): string {
  if (typeof err.detail === "string") return err.detail;
  if (Array.isArray(err.detail) && err.detail.length > 0) {
    const first = err.detail[0];
    if (first && typeof first.msg === "string") return first.msg;
  }
  return "요청을 처리하지 못했어요.";
}
