# frontend_boundary.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 0은 contract / 골격 정의 단계. Phase 1+ 첫 frontend 페이지 구현 시작 시점에 책임 경계를 정량 정의한다. 그 전까지는 `tech_stack_contract.md` §2.1, `frontend_design_contract.md`, `apps/web/design.md`로 충분.

## Scope (TBD)

본 contract가 다룰 범위:

- 웹 전용 UI (apps/web) 책임:
    - 모든 화면 / 라우팅 (Next.js App Router)
    - shadcn/ui 기반 컴포넌트 / Tailwind 스타일
    - 폼 입력 검증 (1차, zod 스키마)
    - 사용자 인터랙션 (카드 클릭, 거절 이유 입력 등)
    - SSE 구독 (progress stepper)
    - 클라이언트 캐싱 (SWR 또는 TanStack Query)
- shared-types (공통 타입) 책임:
    - output_schema 본문 타입 (TypeScript 자동 생성 또는 수동)
    - error_response envelope 타입
    - API request/response 타입
    - Expo 전환 시 그대로 재사용 가능한 형태
- api-client 책임:
    - fetch wrapper (Authorization, X-Request-ID 자동 부착)
    - 에러 envelope 자동 처리 (error.code → UI 액션)
    - SWR 또는 TanStack Query hook 생성
    - SSE 구독 helper
    - Expo 전환 시 그대로 재사용 가능한 형태 (fetch는 양쪽 호환)
- Supabase Client 책임:
    - Auth 직접 호출 (login / logout / refresh)
    - 단 sensitive write는 backend 경유 (RLS 우회 필요 시)
    - Realtime 구독 (Phase 5+)
- frontend 검증 vs backend 검증:
    - frontend는 UX 보조 (즉시 피드백)
    - backend는 단일 진실 (보안)
    - frontend 검증 누락은 보안 사고 아님
- 캐싱 정책:
    - GET 조회: SWR + 30s revalidate
    - POST 후: 관련 캐시 invalidate
    - Cache-Control 헤더 따름 (api_contract §3.2)
- 에러 노출 정책:
    - error.user_message만 노출 (error.message 금지)
    - error.user_action에 매핑된 버튼만 표시
    - request_id는 "문의하기" 폼에 자동 첨부
- Phase 11+ 모바일 전환:
    - shared-types + api-client는 그대로
    - apps/web → apps/mobile (Expo) 분리
    - 단 frontend_design_contract와 컴포넌트 매핑 유지

## Known Dependencies (when filled in)

외부 표준:
- React 18+ best practices
- Next.js App Router 가이드
- WCAG 2.1 AA (accessibility_contract와 연계)

내부 의존 contract:
- `docs/contracts/tech_stack_contract.md` §2.1 (frontend 스택)
- `docs/contracts/frontend_design_contract.md` (UI 표준)
- `docs/contracts/api_contract.md` (endpoint 호출)
- `docs/contracts/output_schema.md` (응답 본문 타입)
- `docs/contracts/error_response_contract.md` (에러 envelope)
- `apps/web/design.md` (디자인 시스템)
- `apps/web/page_map.md` (라우팅)
- `apps/web/component_map.md` (컴포넌트)
- `docs/contracts/backend_boundary.md` (placeholder, 책임 분리 짝)
- `docs/contracts/accessibility_contract.md` (placeholder)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 1+ 진입 (첫 frontend 페이지 구현 시작 시점)
- 또는 shared-types 폴더 구조 결정 시점
- 또는 api-client 라이브러리 첫 작성 시점
- 또는 Expo 전환 검토 시점 (Phase 21+)

## Related Skill / Phase

- Skill: `design-review`
- Phase: 1+
- 책임자: AI(초안) + 사용자(검토)
