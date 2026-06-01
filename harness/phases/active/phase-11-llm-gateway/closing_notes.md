# Phase 11 — Closing Notes (LLM Gateway A안 — cross-validation, 제품 phase)

> 종료일: 2026-06-01 (코드 선완료 + 본 retroactive 정식화)
> 결과: ✅ LLM Gateway(alias→provider) + Gemini 교차검증(gated default-off) / pytest 381→435 / behavior-preserving / 라이브 consensus 입증 / 키 commit 0
> ★ 가속 빌드: 코드 S1·S2·S3 선완료·commit·push, 본 entry 는 retroactive 정식화(코드 0 변경)

## 산출물 (코드 — 선완료)
- S1 (`e1422a6`): `llm/` 패키지(types/errors/registry/aliases/gateway + providers/base·openai_adapter·gemini_adapter) + config additive(google_api_key/cross_validation_model) + test_llm_gateway(31). agents 미연결(behavior-preserving).
- S2 (`f382b6e`): `llm/cross_validation.py`(cross_validate + compare, 순수 함수) + gemini_adapter 튜닝(thinking_budget=0 + 503 재시도 + text fallback) + config additive(cross_validation_enabled default False / gemini_thinking_budget) + test_llm_cross_validation(19).
- S3 (`1ee1c08`): moa_orchestrator §5.5 gated hook(critic 후, default OFF, 로깅만, Envelope 불변, graceful) + per_plan_verdicts additive + test_cross_validation_wiring(4).

## 산출물 (문서 — 본 entry, retroactive)
- entry 8 (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes) + closing_notes.
- ADR-039 (`docs/decisions/phase_11_llm_gateway.md`).
- contract-change CC-010 — `cost_control_policy.md` additive 확장(tier×mode→alias 표 + cross_validation 비용) + `docs/contract_changes/2026-06-01_phase-11-cost-control.md`.
- `meta/retrospectives/phase-11.md`.

## 최종 baseline
| 지표 | Phase 10 final | Phase 11 final |
|---|---|---|
| pytest | 381 | **435** (+54: gateway 31 + cross-val 19 + wiring 4. 기존 381 green, 수정 0) |
| LLM Gateway | — | **alias→provider seam** (registry/alias/gateway + openai/gemini adapter) |
| cross_validation | — | **Gemini 8차원 + compare(consensus/divergence)** — gated default-off, 로깅만 |
| 라이브 입증 | — | **OpenAI 생성 + Gemini consensus** (수동, gemini-2.5-flash 0.7375 vs OpenAI 0.72) |
| agent 수 | 6 | **6 유지** (cross_validation = Critic 추가 pass) |
| P-X1 streak | 60 | **63** (S1·S2·S3) |
| contract-change | CC-009 | **CC-010** (cost_control additive, 누적 11회) |
| PlanCard / component_map 0줄 | 35 / 45 | **유지** (frontend 0 변경) |
| 키 commit | 0 | **0 유지** (.env user-provided, registry env 참조만) |

## ★ 사용자 보고 형식
| 항목 | 내용 |
|---|---|
| 변경 파일 (코드) | 신규 ~13 (llm/ 패키지 + 3 test) / 수정 ~3 (config additive + gemini_adapter + moa_orchestrator additive gated) |
| 변경 파일 (문서) | 신규 ~12 (entry 8 + closing_notes + ADR-039 + CC-010 로그 + retrospective) / 수정 1 (cost_control_policy additive) |
| 핵심 | LLM Gateway(alias→provider, agent 코드 0 변경 토대) + Gemini 교차검증(gated default-off, 로깅만) + Gemini adapter 튜닝(thinking/503) + cost_control CC-010 additive |
| 런타임 변경 | 有(제품 phase) — 단 behavior-preserving(기존 endpoint/agent/test 0 수정, gateway 미연결 + gated default-off), 기존 381 green |
| cross_validation | gated(default OFF) — 발화 시 로깅만(Envelope 불변). 활성 = flag + GOOGLE 키 opt-in. 라이브 consensus 입증 |
| 다음 | agents Stage A 전환 / B안(3-provider) / cost 재조정 / full 라이브 /generate 데모 / cross_validation 응답 노출(output_schema CC) |

## 다음 단계
1. **agents Stage A 전환** — `client or OpenAI(...)` → `gateway.openai_client()` + `resolve_model(alias,...)` 2줄(제안서 §4.1·T-2, behavior-preserving). gateway 경유 OpenAI 호출.
2. **B안 (Phase 12+)** — 3-provider 다양성 + Anthropic adapter + cost_control 전면 재조정(신모델 5~7배) + multi-llm-validation + eval-run(제안서 §18.B).
3. **full 라이브 /generate 데모** — wizard 전체 흐름 + flag ON cross_validation 로그.
4. **cross_validation 응답 노출** — output_schema contract-change + consensus/divergence UX.

## Phase 1~11 총괄
```
Phase 0    : 하네스 마이그레이션
Phase 1~4  : MVP 기본 + PWA + FastAPI
Phase 4.5~6: Critic revise + Output Schema 안정화
Phase 5/5.5: DB/Auth/RLS/SSE + Legacy 통합
Phase 7    : RAG Lite     Phase 8 : MOA orchestrator     Phase 9/9.5 : 결과저장+피드백 + eval-run
M0~M3      : Meta-Factory (self-improvement loop 완주)
Phase 10   : MVP end-to-end 통합 + 배포 Gate A ✅
Phase 11   : LLM Gateway A안 (alias→provider + Gemini 교차검증 gated) ✅
→ LLM Gateway 추상화 토대 + 교차검증 capability(gated). 다음 = agents Stage A 전환 / B안 / 배포 Gate B~G.
```
