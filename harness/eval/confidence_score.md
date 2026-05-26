# confidence_score.md — confidence 점수 정의 + 보정 정책

> 위치: `eval/confidence_score.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `docs/contracts/output_schema.md` §3~§12 (각 prompt의 confidence 필드)
> 참조: `eval/video_planning_eval.md` (Critic 점수와의 차이)
> 참조: `docs/contracts/rag_data_contract.md` §4.2 (eval_score)

---

## 1. 목적

각 LLM 출력에 부착되는 `confidence` 값의 **의미 / 임계값 / 보정 정책**을 통일한다. 현재 5개 prompt(P-001~P-005)의 카드와 P-006/P-005q/P-AUX-1/P-AUX-2에 confidence 필드가 있고, 각 사용 맥락이 다르다. 본 문서가 단일 출처로 통일한다.

---

## 2. 평가 차원 (5 개)

### 2.1 calibration — 캘리브레이션

```
정의: confidence 값이 실제 사용자 채택률과 일치하는가.
측정: 같은 confidence 구간의 카드들 실제 채택 비율.
  - confidence 0.9 카드의 채택률이 90%에 근접해야 정상
임계: 
  - Expected Calibration Error (ECE) ≤ 0.10
  - 누적 100건 이상에서 측정
0점: ECE > 0.30 (심한 미스캘리브레이션)
5점: ECE ≤ 0.05
```

### 2.2 threshold_discrimination — 임계값 분별력

```
정의: 임계 이상 / 이하의 결과 차이가 유의미한가.
측정:
  - confidence ≥ 0.7 그룹의 채택률
  - confidence < 0.5 그룹의 채택률
  - 두 그룹의 차이가 통계적으로 유의
임계: 두 그룹의 채택률 차이 ≥ 30%p
0점: 차이 없음
5점: ≥ 50%p
```

### 2.3 confidence_distribution — 분포 건전성

```
정의: confidence 값이 0과 1에 몰리지 않고 적절한 분포를 보이는가.
측정:
  - 분산 ≥ 0.05
  - 0.0~0.3 비율: 5~15%
  - 0.3~0.7 비율: 30~50%
  - 0.7~1.0 비율: 35~65%
0점: 한 구간에 80% 이상 몰림 (overconfidence)
5점: 균형 분포
```

### 2.4 cross_prompt_consistency — Prompt 간 일관성

```
정의: 같은 의미의 confidence가 prompt 간에 일관된 척도를 갖는가.
측정:
  - P-001 카드의 confidence 0.8과 P-006 plan의 confidence 0.8이 비슷한 채택률
  - prompt 간 캘리브레이션 차이
임계: prompt 간 ECE 차이 ≤ 0.10
0점: 큰 격차 (P-AUX-1만 항상 0.95 등)
5점: 일관
```

### 2.5 user_perceived_match — 사용자 체감 일치도

```
정의: 사용자가 본 카드 / plan의 confidence가 직관적으로 일치하는가.
측정: 사용자 설문 (Phase 2+) 또는 운영자 sample 검토.
임계: 운영자 sample 검토에서 80% 이상 "타당하다" 응답.
0점: 사용자 신뢰 손실 (낮은 점수 카드가 더 좋아 보이는 등)
5점: 사용자 체감 일치
```

---

## 3. Prompt별 confidence 의미

### 3.1 P-001 ~ P-004 (Discovery 카드)

```
필드: cards[*].confidence
의미: 이 카드가 사용자의 short_idea와 selected_context에 얼마나 맞는지 LLM 자기 추정.
임계 (output_schema §3.2):
  - 평균 ≥ 0.5 (카드 4장 평균)
  - 개별 카드 ≥ 0.3 권장
사용:
  - 카드 정렬 (Phase 2+ 검토)
  - 자동 학습 신호 트리거 (rag_data §8.1: ≥ 0.7 + 3회 반복)
```

### 3.2 P-005 / P-005q (oneline_direction)

```
필드: body.confidence
의미: 한 줄 방향이 잘 정리됐는가의 LLM 자기 추정.
임계 (output_schema §7.2):
  - ≥ 0.5: 정상
  - < 0.5: rewrite_offered=true 자동 트리거
사용:
  - rewrite 옵션 노출 분기
  - Planner 진입 가드 (낮은 confidence 시 사용자 확인)
```

### 3.3 P-006 (plan_candidates)

```
필드: (현재 plan 단위 confidence 없음, hook/concept 등 본문만)
대신 Critic이 8 차원 점수로 사후 평가.
Phase 2+ 검토: plan별 confidence 추가 (LLM 자기 추정).
```

### 3.4 P-007 (Critic)

```
필드: (confidence 필드 없음)
대신 8 차원 0~5 점수가 confidence 대체 역할.
overall_score_avg가 confidence 역할.
```

### 3.5 P-AUX-1 (intent_filter)

```
필드: body.confidence
의미: 영상기획 판정의 자기 확신도.
임계 (output_schema §11.2):
  - ≥ 0.6: decision 그대로 사용
  - < 0.6: fallback 정책에 따라 "allow" 강제 (관대 기본값)
사용:
  - decision == block이지만 confidence < 0.6 → allow로 전환
```

### 3.6 P-AUX-2 (brand_memory_extractor)

```
필드: proposed_entries[*].confidence
의미: 이 추출 entry가 신뢰할 수 있는가의 자기 추정.
임계 (output_schema §12.2, agent_io §7.5):
  - 1회성 결정    ≤ 0.3
  - 2회 이상 반복 ≥ 0.7
  - 명시적 선호  ≥ 0.9
사용:
  - 자동 INSERT 분기 (≥ 0.9 + conflicts=false)
  - pending queue 분기 (0.7~0.9)
  - 폐기 (< 0.7)
```

---

## 4. 입력 / 출력 형식

### 4.1 입력 (캘리브레이션 분석)

```yaml
analysis_period: "2026-05-01 ~ 2026-05-31"
prompts:
  - "P-001"
  - "P-005"
  - "P-AUX-2"
data_sources:
  - "discovery_choices"           # 카드 선택 사실
  - "agent_io_logs.output_payload"
  - "brand_memory_entries"
```

### 4.2 출력

```yaml
period: "..."
scores:
  calibration: 0~5
  threshold_discrimination: 0~5
  confidence_distribution: 0~5
  cross_prompt_consistency: 0~5
  user_perceived_match: 0~5
confidence_health_avg: 0~5
per_prompt_metrics:
  P-001:
    ece: 0.08
    distribution: { "0-0.3": 0.10, "0.3-0.7": 0.45, "0.7-1.0": 0.45 }
    threshold_diff: 0.42
  ...
calibration_drift_alerts:           # 시점 간 큰 변화
  - { prompt: "P-006", from: 0.06, to: 0.18 }
```

---

## 5. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| calibration | 자동 (ECE 계산) | — |
| threshold_discrimination | 자동 | — |
| confidence_distribution | 자동 (히스토그램) | 운영자 보조 |
| cross_prompt_consistency | 자동 | 운영자 보조 |
| user_perceived_match | 운영자 sample / 사용자 설문 | 운영자 주도 |

---

## 6. 임계값

```
모든 차원 ≥ 3: passing
1 차원이라도 < 3: warning (캘리브레이션 재검토)
1 차원이라도 < 2: failing (prompt 보정 또는 임계 재설정)

특수 게이트:
- calibration ECE > 0.20: 즉시 prompt 보정 (수치 튜닝 또는 prompt 수정)
- confidence_distribution이 한쪽에 80% 몰림: prompt 안내 강화
- cross_prompt_consistency 차이 ≥ 0.20: prompt별 임계 분리 검토
```

---

## 7. 보정 정책

### 7.1 사후 보정 (post-hoc calibration)

```
Platt scaling 또는 isotonic regression:
  - 누적 1000건 이상 데이터로 보정 모델 학습
  - confidence_raw → confidence_calibrated 매핑
  - DB에는 raw + calibrated 둘 다 저장 (output_schema 확장 검토)

도입 시점: Phase 11+ (충분한 데이터 누적 후).
```

### 7.2 임계값 재설정

```
Phase별 누적 데이터로 임계 재조정:
  - P-AUX-1 fallback 임계 (현재 0.6)
  - P-005 rewrite_offered 임계 (현재 0.5)
  - P-AUX-2 자동 INSERT 임계 (현재 0.9)

재조정 절차:
  1. eval/confidence_score 정기 분석 (월간)
  2. 임계 후보 산출 (ROC 곡선 기반)
  3. contract-change Skill 절차로 output_schema 갱신
  4. golden_set 회귀 평가로 영향 측정
```

### 7.3 prompt 수정으로 보정

```
LLM에게 confidence 산출 가이드 명시:
  "0.9 이상은 매우 확신할 때만 사용. 1회 추측은 0.3 이하."

대안:
  - chain-of-thought로 confidence 근거 작성 후 점수 매기기
  - 자기 검증 단계 추가 (P-007 형식의 단순 self-critic)
```

---

## 8. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §3, §7, §11, §12 (각 prompt의 confidence 필드)
  - rag_data_contract.md §4.2 (eval_score는 별도, confidence와 구분)
  - agent_io_contract.md §7.5 (P-AUX-2 자동 INSERT 임계)

Skill:
  - eval-design (캘리브레이션 분석 갱신)
  - prompt-version-review (임계 변경 시)
  - meta-retrospective (월간 캘리브레이션 회고)

연관 평가:
  - regression_eval.md (회귀에서 confidence 분포 변화 감지)
  - failure_taxonomy.md (낮은 confidence → terminal 비율)
```

---

## 9. Open Questions

1. plan별 confidence 추가 (P-006) — Critic 8차원 점수와의 중복 검토.
2. P-007 자체에 confidence 필드 추가 — "이 채점이 얼마나 확신하는가" 메타.
3. 사후 캘리브레이션 도입 시 raw 값 보관 정책 — 분석 vs UI 노출.
4. user_perceived_match의 사용자 설문 인프라 — Phase 2+ 검토.
5. confidence가 낮을 때 자동 행동 (rewrite_offered 외) — 사용자 안내 강화 vs UI 차별 표시.
6. 카드 다양성과 confidence의 트레이드오프 — 다양성을 위해 의도적으로 낮은 confidence 카드 포함 가능한가.
