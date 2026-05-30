# Phase 8 Pre-Entry Multi-LLM Validation — Self (Claude Code)

> 검증 모델: Claude Code (자가, 지침 참조)
> 검증 일자: 2026-05-29
> 검증 유형: formal (다섯 번째 정식 트리거 — Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째 + Phase 8 다섯째)
> 외부 검증: `2026-05-29_phase-8-pre-entry_external.md` (별도 placeholder)
> Skill 의무 트리거: **ai-architecture-review (★ 첫 정식 트리거 — Slice 1)** + **prompt-version-review (★ 첫 정식 트리거 — Slice 1 분석 + Slice 4 적용)** + multi-llm-validation (formal 다섯 번째)

## 검증 대상

1. orchestrator 추출 behavior-preserving 원칙 (Envelope byte-identical + 기존 pytest 223 수정 0)
2. ProgressSink 인터페이스 (Null default 회귀 0 + Store/Null 분리)
3. SSE progress_store 브릿지 (graceful, background task 미도입, single-process best-effort)
4. Critic conservative adapter (Phase 6 canonical 불변 — 사용자 결정 — P-007 0–5 prompt 유지 + 코드 0–1 정규화)
5. prompt_registry semver 정식화 범위 (P-001~P-008 + AUX + P-EVAL-1)
6. prompt_id/version 단일 출처 정합 (각 agent 파일 상수 ↔ registry)
7. SSE 실시간 concurrency best-effort (single process, full async Phase 11+)

## 참조한 지침

- `harness/CLAUDE.md` § AI 구조, 메타 개선, 큰 결정
- `harness/AGENTS.md` (구현/QA 모델 라우터 — behavior-preserving refactor 대상)
- `harness/ai_system/orchestration/moa_policy.md` (§2 오케스트레이터 항상 중개 + §4 동기/비동기 + §5 실패 격리 + §7 컨텍스트 격리)
- `harness/ai_system/prompts/prompt_registry.md` (P-007 Critic 0–5 8 named dims + §13 변경 관리)
- `harness/backend/fastapi/routers/plans.py` (`plans_generate()` god-function — Intent→RAG→3-plan→Critic+revise→save→Envelope 인라인)
- `harness/backend/fastapi/routers/sse.py` (mock 4단계 `_progress_generator` + `_STEPS` + Origin 검증)
- `harness/backend/fastapi/agents/critic.py` (`run_critic` — 이미 canonical 0–1 산출 확인 + `select_best_plan_index` ADR-018 5단계 fallback + PROMPT_VERSION v1.0.0)
- `harness/backend/fastapi/schemas/output.py` (`CriticEvaluation` canonical overall_score 0–1 + dimensions dict + deprecated Optional)
- `harness/docs/contracts/output_schema.md` (Phase 6 CriticEvaluation canonical — 불변)
- `harness/docs/decisions/phase_6_critic_canonical.md` (ADR-018 — 본 ADR-029가 정합 대상, 불변)
- `harness/docs/decisions/phase_5_sse_progress.md` (ADR-022 — SSE 4단계 baseline)
- `harness/docs/contracts/agent_io_contract.md` (orchestrator 중개 + Critic v1.1.0 adapter 수정 대상 — Slice 4)
- `harness/meta/patterns.md` (P-GRACEFUL-001, P-CONTRACT-FIRST-001, P-X1-EFFECT-001, P-VALIDATION-FORMAL-001)
- Phase 7 closing_notes.md / retrospectives/phase-7.md (Phase 8 진입 체크리스트)
- Phase 8 entry files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes)
- `.claude/skills/ai-architecture-review/SKILL.md` (★ 첫 정식 트리거 절차 7단계)
- `.claude/skills/prompt-version-review/SKILL.md` (★ 첫 정식 트리거 절차 7단계)
- `.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

## 검증 결과 (V1~V7)

### V1. orchestrator 추출 behavior-preserving 원칙 — PASS

- **self-question**: `plans_generate()` 400줄 god-function을 `orchestration/moa_orchestrator.py::generate_plan()`으로 추출할 때, Envelope 출력 byte-identical + 기존 pytest 223 수정 0이 정말로 동작 불변의 충분 증거인가?
- **self-answer**:
  - **moa_policy §2 위반 해소**: 현재 orchestration이 router(`plans.py`)에 인라인 → moa_policy §2 "agent 간 직접 호출 금지. 오케스트레이터(backend service layer)가 항상 중개한다"를 위반. 서비스 레이어 `moa_orchestrator.py` 추출이 정합 회복.
  - **추출 범위**: `plans_generate()` body 7단계 (1. Intent → 2. RAG graceful → 3. 3-plan parallel → 4. Plan schema × 3 → 5. Critic+revise loop asyncio.gather → 6. DB save graceful → 7. Envelope 조립)를 `generate_plan(plan_id, plan_entry, req, *, progress=NullProgressSink())`로 **그대로 이동**.
  - **router thin adapter화**: `plans_generate()` → `_plan_store` 조회 + `_not_found_response` + `return await generate_plan(...)`. helper(`_not_found_response` / `_error_envelope_response`)는 orchestrator와 공유 (orchestration/ 또는 router 잔류).
  - **behavior-preserving 증거**: 기존 `test_plans` / `test_e2e_slice1` / `test_3_plan`이 추출 후에도 **수정 없이** PASS. 테스트가 동작 불변을 검증하는 oracle. 테스트 수정이 필요해지면 추출이 동작을 바꾼 것 → 재작업 신호 (acceptance §6.3 ★ 게이트).
  - **Envelope byte-identical**: `Envelope(meta=..., body=..., validation=...)` 조립 순서·필드·`validation.checks` 7개 순서·`warnings` 병합 순서 모두 보존. `compute_validation_warnings_phase4` 호출 + Phase 7 RAG marker 병합 순서 동일.
- **잠재 risk**:
  - 추출 중 graceful 처리(`E-LLM-001/002/003`, `INV-001/006`) 분기 누락 → Envelope 차이.
  - `_plan_store` 상태 mutation(`plan_entry["status"]="generated"` + `["envelope"]=...`) 위치 보존 실패 → GET `/plans/{id}` 회귀.
  - asyncio.gather 기반 Critic+revise loop를 추출 시 event loop 컨텍스트 깨짐.
- **권장**:
  - ADR-027 §Constraints에 "Envelope byte-identical + pytest 223 수정 0 + graceful/에러코드/validation.checks 순서 100% 보존" 명시.
  - Slice 2 `test_moa_orchestrator.py`에 에러 경로(Intent 차단 INV-001 / Planning 실패 E-LLM-001 / 전체 schema 실패 E-LLM-003) 보존 케이스 추가.
  - non_goals NG "리팩터 김에 로직 개선" 금지 — pure move only.

### V2. ProgressSink 인터페이스 (Null default 회귀 0) — PASS

- **self-question**: orchestrator에 stage별 `progress.emit(...)`를 삽입할 때, default를 `NullProgressSink()`로 두면 Slice 2 단계(SSE 미통합)에서 회귀가 정말 0인가? Store/Null 분리가 적절한가?
- **self-answer**:
  - **Protocol 설계**: `ProgressSink` = `emit(stage: str, **meta) -> None` 단일 메서드 Protocol (duck-typed). `NullProgressSink.emit`은 no-op (pass) → 회귀 0. `StoreProgressSink.emit`은 `progress_store.record(plan_id, event)` (Slice 3 활용).
  - **회귀 0 근거**: `generate_plan(..., *, progress=NullProgressSink())` default → router thin adapter가 progress 인자 미전달 시 Null → 모든 emit이 no-op → Envelope·DB·plan_store 동작에 영향 0. Slice 2 pytest는 NullSink 경로만 통과해도 PASS.
  - **emit 지점**: stage 경계 5곳 (`intent` / `rag` / `planning` / `critic` / `complete`) — sse.py `_STEPS` 4단계 + complete와 1:1 정합. emit은 side-effect-free 관점에서 orchestration 로직과 독립 (값 반환 미사용 → 흐름 불변).
  - **Store/Null 분리**: Null = default·테스트·SSE 미연결, Store = SSE 연결 시 주입 (의존성 역전). 추출(Slice 2)과 통합(Slice 3) 책임 분리 → 충돌 0 (multi_slice_plan 충돌 매트릭스 정합).
- **잠재 risk**:
  - emit 삽입 위치가 stage 실 완료 시점과 어긋나면 SSE 진행률 부정확 (단 회귀는 아님 — Null no-op).
  - `**meta` 자유 인자 → drift 가능 (stage 명 비표준화).
- **권장**:
  - ADR-027 §Decision에 ProgressSink Protocol + NullProgressSink default 명시.
  - stage 명을 `_STEPS` name과 동일 enum-like 상수로 고정 (`intent`/`rag`/`planning`/`critic`/`complete`).
  - Slice 2 `test_moa_orchestrator.py::test_progress_sink_emits`로 stage별 emit 호출 + NullSink no-op 회귀 검증.

### V3. SSE progress_store 브릿지 (graceful, background task 미도입) — PASS

- **self-question**: 동기 blocking `generate`(POST) 처리 중 in-memory `progress_store`에 기록하고, 별도 GET `/progress` SSE가 이를 read하는 single-process 브릿지가 background task 없이 동작 가능한가? graceful fallback이 기존 test_sse를 보존하는가?
- **self-answer**:
  - **사용자 결정 채택**: SSE 통합 = in-memory `progress_store` 브릿지 (graceful). **background task 미도입** — moa_policy §4 "Phase 0~10 동기 처리" 정합. full async streaming은 Phase 11+ (트래픽 증가 후).
  - **브릿지 메커니즘**: `progress_store: dict[str, list[dict]]` (plan_id keyed, in-memory). orchestrator의 `StoreProgressSink.emit` → `record(plan_id, event)`. SSE `_progress_generator` → `progress_store.read(plan_id)` 우선, **비어있으면 기존 mock `_STEPS` 4단계 fallback** (기존 `test_sse` 4 케이스 수정 0 보존).
  - **graceful 핵심**: store가 비었거나(아직 generate 미시작 / 다른 프로세스) read 실패 시 mock으로 자연 fallback → SSE는 항상 event schema 유효 응답. P-GRACEFUL-001 (Phase 1~7 5회 입증) 정신 6번째.
  - **메모리 누수 방지**: `clear(plan_id)` on complete + maxlen 제한 (U6). TTL은 단순 complete-clear로 충분 (single-process MVP).
- **잠재 risk**:
  - **동기 blocking 중 read race**: POST `generate`가 동기 blocking이면 같은 worker가 GET `/progress`를 동시에 처리 못 할 수 있음 (single worker dev). → V7에서 best-effort 명시.
  - in-memory store는 multi-worker(uvicorn --workers N) 환경에서 프로세스 간 미공유 → 다른 worker의 progress 미가시 → mock fallback.
  - store 누수 (clear 누락 시 dict 무한 증가).
- **권장**:
  - ADR-028 §Constraints에 "background task 미도입 + single-process best-effort + full async Phase 11+ + TTL/clear on complete" 명시.
  - Slice 3 `test_sse_integration.py`에 record→read round-trip + graceful fallback(store empty → mock) + clear on complete 케이스.
  - 기존 `test_sse` 4 케이스 수정 0 = graceful fallback 보장 증거.

### V4. Critic conservative adapter (Phase 6 canonical 불변) — PASS

- **self-question**: prompt_registry P-007(0–5 8 named dims) ↔ Phase 6 canonical(overall_score 0–1 + dimensions)의 drift를, Phase 6 ADR-018을 변경하지 않고 conservative adapter로 해소 가능한가? `run_critic`이 이미 canonical을 산출하는가?
- **self-answer**:
  - **사용자 결정 (불변)**: **Conservative adapter** — Phase 6 canonical(0–1 overall_score + dimensions) **불변** (ADR-018 보존). prompt_registry P-007(0–5) prompt 텍스트 **유지** (LLM-facing) + 코드 0–1 정규화 adapter **문서화** + P-007 v1.0.0→v1.1.0 (Slice 4 적용).
  - **현 상태 확인** (코드 정독 결과):
    - `agents/critic.py::run_critic`은 LLM에게 **0–5 정수 8 dims**를 요청(SYSTEM_PROMPT)하고 `norm_scores`(0–5 clamp) + `overall_score_avg`(0–5 평균) + `overall_verdict` 산출. → **deprecated 0–5 형식** 반환.
    - `plans.py`는 `CriticEvaluation(**first_verdict)` 호출 — `CriticEvaluation`은 Phase 6 ADR-018에서 canonical(`overall_score` 0–1, `dimensions` dict) + deprecated(`scores`, `overall_score_avg` 등) **모두 Optional** 강등 → 회귀 0 (deprecated 필드도 수용).
    - `select_best_plan_index`는 canonical(`overall_score` → `dimensions`) 우선, deprecated(`overall_score_avg` → `scores`) fallback + `DeprecationWarning`.
  - **gap 정정**: notes.md/task는 "run_critic 이미 canonical 산출"이라 했으나, 실측 결과 `run_critic`은 **0–5 deprecated 형식**을 산출하고 canonical은 **Optional**로 수용된다. 즉 canonical 우선순위는 `select_best_plan_index`에서만 작동하고, `run_critic` 자체는 0–5만 반환. → conservative adapter가 **필요**한 이유 정당화. Slice 4에서 `run_critic`에 0–5→0–1 정규화 adapter 명시 (norm_scores/5.0 → dimensions, overall_score_avg/5.0 → overall_score) **추가** + 로직 불변(기존 0–5 필드도 유지하여 회귀 0).
  - **adapter 정의 (Slice 4 적용 계획)**: `dimensions[k] = norm_scores[k] / 5.0` (0–1), `overall_score = overall_score_avg / 5.0` (0–1). 기존 0–5 deprecated 필드(scores/overall_score_avg) 병행 유지 → `CriticEvaluation` Optional 호환 → 회귀 0.
- **잠재 risk**:
  - adapter 추가가 기존 `test_critic` 동작 변경 시 회귀 (→ deprecated 필드 병행 유지로 회피).
  - 0–5↔0–1 이중 표현 혼란 (LLM-facing 0–5 vs code-facing 0–1).
  - P-007 v1.1.0 bump가 minor인가 major인가 (output schema 변경 아님 — 내부 정규화 추가 = minor).
- **권장**:
  - ADR-029 §Decision에 conservative adapter (P-007 prompt 0–5 유지 + 코드 0–1 정규화 + Phase 6 canonical 불변 + P-007 v1.0.0→v1.1.0) 명시 + V4 gap 정정(run_critic 현 0–5 산출) 반영.
  - prompt-version-review §2 기준: 0–5 prompt 텍스트 불변 + 내부 정규화 표현 개선 = **minor bump** (v1.0.0→v1.1.0). output schema 미변경 → major 아님.
  - Slice 4 `test_prompt_registry_consistency.py`에 P-007 v1.1.0 adapter(0–5 입력 → 0–1 dimensions) 검증.

### V5. prompt_registry semver 정식화 범위 — PASS

- **self-question**: prompt_registry P-001~P-008 + AUX + P-EVAL-1을 semver로 정식화하는 범위가 Phase 8 12~16h에 무리 없고, A/B 실행(Phase 11+)과 명확히 분리되는가?
- **self-answer**:
  - **정식화 범위**: P-001~P-008 (8 core) + P-AUX-1 (intent_filter) + P-AUX-2 (brand_memory_extractor) + P-EVAL-1 (candidate_knowledge_evaluator) = **11 prompt**. 각각 `(id, version)` 쌍 정식 등록 + active/deprecated 표시 + deactivate_at 정책 baseline.
  - **정식화 ≠ A/B 실행**: 본 Phase 8은 **semver 부여 + 단일 출처 정합 + P-007 v1.1.0**만. golden_set 회귀(prompt-version-review §4) + A/B 50:50 라우팅(§5 major)은 **Phase 9+/11+** (NG3 — semver 정식화만, A/B는 100세션 누적 후). eval-run Skill 정식화는 Phase 9+ (NG7).
  - **현 상태**: registry는 이미 각 prompt에 `Version: v1.0.0` 표기 + §13 변경 관리 절차 보유. P-EVAL-1은 §semver/활성 정책 블록 보유 (모범). 본 Phase는 이 baseline을 P-001~P-008 + AUX에 **일관 확장** + P-007만 v1.1.0.
  - **범위 적정성**: 문서 정식화(registry §추가 + agent_io_contract 명시) + critic.py 소폭(v1.1.0 상수) + consistency test. 코드 변경 최소 → 12~16h 내 무리 0.
- **잠재 risk**:
  - 11 prompt 전부 semver 블록 추가 시 registry 비대 (단 문서만 — 회귀 0).
  - P-005q (Quick Mode 변형) 같은 sub-variant의 version 정책 모호.
  - golden_set 회귀 없이 v1.1.0 bump → 회귀 평가 누락 (단 Phase 8은 정합 test만, golden_set은 Phase 9+).
- **권장**:
  - ADR-029 §Decision에 "P-001~P-008 + AUX + P-EVAL-1 semver 정식화 (A/B·golden_set 회귀는 Phase 9+/11+ — NG3/NG7)" 명시.
  - P-005q 등 variant는 부모 prompt version 상속 (별도 version 미부여) — registry §추가 메모.
  - Slice 4 contract-change Skill로 prompt_registry.md 갱신 (registry는 contract).

### V6. prompt_id/version 단일 출처 정합 — PASS

- **self-question**: 각 agent 파일의 `PROMPT_ID`/`PROMPT_VERSION` 상수 ↔ registry의 `(id, version)`가 단일 출처로 정합한가? drift 검증 test가 가능한가?
- **self-answer**:
  - **현 상태** (코드 정독): `agents/critic.py`에 `PROMPT_ID = "P-007"` + `PROMPT_VERSION = "v1.0.0"` 모듈 상수 존재. `plans.py`는 이를 `CRITIC_PROMPT_ID`/`CRITIC_PROMPT_VERSION` 으로 import + `validation.checks[critic_evaluation].detail = f"{CRITIC_PROMPT_ID}@{CRITIC_PROMPT_VERSION}"`로 Envelope에 노출. `INTENT_PROMPT_ID`/`VERSION` + `PARALLEL_3_PROMPT_ID`/`VERSION`도 동일 패턴.
  - **정합 정책**: registry = **단일 진실 출처 (SoT)**. 각 agent 파일 상수는 SoT를 미러. `test_prompt_registry_consistency.py`가 agent 파일 상수 ↔ registry `(id, version)` 일치를 검증 → drift 0 보장.
  - **검증 방식**: registry.md를 파싱(또는 상수 매핑 dict)하여 `{P-007: v1.1.0, P-001: v1.0.0, ...}` 추출 → 각 agent 모듈 상수와 비교. 불일치 시 test 실패 → CI 게이트.
  - **Critic v1.1.0 정합**: Slice 4에서 `critic.py::PROMPT_VERSION = "v1.1.0"` + registry P-007 v1.1.0 동시 갱신 → 같은 commit 정합 (output_schema §0 "한쪽 변경 시 다른 쪽 같은 commit 갱신" 정신 계승).
- **잠재 risk**:
  - registry.md 텍스트 파싱 fragile (마크다운 포맷 변경 시 test 깨짐) → 상수 매핑 dict 방식 권장.
  - intent/planning/rewriter는 상수가 registry P-ID와 정확 매핑되는지 확인 필요 (planning은 `PARALLEL_3_*` — P-006 정합 확인).
  - agent_io_contract.md도 prompt 버전 노출 → 3중 정합 (registry ↔ agent 상수 ↔ contract).
- **권장**:
  - ADR-029 §Decision에 "prompt_id/version 단일 출처 — registry SoT + agent 파일 상수 미러 + consistency test" 명시.
  - `test_prompt_registry_consistency.py`는 텍스트 파싱보다 명시적 매핑 dict(`EXPECTED = {"P-007": "v1.1.0", ...}`) 비교 권장 (fragile 회피).
  - Slice 4 agent-io-check Skill로 agent_io_contract ↔ 구현 drift 0 검증 (3중 정합 마무리).

### V7. SSE 실시간 concurrency best-effort (single process) — PASS

- **self-question**: single-process 환경에서 POST `generate` in-flight 중 GET `/progress`가 progress_store를 실시간 read하는 것이 보장 가능한가, 아니면 best-effort인가? full async는 언제인가?
- **self-answer**:
  - **best-effort 명시**: 동기 blocking `generate`(POST)가 진행 중일 때, 같은 single worker가 GET `/progress` SSE를 처리하려면 event loop가 yield되어야 함. orchestrator 내 `await`(asyncio.gather, run_in_executor, LLM 호출) 지점에서 loop가 yield되므로 **GET이 진행 중 read 가능** — 단 이는 best-effort (worker 수·yield 타이밍 의존).
  - **graceful 보장**: 실시간 read가 안 되면(store 비었거나 다른 worker) mock `_STEPS` fallback → SSE는 항상 유효 응답. 즉 **실시간성은 best-effort, 가용성은 graceful 100%**.
  - **full async 경계**: 진정한 실시간 양방향·multi-worker 공유 progress는 Phase 11+ (background task / 외부 store Redis 등 — NG1 background task 미도입 / NG13 WebSocket 미도입). moa_policy §4 "11+ 비동기 검토" 정합.
  - **single-process 가정**: MVP는 uvicorn 단일 worker(또는 dev) 가정. multi-worker 시 in-memory 미공유 → mock fallback (회귀 아님, 정확도 저하만).
- **잠재 risk**:
  - dev에서 단일 worker + 동기 LLM 호출(run_in_executor thread)이면 main loop는 free → read 가능하나, 순수 동기 blocking 구간에서는 SSE 지연.
  - production multi-worker 시 progress 미가시 (mock fallback) → 사용자 혼란 가능 (단 complete는 도달).
  - "실시간"이라는 UX 기대 vs best-effort 현실 gap.
- **권장**:
  - ADR-028 §Constraints + §Trade-offs에 "single-process best-effort (POST in-flight 중 GET read) + full async streaming Phase 11+ + multi-worker는 mock fallback" 명시.
  - acceptance/assumptions C11 + U2 정합 (best-effort 명시 — 이미 entry files 반영).
  - Phase 11+ cost/관측성 phase에서 외부 progress store(Redis pub/sub 등) 검토 — 본 Phase 외 (NG12 multi-provider 동반).

## 종합 판정

**Phase 8 entry 허용 — 7/7 PASS (V1~V7)**

| ID | 항목 | 결과 | 후속 조치 |
|---|---|---|---|
| V1 | orchestrator 추출 behavior-preserving | PASS | ADR-027 §Constraints (Envelope byte-identical + pytest 223 수정 0 + 순서 보존) |
| V2 | ProgressSink 인터페이스 (Null default 회귀 0) | PASS | ADR-027 §Decision (Protocol + NullProgressSink default + stage enum 고정) |
| V3 | SSE progress_store 브릿지 (graceful) | PASS | ADR-028 §Constraints (background task 미도입 + clear on complete) |
| V4 | Critic conservative adapter (Phase 6 canonical 불변) | PASS | ADR-029 §Decision (gap 정정 — run_critic 현 0–5 산출 → adapter 추가) |
| V5 | prompt_registry semver 정식화 범위 | PASS | ADR-029 §Decision (P-001~P-008 + AUX + P-EVAL-1, A/B Phase 11+) |
| V6 | prompt_id/version 단일 출처 정합 | PASS | ADR-029 §Decision (registry SoT + consistency test 매핑 dict) |
| V7 | SSE 실시간 concurrency best-effort | PASS | ADR-028 §Constraints/Trade-offs (single-process best-effort + Phase 11+) |

다음: Slice 2 sub-agent dispatch — MOA Orchestrator 추출 (behavior-preserving) + ProgressSink (Null default 회귀 0).

## Gap 정정 기록 (코드 정독 결과)

본 self-validation은 코드 직접 정독으로 entry 가정 1건을 정정:

- **가정**: "run_critic는 이미 canonical(0–1)을 산출 (plans.py가 CriticEvaluation(**verdict) 호출)" (notes.md / task 기술).
- **실측**: `agents/critic.py::run_critic`은 LLM에 **0–5 정수 8 dims**를 요청하고 **deprecated 0–5 형식**(`scores` 0–5 + `overall_score_avg` 0–5)을 반환. canonical(`overall_score` 0–1 + `dimensions`)은 `CriticEvaluation`이 Optional로 **수용**할 뿐 `run_critic`이 산출하지 않음. canonical 우선순위는 `select_best_plan_index`에서만 작동.
- **영향**: conservative adapter의 **필요성 정당화 강화** — Slice 4에서 `run_critic`에 0–5→0–1 정규화 adapter를 **추가**(dimensions = scores/5.0, overall_score = overall_score_avg/5.0)하되 기존 0–5 deprecated 필드 병행 유지 → 회귀 0. ADR-029 본문 반영.

## 외부 검증 연계

self-validation 단일 모델 (Claude Code) 결과. 외부 검증 결과 (GPT/Gemini)는 `2026-05-29_phase-8-pre-entry_external.md` placeholder에 사용자가 외부 진행 후 채울 수 있음.

Phase 8은 architecture refactor 영향 큰 phase (god-function 추출 behavior-preserving + SSE 브릿지 + Critic adapter + prompt semver) → 외부 검증 권장. 단 Phase 4.5/6/5/5.5/7 패턴 계승으로 external placeholder는 **사용자 외부 진행 권장** 형식 유지. self-validation V1~V7 PASS + self-strengthen V-form sub-pattern 가능성 명시. Phase 8 entry 진행 가능.

두 결과 차이 항목 발견 시:
- Phase 8 진행 중 `notes.md`에 기록
- Slice 5 회고 §개선 제안 반영
- Critical 차이 (behavior-preserving 안전성 / Critic canonical 변경 / SSE 브릿지 설계 변경 등) 시 Slice 2 진입 전 사용자 알림

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 5 external: `meta/validations/2026-05-29_phase-5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 7 self: `meta/validations/2026-05-29_phase-7-pre-entry_self.md` (V1~V7 PASS — 네 번째 formal)
- Phase 7 external: `meta/validations/2026-05-29_phase-7-pre-entry_external.md` (placeholder)
- Phase 8 self: 본 문서 (V1~V7 PASS — 다섯 번째 formal)
- Phase 8 external: `meta/validations/2026-05-29_phase-8-pre-entry_external.md` (placeholder)

## Skill 트리거 기록

- **multi-llm-validation**: 다섯 번째 formal 트리거 (Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째 + Phase 8 다섯째) → P-VALIDATION-FORMAL-001 정식 패턴 입증 강화 (5회 누적)
- **ai-architecture-review**: ★ 첫 정식 트리거 (MOA orchestration 설계 검토 → ADR-027 §ai-architecture-review 결과 통합) → unused → active 전환
- **prompt-version-review**: ★ 첫 정식 트리거 (Slice 1 분석 — P-007 Critic 0–5↔0–1 drift + semver 계획 → ADR-029 통합; Slice 4 적용 — P-007 v1.1.0 + consistency test) → unused → active 전환
- **phase-start**: 10번째 트리거 (Phase 1+2+3+4+4.5+6+5+5.5+7+8)
