# Implementation Plan — Small Slices

## Slice 0 — Audit / Baseline

코드 수정 전:

- route 목록
- 페이지 파일
- 컴포넌트 목록
- token 사용처
- `primary-*`, `neutral-*` 직접 사용처
- AppShell 노출 경로
- PlanCard 수정 제한
- 현재 typecheck/lint/build 결과

산출물:

- 변경 파일 목록
- 위험 목록
- before screenshot 또는 구조 기록

---

## Slice 1 — Token Foundation

대상:

- `app/globals.css`
- `tailwind.config.ts`
- 필요 시 font 설정

내용:

- 주황·베이지 semantic token
- warm neutral
- Paperlogy display
- SUIT UI
- Noto Serif KR editorial
- legacy color compatibility

검증:

- 기존 화면 기능 변화 없음
- 대비
- build

---

## Slice 2 — AppShell

대상:

- `components/AppShell.tsx`
- 필요 시 작은 하위 컴포넌트

내용:

- desktop primary rail
- desktop secondary sidebar
- mobile bottom nav 유지
- current route active state

검증:

- `/`, `/brain`에서 표시
- `/login`, `/new/**`, `/plan/**`에서 숨김
- CTA overlap 없음
- 360px / 1024px

---

## Slice 3 — Home

대상:

- `app/page.tsx`
- 필요 시 presentation 컴포넌트

내용:

- Hero
- prompt panel
- 상황 버튼
- 시작 카드
- 주황 CTA

유지:

- 이미지 첨부
- startPlan
- error
- loading
- route href

---

## Slice 4 — Discovery / Branding

대상:

- branding page
- discovery step page
- choice components
- direction summary

내용:

- 2열 카드
- 현재 방향 요약
- 책 페이지 summary
- 모바일 1열
- sticky CTA

유지:

- LLM flow
- 직접 입력
- 이전/다음
- API

---

## Slice 5 — Plan Generation and Comparison

대상:

- `app/plan/[plan_id]/page.tsx`
- wrapper components
- ProgressStepper style

내용:

- generation state
- 3-column comparison
- Brand Memory aside
- selected visual state
- feedback controls

유지:

- PlanCard 우선 무수정
- SSE
- select
- feedback
- reject
- sessionStorage
- AuthGuard

---

## Slice 6 — Final Output Presentation

기존 output schema에서 실제 제공되는 항목만 사용한다.

- summary
- script
- timeline
- shooting notes
- publish copy

없는 필드는 하드코딩하지 않는다.

---

## Slice 7 — Brain

대상:

- `/brain`
- graph component wrappers

내용:

- warm memory cards
- selected node orange
- neutral node beige/brown
- mobile cards
- desktop graph

---

## Slice 8 — QA / Cleanup

- dead class 제거
- duplicate token 제거
- contrast
- keyboard
- reduced motion
- responsive
- route regression
- API regression

명령:

```bash
npm run typecheck
npm run lint
npm run build
```
