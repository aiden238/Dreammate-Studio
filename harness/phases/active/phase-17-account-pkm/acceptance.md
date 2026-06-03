# Phase 17 — Acceptance

```
A1. 가-S1 신원 배선 — auth_user_id/brand_id 가 라우터→orchestrator→planning 경로에 (선택적)
    전달된다. 익명(신원 없음) 요청은 기존과 동일(byte-identical). [자동 test]
A2. 가-S2 brand_memory 구속 주입 — 신원+brand_memory+flag 일 때 build_constraint_preamble 가
    planning 입력에 주입되고, 출력이 brand 톤/금지어/잠금선호를 반영. brand_memory 없으면
    프롬프트 byte-identical. [자동 test + 라이브 1건]
A3. 다-S3 personal PKM — pkm_entries migration(contract-change CC) + PkmRepo graceful CRUD +
    개인 메모리 적재/조회. RLS 격리. [자동 test]
A4. 다-S4 통합 주입 — 개인+brand(+series) 결합 주입 + 실 e2e(위저드→신원→주입→3안). [라이브]
A5. behavior-preserving — 익명/무메모리 경로 회귀 0 (기존 pytest 556 green + scenario_sim + audit).
A6. contract-change 규율 — db_schema/agent_io 변경은 contract-change 경유(직접 편집 0).
A7. phase-complete — smoke/scenario_sim + 회고 + archive + REGISTRY/STATE done.
    (선택) Phase 16 하네스로 실데이터 fit 재측정 — 시뮬 대비 실데이터 Δfit 확인.
```

## 검증 매핑

| 기준 | 방법 | 자동/수동 |
|---|---|---|
| A1/A3 | 단위 test (신원 전달 + gated + PkmRepo graceful) | 자동 |
| A2 | 단위 test(주입 gated, 무메모리 byte-identical) + real-mode 1건 | 혼합 |
| A4 | 실 e2e (브라우저/HTTP) | 수동 |
| A5 | pytest 556 baseline + scenario_sim 36/36 + audit_naming 0 | 자동 |
