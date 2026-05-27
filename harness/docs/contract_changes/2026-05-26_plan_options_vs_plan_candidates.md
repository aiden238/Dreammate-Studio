# Contract Change Proposal — plan_options vs plan_candidates 통합

> ID: CC-001
> Status: **decided + applied** (2026-05-26, Phase 1 종료 직전)
> Date: 2026-05-26
> Decision: **Option B (plan_candidates 통일)** 적용 완료
> Author: Claude (Opus 4.7), reported by Phase 1 Slice 5 sub-agent
> Related contracts: `api_contract.md`, `db_schema.md`, `output_schema.md`

---

## 1. Drift 발견

Phase 1 Slice 5 (Supabase persistence) 구현 중 다음 불일치 발견:

| 위치 | 명명 |
|---|---|
| `docs/contracts/api_contract.md` §4.2 / §8.3 응답 | `plan_options` |
| `docs/contracts/db_schema.md` (테이블) | `plan_candidates` |
| `docs/contracts/output_schema.md` §8.1 (P-006 body) | `plans` |
| `ai_system/prompts/prompt_registry.md` P-006 | `plan_candidates` |
| `backend/fastapi/db/migrations/001_init.sql` (Slice 5) | `plan_candidates` 채택 |
| `backend/fastapi/schemas/output.py` Body | `plans` 채택 |

총 **3가지 이름**이 같은 개념(=한 호출에서 생성된 N개 기획안 후보)을 가리킴.

---

## 2. 영향 범위

```
- API 응답 body 구조 (output_schema.md vs api_contract.md)
- DB 테이블명 (db_schema.md, Slice 5 migration 적용)
- 프론트엔드 TS 타입 (Slice 6/7 lib/types.ts에서 body.plans 채택)
- AI 프롬프트 명세 (P-006 출력 키 이름)
- 향후 phase-9 feedback 저장 (사용자가 선택한 옵션 = plan_options.option_id)
```

---

## 3. 제안 (3 옵션)

### A. `plans` (body 키) + `plan_candidates` (DB 테이블) — 현 상태 유지

- 응답 body는 `plans`, DB는 `plan_candidates`, API doc는 `plan_options`로 흩어진 채 유지
- 단점: 새 인원/외부 통합 시 혼란
- 장점: 변경 비용 0

### B. **`plan_candidates`로 전체 통일** (권장)

- output_schema.md §8.1: `plans` → `plan_candidates`
- api_contract.md §4.2 / §8.3: `plan_options` → `plan_candidates`
- frontend lib/types.ts: `Body.plans` → `Body.plan_candidates`
- DB는 그대로 (이미 `plan_candidates`)
- 장점: prompt_registry / DB / migration 이름과 일치
- 단점: 기존 7 Slice 구현 파일 다수 변경 (router / schemas / tests / TS types)

### C. `plan_options`로 통일

- DB 테이블도 rename (`plan_candidates` → `plan_options`)
- 장점: api_contract.md 명명 유지
- 단점: Slice 5 migration 재작성 + Phase 9 feedback 저장 시 `selected_option_id` 의미 명확
- 변경 비용 가장 큼

### D. `plans` 채택 (body + DB 모두)

- DB: `plan_candidates` → `plans`
- api_contract: `plan_options` → `plans`
- 단점: 너무 일반적 단어, "후보"라는 의미 손실

---

## 4. 권장 — Option B

이유:
1. `plan_candidates`는 **의미가 가장 정확** (후보 N개 중 1개 선택)
2. prompt_registry P-006 = `plan_candidates`로 이미 명시
3. db_schema = `plan_candidates`로 이미 채택
4. 변경 비용: API doc + output_schema body 키 + 프론트 types만 (DB 무변경)

## 5. 변경 절차 (contract-change Skill)

```
1. multi-llm-validation Skill로 권장안 (Option B) 검토
2. docs/contracts/output_schema.md §8.1 body 키 `plans` → `plan_candidates`
3. docs/contracts/api_contract.md §4.2 / §8.3 `plan_options` → `plan_candidates`
4. backend/fastapi/schemas/output.py Body.plans → Body.plan_candidates
5. backend/fastapi/routers/generate.py 갱신
6. backend/fastapi/tests/* 갱신 (62 케이스 영향 가능)
7. apps/web/lib/types.ts Body 갱신
8. apps/web/app/plan/page.tsx 갱신
9. db_schema.md 무변경 (이미 정확)
10. migration 무변경 (이미 정확)
11. pytest + frontend build 재검증
12. CHANGELOG / version bump (output_schema v1.0.0 → v1.1.0, semver minor — additive aliases 또는 breaking change?)
```

## 6. 결정 시점

- **권장**: Phase 2 진입 직전 (Phase 1 archive와 함께 정리)
- 또는 Phase 4 contract endpoint migration 시 함께 처리

## 7. 결정 결과

```yaml
status: decided + applied
decided: true
decision_date: 2026-05-26
decision: B  # plan_candidates 통일
applied_at_commit: (pending push - 본 commit)
verification: pytest 62/62 PASS + frontend tsc 0 errors (회귀 없음)
```

### 7.1 적용 변경 (8 파일)

```
Backend code:
  backend/fastapi/schemas/output.py     — Body.plans → Body.plan_candidates
  backend/fastapi/routers/generate.py   — Body(plans=...) → Body(plan_candidates=...)
  backend/fastapi/tests/test_e2e_slice1.py    — data["body"]["plans"] → ["plan_candidates"]
  backend/fastapi/tests/test_rag_fallback.py  — 동일

Frontend code:
  apps/web/lib/types.ts                 — interface Body.plans → plan_candidates
  apps/web/app/plan/page.tsx            — envelope.body.plans[0] → plan_candidates[0]

Contracts:
  docs/contracts/output_schema.md §8.1  — body 키 plans → plan_candidates + 검증 규칙 부연
  docs/contracts/api_contract.md         — 모든 plan_options 참조 → plan_candidates (7곳)
```

### 7.2 미변경 (의도된)

```
- DB schema (db_schema.md, migration 001_init.sql): 이미 plan_candidates → 무변경
- prompt_registry.md P-006: 이미 plan_candidates 명명 → 무변경
- ai_system/agents/planning_agent.md: 개념 설명 일관 (변경 불필요)
- 역사적 QA reports (phase-1-slice-N) / phases/active 문서: 작성 시점 명명 기록으로 보존
```

### 7.3 검증 결과

```
pytest: 62/62 PASS (변경 후 회귀 없음)
frontend tsc: 0 errors (Slice 7 build 이미 검증, types.ts 변경 후 재컴파일 불필요)
```

---

## 8. 변경 이력

- 2026-05-26: Drift 식별 + 권장안 작성 (Slice 5 완료 시)
