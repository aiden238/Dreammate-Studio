# Phase 25 — 위저드(브랜딩 세션) ↔ 4계층 자동 연결

## 목표
브랜딩 세션(주제발굴) **택1 시점**(`/plans/{id}/branding/select`)에서 선택된 topic→**domain**, format→**series**를 brand 하위에 **자동 생성** → 위저드를 거치면 /brain 4계층이 **자동으로** 채워짐(수동 생성 불필요).
- 현재: brand 만 자동 생성(Phase 17 get_or_create), domain/series 는 /brain 수동 생성만(Phase 22).
- 본 phase: branding/select 에 domain/series 자동 시드 훅(멱등·gated·graceful) + 응답 additive(domain_id/series_id) + 라이브 데모.

## 근거 (조사)
- ★ 범용 Discovery/Quick **위저드는 domain/series 를 discrete 선택값으로 캡처 안 함**(현 설계) → 위저드 step 재설계는 별건(범위 밖).
- 브랜딩 세션 택1 = **큐레이션된 topic/target/format** + auth_user_id + brand 이미 해결(_seed_branding_pkm) → 자연스러운 topic→domain 다리.
- brand 자동 생성(get_or_create_default) 패턴 + Phase 22 DomainRepo/SeriesRepo.create 재사용.

## 핵심 원칙
- **멱등(idempotent)**: 같은 topic domain 이 이미 있으면 재사용(중복 0) — get_or_create.
- **gated/graceful**: 기존 brand_memory 시드와 같은 flag(`branding_pkm_seed_enabled`) 하에. 익명/flag OFF → 생성 0(응답 byte-identical).
- additive: branding/select 응답에 domain_id/series_id 추가(기존 키 불변).

## 산출 (슬라이스)
S1(backend: repos get_or_create + branding/select 자동 시드 훅 + 응답 additive + tests + CC) → S2(라이브 데모: 브랜딩 세션→/brain 4계층 자동 표시 + close).

## 범위 밖
범용 Discovery/Quick 위저드 step 의 domain/series 캡처(위저드 재설계) / video 노드 / 개인 PKM 출처 migration.
