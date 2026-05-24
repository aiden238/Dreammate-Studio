# PHASE_REGISTRY

## 운영 원칙

- 전체 Phase는 큰 지도 역할을 한다.
- 현재 active Phase만 상세히 작성한다.
- planned는 다음 2~3개만 중간 상세화한다.
- archive는 기본 참조하지 않는다.

## Phase 목록

| Phase | 이름 | 상태 | 목적 |
|---|---|---|---|
| 0 | 하네스 초기화 | planned | 기본 구조 생성 |
| 1 | MVP 기본 플로우 | active | 입력→기획→검증→저장 흐름 구현 |
| 2 | design.md 기반 PWA 설계 | planned | 모바일 PWA 화면 구조 확정 |
| 3 | Next.js PWA 기본 UI 구현 | planned | 핵심 화면 구현 |
| 4 | FastAPI 기본 백엔드 구현 | planned | API 및 AI pipeline 뼈대 |
| 5 | DB/Auth 기본 구조 구현 | planned | Supabase/PostgreSQL 연결 |
| 6 | Output Schema + Agent IO 구현 | planned | AI 입출력 안정화 |
| 7 | RAG Lite 구현 | planned | 초기 지식 검색 |
| 8 | MOA Lite 구현 | planned | Intent/Planner/Critic/Rewriter |
| 9 | 결과 저장 + 피드백 저장 | planned | 사용자 선택/수정/반려 저장 |
| 10 | MVP 통합 테스트 | planned | MVP 전체 검증 |
| 11~20 | 서비스 안정화 | future | UX, eval, cost, fallback, 피드백 |
| 21~30 | 확장/고도화 | future | Spring, Expo, Custom RAG, LangGraph |

## 배포 테스트 게이트

- Deploy Test A: Local Smoke Test
- Deploy Test B: Staging 배포
- Deploy Test C: 내부 알파 테스트
- Deploy Test D: Beta Staging
- Deploy Test E: 제한 사용자 테스트
- Deploy Test F: 비용/성능 테스트
- Deploy Test G: Production Readiness
