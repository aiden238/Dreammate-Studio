# Phase 16 — Acceptance 기준

> 각 항목은 H1/H2 + 산출물에 매핑. 자동화 가능한 것은 자동, 사람 채점은 사용자 확인.

```
A1. A/B 하네스 통제 검증 — 동일 입력 × {A,B} 쌍 생성 시 A와 B가 데이터/검색 레이어
    (use_rag/brand_memory/PKM)만 다르고 모델·프롬프트·output_mode·temp는 동일함을 단위 test로 입증.
    [검증] 자동 (단위 test — 두 arm 호출 파라미터 diff = 주입 컨텍스트만)

A2. 정적 H1 측정 — real-mode critic 8~10차원 + depth_actionability로 케이스 부분집합(~10)에
    대해 B−A를 산출하고 리포트화. (키 제공 시 real, 미제공 시 mock fallback 명시)
    [검증] 자동 배치(opt-in) + eval/regression_results/{date}_ab-experiment.md

A3. 사람 blind 채점 — A/B 라벨 가린 채점 키트 생성 + 사용자 채점 결과 수집(B 선호율).
    [검증] 수동 (사용자) + eval/human_review/{date}_ab-blind.md

A4. 종적 H2 측정 — 시뮬 PKM 누적 N={0,5,20}에서 B 품질 + 기울기. N=0은 B≈A(sanity).
    [검증] 자동 배치(opt-in) + 리포트

A5. 종합 판정 — go/no-go/partial을 숫자 기준(기획안 §4)으로 산출 + PARKED 로드맵 재우선순위 제안.
    [검증] S5 리포트 + multi-llm-validation(임계값 확정)

A6. behavior-preserving — Arm A = 현재 use_rag=False 경로 byte-identical. 시뮬 fixture는 실험/test
    영역만. 기존 pytest baseline green (기존 test 수정 0).
    [검증] 자동 (pytest + audit_naming 0 drift)

A7. phase-complete — smoke + scenario_simulation + 회고 + archive + REGISTRY/STATE done.
    [검증] phase-complete Skill 절차
```

## go/no-go 기준 (rough — A5에서 확정)

```
GO     : H1 B−A ≥ +0.15 (0~1 척도) 또는 사람 blind B 선호 ≥ 65%  AND  H2 기울기 양수·단조
PARTIAL: scope별 분해상 일부만 효과 (효과 scope만 빌드)
NO-GO  : B ≈ A → 무거운 PKM/RAG 보류, 차별화 레버 전환
```
