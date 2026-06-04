# Phase 25 — Scope

## 포함 (build)
- **S1 backend**:
  - `DomainRepo.get_or_create(brand_id, name)` + `SeriesRepo.get_or_create(domain_id, name)` — list 로 중복 확인 후 없으면 create(멱등). graceful.
  - `routers/plans.py` `_auto_create_domain_series(plan_id, auth_user_id, req)` 훅 — `_seed_branding_pkm` 패턴 복제:
    - 게이트: `branding_pkm_seed_enabled` + auth_user_id (없으면 skip).
    - brand 해결(BrandRepo.get_or_create_default, 기존과 동일) → DomainRepo.get_or_create(brand_id, topic) → SeriesRepo.get_or_create(domain_id, format 또는 "기본 시리즈").
    - graceful: 실패 시 로깅만, 응답 차단 0.
  - `plans_branding_select` 하단에서 호출 → 응답(BrandingSelectResponse)에 `domain_id`/`series_id` **additive**(없으면 null).
  - 단위 test: 자동 생성(topic→domain, format→series) + 멱등(2회 호출=중복 0) + gated OFF skip + 익명 skip + graceful.
- **S2**:
  - ★ 라이브 데모: 브랜딩 세션(/new/branding) → 질문→후보→택1 → /brain 에 domain(topic)/series 자동 표시.
  - CC(api_contract §8.6 branding/select 응답 additive) + phase-complete.

## 예상 파일 변경
```
editable:
  backend/fastapi/db/repositories/{domain_repo,series_repo}.py (get_or_create 추가)
  backend/fastapi/routers/plans.py (_auto_create_domain_series 훅 + select 호출 + 응답)
  backend/fastapi/schemas/plans.py (BrandingSelectResponse +domain_id/series_id, additive Optional)
  tests/ + phase/state/meta
read-only(→contract-change): docs/contracts/api_contract.md §8.6
forbidden: 범용 위저드 step 재설계 / video 노드 / 개인 PKM 출처 migration / 신규 데이터모델 / archive
```

## 검증
- behavior-preserving: flag OFF/익명 → domain/series 생성 0 + 응답 기존 키 불변. 기존 pytest 735 green + scenario_sim 36 + audit 0.
- S1: 자동 생성 + 멱등(2회=중복 0) + gated + graceful 단위 test.
- S2: ★ 라이브 — 브랜딩 세션 후 /brain 4계층 자동 표시.
