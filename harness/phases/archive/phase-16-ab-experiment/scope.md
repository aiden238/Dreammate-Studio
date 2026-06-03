# Phase 16 — Scope

## 포함 (in-scope)

- **A/B 실험 하네스** (eval 영역 additive): 동일 입력 × {Arm A, Arm B} 쌍 생성 + 채점 + 차이(B−A) 집계.
  - Arm A = 현재 운영 경로 (`use_rag=False`, brand_memory OFF, PKM 없음).
  - Arm B = `use_rag=True` + brand_memory 주입 + **시뮬 PKM context pack**(PKM/RAG §7 형식 fixture).
  - ★ 단일 변수: 데이터/검색 레이어만 다름. 모델/프롬프트/output_mode/critic/temp = A·B 동일 고정.
- **시뮬 PKM 페르소나 fixture** 2종 (personal/brand/series scope 채움) — 채점 케이스와 분리.
- **정적 측정 (H1)**: `run_golden_set_eval`(구조) + critic real-mode 8~10차원 의미채점 + depth_actionability + 사람 blind 채점 키트(human_review_rubric 재사용).
- **종적 측정 (H2)**: 시뮬 PKM 누적량 N={0,5,20} 단계 주입 → 단계별 B 품질 + 기울기.
- **케이스**: golden_set 25 중 brand/series 맥락 의미있는 ~10 부분집합 (페르소나에 고정).
- **output_mode 고정** = director (A·B 동일 — 차이 가장 잘 드러남).
- 리포트 2종(정적/종적) + go/no-go/partial 종합 + 로드맵 재우선순위 제안.

## 예상 파일 변경 목록

| 분류 | 경로 | 변경 |
|---|---|---|
| editable | `backend/fastapi/eval/` (신규 ab_experiment 모듈) | additive 신규 |
| editable | `backend/fastapi/eval/` 시뮬 PKM fixture | additive 신규 |
| editable | `backend/fastapi/tests/` (실험 하네스 단위 test) | additive 신규 |
| editable | `eval/regression_results/`, `eval/human_review/` | 리포트 신규 |
| editable | `phases/active/phase-16-ab-experiment/`, `PROJECT_STATE.md`, `PHASE_REGISTRY.md` | 상태 |
| editable | `meta/proposals/`, `meta/validations/`, `meta/retrospectives/` | 제안/검증/회고 |
| read-only | `docs/contracts/*`, `ai_system/prompts/*` | 참조만 (닿으면 contract-change) |
| read-only | 운영 agents(planning/critic/orchestrator) | ★ 기존 플래그 **토글만** — OFF 경로 동작 변경 0 |

## real-mode 키 취급 (사용자 결정: ON)

- 키는 `.env`(이미 .gitignore)에만. 코드/commit/채팅 평문 **절대 금지**.
- real-mode 실행은 **opt-in 배치** (CI/pytest는 키 미주입 → mock fallback, 실 호출 0).
