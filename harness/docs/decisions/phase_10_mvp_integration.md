# ADR-038: Phase 10 MVP 통합 테스트 (scope C)

> 상태: Accepted
> 결정일: 2026-05-31
> Phase: 10 (MVP 통합 테스트) — 제품 phase (런타임 변경 有)
> 관련: ADR-031(Brand Memory prep) / ADR-033(eval-run harness) / CC-008(P-AUX-2 IO) / CC-009(eval)
> ★ behavior-preserving (기존 0 수정) + eval default mock + 키 커밋 0

---

## Context

Meta-Factory detour(M0~M3) 종료 후 제품 로드맵 복귀. Phase 1~9.5 가 개별 동작/test(339) 통과 → MVP end-to-end **통합 검증** + 준비된 것(P-AUX-2) 활성 + eval 성숙 + 배포 준비가 다음 단계. 사용자 결정: 범위 **C(풀)** + eval 실행 **mock-deterministic 유지**.

## Decision

Phase 10 을 4 Slice 로 수행:
1. **S1 MVP end-to-end 통합** — test_integration_mvp.py 로 전체 흐름(Discovery+Quick→3안→Critic revise canonical→save→select→feedback→SSE) chaining 검증 + 누적 baseline 회귀(smoke_test_phase_10 + scenario_sim v8). mock-deterministic.
2. **S2 P-AUX-2 brand_memory_extractor agent** — heuristic(LLM 0) 추출 + graceful + PII 마스킹, feedback endpoint additive best-effort hook(proposed-only, 자동 INSERT 0). CC-008.
3. **S3 eval 정식화** — 실 LLM eval mode **capability**(default mock, graceful fallback, 실 호출 0, 키 0) + RAG eval_rubric v1.0.0 + golden_set 11→15. CC-009.
4. **S4 배포 게이트 A~G 준비** + close.

★ **eval mode 화해**: "실 LLM eval mode 활성"(범위 C) = mode capability 구축 / "mock 유지"(eval mode 결정) = default 실행 mock. ADR-033 "mock primary + 실 LLM mode flag" 정합. 실 LLM run = opt-in(키 주입 시, Phase 10 CI 미실행).

## Result

- **MVP end-to-end 통합 PASS** — 전 흐름 정상 연결(결함 0). pytest 339 → **381**(+42: 통합 12 + P-AUX-2 14 + eval 16). 기존 339 green 유지(의도된 eval delta 제외).
- **P-AUX-2 brand_memory_extractor** 실 구현(heuristic, 비용 0) — Phase 9 적재 경로 활성. additive(기존 MOA 응답 불변), agent-io-check PASS.
- **eval 성숙** — 실 LLM mode capability(default mock) + RAG eval_rubric 정식화 + golden_set 15 + eval-run mock gate PASS.
- **배포 게이트 A~G 준비** — Gate A 통과(local smoke), B~D 준비, E/G 운영 단계.
- ★ behavior-preserving(기존 endpoint/agent 불변) + 키 커밋 0 + PlanCard/component_map 0줄 유지 + P-X1 연속.

## Consequences

### 긍정
- MVP 완성도 입증 — 9.5 phase 누적이 실제 end-to-end 연결됨을 자동 통합 test 로 확인. 배포 준비 baseline.
- Brand Memory 루프 활성 — 피드백 → brand memory 추출(P-AUX-2). Phase 9 준비 → Phase 10 실현.
- eval 체계 성숙 — 실 LLM capability(opt-in) + RAG rubric + golden_set 확대.
- 배포 게이트 A~G 정의 — 알파/베타 진입 기반.

### 제약 / 한계
- **eval 실 LLM 미실행** — capability 만(default mock). 실 품질 측정은 Beta(Gate D) 키 주입 시.
- **P-AUX-2 proposed-only** — 자동 INSERT 0(NG12). 실 promotion 은 Phase 11+.
- **통합 mock-deterministic** — 실 외부 의존(Supabase/LLM) 미통합 검증. Gate B/C 실 환경에서.
- Gate E/G(제한 사용자/운영) 미준비 — 운영 인프라·키 단계.

## Non-Goals (재확인)
- 영상 제작(영구) / 실 LLM eval default 활성(capability 만) / 4계층 full linkage / SSE async worker / prompt A/B (Phase 11+).

## 다음
- Gate B~G 진행(staging→베타→운영) — 키·인프라 user-provided + 운영 phase.
- Phase 11+: 4계층 linkage / SSE async / prompt A/B / 자동 promotion / 실 LLM eval default 전환 / M3 새 GAP 반영.
