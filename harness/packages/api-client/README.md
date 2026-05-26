# api-client

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 130
last_updated: 2026-05-26
```

## Why Placeholder?

API 스펙(OpenAPI/JSON Schema)이 자동 생성되기 전까지 클라이언트 코드
구조를 확정할 수 없다. Phase 1 API 구현 완료 후 자동 생성 도입 시 작성한다.

## Scope (TBD)

본 패키지가 다룰 범위:
- `api_contract.md` 기반 TypeScript API client 자동 생성 (openapi-typescript 등)
- Next.js 앱 (`apps/web/`) 에서 사용하는 공통 API 호출 함수
- 외부 SDK 연동용 타입 안전 래퍼 제공
- 인증 토큰 자동 주입 (Authorization 헤더 처리)
- 에러 응답 통일 처리 (`error_response_contract.md` 기반)
- 재시도(retry) 및 타임아웃 정책 내장
- 테스트용 mock 클라이언트 제공

## Known Dependencies (when filled in)

- `docs/contracts/api_contract.md` — API 스펙 원천 (자동 생성 소스)
- `docs/contracts/tech_stack_contract.md` — TypeScript 버전, 모노레포 설정
- `packages/shared-types/README.md` — 공유 타입 의존
- `docs/contracts/error_response_contract.md` — 에러 처리 통일
- Next.js 앱 (`apps/web/`) — 주 소비자
- OpenAPI 자동 생성 도구 (openapi-typescript 또는 동등 도구)

## Fill-In Trigger

다음 조건 충족 시 본 패키지 작성 착수:
- Phase 1 FastAPI API 구현 완료 (최소 5개 엔드포인트)
- OpenAPI/JSON Schema 자동 생성 도입 결정 및 설정 완료

## 예시 사용법 (fill-in 시 참고)

```typescript
// 자동 생성된 client 사용 예시
import { createApiClient } from '@dreammate/api-client';

const client = createApiClient({ baseUrl: process.env.API_URL });

const { data, error } = await client.plans.create({
  intent: '뷰티 브랜드 제품 소개 영상',
  mode: 'quick',
});
```

## Related Skill / Phase

- Skill: N/A (자동 생성 기반)
- Phase: 1+
- 책임자: AI / 운영자
