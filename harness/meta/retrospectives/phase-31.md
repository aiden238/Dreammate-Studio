# 회고 — Phase 31: critic 품질 계측기 production화 + 마감

> 2026-06-21~22 | 브랜치 `phase-29-agent-ux`(=main) | critic 품질 연구 아크의 production 마감 + project-2 결착 + cross-project 수렴 착수

## 1. 무엇을 했나

critic 품질 연구 아크(88점 함정 → cross-provider Claude judge=사람정렬 계측기)를 production 레버로 마감하고, project-2 잔여 결정을 main에 통합했다.

- **S1 consensus-min (`866fddd`)**: `critic_judge_provider='consensus_min'` — OpenAI+Claude 둘 다 채점 후 더 엄격한 verdict 채택(단조). gated default-off. 테스트 3, pytest 835→838.
- **S2 P-006 director v1.2.1 (`0f108f8`)**: 특이성 강화 + ★정직 가드(`추정/예시:` 라벨 강제·과확장 금지). prompt-version-review 절차(semver+registry+회귀). 라이브 비퇴행(Δ+0.1~0.2).
- **S3 RAG ON/OFF (`801bb00`)**: cross-provider judge로 RAG grounding 품질 기여 측정 — **리뷰 케이스 Δ+0.9**(use_rag ON 유지 근거). RAG Gemini 라이브 @0.7 검증(`6ba1aaf`).
- **S4 릴리스**: research 5 + project-2 결착 + 본 phase를 main 머지/push(`c82ed9b..bab47ec`, origin/main 동기). 팀↔개인 취합은 경로분리로 이미 완료(aa2d236).
- **project-2 결착 (`5984c07`)**: HIP-B 죽은게이트 4 + HIP-C 스킬 21→19 병합·bug-triage 게이트화 + RAG doc-side taskType.
- **cross-project 수렴 착수(Phase 33 S1, `b996eda`)**: plotter 결정적 게이트(`structure_pacing_issues`) 이식 — 비-LLM `critic_pacing_gate`로 director payoff bloat을 approve→revise 강등(cross-provider judge와 직교). pytest 845.

## 2. 잘된 점

- **연구 아크를 production 레버로 마감** — 측정(계측기)이 아니라 gated 운영 옵션(consensus-min·정직가드·pacing 게이트)으로 안착. 전부 OFF byte-identical.
- **사전동결 임계 + 사람 ground truth 방법론**(plotter식 차용)으로 88점 함정을 정량 확정 → cross-provider judge가 false-approve 10/10→0/10 닫음을 입증.
- **project-2 미커밋 유실 위기를 결착·통합**으로 마감 — proposal-first 기록 + main 동기.
- **cross-project 강점취합 설계를 파악·기획·일부 적용** — "결정적 게이트 + cross-provider judge" 직교 합산을 양 프로젝트에 절반씩 채움.

## 3. ★ 핵심 사건 — CODEX 교차검토가 잡은 live-schema 버그 (P 후보)

- 본 phase 검증 중 **CODEX 독립 검토**가 `brand_memory_entries`의 PK가 `entry_id`인데 코드는 `id`로 쿼리 → 실 Supabase에서 브랜드 PKM 큐레이션 **조용한 무동작**(0행 매칭)을 발견(`a9abc16` 수정).
- ★ **테스트가 mock에 `id`를 주입해 live-schema 회귀를 못 잡았다** — 단위 테스트가 실 스키마를 미러하지 않으면 schema-drift를 숨긴다. 회귀 가드 3 추가(실 컬럼 단언).
- 교훈: **dual-AI 교차검토(Claude×CODEX)가 단일 모델·mock이 놓친 결함을 드러낸다** — cross-provider judge 원리의 메타 레벨 재확인. → 패턴 후보 **P-MOCK-SCHEMA-MIRROR-001** / **P-CROSS-AI-REVIEW-001**.

## 4. 불확실/한계 (U-1~)

- **U-1 측정 N·robustness**: 88점 함정·judge 측정 = N=10·rater A N=1(κ 미산출). gpt-4o-mini가 큰 한국어 director 스키마에서 ~절반 malformed/절단 JSON(측정 confound) → 방향성이지 정식 통계 아님.
- **U-2 default judge**: cross-provider/consensus-min은 gated 옵션 — default 전환(major)은 prompt-version-review로 별도.
- **U-3 RAG 코퍼스**: 검색·grounding 가치는 입증, 단 코퍼스 8건(합성) — 값은 큐레이션/2nd-brain 확대가 다음 레버.
- **U-4 pacing 게이트**: payoff(마지막 beat) 가정 + 0.30 임계 — underfill(목표길이) 미배선(target 슬롯 부재).

## 5. 이월

- rater B(팀원) κ — 여전히 BLOCKED(외부 의존).
- JSON robustness 보강 후 클린 N↑ 재측정.
- 코퍼스 확대(큐레이션·2nd-brain).
- **cross-project 수렴 후속**: Phase 32(plotter cross-provider judge 적용) / 33-S2(게이트∘judge 합산 측정) / 34(정직라벨·UX·Gemini).

## 6. 다음

Phase 31 마감 → **Phase 32(cross-project 강점취합 수렴)** active 승격. 게이트(33-S1) 완료분 + plotter judge 초안 기반으로 직교 합산 검증 + 양 프로젝트 수렴.
