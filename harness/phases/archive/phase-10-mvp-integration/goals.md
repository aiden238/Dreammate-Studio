# Phase 10 — Goals (MVP 통합 테스트, scope C)

> Phase: phase-10-mvp-integration
> 유형: **제품 phase (large, ~12~18h)** — ★ 런타임 변경 有 (A9 미적용. meta-phase detour 종료, 제품 로드맵 복귀)
> 진입일: 2026-05-31
> 결정 근거: 사용자 — 범위 **C(풀)** + eval 실행 **mock-deterministic 유지**

## 한 줄 정의

Phase 1~9.5 누적 MVP(Discovery+Quick → 3안 → Critic revise(canonical) → save → select → feedback → SSE)를 **end-to-end 통합 검증**하고, **P-AUX-2 brand_memory_extractor agent 실 구현** + **실 LLM eval mode 정식화(capability — default 는 mock 유지)** + **RAG eval_rubric golden_set 정식화** + **golden_set 11→확대** + **배포 테스트 게이트 A~G 준비**를 수행한다.

## ★ scope C 결정 + eval mode 화해

```
범위 C (풀)   : 핵심 통합 + P-AUX-2 agent 실구현 + 실 LLM eval mode + RAG rubric + golden_set 확대 + 배포 게이트
eval 실행     : ★ mock-deterministic 유지 (CI 게이트, 비용 0)
실 LLM mode   : capability 정식화(경로 wire + 문서)까지 — default off. 키 제공 시 opt-in run (Phase 10 CI 에선 미실행)
```
→ "실 LLM eval mode 활성"(C) = **모드 capability 구축** / "mock 유지"(eval mode) = **default 실행은 mock**. ADR-033 "mock primary + 실 LLM mode flag" 정합.

## 핵심 목표 (G1~G7)

| ID | 목표 | Slice |
|---|---|---|
| **G1** | MVP **end-to-end 통합 검증** — 전체 흐름(Discovery+Quick → 3안 → Critic revise → save → select → feedback → SSE) 자동 통합 테스트 | S1 |
| **G2** | Phase 1~9.5 **누적 baseline 통합 회귀** — pytest 339 + smoke + scenario_sim 통합 게이트 (smoke_test_phase_10 + scenario_sim v8) | S1 |
| **G3** | **P-AUX-2 brand_memory_extractor agent 실 구현** — feedback → brand memory 추출 (Phase 9 brand_memory_repo/적재 경로 활성, ADR-031) | S2 |
| **G4** | **실 LLM eval mode 정식화 (capability)** — ADR-033 mode flag 실 경로 wire + 문서. ★ default mock 유지 | S3 |
| **G5** | **RAG eval_rubric golden_set 정식화** (Phase 9.5 NG1 이관) + **golden_set 11→확대** (Phase 9.5 개선 §3) | S3 |
| **G6** | **배포 테스트 게이트 A~G 준비** (Deploy Test A~G 체크리스트/문서) | S4 |
| **G7** | 통합 회귀 0 — 기존 endpoint/test behavior-preserving (신규 추가만, 기존 동작 불변) | 전 Slice |

## 메타 목표 (MG1~MG4)

| ID | 목표 |
|---|---|
| **MG1** | multi-llm-validation formal **열 번째** (통합 범위 + P-AUX-2 agent IO + eval mode 경계) + external placeholder |
| **MG2** | contract-change — agent_io_contract(P-AUX-2 IO) + eval contracts(golden_set 확대 + RAG rubric) (CC-008+) |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 (57 → +Slice 수) |
| **MG4** | pytest 339 → 확대 (+신규, 기존 수정 0 — behavior-preserving) + eval gate PASS |

## 사용자 가치 (Why)
- **MVP 완성도 입증**: 9.5 phase 누적이 실제로 end-to-end 연결되는지 통합 검증 → 배포 준비 baseline.
- **Brand Memory 활성**: P-AUX-2 로 피드백 데이터가 brand memory 로 전환 (Phase 9 준비 → Phase 10 실현).
- **eval 성숙**: 실 LLM mode capability + RAG rubric + golden_set 확대 → 품질 평가 체계 완성도 ↑.
- **배포 준비**: Deploy Test A~G 게이트 준비 → 알파/베타 진입 기반.

## ★ 절대 금지 (non_goals.md 상세)
영상 제작/편집·TTS·BGM (MVP 영구 non-goal) / 실 LLM eval **default 활성**(capability 만, default mock) / 4계층 full linkage(Phase 11+) / SSE full async worker(Phase 11+) / prompt A/B 인프라(Phase 11+) / 새 product 기능(통합·안정화·준비 phase).
