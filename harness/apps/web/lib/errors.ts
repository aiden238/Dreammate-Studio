/**
 * Phase 1 Slice 7 — 에러 코드 → 사용자 메시지 매핑
 *
 * 참조: docs/contracts/error_response_contract.md §4 (코드 사전), §5 (한국어 메시지),
 *       §6 (user_action 키), §11 (클라이언트 처리 규칙)
 *
 * 단일 책임: backend 에러 응답을 ErrorCard 가 그릴 수 있는 표시 객체로 변환한다.
 *
 * 절대 금지 (error_response_contract.md §11.2):
 *   - error.message (영어 기술 메시지) 를 사용자에게 그대로 노출 금지
 *   - HTTP status 만으로 메시지 결정 금지 — 항상 error.code 우선
 */

import type { ErrorEnvelope } from "./types";

// ─── 표시 객체 ─────────────────────────────────────────────────────────

export interface DisplayError {
  /** ErrorCard 헤더 (큰 빨강 텍스트). */
  title: string;
  /** 한 줄 본문 (친근체). user_message 우선, 없으면 매핑 fallback. */
  body: string;
  /** "다시 시도" 버튼 노출 여부. retry_allowed=false 면 false. */
  canRetry: boolean;
  /** "처음으로" 버튼 노출 여부. 입력으로 돌아가야 하는 INV-* / SEC-* 에서 true. */
  canGoHome: boolean;
  /** 추적용 (작은 회색 글자로 표시). */
  requestId?: string;
  /** 디버그용 raw code (작은 회색 글자, 사용자 노출 OK — 문의 시 활용). */
  code: string;
}

// ─── 매핑 규칙 ─────────────────────────────────────────────────────────

interface CodeRule {
  /** 정확 매칭 또는 prefix 매칭 (`E-LLM-` 등). */
  match: string | RegExp;
  title: string;
  fallbackBody: string;
  canRetry: boolean;
  canGoHome: boolean;
}

/**
 * 코드 prefix 기반 매핑. 위에서 아래 순서로 첫 매칭 채택.
 *
 * INV-001 은 백엔드(Slice 2)가 "영상기획 외 입력 차단" 으로 사용하므로
 * E-SEC-002 와 동일한 UX (입력으로 돌아가기) 로 매핑.
 */
const RULES: CodeRule[] = [
  // ── INV-001: 영상기획과 거리가 있는 입력 ────────────────────────────
  {
    match: "INV-001",
    title: "영상기획과 거리가 있는 요청 같아요",
    fallbackBody:
      "다른 방식으로 영상 아이디어를 적어주세요. (예: 어떤 사람에게 어떤 영상을 보여주고 싶은지)",
    canRetry: false,
    canGoHome: true,
  },
  // ── 그 외 INV-*: 입력 검증 일반 ──────────────────────────────────
  {
    match: /^E?-?INV-/,
    title: "입력을 다시 확인해주세요",
    fallbackBody:
      "필수 정보가 빠졌거나 형식이 맞지 않아요. 입력으로 돌아가서 다시 시도해주세요.",
    canRetry: false,
    canGoHome: true,
  },
  // ── E-LLM-001: timeout ──────────────────────────────────────────────
  {
    match: "E-LLM-001",
    title: "AI 응답이 늦어졌어요",
    fallbackBody:
      "AI 응답이 늦어져서 멈췄어요. 잠시 후 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── E-LLM-002: parse failure ────────────────────────────────────────
  {
    match: "E-LLM-002",
    title: "AI 응답을 정리하는 중 문제가 생겼어요",
    fallbackBody:
      "AI 응답을 정리하는 중 문제가 생겼어요. 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── E-LLM-003: schema validation failure ────────────────────────────
  {
    match: "E-LLM-003",
    title: "AI가 형식에 맞지 않게 답했어요",
    fallbackBody:
      "AI가 형식에 맞지 않게 답했어요. 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── 그 외 E-LLM-*: LLM 일반 ──────────────────────────────────────
  {
    match: /^E-LLM-/,
    title: "AI 호출 중 문제가 생겼어요",
    fallbackBody:
      "AI 서버가 잠시 불안정해요. 1분 후 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── E-RAG-*: RAG 검색 ─────────────────────────────────────────────
  {
    match: /^E-RAG-/,
    title: "참고 자료 검색 중 문제가 생겼어요",
    fallbackBody:
      "참고 자료를 못 가져왔어요. 자료 없이 다시 시도하시거나 잠시 후 재시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── E-DB-*: DB 저장 (Phase 1은 graceful이라 거의 미발생) ───────────
  {
    match: /^E-DB-/,
    title: "잠시 후 다시 시도해주세요",
    fallbackBody:
      "데이터를 저장하는 중 문제가 생겼어요. 잠시 후 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── E-RL-*: rate limit ────────────────────────────────────────────
  {
    match: /^E-RL-/,
    title: "잠시 후 다시 시도해주세요",
    fallbackBody:
      "사용량 한도에 도달했어요. 잠시 후 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── E-SEC-*: 보안 차단 ────────────────────────────────────────────
  {
    match: /^E-SEC-/,
    title: "이 요청은 도와드리기 어려워요",
    fallbackBody:
      "다른 주제나 다른 방식으로 시도해주세요.",
    canRetry: false,
    canGoHome: true,
  },
  // ── NET-*: 네트워크 (lib/api.ts 가 합성) ────────────────────────────
  {
    match: /^NET-/,
    title: "서버에 연결하지 못했어요",
    fallbackBody:
      "네트워크 상태를 확인하시고 다시 시도해주세요.",
    canRetry: true,
    canGoHome: true,
  },
  // ── UNK-* / E-UNK-*: 분류 불가 ─────────────────────────────────────
  {
    match: /^(E-)?UNK-/,
    title: "문제가 생겼어요",
    fallbackBody:
      "잠시 후 다시 시도해주세요. 문제가 계속되면 새로고침해주세요.",
    canRetry: true,
    canGoHome: true,
  },
];

const DEFAULT_RULE: CodeRule = {
  match: "",
  title: "문제가 생겼어요",
  fallbackBody: "잠시 후 다시 시도해주세요.",
  canRetry: true,
  canGoHome: true,
};

function findRule(code: string): CodeRule {
  for (const rule of RULES) {
    if (typeof rule.match === "string") {
      if (rule.match === code) return rule;
    } else if (rule.match.test(code)) {
      return rule;
    }
  }
  return DEFAULT_RULE;
}

// ─── public API ────────────────────────────────────────────────────────

/**
 * ErrorEnvelope → DisplayError 변환.
 *
 * 규칙:
 *   1. error.code 로 RULES 매핑 (prefix 우선)
 *   2. body 는 user_message 우선, 없으면 rule.fallbackBody
 *   3. canRetry 는 retry_allowed 가 명시 false 면 강제 false 로 다운그레이드
 *      (서버가 false 라고 한 건 무조건 신뢰; true 라고 한 건 rule 도 함께 만족해야 함)
 */
export function toDisplayError(envelope: ErrorEnvelope): DisplayError {
  const err = envelope.error;
  const code = String(err.code ?? "UNK-999");
  const rule = findRule(code);

  const userMessage =
    typeof err.user_message === "string" && err.user_message.length > 0
      ? err.user_message
      : null;

  // 서버가 명시적으로 retry_allowed=false 보내면 그쪽이 우선.
  const serverSaysNoRetry = err.retry_allowed === false;
  const canRetry = serverSaysNoRetry ? false : rule.canRetry;

  return {
    title: rule.title,
    body: userMessage ?? rule.fallbackBody,
    canRetry,
    canGoHome: rule.canGoHome,
    requestId:
      typeof err.request_id === "string" ? err.request_id : undefined,
    code,
  };
}

/**
 * code + userMessage 만 받아서 표시 객체를 만드는 경량 변형.
 * (sessionStorage 에서 직접 복원할 때 사용.)
 */
export function toDisplayErrorFromCode(
  code: string,
  userMessage?: string,
  requestId?: string,
  retryAllowed?: boolean,
): DisplayError {
  const rule = findRule(code);
  const serverSaysNoRetry = retryAllowed === false;
  return {
    title: rule.title,
    body: userMessage && userMessage.length > 0 ? userMessage : rule.fallbackBody,
    canRetry: serverSaysNoRetry ? false : rule.canRetry,
    canGoHome: rule.canGoHome,
    requestId,
    code,
  };
}
