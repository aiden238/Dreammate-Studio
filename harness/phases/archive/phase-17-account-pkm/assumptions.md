# Phase 17 — 진입 4점검 (phase-start §6)

## 1. Assumptions

### 1.1 확정
- Phase 16 GO(Δfit +0.425) + `build_constraint_preamble`/`score_fit` 검증분 재사용.
- auth_middleware 가 request.state.user 주입(Phase 5) — 신원 source 존재.
- brand_memory_entries + BrandMemoryRepo + RLS(0005) 존재 — 저장/로드 재사용.
- **audit_naming 통과 (2026-06-04, 0 drift)**.
- gated/behavior-preserving 원칙: 익명/무메모리 경로 byte-identical (회귀 0).

### 1.2 불확실 (phase-complete 회고)
- U1: 익명 생성 흐름에 신원 주입 지점 정확 위치(라우터/orchestrator) — 가-S1 탐색.
- U2: brand_id 결정 규칙(사용자↔brand 관계) — 가-S1 확인.
- U3: 실 brand_memory 데이터 부재 시 실데이터 fit 재측정 제약(시뮬 대체).

## 2. Simplest Slice (3회 압축)

```
1차: 신원 배선 + brand_memory 주입 + pkm 테이블 + 통합.
2차: auth_user_id 가 planning 호출까지 (gated) 도달, 익명 byte-identical.
3차: 라우터가 request.state.user.auth_user_id 를 generate_plan() 에 optional 인자로 전달 —
     미존재 시 기존과 100% 동일. ★ 가-S1 = 신원 plumbing only(주입 X, 회귀 0 입증).
```
→ 가-S1(신원 plumbing) → 가-S2(brand_memory 구속 주입) → 다-S3(pkm_entries) → 다-S4(통합+e2e).

## 3. Surgical Scope
- editable: backend routers/orchestrator/planning/config + db migration/repo + tests + phase/state/meta.
- read-only (→contract-change): docs/contracts/* + prompt_registry.
- forbidden: phases/archive/*, commercial_viral, 영상 제작.
- ★ Sub-agent 사용 시 P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- 가-S1: 단위 test(신원 전달 gated + 익명 byte-identical) + pytest 556 회귀 0.
- 각 슬라이스: behavior-preserving(무신원/무메모리 byte-identical) + audit_naming 0 + scenario_sim.
