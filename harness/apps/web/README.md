# apps/web — Dreammate Studio (Next.js 14 PWA)

> Phase 1 Slice 6: 입력 페이지 + 결과 페이지 MVP

## 위치

`harness/apps/web/`

## 상태

- Phase 1 Slice 6 (Next.js 14 진입 UI) 완료
- Discovery Wizard / Quick Mode / Generation Stepper 는 Slice 7+ / Phase 3 에서 추가

## 기술 스택

- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- React 18 Server Components + 필요한 곳만 `'use client'`

## 페이지

- `/` (`app/page.tsx`) — 텍스트 입력 + 제출 버튼 (Slice 6 단순화: Wizard UI 없음)
- `/plan` (`app/plan/page.tsx`) — 백엔드 응답에서 받은 단일 PlanCard 표시

## 컴포넌트

- `components/PlanCard.tsx` — output_schema §8.1 Plan 1개 카드 렌더
- `components/SubmitButton.tsx` — primary CTA (44px+ 터치 타겟)

## 라이브러리

- `lib/api.ts` — `generate()` fetch wrapper. Envelope 성공 + ErrorEnvelope/FastAPI default 양 형식 처리.
- `lib/types.ts` — backend `output.py` 의 Meta/Plan/Body/Validation/Envelope/ErrorEnvelope 타입.

## 로컬 실행

```bash
# 1. 의존성 설치 (최초 1회)
npm install

# 2. 환경 변수 복사
cp .env.local.example .env.local
# (필요 시 NEXT_PUBLIC_API_URL 수정)

# 3. 백엔드 (FastAPI) 먼저 기동 — apps/backend 또는 backend/fastapi 참조
#    기본 http://localhost:8000

# 4. 개발 서버
npm run dev
# http://localhost:3000
```

빌드:

```bash
npm run build
npm start
```

타입 / 린트:

```bash
npm run typecheck
npm run lint
```

## 환경 변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend base URL |

## Slice 6 의 Phase 1 Deviation

본 Slice는 흐름 증명을 우선한다. 다음 항목은 후속 Slice 에서 보강:

- 4단계 Generation Progress Stepper (`api_contract.md §13`) — Slice 7+
- ErrorCard / user_action 매핑 (`frontend_design_contract.md §7`) — Slice 7+
- Service Worker / Offline fallback (`frontend_design_contract.md §6`) — Phase 2+
- Discovery Wizard 5장 카드 (`design.md §11`) — Phase 3
- Quick Mode + 한 줄 방향 (`design.md §12`) — Phase 3
- PWA 아이콘 PNG 실제 파일 — 후속 Slice / 디자인 에셋 작업 후

## 참조

- `apps/web/design.md` — 전체 UX 기준
- `apps/web/page_map.md` — MVP 10 페이지 구조
- `apps/web/component_map.md` — 컴포넌트 명세
- `docs/contracts/frontend_design_contract.md` — 토큰/접근성/PWA contract
- `phases/active/phase-1-mvp-basic-flow/work_plan.md` §"Slice 6"
