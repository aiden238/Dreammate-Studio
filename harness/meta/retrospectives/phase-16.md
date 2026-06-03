# Phase 16 회고 — A/B 실험 (Baseline 래퍼 vs Agent-grade PKM/RAG)

> 2026-06-03~04 | 검증/실험 페이즈 (런타임 0 변경) | 판정 GO(메커니즘)

## 1. 무엇을 했나

moat 리서치("현재 MVP=복제 쉬운 래퍼, moat는 미구축 PKM/RAG=가설")를 **단일변수 통제 A/B 실험**으로 검증.
- S1: A/B 하네스(`use_rag`/주입 토글, 포크 아님) + 통제 입증 + real-mode 1차 → generic Δ flat(+0.013).
- S2: 강한 binding 주입 + fit/adherence 측정 → ★fit Δ+0.425 (GO 메커니즘).
- S3: 사람 blind 키트(deferred 사용자 채점).

## 2. 잘된 것

- **실험-우선이 빌드 오판을 막았다**: generic critic 하나만 봤으면 "PKM 무용"으로 잘못 결론 낼 뻔했는데(Δ flat), 6개 빌드 페이즈 전에 측정 설계 결함(generic≠fit, rag_context 약한 주입)을 잡았다.
- **결과가 다음 단계를 바꿨다**: S1 flat → S2 측정·주입 보강(사용자 체크포인트) → GO. 측정 도구가 진화.
- **production 0 변경 통제실험**: 기존 rag_context 주입 경로 재사용 + eval additive. pytest 537→556, behavior-preserving.

## 3. 핵심 학습 → 패턴 후보

- **P-EXPERIMENT-BEFORE-BUILD-001(신규 후보)**: moat/차별성 가설은 빌드 전에 단일변수 통제 A/B로 싸게 측정. "measure don't build" 검증 페이즈가 빌드 방향과 깊이를 가지치기.
- **P-MEASURE-THE-RIGHT-THING-001(신규 후보)**: generic 품질 지표는 차별성을 못 본다(commodity). 차별성은 fit/adherence 같은 **목적-정합 지표**로 따로 측정해야 신호가 잡힌다 (Δgeneric +0.008 vs Δfit +0.425).
- **주입 방식 교훈**: 같은 PKM 도 "참고자료(복제금지)"로 넣으면 효과 0, "구속 지시"로 넣으면 큰 효과 → Phase 17 설계 직접 반영.
- **P-LIVE-VERIFY-001 계승**: mock 통제 입증(자동)과 real-mode 실측(신호)을 분리 — 자동 green ≠ 실효과.

## 4. 정직한 한계 (over-claim 방지)

- judge 약한 순환성: Δfit 은 "주입이 출력을 바꾼다"를 증명(비자명 — S1 rag_context는 못 바꿈)하지 "fit=좋은 영상"은 아님.
- fit≠value → S3 사람 blind(deferred). 시뮬 PKM → compounding/시장 moat 미증명(Phase 17 실데이터 후).

## 5. 이월 / 다음

- A3(사람 blind) deferred — 사용자 채점 후 fit→value 봉인.
- A4(종적 H2) 이월 — 실 누적 데이터 전제 → Phase 17(가/다) 후 측정.
- **Phase 17 = 계정별 PKM 실빌드**: 가(auth 신원→생성 + brand_memory 구속 주입) / 다(개인 PKM·메모리). PKM 은 구속 지시로 주입(S2 교훈).

## 6. 메트릭

- pytest 537→556(+19: S1 9 + S2 10, 기존 0 수정) / scenario_sim 36/36 / 키 0 / 운영 코드 0 변경.
- 실측: Δgeneric +0.008(flat) / Δfit +0.425(GO). real-mode(gpt-4o-mini planning + gpt-4o critic/judge).
