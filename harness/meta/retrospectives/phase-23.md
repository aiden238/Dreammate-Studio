# Phase 23 회고 — 품질 정식화 (실 LLM 전수 eval baseline + human review 정비)

> 2026-06-04 | 평가 phase (런타임 0 — 측정/리포트) | behavior-preserving

## 1. 무엇을 했나
mock-deterministic eval(구조)만 CI화된 상태에서 **실 LLM 품질 baseline** 확정 + human review 정비.
- **S1**: golden_set 25 케이스 실 LLM(rich planning gpt-4o-mini + 9차원 critic gpt-4o) 전수 평가 → baseline 리포트.
- **S2**: Phase 12 S4 kit 2케이스 compact↔rich LLM-judge 대조 + 사용자 채점 시트(실채점=사용자 deferred).

## 2. 핵심 성과 / 검증
- ★ **실 LLM 전수 baseline 확정**(eval/regression_results/2026-06-04_phase-23-real-baseline.md): overall **mean 4.41**(4.0~4.78) / depth **4.22**(4~5) / 18/18 approve / **P0 7/7** / 광고 1(입력 유래) / 차단 0. → 이후 회귀 기준선.
- ★ **정직한 발견 2개**:
  - **critic 낙관 편향("88점 함정")**: 전수 18/18 approve + 8차원 overall 이 compact↔rich 를 거의 구분 못함(둘 다 ~4.25). generic critic 만으론 깊이/fit 우위 안 보임(Phase 16 A/B 와 동일) → 절대품질 아닌 **회귀 기준선**으로만 + 사람 검증 필요.
  - **rich 우위는 depth_actionability(9차원)에서만**: compact 은 미채점, rich 4~5. 사람 would_use 가 이 격차를 보는지 = human review 핵심 질문.
- behavior-preserving: ★ 운영 코드 0 수정(eval=호출만) → pytest **714 불변** + scenario_sim 36/36 + audit 0. mock CI 경로 불변(real=opt-in 1회).

## 3. 학습 / 패턴
- **measurement≠quality**: 높은 critic 점수(4.41/전부 approve)는 "측정 도구(critic)의 낙관"이지 절대 품질 증거가 아니다. baseline 은 **회귀 탐지 기준선**으로 쓰고, 절대 품질은 사람이 본다(P-LLM-JUDGE-OPTIMISM, Phase 16 계승).
- **8차원의 맹점**: generic 8차원은 compact↔rich 무차별 → depth_actionability(9차원) 같은 **목적 특화 차원**이 있어야 tier 우위가 측정됨. fit/depth 류 특화 차원의 가치 재확인.
- **opt-in 실 LLM 1회 baseline**: CI(mock, 비용 0) 유지 + 실 LLM 은 Temp/ 1회 배치(~$1) → baseline 확정. CI 자동 real 전환 회피(비용/비결정성).

## 4. 정직한 한계 / 이월
- **human 실채점 미완**: 채점 시트·LLM 기준선 준비됨, 실채점은 사용자(deferred). 회수 시 human↔LLM diff + would_use 격차 분석.
- **광고 입력-유래 누수**: GS-022(역대급 보온력) — 입력의 과장이 plan 에 잔존. 광고 필터 입력측 강화 = 후속.
- **skip 6 / error 1**: skip=카드 프롬프트 케이스(planning 대상 아님), error 1=planning 1회 변동. baseline 은 planning 18케이스.
- **케이스당 1안·rich·gpt-4o-mini/4o**: 3안 전수·compact 대조 전수·가중 평균은 후속. case_id ?N 라벨(loader 키 코스메틱).

## 5. 산출물
- eval/regression_results/2026-06-04_phase-23-real-baseline.md (전수 baseline)
- eval/human_review/2026-06-04_phase-23-judge-compare.md (LLM-judge 대조 + 사용자 채점 시트)
- Temp/run_eval_baseline.py + run_human_compare.py (레포 밖, 커밋 0)
- 운영 코드/contract 0 (측정 phase)

## 6. 다음
- 이월: human 실채점 회수 → human↔LLM diff / 광고 입력 필터 강화 / 3안·compact 전수 / 가중 평균 검토.
- 로드맵: 배포 Gate B~G(baseline = Gate D 전제 충족) / commercial_viral·director baseline(별도 tier).
