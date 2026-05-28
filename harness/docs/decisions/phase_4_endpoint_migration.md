# ADR-014: Phase 4 Endpoint Migration — Coexistence Policy

> Status: accepted (Phase 4 Slice 1, 2026-05-28)
> 사용자 결정 5-a 반영 (Phase 1 endpoint Phase 8+ 제거 — 교차 검토 + 마이그 완료 후)
> GPT 검토 채택 정신: 단순화, scope creep 금지, Phase 1 회귀 0

---

## Context

Phase 1은 Simplest Slice 원칙 (phase-start v1.1.0 §6.2)에 따라
sync + 1 plan endpoint `/api/v1/generate`를 채택했다 (api_contract.md §8.3과 deviate).

Phase 4 contract 본격 정합 시점에서 두 가지 선택지가 충돌:

1. **Immediate cutover** — Phase 1 endpoint 즉시 제거 후 신 endpoint로 교체
2. **Coexistence** — 두 endpoint 모두 유지, 점진적 마이그
3. **Two-version path** — `/v1` (Phase 1) / `/v2` (Phase 4) 병행

GPT 검토 결과: Phase 4는 "새 endpoint 추가 + Phase 1 회귀 0"만 한다.
사용자 결정 5-a: **공존 + Phase 8+ 제거** (교차 검토 + 마이그 완료 후).

---

## Decision

**Coexistence (공존) — Phase 4 ~ Phase 7 두 endpoint 모두 동작.**

### Phase 1 endpoint `/api/v1/generate`
- 본 endpoint 코드 무수정 (sync 1-plan 동작 그대로)
- `X-API-Deprecation: Phase 4 - use POST /api/v1/plans/{plan_id}/generate` response header만 추가
  - success path (200) + error path (422 INV-001 / 502 E-LLM-*) 모두 동일 header 동봉
  - HTTP header는 latin-1만 허용 — em-dash 등 unicode 사용 금지 (ASCII 하이픈 사용)
- response body / status code / validation.warnings 전부 Phase 1 baseline 그대로
- pytest 62 baseline 회귀 0 (Phase 1 회귀 acceptance A4 통과)

### Phase 4 endpoints (api_contract.md §8 정합)
- `POST /api/v1/plans/start` — 신규 plan_id 발급 (201 Created)
- `POST /api/v1/plans/{plan_id}/wizard/{step}` — Discovery 7-step / Quick 4-step (Slice 1 skeleton, Phase 5+ 본격)
- `POST /api/v1/plans/{plan_id}/generate` — 3-plan generation (Slice 1 skeleton 202 Accepted, Slice 2 본격 + multi-model 가능 구조)
- `GET /api/v1/plans/{plan_id}` — 결과 / 상태 조회
- 미발견 plan_id → 404 + INV-006 ErrorEnvelope (error_response_contract.md §3.2 정합)

### in-memory plan_store (Phase 4 한정)
- 단일 프로세스 in-memory dict (`_plan_store: dict[str, dict[str, Any]]`)
- 재시작 시 휘발 — Phase 5에서 Supabase video_projects + wizard_states로 교체
- Auth 미적용 (익명) — Phase 5에서 user_id 연결

---

## Alternatives

### A. Immediate cutover
- Phase 1 endpoint 즉시 제거 후 신 contract endpoint로 교체
- **거부 사유**: 회귀 위험. Phase 1 frontend (`/`, `/plan`) 즉시 깨짐. 사용자 결정 5-a 정신 위반.

### B. Two-version path (`/v1` / `/v2`)
- Phase 1 endpoint를 `/v1`으로, Phase 4 endpoint를 `/v2`로 분리
- **거부 사유**: 사용자 결정 5-a는 "공존 + Phase 8+ 제거" — version 분리는 마이그 의도가 약함. API surface 추가 부담.

### C. Coexistence + Deprecation header + Phase 8+ 제거 (채택)
- 가장 단순. 회귀 0. 사용자 결정 5-a 정합.
- 점진 마이그 가능 (Phase 5 Auth + Phase 6 통합 + Phase 7 검증 + Phase 8 제거).

---

## Consequences

### Positive
- Phase 1 frontend (`/`, `/plan`) 회귀 0 — acceptance A4 통과
- Phase 4 frontend (`/plan/[plan_id]`, Slice 3 영역) 독립 진화
- 점진 마이그 가능 — 사용자 데이터 / 모니터링 확보 후 안전한 제거
- ADR-008 (Phase 1 Simplest Slice) 결정 보존 — Phase 1 baseline 유지

### Negative
- 두 endpoint 유지 비용 — router / tests / 모니터링 (Phase 4 ~ Phase 7)
- 사용자 혼란 가능성 — deprecation header를 사용자가 명시적으로 안내 필요
- OpenAPI 문서 surface 증가 (4 신규 endpoint + 기존 1개 = 5개)

---

## Migration Plan

| Phase | 작업 | 기준 |
|---|---|---|
| 4 | Phase 1 endpoint 무수정 + `X-API-Deprecation` header 추가 | acceptance A4: Phase 1 회귀 0 |
| 4.5 | (선택) Critic revise loop + Rewriter 추가 — Phase 4 endpoint 사용 | Phase 1 endpoint 유지 |
| 5 | Auth (Supabase) 도입 시 Phase 4 endpoint에 user_id 연결 | in-memory store → Supabase 교체 |
| 6 | 통합 모니터링 — Phase 1 endpoint 사용량 측정 (request count / latency / error rate) | Phase 1 endpoint 사용량 logging |
| 7 | 사용량 임계값 이하 시 deprecation 강화 (HTTP 410 안내 우회) | 사용자 결정 + multi-llm-validation |
| 8 | 교차 검토 + 사용자 검토 + 데이터 마이그 → **Phase 1 endpoint 제거** | 사용자 결정 5-a 최종 |

---

## Validation (Phase 4 Slice 1)

- pytest 77 PASS (62 baseline + 15 신규)
  - test_phase_1_generate_has_deprecation_header (success 200 + header)
  - test_phase_1_generate_body_unchanged (envelope body 무변경)
  - test_phase_1_generate_intent_block_has_deprecation_header (error 422 + header)
  - test_plans_start_creates_plan_id / wizard_chain / generate_skeleton_202 / get_plan_resource 등
- audit_naming 0 drift
- 회귀 0 (test_e2e_slice1 13 + test_critic 6 + test_planning 5 + test_rag_fallback 8 + test_db 다수 모두 통과)

---

## Related

- ADR-008 (Phase 1 Simplest Slice — sync 1-plan 결정 근거)
- ADR-015 (예정, Slice 2): 3-plan multi-model 구조 — Phase 4 endpoint 본격 구현
- api_contract.md §8 (4 endpoints contract 원본)
- error_response_contract.md §3.2 (INV-006 — 4계층 참조 무결성 위반)
- output_schema.md §2 / §8 (Envelope + plan_candidates length 3)
- harness/phases/active/phase-4-fastapi-extension/acceptance.md A1 (Phase 4 endpoints 4개) + A4 (Phase 1 회귀 0)

---

## 변경 이력

- 2026-05-28: 최초 작성 (Phase 4 Slice 1, 사용자 결정 5-a 반영)
