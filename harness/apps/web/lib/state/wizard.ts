/**
 * Phase 3 Slice 2 — wizard state machine baseline.
 *
 * Discovery + Quick 두 흐름이 공유하는 session storage state.
 * Phase 5 Auth 도입 시 server-side persistence (Supabase) 로 migration 검토.
 *
 * key 구조:
 *   dreammate.wizard.discovery.<step>  — Discovery 흐름 (step1~step7)
 *   dreammate.wizard.quick.<step>      — Quick 흐름 (Slice 4)
 *
 * 참조:
 *   - apps/web/discovery_flow.md §1 (Step 1 → Step 2 propagation)
 *   - apps/web/quick_flow.md (Slice 4 확장)
 *
 * SSR safe: typeof window === 'undefined' 시 no-op.
 */

const STORAGE_KEY_PREFIX = 'dreammate.wizard';

export type WizardPrefix = 'discovery' | 'quick';

export interface WizardStepState<T = unknown> {
  step: string;
  data: T;
  updatedAt: string; // ISO8601
}

export function setWizardStep<T>(
  prefix: WizardPrefix,
  step: string,
  data: T,
): void {
  if (typeof window === 'undefined') return; // SSR safe
  const key = `${STORAGE_KEY_PREFIX}.${prefix}.${step}`;
  const value: WizardStepState<T> = {
    step,
    data,
    updatedAt: new Date().toISOString(),
  };
  try {
    window.sessionStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    // Quota / private mode — graceful skip
    if (typeof console !== 'undefined') {
      console.warn('wizard setStep failed:', e);
    }
  }
}

export function getWizardStep<T>(
  prefix: WizardPrefix,
  step: string,
): T | null {
  if (typeof window === 'undefined') return null;
  const key = `${STORAGE_KEY_PREFIX}.${prefix}.${step}`;
  try {
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as WizardStepState<T>;
    return parsed.data;
  } catch {
    return null;
  }
}

export function clearWizard(prefix: WizardPrefix): void {
  if (typeof window === 'undefined') return;
  const keysToRemove: string[] = [];
  for (let i = 0; i < window.sessionStorage.length; i++) {
    const key = window.sessionStorage.key(i);
    if (key?.startsWith(`${STORAGE_KEY_PREFIX}.${prefix}.`)) {
      keysToRemove.push(key);
    }
  }
  keysToRemove.forEach((k) => window.sessionStorage.removeItem(k));
}
