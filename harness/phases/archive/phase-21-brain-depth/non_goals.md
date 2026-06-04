# Phase 21 — Non-Goals

```
- ★ 개인 pkm_entries 출처 엣지 금지 — source_plan_id 컬럼 부재(0006). migration 필요 = 이월(본 phase 는 브랜드 PKM 출처만).
- domains/series 생성 UI/플로우 미포함 — 본 phase 는 그래프 가시화(읽기 집계)만. 4계층 데이터 생성은 별도.
- video_projects 노드 미포함 — 4계층 중 Domain·Series 까지만(Video 는 후속). (deferred legacy 경로 ADR-023.)
- 신규 데이터모델/migration 0 — 기존 테이블(domains/series/brand_memory) 재사용.
- 그래프 외 변경 금지 — /brain 그래프 집계·렌더만. 다른 라우트/엔드포인트 무변경.
- 성능/대규모 그래프 최적화 미포함(데이터 희소 — 현 규모 충분).
```
