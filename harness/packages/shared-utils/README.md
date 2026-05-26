# shared-utils

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 110
last_updated: 2026-05-26
```

## Why Placeholder?

공유 코드 수요는 실제 개발이 시작된 후 파악된다. Phase 1 모노레포 셋업과
첫 공유 코드 발생 시점까지 유틸 목록을 확정할 수 없다.

## Scope (TBD)

본 패키지가 다룰 범위:
- 로깅 유틸 (구조화 로그 포맷, 레벨 관리) — TypeScript + Python 양쪽
- 입력 validation 헬퍼 (Zod + Pydantic 공통 규칙 추출)
- 날짜/시간 포맷 유틸 (ISO 8601, KST 기준)
- 에러 핸들링 헬퍼 (`error_response_contract.md` 기반 래핑)
- 문자열 포맷 유틸 (영상 플랫폼별 제목 포맷, 해시태그 정제)
- 환경변수 로딩 + 타입 안전 접근 유틸
- 비동기 재시도(retry with backoff) 공통 함수

## Known Dependencies (when filled in)

- `docs/contracts/tech_stack_contract.md` — TS/Python 버전, 공유 가능 범위
- `docs/contracts/error_response_contract.md` — 에러 핸들링 규칙
- `packages/shared-types/README.md` — 타입 의존
- `backend/fastapi/README.md` — Python 유틸 소비
- `apps/web/` — TypeScript 유틸 소비

## Fill-In Trigger

다음 조건 충족 시 본 패키지 작성 착수:
- Phase 1 모노레포 셋업 완료
- 프론트엔드/백엔드 양쪽에서 동일 로직이 2회 이상 중복 발생하는 시점

## 예시 유틸 형식 (fill-in 시 참고)

```typescript
// 구조화 로그 유틸 예시
import { createLogger } from '@dreammate/shared-utils';

const logger = createLogger({ service: 'planning-agent' });
logger.info('plan_created', { plan_id: 'abc123', mode: 'quick' });

// 재시도 유틸 예시
import { withRetry } from '@dreammate/shared-utils';

const result = await withRetry(() => callLLMApi(payload), {
  maxAttempts: 3,
  backoffMs: 500,
});
```

## Related Skill / Phase

- Skill: N/A
- Phase: 1+
- 책임자: AI / 운영자
