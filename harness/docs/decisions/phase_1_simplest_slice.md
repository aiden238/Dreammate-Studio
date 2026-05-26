# ADR — Phase 1 Simplest Slice

> ADR ID: ADR-008
> Status: accepted
> Date: 2026-05-26
> Author: Claude (Opus 4.7)
> Related: `phases/active/phase-1-mvp-basic-flow/work_plan.md`, `phase-start` Skill v1.1.0

---

## Context (배경)

Phase 1 (MVP 기본 플로우)는 영상기획 AI 에이전트의 첫 실 코드 작업.  
초기 phase의 핵심 위험은 **scope creep + 추상화 과잉**으로 인한 진입 지연.

phase-start v1.1.0 §6.2의 Simplest Slice 원칙("더 줄일 수 있는가?" 3회 반복)을 적용하여  
Phase 1의 최소 작동 단위를 도출했다.

---

## Decision (결정)

**Phase 1의 Simplest Slice (= Slice 1)는 다음으로 한다:**

```
POST /api/v1/generate (FastAPI 단일 endpoint)
  ↓
gpt-4o-mini 1회 호출 (Intent + Planning 통합 단일 프롬프트, 임시)
  ↓
output_schema v1.0 JSON 반환 (RAG/Critic은 더미 값으로 schema 만족)
```

**구현 파일 ≤ 5개:**
1. `backend/fastapi/main.py`
2. `backend/fastapi/routers/generate.py`
3. `backend/fastapi/schemas/output.py`
4. `backend/fastapi/schemas/input.py`
5. `backend/fastapi/agents/intent_planning.py` (Slice 2에서 분리 예정)

**검증 = curl 1회로 충분:**
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "유튜브 채널 첫 영상 기획해줘"}'
```

HTTP 200 + schema-valid JSON 반환 시 Slice 1 완료.

---

## Slice 압축 과정

| 단계 | 답안 | 평가 |
|---|---|---|
| 1차 | 입력 → Intent → Direction → RAG → Plan → Critic → DB → UI | 너무 많음 |
| 2차 | 입력 → Intent+Plan 통합 → return JSON (DB X, UI X) | 줄어들었으나 더 가능 |
| 3차 | curl → JSON 1개 (LLM 1회 호출만) | **여기서 멈춤** |

3차 답이 최소 단위인 이유:
- LLM 0회는 영상기획 AI 의미 없음
- Endpoint 없으면 외부에서 호출 불가능
- JSON 안 반환하면 후속 Slice 진입 불가능

→ 더 줄이면 "영상기획 AI" 정의 위반.

---

## Slice 점진 확장 순서

```
Slice 1 (필수): API + 단일 LLM 호출 + JSON 반환     ← 본 ADR 범위
Slice 2: Intent / Planning Agent 분리
Slice 3: Critic Agent 추가 (1회 평가)
Slice 4: RAG Lite + fallback
Slice 5: Supabase 저장
Slice 6: Next.js 진입 UI
Slice 7: 진행 stepper + 오류 카드 + PWA manifest
```

각 Slice 독립 commit + 자동 테스트 통과 후 다음 진입.

---

## Alternatives Considered (대안)

### A1. 처음부터 4 Agent 전체 구현

- **장점**: Phase 1 종료 시점이 빠를 수도
- **단점**: 첫 commit이 너무 무거움, 디버깅 시 실패 지점 분리 불가
- **결정**: 거부. Slice 점진 확장이 디버깅·롤백에 유리.

### A2. UI를 먼저 만들고 mock API로 시작

- **장점**: 사용자 피드백 빠름
- **단점**: API 인터페이스가 UI 가정에 종속됨, output_schema 변경 위험
- **결정**: 거부. contract-first 원칙(Phase 0에서 결정).

### A3. RAG 없이 끝까지 진행 (Phase 1 영역에서 제외)

- **장점**: 복잡도 감소
- **단점**: RAG Lite는 acceptance.md A3 명시 항목, Phase 1 핵심 가치
- **결정**: 거부. Slice 4로 포함하되 fallback 보장.

### A4. Critic 제외 (Phase 4로 이관)

- **장점**: 복잡도 감소
- **단점**: Critic 평가 결과(scores)는 acceptance.md A1 응답 구조에 포함
- **결정**: 거부. revise는 제외하되 1회 평가는 포함.

---

## Consequences (결과)

### Positive

- 첫 commit (Slice 1) 매우 작음 → 디버깅 용이
- 각 Slice가 독립적이라 일부 실패해도 일부는 보존
- output_schema 준수가 Slice 1부터 강제됨
- assumptions.md §1.2 불확실 항목(U1~U5)을 Slice 진행 중 점진 검증

### Negative

- Slice 1의 통합 프롬프트가 임시 코드 (Slice 2에서 폐기)
- 더미 RAG/Critic 값으로 schema 만족시키는 우회 필요
- 총 7개 commit으로 history가 늘어남 (단점이라 보기 어려움)

### Mitigation

- Slice 1 코드에 `# TODO: Slice 2에서 분리` 주석 명시
- 더미 값은 명백히 표시 (`"_dummy": true` 등)

---

## Verification Plan

```
Slice 1 완료 조건:
  1. uvicorn main:app 기동 가능
  2. curl 호출 응답 HTTP 200
  3. 응답이 output_schema v1.0 구조 준수 (jsonschema validation)
  4. pytest backend/tests/e2e_slice1.py 통과

후속 Slice는 work_plan.md의 acceptance 참조.
```

---

## Related ADRs / Docs

- `docs/decisions/tech_stack_decision.md` (ADR-001)
- `docs/decisions/orchestration_strategy.md` (ADR-006)
- `phases/active/phase-1-mvp-basic-flow/assumptions.md`
- `phases/active/phase-1-mvp-basic-flow/work_plan.md`
- `.claude/skills/phase-start/SKILL.md` v1.1.0 §6.2

---

## 변경 이력

- 2026-05-26: ADR 최초 작성, Phase 1 Slice 1 결정
