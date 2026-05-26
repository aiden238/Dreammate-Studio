# shared-types

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: high
estimated_final_lines: 140
last_updated: 2026-05-26
```

## Why Placeholder?

모노레포 구조가 확정되고 `output_schema.md` 기반 Pydantic 모델이 구현되기
전까지 TypeScript 타입 정의를 확정할 수 없다. Phase 1 모노레포 셋업 시 작성한다.

## Scope (TBD)

본 패키지가 다룰 범위:
- `output_schema.md` 기반 TypeScript 타입 자동 변환 (Pydantic → TS)
- 프론트엔드 (`apps/web/`, `apps/mobile/`)와 백엔드 공유 타입 단일 소스
- 4계층 데이터 모델 타입 (User / Brand / Domain / Series / VideoProject)
- MOA Lite 입출력 타입 (IntentInput, PlanOutput, CriticResult 등)
- API 요청/응답 타입 (api_contract.md 기반 자동 생성 연계)
- 공통 열거형 (Enum): mode, status, content_type, platform 등
- Zod 스키마 병행 제공 (런타임 검증용)

## Known Dependencies (when filled in)

- `docs/contracts/output_schema.md` — 타입 정의 원천
- `docs/contracts/tech_stack_contract.md` — TypeScript 버전, 빌드 도구
- `packages/api-client/README.md` — API 타입 소비
- `apps/web/` — 프론트엔드 타입 소비
- `backend/fastapi/README.md` — Pydantic 모델 (변환 소스)
- json-schema-to-typescript 또는 동등 자동 변환 도구

## Fill-In Trigger

다음 조건 충족 시 본 패키지 작성 착수:
- Phase 1 모노레포 셋업 완료 (pnpm workspace 또는 turborepo 설정)
- `output_schema.md` Pydantic 모델 첫 구현 완료

## 예시 타입 형식 (fill-in 시 참고)

```typescript
// output_schema.md에서 자동 변환된 타입 예시
export interface VideoPlanOutput {
  plan_id: string;
  version: string;
  mode: 'discovery' | 'quick';
  hook: string;
  storyline: StorylineItem[];
  critic_score: number;
  created_at: string;
}

export interface StorylineItem {
  scene_index: number;
  duration_sec: number;
  description: string;
}
```

## Related Skill / Phase

- Skill: agent-io-check (I/O 타입 드리프트 검증)
- Phase: 1+
- 책임자: AI / 운영자
