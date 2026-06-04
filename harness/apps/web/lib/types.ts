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
 *
 * Phase 6 Slice 3 확장 (ADR-018 / ADR-019 frontend mirror):
 *   - CriticDimensions / CriticVerdictAction / canonical fields (overall_score / dimensions)
 *     추가. ReviseAttempt interface 추가 + Body.revise_history typing 강화
 *     (union: ReviseAttempt[][] | Record<string, unknown>[][]).
 *
 * Phase 9.5 Slice 4 (ADR-034 — deprecated 0–5 Full 제거):
 *   - CriticEvaluation 에서 deprecated 0–5 필드(scores / overall_score_avg) 제거.
 *     canonical(overall_score 0–1 + dimensions) 로 전환. target_plan_id 는 Optional 강등.
 *   - page.tsx (`/plan`, `/plan/[plan_id]`) 가 canonical overall_score 를 % 로 렌더 —
 *     PlanCard.tsx / component_map.md 0줄 변경 (page.tsx inline wrapper 만).
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
  /**
   * Phase 13 S1 rich (additive, optional — backend rich_output_enabled ON 경로에서만 채워짐).
   * compact 응답(model_dump_compact)은 이 키들을 제외하므로 undefined → 옵셔널.
   * 참조: backend/fastapi/schemas/output.py PlanFlowBeat / BEAT_RICH_FIELDS.
   */
  visual?: string | null; // 화면/구도/연출 묘사
  dialogue?: string | null; // 내레이션·대사
  caption?: string | null; // 자막 텍스트
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

/**
 * Phase 15 S1 director — scene_breakdown 요소 (기획 브리프 수준, 촬영지시 아님).
 * 참조: backend/fastapi/schemas/output.py DirectorScene.
 */
export interface DirectorScene {
  scene_intent: string; // 씬 기획 의도
  viewer_emotion: string; // 의도하는 시청자 감정
  retention_device: string; // 이탈 방지/호기심 장치
  why_this_works: string; // 작동 근거
  fallback_scene?: string | null; // 대안 씬
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
  /**
   * Phase 13 S1 rich 슬롯 9종 (additive, 전부 optional — backend rich_output_enabled ON
   * 경로에서만 채워짐). compact 응답(model_dump_compact)은 이 키들을 제외하므로 undefined.
   * 참조: backend/fastapi/schemas/output.py Plan / PLAN_RICH_FIELDS.
   */
  hook_variants?: string[]; // 후크 변형 (단일 hook 외 추가, ≤3)
  target_audience?: string | null; // 타깃 시청자
  tone?: string | null; // 톤·무드
  shots?: string[]; // B-roll/샷 리스트
  thumbnail?: string | null; // 썸네일 컨셉
  title_candidates?: string[]; // 제목 후보 (≤5)
  cta?: string | null; // Call-to-action
  references?: string[]; // 창작 레퍼런스 (rag_used 와 구분, ≤5)
  length_variants?: string[]; // 길이 변형 (예: 30s/60s 컷)
  /**
   * Phase 15 S1 director 슬롯 3종 (additive, optional — backend output_mode=director 경로에서만
   * 채워짐). compact/rich 응답은 이 키들을 제외하므로 undefined.
   * 참조: backend/fastapi/schemas/output.py Plan / DIRECTOR_FIELDS.
   */
  hook_system?: string[]; // 첫 후크 + 재후크(re-hook) 설계 (≤5)
  retention_architecture?: string | null; // 리텐션 구조 (이탈방지·호기심갭·페이싱)
  scene_breakdown?: DirectorScene[]; // 씬 단위 분해
}

// ─── Critic Evaluation (Slice 3) ──────────────────────────────────────

/**
 * 8차원 평가 점수. 각 차원 0~5 정수.
 *
 * Phase 9.5 Slice 4 (ADR-034): CriticEvaluation 에서 deprecated 0–5 `scores` 필드 제거.
 * 본 타입은 run_critic LLM-facing 0–5 출력(P-007 prompt contract) 의 mirror 로만 유지 —
 * envelope 응답 body 에는 더 이상 노출되지 않는다 (canonical dimensions 0–1 로 전환).
 *
 * 참조: output_schema.md §9 (CriticEvaluation), eval/video_planning_eval.md
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

/**
 * Phase 6 Slice 3 (ADR-018): Critic verdict action — revise_history attempt 의
 * action 필드. backend `ReviseAttempt.action` 과 정합 (Literal["approve" |
 * "revise" | "reject" | "unknown"]).
 *
 * "unknown" 은 Critic 이 미정의 verdict 를 반환했을 때 server-side 폴백 마커.
 * `CriticVerdict` (approve|revise|reject) 의 superset.
 */
export type CriticVerdictAction = CriticVerdict | "unknown";

/**
 * Phase 6 Slice 3 (ADR-018): Critic dimensions canonical type.
 *
 * backend canonical `dimensions: dict[str, float]` (정규화 0.0~1.0) 의 frontend mirror.
 * 8 차원 키 (intent_fit / target_clarity / ...) 는 일반 string key 로 받아 미래
 * 차원 확장에 대비 (`CriticScores` 의 고정 8 키와 별개).
 *
 * 값 범위: Phase 6 canonical 0.0 ~ 1.0 (float).
 * Phase 9.5 Slice 4 (ADR-034): deprecated 0–5 `scores` 필드는 envelope 에서 제거됨 —
 * `dimensions` 가 유일한 차원 점수 출처 (0–1).
 */
export type CriticDimensions = Record<string, number>;

export interface CriticEvaluation {
  /**
   * Phase 6 canonical (ADR-018): 종합 점수 (정규화 0.0 ~ 1.0).
   *
   * Phase 9.5 Slice 4 (ADR-034): deprecated `overall_score_avg` (0~5) 제거 완료.
   * page.tsx 는 canonical `overall_score` 를 % 로 표시 (PlanCard 무수정).
   *
   * Optional — graceful skip (critic 호출 실패) 시 backend 가 미포함 가능.
   */
  overall_score?: number | null;
  /**
   * Phase 6 canonical (ADR-018): 8 차원 점수 dict (정규화 0.0 ~ 1.0).
   * 미래 차원 추가에 대비해 일반 `Record<string, number>` 로 정의.
   *
   * Optional — graceful skip 시 미포함 가능.
   */
  dimensions?: CriticDimensions;

  // ── Phase 1 호환 메타 (0–5 점수와 무관 — backend 가 그대로 노출) ──
  // Phase 9.5 Slice 4 (ADR-034): deprecated 0–5 필드(scores / overall_score_avg) 는
  // backend·frontend 양쪽에서 제거. canonical(overall_score / dimensions) 로 전환 완료.
  // target_plan_id 는 backend 가 plan_id echo 로 노출하나 page.tsx 미렌더 → Optional.
  target_plan_id?: string;
  reasons: Record<string, string>;
  suggestions: Record<string, string>;
  overall_verdict: CriticVerdict;
  blocking_issues: string[];
  revise_round: number;
}

/**
 * Phase 6 Slice 3 (ADR-018): Rewriter revise loop attempt log entry.
 *
 * backend `ReviseAttempt` (schemas/output.py) 의 frontend mirror — Body.revise_history
 * 의 내부 배열 entry 1 건. routers/plans.py 가 dict 로 직렬화하므로 frontend 는
 * 본 interface 또는 `Record<string, unknown>` 둘 다 허용 (union).
 *
 * Fields:
 *   - attempt: 0,1,2... (0 = 초기 critic, 1+ = revise 후 재평가)
 *   - action: "approve" | "revise" | "reject" | "unknown"
 *   - revised: boolean — 본 attempt 에서 Rewriter 호출 여부
 *   - max_reached?: max_revise 도달 시 true
 *   - critic_warning?: Critic 호출 실패 graceful 마커
 *   - rewriter_warning?: Rewriter 호출 실패 graceful 마커
 */
export interface ReviseAttempt {
  attempt: number;
  action: CriticVerdictAction;
  revised: boolean;
  max_reached?: boolean;
  critic_warning?: string;
  rewriter_warning?: string;
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
  /**
   * Phase 4.5 Slice 2 / Phase 6 Slice 3 (ADR-018) typing 강화:
   * plan별 revise attempt log.
   *  - 외부 배열: plan_candidates 순서 (length === plan_candidates.length)
   *  - 내부 배열: attempt 0,1,2,... 순차 entry
   *
   * Union typing — backend 직렬화는 dict 유지 (회귀 0). canonical
   * `ReviseAttempt` 모델은 typing 검증 + frontend mirror 용도이므로 양쪽 다 허용.
   *
   * loop 비활성 또는 Phase 4 이하 응답 시 미포함 또는 null.
   */
  revise_history?:
    | Array<Array<ReviseAttempt>>
    | Array<Array<Record<string, unknown>>>
    | null;
  /**
   * Phase 4.5 Slice 3 (Z-X3): Critic 8-dim 기준 best-plan index.
   * plan_candidates 순서 0~2. 모든 verdict invalid / critic skip 시 null.
   * Frontend wrapper(`/plan/[plan_id]/page.tsx`) highlight 에 사용 — PlanCard.tsx 무수정 유지.
   */
  recommended_plan_index?: number | null;
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

// ─── Phase 5 Slice 3 — Auth types ──────────────────────────────────────
//
// 참조:
//   - harness/backend/fastapi/routers/auth.py (AuthSession Pydantic)
//   - harness/meta/security_reviews/2026-05-29_phase-5-auth-rls.md §T1
//
// 정책: access_token / refresh_token 은 backend httpOnly cookie 로만 관리.
// 응답 body 에는 절대 노출 안 함 → 본 interface 에 토큰 필드 없음.

/**
 * /auth/login / /auth/me 응답.
 */
export interface AuthSession {
  user_id: string;
  email: string;
}

// ─── Phase 18 Slice S2/S3 — Branding (topic discovery) types ───────────
//
// 참조:
//   - harness/backend/fastapi/schemas/plans.py
//       BrandingNextRequest / BrandingNextResponse / BrandingFinalizeResponse
//   - harness/backend/fastapi/routers/plans.py
//       POST /plans/{id}/branding/next, POST /plans/{id}/branding/finalize
//
// 정책: 주제를 모르는 사용자를 LLM 동적 스무고개(Akinator식)로 좁혀 후보 주제 3개를 발굴한다.
//   auth-optional (익명 OK). PKM 시드는 S4 범위 밖. 본 타입들은 backend Pydantic 과 1:1 정합.

/**
 * POST /plans/{plan_id}/branding/next body.
 * 직전 질문 답변 — 카드 선택(selected_option) 또는 자유입력(answer). 첫 호출은 둘 다 미지정.
 * 둘 다 주어지면 backend 가 selected_option 을 우선 채택.
 */
export interface BrandingNextRequest {
  answer?: string;
  selected_option?: string;
}

/**
 * POST /plans/{plan_id}/branding/next 응답.
 * mode="ask": question + options(2~4개) 노출. mode="done": question/options=null → finalize 진입.
 * step = 누적 질문 수, max_questions = N고개 상한 (진행바 계산용).
 */
export interface BrandingNextResponse {
  mode: "ask" | "done";
  question: string | null;
  options: string[] | null;
  step: number;
  max_questions: number;
}

/**
 * 후보 영상 주제 1건. backend 가 5필드 보장 (topic / tone / target / format / why_fit).
 */
export interface BrandingCandidate {
  topic: string;
  tone: string;
  target: string;
  format: string;
  why_fit: string;
}

/**
 * POST /plans/{plan_id}/branding/finalize 응답 — 후보 주제(보통 3개).
 */
export interface BrandingFinalizeResponse {
  candidates: BrandingCandidate[];
}

/**
 * Phase 18 Slice S4 — POST /plans/{plan_id}/branding/select body.
 * 택1한 브랜딩 후보. topic 은 필수(후속 generate 입력), tone/target/format 은 brand_memory 시드용
 * (backend gated+authed 일 때만 적재). 본 타입은 backend BrandingSelectRequest 와 1:1 정합.
 */
export interface BrandingSelectRequest {
  topic: string;
  tone?: string | null;
  target?: string | null;
  format?: string | null;
}

/**
 * POST /plans/{plan_id}/branding/select 응답.
 * ok = 택1 저장 성공, seeded = brand_memory 로 새로 적재된 entry 수 (gated/익명/dedup → 0).
 */
export interface BrandingSelectResponse {
  ok: boolean;
  seeded: number;
}

// ─── Phase 19 Slice S2 — 2nd-brain PKM graph types ─────────────────────
//
// 참조:
//   - harness/backend/fastapi/schemas/graph.py
//       PkmGraphNode / PkmGraphEdge / PkmGraphSummary / PkmGraphResponse
//   - harness/backend/fastapi/routers/me.py
//       GET /api/v1/me/pkm-graph (authed, credentials cookie → RLS 자기 데이터만)
//
// 정책: S1 backend 가 기존 pkm_entries / brand_memory_entries / brands 를 읽어
//   {nodes, edges, summary} 그래프 구조로 집계(read-only). S2 카드/리스트(모바일) ·
//   S3 그래프(데스크톱) 양쪽이 동일 구조를 소비. 본 타입들은 backend Pydantic 과 1:1 정합.
//   익명/무데이터 → 빈 nodes/edges + summary 전부 0 (graceful, 200).

/**
 * 그래프 노드 1개 — user / brand / pkm(개인 또는 브랜드 scope).
 * id 는 type 접두어로 네임스페이스 구분 ("user:" / "brand:" / "pkm:" / "bm:").
 */
export interface PkmGraphNode {
  id: string;
  type: "user" | "brand" | "pkm";
  label: string;
  /** PKM 노드의 scope (개인/브랜드). 비-PKM 은 미지정. */
  scope?: "personal" | "brand" | null;
  /** PKM 노드의 entry_type (preferred_tone 등). 비-PKM 은 미지정. */
  entry_type?: string | null;
  /** PKM 노드의 is_user_locked (🔒). 비-PKM 은 미지정. */
  locked?: boolean | null;
}

/**
 * 그래프 엣지 1개 — source → target 관계.
 * kind: owns(user→brand) / has_personal(user→개인 pkm) / has_brand_pkm(brand→브랜드 pkm).
 */
export interface PkmGraphEdge {
  source: string;
  target: string;
  kind: "owns" | "has_personal" | "has_brand_pkm";
}

/**
 * 집계 요약 카운트 (상단 요약 + 빈 그래프 판별용).
 */
export interface PkmGraphSummary {
  /** 개인 PKM entry 수. */
  personal: number;
  /** 브랜드 PKM entry 수 (전 brand 합). */
  brand: number;
  /** 사용자 소유 brand 수. */
  brands: number;
}

/**
 * GET /api/v1/me/pkm-graph 응답 — {nodes, edges, summary}.
 */
export interface PkmGraphResponse {
  nodes: PkmGraphNode[];
  edges: PkmGraphEdge[];
  summary: PkmGraphSummary;
}

// ─── Phase 9 Slice 5 — Select / Feedback types (ADR-030) ───────────────
//
// 참조:
//   - harness/backend/fastapi/schemas/plans.py (SelectPlanRequest/Response,
//     FeedbackRequest/Response — Phase 9 Slice 3)
//   - harness/backend/fastapi/routers/plans.py
//     (POST /plans/{id}/select, POST/GET /plans/{id}/feedback)
//
// 정책: 선택/반려 UI 는 page.tsx inline wrapper 로 추가 (PlanCard.tsx / component_map.md
// 무수정 ★). 본 타입들은 backend Pydantic 스키마와 1:1 정합.

/**
 * POST /plans/{plan_id}/select body.
 * selected_option_index 는 plan_candidates(3-plan) 배열 인덱스 (0–2).
 * selection_reason 은 자유 입력 (옵션).
 */
export interface SelectPlanRequest {
  selected_option_index: number;
  selection_reason?: string | null;
}

/**
 * POST /plans/{plan_id}/select 응답.
 */
export interface SelectPlanResponse {
  plan_id: string;
  selected_option_index: number;
  selection_reason?: string | null;
  selected_at: string;
}

/**
 * 피드백 event 종류. backend Literal["like","dislike","reject","regenerate"] 정합.
 */
export type FeedbackEventType = "like" | "dislike" | "reject" | "regenerate";

/**
 * POST /plans/{plan_id}/feedback body.
 * option_index 는 특정 candidate 대상 (0–2). null/미지정 = plan 전체.
 * reason 은 자유 입력 — backend FeedbackRepo 가 저장 전 PII 마스킹.
 */
export interface FeedbackRequest {
  event_type: FeedbackEventType;
  option_index?: number | null;
  reason?: string | null;
}

/**
 * POST /plans/{plan_id}/feedback 응답.
 */
export interface FeedbackResponse {
  plan_id: string;
  event_type: string;
  option_index?: number | null;
  recorded_at: string;
}
