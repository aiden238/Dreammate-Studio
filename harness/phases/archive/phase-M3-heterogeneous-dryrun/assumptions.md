# Phase M3 — Assumptions

## A. 도메인 선택
- 개인 재무 플래닝은 미디어(영상/팟캐스트)와 **이질**(수치·규제·적합성)이나 **planning-shaped**(목표 → 플랜 3안 + 검토)라 M1 팟캐스트와 공정 비교 가능. 완전 비-planning 도메인(분류/추출)은 generation_workflow 적용 자체가 모호해 generality 신호가 흐려짐 → planning-shaped 이질 도메인이 2nd 검증에 최적.

## B. dry-run 성격 (M1 계승)
- 문서 설계 dry-run. 실 LLM 미호출(NG6). 검증5 = 절차 적용성(pending-by-design). 첫 1회라 fail/pending 정상.
- ★ machinery 개선본은 **읽기만** — M3 는 사용/검증, 변경 0 (NG2). 새 GAP 은 백로그.

## C. with/without (M1 계승, 완화)
- without baseline 먼저 작성(오염 최소화). 단 M3 핵심은 with/without 수치보다 **M2 G1~G8 실사용 + 범용성 판정**. with/without 은 보조(누락률 차원).

## D. M2 개선 행사 가정
- G5(제3자 PII)는 재무에서 강하게 행사(부양가족/수익자). G6(data_model)은 Household 계층으로 행사. G3(conditional)은 부양가족/부채 조건. G4(applies_when)는 세금 모드. → M2 개선이 미디어 외 도메인에서도 사용되면 범용성 입증.
- 단, 일부 개선(예: 미디어 특화가 아닌 범용 개선이라 모든 도메인 적용)은 "사용됨이 당연" — 진짜 신호는 **부적합/미사용/새 GAP**.

## E. 금융 안전 (도메인 forbidden)
- 재무 도메인 자체가 투자권유·원금보장·특정상품추천·세무/법률자문 금지 → forbidden_scope 로 명시. 하네스 **설계**만, 실제 금융 행위·알고리즘 0 (NG7). 안전 민감 분야라 forbidden_scope 매핑(G5/non_goals)이 강하게 테스트됨.

## F. 분기 가정 (사용자 지침)
- S2 종합이 "새 GAP/반영/수정 없음" → Phase 10 직행 기획. "있음" → 백로그 + 후속 결정. ★ 판정은 보수적으로 — 미디어 편향이나 명백한 부적합이 있으면 "있음"으로.

## G. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| 이질 도메인이라 모든 게 GAP (노이즈) | planning-shaped 선택으로 generation_workflow 적용성 확보 + "개선 행사 vs 새 GAP" 구분 |
| sub-agent outputs/TEST/ 외 변경 | forbidden 명시 + git diff 게이트 + revert (P-X1) |
| machinery 무심코 수정 | NG2 — machinery 읽기만 forbidden 명시 |
| 분기 판정 편향(빨리 Phase 10 가려고 GAP 무시) | 보수적 판정 + 새 GAP 0 이면 근거 명시 의무 |
