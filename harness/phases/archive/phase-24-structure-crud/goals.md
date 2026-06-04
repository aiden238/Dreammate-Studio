# Phase 24 — domain/series 편집·삭제 (/brain 4계층 구조 CRUD 완성)

## 목표
Phase 22(domain/series **생성**) + Phase 19(PKM **큐레이션**)에 이어 domain/series **편집·삭제**를 추가 → `/brain` 4계층 구조의 **CRUD 완성**.
- 현재: domain/series 생성만 가능(Phase 22), 잘못 만들면 못 고침/못 지움.
- 본 phase: PATCH(name)/DELETE `/me/domains/{id}`·`/me/series/{id}`(소유검증) + /brain 구조 섹션 편집/삭제 UI + 라이브 데모.

## 근거
- 기능 마감 그룹(🅑) — /brain CRUD 일관성(PKM은 Phase 19에서 편집/삭제 됨, domain/series는 생성만).
- 패턴 재사용: Phase 19 S4 PKM 큐레이션(PATCH/DELETE) + Phase 22 create(소유검증) 동형.

## 핵심 원칙
- additive — 생성/조회/그래프 무변경, 편집·삭제 endpoint·UI만 추가.
- RLS/소유검증 — domain은 본인 brand 하위, series는 본인 domain 하위만 수정/삭제(_owns 패턴).
- 삭제 cascade 주의 — domain 삭제 시 하위 series 처리(DB FK on delete 또는 graceful). graceful.

## 산출 (슬라이스)
S1(backend: repos update/delete + PATCH/DELETE endpoints + 소유검증 + tests + CC) → S2(frontend /brain 편집/삭제 UI + ★라이브 데모 + close).

## 범위 밖 (다음 phase — 🅑 나머지)
위저드↔4계층 자동 연결 / video 노드 / 개인 PKM 출처 migration.
