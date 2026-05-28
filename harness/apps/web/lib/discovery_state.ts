/**
 * Phase 3 Slice 2 + Slice 3 — Discovery 7-step state.
 *
 * Slice 2: Step 1 (Brand) state baseline.
 * Slice 3: Step 2~7 helpers + generic save/load + DirectionApprovalCard payload type.
 *
 * 참조:
 *   - apps/web/discovery_flow.md §1~§7
 *   - apps/web/lib/state/wizard.ts (storage primitive)
 *   - apps/web/component_map.md §DirectionApprovalCard (Behavior layer Props)
 */

import { setWizardStep, getWizardStep } from './state/wizard';

// ─── Step 1 (Slice 2 baseline — 보존) ─────────────────────────────────

export interface DiscoveryStep1State {
  selectedCardId: string | null;
  /** user_direct_input 모드일 때만 채워짐 */
  userInputText?: string;
}

export function saveDiscoveryStep1(state: DiscoveryStep1State): void {
  setWizardStep<DiscoveryStep1State>('discovery', 'step1', state);
}

export function loadDiscoveryStep1(): DiscoveryStep1State | null {
  return getWizardStep<DiscoveryStep1State>('discovery', 'step1');
}

// ─── Step 2~4 (Slice 3 — BrandDirectionCard 패턴 재사용) ───────────────

/** Step 2 Domain — BrandDirectionCard 변형 × 5 (P-002 output_schema §4) */
export interface DiscoveryStep2State {
  selectedCardId: string | null;
  userInputText?: string;
}

/** Step 3 Series — BrandDirectionCard 변형 × 5 (P-003 output_schema §5) */
export interface DiscoveryStep3State {
  selectedCardId: string | null;
  userInputText?: string;
}

/** Step 4 Target — BrandDirectionCard 변형 × 5 (P-004 part 1 output_schema §6) */
export interface DiscoveryStep4State {
  selectedCardId: string | null;
  userInputText?: string;
}

// ─── Step 5 (form 변형 — 다중선택 chip, 5-card 예외) ──────────────────

/**
 * Step 5 Tone — ToneChipsForm (다중선택 chip 8개 + skip)
 * U2-7 결정 (2026-05-27): chip 패턴 채택, 슬라이더 X.
 * discovery_flow.md §5.1 정합.
 */
export interface DiscoveryStep5State {
  selectedTones: string[];
  skipped?: boolean;
}

// ─── Step 6 (DirectionApprovalCard, verbose variant) ─────────────────

/**
 * Step 6 Direction Summary — DirectionApprovalCard verbose
 * P-005 oneline_direction (output_schema §7).
 * direction_approval.md / component_map.md §DirectionApprovalCard 정합.
 */
export interface DirectionReason {
  step: string; // "Step 1 Brand" 등
  value: string; // "정보형 콘텐츠 선택"
}

export interface DiscoveryStep6Direction {
  text: string;
  reasons?: DirectionReason[];
  revise_count?: number;
}

export interface DiscoveryStep6State {
  direction: DiscoveryStep6Direction;
  approved?: boolean;
  editedText?: string;
}

// ─── Step 7 (Generate — Phase 1 PlanCard 재사용) ──────────────────────

/**
 * Step 7 Generate — Phase 1 envelope를 그대로 보관.
 * Phase 4에서 SSE / 3-plan 활성 시 확장.
 */
export interface DiscoveryStep7State {
  generatedAt?: string;
  /** Phase 1 Envelope (lib/types.ts) — Slice 3 타이밍에는 unknown 보관 */
  envelope?: unknown;
}

// ─── Generic save/load (Slice 3) ──────────────────────────────────────

type StepNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7;

type DiscoveryStateByStep = {
  1: DiscoveryStep1State;
  2: DiscoveryStep2State;
  3: DiscoveryStep3State;
  4: DiscoveryStep4State;
  5: DiscoveryStep5State;
  6: DiscoveryStep6State;
  7: DiscoveryStep7State;
};

/** Step N 의 state 저장 (n=2~7 권장 — Step 1은 saveDiscoveryStep1 사용도 가능) */
export function saveDiscoveryStep<N extends StepNumber>(
  n: N,
  state: DiscoveryStateByStep[N],
): void {
  setWizardStep<DiscoveryStateByStep[N]>('discovery', `step${n}`, state);
}

/** Step N 의 state 복원. 없으면 null. */
export function loadDiscoveryStep<N extends StepNumber>(
  n: N,
): DiscoveryStateByStep[N] | null {
  return getWizardStep<DiscoveryStateByStep[N]>('discovery', `step${n}`);
}
