# Phase 25 — 위저드(브랜딩 세션) → 4계층 자동 연결 라이브 데모

> 2026-06-04 | mock 백엔드(Phase 25, branding_pkm_seed_enabled ON) | mock-user-1 | API

## 판정: ★ PASS

| 단계 | 결과 |
|---|---|
| plan start + 로그인 | before domains/series 0/0 |
| **POST /branding/select** `{topic:"동네 카페 모닝 브이로그", format:"30초 쇼츠"}` | 응답 `{ok, seeded, domain_id, series_id}` — domain_id/series_id non-null |
| /me/pkm-graph 반영 | domain **"동네 카페 모닝 브이로그"**(topic) + series **"30초 쇼츠"**(format) 자동 생성, summary 1/1 |
| ★ **멱등** — 같은 topic 재select | domains 여전히 **1**(중복 0) + 동일 domain_id |

## 결론
- ★ 브랜딩 세션 택1(`/branding/select`) → brand 하위 domain(topic)+series(format) **자동 시드** → /brain 4계층 자동 채움(수동 생성 불필요).
- 멱등(get_or_create): 같은 topic 반복 select 해도 domain 중복 0.
- gated(`branding_pkm_seed_enabled`)+authed+graceful. 응답 additive(domain_id/series_id).
- 비고: 전체 브라우저 브랜딩 세션(질문→후보→택1)은 동일 select 훅을 마지막에 태움 — UI 흐름은 /new/branding → select → /brain. 범용 Discovery/Quick step 위저드는 domain/series discrete 캡처 안 함(별건).
