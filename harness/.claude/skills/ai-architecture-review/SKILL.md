---
name: ai-architecture-review
description: |
  AI 시스템 전체 아키텍처 (MOA Lite, RAG Lite, orchestration, cost/fallback
  policy)를 정기적으로 검토한다. Phase 7/8 진입, 새 agent 추가, orchestration
  policy 변경 제안, 분기별 정기 검토 시점에 사용한다. 큰 아키텍처 결정은
  multi-llm-validation 으로 보강한다.
  키워드: "AI 아키텍처 검토", "MOA review", "RAG 구조 검토",
  "orchestration review", "AI 시스템 점검", "agent 추가 검토".
applies_to: [claude]
phase: [phase-7, phase-8, phase-11, ongoing]
related_contracts:
  - docs/contracts/agent_io_contract.md
  - docs/contracts/output_schema.md
related_state:
  - ai_system/architecture.md
  - ai_system/orchestration/
  - ai_system/agents/
  - ai_system/prompts/prompt_registry.md
version: v1.0.0
---

# ai-architecture-review

AI 파이프라인 전체의 구조적 일관성·정책 준수·확장성을 한 번에 점검하기 위한 검토 절차. 단일 agent 점검은 `agent-io-check`로, 단일 prompt 변경은 `prompt-version-review`로 라우팅된다.

## 트리거 조건

- Phase 7 진입 (RAG Lite 본격 구현 시작)
- Phase 8 진입 (MOA Lite 본격 구현 시작)
- 새 agent 추가 검토 (Intent/Planner/Critic/Rewriter 외)
- orchestration policy (`moa_policy.md`, `cost_control_policy.md`, `fallback_policy.md`) 변경 제안
- 분기 정기 검토 (3개월 주기, Phase 11 이후)
- 사용자가 "AI 구조 한 번 봐줘" / "MOA 흐름 점검" 요청

## 사용하지 않는 경우

```
- 단일 agent IO 정합 검사 → agent-io-check
- 단일 prompt 버전 검토 → prompt-version-review
- 평가 차원 자체의 설계 → eval-design
- RAG 데이터 구조만 → rag-design
```

## 절차

### 1. 입력 자료 로드

순서대로 읽는다:

1. `ai_system/architecture.md` — 전체 다이어그램, 컴포넌트 책임
2. `ai_system/orchestration/flow.md` — Intent → Planner → Critic → Rewriter 흐름
3. `ai_system/orchestration/moa_policy.md` — Critic revise 정책 (최대 2회)
4. `ai_system/orchestration/cost_control_policy.md` — 모델 라우팅·token 한도
5. `ai_system/orchestration/fallback_policy.md` — 부분 결과 보존 정책
6. `knowledge/rag/retrieval_policy.md` + `promotion_rule.md` — RAG 정합
7. `docs/contracts/agent_io_contract.md` — 외부 인터페이스 진실

전체를 한꺼번에 로드하지 말고 검토 항목별로 슬라이스해 읽는다.

### 2. MOA 흐름 점검

다음을 한 줄씩 확인:

```
- Intent → Planner: input/output 호환?
- Planner → Critic: plan 후보 3개가 그대로 전달?
- Critic → Rewriter: revise 트리거 조건 명확? (점수 threshold)
- Rewriter → 사용자: 최종 schema가 output_schema.md와 일치?
```

### 3. 정책 준수 검사

| 정책 | 확인 항목 |
|---|---|
| Critic revise 최대 2회 | 무한 루프 차단 코드/조건 존재 |
| cost_control_policy | 토큰 한도, 모델 라우팅 (4o-mini 기본, 4o 일부) |
| fallback_policy | 단일 agent 실패 시 부분 결과 노출 경로 |
| RAG isolation | brand_id별 격리, 타 brand 데이터 누출 차단 |
| 광고 표현 차단 | 단어 필터 위치(Intent 또는 Critic) |
| PII / 인젝션 차단 | Step 1, Step 2 자동 검사 존재 |

### 4. 확장성 / 리스크 점검

- 새 agent 추가 시 영향 받는 contract 수 (작을수록 좋음)
- prompt 변경 폭주 시 회귀 비용
- RAG 소스 추가 시 격리/품질 검사 자동화 정도
- Phase 21+ Custom RAG 마이그레이션 경로

### 5. 큰 결정은 multi-llm-validation

다음 중 하나라도 해당하면 즉시 `multi-llm-validation` Skill을 트리거:

- 새 agent 추가
- orchestration policy 변경
- 모델 라우팅 룰 변경 (4o ↔ 4o-mini)
- RAG isolation 정책 완화

### 6. 보고서 작성

`meta/architecture_reviews/{date}.md` 또는 `meta/proposals/`에 다음 구조로 정리:

```
- 강점 (현행 유지)
- 약점 (개선 필요)
- 리스크 (방치 시 위험)
- 누락 (명시 필요)
- 권장 액션 (각 항목별 후속 Skill 명시)
```

### 7. 후속 라우팅

- contract 변경 필요 → `contract-change`
- prompt 변경 필요 → `prompt-version-review`
- RAG 구조 변경 → `rag-design`
- 비용 정책 변경 → `cost-review`
- 큰 결정 → `multi-llm-validation`

## 출력 형식

```
[ai-architecture-review 결과]
검토 범위 : MOA Lite + RAG Lite + orchestration (Phase 7 진입)
강점      : Critic revise 2회 정책 명확, fallback 부분 결과 노출 경로 존재
약점      : cost_control_policy의 토큰 한도가 agent별로 분리 안 됨
리스크    : RAG isolation이 prompt context 주입 시점에만 적용 → retrieval 단계 추가 필요
누락      : Rewriter 실패 시 fallback이 "이전 plan" 인지 "원본 plan_options" 인지 미정
권장 액션 :
  - cost-review 트리거 → agent별 토큰 한도 정의
  - contract-change → fallback_policy §3 명확화
  - multi-llm-validation → "agent별 비용 한도 분리" 결정 보강
```

## 금지 사항

- 단일 agent / 단일 prompt 디테일 검토 (각 전용 Skill로)
- 구현 코드 직접 수정 (검토만)
- contract 직접 수정 (`contract-change` 절차)
- 큰 결정을 단독 판단 (반드시 multi-llm-validation 권장)

## 자주 발생하는 실수

1. **다이어그램만 보고 OK 처리**: 정책 파일(`moa_policy.md`, `cost_control_policy.md`)을 안 읽고 흐름도만 확인하면 누락이 생긴다.
2. **확장성 검토 누락**: 현재만 보고 Phase 21+ 영향을 안 봄. Custom RAG 마이그레이션 경로는 항상 한 줄 메모.
3. **multi-llm-validation 생략**: 큰 결정을 단독 판단. 비용 절감 의도가 결과 손실로 이어짐.
4. **권장 액션이 모호**: "개선 필요"로 끝내지 말고 후속 Skill 이름을 명시.

## 종료 조건

- 보고서가 `meta/architecture_reviews/` 또는 `meta/proposals/`에 저장
- 모든 약점·리스크 항목에 후속 Skill이 매핑됨
- 큰 결정 항목이 있으면 `multi-llm-validation` 트리거 완료
