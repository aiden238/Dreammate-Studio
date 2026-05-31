# Phase M3 — Acceptance (A1~A7 + MG1~MG3)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | 재무 domain_brief — domain_brief_schema 개선본 충족 (data_model G6 + 제3자 PII risk G5 + forbidden_scope 투자권유/원금보장 금지) | 파일 + 필드 | S1 |
| **A2** | harness_blueprint + 6 scaffold (개선 슬롯 활용 — conditional_execution G3 / applies_when G4 / pending-by-design G8 / harness_status G7) | 파일 7 + 슬롯 | S1 |
| **A3** ★ | **M2 G1~G8 실사용 점검표** — 각 사용됨/유효/부적합 + 이질 도메인 적합도 | 8행 점검표 | S2 |
| **A4** | 6검증 (PASS/FAIL/PENDING/PENDING-BY-DESIGN/GAP) | 6 섹션 | S2 |
| **A5** | 범용성 판정 — 미디어 편향(창의 hook/3-variant 강요) 유무 + 재무 적합도 | 판정 + 근거 | S2 |
| **A6** | 새 GAP 검출 (범용성 한계) — 있으면 목록, 없으면 "0" 명시 | GAP 섹션 | S2 |
| **A7** ★ | 종합 분기 권고 — "추가 검증/반영/수정 필요" 또는 "없음 → Phase 10 직행" | 종합 | S2/assess |

## MG1~MG3
| ID | 항목 | 검증 |
|---|---|---|
| **MG1** | dry-run 변경 outputs/TEST/ 외 0줄 (machinery 0) | git diff --stat |
| **MG2** | FastAPI/Next/Supabase 0줄 (A9) | git diff backend/apps/migrations |
| **MG3** | P-X1 57연속 | S1·S2 sub-agent 검사 |

## ★ M2 개선 8요소 실사용 기대 (A3 — 이질 도메인에서 행사)
| GAP 개선 | 재무 도메인 행사 기대 |
|---|---|
| G1 expert_pool 결정기준 | 목표유형별(저축/투자/은퇴/부채) expert vs 단일 planning 파라미터화 — 결정기준 적용 |
| G2 skill 재사용 결정트리 | 재무 도메인 신규 Skill 후보의 기존 21 Skill 충돌 검사 → 재사용 강제 |
| G3 conditional_execution | 부양가족 있을 때만 보험검토 / 부채 있을 때만 상환우선순위 agent |
| G4 applies_when | 세금최적화 모드에서만 tax_efficiency 차원 채점 |
| G5 제3자 PII risk | 부양가족/수익자(beneficiary) PII → risk 상향 (재무 PII 민감) |
| G6 data_model | User→Household→FinancialGoal→Plan→Allocation 계층 1급 필드 |
| G7 harness_status | dry-run-blueprint 상태 표기 |
| G8 pending-by-design | 검증5 eval-run 실측 미수행 정상 표현 |

→ 8 중 다수가 "사용됨+유효"면 범용성 강함. "부적합/미사용"이 있으면 새 GAP 후보.

## 범용성 판정 기준 (A5)
- **편향 신호**: machinery 가 "창의적 hook 강도" / "3안 다양성(창의)" / "썸네일" 류 미디어 전용 요소를 재무에 **강요**하는가? → 강요 시 미디어 편향 GAP.
- **적합 신호**: 재무 고유(리스크/적합성/규제 forbidden/수치 정확성)를 machinery 가 수용하는가? (G5 risk + forbidden_scope + eval 차원 교체로 수용 가능 기대)
- 판정: 범용 강함 / 부분(편향 일부) / 약함(미디어 종속).

## 회귀 baseline (M2 → M3)
| 지표 | M2 | M3 목표 |
|---|---|---|
| 런타임 변경 | 0 | 0 (A9/MG2) |
| dry-run outputs/TEST/ 외 | — | 0 (MG1) |
| machinery 변경 | (M2 8 additive) | **0** (M3 읽기만) |
| P-X1 | 55 | **57** |
| pytest | 339 | 339 (무관) |
| Skill 수 | 21 | 21 유지 |
| harness-factory 트리거 | 3 | **4** (S2 세 번째 실) |

## qa-check (M3 final 예상)
- 1 범위 PASS / 6 메타 PASS (범용성 검증) / 나머지 skip. dry-run meta-phase.
