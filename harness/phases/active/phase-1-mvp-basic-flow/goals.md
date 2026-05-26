# Phase 1 — Goals

> Phase: 1 / MVP 기본 플로우
> Status: active
> Started: 2026-05-26

---

## 핵심 목표

영상기획 AI 에이전트의 **최소 가동 가능한 단일 흐름**을 구현한다.

```
사용자 입력
→ Intent Agent (영상기획 외 차단)
→ 부족 정보 질문 (Quick Mode 기준: 1–2 질문)
→ 한 줄 기획 방향 승인
→ RAG Lite 최소 검색 (pgvector fallback 포함)
→ 기획안 1개 생성 (P-006 plan_candidates 1개)
→ Critic Agent 평가 (revise 없이 1회 평가만)
→ VideoProject 저장 (Supabase)
```

Phase 1은 **기능 완성도보다 흐름 증명**이 목적이다.  
3개 plan, Critic revise 2회, Brand Memory 추출 등은 Phase 4+ 로 미룬다.

---

## 세부 목표

### G1. Next.js PWA 진입점
- `/` 페이지에서 텍스트 입력 가능
- `/plan` 페이지에서 생성 결과 표시
- 4단계 progress stepper 표시

### G2. FastAPI generate endpoint
- `POST /api/v1/generate` endpoint 동작
- Input → Intent → Direction → RAG → Plan → Critic → Output 순서 처리
- output_schema v1.0 준수

### G3. Supabase 기본 연결
- `video_projects` 테이블에 결과 저장
- 인증 없이 동작 (Phase 5에서 Auth 추가)
- `.env.local` 기반 환경변수

### G4. Intent Filter 동작
- 영상기획 외 입력 → `INV-001` 오류 반환
- 테스트 케이스: GS-001 ~ GS-003 (golden_set)

---

## 우선순위

```
G2 (API 뼈대) > G1 (UI 진입) > G3 (DB 저장) > G4 (Intent Filter)
```

DB 저장 없이도 흐름 확인 가능 → G3은 G2 이후 추가.

---

## 관련 문서

- `scope.md` — 작업 범위 상세
- `acceptance.md` — 완료 기준
- `docs/contracts/api_contract.md` — POST /api/v1/generate 스펙
- `docs/contracts/agent_io_contract.md` — 4 Agent IO
- `docs/contracts/output_schema.md` — 출력 스키마
- `docs/contracts/db_schema.md` — video_projects 테이블
- `ai_system/orchestration/flow.md` — 전체 플로우
