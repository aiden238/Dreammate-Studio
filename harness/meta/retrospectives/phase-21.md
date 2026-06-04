# Phase 21 회고 — /brain 4계층 깊이 + 출처 엣지

> 2026-06-04 | 제품 phase (Phase 19 그래프 확장) | additive/graceful

## 1. 무엇을 했나
Phase 19 `/me/pkm-graph` 를 확장:
- **S1 backend**: DomainRepo/SeriesRepo(BrandRepo 패턴 신규) + me.py 집계에 domain/series 노드(has_domain/has_series) + 브랜드 PKM 출처(source_plan_id → source 노드 + sourced_from, dedup) + graph.py type/kind/summary literal 확장. (CC-029 코드)
- **S2 frontend**: PkmGraph domain/series/source 노드 스타일(dashed/solid/dotted) + 전용 컬럼 레이아웃 + 엣지 스타일(accent/점선) + types.ts. CC-029(api_contract §8.7).

## 2. 핵심 성과 / 검증
- ★ **graceful/byte-identical**: domains/series/source 0 → 기존 그래프(user/brand/pkm) 노드·엣지 **불변**(summary 만 0키 additive). hermetic pytest 691→**698**(+7) + scenario_sim 36/36 + audit 0 + 프론트 typecheck/lint.
- 4계층 모델(User→Brand→Domain→Series) 구조가 그래프에 가시화 가능 + 브랜드 PKM 출처 추적(어디서 학습됐는가).
- DomainRepo/SeriesRepo = BrandRepo 패턴(graceful/RLS/in-memory) 재사용 — 일관성.

## 3. 학습 / 패턴
- **조사 우선이 범위를 정직하게 만들었다**: 사전 Explore 조사로 "domains/series 테이블 존재하나 repo 미구현 + 개인 pkm source_plan_id 부재"를 확인 → 범위를 정확히(브랜드 PKM 출처만, 개인은 이월) 설정. 헛빌드 방지.
- **graceful 확장의 정형**: 새 노드/엣지 타입을 additive 로 추가하되 "데이터 0 = 기존 불변"을 단위 test 로 고정 → 회귀 0 보장(Phase 19 패턴 계승).
- summary 에 키 추가는 nodes/edges byte-identical 이어도 응답 dict 변화 → 기존 test 의 summary 단언 갱신 필요(additive, 정당).

## 4. 정직한 한계 / 이월
- **개인 PKM 출처 엣지 불가**: pkm_entries 에 source_plan_id 컬럼 부재(0006) → 개인 PKM 의 feedback 출처는 미구현(이월 — migration 필요). 본 phase 출처는 **브랜드 PKM 한정**.
- **domains/series 실데이터 희소**: 생성 경로(UI/플로우) 미비 → 현재 대부분 빈 그래프. 구조는 완성, 풍부함은 실사용/별도 생성 기능.
- **프론트 시각 e2e 이월**: PkmGraph 렌더는 typecheck/lint + 단위(backend 집계)로 검증, 실 브라우저 4계층 그래프 시각은 미확인(Phase 19/20과 동일 환경 한계 — ResizeObserver/screenshot).

## 5. 산출물
- backend: repositories/{domain,series}_repo(신규) + me.py 집계 + schemas/graph.py(type/kind/summary)
- frontend: PkmGraph(domain/series/source 스타일+레이아웃+엣지) + types.ts
- contract: CC-029(api_contract §8.7)
- tests +7(691→698): test_pkm_graph_depth(4계층/출처/graceful/RLS)
- 회고/closing

## 6. 다음
- 이월: 개인 PKM 출처(source_plan_id migration) / domains·series 생성 기능 / video 노드(4계층 완성) / 프론트 시각 e2e.
- 로드맵: 배포 Gate B~G. (PKM 그래프 = 4계층 구조 + 출처 추적까지 확장 완료.)
