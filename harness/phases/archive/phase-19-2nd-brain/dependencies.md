# Phase 19 — Dependencies

## 선행 (충족)
| 의존 | 상태 | 제공 |
|---|---|---|
| Phase 17 (계정별 PKM) | ✅ done | pkm_entries + brand_memory_entries + BrandRepo/PkmRepo/BrandMemoryRepo + RLS — 도식화 데이터 source |
| Phase 18 (브랜딩 세션) | ✅ done | brand_memory 시드 source(데이터 풍부화) |
| Phase 5 (Auth/RLS) | ✅ done | auth_user_id(request.state.user) + RLS 격리 + AuthGuard |
| Phase 2/3 (PWA) | ✅ done | AppShell(모바일 탭바/데스크톱 사이드바) + 카드 컴포넌트 + design.md |

## 재사용 자산
```
PkmRepo.list_for_user / BrandMemoryRepo.list_for_brand / BrandRepo (Phase 17) — 집계 source
brands/domains/series (0001) — 4계층 노드
_auth_user_id(request) + RLS(service key) — 격리
AppShell / 카드 컴포넌트 / design.md 토큰 — 프론트
react-flow (신규 의존, 데스크톱 lazy-load)
```

## 불확실 / 외부
- U1: react-flow 번들/모바일 영향 — lazy-load(ssr:false)로 모바일 미로드, design-review 점검.
- U2: 데이터 빈약(현재 PKM 적음) → 빈/희소 그래프 UX(온보딩 안내).
- U3: 모바일 카드 ↔ 데스크톱 그래프 반응형 분기점(브레이크포인트) — S2/S3에서 확정.
