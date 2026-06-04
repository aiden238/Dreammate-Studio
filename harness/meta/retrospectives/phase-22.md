# Phase 22 회고 — domains/series 생성 기능 (4계층 데이터 풍부화)

> 2026-06-04 | 제품 phase | additive | ★ 라이브 데모 PASS

## 1. 무엇을 했나
4계층(User→Brand→Domain→Series)을 사용자가 직접 생성 → Phase 21 `/brain` 그래프가 빈 4계층에서 실데이터로 채워짐.
- **S1 backend**: DomainRepo/SeriesRepo **create**(BrandRepo insert 패턴) + POST /me/domains·/me/series + 소유검증(_owns_brand/_owns_domain). 401/404/422/503. CC-030.
- **S2 frontend**: /brain "지식 구조 (4계층)" 섹션 — 그래프에서 brand→domain→series 트리 도출 + 생성 입력(+도메인/+시리즈) + refetch. StructureCreateInput 컴포넌트. ★ 라이브 데모.

## 2. 핵심 성과 / 검증
- ★ **라이브 데모 PASS end-to-end**(eval/.../2026-06-22-... 리포트): 생성 API(도메인2/시리즈2, 미소유 404) → /me/pkm-graph 4계층 반영(summary domains:2/series:2 + has_domain/has_series 엣지) → /brain 구조 섹션 렌더(트리 + 생성 UI).
- behavior-preserving: 기존 /brain(읽기/큐레이션/그래프) + 그래프 집계 builder **무변경** — 생성 데이터가 Phase 21 집계로 자동 반영. hermetic pytest 698→**714**(+16) + scenario_sim 36/36 + audit 0 + typecheck/lint.
- RLS 소유검증: domain 은 본인 brand, series 는 본인 domain(2-hop) 하위만 생성(미소유 404).

## 3. 학습 / 패턴
- **Phase 21 집계의 배당**: 그래프 builder 를 "데이터를 읽어 반영"하게 설계한 덕에 Phase 22 는 **생성 경로만** 추가 → builder 0 변경으로 4계층 가시화. 읽기/쓰기 분리의 이점.
- **2-hop 소유검증**: series 는 domain→brand→user 2-hop. DomainRepo 가 brand_id 만 가지므로 "user 의 brand 들의 domain"을 모아 검증(_owns_domain). RLS 정형.
- **mock 공유 store 확장**: 라이브 데모 위해 런처가 DomainRepo/SeriesRepo store 도 monkeypatch 공유(요청 간 휘발 방지) — Phase 17 패턴 계승.
- 생성 repo 실패는 **503**(controlled) — unhandled 500 회피.

## 4. 정직한 한계 / 이월
- **데스크톱 그래프 시각**: domain/series 노드의 react-flow 시각은 headless ResizeObserver 한계(Phase 19/21 동일)로 육안 미확인 — 그래프 데이터 + 구조 섹션 렌더는 확인.
- **편집/삭제 미포함**: 본 phase 는 생성만. domain/series 편집·삭제는 후속.
- **위저드 연결 미포함**: /new/discovery 의 domain/series 자동 생성 연결은 별도(현재 /brain 직접 생성).
- video 노드(4계층 완성) / 개인 PKM 출처(Phase 21 이월) 잔존.

## 5. 산출물
- backend: repositories/{domain,series}_repo(create) + me.py(POST + _owns_brand/_owns_domain) + schemas/graph.py(요청/응답)
- frontend: /brain 구조 섹션 + StructureCreateInput + api(createDomain/createSeries) + types
- contract: CC-030(api_contract §8.7 POST)
- tests +16(698→714): test_me_structure_create
- 라이브 데모 리포트 + 회고/closing

## 6. 다음
- 이월: domain/series 편집·삭제 / 위저드 연결 / video 노드 / 개인 PKM 출처 migration.
- 로드맵: 배포 Gate B~G. (4계층 = 생성+가시화+출처추적까지 — 2nd brain 이 편집 가능한 지식 구조로.)
