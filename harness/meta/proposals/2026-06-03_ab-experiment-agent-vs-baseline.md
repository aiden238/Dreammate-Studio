# Proposal: A/B 실험 — Baseline(멀티모델 래퍼) vs Agent-grade(PKM/RAG) — 실험 기획안 (rough v0)

> 날짜: 2026-06-03
> 유형: **실험 설계 제안 (proposal-only)** — ★ 코드/contract/migration/endpoint/schema **0 변경**. 전부 "제안".
> 작성 근거: moat 리서치(LLM 래퍼 commoditization + 버티컬 AI 모트 4요소) + 실측 아키텍처(config `use_rag`/`effective_output_mode`, eval/runner.py, critic 8~10차원, brand_memory_*, feedback_to_candidate, PKM/RAG 설계서 `2026-06-03_pkm-rag-orchestrator-design.md`)
> 상호참조: `2026-06-03_pkm-rag-orchestrator-design.md`(treatment arm 설계) + `2026-06-03_commercial-viral-mode-design.md`(품질 상한 모드)
> 절차: 실 착수 시 phase-start + eval-run + multi-llm-validation + (스키마 닿으면) contract-change 경유

---

## 0. 상태 / 목적 / 한 줄

- **상태**: rough v0 제안. 이 문서는 "실험 설계"이며, 이걸 게이트로 PARKED 로드맵(P16~21)을 재우선순위한다.
- **한 줄**: 현재 MVP(=복제 쉬운 멀티모델 래퍼)와 사용자 계획(=PKM/RAG agent-grade)을 **단일 변수(데이터/검색 레이어 주입) 통제 실험**으로 비교하여, "moat가 실재하는가 / 어느 scope가 효과 있는가"를 **측정된 숫자 + go/no-go**로 만든다.
- **핵심 원칙**: 포크 2개 아님 → **1 코드베이스 + 플래그**(통제실험). 싸고 결정-지향(완벽 빌드 아님).

---

## 1. 배경 & 가설 (moat 가설 → 검증가능 명제)

리서치 결론: 현재 MVP의 생성코어(prompt→3plan→critic→RAG-lite)는 commodity. moat는 **미구축 PKM/RAG(쌓이는 데이터)+브랜딩(전문화)** 에 있다 — 단 **가설**.

이 가설을 두 개의 검증가능 명제로 분해:

```
H1 (메커니즘): 개인/brand/series 컨텍스트(PKM)와 검색(RAG)을 주입하면,
              동일 모델·동일 프롬프트·동일 output_mode에서도 기획안 품질이 유의하게 오른다.
              → 정적 A/B로 측정 (지금 데이터 없이도 시뮬 컨텍스트로 가능).

H2 (compounding): 누적된 PKM 항목이 많아질수록 B의 품질이 단조 증가한다 ("쓸수록 좋아진다").
              → 종적(누적량 N=0/5/20) 측정 (시뮬 페르소나로 proxy, 실사용은 상한).
```

H1 = "agent-grade가 래퍼보다 지금 더 좋은가". H2 = "그 우위가 데이터와 함께 커지는가(= 진짜 moat 엔진)".

---

## 2. 두 arm 정의 (★ 단일 변수 — 나머지 전부 고정)

> 변수: **데이터/검색 레이어(RAG + brand_memory + PKM 컨텍스트팩) 주입 여부**. 그 외(모델·프롬프트·output_mode·critic·temperature·3안 다양성)는 **A=B 동일 고정**.

| 요소 | Arm A — Baseline (래퍼/대조군) | Arm B — Agent-grade (처치군 = 내 계획) | 고정/변수 |
|---|---|---|---|
| 입력→3plan→critic 코어 | 동일 | 동일 | 고정 |
| 모델 | 동일(예: gpt-4o-mini ×3) | 동일 | 고정 |
| `output_mode` | 동일(예: director로 고정 — 공정비교) | 동일 | 고정 |
| P-006 프롬프트 | 동일 | 동일 (단 context pack 주입 슬롯만 채워짐) | 고정 |
| `use_rag` | **False** | **True** | ★ 변수 |
| brand_memory 주입 | OFF | **ON** | ★ 변수 |
| PKM context pack (personal/brand/series scope) | 없음 | **주입(시뮬)** | ★ 변수 |

→ A는 현재 운영 경로 그대로(`use_rag=False`). B는 `use_rag=True` + brand_memory + PKM 컨텍스트팩(시뮬). **차이는 오직 "주입된 맥락"** 이므로 품질 차이는 데이터레이어에 귀속된다.

★ 구현 노트: B의 PKM context pack은 PKM/RAG 제안서 §7 형식(locked_preferences/personal_patterns/brand_guide/series_format)을 **시뮬 페르소나로 채운 고정 fixture**로 시작(실 orchestrator 미구축 — 실험은 "주입의 효과"만 본다). 효과 확인되면 그때 orchestrator를 실제로 짓는다.

---

## 3. 측정 설계 (2층)

### 3.1 정적 품질 (H1) — eval + 사람 blind

| 도구 | 출처 | 무엇을 |
|---|---|---|
| `run_golden_set_eval` | eval/runner.py | schema 100% + structural(plan/hook/flow/광고/차단) — 회귀 게이트 |
| Critic 8~10차원 | critic.py (director=10, depth_actionability 포함) | 의미 품질 점수 (real-mode = 키 필요) |
| depth_actionability | Phase 12 (CC-011) | 깊이/실행가능성 (Phase 12 0.231↔1.000 척도) |
| **사람 blind A/B** | human_review_rubric.md | 채점자가 A/B 모름 + 어느 쪽이 더 쓸만한지 선택 (편향 차단) |

- 케이스: golden_set 25 중 brand/series 맥락이 의미있는 부분집합(예: 8~12). 페르소나 1~2개에 고정.
- 동일 입력 × {A, B} 쌍 생성 → 채점 → 차이(B−A) 측정.

### 3.2 종적 / compounding (H2) — 누적 PKM proxy

```
시뮬 페르소나의 PKM 누적량을 N=0 / 5 / 20 으로 단계 주입 → 각 단계에서 B 품질 측정.
  N=0  → B는 A와 같아야 함 (주입할 맥락 없음 = sanity check)
  N=5  → 소폭 상승 기대
  N=20 → 더 상승 기대 (단조 증가 = compounding 신호)
기울기(slope)가 양수 + 유의 → H2 지지. 평평 → moat 엔진 약함.
```

---

## 4. 의사결정 게이트 (go / no-go — 실험의 산출물)

> 임계값은 rough(실 entry 시 multi-llm-validation으로 확정). 핵심은 "숫자로 결정한다".

```
GO (PKM/RAG 빌드 승격):
  H1: B−A ≥ +0.15 (critic/depth 0~1 척도) 또는 사람 blind 선호 ≥ 65% B
  AND H2: N=0→20 기울기 양수 + 단조
  → PKM/RAG 제안서 §9 단계화를 실 Phase로 재우선순위 entry.

PARTIAL (일부 scope만):
  brand_pkm 효과 有 / trend 무효(또는 그 반대) 등 scope별 분해 → 효과 있는 scope만 빌드.
  → 로드맵을 측정 결과로 가지치기 (★ 이게 실험의 최대 가치).

NO-GO / RE-SCOPE (moat 가설 기각):
  B ≈ A (주입이 품질을 못 올림) → 무거운 PKM/RAG 보류.
  → 차별화 레버를 데이터레이어가 아닌 곳(UX/Akinator·전문화·워크플로)으로 전환.
```

---

## 5. ★ 정직한 한계 (직전 리서치와 직결 — 반드시 명시)

```
1. 실험은 "메커니즘"을 검증한다(맥락 주입이 품질을 올리는가), "시장 moat"를 증명하지 못한다.
   진짜 moat("쓸수록 좋아지는 독점 데이터")는 실사용자 누적이 전제 — 시뮬은 proxy일 뿐.
   → 실험 GO여도 "데이터 쌓을 실사용 루프"는 여전히 별도 숙제(직전 리서치 결론 유지).

2. compounding(H2)을 시뮬 페르소나로 보면 over-optimistic 위험.
   시뮬 PKM이 채점 케이스에 "과적합"되면 실제보다 좋게 나온다.
   → 시뮬 PKM은 채점 케이스와 분리된 페르소나로 작성 + 사람 blind로 교차 확인.

3. real-mode 의미채점은 LLM 키 필요(opt-in). 키 없으면 structural만 → H1 약하게만 검증.
   → 키 제공 여부가 실험 깊이를 결정(결정 필요 사항 §8).
```

---

## 6. Phase 재정립 (제안 — ★ 실험만 지금, 하류는 verdict 후)

> 조정 2 적용: 모든 페이즈를 지금 재정립하지 않는다. 실험 페이즈만 완전 정의 → 결과가 하류를 재배정.

```
[지금 정의] 실험 페이즈 (A/B: baseline vs agent-grade)  ← 본 문서가 entry 근거
   S1  실험 하네스: A/B 토글 + 시뮬 PKM fixture + 케이스 부분집합 고정
   S2  정적 A/B(H1): eval + critic/depth + (키 있으면 real-mode)
   S3  사람 blind 채점 키트(human_review_rubric 재사용) — 사용자 채점
   S4  종적(H2): N=0/5/20 누적 + 기울기
   S5  종합 + go/no-go/partial 판정 리포트 → PARKED 로드맵 재우선순위 제안

[verdict 후 재정립] — 결과에 따라 가지치기:
   GO     → PKM/RAG §9 1차(trend+personal+brand orchestrator) 실 Phase 부여
   PARTIAL→ 효과 scope만 (예: brand_pkm만) Phase
   NO-GO  → UX/전문화 트랙으로 로드맵 전환
   (commercial_viral / director 품질 보강은 PKM/RAG 결과에 종속 — 그 뒤)
```

★ 번호 정합 필요(결정): 현재 Phase 15 done. PKM/RAG 제안서가 P16~21을 provisional로 점유 + `phase-16-intent-leniency` 브랜치 미머지. 실험은 **그 P16~21의 GATE**이므로 번호상 가장 앞. → 실험을 다음 번호로, PKM/RAG provisional은 실험 verdict 후 재배정(제안서 §0.3과 일치).

---

## 7. 하네스 매핑 (각 지침에 어떻게 전달되나)

| 단계 | 트리거되는 하네스 지침(Skill) | 산출 |
|---|---|---|
| 실험 entry | **phase-start** (4점검: assumptions/simplest slice/surgical scope/verification) | phases/active/{실험}/goals·scope·non_goals·acceptance |
| 측정 | **eval-run** (golden_set runner + 임계값 게이트) | eval/regression_results/{date}_ab-experiment.md |
| 사람 채점 | human_review_rubric | eval/human_review/{date}_ab-blind.md |
| 시뮬 PKM이 스키마/contract에 닿으면 | **contract-change** (직접 편집 금지 → 제안서) | meta/proposals/ |
| 큰 결정(임계값·go/no-go 기준) | **multi-llm-validation** | meta/validations/ |
| 종료 | **phase-complete** (smoke + scenario_sim + 회고 + archive + REGISTRY/STATE) | meta/retrospectives/ |

★ 비충돌: 실험은 `use_rag`/brand_memory 주입을 **읽기/토글**만 — 운영 경로 behavior-preserving(A=현재 OFF 경로 byte-identical). 시뮬 fixture는 테스트/실험 영역에만.

---

## 8. 결정 필요 사항 (실 entry 전 사용자 승인)

> ★ 2026-06-03 사용자 결정 반영: #1 real-mode ON. #2~#5 는 rough 권장 default 채택(entry 시 multi-llm-validation 으로 임계값만 재확인).

```
1. ✅ real-mode 의미채점 = ON (LLM 키 제공). critic 8~10차원 의미채점으로 H1 강하게 측정.
      → 키는 .env(이미 .gitignore)에만, 코드/commit/채팅 평문 절대 금지. 실행 = opt-in 배치.
2. (default) 페르소나 = 2개 (1개는 과적합 위험, 2개로 견고성↑).
3. (default) 케이스 부분집합 = golden_set 25 중 brand/series 맥락 의미있는 ~10.
4. (default) output_mode 고정 = director (가장 풍부 → A/B 차이 가장 잘 드러남).
5. (default) compounding N 단계 = {0, 5, 20}.
6. ⏳ Phase 번호 정합(§6) + 미머지 intent 브랜치 정리 — entry 직전 확정(사용자).
```

---

## 9. 리스크와 방어책

| 리스크 | 방어책 |
|---|---|
| 기획안 무한루프(문서만 쌓임) | 실험 = 싸고 결정-지향. S5에서 **반드시 go/no-go 숫자** 산출. 빌드는 그 뒤 |
| 시뮬 PKM 과적합(over-optimistic) | 시뮬 페르소나 ↔ 채점 케이스 분리 + 사람 blind 교차확인 (§5) |
| 통제 깨짐(A/B가 데이터 외 다른 것도 다름) | output_mode/모델/프롬프트/temp 전부 고정 — 단일 변수 강제 (§2) |
| compounding을 실험으로 과신 | 실험=메커니즘, moat=실사용 — 명시적 분리 (§5.1) |
| 운영 회귀 | A=현재 OFF 경로 byte-identical, 시뮬은 실험 영역만 (§7) |
| 하류 페이즈 조기 재정립 | verdict 후 재우선순위(§6) — PKM/RAG §0.3과 일치 |

---

## 10. 다음 단계

```
1. 본 rough v0 검토 + §8 결정 사항 확정 (사용자).
2. phase-start 로 실험 페이즈 entry (4점검 + acceptance = H1/H2 측정 기준).
3. S1~S5 진행 → S5 go/no-go/partial 리포트.
4. 결과로 PARKED 로드맵(PKM/RAG §9 / commercial_viral) 재우선순위 → 실 Phase 부여.
```
