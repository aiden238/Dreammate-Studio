# Phase 8 — Closing Notes

> 종료일: 2026-05-29
> 결과: A1~A10 10/10 + M1~M5 5/5 PASS
> 다음 phase: **🟡 pending_user_decision** (A Phase 9 저장-피드백 / B Phase 9.5 eval-run / C Phase 10 통합 / D Phase 11+)

---

## 최종 산출물

### Backend orchestration layer (~+700 LOC, 5 신규)
- `backend/fastapi/orchestration/__init__.py` (export — generate_plan + ProgressSink + NullProgressSink + StoreProgressSink + progress_store)
- `backend/fastapi/orchestration/responses.py` (now_iso / not_found / error_envelope helper — orchestrator/router 공유)
- `backend/fastapi/orchestration/progress_sink.py` (`ProgressSink` Protocol + `NullProgressSink` no-op default + `StoreProgressSink` → progress_store record)
- `backend/fastapi/orchestration/moa_orchestrator.py` (`async def generate_plan(...)` — `plans_generate()` body 이관, Intent→RAG→3-plan→Critic+revise→save→Envelope, stage별 progress.emit)
- `backend/fastapi/orchestration/progress_store.py` (`_store: dict[str, list[dict]]` in-memory graceful + record / read / clear + TTL/maxlen 누수 방지)

### Backend 수정 (2 routers + 1 agent)
- `backend/fastapi/routers/plans.py` (thin adapter화 — god-function 659→243 LOC, `return await generate_plan(...)` + StoreProgressSink 주입)
- `backend/fastapi/routers/sse.py` (실 stage read — progress_store 우선 + graceful fallback 기존 mock 4단계 보존)
- `backend/fastapi/agents/critic.py` (PROMPT_VERSION v1.0.0→v1.1.0 + `normalize_to_canonical` helper additive, run_critic 미강제 → 회귀 0)

### Tests (+26 신규)
- `test_moa_orchestrator.py` — generate_plan 기본 (mock agents) + ProgressSink emit stage별 + NullProgressSink 회귀 0 + 에러 경로 (Intent 차단 / Planning 실패) 보존
- `test_sse_integration.py` — progress_store record → sse read round-trip + graceful fallback (store empty → mock) + clear on complete
- `test_prompt_registry_consistency.py` — 각 agent PROMPT_ID/VERSION 상수 ↔ registry 정합 + normalize_to_canonical 0–5→0–1 + registry 문서화 검증
- (의도된 baseline delta 2) test_critic.py:93 + test_e2e_slice1.py:172 — Critic v1.1.0 version-string assertion (Phase 6 Rewriter 선례)

### Contracts / ADRs
- `docs/decisions/phase_8_moa_orchestrator.md` (ADR-027, Slice 1 — ai-architecture-review Skill 첫 정식)
- `docs/decisions/phase_8_sse_progress_integration.md` (ADR-028, Slice 1)
- `docs/decisions/phase_8_prompt_registry_semver.md` (ADR-029, Slice 1 — prompt-version-review Skill 첫 정식 + §Amendment)
- `ai_system/prompts/prompt_registry.md` (P-001~P-008 + AUX semver 정식화 + P-007 §0–5↔0–1 adapter, Slice 4)
- `docs/contracts/agent_io_contract.md` (v1.2.0 §5 Critic v1.1.0 adapter + §8 orchestrator 중개, Slice 4)
- `ai_system/orchestration/moa_policy.md` (§2 moa_orchestrator.py cross-ref, Slice 4)
- `meta/proposals/2026-05-29_phase-8-slice-4-prompt-registry-semver.md` + `docs/contract_changes/...` (CC-003)

### Meta
- `meta/validations/2026-05-29_phase-8-pre-entry_self.md` (V1~V7 PASS — formal 다섯 번째)
- `meta/validations/2026-05-29_phase-8-pre-entry_external.md` (placeholder)
- `meta/retrospectives/phase-8.md` (본 phase 회고)
- `meta/patterns.md` (P-MOA-ORCHESTRATOR-001 신규 + P-BEHAVIOR-PRESERVING-001 신규 + P-X1-EFFECT-001 update 36연속 + P-VALIDATION-FORMAL-001 update 다섯 번째)
- `meta/skill_usage_log.md` (Phase 8 사용 요약 10 Skill — ai-architecture-review + prompt-version-review 첫 정식)

### Scripts
- `scripts/smoke_test_phase_8.ps1` 신규 (14 체크 — 13 PASS + 1 WARN intended)
- `scripts/scenario_simulation.ps1 v4` (20 시나리오, S16~S20 MOA 추가, P-X2 여섯 번째)

---

## Phase 8 핵심 baseline

| 지표 | Phase 8 종료 |
|---|---|
| pytest | **249/249** (Phase 7 223 baseline + 26 신규) |
| smoke_test_phase_8 | **14/14** (13 PASS + 1 WARN intended — Phase 5 baseline AuthGuard + /login) |
| scenario_simulation v4 | **20/20** (P-X2 여섯 번째 자동 게이트) |
| schema_stress_test | 5/5 (Phase 6 v2 유지) |
| audit_naming | 0 drift |
| audit_page_component | 2 intended WARN (Phase 5 baseline 계승) |
| plans.py LOC | **659 → 243** (god-function 분해, thin adapter) |
| component_map.md 0줄 | **34연속** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5) |
| PlanCard.tsx 0줄 | **24연속** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5) |
| P-X1 streak | **36연속** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5) |

---

## 다음 Phase 옵션 (사용자 결정 대기)

### A. Phase 9 — 결과 저장 + 피드백 (6~10h)
- 사용자 plan 선택 / 수정 / 반려 누적
- Phase 5 plans_repo + RLS + Phase 7 RAG + Phase 8 orchestrator 활용
- **Brand Memory 자동 추출 ADR 신규** (개선 제안 §5, 사용자 결정 5 누적 3회 confirm)
- **normalize_to_canonical wiring 연결** (개선 제안 §1) + per-user rate-limit + audit-log

### B. Phase 9.5+ — eval-run Skill 정식화 (4~6h)
- golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 6회 deferred 해소)
- **Critic deprecated 0–5 fallback 완전 제거** (개선 제안 §4, Phase 6 ADR-018 다음 단계 누적 2회)
- 간이 RAG eval_rubric → golden_set 기반 정식 (Phase 7 개선 제안 §6 흡수)
- **eval-design + eval-run Skill 첫 정식 트리거 baseline**

### C. Phase 10 — MVP 통합 테스트 (6~8h)
- MVP 전체 end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise → save → SSE progress)
- Phase 1~8 누적 baseline 통합 회귀
- 배포 테스트 게이트 A~G 준비

### D. 다른 우선순위 (Phase 11+)
- **SSE full async worker** (개선 제안 §2, 누적 2회 — Phase 5 + Phase 8)
- **prompt A/B 실행 인프라** (개선 제안 §3 — multi-provider 대비, prompt-version-review 두 번째 트리거)
- 사용자 데이터 자동 promotion (rag-update Skill 두 번째)
- Supabase SQL function `match_approved_knowledge` 정의 (운영 단계 필수) / cost-review Skill 정식화

---

## 운영 단계 권장

- **normalize_to_canonical wiring 연결** — Phase 9+ 결과 저장 시점 (현재 additive helper, run_critic 미강제 → canonical 우선순위 실 활성 필요, 개선 제안 §1)
- **SSE full async worker** — Phase 11+ (현재 in-memory single-process best-effort, multi-worker / multi-client broadcast 시 필수, ADR-028 §full async, 개선 제안 §2)
- **prompt A/B 실행 인프라** — Phase 11+ multi-provider 대비 (semver 정식화 완료 → A/B 단계적 활성화 10%→50%→100%, 확정 결정 [20], 개선 제안 §3)
- **Critic deprecated 0–5 fallback 완전 제거** — Phase 9+ eval-run 정식화 후 (현재 conservative adapter로 0–5 병행 유지 회귀 0 우선, 개선 제안 §4)
- **Brand Memory 자동 추출 ADR** — Phase 9+ MVP 본격 운영 후 (사용자 결정 5 누적 3회 confirm, 개선 제안 §5)

---

## Phase 8 사용자 결정 1:1 mapping (3건, 2026-05-29 entry 시 명시)

| 결정 ID | 결정 내용 | Phase 8 mapping |
|---|---|---|
| Scope | A orchestrator + B SSE + C prompt_registry (3개 모두, 5 Slice, 12~16h) | ✅ ADR-027 (orchestrator) + ADR-028 (SSE progress_store) + ADR-029 (prompt_registry semver) — 5 Slice 전부 구현 |
| Critic drift | Conservative adapter — Phase 6 canonical(0–1) 불변 + P-007 prompt(0–5) 유지 + 코드 0–1 정규화 + v1.0.0→v1.1.0 | ✅ critic.py PROMPT_VERSION v1.1.0 + normalize_to_canonical helper additive (run_critic 미강제 → 회귀 0) + ADR-029 §Amendment + agent_io_contract §5 v1.1.0 adapter |
| SSE 통합 | in-memory progress_store 브릿지 (graceful, background task 미도입 — moa_policy §4 sync, async Phase 11+) | ✅ progress_store.py in-memory + StoreProgressSink + sse.py 실 stage read + graceful fallback (기존 mock 4단계 보존) + background task 미도입 |

추가 결정 0건 (entry 시점 3건 명시 → Slice 진행 중 추가 결정 없이 그대로 채택). Slice 1 Gap 정정 1건 (run_critic 0–5 deprecated → conservative adapter 필요성 정당화 강화, ADR-029 §Amendment).

---

## 변경 이력

- 2026-05-29: Phase 8 closing notes 최초 작성 (Slice 5 final). A1~A10 10/10 + M1~M5 5/5 PASS. **ai-architecture-review + prompt-version-review Skill 둘 다 ★ 첫 정식 트리거 완료 + ADR-027/028/029 + contract-change CC-003 (prompt_registry semver + agent_io_contract v1.2.0) + MOA orchestrator 추출 (plans.py 659→243 god-function 분해) + behavior-preserving (Envelope byte-identical, 기존 test 수정 0 의도된 2 version assertion 제외) + SSE 실 stage 통합 + Critic v1.1.0 conservative adapter (Phase 6 canonical 불변) + P-MOA-ORCHESTRATOR-001/P-BEHAVIOR-PRESERVING-001 신규 후보 + P-X1 36연속 + PlanCard 24연속 + component_map 34연속 + pytest 249/249 + smoke 14/14 + scenario_sim v4 20/20 + P-X2 여섯 번째 자동 게이트**. 다음 phase = 🟡 pending_user_decision (옵션 A Phase 9 저장-피드백 / B Phase 9.5 eval-run / C Phase 10 통합 / D Phase 11+).
