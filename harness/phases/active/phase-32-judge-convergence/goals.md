# Phase 32 — Judge 수렴 (cross-provider + consensus, plotter ← Dreammate) · goals

> 상세 설계: `meta/proposals/2026-06-22_cross-project-convergence-plan.md` (Phase 32 절). Phase 31 마감 후 active 승격.

## 목표
plotter가 보류한 **cross-provider judge**를, Dreammate 측정 근거로 재고·적용해 양 프로젝트가 동일한 self-review-편향-차단 judge층을 갖게 한다. consensus-min(in-provider ∧ cross, 더 엄격)으로 비용/키 의존을 통제.

## 배경
plotter ADR-0031 D1-C("항상 Opus" cross-provider)·ADR-0007 대안C가 "B로 cross-model 편향 남으면/κ<0.5면 재고"로 보류. Dreammate가 in-provider judge에 편향 잔존(false-approve 10/10) + cross-provider가 닫음(0/10, ko 사람정렬 0.53)을 측정 → **재고 트리거 충족**. 결정적 게이트(Phase 33 S1, 구현완료)와 **직교** — 둘 다 필요(calib-ab-preliminary:43).

## 통과 기준
cross/consensus가 in-provider judge 대비 false-approve↓(또는 비퇴행) + 비용 가드 내 + gated default 비퇴행. plotter 적용·측정(원격, user 협조).

## 명시적 결정
- cross-provider judge는 **gated 옵션 + consensus-min**(default 전환 아님 — major, 별도).
- 3-judge ensemble 부활 아님(plotter ADR-0007 기각 존중). MoA(generation diversity) 무관.
