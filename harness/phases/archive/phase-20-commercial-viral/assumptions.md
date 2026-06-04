# Phase 20 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- PARKED 제안서 §0.2 선행조건(a rich 실사용 / b 위저드 실연결 / c human review) + 데이터레이어(PKM/RAG) **전부 충족** → 착수 정당(validate-before-expand).
- director(Phase 15) 패턴 **직접 계승** — output_mode enum + DIRECTOR_FIELDS + model_dump_for_mode + DirectorScene + DIMENSIONS_RICH gated. commercial_viral = 동일 패턴 1-tier 위(겹침 0, COMMERCIAL_FIELDS 별도).
- gated/additive/OFF byte-identical — default=compact 불변. compact/rich/director 직렬화 키 불변.
- **audit_naming PASS (2026-06-04, no drift)** — CC-024 §8.7 포함.
- v1 = LLM-only(보정3 추측 표기). 실데이터 enrichment 후속.
### 1.2 불확실
- U1 director↔commercial 슬롯 경계 → 현 director=DIRECTOR_FIELDS(3 전용)이라 commercial=COMMERCIAL_FIELDS(10 별도)로 깔끔 분리(S1 확정).
- U2 추측표기 UX / U3 scene N씬 상한 / U4 17차원 비용·지연 — S6 실측.

## 2. Simplest Slice (3회 압축)
```
1차: schema + prompt + wiring + critic + frontend + live verify (full tier).
2차: schema + prompt + wiring + live verify (core); critic/frontend follow.
3차: output_mode Literal +commercial_viral + COMMERCIAL_FIELDS(10) + CommercialScene(7) +
     Plan additive 슬롯 + model_dump_for_mode 4-tier 확장. LLM/wiring 없이 직렬화 단위 test.
     ★ compact/rich/director byte-identical(COMMERCIAL 제외) — 기존 668 불변.
     ← S1 = schema 단독(mock/단위 test, Phase 15 S1 과 동형).
```
→ S1(schema) → S2(prompt) → S3(wiring) → S4(critic 17차원) → S5(frontend) → S6(live verify+cost+close).

## 3. Surgical Scope
- editable: config.py(Literal) + schemas/output.py + agents/planning.py + agents/critic.py + orchestration + apps/web(S5) + tests + phase/state/meta.
- read-only(→contract-change): output_schema.md · prompt_registry.md · cost_control_policy.md.
- forbidden: product_boundary 침범(영상 제작) / 새 MOA agent / commercial_viral default ON / archive / 데이터레이어 신규 파이프.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: model_dump_for_mode 4-tier 단위 test(commercial dump=전체 / director·rich·compact 에서 COMMERCIAL 제외) + 기존 668 green(byte-identical).
- 각 슬라이스: behavior-preserving(pytest 668) + scenario_sim 36 + audit 0.
- A7 라이브: commercial_viral 생성 슬롯 채움 + 보장표현 0 + 추측표기 + OFF byte-identical.
