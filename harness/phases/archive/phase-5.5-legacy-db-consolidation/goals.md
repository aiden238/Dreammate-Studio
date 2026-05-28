# Phase 5.5 — Goals

> Phase: phase-5.5-legacy-db-consolidation
> 유형: consolidation mini-phase (Phase 5 후속, Phase 7 진입 전 정리)
> 진입일: 2026-05-29
> 예상 시간: 4~6h (4 Slice 모두 sub-agent dispatch)

## 한 줄 정의

Phase 5 종료 시점 발견된 **legacy DB 인프라**(Phase 1 `db/supabase_client.py` + `save_video_planning`)와 **Phase 5 신규 인프라**(`db/client.py` + `plans_repo`)의 통합을 결정하고, **3개 phase의 external validation placeholder**(Phase 4.5/6/5)를 self-validation 형식으로 강화 작성하며, **Phase 7 RAG scope 진화 지침**을 신규 작성하여 Phase 7 진입 baseline을 확립한다.

## 핵심 목표 (G1~G6)

| ID | 목표 | 검증 매핑 |
|---|---|---|
| **G1** | Legacy DB 통합 결정 명시 (ADR-023) — 두 layer 공존 / 통합 / 단계적 deprecation 중 선택 + 회귀 0 | A1, A2 |
| **G2** | Phase 4.5 + 6 + 5 external validation placeholder 3개 모두 self-strengthen 작성 (Claude Code 자가 검토 강화, V1~V4/5/6 항목별 검증 추가) | A3 |
| **G3** | `docs/decisions/phase_7_rag_scope_evolution.md` 신규 (ADR-024) — RAG Lite 정의 + candidate_knowledge 5단계 MVP 명시 + 확대 지점 (다른 phase 확장 경로) | A4 |
| **G4** | Brand Memory 자동 추출 **Phase 9+** 이관 confirmation (NG 명시) | A5 |
| **G5** | **PlanCard.tsx 18연속 0줄** + **component_map.md 28연속 0줄** baseline 유지 | A6 |
| **G6** | 회귀 0 — Phase 5 baseline (pytest 170/170, smoke 12/12, scenario_sim v2 10/10) 유지 | A7, A8 |

## 메타 목표 (M1~M2)

| ID | 목표 |
|---|---|
| **M1** | P-X1 §SELF-VERIFICATION **26연속 PASS** (Phase 3:5 + 4:4 + 4.5:4 + 6:4 + 5:5 + 5.5:4) |
| **M2** | Phase 7 RAG 진입 baseline 확립 (사용자 결정 4: candidate_knowledge 5단계 MVP 전부) |

## 사용자 가치 (Why)

- **장기 운영 안정성 ↑**: legacy DB 인프라 명확한 통합 결정 → Phase 7 RAG가 두 layer 공존 혼란 없이 단일 인터페이스 활용
- **검증 baseline 강화**: external validation 3개 self-strengthen → 추후 사용자 외부 GPT/Gemini 검토 시 비교 baseline 확립
- **Phase 7 안전 진입**: RAG Lite scope + 5단계 MVP 결정 + 확대 지침 → Phase 7 본 phase 진입 시 scope creep 차단
- **Brand Memory 지연 정당화**: Phase 9+ 이관 명시 → MVP 본격 운영 데이터 누적 후 자동 추출 결정

## 비목표 (별도 문서: non_goals.md)

Phase 7 RAG 본격 구현 / Brand Memory 자동 추출 / candidate_knowledge 5단계 코드 / PlanCard 수정 / prompt_registry 본문 / multi-provider — 모두 Phase 7+/9+/21+ 이관.
