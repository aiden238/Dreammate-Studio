# regression_eval.md — 회귀 평가

> 위치: `eval/regression_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `eval/golden_set.md` (회귀 케이스 정의)
> 참조: `docs/contracts/output_schema.md` §19 회귀 평가
> 참조: `docs/contracts/rag_data_contract.md` §12.3 회귀 평가
> Skill 연동: `prompt-version-review`, `eval-run`

---

## 1. 목적

영상기획 AI 에이전트의 prompt / contract / RAG 데이터 변경 시 행동 일관성을 회귀 평가한다. 본 문서는 실행 절차 / 비교 정책 / 임계 / 리포트 포맷을 정의한다. 케이스 정의 자체는 `golden_set.md`에서 단일 출처로 관리한다.

---

## 2. 평가 차원 (5 개)

### 2.1 case_pass_rate — 케이스 통과율

```
정의: golden_set.md의 모든 case의 passing_criteria 통과 비율.
측정: pass / (pass + fail + error)
임계 (golden_set §3):
  - 전체 ≥ 90%
  - P0 100%
  - P1 ≥ 90%
  - P2 ≥ 80%
0점: P0 < 100%
5점: 모든 등급 임계 초과
```

### 2.2 baseline_diff — 베이스라인 대비 변화량

```
정의: latest-baseline.jsonl과 비교한 점수/응답 변화량.
측정:
  - quality_score 평균의 절대 변화
  - 각 케이스의 validation 결과 diff (true → false 또는 반대)
  - 광고 단어 차단율 diff
임계: 
  - quality_score 평균 변화 ≤ ±0.3 (output_schema §19.2)
  - validation true → false 회귀 1건이라도 발견 시 fail
0점: 회귀 1건 이상
5점: 변화 없음 또는 개선만
```

### 2.3 cost_drift — 비용 드리프트

```
정의: 케이스별 평균 비용 변화.
측정: latest-baseline 대비 케이스당 cost_usd 평균 변화.
임계:
  - 평균 비용 증가 ≤ 20% (이상이면 비용 통제 위반)
  - max 비용 ≤ agent_io_contract §9.1의 호출당 상한 1.5배
0점: 평균 비용 50% 이상 증가
5점: 비용 동일 또는 감소
```

### 2.4 latency_drift — 지연 드리프트

```
정의: 케이스별 평균 latency 변화.
측정: latest-baseline 대비 케이스당 latency_ms 평균 변화.
임계:
  - 평균 latency 증가 ≤ 30%
  - p95 latency ≤ agent_io_contract §14 타임아웃의 80%
0점: 평균 latency 100% 이상 증가
5점: 동일 또는 개선
```

### 2.5 rag_recall_at_5 — RAG recall@5

```
정의: RAG 검색이 관련 chunk를 top 5에 노출하는 비율.
측정 (rag_data_contract §6.3, §12.3):
  - 케이스에 expected_chunk_ids가 있을 때만 적용
  - recall@5 = (expected ∩ top5) / |expected|
  - GS-007이 주 대상
임계: recall@5 ≥ 기존 베이스라인 - 5% (rag_data §6.3)
0점: 20% 이상 하락
5점: 동일 또는 개선
```

---

## 3. 입력 / 출력 형식

### 3.1 실행 입력

```yaml
run_id: uuid
trigger:
  - "pr"                          # PR 별 자동
  - "nightly"                     # 야간 배치
  - "prompt_version_bump"         # major / minor 시
  - "manual"                      # 수동 트리거
mode: fast | full | batch         # golden_set §4.2
target_cases:                     # 지정 시 그 케이스만, 미지정 시 모드별 기본
  - "GS-001"
  - "GS-005"
environment:
  model_override: null | "gpt-4o-mini"
  temperature_override: 0.1
  seed: null | integer
```

### 3.2 실행 출력 (요약)

```yaml
run_id: uuid
timestamp: ISO8601
total_cases: 11
pass: 10
fail: 1
error: 0
case_pass_rate: 0.91
scores:
  case_pass_rate: 0~5
  baseline_diff: 0~5
  cost_drift: 0~5
  latency_drift: 0~5
  rag_recall_at_5: 0~5
regression_avg: 0~5
verdict: pass | fail
blockers:
  - { case_id: "GS-005", reason: "..." }
report_url: "eval/regression_results/2026-05-26-{run_id}-summary.md"
```

---

## 4. 자동 평가 vs 수동 평가

본 문서는 **자동 평가 주도**. 운영자는 결과 검토 + 새 케이스 추가만 담당.

```
자동:
  - 케이스 실행 (병렬, mock RAG 가능)
  - passing_criteria 검증
  - baseline diff 계산
  - 비용 / latency 측정
  - jsonl 결과 기록
  - summary.md 리포트 생성

수동:
  - 새 케이스 추가 / 수정 (golden_set §6)
  - 베이스라인 갱신 승인 (verdict=fail이지만 변경이 의도된 경우)
  - 누적 결과 회고 (meta-retrospective)
```

---

## 5. 임계값

```
verdict 결정:
  - 모든 차원 ≥ 3 AND case_pass_rate (P0 100%): pass
  - 1 차원이라도 < 3 OR P0 < 100%: fail (PR 머지 차단)

특수 게이트 (PR 머지 차단):
- P0 1개라도 실패: 즉시 차단
- baseline_diff에서 회귀 (validation true→false) 1건: 차단
- cost_drift > 50% 증가: 차단 + 운영자 확인
- 보안 회귀 (GS-010 등): 즉시 차단 + 운영자 알림

prompt-version-review Skill 절차:
- major bump: full mode 100% 회귀 필수
- minor bump: P0 + P1 회귀
- patch bump: P0 회귀
```

---

## 6. 실행 절차

### 6.1 CI 통합

```
GitHub Actions trigger:
  - on: pull_request (paths: docs/contracts/**, ai_system/**, eval/golden_set.md)
  - on: schedule (cron: '0 17 * * *' = 02:00 KST)
  - on: workflow_dispatch (manual)

순서:
  1. pre-flight: golden_set.md 파싱, 케이스 N개 추출
  2. 모드 결정 (fast / full / batch)
  3. 케이스별 LLM 실행 (병렬, 동시 5개)
  4. passing_criteria 자동 검증
  5. latest-baseline.jsonl과 diff
  6. jsonl + summary.md 생성
  7. verdict 결정
  8. PR 코멘트 자동 게시 + 머지 차단 결정
```

### 6.2 베이스라인 갱신

```
의도된 변경 (예: prompt 개선) 시:
  1. PR 본문에 [baseline-update] 태그
  2. 1차 회귀 fail 확인 (의도된 변경이므로 정상)
  3. 운영자 승인 (PR review)
  4. latest-baseline.jsonl을 새 결과로 덮어쓰기 (CI 자동)
  5. 다음 PR부터 새 baseline 기준 비교

비의도 회귀 시:
  1. PR 머지 차단 유지
  2. 케이스별 원인 분석
  3. prompt 또는 contract 수정
  4. 재실행 → 통과 시 머지
```

### 6.3 결과 보존

`golden_set.md` §5.3과 동일:

```
- raw jsonl: 90일
- summary.md: 1년
- latest-baseline.jsonl: 1개만 유지
- 보안 회귀: 3년
```

---

## 7. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §19 (회귀 평가)
  - rag_data_contract.md §6.3, §12.3 (recall@5 측정)
  - agent_io_contract.md §9 (비용 상한)

Skill:
  - eval-run (회귀 실행)
  - prompt-version-review (prompt 변경 시 회귀 강제)
  - contract-change (contract 변경 시 회귀)
  - meta-retrospective (누적 회귀 결과 회고)

연관 파일:
  - eval/golden_set.md (케이스 정의)
  - eval/regression_results/ (결과 보관)
```

---

## 8. Open Questions

1. CI 비용 — full mode 야간 배치는 ~$0.5 / 회. 월 ~$15.
2. mock RAG vs 실제 RAG — 실제는 비싸지만 정확, mock은 빠르지만 RAG ETL 변경 회귀 어려움.
3. seed 고정 가능한 모델 — gpt-4o-mini는 seed 지원, claude는 부분 지원.
4. 새 케이스 추가 시 즉시 baseline 포함 vs 1주일 관찰 후 — 현재 즉시 포함.
5. P2 케이스의 머지 차단 정책 — golden_set Open Question §8.4와 동일.
6. 회귀 실패 시 자동 rollback — 현재 운영자 수동, Phase 2+ 자동화 검토.
