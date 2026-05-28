/**
 * Phase 5 Slice 4 — SSE Progress listener wrapper (D7).
 *
 * 확정 결정 [10] (30-60초 plan 생성 progress + 부분 결과) 정합.
 * security-review §T4 (SSE hijacking) 권장 적용.
 *
 * 설계:
 *   - EventSource (브라우저 표준) 사용.
 *   - 인증은 cookie 기반 (withCredentials=true). Slice 3 baseline 의
 *     httpOnly cookie 가 EventSource 에도 자동 동반된다.
 *   - "complete" 이벤트 수신 시 자동 close.
 *   - onerror 시 caller 에 통지 (EventSource 자체는 자동 재연결).
 *
 * 참조:
 *   - harness/backend/fastapi/routers/sse.py (/api/v1/plans/{id}/progress)
 *   - harness/docs/decisions/phase_5_sse_progress.md (ADR-022)
 *   - harness/meta/security_reviews/2026-05-29_phase-5-auth-rls.md §T4
 */

import { API_BASE_URL } from "./api";

/**
 * 서버 send 이벤트 schema. routers/sse.py `_progress_generator` 정합.
 */
export interface ProgressEvent {
  type: "progress" | "complete" | "error";
  step: number;
  name?: string;
  message: string;
  plan_id: string;
  duration_estimate_sec?: number;
  payload?: unknown;
}

export type ProgressListener = (event: ProgressEvent) => void;

export interface SSESubscription {
  close: () => void;
}

/**
 * /api/v1/plans/{plan_id}/progress 구독.
 *
 * @param planId   plan UUID
 * @param onEvent  ProgressEvent 수신 콜백
 * @param onError  EventSource 에러 콜백 (옵션). EventSource 는 자체 재연결.
 * @returns        구독 핸들 (`close()` 로 명시적 종료)
 */
export function subscribeToPlanProgress(
  planId: string,
  onEvent: ProgressListener,
  onError?: (err: Event) => void,
): SSESubscription {
  const url = `${API_BASE_URL}/api/v1/plans/${encodeURIComponent(planId)}/progress`;
  // withCredentials=true → cookie (Slice 3 httpOnly sb_access_token) 자동 동반.
  const eventSource = new EventSource(url, { withCredentials: true });

  eventSource.onmessage = (msg: MessageEvent) => {
    try {
      const data = JSON.parse(msg.data) as ProgressEvent;
      onEvent(data);
      if (data.type === "complete") {
        eventSource.close();
      }
    } catch (err) {
      // graceful: 파싱 실패는 caller 차단 X (로그만).
      // eslint-disable-next-line no-console
      console.error("sse_parse_failed", err);
    }
  };

  eventSource.onerror = (err: Event) => {
    if (onError) onError(err);
    // EventSource 자체는 표준 자동 재연결 (브라우저 동작).
  };

  return {
    close: () => {
      eventSource.close();
    },
  };
}
