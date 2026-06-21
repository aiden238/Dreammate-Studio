# Cross-provider Judge (Claude) — 88점 함정 verdict 차단 측정 + production 배선

> 2026-06-21 · 같은 10개 plan + 같은 사람(rater A) ground truth 에 대해 **3-arm** 비교.
> 데이터: `eval/human_review/2026-06-15-calib-ab-{cases,key}.json` · `-scores-A.json` ·
> `-claude.json`(본 측정). 측정 스크립트: `scripts/cross_provider_judge_rescore.py`.
> 선행 예비: `eval/regression_results/2026-06-15-critic-calib-ab-preliminary.md`.

## 0. 한 줄 결론

**Cross-provider Claude judge 가 "88점 함정"을 verdict 기준으로 닫는다 — false-approve
10/10 → 0/10. approve 10건을 전부 뒤집고(8 revise · 2 reject) 사람과의 평균괴리를
2.27 → 0.53 으로 줄였다.** 동일-provider calibration(A1)이 verdict 를 0건도 못 뒤집은
것과 대조적. self-review 편향이 깨지며 genericness("전형적 패턴"·"흔한 포맷")가
differentiation·hook 저점으로 잡혔다.

## 1. 설정 (3-arm, 통제)

| arm | 채점자 | 메커니즘 | 비고 |
|---|---|---|---|
| **A0** | gpt-4o critic | calibration OFF (현 default) | 생성=gpt-4o-mini / 채점=gpt-4o (self-provider) |
| **A1** | gpt-4o critic | calibration ON (anti-optimism 프리앰블 + per-axis 게이트) | 동일-provider 보정 |
| **A2** | **claude-sonnet-4-6** | **cross-provider 독립 judge** | 같은 critic system_prompt·10차원·verdict 규칙, **채점 모델만 교차** |

- 10케이스(정상 5 = golden_set 도메인 / 얕은 5 = 의도적 빈약 입력), output_mode=director(10차원).
- A2 는 A0/A1 과 **같은 plan** 을 재채점 (생성 0, 채점만 교차) → 변인 = 채점 provider 1개.
- 사람: blind 5차원 0~5 평균 = human_avg (rater A, N=1 예비). verdict 동형 규칙
  approve≥3.5 / revise 2.5~3.5 / reject<2.5.
- 사전 동결 임계: **false-approve = critic verdict=approve AND human_avg < 3.0**.

## 2. 결과표

| case | kind | human/5 | human verdict | A0 | A1 | **A2 (Claude)** | 사람일치 |
|---|---|---|---|---|---|---|---|
| GS-001 | normal | 2.6 | revise | approve 4.5 | approve 4.0 | **revise 2.8** | ✓ |
| GS-002 | normal | 2.8 | revise | approve 4.6 | approve 4.1 | **revise 2.9** | ✓ |
| GS-003 | normal | 1.8 | reject | approve 4.4 | approve 4.2 | **revise 3.0** | ✗(덜 엄격) |
| GS-004 | normal | 1.6 | reject | approve 4.2 | approve 3.8 | **reject 2.3** | ✓ |
| GS-005 | normal | 2.6 | revise | approve 4.5 | approve 4.1 | **revise 2.9** | ✓ |
| SHALLOW-1 | shallow | 2.6 | revise | approve 4.5 | approve 4.2 | **revise 2.5** | ✓ |
| SHALLOW-2 | shallow | 2.0 | reject | approve 4.4 | approve 4.0 | **reject 2.4** | ✓ |
| SHALLOW-3 | shallow | 1.8 | reject | approve 4.3 | approve 3.9 | **revise 2.5** | ✗(덜 엄격) |
| SHALLOW-4 | shallow | 2.0 | reject | approve 4.5 | approve 4.3 | **revise 2.9** | ✗(덜 엄격) |
| SHALLOW-5 | shallow | 2.0 | reject | approve 4.6 | approve 4.4 | **revise 2.9** | ✗(덜 엄격) |

**평균**: 사람 **2.18/5**(≈44점) · A0 **4.45**(≈89점) · A1 **4.10**(≈82점) · A2 **2.71**(≈54점).

## 3. 핵심 지표

| 지표 | A0 | A1 | **A2 (Claude)** |
|---|---|---|---|
| **false-approve율** | **10/10** | **10/10** | **0/10** ✅ |
| approve 건수 | 10 | 10 | **0** (→ revise 8 / reject 2) |
| 사람괴리 mean(\|critic−human\|) | 2.27 | 1.92 | **0.53** (≈76%↓) |
| verdict-exact 사람일치 | 0/10 | 0/10 | **6/10** (나머지 4 = revise vs 사람 reject, **approve 아님**) |

- A1(calibration) 단독: 점수만 0.35 당기고 **verdict 0건 변경** → false-approve 100% 잔존.
- A2(cross-provider): approve **10건 전부** 뒤집음. 불일치 4건도 "Claude revise vs 사람 reject"
  (Claude 가 덜 엄격)일 뿐 **approve 로 잘못 통과시킨 건 0** → false-approve 게이트 완전 차단.

## 4. 메커니즘 — genericness 를 잡는가 (예)

verdict 를 뒤집은 직접 동인은 차원 점수 급락 (A0→A2 평균):
**differentiation 3.60→1.90 · hook_strength 3.80→1.90 · structure 5.00→3.00 ·
retention_design 4.00→2.20 · depth_actionability 4.40→2.80.**

Claude reason 원문이 genericness 를 명시:
- GS-001: "동아리 소개→활동→인터뷰→비전 구조는 대학 홍보 영상의 **전형적 패턴**… 차별화
  장치가 없다", 후크 "슬로건 수준".
- SHALLOW-4: "엉뚱한 실험 콘텐츠는 유튜브에서 **매우 흔한 포맷**이며 차별화 요소가 plan 내에
  제시되지 않았다", 후크 "막연한 질문형".

→ OpenAI(gpt-4o)가 생성한 plan 을 같은 OpenAI critic 이 채점하던 **self-review 편향**
(differentiation 후한 점수)이, 다른 provider 에선 깨졌다. **모델 교체 = 다른 blind spot**
이라는 아키텍처 레벨 효과 (plotter 의 in-provider Haiku→Opus judge 보다 강함).

- normal/shallow 구분력은 Claude 도 약함(전부 revise/reject 권역) — verdict 게이트는 닫지만
  미세 랭킹 분리는 별개 과제.
- malformed/실패 0/10 (GS-001 attempt 1 토큰절단성 malformed → 재시도 1회로 흡수, A11 정합).

## 5. Production 배선 (gated / additive / behavior-preserving)

측정이 강한 레버임을 입증 → opt-in 운영 레버로 배선 (DEFAULT 불변).

- **config**: `critic_judge_provider` (default `"openai"`). `"anthropic"` 시 critic 채점만
  Claude(registry `claude-sonnet`)로 교체 — plan 생성·출력 스키마·verdict 규칙 불변.
- **critic**: `agents/critic.py::_judge_via_anthropic` (AnthropicAdapter + gateway seam,
  cross_validation 과 동일 축). json_mode → 펜스 정규화. ANTHROPIC_API_KEY 없으면 ValueError(안전 차단).
- **OFF=byte-identical**: default `"openai"` → 기존 gpt-4o 경로 그대로. client 주입(테스트 mock)
  시 provider 무관하게 그 client 사용(결정성 보존).
- **검증**: `tests/test_critic_cross_provider.py` (4) + **전체 pytest 835 passed**
  (기존 critic 51 불변 = OFF byte-identical).
- realuse 프로파일에 **미포함** (default 전환 = 모델 교체(major) → prompt-version-review 절차 대상).

## 6. 한계 + 다음

- **N=1 rater 예비** (κ 미산출), **N=10 소표본** → 방향성 1차. 팀원(rater B) 채점 후
  `scripts/analyze_blind_ab.py --rater A --rater B` 로 inter-rater κ + 정식 리포트.
- 측정 temp=0.1, production 배선 temp=0.2(critic 표준) — 저온 평가 영역이라 verdict-flip 효과는
  강건(differentiation 저점은 온도 비민감)하나, 정식화 시 동일 temp 재측정 권장.
- **권장 운영 디폴트**: A2(provider 교체)는 OpenAI 신호를 버림. 더 안전한 대안은
  **consensus-min(둘 중 더 엄격한 verdict 채택)** — 단조(절대 더 약해지지 않음)이며 본 10케이스에선
  Claude verdict 와 동일 결과(Claude ≤ OpenAI). 비용 2× 트레이드오프. 별도 측정 대상.
- 후속: rater B → κ / consensus-min ablation / content-specificity anchor(병행 레버).
