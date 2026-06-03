# Phase 16 — 진입 4점검 (phase-start §6)

## 1. Assumptions

### 1.1 확정 가정

- 선행조건 A(Phase 13 rich 실사용 검증) + B(Phase 14 위저드 실연결) 충족 (dependencies.md).
- 기존 플래그(`use_rag`/`effective_output_mode`/brand_memory 주입)로 A/B arm을 **코드 분기 없이 토글** 가능 (config 실측).
- eval real-mode capability 존재 (Phase 10, `eval/mode.py` ScoreContext + 키 opt-in).
- critic director 10차원 + depth_actionability 존재 (Phase 13/15).
- **audit_naming 통과 (2026-06-03, 0 drift)** — contract cross-ref drift 없음.
- 사용자 결정: real-mode ON(키 제공). output_mode=director / 페르소나 2 / 케이스 ~10 / N={0,5,20} (기획안 §8 default).

### 1.2 불확실 항목 (phase-complete 시 회고)

- **U1**: 시뮬 PKM이 실제 누적 데이터를 얼마나 대표하는가 (proxy 한계 — 기획안 §5.1). 사람 blind로 보정.
- **U2**: LLM 비결정성 → B−A 측정 노이즈. 페어 다수회 평균 + 동일 seed/temp 고정으로 완화.
- **U3**: real-mode 비용/latency 실측 미상 (케이스 ~10 × arm 2 × N 3단계 × 반복). S1에서 소규모로 먼저 측정.
- **U4**: go/no-go 임계값(+0.15 / 65%)은 rough — A5 multi-llm-validation에서 확정.

## 2. Simplest Slice (3회 압축)

```
1차: A/B 토글 + 시뮬 PKM + 정적(H1) + 사람 blind + 종적(H2) 전부.
2차: 동일 입력 1케이스 × {A,B} 2회 생성 → critic real-mode 채점 → B−A 숫자 1개.
3차: run_planning을 (use_rag OFF) vs (use_rag ON + brand_memory + 시뮬 PKM 1건) 1쌍 생성하고
     real-mode critic으로 채점해 B−A 단일 숫자 + 통제(파라미터 diff=컨텍스트만) 입증.
     ← ★ Simplest Slice = S1
```

→ S1이 "B−A 숫자 1개 + 통제 입증"을 내면, 케이스 부분집합(S2) → 사람 blind(S3) → 종적(S4) → 종합(S5)로 확장.

## 3. Surgical Scope

| 분류 | 대상 |
|---|---|
| **editable** | `backend/fastapi/eval/` (실험 하네스 + 시뮬 fixture, additive) · `backend/fastapi/tests/` (실험 test) · `eval/regression_results/` · `eval/human_review/` · `phases/active/phase-16-ab-experiment/` · 상태파일(`PROJECT_STATE`/`PHASE_REGISTRY`) · `meta/{proposals,validations,retrospectives}/` |
| **read-only** | `docs/contracts/*` · `ai_system/prompts/*` (닿으면 contract-change) · 운영 agents(planning/critic/orchestrator/config) — ★ 기존 플래그 **토글만**, OFF 경로 동작 변경 0 |
| **forbidden** | `phases/archive/*` · 신규 endpoint/agent/migration · 실 PKM/RAG orchestrator 구현 · commercial_viral |

★ Sub-agent 사용 시 P-X1 §SELF-VERIFICATION(git diff --stat 자기검증) 의무.

## 4. Verification (acceptance 매핑)

| acceptance | 검증 방법 | 자동/수동 |
|---|---|---|
| A1 통제 | 단위 test — 두 arm 호출 파라미터 diff = 컨텍스트만 | 자동 |
| A2 정적 H1 | real-mode 배치(opt-in) + 리포트 | 자동(배치) |
| A3 사람 blind | 채점 키트 + 사용자 채점 | 수동 |
| A4 종적 H2 | N={0,5,20} 배치 + 기울기 | 자동(배치) |
| A5 종합 | go/no-go/partial 리포트 + multi-llm-validation | 혼합 |
| A6 behavior-preserving | pytest baseline green + audit_naming 0 | 자동 |
| A7 종료 | phase-complete (smoke/scenario_sim/회고/archive) | 절차 |
