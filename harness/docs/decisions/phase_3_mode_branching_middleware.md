# ADR-013: Phase 3 Mode Branching — Page Redirect over Middleware

> Status: accepted (Phase 3 Slice 5, 2026-05-28)
> Author: Phase 3 Slice 5 sub-agent
> Related: ADR-010 (4-layer minimal), ADR-011 (Variants 3 components), ADR-012 (Tailwind tokens mapping)

---

## Context

Phase 2 `apps/web/mode_branching.md` (yaml spec) → Phase 3 코드 구현. /new 진입 시
사용자 컨텍스트(brand/series 보유 여부) 기반 자동 분기 라우팅 필요. Slice 5에서
yaml → TS 변환 + 라우팅 진입점 1개 추가.

라우팅 분기 위치 결정이 필요:
- (A) Next.js `middleware.ts` — 서버 측, 모든 요청 가로채기, edge runtime
- (B) `/new/page.tsx` 클라이언트 redirect — 페이지 컴포넌트에서 `useRouter().replace`
- (C) API route + 클라이언트 polling — `/api/branch` → JSON 응답 → 클라이언트 redirect

추가 제약:
- Phase 3 = 익명 phase (Supabase Auth 미도입). Phase 5에서 도입 예정
- `mode_branching.md` §0.3 적용 시점: "Phase 3: Next.js middleware로 라우팅 구현" 명시
  그러나 Auth 부재 상황에서 middleware는 user 데이터를 fetch할 수 없음 → Phase 5 도입과 함께 재검토 적합
- Phase 1 baseline (Next.js 14 App Router) 보존
- session storage state machine (Slice 2/4) 보존 — 클라이언트 측 상태

---

## Decision

**(B) `/new/page.tsx` 클라이언트 redirect 채택**.

```typescript
// apps/web/app/new/page.tsx
'use client';
import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { resolveMode, getMockUserContext } from '@/lib/mode_branching';

export default function NewEntryPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  useEffect(() => {
    const ctx = getMockUserContext(/* searchParams */);
    const result = resolveMode(ctx);
    router.replace(result.redirectPath);
  }, [router, searchParams]);
  return <main>{/* 로딩 placeholder */}</main>;
}
```

라우팅 로직 자체는 `apps/web/lib/mode_branching.ts` 순수 함수로 분리:
- `resolveMode(ctx: UserContext): BranchingResult` — yaml 4 branching_rules + 3 override_rules 1:1 정합
- `getMockUserContext(searchParams)` — Phase 5 Auth 도입 전 mock 소스

---

## Alternatives

### A. `middleware.ts` (서버 측 redirect)

**장점**:
- SEO/성능 우수 (클라이언트 렌더 전 redirect)
- mode_branching.md §0.3 원래 의도와 정합

**단점**:
- Edge runtime에서 Supabase user fetch 복잡 (cookies → JWT → user → brands/series 4-hop)
- Phase 3 = Auth 미도입 → middleware에서 분기할 user 데이터 없음 → 실질적으로 default Discovery 항상 hit
- Middleware는 globals.css / Tailwind 적용 안 되므로 로딩 화면 표현 불가
- 회귀 위험: 모든 요청 가로채기 → Phase 1 경로 (/, /plan) 영향 가능
- Phase 5 Auth 도입 시 middleware 재작성 필요 → 2번 작업

→ **기각**. Phase 5 도입 시 별도 ADR로 재논의.

### B. `/new/page.tsx` 클라이언트 redirect ★ 채택

**장점**:
- Phase 3 익명 phase에 적합 — Auth 없이 mock context로 동작
- `mode_branching.ts` 순수 함수로 분리되어 Phase 5 Auth 합류 시 mock 1곳만 교체
- 로딩 placeholder 표시 가능 (UX)
- URL query (?new=true / ?quick=true) override 지원 간단
- Phase 1 회귀 0 (다른 route 영향 없음)

**단점**:
- 클라이언트 측 redirect라 첫 paint 후 router.replace → 미세한 깜박임 가능 (placeholder로 완화)
- SEO 영향 (Phase 3 영역 외 — 실 SEO는 Phase 10+ marketing 페이지에서 검토)

→ **채택**.

### C. API route + 클라이언트 polling

**장점**:
- 분기 로직 서버 측 단일 진실 (Phase 11+ ABAC 합류 가능)

**단점**:
- Over-engineering (Phase 3에서 분기 로직은 yaml 정적 규칙 4개 + override 3개. API 호출 불필요)
- 네트워크 1-hop 추가 → 사용자 체감 지연
- Phase 4 backend `/api/v1/plans/start` (api_contract §8.1)가 mode 반환 예정이므로 중복

→ **기각**. Phase 4+ 검토 (이미 별도 endpoint 계획 있음).

---

## Consequences

### Positive
- Phase 5 Auth 도입 전까지 Auth 없이 동작 (mock context)
- `getMockUserContext()` 1곳만 교체하면 Phase 5 마이그 완료 (replaceability L)
- URL query override 지원 (`?new=true` / `?quick=true`) — 디버깅/테스트 용이
- Phase 1 회귀 0 (다른 route 영향 없음)
- mode_branching.md yaml ↔ mode_branching.ts 함수 1:1 정합 (변경성 L 유지)

### Negative
- 클라이언트 측 redirect라 SEO 영향 (Phase 3 영역 외, 실 SEO는 Phase 10+)
- 첫 paint 후 redirect라 미세한 placeholder 깜박임 가능 (loading spinner로 완화)
- Phase 5 Auth 도입 시 server component / middleware로 마이그 가능 (별도 ADR로 갱신)

### Neutral
- `mode_branching.md` §0.3 "Phase 3: Next.js middleware" 문구는 spec 의도였으나,
  Auth 미도입 상황에서 page redirect가 더 적합. mode_branching.md 자체는 본 Slice에서 수정 0줄 (Phase 2 spec read-only 정책 준수)
  → Phase 5 진입 시 mode_branching.md §0.3 갱신 검토 (별도 contract-change 절차)

---

## Verification

본 ADR 적용 후 다음이 통과:

```
✅ next build 0 errors
✅ tsc --noEmit 0 errors
✅ ESLint clean
✅ pytest 62/62 PASS (backend 회귀 0)
✅ audit_naming 0 drift

✅ /new 진입 시 mock context (brandsCount=0) → /new/discovery/step/1 redirect (rule_new_user)
✅ /new?new=true → /new/discovery/step/1 redirect (user_new_project)
✅ /new?quick=true → 현재 mock brandsCount=0이므로 fallthrough → rule_new_user → /new/discovery/step/1
✅ Phase 1 / 페이지 + /plan 페이지 0 회귀
```

수동 4 branching_rules + 3 override_rules 검증은 Slice 5 QA report §5 매트릭스 참조.

---

## Related

- ADR-010 — 4-layer minimal (Phase 2 Slice 1)
- ADR-011 — Variants 3 components (Phase 2 Slice 1)
- ADR-012 — Tailwind tokens mapping (Phase 3 Slice 1)
- `apps/web/mode_branching.md` (Phase 2 yaml spec — read-only, 본 Slice 0줄 수정)
- `apps/web/lib/mode_branching.ts` (Slice 5 TS 변환 구현)
- `apps/web/app/new/page.tsx` (Slice 5 진입점 redirect)
- `apps/web/page_map.md` (/new route 명세 — Phase 2, read-only)

---

## Change Log

- 2026-05-28: Phase 3 Slice 5 — ADR-013 최초 작성. mode_branching.ts + /new/page.tsx 채택.
