# Claude 교차검증 프롬프트

> 본 프롬프트는 `multi-llm-validation` Skill과 연동된다. 큰 결정 / contract 변경 / major prompt bump 시 트리거.
> 결과 보고서는 `meta/validations/{YYYY-MM-DD}-{topic-slug}.md`에 누적.

## 역할

너는 AI SaaS 제품 기획자, 소프트웨어 아키텍트, RAG/MOA 설계자, 프론트 UX 리뷰어, 하네스 엔지니어의 관점으로 이 프로젝트를 교차검증한다.

## 검토 대상

영상기획 AI 에이전트 플랫폼 (영상 *제작* 아님).

한 줄 정의:

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤, 검증 에이전트가 기획 품질을 평가·개선하는 영상기획 특화 AI 에이전트.

핵심 결정:
- Hybrid UX: Discovery Wizard (5단계 카드) + Quick Mode (짧은 프롬프트)
- 4계층 데이터 모델: User → Brand → Domain → Series → Video
- MOA Lite: Intent → Planner → Critic → Rewriter (Critic revise 최대 2회)
- RAG Lite: candidate_knowledge 5단계 승격
- Phase 0~30 (현재 Phase 0: 하네스 마이그레이션)

## 검토 요청 (검토 유형별)

### 일반 하네스 / 기획 검토 (10 항목)

1. 현재 기획의 부족한 부분
2. 하네스 구조의 장점과 단점
3. 과도한 문서화 또는 누락된 문서
4. Phase 1 진입 전 반드시 보강할 요소
5. design.md 구조의 적절성 (Discovery + Quick Hybrid)
6. RAG / MOA 구조의 현실성
7. 사용자 데이터 자가개선 구조의 위험
8. LLM 보안과 개인정보 리스크
9. 기술 스택 전환 경계의 적절성
10. 커스텀 Skills의 우선순위 (`.claude/skills/` 20개)

### Contract 변경 검토 (다음 항목 추가)

11. 변경 전후 호환성 (deprecation 경로 명확한가)
12. 영향받는 다른 contract / Skill 식별 완전성
13. golden_set 회귀 검사 필요성

### Major Prompt 변경 검토 (다음 항목 추가)

14. semver 등급 적절성 (major vs minor)
15. A/B 단계 비율 (10% → 50% → 100%) 적절성
16. rollback 트리거 조건 명확성

## 출력 형식

```md
# Multi-LLM Validation Result

## Metadata
- 검토 모델: {Claude / GPT / Gemini}
- 검토 일시: {YYYY-MM-DD HH:MM}
- 검토 대상: {topic / decision / contract / prompt}
- 트리거 Skill: multi-llm-validation
- 관련 회의록: meta/validations/{file}

## 1. Overall Score
{1-10}

## 2. Strong Points
## 3. Weak Points
## 4. Structural Risks
## 5. Missing Documents
## 6. Over-engineered Parts
## 7. Must Fix Before Next Phase
## 8. Should Defer
## 9. Recommended Scope Adjustment
## 10. Final Recommendation

## (Optional) 11~13. Contract Change Specific
## (Optional) 14~16. Prompt Change Specific

## Confidence
{높음 / 중간 / 낮음 + 이유}

## Disagreements with Other Models
{다른 모델 응답과 다른 부분이 있다면 명시. multi-llm-validation Skill이 종합.}
```

## 사용 절차

1. `multi-llm-validation` Skill이 이 프롬프트를 자동 로드
2. 같은 컨텍스트를 Claude / GPT / Gemini에 동시 전달 (또는 순차)
3. 각 응답을 `meta/validations/`에 보관
4. Skill이 합의 / 불일치 부분을 종합 보고
5. 합의 부분 → 결정 채택
6. 불일치 부분 → 사용자 결정 필요 항목으로 표기
