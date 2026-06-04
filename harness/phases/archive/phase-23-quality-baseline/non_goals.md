# Phase 23 — Non-Goals

```
- ★ 운영 코드 변경 금지 — eval 은 측정/리포트만. behavior-preserving(pytest 714 불변).
- ★ mock CI 경로 → real 자동 전환 금지 — real 은 opt-in 1회 baseline. CI 는 mock 유지(비용 0, ADR-033).
- golden_set 케이스 변경/추가 금지 — 25 케이스 고정(채번 불변), 측정만.
- human 실채점 수행 금지(불가) — 채점은 사용자. 본 phase 는 시트/대조 준비까지(deferred = Phase 12 S4 동일).
- 가중 평균 산식 변경 금지 — 현 산술 평균 유지(가중 도입은 별도 prompt-version-review).
- 3안(parallel_3) 전수 미포함 — baseline 은 케이스당 1안(rich)으로 비용 통제(전수 3안은 후속).
- rich default 전환 결정 금지(별도) — baseline 은 측정만.
- Gate D 실 배포/베타 환경 미포함 — 본 phase 는 baseline 수치 확보.
```
