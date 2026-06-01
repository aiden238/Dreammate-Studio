# Phase 12 — Assumptions

## A. 검증/계획 phase 성격
- ★ 런타임 변경 0 — Phase 12 는 **측정·분석·계획**만. 운영 endpoint/agent/prompt/schema 0 수정. behavior-preserving(pytest 471) + 키 0 이 게이트.
- 산출물 = eval 데이터(실 LLM 점수) + 깊이 격차 분석 + human review kit + 확장 우선순위 제안(문서). 코드 산출 0.

## B. 실 LLM 호출 비용 — 사용자 승인됨 (핵심)
- ★ S2 실 LLM eval(golden_set ~25 × 1회) + S3 깊이 격차 측정(compact vs rich)은 **실 LLM 호출 = 실비용**. 사용자가 승인함(`PROJECT_STATE.md` §"S2: 실 LLM eval ON, 실 LLM 호출=실비용").
- 비용 추정 기준 = `ai_system/orchestration/cost_control_policy.md` (B-RES-1 다중-provider cost 재조정 잔여 참조). 실 호출 = 측정 1회, CI 미실행.
- mock-deterministic eval = CI 회귀 게이트로 **유지** — real 은 측정 전용(NG9).

## C. golden_set 도메인 가정
- golden_set 도메인 = **영상기획**(GS-001~GS-015: Discovery/Quick·intent 차단·revise·RAG·길이 분기·Brand Memory·인젝션·도메인 다양). 확장(~25)도 동일 도메인 — depth/actionability 측정에 적합한 케이스 보강.
- 확장 = **additive**(기존 15 회귀 보존) + contract-change(S1) 경유. 기존 케이스 의미 변경 0.

## D. LLM-as-judge + human review 대조 가정
- 자동 채점 = LLM-as-judge(eval runner). ★ 단일 판정으로 신뢰하지 않고 **human review 표본으로 신뢰도 대조**(MO3) — solo 운영의 단일 채점 편향 완화(multi-llm-validation 정신).
- human review = **kit 준비까지가 Phase 12 산출**(표본 + 시트 + 대조 설계). 사용자 실 채점 시간은 deferred(NG7). 대조 분석은 채점 회수 후 후속.

## E. 깊이 격차 데모 재현 가정 (★ 중심 가설)
- 2026-06-02 라이브 데모(gpt-4o-mini compact vs rich)에서 관찰된 깊이 격차가 golden_set 표본에서도 **재현된다**고 가정 — S3 가 이를 수치로 확정(재현 안 되면 그 자체가 결과).
- compact = 현 운영 7필드 / rich = 확장 측정-프롬프트(hook 3변형·타임코드·대사·자막·B-roll·썸네일·CTA·레퍼런스·길이 변형). ★ 단순함 = 모델 한계 아니라 prompt/schema 설계 선택이라는 가설.
- rich = **측정 전용** — 운영 prompt/schema 0 반영(NG1) + 기획 브리프 경계 유지(완성 대본 아님, NG2).

## F. 비용·토큰 트레이드오프 가정
- rich 출력 = **출력 토큰 ↑** (필드·서술·변형 증가) × 3안 = 비용 배수. 깊이 격차 측정 시 토큰/비용도 metric 으로 기록 → Phase 13 확장 ROI 판단 입력.
- 깊이 ↑ 가 항상 가치 ↑ 는 아님(과잉 상세 risk) — actionability rubric 으로 "실행 가능한 깊이"를 측정(맹목 토큰 증가 ≠ 가치).

## G. B안 비차단 잔여 가정 (GPT ④)
- B-RES-1(cost_control 다중-provider 재조정) / B-RES-2(B안 ADR) / B-RES-3(agent_io/registry contract-change) 는 **비차단 추적 항목** — Phase 12 비용·범위 기준에 영향하나 acceptance blocking 아님. Phase 12 내 또는 직후 처리(dependencies §B안 참조).

## H. Slice 분리 가정
- Entry → S1(golden_set·rubric) → S2(실 LLM eval) → S3(깊이 격차) → S4(human kit) → S5(종합). S2·S3 는 S1 확장본·차원에 의존(sequential). S4 는 S2 점수에 대조(병행 가능). sub-agent dispatch, P-X1 게이트.

## I. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| 실 LLM eval 비용 폭증 | golden_set ~25 × 1회로 한정 + cost_control 기준(B-RES-1) + 사용자 승인 범위. CI 미실행(mock 유지) |
| 깊이 격차가 측정에서 약하게 나옴 | 그 자체가 결과(가설 반증) — Phase 13 우선순위에 반영. 데모는 단일 표본, S3 는 다수 표본으로 일반화 |
| rich 측정이 운영 prompt 로 누수 | ★ rich = 측정 전용 프롬프트(운영 prompt_registry/output_schema 0 반영). entry 단계 사전 변경 0(NG6) |
| rich 가 완성 대본화 | actionability = "기획 브리프" 깊이로 한정(product_boundary). 촬영·편집 산출 0(NG2) |
| LLM-as-judge 편향 | human review 표본 대조 설계(MO3) — 자동 점수 보정 |
| 운영 코드 무심코 수정 | ★ P-X1 게이트 — git diff 운영 .py 0 + pytest 471. 위반 시 revert |
| 키 노출 | .env user-provided + .gitignore + push 전 `git diff | grep sk-/AIza` |
| golden_set 확장이 기존 회귀 깸 | ★ additive(기존 15 보존) + contract-change(S1) + mock 게이트 재실행 |
