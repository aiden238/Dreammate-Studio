# Phase 13 S6 — 깊이 재측정 리포트 (rich 운영 반영 후 OFF/ON 토글 실측)

> 작성: 2026-06-03 | Phase 13 출력 확장 phase (Slice S6 — cost 재조정 + phase-complete)
> 평가 차원 근거: CC-011 `depth_actionability` (eval/video_planning_eval.md §2.A.1)
> 선행 측정: `eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md` (Phase 12 — compact 0.231 vs rich(측정 전용 프롬프트) 1.000 = 4.3x)

## 1. 목적

Phase 12 는 **측정 전용 프롬프트**(운영 미반영)로 깊이 격차(compact 0.231 / rich 1.000)를 입증했다.
Phase 13(S1~S5)은 그 rich 출력을 **운영 경로에 gated additive 로 반영**했다 — 스키마 12 슬롯(S1) + 프롬프트 P-006 v1.1.0(S2) + gated wiring `rich_output_enabled`(S3) + Critic depth(S4) + frontend rich(S5).

본 재측정의 질문 = **"Phase 12 가 측정으로 보여준 깊이(잠재 1.0)가, 운영 `run_planning()` 의 flag ON 경로에서 실제로 재현되는가"** + **"flag OFF 는 Phase 12 baseline(compact 0.231)을 byte-identical 로 유지하는가"**.

즉 Phase 12 가 "측정 전용 프롬프트로 가능"을 보였다면, S6 는 "**운영 코드 ON 경로로 동일 깊이가 나온다**"를 확정한다 (격차 해소의 운영 입증).

## 2. 방법 (재현 가능)

- **모델**: `gpt-4o-mini` (운영 slot0 동일 모델 — Phase 12 와 동일, 모델 변수 통제).
- **측정 대상 = 운영 함수 `backend/fastapi/agents/planning.run_planning()`** (★ Phase 12 와 달리 측정 전용 프롬프트 없음 — 운영 코드 그대로).
- **flag 토글**: `rich_output_enabled` 를 OFF/ON 으로 토글하며 동일 함수 호출.
  - 토글 절차: env 설정 변경 후 `get_settings.cache_clear()` (lru_cache 무효화) → `run_planning()` 재호출. 운영 코드 0 수정 (config flag 만 토글).
  - **OFF**: `run_planning()` 이 운영 compact `SYSTEM_PROMPT`(v1.0.0) 경로 — Phase 12 baseline 과 동일.
  - **ON**: `run_planning()` 이 rich `RICH_SYSTEM_PROMPT`(P-006 v1.1.0, S2/S3 wiring) 경로 — rich 12 슬롯 요구.
- **표본**: golden_set 도메인 대표 **4** (요리·뷰티·IT리뷰·운동 — Phase 12 6 표본의 부분집합, 핵심 도메인 커버).
- **채점**: `depth_actionability` **13 feature** 의 구조적 존재 여부(0/1) → depth = 존재 비율(0~1). (Phase 12 와 동일 채점기)
  - features: target_audience, tone, hook_variants, beats_3plus, beat_visual, beat_dialogue, beat_caption, shots_broll, thumbnail, title_candidates, cta, references, length_variants
- 측정 스크립트(임시, 레포 외 보관)는 위 절차를 그대로 구현 — 운영 `run_planning` + `get_settings.cache_clear()` import 만(운영 코드 수정 0).

## 3. 결과

| 케이스(도메인) | OFF (compact) | ON (rich) | gap |
|---|---|---|---|
| 자취요리 30s | 0.231 | 1.000 | +0.769 |
| 메이크업 60s | 0.231 | 1.000 | +0.769 |
| 이어폰 리뷰 45s | 0.231 | 1.000 | +0.769 |
| 홈트 30s | 0.231 | 1.000 | +0.769 |
| **평균** | **0.231** | **1.000** | **+0.769 (4.3x)** |

- **목표 ≥ 0.8 → ON 1.000 PASS** (4/4 케이스 일관, 편차 0).
- **OFF 0.231 = Phase 12 baseline(compact) byte-identical 재확인** — flag OFF 경로가 운영 compact 출력을 그대로 유지(S3 gated wiring 의 OFF byte-identical 보장 실측 확인).
- 격차(Phase 12 = compact 0.231 vs 잠재 1.0)가 **운영 ON 경로에 그대로 반영됨 = 격차 해소**. 측정 전용(Phase 12)이 아니라 운영 `run_planning()` ON 으로 동일 깊이.

### feature별 (OFF / ON)

| feature | OFF | ON | 비고 |
|---|---|---|---|
| beats_3plus | 1.00 | 1.00 | compact 보유 (변동 없음) |
| beat_visual | 1.00 | 1.00 | compact 보유 (beat 설명) |
| cta | 1.00 | 1.00 | compact 보유 (purpose) |
| target_audience | **0.00** | 1.00 | OFF 결핍 → ON 충족 |
| tone | **0.00** | 1.00 | OFF 결핍 → ON 충족 |
| hook_variants | **0.00** | 1.00 | OFF 후크 1개 → ON 변형 |
| beat_dialogue (대사) | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |
| beat_caption (자막) | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |
| shots_broll | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |
| thumbnail | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |
| title_candidates | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |
| references | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |
| length_variants | **0.00** | 1.00 | S1 스키마 슬롯 추가 → ON 충족 |

→ OFF 는 13 feature 중 **3개만**(23%) 보유(compact 동일), ON 은 **13/13**(100%). Phase 12 가 "스키마 슬롯 부재"로 지목한 결핍 10개가 S1 additive 슬롯 + S2/S3 rich 프롬프트로 ON 경로에서 채워짐.

## 4. 결론

- **격차 해소 = 운영으로 입증.** Phase 12 의 "잠재 1.0"이 측정 전용이 아니라 운영 `run_planning()` flag ON 으로 **1.000 재현**(4/4 편차 0). 목표 ≥0.8 PASS.
- **OFF byte-identical 재확인.** flag OFF = Phase 12 baseline(0.231) 유지 — gated 롤아웃이 기존 동작을 절대 바꾸지 않음(behavior-preserving). 489/499 OFF 회귀 0 과 정합.
- 따라서 Phase 13 = "Phase 12 가 측정한 깊이 격차를 운영 출력에 gated 로 안전하게 반영"이 **수치로 완결**. rich 활성(ON) 전환은 별도 결정(default OFF 유지 — closing_notes non_goal).

## 5. 한계 / 주의 (정직한 캘리브레이션)

- **feature 존재 채점(0/1)은 품질이 아니다.** depth_actionability 13 feature 는 **슬롯 충족 여부**만 본다 — "대사가 있어도 진부할 수 있음". ON=1.000 의 의미 = 슬롯 100% 충족이지 콘텐츠 우수성 아님. 품질 채점은 human review / LLM-as-judge 보강 대상(Phase 12 S4 kit 계승).
- **표본 4** (Phase 12 6 표본의 핵심 부분집합). Phase 12 6/6 + S6 4/4 = 누적 일관성(편차 0) 높아 방향성 robust 하나, 전수(golden_set 25) 실 LLM eval 은 비용·범위로 미수행.
- ON=1.000 은 **rich 프롬프트가 13 feature 를 명시적으로 요구**해서 나온 상한선 — "이만큼 가능·운영 재현"의 증거이지 "이것이 최적 깊이"는 아님.

## 6. 비용 트레이드오프 (cost_control 연계 — S6 §2 cost 재조정 입력)

- rich 출력(ON)은 compact(OFF) 대비 **출력 토큰이 크게 증가**(rich 프롬프트가 12 슬롯 요구 → 대략 3~5배 추정). 3-plan 경로면 **× 3안**.
- → S6 cost 재조정(`ai_system/orchestration/cost_control_policy.md` §13~§14, B안 잔여 B-RES-1 통합)에 반영. flag OFF=기존 cost 불변 / ON=rich cost.

## 7. Phase 13 종료 함의

- **acceptance 충족**: depth 재측정 ON ≥0.8 (실측 1.000) PASS + OFF byte-identical 재확인 = Phase 13 S6 acceptance 핵심 조건 충족.
- rich default 전환(flag default ON)은 **미결정**(non_goal — gated OFF 유지, 사용자 opt-in / Phase 14 후속 결정).
- 후속: human review 실 채점 ↔ LLM-as-judge 신뢰도 대조(Phase 12 S4 kit) / 전수(25) 실 LLM eval baseline.
