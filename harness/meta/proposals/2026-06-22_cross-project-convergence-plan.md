# 강점 취합 수렴 설계 — Phase 32~34 기획 (Dreammate ↔ plotter)

> 작성: 2026-06-22. 트리거: 사용자 "지난 세션에서 서로 장점을 취합하여 설계하기로 했는데 미적용 — 파악 + phase 기획." + "하네스 phase에 맞게."
> 성격: **cross-project 수렴 제안(proposal-first)**. plotter=`qbuzxj370-crypto/plotter`(원격), Dreammate=본 repo.
> Codex 검토 반영: UX는 "완전 단발"이 아니라 "confirm/reject 보정 턴은 있으나 done 카드 후 follow-up 없음" / plotter exp4(MoA)는 generation-diversity 실험이지 cross-provider judge 반박 아님(N=14·single judge·human GT 없음).
> ★ **번호 정정**: canonical(main)은 Phase 31(active)까지 진행 → 다음 = **Phase 32**. (OneDrive 트리는 stale=Phase 27 active 뷰라 "28~30 future"로 보이나, 그건 미정렬분.) 31 active 동안엔 본 phase들은 **planned/provisional**.

## 0. 한 줄
지난 세션(critic 연구 아크)이 설계한 **"false-approve 통합 방어 = plotter의 결정적 깊이 게이트 + Dreammate의 cross-provider judge"**를 양 프로젝트에 적용한다. 현재 **어느 쪽도 풀세트를 안 가져** 미적용 상태다.

## 0.5 현재 상태 + (d) 조정 (2026-06-22, a~d 실행 반영)

| Phase | 상태 | 비고 |
|---|---|---|
| **32 Judge 수렴** | **초안 완료**(plotter 적용 대기) | `plotter-draft/ADR-0033` + `validator-cross-judge.patch.md`. plotter 원격이라 적용·테스트는 plotter에서(user). |
| **33 결정적 게이트** | **S1 구현완료**(b996eda) | Dreammate `critic_pacing_gate`(비-LLM, gated, pytest 845). S2(게이트∘judge 직교 합산 측정) 대기. |
| **34 정직·UX·RAG** | 미착수 | 후속. |

**(d) 조정 결론**:
- **번호**: canonical 기준 **32~34** 확정(PHASE_REGISTRY 등록 완료). OneDrive 트리도 main 정렬돼 동일 번호 인식("phase 30" 혼선 해소).
- **분할**: 3-phase(Judge/Gate/UX-RAG) 유지 — 직교 관심사라 합치지 않음.
- **우선순위 실측 보정**: 계획상 Phase 32(Judge)가 ★최우선이었으나, **Dreammate 직접 구현 가능분(Phase 33 게이트)이 저마찰이라 먼저 완료**. 실제 흐름 = ① Dreammate 게이트(완료) → ② plotter judge(초안→user 적용) → ③ 게이트∘judge 합산 측정(Phase 33 S2) → ④ UX/RAG(34).
- **active 1개**: 게이트는 critic 품질이라 Phase 31 테마와 겹치나, cross-project 수렴이라 **Phase 33로 등록**(planned). Phase 31(S1~S4 사실상 done) 정식 close 후 32~34가 active 승격 권장.

## 1. 찾은 결정 (파악)
- **근거**: `eval/regression_results/2026-06-15-critic-calib-ab-preliminary.md:43` — "후속(데이터가 정당화): **L3 결정적 깊이 게이트(plotter식 — LLM 점수 재량 박탈, 비-LLM 계산으로 approve 상한 강제) + cross-provider 독립 Judge(OpenAI 생성 → Claude 채점)**. 둘 다 같은 10 plan + 같은 사람 점수에 대보면 됨."
- **근거**: `2026-06-21-cross-provider-judge.md:74` — "모델 교체 = 다른 blind spot (plotter의 in-provider Haiku→Opus judge보다 강함)."
- **핵심**: calibration(프롬프트+per-axis gate) 단독은 verdict 0건 flip(false-approve 100% 잔존) → **결정적 게이트 + cross-provider judge를 합쳐야** 닫힌다. 이게 "서로 장점 취합" 설계의 정체.

## 2. 현재 상태 — gap 매트릭스 (어느 쪽도 풀세트 미보유)

| 강점 | 출처 | 무엇 | Dreammate | plotter |
|---|---|---|---|---|
| **cross-provider 독립 judge** | Dreammate | 생성≠채점 provider → self-review 편향 원천 차단. 측정: false-approve 10/10→0/10, ko 사람괴리 0.53 | ✅ (Phase 31 S1) | ❌ **보류**(ADR-0031 D1-C "항상 Opus", ADR-0007 대안C) |
| **consensus-min** | Dreammate | 두 judge 중 더 엄격 verdict 채택(단조, 2-judge) | ✅ | ❌ (ensemble은 ADR-0007서 기각 — 단 그건 3-judge 평균/다수결, consensus-min과 다름) |
| **결정적 깊이/pacing 게이트** | plotter | 비-LLM time-split·축 하드 게이트로 approve 상한 강제(LLM 점수 재량 박탈) | ❌ (calibration per-axis는 LLM 점수 기반 — director에서 미발동) | ✅ (`validator.py` 축 하드 게이트 + `structure_pacing_issues`) |
| **사전동결 임계 방법론** | plotter | 분석 전 임계 동결(사후 합리화 차단) | 🟡 (analyze_blind_ab "plotter식" 차용) | ✅ (exp 사전정의 Δ) |
| **정직 라벨(`추정/예시:`)** | Dreammate | 미검증 사실/고유명/레퍼런스 라벨 강제 | ✅ (P-006 v1.2.1) | 🟡 (날조금지+doc_id 인용 강제 O, 라벨 강제 X) |
| **Gemini ko 임베딩 + RAG ON/OFF 측정** | Dreammate | ko 검색 우위 + 가치 실측(Δ+0.9) | ✅ (측정) | ❌ (OpenAI 3-small 고정) / 🟡 측정 배선만(코퍼스 빈손) |
| **대화형 연속 UX(카드 후 follow-up)** | (양쪽 미흡) | 결과 카드 후 prompt/chat으로 재기획·iterate | ❌ | ❌ (confirm/reject 보정 턴만, done 후 follow-up 없음) |

## 3. 통합 목표 설계 (수렴점)
**품질 코어 = [결정적 깊이/pacing 게이트] ∘ [cross-provider 독립 judge] ∘ [consensus-min(선택)]** 를 양 프로젝트 공통으로.
- 결정적 게이트가 **비-LLM으로 approve 상한**을 막고(축/pacing 붕괴 차단), cross-provider judge가 **남은 self-review 낙관**을 다른 provider blind-spot으로 차단. 두 층은 **직교**(서로 다른 실패모드) → 합산 효과.
- 부가 수렴: 정직 라벨(`추정/예시:`) + Gemini ko 임베딩 옵션 + 대화형 연속 UX.
- ★ plotter의 **의도적 선택 존중**: cost/ROI(1인 팀), 트랙 자족성. cross-provider는 **gated 옵션 + consensus-min**으로 비용·키 의존을 통제. Dreammate 측정이 plotter의 보류 재고 트리거("B로 cross-model 편향 남으면", "κ<0.5면 GPT cross-Judge")를 충족.

---

# 4. Phase 기획 (하네스 phase 형식 — Phase 32~34, planned)

> 각 phase = `goals(목표·배경·통과기준) / scope(slices) / acceptance / non-goals` 4-섹션(Phase 31 컨벤션). Phase 31 종료 후 active 승격(active 1개). MoA(generation diversity, plotter exp4서 ROI 음수 기각)와 혼동 금지 — 본 plan은 **judge층 cross-provider + 결정적 게이트**(다른 레이어).

## Phase 32 — Judge 수렴 (cross-provider + consensus, plotter ← Dreammate) ★최우선

**목표**: plotter가 보류한 cross-provider judge를, Dreammate 측정 근거로 재고·채택해 양 프로젝트가 동일한 self-review-편향-차단 judge층을 갖게 한다.
**배경**: plotter ADR-0031 D1-C("항상 Opus")·ADR-0007 대안C(GPT cross-Judge)가 "B로 cross-model 편향 남으면/κ<0.5면 재고"로 보류. Dreammate가 false-approve 10/10→0/10 + ko 사람정렬(0.53)을 측정 → **재고 트리거 충족**.
**통과 기준**: cross/consensus가 in-provider judge 대비 false-approve↓(또는 비퇴행) + 비용 가드 내 + gated default 비퇴행.

**scope (slices)**
- **S1 (plotter ADR)**: `ADR-0033(가칭) — cross-provider judge 재고`. 근거 = Dreammate 측정 첨부. 결정 = judge provider 교차를 **gated 옵션** + **consensus-min**(in-provider judge ∧ cross judge 중 엄격 채택)으로 비용/키 통제.
- **S2 (plotter 배선)**: `app/agents/validator.py`에 judge provider 교차 옵션(default=현행 in-provider 상위) + consensus-min 경로. ANTHROPIC 키 없으면 graceful(현행). 일일 비용 가드(NF-M01) 내.
- **S3 (측정)**: 같은 평가셋(plotter 골든 or Dreammate 10케이스)에서 **in-provider(Opus) vs cross-provider vs consensus-min** false-approve·사람괴리 비교. 사전동결 임계(plotter식).

**acceptance**

| # | 기준 | 측정 | 통과선 |
|---|---|---|---|
| A1 | cross/consensus 배선(gated) | 코드+테스트 | OFF=현행 byte-identical, 키 부재 graceful |
| A2 | 편향 차단 효과 | 같은 평가셋 | cross/consensus false-approve ≤ in-provider |
| A3 | 비용 | 가드 | 일일 비용 가드(NF-M01) 내 |

**non-goals**: default judge 강제 전환(major, 별도) / 3-judge ensemble 부활(ADR-0007 기각 존중) / MoA generation-diversity.

## Phase 33 — 결정적 깊이 게이트 수렴 (Dreammate ← plotter) ★핵심

**목표**: Dreammate가 누락한 **비-LLM 결정적 게이트**(연구 arc의 나머지 절반)를 plotter에서 이식해, cross-provider judge와 직교하는 두 번째 false-approve 차단층을 만든다.
**배경**: calibration per-axis 게이트는 LLM 점수 기반이라 director "얕은 입력→깊은 plan"에서 미발동(연구 arc). plotter `structure_pacing_issues`는 plan 구조에서 직접 time-split을 계산(비-LLM).
**통과 기준**: 결정적 게이트가 LLM 점수와 무관하게 축/pacing 붕괴를 approve에서 차단 + OFF byte-identical.

**scope (slices)**
- **S1 (Dreammate 이식)**: critic/orchestrator에 **결정적 pacing/depth 게이트** — plotter `structure_pacing_issues`(시간합<목표×0.85 underfill / payoff>30% bloat) 이식 + director approve 상한을 **비-LLM 계산**으로 강제. gated/additive.
- **S2 (측정)**: 같은 10케이스에서 **cross-provider judge + 결정적 게이트 조합**이 false-approve를 닫는지(연구 arc 원래 후속 — 둘 다 같은 plan/사람점수에 대보기) + consensus-min과 직교성 확인.

**acceptance**

| # | 기준 | 측정 | 통과선 |
|---|---|---|---|
| A1 | 결정적 게이트(비-LLM) | 코드+테스트 | 축/pacing 붕괴 plan을 LLM 점수 무관 차단, OFF byte-identical |
| A2 | 직교 합산 | 같은 10케이스 | 게이트∘judge가 게이트·judge 단독보다 false-approve↓(또는 동률) |
| A3 | 게이트 | pytest | 전체 green(현 841 기준) |

**non-goals**: 새 평가 차원 추가(eval-design 별도) / plotter 게이트 1:1 복붙(Dreammate 스키마에 적응).

## Phase 34 — 정직·UX·RAG 수렴 (양방향, 후속)

**목표**: 부가 강점을 양방향 수렴 — 정직 라벨(plotter←Dreammate), 대화형 연속 UX(양쪽 신규), Gemini ko 임베딩(plotter←Dreammate, 선택).
**통과 기준**: 각 항목 gated/additive 비퇴행 + 측정 가능 개선 신호.

**scope (slices)**
- **S1 정직 라벨(plotter ← Dreammate)**: plotter `plan.py` 생성 프롬프트에 `추정/예시:` 라벨 강제(현 "날조 금지+doc_id 인용 강제"에 라벨링층). 검증 불가 고유명/통계 자인.
- **S2 대화형 연속 UX(양쪽)**: 결과 카드 후 **follow-up prompt/chat 입력**(refine/iterate/후속). plotter는 `ADR-0024 intent-confirm-loop stateless` 확장(done→follow-up stage). Dreammate도 동일 미보유 → 공통 신규.
- **S3 Gemini ko 임베딩(plotter ← Dreammate, 선택)**: plotter 코퍼스 큐레이션(50건) 후 ko 검색에서 Gemini vs OpenAI 임베딩 비교(Dreammate Δ 근거) → RAG ON/OFF 실측(현 코퍼스 빈손 no-op 해소).

**acceptance**

| # | 기준 | 측정 | 통과선 |
|---|---|---|---|
| A1 | 정직 라벨 | plotter 생성 샘플 | 미검증 단정에 `추정/예시:` 라벨 출현 |
| A2 | 연속 UX | e2e | done 카드 후 follow-up 입력→재기획 동작 |
| A3 | Gemini ko(선택) | 임베딩 비교 | ko 검색 Gemini ≥ OpenAI(코퍼스 후) |

**non-goals**: 대대적 UX 재설계 / MoA 부활 / 코퍼스 미수집 상태에서 RAG 강제 ON.

---

## 5. PHASE_REGISTRY 행 (provisional — 31 종료 후 등록)

```
| 32 | Judge 수렴 (cross-provider + consensus, plotter←Dreammate) | planned | plotter 보류 cross-provider judge 재고(Dreammate 측정 근거) + consensus-min. gated 옵션. |
| 33 | 결정적 깊이 게이트 수렴 (Dreammate←plotter) | planned | plotter structure_pacing_issues(비-LLM) 이식 → cross-provider judge와 직교 차단층. |
| 34 | 정직·UX·RAG 수렴 (양방향) | planned | 추정/예시: 라벨(plotter) + 결과-후 follow-up UX(양쪽) + Gemini ko 임베딩(plotter, 선택). |
| 35+ | 고도화 / 배포 | future | (기존 32+ 항목 이월) |
```

## 6. 비용·리스크·존중
- **비용**: cross-provider/consensus = LLM 콜 ↑ → gated + 일일 가드 + 2-judge(3-judge ensemble보다 쌈). plotter 1인-팀 ROI 우려를 옵션화로 흡수.
- **방향성 한계**: Dreammate 측정 N=10·rater A N=1(κ 미산출). plotter 적용 전 **rater B/κ + plotter 골든셋 재측정** 권장(둘 다 미충족 명시).
- **OneDrive 트리 정렬**: 본 번호(32~)는 canonical/main 기준. OneDrive 트리(phase-27 stale)는 main 정렬 후 동일 번호 인식.

## 7. 다음 액션 (사용자 결정)
1. Phase 33(Dreammate 결정적 게이트 이식) **실제 구현**(내가 write 가능) + 측정.
2. Phase 32 plotter `ADR-0033` 초안 + `validator.py` cross-provider/consensus **diff 초안**(plotter 원격이라 PR 초안 제공).
3. (선택) Phase 34 수렴.
