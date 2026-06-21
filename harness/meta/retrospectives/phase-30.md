# 회고 — Phase 30: UI 리브랜딩 (Orange × Beige)

> 2026-06-15 | worktree `phase-27`(canonical) / branch phase-30-ui-rebrand | 기능 0 변화 = indigo/cyan → 따뜻한 주황×베이지 "종이 워크스페이스" behavior-preserving 리스킨

## 1. 무엇을 했나

사용자 채택(2026-06-15, Claude Code UI Handoff v1)에 따라 기능(API/SSE/Auth/PKM/피드백/route/타입)을 100% 보존하며 시각 체계만 indigo(#6366F1)/cyan → 주황(#F47B20)×아이보리·베이지로 재구성. 제품 경계(영상기획 브리프, 제작 아님) 유지.

- **S0 entry (3f522b4)**: design_reference/ 설치(VISUAL_CONTRACT/MAPPING/PLAN + reference HTML 13) + apps/web/CLAUDE.md. 진입 4점검 + audit_naming 0. **Slice 0 audit**: legacy scale 직접 사용 `primary-N00` 75 + `neutral-N00` 182 + status 68 = **~325건** → 토큰 재매핑 de-risk 근거 확보. 구현 0(entry+reference만).
- **S1 토큰 (bb0509b)**: globals.css `:root` semantic 토큰 + tailwind.config scale(primary/neutral 50~900)을 웜 팔레트로 재매핑 → `*-N00` 직접사용분 **자동 리컬러**. warning=앰버 / error=적갈색으로 주황 CTA와 구분. contract 3종(tokens/frontend_design/design.md) 동기. 폰트파일·deps 추가 없음.
- **S2 AppShell (b97e32e)**: 데스크톱(>=1024px) Primary Rail(76px)+Secondary Sidebar(244px), 모바일 기존 하단 탭바 유지. 라우팅/HIDDEN_PREFIXES/aria-current/safe-area 보존.
- **S3 홈 (263b470)**: app/page.tsx Hero + 웜 prompt panel + 4 상황 시작카드. startPlan/이미지첨부/검증/route 무수정.
- **S4 Discovery/Branding (77b84f0)**: 진행률 헤더 + ChoiceGrid/ChoiceCard/ToneChips 웜 리스킨. LLM Q&A 흐름·wizardStep·radiogroup 보존.
- **S5 Plan 비교 (1d3ba2b)**: PlanCard.tsx **무수정**, 외부 wrapper만 신규(ComparisonGrid/OptionFrame/FeedbackControls/BrandMemoryAside). API·SSE·sessionStorage 복원 전부 보존.
- **S6 Final-output (0c8a0c5)**: FinalBriefPanel wrapper — 현 output_schema 실데이터만 표시, 대본·체크리스트는 schema 미제공 → 준비중(graceful, 하드코딩 금지).
- **S7 Brain (7195983)**: PkmGraph 인라인 TOKEN(CSS var 미적용분) 웜 교체. 80/20(주황=root/hub 한정) 유지. page.tsx는 semantic 토큰으로 자동 리컬러=무변경.
- **S8 QA/정리 (0d5007e)**: PWA themeColor/manifest/아이콘 indigo→주황, lib/design_tokens.ts(dead 중복 소스) 동기. 전 tsx 스캔 — 활성 코드에 cool/indigo 리터럴 0.

결과: 전 슬라이스 tsc --noEmit 0 / next lint 0. backend/API/schema/route 변경 0건.

## 2. 잘된 점

- **scale 재매핑으로 ~325건 자동 리컬러** — Slice 0 audit로 직접 사용분을 수치화한 뒤, 컴포넌트 개별 편집이 아니라 tailwind.config scale 값 자체를 웜으로 바꿔 표면적을 최소화(de-risk).
- **PlanCard 무수정 wrapper 패턴 일관** — S5/S6에서 핵심 컴포넌트를 건드리지 않고 외부 frame/panel로만 리스킨 → 회귀 표면 0.
- **접근성·색상-외 표시 보존** — radiogroup/radio·aria-checked·focus-visible·44px 터치 + 선택 시 체크/라벨(색에만 의존 안 함)을 전 슬라이스에서 유지.
- **제품 경계 사수** — Final-output에서 schema 없는 제작 산출물을 하드코딩하지 않고 준비중 처리 → 브리프=제품, 제작 아님 경계 보존.

## 3. ★ 핵심 패턴 — behavior-preserving 리스킨 (토큰층 + wrapper)

- 충돌 우선순위(API/보안/접근성 > 동작/테스트 > 시각)를 명시 규율로 두고, 시각 변경을 **두 층**에만 격리: ① semantic 토큰 + scale 재매핑(globals.css/tailwind.config) ② 외부 wrapper 컴포넌트. 핸들러·상태·ref·API 호출은 전 슬라이스에서 무수정 — "클래스/마크업만 변경".
- 효과: 9개 슬라이스 모두 tsc/lint 0을 유지하며 8페이지 전체를 리스킨했고, backend/route는 단 한 줄도 안 바뀜.
- 잔재 처리의 경계: CSS var를 안 쓰는 곳(react-flow 인라인 style=S7, PWA 매니페스트/아이콘=S8, dead 토큰 소스 lib/design_tokens.ts)은 자동 리컬러가 닿지 않아 **수동 점검 슬라이스(S8 QA)**로 따로 정리해야 했다. → 토큰화되지 않은 색 소스가 리스킨의 long tail.

## 4. 불확실/한계 (U-1~U-4)

- **U-1**: 검증이 코드 레벨(tsc/lint + tsx 스캔)까지 — 실 렌더 픽셀/대비비(WCAG AA) 자동 측정은 미수행(headless 한계, phase-27 U-4와 동류).
- **U-2**: 폰트는 fallback 체인만 선언(Paperlogy/SUIT/Noto Serif KR) — 실제 웹폰트 파일·로딩은 미포함, 현재는 시스템 fallback으로 표시.
- **U-3**: dark-mode는 globals.css 주석 블록(TBD)으로 남김 — 잔여 #6366F1는 그 주석 안에만 존재.
- **U-4**: design_reference 13개 HTML과 실 구현의 1:1 시각 일치는 사람 눈 검토 필요(자동 대조 없음).

## 5. 이월

- **웹폰트 실제 설치**(Paperlogy/SUIT/Pretendard/Noto Serif KR 파일+로딩) — 현재 fallback만.
- **dark-mode 토큰 세트** — 주석 TBD 블록 활성화.
- **시각 회귀 자동화**(스크린샷 diff / 대비비 게이트) — 현 검증은 typecheck/lint 갈음.
- 제작 산출물 슬롯(대본·촬영 체크리스트·업로드 문구) — output_schema 확장 시 준비중 → 실데이터 전환.

## 6. 다음

UI 리브랜딩(orange×beige) behavior-preserving 완료 → **다음 = 사람 눈 시각 검토 + 실 렌더 대비비/폰트 확인 → 실사용 데모(phase-27 이월) 시 새 UI로**. 기능 불변이므로 실사용 마감 흐름과 독립 병행 가능.
