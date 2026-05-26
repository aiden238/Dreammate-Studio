# apps/web — Dreammate Studio (Next.js 14 PWA)

> Phase 1 Slice 7: Polish (ProgressStepper + ErrorCard + PWA manifest 보강)

## 위치

`harness/apps/web/`

## 상태

- Phase 1 Slice 6 (Next.js 14 진입 UI) 완료
- Phase 1 Slice 7 (Polish — ProgressStepper, ErrorCard, PWA manifest) 완료 → **Phase 1 MVP 종료 준비**
- Discovery Wizard / Quick Mode 는 Phase 3 에서 추가
- Service Worker / Offline 캐시는 Phase 2+ 에서 추가

## 기술 스택

- Next.js 14 (App Router)
- TypeScript
- TailwindCSS
- React 18 Server Components + 필요한 곳만 `'use client'`

## 페이지

- `/` (`app/page.tsx`) — 텍스트 입력 + 제출 + 진행 stepper + ErrorCard
- `/plan` (`app/plan/page.tsx`) — 단일 PlanCard + Critic 점수 + RAG 참조 수 + 저장 상태

## 컴포넌트

- `components/PlanCard.tsx` — output_schema §8.1 Plan 1개 카드. approach 배지 색상 + flow 총 길이.
- `components/SubmitButton.tsx` — primary CTA (44px+ 터치 타겟)
- `components/ProgressStepper.tsx` (Slice 7) — 4단계 진행 시각화 (Intent → RAG → Planning → Critic)
- `components/ErrorCard.tsx` (Slice 7) — error.code → title/body/액션 매핑 카드

## 라이브러리

- `lib/api.ts` — `generate()` fetch wrapper. Envelope 성공 + ErrorEnvelope/FastAPI default 양 형식 처리.
                Slice 7: 항상 정규화된 ErrorEnvelope + errorCode alias 반환.
- `lib/types.ts` — backend `output.py` 의 Meta/Plan/Body/Validation/Envelope/ErrorEnvelope 타입.
                  Slice 7: CriticEvaluation + RAGReference + Meta.project_id 추가.
- `lib/errors.ts` (Slice 7) — `error.code` → `DisplayError` 매핑.
                              INV-001 / E-LLM-* / E-RAG-* / E-DB-* / E-SEC-* / NET-* / UNK-* 13개 규칙.

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

## 구조 (Slice 7 기준)

```
apps/web/
├── app/
│   ├── globals.css        # Tailwind + prefers-reduced-motion + safe-area
│   ├── layout.tsx         # metadata (manifest, theme, apple-web-app)
│   ├── page.tsx           # 입력 + ProgressStepper + ErrorCard
│   └── plan/
│       └── page.tsx       # 결과 + Critic 점수 + RAG 참조 수
├── components/
│   ├── ErrorCard.tsx      # (Slice 7) 코드별 user 메시지 + 액션
│   ├── PlanCard.tsx       # (Slice 6 + 7 enhancement)
│   ├── ProgressStepper.tsx # (Slice 7) 4단계 시각화
│   └── SubmitButton.tsx
├── lib/
│   ├── api.ts             # fetch wrapper (errorCode alias 포함)
│   ├── errors.ts          # (Slice 7) code → DisplayError 매핑
│   └── types.ts           # backend envelope TS interfaces
├── public/
│   ├── icons/
│   │   ├── icon-192.svg   # (Slice 7) any-purpose
│   │   ├── icon-512.svg
│   │   └── maskable-512.svg
│   └── manifest.json      # (Slice 7) full PWA manifest
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── postcss.config.js
└── .eslintrc.json
```

## Slice 7 에서 충족한 항목

- design.md §22 — 4단계 Generation Stepper
- design.md §20 — Error UX 원칙 (코드 매핑, 액션 최대 2개)
- frontend_design_contract.md §6.1 — PWA manifest 필수 필드 + icons (any/maskable)
- frontend_design_contract.md §7 — ErrorCard + user_action 매핑
- error_response_contract.md §5 / §6 — 사용자 메시지 + user_action 키

## Phase 2+ 이월

- Service Worker / Offline cache (`frontend_design_contract.md §6.2`)
- Discovery Wizard 5장 카드 (`design.md §11`) — Phase 3
- Quick Mode + 한 줄 방향 (`design.md §12`) — Phase 3
- 실제 SSE/폴링 기반 단계별 stepper 갱신 — Phase 4+
- PNG 아이콘 (현재 SVG, 브라우저 호환성 충분하나 디자인 에셋 작업 후 PNG 추가 권장)
- shadcn/ui 토큰 alias 통합

## 참조

- `apps/web/design.md` — 전체 UX 기준
- `apps/web/page_map.md` — MVP 10 페이지 구조
- `apps/web/component_map.md` — 컴포넌트 명세
- `docs/contracts/frontend_design_contract.md` — 토큰/접근성/PWA contract
- `docs/contracts/error_response_contract.md` — 에러 코드 + user_message 표준
- `phases/active/phase-1-mvp-basic-flow/work_plan.md` §"Slice 7"
