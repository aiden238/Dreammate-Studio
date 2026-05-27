# Phase 1 — Acceptance Criteria

> 아래 항목이 **모두** 통과해야 Phase 1 완료. 미달 시 phase-complete 트리거 불가.

---

## A1. End-to-End 흐름 동작

```
체크: 텍스트 입력 → API 호출 → 기획안 JSON 반환이 로컬에서 end-to-end 동작
방법: Postman 또는 curl로 POST /api/v1/generate 직접 호출
기준: HTTP 200 + output_schema v1.0 구조 준수 응답
```

- [ ] POST /api/v1/generate 200 응답
- [ ] `meta.schema_version == "1.0"` 존재
- [ ] `body.plan_candidates` 배열 길이 1 이상
- [ ] `body.critic_evaluation` 존재

---

## A2. Intent Filter 동작

```
체크: 영상기획 외 입력 차단
기준: "오늘 날씨 알려줘" 입력 시 INV-001 오류 반환
```

- [ ] 비관련 입력 → `error.code == "INV-001"` 반환
- [ ] 영상기획 관련 입력 → 정상 처리

---

## A3. RAG Lite 검색 동작

```
체크: RAG 검색 결과 또는 fallback이 output에 반영
기준: body.rag_references 배열 존재 (빈 배열이면 fallback 사용 표시)
```

- [ ] `body.rag_references` 필드 존재
- [ ] pgvector 연결 실패 시 fallback 동작 (오류 없이 빈 배열 반환)

---

## A4. Supabase 저장

```
체크: 생성된 기획안이 video_projects 테이블에 저장
기준: 생성 후 Supabase 대시보드에서 row 확인
```

- [ ] `video_projects` 테이블에 row 생성됨
- [ ] `plan_candidates` 테이블에 row 생성됨

---

## A5. Frontend 진입점 동작

```
체크: Next.js 로컬 서버에서 UI 접근 가능
기준: http://localhost:3000 에서 입력 페이지 렌더링
```

- [ ] `npm run dev` 후 http://localhost:3000 접근 가능
- [ ] 텍스트 입력 + 제출 버튼 존재
- [ ] 제출 후 `/plan` 페이지로 이동 + 결과 표시

---

## A6. output_schema 준수

```
체크: API 응답 구조가 docs/contracts/output_schema.md v1.0 기준 충족
방법: golden_set GS-001 케이스로 검증
```

- [ ] GS-001 입력으로 schema 검증 통과
- [ ] `meta`, `body`, `validation` 3 섹션 모두 존재

---

## A7. 환경변수 문서화

```
체크: .env.example 파일로 설정 방법 문서화
기준: README 또는 .env.example만 보고 로컬 실행 가능
```

- [ ] `apps/web/.env.local.example` 존재
- [ ] `backend/fastapi/.env.example` 존재
- [ ] 필수 변수 (OPENAI_API_KEY, SUPABASE_URL, SUPABASE_ANON_KEY) 명시

---

## A8. MVP Non-Goals 미포함

```
체크: scope/non_goals.md의 영구 제외 항목이 코드에 없음
방법: 코드 검색 (TTS, upload, video_edit 키워드)
```

- [ ] 자동 영상 생성 / 편집 코드 없음
- [ ] TTS / BGM / 자막 코드 없음
- [ ] 결제 코드 없음

---

## Done Definition

위 A1~A8 모두 통과 + git commit 1개 이상 + 로컬 smoke test 통과.

## 이후 Phase

**Phase 2. design.md 기반 PWA 설계** — Discovery Wizard + Quick Mode 분기 화면 설계.
