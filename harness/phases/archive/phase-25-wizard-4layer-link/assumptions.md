# Phase 25 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- 브랜딩 select(`plans_branding_select`, plans.py ~950)에서 auth_user_id + branding.selected(topic/tone/target/format) 보유 + `_seed_branding_pkm`이 BrandRepo.get_or_create_default 로 brand 해결.
- DomainRepo/SeriesRepo.create(Phase 22) + list_for_brand/list_for_domain(Phase 21) → get_or_create(멱등) 구성.
- 게이트 `branding_pkm_seed_enabled`(기존 branding 시드 flag) 재사용 — 같은 "branding select 부수효과" 개념.
- **audit_naming 통과 (2026-06-04, 0 drift)**.
### 1.2 불확실
- U1 series 매핑 — branding 은 topic 1개. series name = format(있으면) 또는 "기본 시리즈". (presumption 최소화: domain 우선, series 는 format 기반.)
- U2 멱등 키 = (brand_id, domain name) / (domain_id, series name) — 동일 이름 재사용.

## 2. Simplest Slice (3회 압축)
```
1차: backend 훅 + 응답 + 라이브.
2차: branding/select 자동 시드 훅 + repos get_or_create + 응답 additive + tests.
3차: DomainRepo.get_or_create + branding/select 에서 topic→domain 1개 생성(멱등, gated) — 단위 test.
     (series 동반.) ← S1 = backend 훅.
```
→ S1(backend 훅+repos get_or_create+응답+tests+CC) → S2(라이브 데모 + close).

## 3. Surgical Scope
- editable: db/repositories/{domain,series}_repo(get_or_create) + routers/plans.py(_auto_create_domain_series + select 호출) + schemas/plans.py(응답 additive) + tests + phase/state/meta.
- read-only(→contract-change): api_contract.md §8.6.
- forbidden: 위저드 step 재설계 / video / 개인 PKM 출처 migration / migration / archive.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: branding/select(authed, flag ON) → domain(topic)/series 생성 + 멱등(2회=중복0) + gated OFF/익명 skip(응답 byte-identical) + graceful 단위 test.
- 각 슬라이스: behavior-preserving(기존 pytest 735) + scenario_sim 36 + audit 0.
- S2: ★ 라이브 브랜딩 세션 → /brain 4계층 자동 표시.
