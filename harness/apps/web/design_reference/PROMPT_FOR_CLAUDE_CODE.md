# Claude Code 실행 프롬프트

현재 저장소의 Dreammate Studio 프론트엔드를 주황 포인트 + 아이보리·베이지 기반 디자인으로 이식하라.

작업 전 다음을 순서대로 읽어라.

1. `harness/PROJECT_STATE.md`
2. `harness/AGENTS.md`
3. 현재 active Phase 문서
4. `harness/apps/web/CLAUDE.md`
5. `harness/apps/web/design_reference/README.md`
6. `harness/apps/web/design_reference/VISUAL_CONTRACT.md`
7. `harness/apps/web/design_reference/PAGE_MAPPING.md`
8. `harness/apps/web/design_reference/COMPONENT_MAPPING.md`
9. `harness/apps/web/design_reference/IMPLEMENTATION_PLAN.md`
10. `harness/apps/web/design_reference/ACCEPTANCE.md`
11. `harness/apps/web/design_reference/reference/style-guide.html`
12. 필요한 페이지별 HTML 레퍼런스

## 첫 응답에서 할 일

아직 코드를 수정하지 마라.

다음만 보고하라.

1. 현재 route와 페이지 파일 목록
2. 공통 shell과 token의 현재 상태
3. 레퍼런스와 현재 코드 사이의 차이
4. 기존 기능을 깨뜨릴 위험
5. 수정할 파일 목록
6. Slice별 구현 계획
7. contract-change가 필요한 부분
8. PlanCard를 수정하지 않고 구현 가능한지
9. AppShell의 `HIDDEN_PREFIXES` 회귀 방지 방법
10. 테스트 계획

## 승인 후 구현 원칙

- API·DB·output schema를 변경하지 않는다.
- 정적 HTML을 복사하지 않고 기존 React/Tailwind 컴포넌트로 번역한다.
- 목업 데이터를 하드코딩하지 않는다.
- 우선 토큰 → shell → 홈 → discovery → plan → brain 순서로 진행한다.
- 각 Slice 후 typecheck, lint, 관련 테스트를 실행한다.
- 한 Slice에서 실패하면 다음 Slice로 넘어가지 않는다.
- 모바일 360px과 데스크톱 1024px 이상을 모두 검증한다.
- 기존 ErrorCard, ProgressStepper, AuthGuard, SSE, feedback, PKM 기능을 유지한다.
- PlanCard는 우선 외부 wrapper 방식으로 유지한다.
- AppShell이 `/new`, `/plan`의 고정 CTA를 덮지 않게 한다.

최종 결과는 `ACCEPTANCE.md`의 체크리스트를 전부 충족해야 한다.
