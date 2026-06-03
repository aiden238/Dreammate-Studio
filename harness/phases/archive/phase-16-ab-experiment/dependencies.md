# Phase 16 — Dependencies

## 선행 Phase (모두 done)

| 의존 | 상태 | 무엇을 제공하나 |
|---|---|---|
| Phase 13 (출력 확장 rich) | ✅ done | rich/director 슬롯 + depth 0.231→1.000 척도 (품질 측정 기반) |
| Phase 14 (위저드 실연결) | ✅ done | e2e 흐름 (선행조건 B) |
| Phase 15 (director 모드) | ✅ done | output_mode=director 고정값 + critic 10차원(retention_design) |
| Phase 12 (검증) | ✅ done | depth_actionability(CC-011) + golden_set 25 + human_review_rubric |
| Phase 10/11 (통합/Gateway) | ✅ done | eval real-mode capability + brand_memory_extractor(P-AUX-2) + multi-provider |
| Intent 완화 (CC-021) | ✅ merged | 맨 토픽 수용 — 실험 케이스 입력이 INV-001로 막히지 않음 |

→ PKM/RAG 제안서 §0.2 선행조건 A·B **모두 충족**. 실험 entry 자격 있음.

## 재사용 자산 (기존 — 신규 최소화)

```
config.use_rag / effective_output_mode / brand_memory 주입 경로   ← Arm 토글
eval/runner.py run_golden_set_eval + eval/mode.py (real-mode ScoreContext)  ← 측정
critic.py DIMENSIONS_DIRECTOR(10) + depth_actionability             ← 의미채점
eval/human_review_rubric.md                                         ← blind 채점
rag/feedback_to_candidate.py / brand_memory_repo                    ← (참조) compounding 시뮬 형식
PKM/RAG 제안서 §7 context pack 형식                                  ← 시뮬 fixture 스펙
```

## 외부 의존 / 불확실

- real-mode 의미채점 = LLM 키(.env, user-provided) — 미제공 시 mock fallback(H1 약).
- LLM 비결정성 — 동일 입력도 출력 변동 → 페어 다수회/평균으로 완화(assumptions U2).
