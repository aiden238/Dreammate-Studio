# Phase 22 — domains/series 생성 기능 (4계층 데이터 풍부화)

## 목표
4계층(User→Brand→**Domain→Series**)을 사용자가 **직접 생성**할 수 있게 → Phase 21 `/brain` 그래프가 실데이터로 채워짐.
- 현재: domains/series 테이블·read repo(Phase 21)만 존재, **생성 경로 0** → 그래프 항상 빈 4계층.
- 본 phase: DomainRepo/SeriesRepo **create** + POST `/me/domains`·`/me/series`(소유검증) + `/brain` 추가 UI + ★ **라이브 데모**(생성→그래프 4계층 표시).

## 근거
- Phase 21 이월("domains·series 생성 기능 — 실데이터 풍부화"). 데이터 모델(0001) + read repo(Phase 21) 충족.
- /brain = 2nd brain → 사용자가 지식 구조를 직접 구축(생성+큐레이션)하는 곳으로 확장.

## 핵심 원칙
- additive — 기존 /brain(읽기/큐레이션) + 그래프 무변경, 생성 endpoint·UI 만 추가.
- RLS/소유검증 — domain 은 본인 brand 하위에만, series 는 본인 domain 하위에만 생성(_owns 패턴 계승).
- graceful — 생성 실패 시 500 금지(brand/domain repo 패턴).

## 산출 (슬라이스)
S1(backend: repos create + POST endpoints + 소유검증 + tests + CC) → S2(frontend /brain 추가 UI + api + ★라이브 데모 + close).
