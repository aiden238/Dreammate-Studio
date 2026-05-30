# Phase 9.5 — Non-Goals

## 명시적 제외 (NG1~NG12)

| ID | 항목 | 이관 | 사유 |
|---|---|---|---|
| **NG1** | RAG eval_rubric → golden_set 정식화 (Phase 7 §6) | Phase 10+ | 사용자 결정 — scope 집중 |
| **NG2** | 실 LLM eval harness 우선 (비결정적, 비용) | 운영 단계 | mock-deterministic primary, 실 LLM은 mode flag + 문서 |
| **NG3** | **run_critic 0–5 출력 제거** | — | P-007 prompt contract (LLM-facing 0–5 유지). 제거 대상은 fallback + schema Optional 필드만 |
| **NG4** | P-AUX-2 brand_memory_extractor agent 구현 | Phase 10+ | 사용자 결정 5 (Phase 9 준비만) |
| **NG5** | 사람 검토(human_review) 실 운영 | 운영 단계 | eval-run §4 사람 채점은 절차만, 자동 채점 primary |
| **NG6** | hook 강도 평가 / 안전 평가 별도 runner | Phase 10+ | golden_set 회귀 + revise effect 집중 |
| **NG7** | async / background eval 큐 | Phase 11+ | sync (moa_policy §4) |
| **NG8** | **PlanCard.tsx 수정** ★ | Phase 11+ | eval은 backend |
| **NG9** | **component_map.md 수정** ★ | Phase 11+ | |
| **NG10** | golden_set 케이스 신규 추가 (47 → 확대) | Phase 10+ | 기존 47 케이스로 runner 구축, 확대는 eval-run §7 절차 후속 |
| **NG11** | prompt A/B 실행 인프라 | Phase 11+ | |
| **NG12** | 영상 자동 편집 / TTS / BGM | **MVP 영구 제외** | |

## 핵심 제약: Critic deprecated 제거의 정확한 경계 (★)

**제거 대상**:
- `select_best_plan_index`의 deprecated fallback branch (overall_score_avg / scores / eight_dim_scores 소비 + `DeprecationWarning`) — Phase 9 wiring으로 canonical 항상 존재 → dead
- `CriticEvaluation` Optional deprecated 필드 (overall_score_avg / scores / eight_dim_scores) — schema

**불변 (제거 X)**:
- `run_critic`의 0–5 출력 (scores dict + overall_score_avg) — **P-007 prompt contract** (NG3). LLM이 0–5 산출 → normalize_to_canonical가 0–1 변환. test_critic의 run_critic 0–5 케이스 보존.
- `normalize_to_canonical`의 0–5→0–1 변환 로직 (scores 읽어 dimensions 생성) — 유지

**의도된 baseline delta**:
- test_critic.py의 select_best_plan_index deprecated-fallback `pytest.warns(DeprecationWarning)` 케이스 (Phase 6 Slice 2 추가) → canonical-only로 갱신 (eval 검증 후, Phase 8 Slice 4 패턴)

## 회피 패턴
- ❌ "deprecated 제거 김에 run_critic 0–5도 제거" → NG3 (P-007 contract)
- ❌ "eval 김에 RAG eval_rubric 정식화도" → NG1
- ❌ "eval 김에 golden_set 케이스 확대도" → NG10
- ❌ eval 검증 없이 deprecated 제거 → 순서 위반 (Slice 2~3 eval → Slice 4 제거)

## 단어 수준 금지 (신규 파일)
- `background task`, `Celery`, `큐` (NG7) / `human_review 자동 실행` (NG5) / `Anthropic`, `Spring`, `Expo` / `자동 편집`, `TTS`, `BGM`
