# Phase M3 — Notes

## 진입 맥락
- 사용자: "이질 도메인 dry-run — 개선 machinery 범용성 2차 검증후 추가 검증이나 반영요소, 수정 요소가 없으면 바로 Phase 10 기획".
- M1(인접 팟캐스트, M0 원본) → M2(8 GAP 반영) → **M3(이질 재무, M2 개선본)**. Meta-Factory 도메인 범용성 2차 검증.

## 도메인: 개인 재무 플래닝 AI (이질)
- 정의: 재무 목표 → 예산·저축·투자배분 플랜 3안 + 리스크/적합성 검토.
- ★ 아님(forbidden): 투자 자문/권유, 원금 보장, 특정 상품 추천, 세무·법률 자문. (정보·기획 도구)
- 이질성: 미디어 → 금융(수치/규제/적합성). 창의 hook 부재, forbidden_scope 강함.

## M2 개선 8요소 행사 (이질 도메인에서)
| G | 재무 행사 |
|---|---|
| G1 expert_pool 기준 | 목표유형별 expert vs 단일 planning |
| G2 skill 결정트리 | 재무 신규 Skill 충돌 검사 → 재사용 |
| G3 conditional | 부양가족/부채 조건부 agent |
| G4 applies_when | 세금모드 tax_efficiency 차원 |
| G5 제3자 PII | 부양가족/수익자 risk 상향 |
| G6 data_model | User→Household→Goal→Plan→Allocation |
| G7 harness_status | dry-run-blueprint |
| G8 pending-by-design | 검증5 실측 미수행 정상 |

## ★ 안전 게이트
```
A9   : 런타임 0
MG1  : dry-run outputs/TEST/ 외 0줄 (machinery 개선본 읽기만 — 변경 0)
MG3  : P-X1 57연속
분기 : S2 종합 → 새 GAP 없음 → Phase 10 / 있음 → 백로그+후속 (보수적 판정)
```

## 산출물 맵
```
meta_factory/outputs/TEST/finance/
  _without_baseline.md / domain_brief.md / harness_blueprint.md / scaffolds/{6}_draft.md
meta_factory/outputs/TEST/sample_test_finance_validation.md  (6검증 + M2 G1~G8 점검 + 범용성 + 새 GAP + 분기)
```
> podcast 산출물(M1·M2)과 finance 산출물 분리. 실 산출 영역(generated_harnesses/improvement_reports)과도 분리.

## 분기 후
- **없음**: Phase 10 (MVP 통합) entry 기획 — meta-phase detour(M0~M3) 종료, 제품 로드맵 복귀.
- **있음**: 새 GAP 백로그 → M2 식 반영(별도) 또는 Phase 10 후 처리, 사용자 보고.

## 다음
- M3 = Meta-Factory 범용성 2차 검증(이질). 통과 시 도메인 범용성 입증 완료 → 제품(Phase 10) 복귀.
