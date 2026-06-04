# Phase 19 회고 — 2nd Brain 시각화 (마이페이지 PKM 도식화)

> 2026-06-04 | 제품 phase (런타임 有, gated/additive) | "발굴→축적→주입→**가시화**" 루프 완성

## 1. 무엇을 했나

축적된 PKM(개인 + 브랜드 + 4계층)을 `/brain`에서 보여주고 큐레이션하게 함. 읽기 레이어(신규 데이터모델 0).

- **S1**: `GET /api/v1/me/pkm-graph`(신규 /me 라우터) — 개인 pkm_entries + 소유 brands + 브랜드 brand_memory를 {nodes,edges,summary}로 집계, RLS 격리.
- **S2**: `/brain` 모바일 카드/리스트(scope 섹션 + 🔒 + empty state→브랜딩 세션) + 홈 진입 링크.
- **S3**: 데스크톱 react-flow(@xyflow/react@12) 그래프 — 반응형 lazy-load(데스크톱만, 모바일 번들 미포함) + 뷰 토글.
- **S4**: 큐레이션 — PATCH/DELETE `/me/pkm/{node_id}`(개인+브랜드, RLS+소유검증) + repo update/delete + /brain 잠금/편집/삭제 UI.

## 2. 핵심 성과 / 검증

- ★ **루프 완성**: 발굴(Phase 18 브랜딩)→축적(brand_memory/pkm_entries, Phase 17)→주입(Phase 17)→**가시화·큐레이션(Phase 19)**. moat(쌓이는 데이터)가 사용자-facing 자산으로.
- behavior-preserving: 신규 /brain + /me endpoint **additive**, 기존 흐름·모바일 byte-identical. pytest 641→**668**(+27: S1 8 + S4 19) + scenario_sim 36/36 + audit 0 + typecheck/lint.
- 모바일 우선 준수(검토 발견): 모바일=카드/리스트, 데스크톱=그래프(lazy-load) — design.md 제약("트리 아닌 breadcrumb") 정합.

## 3. 학습 / 패턴

- **검토가 설계를 구했다**: 초안의 "그래프 viz"가 모바일 우선과 충돌 → 검토에서 하이브리드(모바일 카드 + 데스크톱 그래프 lazy-load)로 수정. design.md 사전 확인이 핵심.
- **의존성 격리**: @xyflow/react를 데스크톱 dynamic(ssr:false)+조건부 렌더 → 모바일 번들 미포함. 무거운 dep의 비용 봉쇄.
- **AppShell 부재 발견**: 문서(component_map)엔 AppShell이 있으나 코드 미구현 → 홈 헤더 링크로 additive 진입(범위 밖 전역 셸 생성 회피).
- RLS 큐레이션: node_id prefix(pkm:/bm:) 분기 + 소유 검증(개인=auth_user_id, 브랜드=brand→user)으로 교차 사용자 변경/삭제 0.

## 4. 정직한 한계 / 이월

- **/brain 그래프 시각 e2e**: 신규 @xyflow 의존성 → 프론트 재기동 필요 → 본 phase는 **유닛(668)+typecheck**로 검증, 실 브라우저 그래프 렌더 시각 e2e는 이월(프론트 재기동 후).
- 데이터 빈약(실사용 누적 전): 빈/희소 그래프 → empty state로 완화. 풍부함은 실사용/브랜딩 세션 누적.
- viz 번들(@xyflow) 데스크톱 영향 — lazy-load로 모바일 0, 데스크톱 측정은 운영.

## 5. 산출물
- backend: routers/me.py(pkm-graph + PATCH/DELETE pkm) + schemas/graph.py + PkmRepo/BrandMemoryRepo update/delete + BrandRepo.list_for_user
- frontend: app/brain/page.tsx + components/brain/PkmGraph.tsx + lib/use_media_query.ts + api(getPkmGraph/update/delete) + types + 홈 링크 + @xyflow/react dep
- contract: CC-024(api_contract /me/pkm-graph·/me/pkm) + page_map(/brain)
- tests +27(641→668). 회고/closing.

## 6. 다음
- 이월: /brain 그래프 시각 e2e(프론트 재기동) / 데스크톱 그래프 데이터 풍부화(실사용) / 4계층 깊이(domains/series) + 출처 엣지(feedback→PKM).
- 로드맵: Phase 20 commercial_viral / 배포 Gate B~G. (PKM 루프 4단계 완성 — 발굴·축적·주입·가시화.)
