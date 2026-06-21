# Phase 31 — critic 품질 계측기 production화 + 마감 · goals

## 목표
critic 품질 연구 아크(2026-06-21)가 발견·검증한 **사람정렬 자동 계측기(cross-provider
Claude judge)** 를 production 레버로 마감하고, project-2 잔여 결착을 main에 통합한다.
"88점 함정(critic 낙관편향, false-approve 10/10)"의 진짜 fix가 cross-provider judge임을
실측으로 확인했으니, 이제 ① 더 안전한 default 후보(consensus-min)를 배선하고 ② 생성
프롬프트(P-006)를 검증된 표면 레버로 개선하며 ③ RAG가 실제로 품질을 올리는지 측정한다.

## 배경 (왜 지금)
- 연구 아크 3대 발견(eval/regression_results/2026-06-15·2026-06-21): 88점 함정 정량
  확정 / cross-provider Claude judge가 verdict 차단(false-approve 10/10→0/10, 사람괴리
  2.27→0.53) / B0/B1 특이성 rewrite는 표면만 개선(Δ+0.33, 차별화는 RAG/PKM grounding 필요).
- project-2 잔여 결정(HIP-B/C·RAG Gemini)은 결착·구현 완료(5984c07/6ba1aaf), 단 research
  5커밋과 함께 **main 미머지** → 통합이 본 phase의 릴리스 단계.

## 통과 기준(요지)
- consensus-min이 gated/additive로 배선되고 OFF면 byte-identical(기존 pytest green 유지).
- P-006 개선안이 prompt-version-review 절차(semver + golden_set 회귀 + 비퇴행 게이트)를
  통과(할루시네이션 라벨 강제 + 과확장 금지 가드 포함).
- golden_set RAG ON/OFF 품질이 cross-provider judge로 측정되어 "RAG가 품질을 올리나"에
  처음으로 정량 답을 냄(개선/중립/하락 명시 — 하락 시 use_rag 보류 판단).
- research 5커밋 + project-2 결착이 main에 통합(머지/push)되고 두-워크트리 재분기 0.
- 상세 = acceptance.md.

## 명시적 결정 (사용자, 2026-06-21)
- 옵션 1 전체를 **페이즈로 기획해서 진행**(본 phase) — 4→2→1 순의 마지막.
- default judge 전환(openai→anthropic)은 본 phase 비포함 — major model swap = 별도
  prompt-version-review. 본 phase는 consensus-min(안전 default 후보)까지.
- 코퍼스 확대(큐레이션·2nd-brain)는 별도 아크(non_goal) — 본 phase는 측정까지.
