# Phase 7 — Goals

> Phase: phase-7-rag-lite
> 유형: large phase (RAG Lite — candidate_knowledge 5단계 MVP 전부)
> 진입일: 2026-05-29
> 예상 시간: 12~16h (5 Slice 모두 sub-agent dispatch)
> 기반 ADR: ADR-024 (Phase 5.5 RAG scope evolution)

## 한 줄 정의

ADR-024 기반으로 **candidate_knowledge 5단계 파이프라인 전부**(pending → filtered → evaluated → approved → promoted)와 **pgvector 기반 retrieval**(top-k=5, threshold=0.7)을 MVP에 구현하여, 영상기획 AI의 동적 지식 baseline을 확립한다.

## 핵심 목표 (G1~G8)

| ID | 목표 | 검증 매핑 |
|---|---|---|
| **G1** | candidate_knowledge 5단계 stage enum 정의 + DB schema migration (ADR-025) | A1 |
| **G2** | quality_filter 구현 (PII + 인젝션 + 광고적 표현 차단 단어) | A2 |
| **G3** | 간이 eval rubric (Phase 9+ eval 정식화 전까지) | A3 |
| **G4** | promotion 5단계 transition logic + promotion_history JSONB | A4 |
| **G5** | pgvector retrieval (cosine + top-k=5 + threshold=0.7) | A5 |
| **G6** | chunking 512 tokens 표준 + OpenAI embedding 통합 | A6 |
| **G7** | LLM Wiki vs RAG 분리 명확 (static vs dynamic) + agents/rag.py 통합 | A7 |
| **G8** | 회귀 0 — Phase 5.5 baseline (pytest 172/172, smoke 12/12, scenario_sim v2 10/10) 유지 | A8~A10 |

## 메타 목표 (M1~M4)

| ID | 목표 | 결과물 |
|---|---|---|
| **M1** | multi-llm-validation **formal self** 네 번째 트리거 + external placeholder | `meta/validations/2026-05-29_phase-7-pre-entry_self.md` + external |
| **M2** | **rag-design Skill ★ 첫 정식 트리거** (RAG architecture 결정) | Slice 1 + ADR-025 |
| **M3** | **rag-update Skill ★ 첫 정식 트리거** (5단계 승격 절차 강제) | Slice 4 |
| **M4** | P-X1 §SELF-VERIFICATION **31연속 PASS** (Phase 5.5:4 + Phase 7:5) | sub-agent 5 dispatch |

## 사용자 가치 (Why)

- **영상기획 품질 ↑**: 동적 지식(사용자 입력 + 외부 시드) → 영상기획안 근거 강화
- **장기 운영 baseline**: 5단계 파이프라인 → 사용자 데이터 누적 시 자동 promotion 가능 (Phase 11+ 확장)
- **확정 결정 [18] 실현**: RAG candidate_knowledge 5단계 승격 파이프라인 MVP 구현
- **사용자 결정 4 실현**: 5단계 전부 MVP 구현 (Lite 유지 + 확대는 별도 phase)

## 비목표 (별도 문서: non_goals.md)

Brand Memory 자동 추출 / Custom RAG / Graph RAG / Multi-modal RAG / Re-ranking / Hybrid retrieval / 사용자 데이터 자동 promotion / PlanCard 수정 — 모두 Phase 8+/9+/11+/21+ 이관 (ADR-024 §확대 지점 A~F).
