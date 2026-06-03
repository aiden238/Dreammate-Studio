# Phase 17 — Closing Notes (계정별 PKM 실빌드)

> 종료: 2026-06-04 | 제품 phase (gated/behavior-preserving) | 게이트: pytest 608 + scenario_sim 36/36 + audit 0

## Acceptance 판정

| # | 기준 | 상태 | 근거 |
|---|---|---|---|
| A1 | 가-S1 신원 배선 | ✅ | auth_user_id→generate_plan (가-S1, 433167d), 익명 byte-identical |
| A2 | 가-S2 brand_memory 구속 주입 | ✅ | build_brand_constraint_preamble + gated, ★라이브 steer 확인 (8ebedc5) |
| A3 | 다-S3 personal PKM | ✅ | pkm_entries(0006)+PkmRepo+주입, CC-022 (f1dbf2e) |
| A4 | 다-S4 통합 실 e2e | ✅ | 개인 PKM 전체 루프 e2e PASS(실 LLM) + Supabase 영속 e2e (ed0c710) |
| A5 | behavior-preserving | ✅ | pytest 470→608(기존 0 수정) + scenario_sim 36/36 + audit 0 |
| A6 | contract-change 규율 | ✅ | CC-022(db_schema §6.2 pkm_entries) |
| A7 | phase-complete | ✅ | 본 종료 |

★ 추가(범위 내 확장): 가-S3 brand foundation(BrandRepo) / 다-S5 brand 추출루프 / 다-S6 개인 추출루프 / get_supabase service-key / video_projects 소음 제거.

## 핵심 결론

```
PKM 루프 양쪽 폐쇄: feedback→추출(≥0.9)→(brand_memory/pkm_entries)→다음 생성 주입(personal>brand).
전부 gated default-OFF + behavior-preserving. 라이브 3중 입증(brand steer / 개인 e2e / Supabase 영속).
Supabase 실DB: 개인 PKM 3건 + 브랜드 PKM 4건 + brands 1 영속 확인.
```

## 이월 (follow-up)

- **PlansRepo plan 영속**(orchestrator→PlansRepo, video_projects 레거시 대체) — 테스트 결합으로 별도 slice.
- Supabase 실계정 브라우저 e2e(비번 필요 — 사용자 직접) / commercial_viral / 배포 게이트.

## 다음 Phase

- **Phase 18 브랜딩 세션(Akinator)** — 제안서 `meta/proposals/2026-06-04_branding-session-akinator-design.md`.
- **Phase 19~20(provisional) 2nd brain 시각화**.
