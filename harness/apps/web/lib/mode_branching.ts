/**
 * Phase 3 Slice 5 — mode_branching.md yaml → TS 변환.
 *
 * Phase 2 spec: `apps/web/mode_branching.md` §2 branching_rules (4) + §3 override_rules (3).
 * 원천 priority 평가 순서:
 *   override > branching (priority 작은 순) > default
 *
 * Phase 5 Auth 도입 전이라 UserContext는 mock (sessionStorage 또는 default).
 * Phase 5에서 Supabase Auth + brands/series 데이터 합류 시:
 *   - getMockUserContext() → getUserContext() (실 supabase fetch)
 *   - mode_branching.ts §resolveMode 로직 그대로 유지 (yaml ↔ TS 정합)
 *
 * 참조:
 *   - apps/web/mode_branching.md (Phase 2 yaml spec, read-only)
 *   - apps/web/page_map.md /new entry
 *   - docs/decisions/phase_3_mode_branching_middleware.md (ADR-013, 본 Slice)
 *
 * 변경성 (replaceability_score.md §3.3 정합):
 *   - 임계값 변경 → 본 파일 + mode_branching.md 1줄씩 (수동 동기, L)
 *   - 새 rule 추가 → 본 파일 함수 +1 분기 + mode_branching.md yaml +1 (L)
 */

export type WizardMode = 'discovery' | 'discovery_from_step3' | 'quick';

/**
 * 사용자 컨텍스트.
 * Phase 5에서 Supabase Auth 데이터로 실 채움.
 */
export interface UserContext {
  /** Brand 보유 수 (0 = 신규 사용자) */
  brandsCount: number;
  /** 현재 active Brand의 Series 보유 수 */
  currentBrandSeriesCount: number;
  /** override flag — 사용자 명시 "새로 시작" (Dashboard / Workspace 진입) */
  forceNewProject?: boolean;
  /** override flag — 사용자 명시 "Quick Mode" (Settings advanced 또는 직접 URL) */
  forceQuick?: boolean;
}

/**
 * 분기 결과.
 * rule_id는 mode_branching.md yaml의 id와 1:1 정합.
 */
export interface BranchingResult {
  mode: WizardMode;
  redirectPath: string;
  rule_id: string;
  rationale: string;
}

/**
 * mode_branching.md §2 branching_rules + §3 override_rules 그대로 적용.
 *
 * 평가 순서 (mode_branching.md §0.2):
 *   1. override_rules — user_new_project / user_quick_force
 *   2. branching_rules priority 작은 순 — rule_new_user (1) → rule_brand_no_series (2) → rule_has_series (3)
 *   3. rule_default (priority 99) fallback
 *
 * direction_renarrow override는 Quick Mode Step 3 DirectionApprovalCard "다시 좁히기" 버튼 클릭 시
 * 컴포넌트가 직접 /new/discovery/step/1 로 router.push 하므로 본 함수에서 처리하지 않음
 * (mode_branching.md §3 표 1행과 정합).
 */
export function resolveMode(ctx: UserContext): BranchingResult {
  // === Override 1: user_new_project ===
  // 사용자 명시 "새로 시작" — 기존 컨텍스트 무시, Discovery 강제.
  if (ctx.forceNewProject) {
    return {
      mode: 'discovery',
      redirectPath: '/new/discovery/step/1',
      rule_id: 'user_new_project',
      rationale: '사용자 명시 "새로 시작" — 기존 컨텍스트 무시, Discovery 강제',
    };
  }

  // === Override 2: user_quick_force ===
  // 사용자 명시 Quick force — Brand 있을 때만 허용. Brand 없으면 자동으로 branching_rules로 fallthrough.
  if (ctx.forceQuick && ctx.brandsCount >= 1) {
    return {
      mode: 'quick',
      redirectPath: '/new/quick',
      rule_id: 'user_quick_force',
      rationale: '사용자 명시 Quick force — Brand 있을 때만 허용',
    };
  }

  // === Rule 1 (priority 1): rule_new_user ===
  // 신규 사용자 (Brand 0) → Discovery 7-step 강제 (onboarding).
  if (ctx.brandsCount === 0) {
    return {
      mode: 'discovery',
      redirectPath: '/new/discovery/step/1',
      rule_id: 'rule_new_user',
      rationale: '신규 사용자 — Brand 컨텍스트 0, Discovery 7-step 강제',
    };
  }

  // === Rule 2 (priority 2): rule_brand_no_series ===
  // Brand 있음, Series 신규 → Step 1 (Brand) / Step 2 (Domain) skip, Step 3 (Series)부터.
  if (ctx.brandsCount >= 1 && ctx.currentBrandSeriesCount === 0) {
    return {
      mode: 'discovery_from_step3',
      redirectPath: '/new/discovery/step/3',
      rule_id: 'rule_brand_no_series',
      rationale: 'Brand 있음, Series 신규 — Step 1/2 skip, Step 3 (Series)부터 시작',
    };
  }

  // === Rule 3 (priority 3): rule_has_series ===
  // Series 존재 → Quick Mode 짧은 흐름 (기존 컨텍스트 재활용).
  if (ctx.currentBrandSeriesCount >= 1) {
    return {
      mode: 'quick',
      redirectPath: '/new/quick',
      rule_id: 'rule_has_series',
      rationale: 'Series 존재 — Quick Mode 짧은 흐름',
    };
  }

  // === Rule default (priority 99): rule_default ===
  // 분류 불가 — 안전한 default Discovery (정보 더 많이 수집).
  return {
    mode: 'discovery',
    redirectPath: '/new/discovery/step/1',
    rule_id: 'rule_default',
    rationale: '분류 불가 — 안전한 default Discovery',
  };
}

/**
 * Phase 3 mock UserContext.
 *
 * 현재 (Phase 1/3): 익명 사용자, 신규 진입 가정.
 *   - brandsCount = 0 (Brand 미생성)
 *   - currentBrandSeriesCount = 0
 * 결과적으로 rule_new_user 가 항상 hit → /new/discovery/step/1.
 *
 * URL query override 지원:
 *   - ?new=true     → forceNewProject (Discovery 강제)
 *   - ?quick=true   → forceQuick (Brand 있을 때만, mock에서는 brandsCount 0이므로 fallthrough)
 *
 * Phase 5에서 Supabase Auth 데이터로 교체:
 *   const { data: { user } } = await supabase.auth.getUser();
 *   const { data: brands } = await supabase.from('brands').select('id').eq('user_id', user.id);
 *   const { data: currentBrand } = await supabase.from('brands').select('id').eq('user_id', user.id).eq('is_active', true).single();
 *   const { data: series } = currentBrand
 *     ? await supabase.from('series').select('id').eq('brand_id', currentBrand.id)
 *     : { data: [] };
 *   return {
 *     brandsCount: brands?.length ?? 0,
 *     currentBrandSeriesCount: series?.length ?? 0,
 *     forceNewProject: searchParams?.get('new') === 'true',
 *     forceQuick: searchParams?.get('quick') === 'true',
 *   };
 */
export function getMockUserContext(searchParams?: URLSearchParams): UserContext {
  return {
    brandsCount: 0,
    currentBrandSeriesCount: 0,
    forceNewProject: searchParams?.get('new') === 'true',
    forceQuick: searchParams?.get('quick') === 'true',
  };
}
