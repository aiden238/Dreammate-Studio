# Claude 교차검증 프롬프트

너는 AI SaaS 제품 기획자, 소프트웨어 아키텍트, RAG/MOA 설계자, 프론트 UX 리뷰어, 하네스 엔지니어의 관점으로 이 프로젝트를 교차검증한다.

## 검토 대상

영상기획 AI 에이전트 플랫폼.

한 줄 정의:

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤, 검증 에이전트가 기획 품질을 평가·개선하는 영상기획 특화 AI 에이전트.

## 검토 요청

1. 현재 기획의 부족한 부분
2. 하네스 구조의 장점과 단점
3. 과도한 문서화 또는 누락된 문서
4. Phase 1 진입 전 반드시 보강할 요소
5. design.md 구조의 적절성
6. RAG/MOA 구조의 현실성
7. 사용자 데이터 자가개선 구조의 위험
8. LLM 보안과 개인정보 리스크
9. 기술 스택 전환 경계의 적절성
10. 커스텀 Skills의 우선순위

## 출력 형식

```md
# Claude Cross Validation Result

## 1. Overall Score
## 2. Strong Points
## 3. Weak Points
## 4. Structural Risks
## 5. Missing Documents
## 6. Over-engineered Parts
## 7. Must Fix Before Phase 1
## 8. Should Defer
## 9. Recommended Phase 1 Scope
## 10. Final Recommendation
```
