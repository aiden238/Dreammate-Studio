# Phase M2 — Assumptions

## A. proposal-first 정합
- 8 GAP 의 proposal 은 이미 M1 `sample_test_podcast_validation.md §D` 에 존재(각 1줄 보완안). M2 는 새 발굴이 아니라 **그 proposal 의 검토 → 승인 → 반영** → self_improvement_loop §0 "자동 수정 아님, 항상 제안→검토→승인→반영" 정합.
- machinery = L3 contract → 반영은 contract-change(CC-007) 절차. Skill 본문이 아니라 machinery **문서**이므로 키워드 충돌 검토는 불필요(Skill description 무변경).

## B. additive-only (★ 핵심 가정)
- 8 GAP 은 전부 **추가형** 개선(새 결정트리/필드/슬롯/enum 값). 기존 필드·절차 삭제·재명명 0 → 기존 M1 blueprint(구 machinery 산출)가 개선 machinery 하에서도 valid (backward-compat).
- 따라서 재검증(S3)에서 M1 podcast 산출물을 "다시 생성"할 필요 없이 **개선 슬롯을 적용(추가)** 하는 것으로 before/after 입증 가능.

## C. 재검증의 성격
- S3 재검증은 실 LLM 호출 없는 **문서 재적용**(M1 dry-run 정신 계승, NG11). 검증5(eval-run)는 절차 적용성까지(여전히 PENDING — 실측은 별도).
- 재검증 목적 = "8 GAP 이 개선 machinery 로 해소/표현 가능해졌는가" before/after 확인. 새 GAP 발굴 아님(NG8).

## D. 격리/안전
- 변경은 machinery docs + meta + state + outputs/TEST/ 만. runtime(L1) 0줄(A9). product contract / Skill 본문 / 라우터 0줄.
- pytest 339 무관(machinery 문서는 import 안 됨) → 회귀 위험 0.

## E. Slice 분리 근거
- S1(생성 입력/절차) ↔ S2(scaffold/schema) 는 **파일 비중첩** → 충돌 0. 단 git index race 회피 위해 **sequential** dispatch (S1 → S2, 기존 패턴).
- S3(재검증) 는 S1+S2 완료 후 (개선 machinery 전부 반영된 상태에서 재적용).

## F. 시간/규모
- S1 ~1h / S2 ~1~1.5h / S3 ~1h / doc-sync ~0.5h = 3~5h. Skill 수 21 유지(본문 무변경).

## G. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| machinery 변경이 기존 절차/cross-ref 깨뜨림 | additive-only(NG9) + S3 재검증에서 validation_workflow 참조 가능성 확인 + A5 게이트 |
| sub-agent 가 forbidden 영역(product contract/Skill/runtime) 변경 | forbidden 명시 + 사후 git diff 게이트 + P-X1 revert |
| 8 GAP 과 무관한 "정리" 욕심 | NG9(additive)/NG5(GAP 없는 파일)/NG2(product contract) 명시 |
| 재검증이 새 GAP 발굴로 번짐 | NG8 — M1 8 GAP 해소 확인까지만, 새 GAP 은 백로그로 기록만 |
