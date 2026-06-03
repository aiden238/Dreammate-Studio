# Phase 17 회고 — 계정별 PKM 실빌드 (가 + 다)

> 2026-06-04 | 제품 phase (런타임 有, gated/behavior-preserving) | Phase 16 GO 기반 첫 production 빌드

## 1. 무엇을 했나

"익명 생성 래퍼" → **agent-grade 계정별 PKM 파이프라인**으로 구조 전환. 전부 gated default-OFF.

- **가(실연결)**: 가-S1 신원 plumbing(auth_user_id→generate_plan) / 가-S2 brand_memory 구속 주입(build_brand_constraint_preamble, user_input prepend — Phase 16 교훈) / 가-S3 brand foundation(BrandRepo.get_or_create_default).
- **다(개인 메모리)**: 다-S3 개인 PKM(`pkm_entries` migration 0006 + PkmRepo, CC-022) / 다-S5 brand 추출루프 / 다-S6 개인 추출루프(feedback→추출≥0.9→적재) / 다-S4 e2e PASS.
- **인프라**: get_supabase() service_role key 우선(RLS 우회 server-side) / .env.example / video_projects 레거시 소음 제거.

## 2. 핵심 성과 / 검증

- **PKM 루프 양쪽 폐쇄**: feedback→추출→(brand_memory/pkm_entries)→다음 생성 구속 주입(personal>brand).
- ★ **라이브 입증 3중**: 가-S2(brand 주입 steer) + 다-S4(개인 PKM 전체 루프 e2e, 실 LLM) + **Supabase 모드 e2e**(service key write→영속 재조회 + 주입). 개인 PKM 3건 + 브랜드 PKM 4건 실 Supabase 영속 확인.
- behavior-preserving: 전 슬라이스 gated default-OFF, 익명/무메모리 byte-identical. pytest **470→608**(기존 0 수정) + scenario_sim 36/36 + audit 0 drift.

## 3. 학습 → 패턴

- **주입 방식이 결정적**(Phase 16 계승): PKM 은 rag_context("복제금지 참고") 아니라 **구속 지시(user_input prepend)** 로 — 효과 0 vs 큰 효과.
- **갭 연쇄 발견**: 익명 생성(신원 미배선) → brand_memory anchor 부재(brands 미생성) → brand_memory 비어있음(추출 미배선). 각 갭을 슬라이스로 메움(가-S1→S3, 다-S5/S6).
- **P-LIVE-VERIFY-001 재확인**: 자동 green ≠ 실동작. in-process e2e + Supabase 실DB 조회로 영속까지 확인.
- **service_role 패턴**: server-side 는 service key(RLS 우회) — auth.uid()=null 서버 컨텍스트에서 본인-스코프 write 가능.

## 4. 정직한 한계 / 이월

- **plan 영속**: 생성 plan 은 _plan_store(in-memory)만 — 레거시 save_video_planning(video_projects)은 deprecated+Phase 5 스키마 불일치로 skip. **proper 영속 = orchestrator→PlansRepo 마이그레이션**(테스트 결합 커서 별도 slice 이월).
- **브라우저 Supabase 로그인**: 실 계정 비번 필요 → 자동 드라이브는 mock 으로 검증(로직 동일), Supabase 영속은 in-process e2e 로 입증.
- compounding(쌓일수록↑)은 실사용 데이터 누적이 전제 — 시뮬/시드로 메커니즘만 입증.

## 5. 산출물

- backend: orchestration(신원+주입+brand 해결) · agents/brand_injection · db/repositories/{brand_repo,pkm_repo} · config 4 flag · migration 0006 · db/client service-key · routers/plans(추출 hook×2) · routers(credentials)
- contract: CC-022(db_schema §6.2 pkm_entries)
- frontend: api.ts generate credentials:include
- 리포트: eval/regression_results/2026-06-04_phase-17-pkm-e2e.md
- 테스트: +138 누적(470→608)

## 6. 다음

- **Phase 18 브랜딩 세션(Akinator)** — 제안서 작성됨(`meta/proposals/2026-06-04_branding-session-akinator-design.md`). 발굴→brand_memory 시드→Phase 17 주입 루프 결합.
- **Phase 19~20(provisional) 2nd brain 시각화** — 마이페이지 PKM 도식화(읽기 레이어, 데이터 기반 이미 존재).
- 이월: PlansRepo plan 영속 / Supabase 실계정 브라우저 e2e / commercial_viral / 배포 게이트.
