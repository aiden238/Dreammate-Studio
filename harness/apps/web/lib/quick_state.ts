/**
 * Phase 3 Slice 4 — Quick Mode state machine (4-step).
 *
 * wizard.ts (Slice 2 baseline) prefix='quick' 위에 4 step state 정의.
 * sessionStorage key 구조:
 *   dreammate.wizard.quick.step1  — initial prompt
 *   dreammate.wizard.quick.step2  — follow-up answer (optional, skipped 가능)
 *   dreammate.wizard.quick.step3  — direction approval
 *   dreammate.wizard.quick.step4  — generate result envelope
 *
 * 참조:
 *   - apps/web/quick_flow.md §1.4 / §2.4 / §3 / §4
 *   - apps/web/lib/state/wizard.ts (storage primitive)
 *   - docs/contracts/output_schema.md §7 P-005 oneline_direction
 */

import { setWizardStep, getWizardStep } from './state/wizard';

// ─── Step 1 (initial prompt) ─────────────────────────────────────────

export interface QuickStep1State {
  /** Quick Mode 짧은 프롬프트 (10~300자, quick_flow.md §1.4) */
  initialPrompt: string;
}

// ─── Step 2 (follow-up question, optional) ───────────────────────────

export interface QuickStep2State {
  /** 사용자 답변 (skipped=true 시 undefined) */
  followUpAnswer?: string;
  /** AI에게 위임 (output_schema §7.2 missing_info에 자동 기록 — quick_flow.md §2.4) */
  skipped?: boolean;
}

// ─── Step 3 (DirectionApprovalCard, minimal variant) ─────────────────

export interface QuickStep3DirectionState {
  text: string;
  revise_count?: number;
}

export interface QuickStep3State {
  direction: QuickStep3DirectionState;
  approved?: boolean;
  /** onEditAndApprove 경유 시 채워짐 */
  editedText?: string;
}

// ─── Step 4 (Generate, Phase 1 endpoint 또는 mock) ───────────────────

export interface QuickStep4State {
  /** ISO8601 — UI 표시용 (실 envelope는 Phase 4+ 영역) */
  generatedAt?: string;
  /** Phase 1 Envelope (실 호출 시) — `lib/types.ts` Envelope */
  envelope?: unknown;
}

// ─── Generic save / load helpers ─────────────────────────────────────

export function saveQuickStep<T>(
  step: 1 | 2 | 3 | 4,
  state: T,
): void {
  setWizardStep('quick', `step${step}`, state);
}

export function loadQuickStep<T>(
  step: 1 | 2 | 3 | 4,
): T | null {
  return getWizardStep<T>('quick', `step${step}`);
}
