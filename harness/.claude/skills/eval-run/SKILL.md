---
name: eval-run
description: |
  품질 평가(eval) 체계의 설계와 실행을 모두 담당한다 (2026-06-21 구 eval-design 흡수, HIP-C).
  [실행] golden_set 회귀, 영상기획 품질 평가, hook 강도 평가, 사람 검토를 어떤
  조합으로 어떤 순서로 돌릴지, 결과를 어디에 저장하고 어떤 임계값에서 작업을 차단할지 강제한다.
  [설계] 새 평가 차원·rubric·golden_set 확장·Critic 점수 체계 변경 제안서 작성.
  키워드: "eval 실행", "평가 돌려", "golden_set", "회귀 테스트", "regression",
  "품질 평가", "human review", "video_planning_eval",
  "eval 설계", "golden_set 확장", "rubric 설계", "평가 체계 설계", "평가 차원 추가".
applies_to: [agents, claude]
phase: [phase-6, phase-9.5, phase-10, phase-11, ongoing]
related_contracts:
  - eval/golden_set.md
  - eval/video_planning_eval.md
  - eval/hook_quality_eval.md
  - eval/human_review_rubric.md
  - docs/contracts/output_schema.md
related_state:
  - eval/regression_results/
  - agent_io_logs
version: v1.1.0
---

# eval-run

평가는 통과/실패가 아니라 점수와 분포다. 어떤 평가를 언제 돌리고 결과를 어떻게 해석할지 절차로 고정한다.

> 정식화 이력: **Phase 9.5에서 first formal baseline으로 정식화**(golden_set 11 케이스 mock-deterministic runner + revise effect + 임계값 게이트, ADR-033)되었고, Phase 10+ 부터 반복 운영한다.
>
> **v1.1.0 (2026-06-21, HIP-C 흡수)**: 구 `eval-design` Skill을 흡수 — 이 Skill이 eval **설계**(차원/rubric/golden_set 제안)와 **실행**(회귀/품질/사람검토)을 모두 담당한다. 설계는 아래 "## 설계 모드", 실행은 기존 절차. applies_to=[agents, claude].

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

---

# 설계 모드 (구 eval-design 흡수, v1.1.0)

> 평가를 **실행**(위)이 아니라 **설계/확장**할 때 — 새 평가 차원, golden_set 확장, rubric/Critic 점수 체계 변경 — 의 절차. "무엇을 어떻게 측정할지"만 다루고, 실제 채점은 위 실행 절차가 담당한다. 산출물 = 제안서(직접 수정 금지).

## 설계 트리거

- 새 평가 차원 필요 (예: `brand_consistency`, `hook_strength`)
- golden_set 확장 (10 → 20 → 50 케이스)
- 새 Phase acceptance를 정량 측정할 방법 필요
- Critic Agent 점수 체계(0~5, 가중치) 변경 제안
- human_review_rubric 새 항목 추가

## 설계 절차

1. **현재 평가 자산 로드**: `eval/golden_set.md` · `video_planning_eval.md` · `human_review_rubric.md` (+ `eval/design_reviews/`) → 각 평가가 다루는 차원을 표로 정리.
2. **부족한 차원 식별**: 형식정합/사실성/브랜드정합/타겟적합/광고표현/다양성/비용·지연 체크리스트로 누락 점검.
3. **metric 정의**: 각 새 차원에 정량 metric(0~1 또는 0~5) + 계산법(LLM-judge/규칙/사람) + 임계값(PASS/WARN/FAIL) + 회귀 허용 폭. LLM-judge면 judge prompt 초안도 함께(`ai_system/prompts/judge_drafts/`).
4. **golden_set 변경 제안**: 추가 케이스 수·선정 기준(브랜드/도메인/타겟 다양성)·expected fields(positive/negative)·출처(실/합성). PII/저작권 위험은 `security-review` 트리거.
5. **human_review_rubric 반영**: 자동으로 안 잡히는 차원은 사람 rubric(0~5 + 1줄 메모 + 분기별 샘플 N).
6. **eval-run 실행표 갱신 제안**: 새 차원을 위 실행 절차가 돌릴 수 있게 `video_planning_eval.md` 실행표·임계값·출력형식 갱신 제안.
7. **contract-change 라우팅**: 평가 체계 변경 = contract 수준 → `contract-change` Skill. 제안서를 `docs/contract_changes/proposals/eval_design_{date}.md`에 작성.

## 설계 금지 사항

- 평가 **실행** 수행은 위 실행 절차로 (설계 모드는 제안만).
- golden_set 파일 직접 수정 금지 (제안서만).
- judge prompt를 prompt_registry에 직접 추가 금지 (`prompt-version-review` 절차).
- 사용자 동의 없이 임계값 임의 조정 금지.

## 설계 자주 발생하는 실수

1. **차원 중복**: 기존과 의미 겹치는 차원 추가 — §1 표로 중복 확인.
2. **임계값 근거 부재**: 임의 0.75 — 최소 5케이스 베이스라인 근거.
3. **회귀 폭 누락**: 임계값만 정의하고 직전 버전 대비 허용 폭 빠지면 회귀 감지 불가.
4. **사람 rubric 미반영**: 정성 차원은 반드시 사람 항목도.
