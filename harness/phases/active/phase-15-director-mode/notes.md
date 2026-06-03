# Phase 15 — Notes (진행 메모)

## 진입 (2026-06-03)
- 사용자 결정: 로드맵 ① director(본) → ② 검증 보강 → ③ PKM/RAG 데이터레이어 기획안. "이대로 진행".
- 기반: project-1 PARKED 제안서 `meta/proposals/2026-06-03_commercial-viral-mode-design.md`.
- director = output_mode 3rd tier(compact<rich<director), rich + 연출/리텐션 슬롯, LLM-only(데이터레이어 비의존), gated/additive/OFF byte-identical.
- baseline: pytest 508 / origin main 748efe2 / Phase 14 done.

## 확정 설계 (제안서 open issue 해소)
- **director 슬롯 경계(#1)**: hook_system + retention_architecture + scene_breakdown(director-subset 5필드). 상업필드 = commercial_viral(NG1).
- **flag→enum(#2)**: rich_output_enabled → output_mode enum, backward-compat 매핑.

## TODO
- [ ] S1 output_mode enum + director 스키마 + model_dump 모드별(compact/rich byte-identical) + agent-io-check
- [ ] S2 P-006 director 프롬프트(v1.2.0, gated)
- [ ] S3 gated wiring(output_mode 분기)
- [ ] S4 Critic director 차원(retention_design, P-007 v1.3.0)
- [ ] S5 frontend PlanCard director 조건부
- [ ] S6 cost + director depth 측정 + close

## 참조
- ★ **Phase 15 전체 기획안(구현 spec)**: `meta/proposals/2026-06-03_phase-15-director-mode-plan.md` — entry 통합 + 구체 설계(enum 매핑/DirectorScene/model_dump_for_mode/프롬프트 구조/critic 차원/slice 상세).
- 기반 제안서 §2(스키마)/§3(P-006)/§4(critic)/§6(cost)/§7(단계화·의존성).
- sibling: `2026-06-03_pkm-rag-orchestrator-design.md`(로드맵 ③).
- 계승 패턴: P-GATED-OUTPUT-CHANGE-001(Phase 13) + P-WIZARD-WIRING-001(Phase 14).
