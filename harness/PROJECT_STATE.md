# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 하네스 구조와 기술 스택 방향 초안이 정리되었다.

## 확정 방향

- 영상 제작 AI가 아닌 영상기획 AI 에이전트
- 초기 MVP는 Next.js PWA + FastAPI + Supabase/PostgreSQL/pgvector
- RAG Lite와 MOA Lite를 MVP부터 일부 적용
- 영상 제작/편집/TTS/BGM/자동 업로드는 MVP 제외
- Phase 기반 구현 진행
- contracts, eval, meta, design.md 하네스 포함

## 현재 단계

```text
하네스 구조 확정
→ 기술 스택 방향 확정
→ MVP 범위 문서화
→ Phase 1 구현 지침 작성
→ 구현 시작
```

## 현재 Active Phase

`phases/active/phase_1_mvp_basic_flow.md`

## 주요 리스크

- output schema 불명확
- Golden Set 부족
- LLM 보안 지침 부족
- 사용자 데이터 승격 정책 미흡
- 프론트 상태/에러 UX 미흡
- 문서 수 과다로 인한 참조 혼란

## 다음 액션

Phase 1 구현 전에 contracts와 design.md의 최소 초안을 작성하고, Claude 등 다른 모델로 교차검증한다.
