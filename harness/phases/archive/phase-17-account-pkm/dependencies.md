# Phase 17 — Dependencies

## 선행 (충족)

| 의존 | 상태 | 제공 |
|---|---|---|
| Phase 16 (A/B 실험) | ✅ done | GO(메커니즘) Δfit +0.425 + `build_constraint_preamble`/`score_fit` 검증분 |
| Phase 5 (Auth/RLS) | ✅ done | Supabase Auth + JWT + auth_middleware(request.state.user) + RLS |
| Phase 9 (brand_memory 준비) | ✅ done | brand_memory_entries 테이블 + BrandMemoryRepo + RLS(0005) |
| Phase 8 (MOA orchestrator) | ✅ done | generate_plan() 단일 진입 — 신원/주입 연결 지점 |

## 재사용 자산

```
auth_middleware → request.state.user (auth_user_id/email)   ← 신원 source
BrandMemoryRepo.list_for_brand(brand_id)                    ← brand_memory 로드
eval/ab_experiment.build_constraint_preamble               ← 구속 주입 빌더(Phase 16 검증)
brand_memory_entries(0005) + RLS                           ← 저장/격리 (재사용)
pkm_entries (신규 제안 — 제안서 §8.2)                       ← 개인 PKM (다-S3, contract-change)
```

## 불확실 / 외부

- U1: 현재 /generate(익명) ↔ /plans(인증?) 의 신원 흐름 실측 필요 (가-S1 진입 시 탐색).
- U2: brand_id 가 요청에 어떻게 결정되나(사용자당 brand 1개? 선택?) — 가-S1 확인.
- U3: 실데이터 fit 재측정은 실 brand_memory 적재 데이터 필요(없으면 시뮬로 대체).
