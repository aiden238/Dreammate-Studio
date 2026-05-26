# smoke_test_checklist.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 90
last_updated: 2026-05-26
```

## Why Placeholder?

배포 환경(staging)이 구축되기 전까지 smoke test 항목의 실제 URL, 인증 토큰,
기대 응답값을 확정할 수 없다. Phase 1 첫 staging 배포 시 작성 착수한다.

## Scope (TBD)

본 파일이 다룰 범위:
- 헬스체크 엔드포인트 (GET /health, GET /ready) 응답 확인
- 핵심 API 엔드포인트 5개 이상 정상 응답 확인
- 인증 flow (로그인 → 토큰 발급 → 보호 API 접근) 동작 확인
- RAG retrieval 정상 동작 (최소 1건 검색 결과 반환)
- LLM 호출 정상 (Intent Agent → Planning Agent 순서 응답)
- output_schema 필드 존재 여부 기본 검증
- 응답 시간 기준 내 완료 (전체 흐름 p95 < 10s)

## Known Dependencies (when filled in)

- `backend/fastapi/README.md` — 엔드포인트 목록 및 스펙
- `docs/contracts/api_contract.md` — 기대 응답 구조
- `docs/contracts/output_schema.md` — 필드 검증 기준
- `qa-check` Skill — smoke test 실행 자동화
- staging 환경 URL 및 인증 정보 (Phase 1 배포 후 확정)
- CI/CD 파이프라인 (배포 후 자동 트리거)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 첫 staging 환경 배포 완료
- 최소 3개 API 엔드포인트 구현 완료

## 예시 smoke 항목 형식 (fill-in 시 참고)

```
## 헬스체크

- [ ] GET /health → 200 OK, {"status": "ok"}
- [ ] GET /ready → 200 OK (DB + RAG 연결 확인 포함)

## 핵심 흐름

- [ ] POST /api/v1/plans (Intent 입력) → 200 OK, plan_id 반환
- [ ] GET /api/v1/plans/{plan_id} → 200 OK, output_schema 구조 일치
- [ ] POST /api/v1/feedback → 200 OK

## RAG 확인

- [ ] GET /api/v1/search?q=뷰티 → 최소 1건 결과 반환
```

## Related Skill / Phase

- Skill: qa-check
- Phase: 1+
- 책임자: 운영자 / AI
