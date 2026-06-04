# Phase 23 — 품질 정식화 (실 LLM 전수 eval baseline + human review 정비)

## 목표
지금까지 mock-deterministic eval(구조 정확성)만 CI 화 → **실 LLM 품질 baseline** 확정.
1. **실 LLM 전수 baseline**: golden_set 25 케이스를 실 LLM(rich planning + 9차원 critic)로 전수 평가 → overall/depth/verdict 분포 + P0/P1/P2 pass + 광고/차단 clean 리포트.
2. **human review 정비**: Phase 12 S4 kit(compact vs rich)에 LLM-judge 대조 컬럼 추가 + 사용자 실채점 시트 준비(★ 실채점은 사용자 액션 = deferred, Phase 12 S4 동일).

## 근거
- 로드맵 D(품질 정식화) + Gate D 전제(실 LLM eval baseline). eval 인프라 조사: real 경로 wire됨(graceful fallback)이나 **전수 baseline 미확정** + human kit 실채점 대기.
- depth_actionability = critic 9번째 차원(rich) → 실 LLM 으로만 의미 채점(mock 미채점).

## 핵심 원칙
- ★ 운영 코드 0 수정 — eval 은 측정/리포트, behavior-preserving. mock CI 경로 불변.
- 실 LLM = opt-in 비용(전수 ~$0.3~0.5). 1회 실행 baseline.
- human 실채점은 사용자 — 본 phase 는 시트/대조 **준비**까지.

## 산출 (슬라이스)
S1(실 LLM 전수 baseline 러너 + 리포트) → S2(human kit LLM-judge 대조 + 실채점 시트 정비 + close).
