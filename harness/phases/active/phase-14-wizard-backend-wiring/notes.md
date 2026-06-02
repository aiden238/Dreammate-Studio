# Phase 14 — Notes (진행 메모)

## 진입 (2026-06-03)
- 방향 결정: **Scope A(최소 배선)** — project-1(메인 세션 6f30283a) 위저드 분석 검토 결과.
  - project-1 결론: 위저드 mock, 랜딩 `/` 만 실동작, 실연결=한 페이즈 분량, per-step 실 LLM 카드=PKM/RAG(PARKED).
  - → Phase 14 = 위저드 입력 → 실 생성(/generate) 배선 → /plan/[id] rich. per-step LLM 은 NG1(PARKED 이연).
- Phase 13 done(archive) 직후, active phase 없음 상태에서 진입. baseline: pytest 499 / origin main 6574da9 / 키 0.

## 핵심 사실 (실측, project-1 + 직접 확인)
- 기존 endpoint/클라이언트 함수 전부 존재 → **신규 endpoint 0**, 배선만.
- 생성 입력 = `moa_orchestrator.py:88` `plan_entry["initial_input"]`. wizard_data 는 현재 미소비 → S1 에서 additive 조립.
- rich gated 는 /generate 경로 내부 → 위저드 자동 상속.
- 랜딩 `/`(dreammate.slice6.plan → /plan) vs 위저드(wizard.* 키, /plan 미연동) 분리 → 위저드를 /plan/[plan_id](백엔드 read)로 수렴.

## 참조
- project-1 세션(6f30283a, 유지 중) = in-context 위저드 분석 원본 (L6614~6790).
- handoff: `meta/handoffs/2026-06-03_checkpoint-phase13-done.md`.
- PARKED: `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md`(per-step 지능 = 여기) / `2026-06-03_commercial-viral-mode-design.md`.

## TODO (slice 진행하며 갱신)
- [ ] S1 백엔드 wizard_data 조립 (additive, 랜딩 byte-identical) + tests
- [ ] S2 Quick 위저드 실연결
- [ ] S3 Discovery 위저드 실연결
- [ ] S4 라이브 e2e(rich ON) + 회귀 + close
