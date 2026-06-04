# Phase 22 S2 — domains/series 생성 라이브 데모

> 2026-06-04 | mock 백엔드(Phase 22, 공유 store) + 프론트 재기동 | mock-user-1
> 스크립트: API(urllib) + 브라우저 DOM(preview) — P-LIVE-VERIFY-001

## 판정: ★ PASS (end-to-end)

### ① 백엔드 생성 API
| 호출 | 결과 |
|---|---|
| 로그인(mock) | 200, mock-user-1 |
| 시드 brand | "동네 카페" (before summary domains:0/series:0) |
| POST /me/domains ×2 | 200 — "카페 브이로그" / "신메뉴 소개" |
| POST /me/series ×2 | 200 — "아침 오픈 루틴" / "단골 인터뷰" (domain1 하위) |
| POST /me/series (미소유 domain) | **404** (RLS 소유검증) |

### ② /me/pkm-graph 4계층 반영 (Phase 21 집계 자동)
```
after summary: {personal:3, brand:2, brands:1, domains:2, series:2, sources:0}
domain nodes: [카페 브이로그, 신메뉴 소개]
series nodes: [아침 오픈 루틴, 단골 인터뷰]
edge kinds: {owns:1, has_personal:3, has_brand_pkm:2, has_domain:2, has_series:2}
```

### ③ 브라우저 /brain 렌더 (DOM)
"지식 구조 (4계층)" 섹션이 트리를 렌더:
```
동네 카페  [+ 도메인]
  카페 브이로그
    아침 오픈 루틴 / 단골 인터뷰   [+ 시리즈]
  신메뉴 소개                      [+ 시리즈]
```
생성 입력(도메인 1 + 시리즈 2 = 3 text inputs) + "+ 도메인"/"+ 시리즈" 버튼 렌더. ★ 기존 PKM 카드(개인 3 + 브랜드 2) + 큐레이션(🔒/✏️/🗑) 무변경.

## 결론
- ★ 4계층 데이터 생성(POST /me/domains·/me/series) → 그래프 자동 반영(Phase 21 집계, builder 무변경) → /brain 구조 섹션 렌더까지 **end-to-end 라이브 동작**.
- RLS 소유검증(미소유 domain 404) 실증. additive(기존 /brain 무변경).
- 비고: 데스크톱 react-flow 그래프의 domain/series 노드 시각은 ResizeObserver headless 한계(Phase 19/21 동일)로 육안 미확인 — 단 그래프 데이터(노드/엣지) + 구조 섹션 렌더는 확인.
