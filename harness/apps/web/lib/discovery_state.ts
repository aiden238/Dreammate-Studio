/**
 * Phase 3 Slice 2 — Discovery 7-step state baseline.
 *
 * Slice 2: Step 1 (Brand) state만 정의. Slice 3에서 Step 2~7 확장.
 *
 * 참조:
 *   - apps/web/discovery_flow.md §1
 *   - apps/web/lib/state/wizard.ts (storage primitive)
 */

import { setWizardStep, getWizardStep } from './state/wizard';

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

// TODO(Slice 3): saveDiscoveryStep2 ~ saveDiscoveryStep7 + loadDiscoveryStep2~7
// 패턴: Step 1과 동일 (selectedCardId + optional userInputText).
