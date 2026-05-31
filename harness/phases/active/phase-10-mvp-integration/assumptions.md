# Phase 10 — Assumptions

## A. 제품 phase 성격
- ★ meta-phase(M0~M3)와 달리 **런타임 변경 有** — A9(런타임 0) 미적용. 대신 **behavior-preserving**(기존 불변 + 신규 추가) + pytest baseline 성장 + eval 회귀가 게이트.
- MVP 조각(Phase 1~9.5)이 이미 개별 동작/test 통과 → Phase 10 은 **연결/통합 검증** + 준비된 것(P-AUX-2) 활성 + eval 성숙.

## B. 통합 테스트 가정
- 통합 테스트는 **mock-deterministic** (실 LLM 0, 비용 0) — 기존 pytest 패턴 계승. 실 외부 의존(Supabase/LLM)은 mock/graceful.
- end-to-end 는 흐름 연결성 검증 (각 단계 산출이 다음 입력으로 정상 전달). 실 품질 측정 아님.

## C. P-AUX-2 가정 (S2)
- Phase 9 가 brand_memory_repo + feedback→candidate 적재 경로를 이미 준비(ADR-031) → Phase 10 은 **추출 agent 만 추가**. 기존 MOA 흐름에 additive(orchestrator 경유), 기존 응답 불변.
- graceful(추출 실패 시 차단 0) + PII 마스킹(Phase 9 security-review 계승) 필수.

## D. eval mode 가정 (S3, 사용자 결정)
- 실 LLM eval mode = **capability 정식화** (ADR-033 mode flag 실 경로 wire + 문서). default 실행은 mock-deterministic — Phase 10 CI 에서 실 LLM 미호출.
- 실 LLM run = opt-in (키 제공 시). ★ 키/자격증명 파일 커밋 0 (.env user-provided).
- golden_set 11→확대 + RAG eval_rubric 은 contract-change 경유.

## E. frontend 가정
- 통합은 **page/wrapper 레벨** — PlanCard.tsx(35연속 0줄) / component_map.md(45연속 0줄) 무수정. 신규 컴포넌트 0.

## F. Slice 분리
- S1(통합/회귀) → S2(P-AUX-2 agent) → S3(eval) → S4(배포 게이트+close). sub-agent sequential (git index race 회피). S2·S3 는 다른 모듈(agents vs eval)이나 순차.
- multi-llm-validation formal 10th = entry (큰 제품 phase).

## G. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| 통합 시 조각 간 미연결 발견 (실 버그) | ★ 그것이 통합 테스트의 가치 — bug-triage 로 분류, 필요 시 수정 slice (behavior-preserving) |
| P-AUX-2 가 기존 MOA 흐름 회귀 | additive(orchestrator 경유) + 기존 test 339 green 게이트 + agent-io-check |
| 실 LLM mode 무심코 default-on | NG2 + default mock 확인 게이트 + 키 커밋 금지 |
| golden_set 확대가 기존 11 회귀 깨뜨림 | 확대는 추가만 + eval gate 신구 비교 |
| PlanCard/component_map 수정 유혹 | NG9 + page 레벨 통합 한정 |
| 범위 C 가 커서 scope creep | NG3~NG7(Phase 11+ 명시) + Slice 게이트 |
