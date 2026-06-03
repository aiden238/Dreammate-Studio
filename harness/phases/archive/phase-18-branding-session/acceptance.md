# Phase 18 — Acceptance

```
A1. S1 topic_discovery agent — ask(상태→다음 질문 1개 + 카드 2~4개 or 종료신호) /
    finalize(상태→후보 주제 3개 × {topic,tone,target,format,why_fit}). prompt_registry 등록. [단위 test mock]
A2. S2 branding endpoint — next/finalize 동작 + Q&A 상태 누적(plan_entry.wizard_data.branding).
    N고개 상한 종료. [agent-io-check + 단위 test]
A3. S3 frontend /new/branding — 질문 카드+자유입력+진행바 → 후보 3 → 택1 → /plan/[id]. [build + 수동]
A4. S4 planning 연결 — 택1 topic/방향 → initial_input/approved_direction → 기존 3안 생성.
    + brand_memory 시드(gated, ≥0.9/proposal governance). [단위 test + 라이브 1건]
A5. behavior-preserving — Quick/Discovery/planning/output byte-identical. 기존 pytest 608 green + audit 0.
A6. contract-change 규율 — prompt_registry(P-신규) + (스키마 닿으면) contract-change 경유.
A7. phase-complete — gates + 회고 + archive + REGISTRY/STATE.
```

## 검증 매핑
| 기준 | 방법 |
|---|---|
| A1/A2 | 단위 test(mock LLM) — ask 질문+카드 / finalize 후보3 / 상태 누적 |
| A4 | 단위 test(주입 gated) + real-mode 1건(스무고개→주제→생성) |
| A5 | pytest 608 baseline + scenario_sim 36 + audit 0 |
