# Phase 31 — acceptance

| # | 기준 | 측정 | 통과선 |
|---|---|---|---|
| A1 | consensus-min 배선(additive gated) | 코드 + 테스트 | OpenAI+Claude 중 엄격 verdict 채택, OFF byte-identical |
| A2 | consensus-min 안전동작 | 테스트 | ANTHROPIC_API_KEY 부재 시 graceful/안전차단, 단조성(절대 약화 0) |
| A3 | OFF 회귀 0 | pytest | 기존 스위트 green(현 835 기준) byte-identical |
| A4 | P-006 prompt-version-review | 절차 | semver bump + golden_set 회귀 + verdict 비퇴행 + 할루시네이션 단정 0 |
| A5 | P-006 개선 실측 | cross-provider judge | B0 대비 Δ>0 ∧ 회귀 케이스 ≤ 허용 ∧ 과확장 가드 작동 |
| A6 | golden_set RAG ON/OFF 측정 | judge 채점 | ON vs OFF Δ 산출 + 개선/중립/하락 판정 기록 |
| A7 | main 통합 | git | research 5 + project-2 결착 + 본 phase가 main 반영, 두-워크트리 재분기 0 |
| A8 | 게이트 | pytest + audit_naming + (해당 시) frontend | 전부 green/0 drift |

## 통과 조건
- A1~A3(consensus-min) + A8 = **무비용 코드 마감**(우선 완결).
- A4~A6 = **코스티드 측정**(실 LLM, 사용자 opt-in). 비용 발생 단계는 진행 전 확인.
- A7 = **릴리스**(outward push, 사용자 승인). 코드/측정 완료 후 마지막.

## 정직 표기 (계승)
- judge는 사람정렬 검증된 단일 계측기(rater A N=1) — 다중 human 재평가가 최종 확증(rater B 미도착=blocked, 본 phase 비포함).
- RAG 측정은 8건 합성 코퍼스 기준 — "검색 작동"은 입증됨(6ba1aaf), "품질 기여"가 A6 측정 대상. 코퍼스 빈약은 별도 아크.
