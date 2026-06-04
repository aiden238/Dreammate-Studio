# Phase 25 — Acceptance

```
A1. S1 repos — DomainRepo.get_or_create(brand_id,name) + SeriesRepo.get_or_create(domain_id,name) — 멱등(있으면 재사용). [단위]
A2. S1 훅 — branding/select 에서 (gated branding_pkm_seed_enabled + authed) topic→domain, format→series 자동 생성(brand get_or_create_default 하위). graceful. [단위]
A3. S1 멱등/gated — 같은 topic 2회 select → domain 중복 0. flag OFF/익명 → 생성 0 + 응답 byte-identical. [단위]
A4. S1 응답 additive — BrandingSelectResponse 에 domain_id/series_id(Optional, 미생성 시 null). 기존 키 불변. [단위]
A5. behavior-preserving — 기존 pytest 735 green + scenario_sim 36/36 + audit 0.
A6. ★ 라이브 데모 — 브랜딩 세션(/new/branding) 완주(택1) → /brain 에 domain(topic)/series 자동 표시.
A7. contract-change — api_contract §8.6 branding/select 응답(domain_id/series_id) docs-sync(CC).
A8. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A4 | 단위 test(자동 생성 + 멱등 + gated/익명 skip + 응답 additive) |
| A5 | pytest 735 baseline + scenario_sim 36 + audit 0 |
| A6 | 라이브 브랜딩 세션 → /brain 4계층 |
