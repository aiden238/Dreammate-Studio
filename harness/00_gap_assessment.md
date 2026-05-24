# 현재 기획 및 하네스 객관적 점검

## 1. 전체 판단

현재 기획은 일반적인 AI 스크립트 생성기보다 구조적으로 깊다. LLM Wiki, RAG Lite, MOA Lite, Critic Agent, 사용자 피드백 저장, Phase 기반 하네스를 함께 고려했다는 점은 강점이다.

다만 지금 상태는 **아키텍처와 하네스 구조는 강하지만, 구현 직전 필요한 세부 계약·평가 데이터셋·보안/동의 정책이 아직 약한 상태**다.

## 2. 강점

### 2.1 포지션이 명확함

이 프로젝트는 영상 제작 AI가 아니라 영상기획 AI다. 자동 편집/생성 서비스와 직접 경쟁하지 않고, 제작 전 의사결정 영역을 공략한다.

### 2.2 하네스 구조가 장기 프로젝트에 적합함

`product/`, `ai_system/`, `knowledge/`, `docs/contracts/`, `eval/`, `meta/`, `phases/`를 분리한 것은 적절하다.

특히 다음 원칙은 장점이 크다.

- AGENTS.md / CLAUDE.md 라우터화
- archive 기본 참조 금지
- contracts 직접 수정 금지
- meta는 자동 수정이 아니라 개선 제안 구조
- active Phase만 깊게 관리

### 2.3 기술 전환 전략이 현실적임

초기에는 Next.js PWA + FastAPI + Supabase/PostgreSQL/pgvector로 빠르게 검증하고, 후반에 Expo, Spring Boot, Custom RAG, LangGraph로 확장하는 전략은 현실적이다.

## 3. 부족한 부분

### 3.1 Output Schema가 더 엄격해야 함

AI 출력이 조금만 흔들려도 프론트/저장/검증이 깨질 수 있다. `output_schema.md`, `agent_io_contract.md`, `error_response_contract.md`를 Phase 1 전에 작성해야 한다.

### 3.2 Golden Set 부족

Critic Agent의 품질 판단을 검증하려면 좋은/나쁜 예시 데이터셋이 필요하다. 없으면 점수는 그럴듯하지만 실제 품질 개선은 어렵다.

### 3.3 사용자 데이터 승격 정책 위험

사용자 입력과 피드백을 바로 공통 RAG에 넣으면 개인정보, 사업 아이디어, 낮은 품질 데이터가 섞일 수 있다.

필수 흐름:

```text
Raw User Log
→ Candidate Knowledge
→ Privacy Filter
→ Quality Filter
→ Eval
→ Human/Rule Approval
→ Global Knowledge
```

### 3.4 LLM 보안 설계 미흡

필요 항목:

- prompt injection 방어
- RAG data poisoning 방어
- 비용 폭주 방지
- system prompt leakage 방지
- output schema validation

### 3.5 운영자 도구 계획이 약함

중기에는 최소 관리자 화면이 필요하다.

- 실패 요청 조회
- 비용 높은 요청 조회
- RAG 실패 사례 조회
- 후보 지식 승인/반려
- 프롬프트 버전 변경 기록

### 3.6 design.md는 필요하지만 화면 단위 세부화가 더 필요함

Phase 2 전에 `apps/web/page_map.md`, `apps/web/component_map.md`, 핵심 화면별 상태 정의가 필요하다.

## 4. 하네스 구조적 단점

### 4.1 초기 진입 장벽

문서 수가 많아 다른 모델이나 구현자가 어디서 시작할지 헷갈릴 수 있다. `00_START_HERE.md`와 `instruction_index/routes.yaml`이 중요하다.

### 4.2 contracts 과다화 위험

contracts가 많아지면 변경 비용이 커진다. Phase 1에서는 핵심 contracts만 active로 사용하고 나머지는 placeholder로 유지한다.

### 4.3 meta 과사용 위험

모든 실패를 meta로 보내면 실행 속도가 느려진다. 반복 실패 2회 이상 또는 구조 변경 필요 시에만 meta-retrospective를 실행한다.

### 4.4 30개 Phase 상세화 위험

30개 Phase는 지도 역할로 좋지만, 처음부터 상세화하면 문서 부채가 된다. active 1개만 상세, planned 2~3개만 중간 상세로 유지한다.

## 5. 단점보다 장점이 많은 부분

### AGENTS.md / CLAUDE.md 라우터 방식

장점이 더 크다. 지침 과부하를 막고, 모델별 역할을 분리하며, 필요한 문서만 참조하게 만든다.

### PWA 우선 전략

장점이 더 크다. 빠른 MVP 검증, 낮은 비용, 모바일 대응이 가능하다. 단, 공통 타입과 API client는 초기에 분리해야 한다.

### FastAPI 우선 전략

장점이 더 크다. AI/RAG 실험 속도가 빠르다. 단, 결제/권한/팀 기능이 커지면 Spring Boot 분리를 검토해야 한다.

## 6. Phase 1 전 최우선 보강

1. `docs/contracts/output_schema.md`
2. `docs/contracts/agent_io_contract.md`
3. `apps/web/design.md`
4. `eval/golden_set.md`
5. `docs/contracts/llm_security_contract.md`
6. `docs/contracts/user_consent_contract.md`
7. `docs/contracts/error_response_contract.md`
8. `phases/active/phase_1_mvp_basic_flow.md`
