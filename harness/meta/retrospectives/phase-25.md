# Phase 25 회고 — 위저드(브랜딩 세션) ↔ 4계층 자동 연결

> 2026-06-04 | 제품 phase | additive/gated | ★ 라이브 데모 PASS | 기능마감(🅑) 2차

## 1. 무엇을 했나
브랜딩 세션 택1(`/plans/{id}/branding/select`)에서 topic→domain, format→series 를 brand 하위에 자동 시드 → 위저드 거치면 /brain 4계층 자동 채움.
- **S1 backend**: DomainRepo/SeriesRepo get_or_create(멱등) + plans.py `_auto_create_domain_series` 훅(gated `branding_pkm_seed_enabled` + authed + brand get_or_create_default + graceful) + branding/select 호출 + 응답 additive(domain_id/series_id). CC-032.
- **S2**: 라이브 데모(select → domain/series 자동 + 멱등) + close.

## 2. 핵심 성과 / 검증
- ★ **라이브 데모 PASS**(eval/.../phase-25-4layer-link-live.md): select{topic,format} → domain "동네 카페 모닝 브이로그" + series "30초 쇼츠" 자동, summary 1/1. **멱등**: 같은 topic 재select → domain 1(중복 0).
- behavior-preserving: 익명/flag OFF → 생성 0 + 응답 byte-identical(기존 ok/seeded 불변). hermetic pytest 735→**749**(+14) + scenario_sim 36/36 + audit 0.
- brand 자동 생성(Phase 17) + DomainRepo/SeriesRepo(Phase 22) 재사용 — 신규 자산 최소.

## 3. 학습 / 패턴
- ★ **조사가 범위를 정직하게 잡았다**: "위저드↔4계층 연결" 요청을 사전 조사 → 범용 Discovery/Quick step 위저드는 domain/series 를 discrete 선택값으로 캡처 안 함(현 설계) 발견 → **브랜딩 세션의 큐레이션 topic** 이 자연스러운 연결점으로 재정의. 헛 구현(위저드 step 재설계) 회피.
- **부수효과 훅의 정형**: branding/select 가 이미 brand_memory 를 시드(Phase 18) → 같은 자리·같은 gate 에 domain/series 시드 추가(_seed_branding_pkm 패턴 복제). gate 재사용으로 launcher/flag 변경 0.
- **멱등 get_or_create**: list→match→create. 반복 select 의 중복 방지. 시드형 자동 생성의 필수.

## 4. 정직한 한계 / 이월
- **범용 step 위저드 미연결**: Discovery 7-step / Quick 은 domain/series discrete 캡처 안 함 → 본 phase 미포함(위저드 재설계는 별건). 브랜딩 세션 경로만 자동 연결.
- series 매핑 단순(format→series name) — 더 정교한 series 개념(연재 회차 등)은 후속.
- 🅑 나머지: video 노드 / 개인 PKM 출처 migration.
- 데스크톱 그래프 노드 시각(headless 한계).

## 5. 산출물
- backend: repositories/{domain,series}_repo(get_or_create) + plans.py(_auto_create_domain_series + select 호출) + schemas/plans.py(응답 additive)
- contract: CC-032(api_contract §8.6)
- tests +14(735→749): test_branding_4layer_link(자동 생성/멱등/gated/익명/graceful)
- 라이브 데모 리포트 + 회고/closing

## 6. 다음
- 🅑 나머지: video 노드(4계층 마지막) / 개인 PKM 출처 migration.
- 또는 품질 후속(🅒) / 배포(보류). ★ 브랜딩→4계층 자동 연결로 "발굴→구조화" 흐름 매끄러워짐.
