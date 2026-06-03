# Phase 16 — A/B 실험 (Baseline 래퍼 vs Agent-grade PKM/RAG) — Goals

> 유형: **검증/실험 페이즈** (Phase 12 "검증 페이즈" 성격 — 측정하고 빌드하지 않음).
> 근거 기획안: `meta/proposals/2026-06-03_ab-experiment-agent-vs-baseline.md` (rough v0).
> 선행조건(PKM/RAG 제안서 §0.2): A(rich 실사용 검증=Phase 13 ✅) + B(위저드 실연결=Phase 14 ✅) 모두 충족.

## 한 줄 목표

현재 MVP(=복제 쉬운 멀티모델 래퍼)와 사용자 계획(=PKM/RAG agent-grade)을 **단일 변수(데이터/검색 레이어 주입) 통제 실험**으로 비교하여, moat 가설을 **측정된 숫자 + go/no-go/partial**로 만든다.

## 검증 명제

```
H1 (메커니즘): 동일 모델·프롬프트·output_mode에서 PKM/RAG 컨텍스트 주입이 기획안 품질을
              유의하게 올리는가? → 정적 A/B (real-mode critic 8~10차원 + depth + 사람 blind).
H2 (compounding): 누적 PKM 항목(N=0/5/20)이 많을수록 B 품질이 단조 증가하는가? → 종적 기울기.
```

## 산출물 (이 페이즈가 내놓을 것)

1. A/B 실험 하네스 — 1 코드베이스 + 플래그(`use_rag`/brand_memory/PKM 시뮬 주입). **포크 아님**.
2. 시뮬 PKM 페르소나 fixture 2종 (채점 케이스와 분리 — 과적합 방지).
3. 정적 A/B 리포트 (H1) — real-mode 의미채점 + depth + 사람 blind.
4. 종적 리포트 (H2) — N=0/5/20 기울기.
5. **go/no-go/partial 판정 리포트** → PARKED 로드맵(PKM/RAG §9 / commercial_viral) 재우선순위 제안.

## 비전 정합 (왜 이 페이즈인가)

리서치 결론: 현재 MVP는 commodity 래퍼, moat는 미구축 PKM/RAG(가설). 이 페이즈는 6개 빌드 페이즈를
가설 위에 올리기 전에, "agent-grade가 실제로 품질을 올리는지"를 **싸게 측정**하는 GATE다.
GO면 PKM/RAG provisional(P17~)을 실 Phase로 재배정, NO-GO면 차별화 레버를 전환.
