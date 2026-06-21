# 회고 — phase-29: 에이전트 UX 마감

> 2026-06-08~ | 브랜치 `phase-29-agent-ux` (main 미머지) | 신규 제품기능 0 = 경험·진입층 마감 + 멀티모달/그래프 폴리시

## 1. 무엇을 했나

"기능이 없는 게 아니라 **사용자가 기능까지 도달 못 하는 게 문제**" — 첫 사용자가 도움 없이 핵심 루프(아이디어→상황→질문→기획안→저장→내 brain)를 완주하도록 진입·용어·에이전트 느낌을 닫음. 기획 초안 = `meta/proposals/2026-06-08_agent-ux-mvp-close.md`(사용자 UI/UX 브리프 기반).

- **S0~S2 (7ffc0c2)**: ① S0 — 위저드 자체 고정 CTA를 Phase27 AppShell(고정 네비)이 덮어 "다음/생성/저장" 클릭 불가 → `/new`·`/plan` 에서 AppShell 숨김(집중 플로우). Discovery 안 넘어가던 버그 해소. ② S1 — 홈 = 슬로건 + 큰 입력창 + 4 상황 버튼(기존 route 재사용), 2 진입카드 교체. ③ S2 — jargon 제거(도메인/시리즈/타깃/톤 → 쉬운 질문), 코드/스키마 불변 표시 문자열만.
- **S3~S5 (dd833f6)**: S3 진행요약 칩(DiscoveryProgress, 완료✓·현재 강조) + S4 저장 후 Brain CTA([내 brain에서 보기]/[같은 방향 새 영상]/[SNS 준비중]) + S5 에이전트 느낌(생성중 메시지 + "내 brain 선호 N개 반영" 배너, graceful).
- **입력카드 폴리시 (8a2ed32)**: 라운드 카드 + 멀티모달 첨부 affordance(준비중, 정직 disabled). ★ Genspark 만능 기능그리드는 채택 X — 정체성 유지.
- **4 상황버튼 distinct (db0e6bf)**: 버튼3(SNS)이 goal 무시로 버튼2와 동일하던 것 → `goal` 을 branding LLM 까지 전달(sns_validation/organize 프레이밍 분기), additive.
- **A 멀티모달 (2c738a7)**: `vision_analyzer.py` — 레퍼런스 이미지 1회 비전 분석(gpt-4o-mini)→{summary, keywords}. A1=summary user_input 프리펜드(생성 반영), A2=keywords PKM 적재. images 없으면 호출0=byte-identical.
- **B1 /brain force 그래프 (c7b5530)**: 고정 계층 레이아웃 → d3-force 물리 시뮬(420 tick 결정적 settle, react-flow) Obsidian 풍 동적 그래프 + 필터 칩 4종 + 노드 드래그. 기존 {nodes,edges} 인터페이스 무변경.

결과: hermetic pytest 802→**821**(무회귀) + typecheck/lint 0 + next build 14 라우트 green.

## 2. 잘된 점

- **진입·도달 문제로 정밀화** — "신규 기능"이 아니라 "도달 못 함"이 진짜 갭임을 라이브 테스트로 확인하고 경험층만 마감(Phase 27 패턴 계승).
- **additive·byte-identical 일관** — goal 미지정/images 미첨부 시 기존과 동일(model_fields override·호출0), 실사용 활성과 테스트 결정성 양립.
- **영리한 멀티모달 스코프** — 이미지를 모든 planning 호출에 태우지 않고 레퍼런스 분석 1회로 한정, 비용·기획관점 정체성 유지(영상제작 X).
- **결정적 force 레이아웃** — golden-angle 초기좌표 + 명시 width/height로 headless/preview(ResizeObserver 부재)에서도 엣지/fitView 결정적.

## 3. ★ 핵심 사건 — 멀티모달 키워드 FK 23503 회귀 (P-LIVE-VERIFY-001)

- **발견**: 라이브 e2e 검증에서 멀티모달 레퍼런스 키워드가 PKM에 **0건 적재**.
- **원인**: `pkm_entries.source_plan_id` 가 `plans.id` 를 FK 참조하는데, A2 적재가 generate **초반(plans 행 영속 전)**에 실행 → 모든 INSERT 가 FK 위반(23503)으로 전량 실패 후 `except` 로 silent swallow.
- **대응 (18795d6)**: A1(요약 프리펜드)은 생성 입력이라 위치 유지, A2(키워드 적재)만 `_persist_plan_envelope` **직후로 이동** — 영속 성공 시 `source_plan_id=plan_id`(provenance·그래프 edge 보존), OFF 시 None. 회귀 가드 2종 추가(순서 검증 + no-image byte-identical). 라이브 demo pkm 0→4 학습 확인.
- **교훈**: graceful `except` 가 FK 위반을 삼켜 단위테스트는 green인데 실 적재 0 — **순서 의존(영속→provenance 적재)은 라이브 e2e가 아니면 안 잡힌다.** 자동 검증 = graceful 까지, 실 row 검증 = 라이브.

## 4. 불확실/한계 (U-1~U-4)

- **U-1**: 멀티모달 실 이미지 e2e는 라이브 1회 확인(demo) — 다양한 이미지·실패 패턴 폭넓은 검증은 후속.
- **U-2**: SNS 상황(버튼3)은 질문 프레이밍만 분기 — 완전한 "콘텐츠 실험 설계" 흐름은 2차.
- **U-3**: S5 "내 brain 반영" 배너는 getPkmGraph personal+brand>0 신호 기반(휴리스틱), 실 반영 강도 계측은 미상.
- **U-4**: 브랜치 `phase-29-agent-ux` main 미머지 — critic 품질 연구 아크와 동거(c90b08a handoff는 별 아크), 머지 시 PROJECT_STATE 충돌 조율 필요.

## 5. 이월

- 멀티모달 실 이미지 폭넓은 e2e + 비용 패턴 — 사용자 opt-in(비전 API).
- SNS "콘텐츠 실험 설계" 완전 흐름, S4 SNS 준비중 → 실기능 — 2차.
- phase-29-agent-ux → main 머지(연구 아크와 분리 머지 순서).

## 6. 다음

에이전트 UX 마감(로컬) 완료 → **다음 = 5~10명 실사용 테스트(첫-사용자 완주 통과기준 §18) → 2차 MVP(SNS·멀티모달 확장)**. 진입·도달 갭 닫힘이 전제.
