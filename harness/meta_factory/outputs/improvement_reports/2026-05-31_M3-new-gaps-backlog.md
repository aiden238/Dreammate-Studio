# Meta-Factory 개선 백로그 — Phase M3 발견 (새 GAP 3, blocking 0)

> 출처: Phase M3 이질 도메인 dry-run (재무) — `outputs/TEST/sample_test_finance_validation.md §D`
> 날짜: 2026-05-31
> 상태: **백로그** (전부 minor/nice-to-have — blocking 0, Phase 10 진입 막지 않음). 반영은 Phase 10 후 또는 차기 meta-phase, contract-change(M2 식) 경유.
> ★ 이 파일은 실 산출 백로그(generated_harnesses/improvement_reports). M3 dry-run 산출(outputs/TEST/finance)과 별개.

---

## 배경
M3 가 M2 개선본(G1~G8)을 이질 도메인(재무)에 적용한 결과 **범용 강함**(미디어 편향 0) + M2 개선 유효 7/부분 1. 단 이질 도메인이 새 GAP 3개를 표면화. 전부 blocking 아님(기존 게이트로 실질 차단됨) → 백로그.

## 새 GAP (3)

| GAP | 내용 | 심각도 | 대상 파일 | 보완 방향 (반영 X — 기록만) |
|---|---|---|---|---|
| **NEW-G9** | `forbidden_scope` 가 **regulatory_forbidden**(법적·영구 금지: 투자권유/원금보장) vs **deferred_scope**(MVP 후순위)를 한 필드에 혼재 | **minor** | `domain_brief_schema.md` | forbidden_scope 를 2 하위 필드로 분리 (regulatory_forbidden / deferred_scope). 실질 차단은 advisory_boundary 하드 게이트가 이미 수행 — 표현 정밀도만 |
| **NEW-G10** | `risk_level` 단일 enum 이 **data_risk**(PII) vs **regulatory_risk**(자문·규제)를 미분해 | **nice-to-have** | `domain_brief_schema.md` | risk 축 분해(data_risk/regulatory_risk). 단 G9 와 부분 중복(규제위험은 forbidden_scope 축으로 이미 표현). G9 와 함께 검토 |
| **NEW-G11** | `conditional_execution` template 예시가 **enum mode(mode==guest)에 치우침** — 불리언 데이터조건(has_debt/has_dependents) 문서화 부재 | **nice-to-have** | `templates/agent_template.md` | conditional_execution 예시에 불리언 데이터조건 1개 추가 (표현은 이미 작동 — 문서 명료화만). machinery 결함 아님 |

## 판정
- **blocking 0** — 3개 모두 기존 게이트(advisory_boundary 하드 게이트 / forbidden_scope 축 / conditional_execution 작동)로 실질 커버됨. 표현 정밀도·문서화 개선 수준.
- **Phase 10 진입 영향 0** — 사용자 분기 조건("수정 요소 없으면 Phase 10") 충족. 본 백로그는 Phase 10 을 막지 않음.

## 후속 (제안)
- Phase 10 (MVP 통합) 완료 후 또는 차기 meta-phase 에서 G9+G10(domain_brief_schema risk/forbidden 정밀화) + G11(template 문서화)을 묶어 additive 반영 검토 (M2 식 contract-change).
- 우선순위 낮음 — 차기 도메인 하네스 생성이 실제 필요해질 때 반영해도 충분.
