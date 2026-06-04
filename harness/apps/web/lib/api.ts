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
  BrandingFinalizeResponse,
  BrandingNextRequest,
  BrandingNextResponse,
  BrandingSelectRequest,
  BrandingSelectResponse,
  Envelope,
  ErrorEnvelope,
  FastAPIDetailError,
  FeedbackRequest,
  FeedbackResponse,
  MeDomainCreateResponse,
  MeSeriesCreateResponse,
  MultiPlanEnvelope,
  PkmGraphNode,
  PkmGraphResponse,
  PlanResource,
  PlanStartResponse,
  SelectPlanRequest,
  SelectPlanResponse,
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
      // Phase 17 가: auth httpOnly cookie 전송 → auth_user_id 흐름(PKM 주입 조건).
      //   cross-origin(:3000→:8000)이라 명시 필요. CORS allow_credentials=True.
      credentials: "include",
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
      // Phase 17 가: auth httpOnly cookie 전송 → auth_user_id 흐름(PKM 주입 조건).
      //   cross-origin(:3000→:8000)이라 명시 필요. CORS allow_credentials=True.
      credentials: "include",
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

// ═══════════════════════════════════════════════════════════════════════
// Phase 9 Slice 5 — Select / Feedback endpoint wrappers (ADR-030)
// ═══════════════════════════════════════════════════════════════════════
//
// 참조: harness/backend/fastapi/routers/plans.py
//         POST /api/v1/plans/{id}/select   (SelectPlanRequest → SelectPlanResponse)
//         POST /api/v1/plans/{id}/feedback (FeedbackRequest   → FeedbackResponse)
//       harness/backend/fastapi/schemas/plans.py (Pydantic 정합)
//
// 정책:
//   - Phase 5 auth 패턴: credentials: "include" (httpOnly cookie 전송).
//   - 단순 throw on !ok (page.tsx inline UI 가 try/catch 로 처리).
//   - 선택/반려 UI 는 page.tsx inline wrapper — PlanCard.tsx / component_map.md 무수정 ★.

/**
 * POST /api/v1/plans/{plan_id}/select
 * 3-plan 중 하나를 선택 저장 (selected_option_index 0–2).
 */
export async function selectPlan(
  planId: string,
  body: SelectPlanRequest,
): Promise<SelectPlanResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(planId)}/select`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`select_failed: ${resp.status}`);
  }
  return resp.json() as Promise<SelectPlanResponse>;
}

/**
 * POST /api/v1/plans/{plan_id}/feedback
 * like / dislike / reject / regenerate 피드백 저장.
 * reason 자유 입력은 backend FeedbackRepo 가 저장 전 PII 마스킹.
 */
export async function sendFeedback(
  planId: string,
  body: FeedbackRequest,
): Promise<FeedbackResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(planId)}/feedback`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`feedback_failed: ${resp.status}`);
  }
  return resp.json() as Promise<FeedbackResponse>;
}

// ═══════════════════════════════════════════════════════════════════════
// Phase 18 Slice S2/S3 — Branding (topic discovery) endpoint wrappers
// ═══════════════════════════════════════════════════════════════════════
//
// 참조: harness/backend/fastapi/routers/plans.py
//         POST /api/v1/plans/{id}/branding/next     (BrandingNextRequest → BrandingNextResponse)
//         POST /api/v1/plans/{id}/branding/finalize  (no body → BrandingFinalizeResponse)
//       harness/backend/fastapi/schemas/plans.py (Pydantic 정합)
//
// 정책:
//   - auth-optional (익명 OK, wizard 와 동일) — 그래도 select/feedback 패턴처럼 credentials:"include"
//     로 호출(향후 PKM 시드 S4 대비 + 동일 컨벤션). CORS allow_credentials=True.
//   - 단순 throw on !ok (page.tsx inline UI 가 try/catch 로 처리). backend 는 agent 실패 시
//     graceful(mode=done / 빈 candidates) 로 200 을 돌려주므로 throw 는 주로 404/네트워크.

/**
 * POST /api/v1/plans/{plan_id}/branding/next
 * 직전 답변(카드 선택 or 자유입력)을 받아 다음 질문(mode="ask") 또는 종료(mode="done")를 반환.
 * 첫 호출은 빈 body({}) — 첫 질문 생성.
 */
export async function brandingNext(
  planId: string,
  body: BrandingNextRequest = {},
): Promise<BrandingNextResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(
    planId,
  )}/branding/next`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`branding_next_failed: ${resp.status}`);
  }
  return resp.json() as Promise<BrandingNextResponse>;
}

/**
 * POST /api/v1/plans/{plan_id}/branding/finalize
 * 누적 Q&A 를 종합해 후보 영상 주제(보통 3개)를 합성·반환.
 */
export async function brandingFinalize(
  planId: string,
): Promise<BrandingFinalizeResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(
    planId,
  )}/branding/finalize`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
  });
  if (!resp.ok) {
    throw new Error(`branding_finalize_failed: ${resp.status}`);
  }
  return resp.json() as Promise<BrandingFinalizeResponse>;
}

/**
 * POST /api/v1/plans/{plan_id}/branding/select
 * 발굴한 후보 주제 1개를 택1 → backend 가 plan_entry.initial_input 을 그 주제로 설정(planning 연결)하고,
 * gated+authed 일 때 그 브랜딩 방향(tone/target/format)을 사용자 brand_memory 로 시드한다 (P18 축적 단계).
 * ★ best-effort: 시드는 backend 가 graceful 처리(flag OFF/익명 → seeded:0). credentials:"include"
 *   (auth httpOnly cookie 전송 → seed 조건). 호출 실패해도 호출측은 generate 로 진행(seed 는 부가 단계).
 */
export async function brandingSelect(
  planId: string,
  body: BrandingSelectRequest,
): Promise<BrandingSelectResponse> {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(
    planId,
  )}/branding/select`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`branding_select_failed: ${resp.status}`);
  }
  return resp.json() as Promise<BrandingSelectResponse>;
}

// ═══════════════════════════════════════════════════════════════════════
// Phase 19 Slice S2 — 2nd-brain PKM graph endpoint wrapper
// ═══════════════════════════════════════════════════════════════════════
//
// 참조: harness/backend/fastapi/routers/me.py
//         GET /api/v1/me/pkm-graph (authed → {nodes, edges, summary})
//       harness/backend/fastapi/schemas/graph.py (PkmGraphResponse 정합)
//
// 정책:
//   - auth-required (RLS — 자기 데이터만). credentials:"include" 로 httpOnly cookie 전송
//     (cross-origin :3000→:8000, CORS allow_credentials=True).
//   - GET 이라 멱등 — 익명/무데이터는 backend 가 빈 graph(200) 로 graceful 반환.
//   - 단순 throw on !ok (page.tsx 가 try/catch 로 친근한 에러 표시).

/**
 * GET /api/v1/me/pkm-graph
 * 사용자의 개인 PKM + 브랜드 PKM + 4계층(user/brand)을 {nodes, edges, summary}로 집계 반환.
 * S2 카드/리스트(모바일) · S3 그래프(데스크톱)가 동일 구조를 소비한다.
 */
export async function getPkmGraph(): Promise<PkmGraphResponse> {
  const url = `${API_BASE_URL}/api/v1/me/pkm-graph`;
  const resp = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
    // RLS auth httpOnly cookie 전송 (자기 데이터만). cross-origin 명시 필요.
    credentials: "include",
  });
  if (!resp.ok) {
    throw new Error(`pkm_graph_failed: ${resp.status}`);
  }
  return resp.json() as Promise<PkmGraphResponse>;
}

// ═══════════════════════════════════════════════════════════════════════
// Phase 19 Slice S4 — PKM 큐레이션 (잠금/편집/삭제) endpoint wrappers
// ═══════════════════════════════════════════════════════════════════════
//
// 참조: harness/backend/fastapi/routers/me.py
//         PATCH  /api/v1/me/pkm/{node_id}  (MePkmPatchRequest → MePkmMutationResponse)
//         DELETE /api/v1/me/pkm/{node_id}  (no body → MePkmMutationResponse)
//       harness/backend/fastapi/schemas/graph.py (정합)
//
// 정책:
//   - auth-required (RLS — 자기 데이터만). credentials:"include" (httpOnly cookie 전송).
//   - node_id 는 그래프 노드 id 그대로('pkm:<id>' / 'bm:<id>'). path 에 그대로 인코딩.
//   - 단순 throw on !ok (page.tsx 가 try/catch + 그래프 refetch 로 처리).

/** PATCH /api/v1/me/pkm/{node_id} 요청 본문 (둘 다 선택). */
export interface UpdatePkmNodeBody {
  content?: string;
  locked?: boolean;
}

/** PATCH/DELETE 큐레이션 응답 — ok + (PATCH 시) 갱신 node. */
export interface PkmMutationResult {
  ok: boolean;
  node?: PkmGraphNode;
}

/**
 * PATCH /api/v1/me/pkm/{node_id}
 * PKM 노드의 content 편집 또는 locked(🔒) 토글. 'pkm:<id>'(개인) / 'bm:<id>'(브랜드) 모두 지원.
 * 미소유/미존재 → 404 throw. 익명 → 401 throw.
 */
export async function updatePkmNode(
  nodeId: string,
  body: UpdatePkmNodeBody,
): Promise<PkmMutationResult> {
  const url = `${API_BASE_URL}/api/v1/me/pkm/${encodeURIComponent(nodeId)}`;
  const resp = await fetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    throw new Error(`pkm_update_failed: ${resp.status}`);
  }
  return resp.json() as Promise<PkmMutationResult>;
}

/**
 * DELETE /api/v1/me/pkm/{node_id}
 * PKM 노드 삭제. 'pkm:<id>'(개인) / 'bm:<id>'(브랜드) 모두 지원.
 * 미소유/미존재 → 404 throw. 익명 → 401 throw.
 */
export async function deletePkmNode(nodeId: string): Promise<PkmMutationResult> {
  const url = `${API_BASE_URL}/api/v1/me/pkm/${encodeURIComponent(nodeId)}`;
  const resp = await fetch(url, {
    method: "DELETE",
    headers: { Accept: "application/json" },
    credentials: "include",
  });
  if (!resp.ok) {
    throw new Error(`pkm_delete_failed: ${resp.status}`);
  }
  return resp.json() as Promise<PkmMutationResult>;
}

// ═══════════════════════════════════════════════════════════════════════
// Phase 22 Slice S1/S2 — 구조 생성 (Domain/Series CREATE) endpoint wrappers
// ═══════════════════════════════════════════════════════════════════════
//
// 참조: harness/backend/fastapi/routers/me.py
//         POST /api/v1/me/domains {brand_id, name}  → {ok, domain} (authed, RLS)
//         POST /api/v1/me/series  {domain_id, name} → {ok, series} (authed, RLS)
//       harness/backend/fastapi/schemas/graph.py (Me{Domain,Series}Create* 정합)
//
// 정책:
//   - auth-required (RLS — 자기 brand/domain 아래만). credentials:"include" (httpOnly cookie 전송,
//     cross-origin :3000→:8000, CORS allow_credentials=True). 미소유/미존재 → 404, 익명 → 401,
//     빈 name → 422, 저장 실패 → 503. 단순 throw on !ok (page.tsx 가 try/catch + 그래프 refetch).
//   - 생성 즉시 /me/pkm-graph 가 domain/series 노드+엣지(has_domain/has_series)로 노출 → refetch 로 반영.

/**
 * POST /api/v1/me/domains
 * 소유 brand(brandId) 아래 domain 1개 생성. 미소유 brand → 404, 빈 name → 422 throw.
 */
export async function createDomain(
  brandId: string,
  name: string,
): Promise<MeDomainCreateResponse> {
  const url = `${API_BASE_URL}/api/v1/me/domains`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ brand_id: brandId, name }),
  });
  if (!resp.ok) {
    throw new Error(`domain_create_failed: ${resp.status}`);
  }
  return resp.json() as Promise<MeDomainCreateResponse>;
}

/**
 * POST /api/v1/me/series
 * 소유 domain(domainId) 아래 series 1개 생성. 미소유 domain → 404, 빈 name → 422 throw.
 */
export async function createSeries(
  domainId: string,
  name: string,
): Promise<MeSeriesCreateResponse> {
  const url = `${API_BASE_URL}/api/v1/me/series`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ domain_id: domainId, name }),
  });
  if (!resp.ok) {
    throw new Error(`series_create_failed: ${resp.status}`);
  }
  return resp.json() as Promise<MeSeriesCreateResponse>;
}
