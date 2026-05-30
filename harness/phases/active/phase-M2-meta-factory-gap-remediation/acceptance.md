# Phase M2 — Acceptance (A1~A8 + MG1~MG3)

## A1~A8

| ID | 항목 | 검증 방법 | Slice |
|---|---|---|---|
| **A1** | S1 cluster 4 GAP 반영 (G1 architecture_patterns 결정기준 / G2 generation_workflow 결정트리 / G5 domain_brief risk 격상 / G6 data_model 필드) | 각 파일 string match (신규 섹션/필드) | S1 |
| **A2** | S2 cluster 4 GAP 반영 (G3 agent+contract conditional / G4 eval applies_when / G7 project_state harness_status / G8 blueprint validation pending-by-design) | 각 파일 string match (신규 슬롯/enum) | S2 |
| **A3** | M1 TEST 팟캐스트 재검증 — 8 GAP before/after + 개선 machinery 로 6검증 재실행, 이전 GAP-flag(검증3 조건부축 / 검증5 pending 표현 등) **해소** 확인 | revalidation.md 8 GAP 표 + 6검증 재판정 | S3 |
| **A4** | **CC-007** — 8 machinery 변경 로그 + cross-ref 정합 + M1 §D proposal 추적 | docs/contract_changes/ 파일 | doc-sync |
| **A5** ★ | **backward-compat** — 기존 M1 blueprint/scaffold 가 개선 machinery 하에서도 유효 (additive-only, 파괴적 변경 0) | git diff 에 기존 필드/절차 삭제·재명명 0 + validation_workflow 참조 깨짐 0 | 전 Slice |
| **A6** | 8 GAP 전부 반영 (백로그 0 — 사용자 결정 "전체 8개") | improvement backlog 8 → 0 매핑 표 | S3/doc-sync |
| **A7** | ADR-037 + 회고 — 변경 요약 + 재검증 결과 + 다음 단계 | ADR-037 + retrospective | doc-sync |
| **A8** | 결과 요약 — 변경 파일 + GAP 해소 + 다음 phase | closing_notes + 보고 | doc-sync |

## MG1~MG3 (메타 게이트)

| ID | 항목 | 검증 |
|---|---|---|
| **MG1** ★ | FastAPI/Next.js/Supabase **0줄** (A9) | `git diff backend/ apps/web/ migrations/` = 0 (전 Slice) |
| **MG2** | multi-llm-validation formal self **아홉 번째** (8 GAP 반영 타당성 + backward-compat) + external placeholder | meta/validations/ 파일 V1~V5 PASS |
| **MG3** | P-X1 §SELF-VERIFICATION **55연속** | S1·S2·S3 각 sub-agent git status/diff + forbidden 검사 |

## ★ backward-compat 게이트 (A5 상세 — additive-only)

```
변경 = 추가만 (새 섹션 / 필드 / 슬롯 / enum 값 / 결정트리)
금지 = 기존 필드 삭제 / 재명명 / 기존 절차 단계 제거
검증 = git diff --stat 에서 삭제(-) 라인이 "추가에 수반된 재구성"인지 확인 + validation_workflow.md 가 개선 schema 를 여전히 참조 가능
효과 = M1 podcast blueprint(구 machinery 산출)가 개선 machinery 하에서도 그대로 valid → 재검증(A3)에서 입증
```

## 재검증(A3) 의 GAP 해소 판정 기준

| GAP | M1 에서의 상태 | M2 재검증 기대 |
|---|---|---|
| G1 | architecture_patterns 결정 기준 암묵 | 명문 결정 기준 → expert_pool 미채택 근거가 명시적 |
| G2 | skill 신규 vs 재사용 결정트리 부재 | 결정트리 적용 → podcast-eval-run 충돌 시 재사용 강제가 절차로 |
| G3 | contract 조건부 산출 축 / agent conditional 부재 | conditional_execution 슬롯 + cross-ref 행 → guest_brief/question/shownotes 조건부 표현 가능 |
| G4 | eval 조건부 차원 우회(notes) | applies_when → question_quality/guest_fit 조건부 차원 정식 표현 |
| G5 | 제3자 PII risk 미반영 (medium 모호) | risk 격상 트리거 → 게스트 PII 로 risk 상향 판정 가능 |
| G6 | data_model schema 밖 별도 섹션 | data_model 필드 → 계층 1급 필드로 수용 |
| G7 | dry-run 상태 표현 부재 ("(제안)" 수동) | harness_status enum → dry-run-blueprint 명시 |
| G8 | validation pending 단일값 (정상 pending 구분 불가) | pending-by-design → 검증5 "절차 적용 가능/실측 미수행"이 정상으로 표현 |

→ 8 GAP 전부 "해소(addressed)" 또는 "표현 가능(expressible)"로 재판정되면 A3 PASS.

## 회귀 baseline (M1 → M2)

| 지표 | Phase M1 | M2 목표 |
|---|---|---|
| FastAPI/Next/Supabase 변경 | 0줄 | **0줄 (A9/MG1)** |
| pytest | 339 (무관) | **339 유지** (machinery 문서 — import 무관) |
| machinery 파괴적 변경 | — | **0 (additive-only, A5)** |
| GAP 백로그 | 8 | **0** (전부 반영) |
| P-X1 streak | 52 | **55** (S1·S2·S3) |
| Skill 수 | 21 | **21 유지** (Skill 본문 변경 0) |
| PlanCard / component_map 0줄 | 35 / 45 | **유지** (frontend 0) |
| harness-factory 트리거 | 2 (M1 첫 실) | **3** (S3 재검증 — 두 번째 실 트리거) |
| contract-change | CC-006 (7회) | **CC-007 (8회)** |

## qa-check (M2 final 예상)
- 1 제품/범위 PASS (machinery 개선 — 범위 정확) / 2 AI 구조 skip / 3 RAG skip / 4 프론트 skip(0) / 5 평가 부분(재검증5 절차 적용성 PENDING) / 6 **메타 PASS** (★ self-improvement loop 완주) / 8 큰 결정 PASS (CC-007 + multi-llm) / 9 Phase 운영 PASS / 나머지 skip.
- **예상**: 4 PASS / 1 부분 / 6 skip.
