# CLAUDE.md — Dreammate Studio Web UI Implementation

이 파일은 `harness/apps/web/**`에서 작업하는 Claude Code용 로컬 지침이다.

상위 하네스의 다음 문서와 함께 적용한다.

- `../../PROJECT_STATE.md`
- `../../AGENTS.md`
- 현재 active Phase 문서
- `design.md`
- `page_map.md`
- `component_map.md`
- `../../docs/contracts/frontend_design_contract.md`

---

## 1. 작업 목적

기존 기능, API, 라우트, 저장, 피드백, SSE, Brand Memory를 유지하면서 프론트엔드 시각 체계를 다음 방향으로 변경한다.

> **주황 포인트 + 아이보리·베이지 기반의 영상기획 워크스페이스**

이 작업은 기능 확장이 아니라 시각·레이아웃·정보 계층 재구성이다.

---

## 2. 필수 참조 순서

1. `design_reference/README.md`
2. `design_reference/VISUAL_CONTRACT.md`
3. `design_reference/PAGE_MAPPING.md`
4. `design_reference/COMPONENT_MAPPING.md`
5. `design_reference/IMPLEMENTATION_PLAN.md`
6. `design_reference/ACCEPTANCE.md`
7. `design_reference/reference/style-guide.html`
8. 해당 페이지의 HTML 레퍼런스
9. 기존 `design.md`, `page_map.md`, `component_map.md`

---

## 3. 충돌 우선순위

```text
API·데이터·보안·접근성 contract
> 현재 동작하는 사용자 흐름과 테스트
> IMPLEMENTATION_PLAN.md
> VISUAL_CONTRACT.md
> PAGE_MAPPING.md
> HTML 레퍼런스의 시각적 계층
> 기존 design.md의 시각 규칙
> 기존 색상 토큰
```

HTML 레퍼런스는 **시각 기준**이다. 제품 코드가 아니다.

- 정적 HTML을 React에 그대로 붙이지 않는다.
- 목업 문구와 데이터를 하드코딩하지 않는다.
- 기존 API 상태와 타입을 재사용한다.
- 기존 컴포넌트를 우선 재사용하거나 외부 wrapper로 스타일링한다.

---

## 4. 반드시 유지할 것

- `/`, `/new/**`, `/plan/**`, `/brain`의 기존 동작
- Discovery / Quick 자동 분기
- 3개 기획안 비교와 선택
- 선택 이유, 좋아요·싫어요·반려 이유 저장
- SSE 진행 상태와 부분 결과
- ErrorCard와 재시도 흐름
- Brand Memory / PKM / Brain
- AuthGuard와 인증 흐름
- 모바일 하단 내비게이션
- 집중 플로우에서 AppShell을 숨기는 `HIDDEN_PREFIXES`
- 키보드 탐색, focus-visible, aria-label
- `prefers-reduced-motion`
- 기존 타입과 API 스키마

---

## 5. 특별 보호 규칙

### PlanCard

현재 `/plan/[plan_id]`는 `PlanCard.tsx`를 수정하지 않고 외부 wrapper에서 선택·피드백 기능을 결합해 온 이력이 있다.

따라서:

1. 우선 `PlanCard.tsx`를 수정하지 않는다.
2. `PlanOptionFrame`, `PlanComparisonGrid` 같은 외부 wrapper를 만든다.
3. 수정이 불가피하면 active Phase와 사용자 승인을 먼저 확인한다.
4. API·타입 변경 없이 표현 계층만 변경한다.

### AppShell

- `/login`, `/new`, `/plan`에서 하단 네비가 집중 CTA를 가리지 않아야 한다.
- 데스크톱 이중 사이드바를 추가하더라도 모바일 하단 내비는 유지한다.
- 숨김 경로 회귀를 반드시 테스트한다.

---

## 6. 금지

- API, DB, output schema 변경
- 정적 목업을 실제 기능으로 대체
- 기존 에러·로딩·빈 상태 제거
- 화면 전체를 주황색으로 채우기
- 새 UI 라이브러리 무단 추가
- 기존 기능 삭제 후 레퍼런스 화면만 표시
- archive Phase를 기본 근거로 사용
- `--no-verify`
- 한 커밋에서 전체 앱 재작성

---

## 7. 구현 원칙

1. 토큰과 폰트부터 변경한다.
2. 공통 shell을 먼저 만든다.
3. 페이지를 작은 Slice로 이식한다.
4. 모바일 360px에서 먼저 검증한다.
5. 기존 기능 테스트 후 다음 Slice로 이동한다.
6. 레퍼런스의 복잡한 장식보다 정보 계층을 우선한다.
7. `베이직 80% + 주황 포인트 20%` 비율을 지킨다.

---

## 8. 필수 명령

```bash
npm run typecheck
npm run lint
npm run build
```

프로젝트에 프론트 테스트가 있으면 함께 실행한다.
