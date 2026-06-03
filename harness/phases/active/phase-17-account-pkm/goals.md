# Phase 17 — 계정별 PKM 실빌드 (가 + 다) — Goals

> 유형: **제품 phase (런타임 有)** — gated/behavior-preserving. Phase 16 GO(메커니즘) 기반 실빌드.
> 근거: Phase 16 실측(Δfit +0.425) + `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md` §9 1차.

## 한 줄 목표

현재 "익명 생성"(generate user_id=NULL, orchestrator 신원 0)을 해소하고, **계정별 PKM(개인/브랜드)을
생성에 구속 주입**하여 사용자별로 적합도(fit) 높은 기획안을 만든다. ★ Phase 16 교훈: PKM 은
`rag_context`(참고) 아니라 **구속 지시**로 주입한다.

## 범위 (가 + 다)

```
가 (실연결) — 익명 생성 해소
  - auth 신원(auth_user_id / brand_id)을 생성 흐름(라우터→orchestrator→planning)에 연결.
  - brand_memory_entries 로드 → build_constraint_preamble(Phase 16 검증분) 구속 주입.
  - ★ gated/behavior-preserving: 신원 없음(익명) 또는 brand_memory 없음 → 기존 경로 byte-identical.

다 (개인별 메모리)
  - personal_pkm(pkm_entries) 테이블 + repo — 개인 단위 선호/패턴 적재·조회.
  - 개인 + 브랜드 (+ 시리즈) 통합 주입 + 실 e2e 검증.
```

## 산출물

1. 신원→생성 배선 (gated) + brand_memory 구속 주입 (production).
2. pkm_entries migration + PkmRepo + 개인 메모리 적재/조회.
3. 통합 주입 + 실 e2e 테스트 + (가능 시) Phase 16 하네스로 실데이터 fit 재측정.

## 비전 정합

Phase 16 이 "fit 이 차별성"임을 입증 → Phase 17 은 그 fit 을 **실제 계정 데이터로** 만들어내는
첫 production 빌드. agent-grade(메모리 누적 + 구속 주입)로 가는 1차 단계.
