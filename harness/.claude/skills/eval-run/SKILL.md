---
name: eval-run
description: |
  품질 평가(eval)를 실행할 때 사용한다. golden_set 회귀, 영상기획 품질 평가,
  hook 강도 평가, 사람 검토를 어떤 조합으로 어떤 순서로 돌릴지, 결과를
  어디에 저장하고 어떤 임계값에서 작업을 차단할지 강제한다.
  키워드: "eval 실행", "평가 돌려", "golden_set", "회귀 테스트", "regression",
  "품질 평가", "human review", "video_planning_eval".
applies_to: [agents]
phase: [phase-10, phase-11, ongoing]
related_contracts:
  - eval/golden_set.md
  - eval/video_planning_eval.md
  - eval/hook_quality_eval.md
  - eval/human_review_rubric.md
related_state:
  - eval/regression_results/
  - agent_io_logs
version: v1.0.0
---

# eval-run

평가는 통과/실패가 아니라 점수와 분포다. 어떤 평가를 언제 돌리고 결과를 어떻게 해석할지 절차로 고정한다.

## 트리거 조건

- Phase 종료 직전 acceptance 확인
- prompt-version-review 4단계 회귀 평가
- rag-update 5단계 승격 후 회귀 평가
- 사용자가 "품질 평가 돌려"
- 정기 모니터링 (주 1회)

## 평가 종류

### 1. golden_set 회귀

`eval/golden_set.md`의 정해진 케이스로 신구 시스템 비교.

용도:
- prompt 변경 후 품질 유지 확인
- RAG 변경 후 품질 유지 확인
- 모델 교체 후 품질 유지 확인
- 코드 리팩토링 후 동작 동일성 확인

### 2. 영상기획 품질 평가 (`video_planning_eval.md`)

생성된 영상기획안의 품질을 8차원으로 평가.

차원:
- intent_fit, target_clarity, hook_strength, message_clarity,
  structure, feasibility, brand_consistency, differentiation

용도: 신규 기획 생성 후 자동 평가, 일정 점수 미만이면 Critic이 revise 트리거

### 3. Hook 강도 평가 (`hook_quality_eval.md`)

후킹 문장만 따로 평가.

지표: 3초 시선 유지 추정, 정보 밀도, 호기심 유발, 광고적 표현 여부.

### 4. 사람 검토 (`human_review_rubric.md`)

자동 평가로 판정 어려운 case를 사람이 검토.

기준: 5점 척도 + 정성 코멘트.

### 5. 안전 평가 (`security_eval.md`의 자동 부분)

- 프롬프트 인젝션 차단율
- PII 마스킹 정확도
- 부적절 표현 차단율

## 절차

### 1. 평가 조합 결정

트리거 상황에 따라 어떤 평가를 돌릴지:

| 트리거 | 필수 평가 | 선택 평가 |
|---|---|---|
| Phase 종료 (프론트) | 회귀(UI 케이스) | - |
| Phase 종료 (AI) | golden_set + 영상기획 품질 | hook 평가 |
| prompt-version-review | golden_set + 영상기획 품질 | hook + 사람 검토 (major) |
| rag-update 승격 후 | golden_set (RAG 영향 케이스) | 영상기획 품질 |
| 정기 (주 1회) | golden_set | 영상기획 품질 |
| 사용자 요청 | 사용자가 명시한 것 | - |

### 2. 케이스 선정

전체 케이스를 다 돌리는 게 항상 좋은 건 아님:

```
변경 종류                  | 케이스 수
prompt patch              | 영향 prompt의 대표 5케이스
prompt minor              | 영향 prompt 전체 케이스
prompt major              | golden_set 전체
RAG 신규 추가             | RAG 사용하는 케이스 + 신규 chunk 관련 케이스
RAG 임베딩 모델 변경      | golden_set 전체
모델 교체                 | golden_set 전체 + 추가 사람 검토 10
정기 모니터링             | 무작위 샘플 30%
```

### 3. 실행

각 케이스를 모델에 입력하고 출력을 받음.

#### 동시 실행 vs 순차

- LLM 호출 제한 안에서 가능한 한 동시 실행
- rate_limit_policy.md 확인 후 batch 크기 결정
- 각 호출은 agent_io_logs에 prompt_version과 함께 기록

#### 비교 모드 (신구 비교 시)

```
case_001 → v1.0.0 결과 + v1.1.0 결과
case_002 → v1.0.0 결과 + v1.1.0 결과
...
```

### 4. 채점

#### 자동 채점

- schema 준수: 100% 필수
- 영상기획 품질: P-007(Critic) prompt로 8차원 자동 채점
- hook 강도: 별도 prompt로 자동 채점
- 다양성: 후보 간 cosine similarity

#### 사람 채점

`human_review_rubric.md`의 5점 척도로 검토자가 입력.

여러 검토자 시 평균 + 표준편차 기록. 표준편차 1.0 초과는 의견 불일치 케이스로 표시.

### 5. 결과 저장

`eval/regression_results/{trigger}_{YYYY-MM-DD-HHMM}.md`:

```markdown
# Eval Run: {trigger 식별자}

- 실행일: {YYYY-MM-DD HH:MM}
- 트리거: {phase-complete / prompt-version-review / ...}
- 케이스 수: {N}
- 비교 대상: {v1.0.0 vs v1.1.0 등}

## 요약 점수

| 지표 | 구버전 | 신버전 | 차이 |
|---|---|---|---|
| schema 준수율 | 100% | 100% | 0 |
| 영상기획 평균 (8차원) | 3.6 | 3.7 | +0.1 |
| Hook 강도 평균 | 3.4 | 3.8 | +0.4 |
| 다양성 (cos sim) | 0.32 | 0.31 | -0.01 |
| 평균 latency | 12.3s | 11.8s | -0.5s |
| 평균 토큰 (out) | 850 | 870 | +20 |
| 평균 비용 ($) | 0.0023 | 0.0025 | +9% |

## 차원별 분포
{각 차원 점수 분포 표}

## 케이스별 결과
{각 케이스 통과/실패, 점수 차이}

## 임계값 점검
- schema 준수율 < 100%: ❌ / ✅
- 평균 점수 변화 ±0.3 이내: ✅
- 비용 변화 +30% 이내: ✅
- latency 변화 +20% 이내: ✅

## 결정
{pass / fail / human_review_needed}

## 후속 액션
{필요한 후속 Skill 또는 phase}
```

### 6. 임계값 판정

자동 차단 임계값:

```
| 지표 | 임계값 | 위반 시 |
|------|--------|---------|
| schema 준수율 | < 100% | 즉시 fail, rollback |
| 평균 점수 하락 | > 0.3 | fail, 사람 검토 |
| 비용 증가 | > 30% | cost-review Skill 트리거 |
| latency 증가 | > 20% | 경고, 사용자 결정 |
| 다양성 하락 | > 0.1 | 경고, 사람 검토 |
| 광고 표현 검출 | > 5% | fail |
| 차단된 단어 검출 | > 0% | fail |
```

위반은 즉시 활성화 차단 + 사용자 알림.

### 7. golden_set 갱신

평가 도중 발견된 좋은/나쁜 예시는 golden_set에 추가 후보:

```
- 자동 평가가 잘못 판정한 케이스 → 사람 라벨 추가하고 golden_set에 추가
- 모델이 새로 만들어낸 흥미로운 패턴 → 좋은 예시로 추가
- 모델 실패 사례 → 나쁜 예시로 추가
```

이 갱신은 contract-change Skill을 통한다 (golden_set.md는 contract).

## 자주 발생하는 실수

1. **케이스 5개로 모든 변경 평가**: 통계적 의미 없음. major bump엔 골든셋 전체.
2. **자동 점수만으로 사람 검토 생략**: 정성 차원 (브랜드 톤, 자연스러움) 놓침.
3. **결과 저장 위치 통일 안 함**: 비교 분석 불가.
4. **임계값 위반 무시**: "이 정도는 괜찮을 거"가 누적되면 품질이 슬금슬금 떨어짐.
5. **prompt_version 같이 기록 안 함**: 어느 버전 결과인지 추적 안 됨.

## 다른 Skill과의 관계

```
prompt-version-review : 4단계에서 호출
rag-update            : 5단계 후속 회귀 평가
phase-complete        : 6단계 eval 결과 보관
cost-review           : 비용 임계값 위반 시 트리거
bug-triage            : 실패 케이스가 새 버그인지 분류
contract-change       : golden_set 갱신 시
```

## 종료 조건

- 모든 결과 저장 + 결정(pass/fail) 기록 → 정상 종료
- 임계값 위반 → 후속 Skill 위임 후 종료
- 사람 검토 대기 → 검토 완료 후 다시 종료 처리
