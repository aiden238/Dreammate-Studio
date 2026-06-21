# 회고 — Phase 28: 2nd brain 학습 루프

> 2026-06-08~ | 브랜치 `phase-28-2ndbrain-loop` | "쓸수록 내 브랜드를 이해하는 영상기획 2nd brain" /GOAL을 향한 단계적 빌드 — 저장→강화/정리→컨셉 루프 연결

## 1. 무엇을 했나

라이브 테스트에서 드러난 갭(홈 입력이 막다른 길 = 레거시 /generate 저장 실패 + 피드백→학습 미연결 → 첫 사용자가 써도 brain 0건)을, "모든 대화 → 저장 → 강화/정리 → 컨셉" 루프로 연결. /GOAL을 한 번에 도달이 아니라 이번 기획의 방향 목표로 삼아 단계적으로 빌드(사용자 합의 2026-06-08, 학습 신호 = 명시 피드백 + 암묵 신호 둘 다).

- **S1 모든 대화 저장 + 학습 연결**(6bc2a2b): 홈 handleSubmit을 plans 흐름으로 전환 — startPlan→/plan/[id]가 generateMultiPlan(credentials=auth)+영속(plans)+피드백 UI 제공 → 어느 경로로 써도 저장+피드백→학습(PKM). 검증: 데모 e2e plans 0→1, pkm 0→2.
- **S2 반복 강화 + 불필요 제거**(6aef3f5): `PkmRepo.consolidate_entry`(노이즈 필터 + 유사 재등장=강화·dedup / 신규=insert, confidence 재활용 — **스키마 변경 0**) + `decay_and_prune`(미강화 비-locked entry ×0.95 decay → floor 0.3 미만 제거, user_locked 보호). 주입(moa_orchestrator)도 confidence desc top-8 cap. 검증: 단위 5 + 실 Supabase(0.9→1.0→dedup) + hermetic 814→819.
- **S3 나만의 컨셉 수렴**(28e2c33): 누적 PKM 1회 LLM 합성 → 핵심 컨셉 한 줄 + 기둥 + 모순쌍 표면화. `GET /me/concept`(read-time, 영속 0 = NG12 계승), `concept_synthesizer.py`, /brain 상단 '내 컨셉' 카드. gated default-off(realuse ON). 검증: 라이브 11신호 → concept + warm↔neon 모순 자동 검출, pytest 821→827.

머지(aa2d236): origin/main(중간발표·WBS 문서 7커밋) ↔ phase-28/29(11커밋) 경로 분리(docs/ vs harness/)로 충돌 0 자동 병합.

## 2. 잘된 점

- **스키마 변경 0으로 강화 루프 구현** — S2 consolidate/decay 전부 기존 confidence 컬럼 재활용. 마이그레이션 없이 "반복 강화·불필요 제거" 비전 달성, 실 Supabase에서 0.9→1.0→dedup 검증.
- **노이즈 억제 실증** — generic 무정보('반복 선호한 기획 패턴' 류) 더는 안 쌓임. 추출 품질 정련이 brain 신뢰도로 직결.
- **gated + behavior-preserving 일관(Phase 27 계승)** — S3 concept_surfacing OFF/익명 시 합성 미호출 byte-identical, 회귀 6종으로 게이트 경계 고정.
- **read-time 합성(영속 0, NG12 계승)** — 컨셉을 저장하지 않고 매 조회 시 재합성 → 신호 누적에 자동 추종, 캐시 무효화 부담 없음.

## 3. ★ 핵심 사건 또는 패턴 — 막다른 길(silent dead-end)의 비용

- 라이브 테스트 전까지 코드는 PASS였으나 **가장 눈에 띄는 진입(홈)이 레거시 경로로 빠져** 저장도 학습도 0건이었음. 단위/빌드 green과 "실제로 brain에 쌓이는가"는 별개 — **end-to-end 신호 누적을 데모 e2e로 직접 계측**(plans 0→1, pkm 0→2)해야 드러남.
- **교훈**: 학습 루프류 기능은 "코드 경로 존재"가 아니라 "신호가 실제로 적재되는가"를 acceptance로 잡아야 한다. → 패턴 후보 **P-LEARNING-LOOP-E2E-COUNT**(저장·학습은 카운트 증가 e2e로 통과 검증).

## 4. 불확실/한계 (U-1~U-4)

- **U-1**: brand PKM(시드) 강화 parity 미구현 — 개인 PKM만 consolidate/decay 적용, brand 측 강화는 후속.
- **U-2**: decay가 패스-기반(미강화 시 ×0.95)이라 **시간 기반 decay 아님** — 호출 빈도에 의존, time-based는 후속.
- **U-3**: concept 합성 품질은 라이브 11신호 1케이스 검증 — 신호 수·도메인 다양성에 따른 합성 안정성 미상.
- **U-4**: 실 누적 곡선(여러 세션에 걸친 강화/decay 수렴)은 실사용 opt-in 필요 — 자동은 단일 패스까지.

## 5. 이월

- **brand PKM 강화 parity** + **시간 기반 decay** — S2 후속.
- **concept 합성 품질 평가** — golden_set/rubric에 컨셉 수렴 차원 추가(eval-design 트리거 후보).
- **실 라이브 다세션 누적 검증** — 강화·prune·컨셉 수렴이 여러 세션에 걸쳐 실제로 수렴하는지(사용자 opt-in, 비용+Supabase).

## 6. 다음

저장→강화→컨셉 루프 1차 배선 완료 → **다음 = 에이전트 UX(phase-29) + 컨셉 품질 계측·다세션 실누적 검증**. /GOAL("쓸수록 내 브랜드 이해")로의 방향 정합 유지.
