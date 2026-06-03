# Phase 18 — 브랜딩 세션 (Akinator 주제발굴) — Goals

> 유형: 제품 phase (런타임 有) — gated/additive(신규 진입, 기존 Quick/Discovery 무변경).
> 근거: `meta/proposals/2026-06-04_branding-session-akinator-design.md` (사용자 결정 반영).
> 선행: Phase 17(계정별 PKM) ✅ done — brand_memory/PKM 재사용.

## 한 줄 목표

주제를 모르는 사용자를 **LLM 동적 스무고개**(카드+자유입력)로 좁혀 **후보 주제 3개 × 각 브랜딩 방향(톤/타깃/포맷/왜)** 을 제안하고, 택1 → 기존 planning + brand_memory(PKM) 시드로 연결한다.

## 사용자 결정 (2026-06-04)
- 질문 엔진 = **LLM 동적**(답변 적응형, 모든 주제) / 종료 = 충분 신호 or N고개 상한.
- 답변 = **카드 2~4개 + 자유입력 혼합**.
- 결과 = **후보 주제 3개 × 브랜딩 방향 + PKM 연결**(택1 → planning + brand_memory 시드).

## ★ 루프 결합
발굴(Phase 18 스무고개) → 축적(brand_memory) → 주입(Phase 17 PKM) → "쓸수록 맞춰지는" 완성.

## 산출물
1. `topic_discovery` agent(LLM, ask/finalize 2모드) + prompt_registry 등록.
2. branding endpoint(next/finalize) + 세션 상태 누적.
3. frontend `/new/branding` (질문 카드+자유입력+진행바 → 후보 3 → 택1).
4. planning 연결 + brand_memory 시드(gated, Phase 17 재사용).
5. 라이브 e2e + phase-complete.
