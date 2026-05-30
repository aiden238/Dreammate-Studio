# Phase 9 — Goals

> Phase: phase-9-result-feedback
> 유형: large phase (결과 저장 + 피드백 + Brand Memory 준비 + normalize wiring + 피드백 UI)
> 진입일: 2026-05-29
> 예상 시간: 10~14h (6 Slice 모두 sub-agent dispatch)

## 한 줄 정의

사용자의 **plan 선택 / 수정 / 반려 / 피드백을 영속화**(Phase 5 PlansRepo graceful 패턴)하고, **Critic canonical(0–1)을 live pipeline에 연결**(normalize_to_canonical wiring)하며, **Brand Memory 자동 추출을 위한 schema + ADR + 피드백 적재 경로를 준비**(P-AUX-2 agent는 Phase 10+ 이관)하고, **선택/반려 피드백 UI를 wrapper로 추가**(PlanCard 무수정)하여 MVP 피드백 루프를 완성한다.

## 핵심 목표 (G1~G8)

| ID | 목표 | 검증 |
|---|---|---|
| **G1** | 결과 저장 — `selected_plans` (plan 선택 + option_index 0–2 + 사유) 영속화 (실 `plans` 테이블 정합) | A1, A2 |
| **G2** | 피드백 — `feedback_events` (like/dislike/reject/regenerate + reason) 영속화 | A3 |
| **G3** | repo graceful — selection_repo / feedback_repo (Supabase 실패 시 in-memory, PlansRepo 패턴) | A4 |
| **G4** | API endpoints — POST /plans/{id}/select + POST /plans/{id}/feedback + GET 조회 + orchestrator 정합 | A5 |
| **G5** | **normalize_to_canonical wiring** — critic step → canonical(0–1) 저장 (deprecated 0–5 병행 회귀 0, Phase 8 개선 §1) | A6 |
| **G6** | Brand Memory **준비** — `brand_memory_entries` schema + 피드백→candidate_knowledge source_kind 적재 경로 + **P-AUX-2 ADR** (agent 미구현, Phase 10+) | A7 |
| **G7** | **피드백 UI wrapper** — 선택 버튼 + 반려 이유 입력 (page.tsx inline, **PlanCard·component_map 무수정**) | A8 |
| **G8** | 회귀 0 — Phase 8 baseline (pytest 249 + smoke 14 + scenario_sim v4 20) 유지/확장 | A9, A10 |

## 메타 목표 (M1~M4)

| ID | 목표 |
|---|---|
| **M1** | multi-llm-validation **formal self** 여섯 번째 + external placeholder |
| **M2** | **security-review Skill 두 번째 정식** (피드백 reason text PII + reject 사유 저장 보안) |
| **M3** | contract-change Skill (db_schema.md feedback/selection 정식 등록 — 실 plans 테이블 정합) |
| **M4** | P-X1 §SELF-VERIFICATION **42연속 PASS** (Phase 8:36 + Phase 9:6) |

## 사용자 가치 (Why)

- **피드백 루프 완성**: 사용자 선택/반려 누적 → 추후 Brand Memory / RAG 자동 promotion / eval 의 데이터 기반 (Phase 10+/11+)
- **Critic canonical 활성**: 0–1 dimensions 저장 → 추후 best-plan 정확도 + eval 정합 (Phase 9.5 eval-run baseline)
- **Brand Memory 준비**: 사용자 결정 5 — 자동 추출 인프라(schema + 적재 경로 + ADR) 선 구축, 활성화는 데이터 누적 후
- **UX 완결**: 선택/반려 UI → 30~60초 생성 후 사용자 의사결정 + 피드백 캡처

## 비목표 (별도 문서: non_goals.md)

P-AUX-2 자동 추출 agent 실 구현 / 4계층 full linkage(plan_options/video_projects) / Critic 0–5 fallback 완전 제거 / eval-run / async / PlanCard·component_map 수정 — 모두 Phase 9.5+/10+/11+ 이관.
