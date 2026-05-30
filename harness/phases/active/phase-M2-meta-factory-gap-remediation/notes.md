# Phase M2 — Notes

## 진입 맥락
- M1 dry-run 이 meta_factory machinery 의 8 GAP 을 발견(`outputs/TEST/sample_test_podcast_validation.md §D`). 사용자 선택: **① GAP 보완 meta-phase(M2)**.
- 사용자 결정 2건: **GAP 범위 = 전체 8개(G1~G8)** + **검증 = M1 TEST 재적용(re-validate)**.

## M1 ↔ M2 의 결정적 차이
```
M1 : dry-run — machinery 0 변경 (읽기만), 산출물 outputs/TEST/ 격리, GAP 발견
M2 : machinery 실제 변경 (CC-007, L3 contract) — 8 GAP 반영 + M1 TEST 재적용으로 해소 입증
```
→ M2 sub-agent 의 editable 은 machinery 문서(S1·S2) + outputs/TEST/(S3). M1 의 "machinery 읽기만" 제약과 반대.

## 핵심 원칙 3
1. **additive-only** (NG9/A5) — 추가만, 기존 필드·절차 삭제·재명명 0 → M1 blueprint backward-compat. 재검증(S3)에서 입증.
2. **contract-change (CC-007)** — machinery = L3 contract. proposal(M1 §D) → 검토 → 승인 → 반영 → 로그.
3. **재검증으로 입증** — "반영했다"가 아니라 M1 TEST before/after 로 8 GAP 해소 확인 (사용자 결정).

## 8 GAP → 파일 → fix 요지
| GAP | 파일 | fix |
|---|---|---|
| G1 | architecture_patterns.md | expert_pool vs 단일 agent 결정 기준 (특화도/포맷수/독립진화) |
| G2 ★ | generation_workflow.md 단계4 | 신규 Skill vs 재사용 결정트리 (키워드 충돌 검사 → 충돌 시 재사용 강제) |
| G3 ★ | agent_template + contract_template | conditional_execution 슬롯 + 조건부 산출 cross-ref 행 |
| G4 | eval_template.md | applies_when (조건부 차원, 미해당 시 평균 제외) |
| G5 ★ | domain_brief_schema.md | 제3자 PII → risk 격상 트리거 |
| G6 | domain_brief_schema.md | data_model 선택 필드 |
| G7 | project_state_template.md | harness_status enum (active/dry-run-blueprint/proposal) |
| G8 | harness_blueprint_schema.md | validation pending-by-design enum |

## ★ 안전 게이트 요약
```
A9   : FastAPI/Next.js/Supabase 0줄 (machinery/meta/state/outputs/TEST 만)
A5   : additive-only — 파괴적 변경 0, M1 blueprint backward-compat (재검증 입증)
MG3  : P-X1 55연속 (S1·S2·S3)
CC-007: machinery 변경 contract-change 로그
```

## 결정 대기 / 옵션
- 본 entry 는 실행 전 계획. 사용자 별도 지시 없으면 entry commit → S1 → S2 → S3 → doc-sync 순차 진행 (이미 "① 진행" 선택).
- self-improvement loop 완주 (M0 도입 → M1 검증/GAP 발견 → M2 반영/재검증) — P-META-FACTORY-002 update.

## 다음 단계 (M2 이후)
- machinery 개선 완료 → 차기 도메인 dry-run(이질 도메인) 시 개선 슬롯 활용 / 2nd 하네스 생성 품질 ↑.
- 검증5 실 eval-run 표본(M1·M2 공통 미해소 — PENDING)은 별도 (eval-run §3~§6 mock-deterministic).
- Phase 10 (MVP 통합) — meta-phase detour 종료, 제품 로드맵 복귀 (next_phase_status pending_user_decision 불변).
