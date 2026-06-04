# Phase 25 — Acceptance

```
[x] A1. S1 repos — DomainRepo/SeriesRepo get_or_create 멱등(있으면 재사용). [단위]
[x] A2. S1 훅 — branding/select (gated branding_pkm_seed_enabled + authed) topic→domain, format→series 자동(brand 하위). graceful. [단위]
[x] A3. S1 멱등/gated — 같은 topic 2회→domain 1 / flag OFF·익명→생성 0 byte-identical. [단위]
[x] A4. S1 응답 additive — BrandingSelectResponse +domain_id/series_id(Optional null). 기존 키 불변. [단위]
[x] A5. behavior-preserving — hermetic pytest 735→749 + scenario_sim 36/36 + audit 0.
[x] A6. ★ 라이브 데모 — select{topic,format}→domain/series 자동 생성 + 멱등(2회=1) (eval/.../phase-25-4layer-link-live.md).
[x] A7. contract-change — api_contract §8.6 응답(domain_id/series_id) — CC-032.
[x] A8. phase-complete — gates + 회고 + archive + REGISTRY/STATE + main 머지.
```
> 판정: 8/8 충족 + 라이브 데모 PASS. (전체 브라우저 브랜딩 세션은 동일 select 훅 — UI: /new/branding→select→/brain.) 범용 step 위저드 연결은 별건(이월). closing_notes.md.

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1~A4 | 단위 test(자동 생성 + 멱등 + gated/익명 skip + 응답 additive) |
| A5 | pytest 735 baseline + scenario_sim 36 + audit 0 |
| A6 | 라이브 브랜딩 세션 → /brain 4계층 |
