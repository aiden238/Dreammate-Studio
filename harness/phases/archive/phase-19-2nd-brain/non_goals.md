# Phase 19 — Non-Goals

```
✗ 신규 PKM 데이터모델/migration — 기존 pkm_entries/brand_memory/brands/series 읽기 + CRUD만.
✗ 협업/공유 그래프 — 본인 PKM 한정(RLS). global_wiki 익명(원문 0) 계승.
✗ 자동 그래프 편집(LLM이 노드 추가) — 사용자 큐레이션 + 기존 추출 governance(≥0.9) 유지.
✗ 모바일 force-graph — design.md 제약(트리 아닌 breadcrumb). 모바일은 카드/리스트.
✗ commercial_viral / 배포 게이트 — 별도(future).
✗ 영상 제작 — product_boundary 영구 계승.
```

## 회피할 함정
- 모바일에 그래프 강요 금지(원칙#10 한 손 조작) — 모바일=카드/리스트, 그래프=데스크톱.
- react-flow 번들 비대 → 데스크톱 lazy-load(모바일 미로드).
- 빈 그래프(데이터 빈약) → 온보딩 안내 + 브랜딩 세션(채우기) 유도.
- 큐레이션 삭제 실수 → user_locked 보호 + 확인.
- scope creep: 본 phase = PKM 가시화/큐레이션. 협업/공유/자동편집 X.
