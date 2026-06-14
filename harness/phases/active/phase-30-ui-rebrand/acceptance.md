# Phase 30 — acceptance

- **A1 토큰**: 주황×베이지 semantic 토큰 + 폰트(Paperlogy/SUIT/Noto Serif KR) 적용, legacy scale(primary-N00/neutral-N00/status) **잔재 0**(보라/회색 없음), 대비 AA. (Slice 1)
- **A2 AppShell**: 데스크톱 Primary Rail + Secondary Sidebar + 모바일 하단탭, `HIDDEN_PREFIXES`(/login·/new·/plan) 회귀 0, CTA overlap 0 (360px·1024px). (Slice 2)
- **A3 기능 보존**: 전 route 동작 — startPlan/이미지첨부4/Discovery·Quick 분기/3안 비교·select/feedback(좋아요·싫어요·반려)/SSE 부분결과/PKM·Brain/AuthGuard. (Slice 3~7)
- **A4 경계**: final-output = **브리프 깊이만** — 없는 필드 숨김/준비중, 하드코딩 0. (Slice 6)
- **A5 force graph 색**: Brain 그래프 selected=orange / 일반=neutral, 노드 대비 확인, 모바일 카드·데스크톱 그래프 유지. (Slice 7)
- **A6 게이트**: `tsc 0` / `lint 0` / `build OK` + 80/20 색 비율 + 접근성(focus-visible·aria·reduced-motion). (Slice 8)
- **A7 contract**: design_system/tokens.md · frontend_design_contract.md · design.md Visual Style = contract-change 반영(코드와 정합).

> 검증: 각 Slice 후 tsc/lint + 해당 route 기능 회귀 + (변경 페이지) 라이브 스크린샷.
