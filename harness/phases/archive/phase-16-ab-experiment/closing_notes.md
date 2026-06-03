# Phase 16 — Closing Notes (A/B 실험)

> 종료: 2026-06-04 | 유형: 검증/실험 페이즈 (측정 — 런타임 0 변경) | 판정: **GO(메커니즘)**

## Acceptance 판정

| # | 기준 | 상태 | 근거 |
|---|---|---|---|
| A1 | 통제 입증 | ✅ | 두 arm 시스템 프롬프트가 주입 컨텍스트만 차이 (mock test, S1·S2) |
| A2 | 정적 H1 | ✅ | real-mode 실측 — generic Δ+0.008(flat) / ★fit Δ+0.425 (S2 리포트) |
| A3 | 사람 blind | 🟡 **deferred(사용자 채점 대기)** | S3 블라인드 키트 생성·전달(`eval/human_review/2026-06-04_phase-16-s3-blind.md`). 채점은 사용자 비동기 — Phase 12 S4 deferred 패턴 계승 |
| A4 | 종적 H2 (compounding) | ⏸ **드롭/이월** | S2 fit GO 로 빌드 결정 → 종적은 실 누적 데이터 전제(시뮬 proxy 한계, §5.1). 실데이터 누적은 Phase 17(가/다) 후 측정이 타당 → Phase 17+ 이월 |
| A5 | 종합 판정 | ✅ | GO(메커니즘) — S1/S2 리포트 + 본 closing |
| A6 | behavior-preserving | ✅ | 운영 코드 0 변경(eval/ additive). pytest 537→556(기존 0 수정), scenario_sim 36/36, 키 0 |
| A7 | phase-complete | ✅ | 본 종료 |

## 핵심 결론 (GO 판정)

```
1. generic 품질 = commodity (래퍼≈agent-grade, Δ flat +0.008, S1·S2 2회).
2. 개인화 fit = agent-grade 압도 (Δfit +0.425, 일관) — 구속 PKM 주입이 plan 을 실제로
   브랜드 톤/잠금선호/시리즈포맷에 맞춘다.
3. 주입 방식 결정적: rag_context("복제금지 참고")=효과 0 / binding 지시=큰 효과.
   ⇒ Phase 17(가/다)는 PKM 을 구속 지시 슬롯으로 주입한다 (rag_context 아님).
```

## 정직한 한계 (이월)

- judge 약한 순환성(주입 반영 여부 측정=부분 자명) → S3 사람 blind 로 fit→value 확인(deferred).
- fit ≠ value 미증명 → S3 채점 결과로 봉인.
- 시뮬 PKM(실 누적 아님) → compounding(H2)·시장 moat 미증명 → Phase 17 실데이터 후 측정(A4 이월).

## 산출물

- 하네스: `backend/fastapi/eval/ab_experiment.py`(S1+S2) + `ab_personas.py` + test(`test_ab_experiment.py` 9 + `test_ab_fit.py` 10)
- 리포트: `eval/regression_results/2026-06-04_phase-16-s1-ab.md` + `..._s2-fit.md`
- blind 키트: `eval/human_review/2026-06-04_phase-16-s3-blind.md`
- 기획안: `meta/proposals/2026-06-03_ab-experiment-agent-vs-baseline.md`
- 커밋: 9270896(entry)/f22a53d·bdff167(S1)/abbc219·a0487ec(S2)/af24d1b(S3 kit)

## 다음 Phase

**Phase 17 = 계정별 PKM 실빌드 (가/다)** — GO 근거(Δfit +0.425) + S3(채점 후 봉인). 가=auth 신원→생성 연결 + brand_memory 구속 주입(gated) / 다=개인 PKM·메모리 기능.
