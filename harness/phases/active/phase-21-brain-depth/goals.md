# Phase 21 — /brain 4계층 깊이 + 출처 엣지 (2nd brain 확장)

## 목표
Phase 19 `/brain` PKM 그래프를 확장:
1. **4계층 깊이**: domain·series 노드 추가 (User→Brand→**Domain→Series**→Video 4계층 모델 가시화). DomainRepo/SeriesRepo 신규.
2. **출처 엣지**: 브랜드 PKM(brand_memory.source_plan_id)의 출처(기획안) 노드 + `sourced_from` 엣지 — "이 PKM이 어디서 왔는가" 추적.

전부 **additive / graceful**(데이터 없으면 빈 — 기존 그래프 byte-identical) — Phase 19 패턴 계승.

## 근거
- Phase 19 이월 항목("4계층 깊이(domains·series)+출처 엣지(feedback→PKM)").
- 데이터 모델 충족: domains/series 테이블(0001) + brand_memory.source_plan_id(0005) 존재.

## 핵심 제약 (정직)
- domains/series 는 현재 실데이터 희소(생성 경로 미비) → graceful empty(노드 0 = 기존 그래프 불변). 구조는 완성, 풍부함은 실사용.
- **개인 pkm_entries 는 source_plan_id 없음** → 개인 PKM 출처 엣지 **불가**(이월 — migration 필요). 본 phase 출처 엣지는 **브랜드 PKM 한정**.

## 산출 (슬라이스)
S1(backend: DomainRepo/SeriesRepo + me.py 4계층+출처 집계 + graph.py 스키마 + tests) → S2(frontend 렌더 + CC + 라이브 + close).
