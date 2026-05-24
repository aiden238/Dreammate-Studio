---
name: eval-design
description: |
  평가 체계 자체를 설계할 때 사용한다 (≠ eval-run 실행). 새 평가 차원이
  필요하거나, golden_set을 확장하거나, Critic Agent의 점수 체계를 변경할 때
  트리거한다. 측정 metric의 정의·rubric·golden_set 변경 제안서 작성을 담당한다.
  키워드: "eval 설계", "golden_set 확장", "rubric 설계",
  "evaluation framework", "평가 체계 설계", "평가 차원 추가".
applies_to: [claude]
phase: [phase-6, phase-10, ongoing]
related_contracts:
  - docs/contracts/output_schema.md
related_state:
  - eval/golden_set.md
  - eval/video_planning_eval.md
  - eval/human_review_rubric.md
version: v1.0.0
---

# eval-design

평가 체계를 새로 정의하거나 확장할 때 사용하는 설계 절차. 평가 실행은 `eval-run`이 담당하므로 본 Skill은 "무엇을 어떻게 측정할지" 만 다룬다.

## 트리거 조건

- 새 평가 차원이 필요 (예: `brand_consistency`, `target_audience_fit`, `hook_strength`)
- golden_set 확장 (10 → 20 → 50 케이스)
- 새 Phase 진입 시 acceptance를 정량 측정할 방법이 필요
- Critic Agent 점수 체계(0~5, 가중치) 변경 제안
- human_review_rubric에 새 항목 추가 요청

## 사용하지 않는 경우

```
- 기존 평가 실행 (회귀 / A/B) → eval-run
- 단일 prompt 회귀만 → prompt-version-review
- 평가 결과의 액션 분석 → meta-retrospective
- 평가 데이터 누출 / PII 검사 → security-review
```

## 절차

### 1. 현재 평가 자산 로드

```
1. eval/golden_set.md
2. eval/video_planning_eval.md
3. eval/human_review_rubric.md
4. (있다면) eval/design_reviews/
```

각 평가가 어떤 차원을 다루는지 표로 정리한다.

### 2. 부족한 차원 식별

다음 체크리스트로 누락 점검:

| 차원 | 측정 대상 | 현재 상태 |
|---|---|---|
| 형식 정합 | output_schema 일치 | ? |
| 사실성 | LLM Wiki / RAG 일치 | ? |
| 브랜드 정합 | brand_memory와 충돌 없음 | ? |
| 타겟 적합 | 페르소나·연령대 매핑 | ? |
| 광고 표현 | 차단 단어 회피 | ? |
| 다양성 | 3 후보 간 차별성 | ? |
| 비용/지연 | 토큰·응답시간 | ? |

`?` 인 칸이 본 Skill의 작업 대상.

### 3. metric 정의

각 새 차원에 대해:

- **정량 metric**: 0~1 또는 0~5 스칼라
- **계산 방법**: 자동 (LLM-as-judge) / 규칙 / 사람
- **임계값**: PASS / WARN / FAIL 경계
- **회귀 허용 폭**: 직전 버전 대비 -X% 이상이면 FAIL

LLM-as-judge를 사용한다면 judge prompt 초안도 함께 작성 (`ai_system/prompts/judge_drafts/`).

### 4. golden_set 변경 제안

확장 시 다음을 명시:

```
- 추가 케이스 수
- 케이스 선정 기준 (브랜드/도메인/타겟 다양성)
- 각 케이스의 expected fields (positive / negative)
- 출처 (실데이터 / 합성)
```

PII / 저작권 위험은 `security-review` 트리거.

### 5. human_review_rubric 반영

자동 측정으로 잡히지 않는 차원은 사람 rubric에 추가:

- 0~5 점수 + 1줄 정성 메모
- 분기별 샘플 수 (최소 N 케이스)

### 6. eval-run 명세 정리

새 차원을 `eval-run`이 실행할 수 있도록 다음을 갱신 제안:

- `eval/video_planning_eval.md` 의 실행 표
- 임계값과 회귀 허용 폭
- 출력 형식 (logs/evals/{date}/...)

### 7. contract-change 절차

평가 체계 변경은 contract와 동일 수준으로 다룬다 → `contract-change` Skill 트리거. 변경 제안서를 `docs/contract_changes/proposals/eval_design_{date}.md`에 작성.

## 출력 형식

```
[eval-design 결과]
새 차원       : brand_consistency
metric        : LLM-as-judge 0~1 (judge prompt 초안 첨부)
임계값        : PASS >= 0.75 / WARN 0.6~0.75 / FAIL < 0.6
회귀 허용 폭  : -5%p
golden_set    : 케이스 +8 (브랜드 3종 × 도메인 2종 + edge 2)
human rubric  : §4에 "brand voice 일치도" 항목 추가
eval-run 갱신 : video_planning_eval.md §5 실행표에 1행 추가
contract-change: proposals/eval_design_2026-05-24.md 작성됨
```

## 금지 사항

- 평가 실행 수행 (이건 `eval-run`)
- golden_set 파일 직접 수정 (제안서만)
- judge prompt를 prompt_registry에 직접 추가 (`prompt-version-review` 절차)
- 사용자 동의 없이 임계값을 임의 조정

## 자주 발생하는 실수

1. **차원 중복**: 기존 차원과 의미가 겹치는 새 차원을 추가. 항상 §1 표로 중복 확인.
2. **임계값 근거 부재**: 임의의 0.75를 적음. 최소 5케이스 베이스라인 근거를 함께.
3. **judge prompt만 만들고 회귀 폭 누락**: 임계값은 정의했지만 직전 버전 대비 허용 폭이 빠지면 회귀 감지 불가.
4. **사람 rubric 미반영**: 자동만 추가하고 사람 rubric을 안 건드림. 정성 차원은 반드시 사람 항목도.

## 종료 조건

- 새 차원/케이스가 `proposals/eval_design_{date}.md`에 정리됨
- judge prompt 초안 또는 자동 룰이 첨부됨
- `eval-run`이 새 차원을 실행 가능하도록 video_planning_eval.md 갱신 제안 포함
- `contract-change` Skill로 라우팅됨
