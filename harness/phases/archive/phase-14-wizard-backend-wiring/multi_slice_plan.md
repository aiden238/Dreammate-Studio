# Phase 14 — Multi-Slice Plan

> Entry + 4 Slice. Scope A(최소 배선). ★ 랜딩 `/` byte-identical(behavior-preserving) + 키 0 + pytest 499 회귀 게이트. 각 Slice sub-agent + P-X1 §SELF-VERIFICATION.

## Wave 구조
```
Entry [8 entry + validation self(13th) + REGISTRY/STATE active]  (본 문서)
  ↓
S1 [백엔드: wizard_data → 생성 user_input additive 조립 (랜딩 initial_input 경로 byte-identical) + tests]
  ↓                                                            ┌ (S1 백엔드 의존)
S2 [프론트: Quick 위저드 실연결 (startPlan→wizardStep×→generateMultiPlan→/plan/[id], mock 제거)]
  ↓
S3 [프론트: Discovery 위저드 실연결 (동일 패턴, 7-step)]   (S1 의존, S2 와 동형)
  ↓
S4 [라이브 e2e(rich ON 1회) + 회귀(499+신규) + phase-complete]   (전체 의존)
```

## Entry (본 문서 — phase-start)
- 8 entry + `meta/validations/2026-06-03_phase-14-pre-entry_self.md`(multi-llm-validation self 13th) + PHASE_REGISTRY(14 pending→active) + PROJECT_STATE active.
- sub-agent: **main**. P-X1: 운영 .py 0(entry=계획).

## S1 — 백엔드 wizard_data 소비 (additive, behavior-preserving)
1. generate 입력 조립: `initial_input` 우선, 없고 `wizard_data` 있으면 step 입력(brand/domain/series/target/tone/direction or quick.*)을 **한 user_input 문자열로 조립** (`moa_orchestrator.py` 또는 `plans.py`). ★ `wizard_data` 없으면 기존 경로 byte-identical.
2. (필요 시) `api_contract.md` §8 위저드 생성 입력 소비 명시 — contract-change.
3. tests: ① wizard_data 조립 케이스 ② 랜딩(initial_input) 회귀 0 ③ 둘 다 없을 때 "(빈 입력)" 폴백 유지.
- sub-agent: 1 dispatch. editable: plans.py/moa_orchestrator.py + tests + (api_contract). forbidden: 랜딩 경로 동작 변경, frontend(S2/S3).
- ★ 산출: wizard_data additive 소비 + pytest 499→+신규.

## S2 — Quick 위저드 실연결 (frontend)
1. `app/new/quick/*`: 진입 시 `startPlan()` → step별 `wizardStep(plan_id, step, data)` → 최종 `generateMultiPlan(plan_id)` → `router.push('/plan/{plan_id}')`. plan_id 위저드 상태 보관.
2. `buildMockPlan`/setTimeout mock 제거. 생성 대기 UX(ProgressStepper)는 실 호출 await 로 전환.
- sub-agent: 1 dispatch. editable: app/new/quick/**, lib/api·state(필요분). forbidden: 랜딩, backend, Discovery(S3), per-step LLM.
- ★ 산출: Quick 위저드 → 실 3-plan → /plan/[id].

## S3 — Discovery 위저드 실연결 (frontend)
1. `app/new/discovery/step/1~7`: 동일 패턴(startPlan→wizardStep×7→generateMultiPlan→/plan/[id]). 중간 step 카드(brand/domain 등)는 **현행 입력 수집 UX 유지**(per-step 실 LLM = NG1).
2. mock plan 생성(setInterval) 제거.
- sub-agent: 1 dispatch. editable: app/new/discovery/**, lib. forbidden: 랜딩, backend, per-step LLM 카드 생성.
- ★ 산출: Discovery 위저드 → 실 3-plan → /plan/[id].

## S4 — 검증 + 종료
1. 라이브 e2e: 로컬 서버(rich ON 데모) 에서 Quick + Discovery 위저드 완주 → 실 rich 카드(/plan/[id]) 확인.
2. 회귀: pytest 499 + 신규 green + 랜딩 byte-identical + 키 0.
3. phase-complete: retrospective + closing + archive + REGISTRY 14 done + PROJECT_STATE.
- sub-agent: **main** 또는 1. editable: eval/regression_results/phase-14-*, retrospective, closing, state docs.
- ★ 산출: 라이브 입증 + 회귀 + close.

## 충돌 매트릭스
| Slice | backend(plans/moa) | quick frontend | discovery frontend | eval/close |
|---|---|---|---|---|
| S1 | ✅ | ❌ | ❌ | ❌ |
| S2 | ❌ | ✅ | ❌ | ❌ |
| S3 | ❌ | ❌ | ✅ | ❌ |
| S4 | ❌ | ❌ | ❌ | ✅ |
S2·S3 는 S1 의존(순차), 충돌 0.

## Skill 트리거
| Slice | Skill |
|---|---|
| Entry | multi-llm-validation(self 13th) + phase-start |
| S1 | (contract-change api_contract 필요 시) + behavior-preserving 게이트 |
| S2/S3 | design-review(위저드 흐름·모바일·제작UI 미포함) |
| S4 | qa-check(release gate) + meta-retrospective + phase-complete |

## 시간 추정
Entry ~1h + S1(백엔드 additive) ~1.5h + S2(Quick) ~2h + S3(Discovery) ~2h + S4(라이브+close) ~1.5h.
