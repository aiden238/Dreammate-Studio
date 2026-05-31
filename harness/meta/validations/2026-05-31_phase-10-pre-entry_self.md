# Phase 10 Pre-Entry Self-Validation (multi-llm-validation formal — 열 번째)

> 작성: Claude Code 자가 검증 (CLAUDE.md + contracts + ADR-031/033 + patterns 참조)
> 날짜: 2026-05-31
> 대상: Phase 10 (MVP 통합 테스트, scope C) 진입 타당성
> 외부: `2026-05-31_phase-10-pre-entry_external.md` (placeholder)
> ★ P-VALIDATION-FORMAL-001 열 번째 (M0~M3 meta-phase 8~9 에 이은 — 제품 phase 복귀, V dimension 제품 통합 영역)

---

## V1 — 통합 범위 타당성 → ✅ PASS
- Phase 1~9.5 가 개별 동작/test(339) 통과 → Phase 10 은 **연결/통합 검증**이 자연스러운 다음 단계. end-to-end 흐름(Discovery+Quick→3안→Critic revise canonical→save→select→feedback→SSE)이 실제 endpoint 들로 구성됨(Phase 1/4/5/8/9). 통합 테스트로 연결성 확인 타당.
- 범위 C(풀)는 사용자 결정 — 통합 + P-AUX-2 + eval 성숙 + 배포 준비. 단 신규 product 기능 0(통합·준비 phase) → scope creep 은 NG3~NG7(Phase 11+)로 차단.

## V2 — P-AUX-2 additive 회귀 0 → ✅ PASS (조건)
- Phase 9 가 brand_memory_repo + feedback→candidate 적재 경로 준비(ADR-031) → Phase 10 은 **추출 agent 만 추가**. orchestrator 경유 additive, 기존 MOA 응답 불변.
- ⚠ 조건: 기존 endpoint/agent 응답 schema 변경 0 (behavior-preserving). agent-io-check 로 정합 + pytest 339 기존 수정 0 게이트. P-AUX-2 는 비동기/후처리 성격(피드백 후 추출)이라 동기 응답 경로 무영향.

## V3 — eval mode 경계 (default mock) → ✅ PASS
- 사용자 결정: 실 LLM eval mode = **capability(경로 wire + 문서)만**, default 실행 mock-deterministic. ADR-033 "mock primary + 실 LLM mode flag" 정합 — flag 의 실 경로를 채우되 default off.
- ★ 실 키/자격증명 파일 커밋 0 (.env user-provided). 실 LLM run 은 opt-in (Phase 10 CI 미실행). NG2 명시.

## V4 — behavior-preserving → ✅ PASS
- 제품 phase 핵심 게이트: 기존 endpoint/test 동작 불변 + 신규 추가만. pytest 339 전부 green + 신규 추가분만 증가. Phase 8 P-BEHAVIOR-PRESERVING-001 정신 계승.
- 통합 테스트는 기존 흐름을 **관찰**(mock-deterministic chaining)하지 변경하지 않음. PlanCard/component_map 0줄(page 레벨).

## V5 — golden_set 확대 + RAG rubric → ✅ PASS
- golden_set 11→확대는 **추가만**(기존 11 회귀 보존) + eval gate 신구 비교. RAG eval_rubric 은 신규 contract(Phase 9.5 NG1 이관) — contract-change(CC-009) 경유.
- eval-design/eval-run Skill(Phase 9.5 첫 정식)로 절차 통과.

## V6 — 배포 게이트 준비 범위 → ✅ PASS
- Deploy Test A~G 는 **준비 문서/체크리스트**까지 (실 배포·운영 SQL function 정의는 NG11, 운영 단계). 배포 게이트 준비는 통합 phase 의 자연스러운 마무리.

---

## 종합
| V | 항목 | 결과 |
|---|---|---|
| V1 | 통합 범위 타당성 | ✅ PASS |
| V2 | P-AUX-2 additive 회귀 0 | ✅ PASS (behavior-preserving 조건) |
| V3 | eval mode 경계 (default mock + 키 커밋 0) | ✅ PASS |
| V4 | behavior-preserving | ✅ PASS |
| V5 | golden_set 확대 + RAG rubric (additive + contract-change) | ✅ PASS |
| V6 | 배포 게이트 준비 범위 | ✅ PASS |

**판정**: Phase 10 진입 타당 (V1~V6 PASS). 조건 — behavior-preserving(기존 0 수정) + eval default mock + 키 커밋 0 + P-AUX-2 additive(orchestrator 경유).
**P-VALIDATION-FORMAL-001 열 번째** (M-detour 종료 후 제품 phase 복귀 — V dimension 을 제품 통합/배포 준비 영역으로 확장).
