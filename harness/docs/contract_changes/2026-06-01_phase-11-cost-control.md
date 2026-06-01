# Contract Change Log — Phase 11 LLM Gateway A안 (cost_control_policy 확장)

> ID: CC-010
> Status: **decided + applied** (2026-06-01, Phase 11 A안 정식화)
> Date: 2026-06-01
> Decision: cost_control_policy 에 LLM Gateway **tier×mode → alias → model 표**(§11) + **cross_validation 비용**(§12, Gemini 1회, gated) **additive** 추가. 기존 §1~§10 전부 보존.
> Author: Claude (Phase 11 정식화 sub-agent)
> Related contracts: `ai_system/orchestration/cost_control_policy.md` (비용 통제 단일 출처)
> Related ADR: ADR-039 (`docs/decisions/phase_11_llm_gateway.md` — LLM Gateway A안 + cross_validation gated)
> Related proposal: `meta/proposals/2026-05-31_llm-gateway-design.md` §6 / §18.A·§18.D
> Skill: contract-change (절차)

---

## 1. 변경 요약

| 대상 | 변경 | 종류 |
|---|---|---|
| `cost_control_policy.md` §11 (신규) | **LLM Gateway tier×mode → alias → model 표** — agent=alias / gateway=provider 결정. 현 §5 모델 선택 정책을 alias 표로 선언적 정식화(byte-identical 해석). cost_saving Critic 폴백을 alias 로 흡수. | **additive** |
| `cost_control_policy.md` §12 (신규) | **cross_validation 비용** — Gemini 1회 교차검증(gated default-off). 호출당 상한 $0.002 + additive 반영 권고(활성 시) + B안 cost 재조정 보관. | **additive** |
| §1~§10 (기존) | **무변경** — user tier(무료/유료) + 호출당/세션당/일일 상한 + cost_saving + 토큰 압축 + cost-review 연동 전부 보존. | **보존** |

## 2. 코드 영향

```
★ 코드 0 변경 — 본 CC-010 은 cost_control_policy.md 문서 확장만.
  cost_control 표는 LLM Gateway(backend/fastapi/llm/aliases.py·registry.py, S1·S2 선완료)의
  alias 표를 문서로 정식화한 것 — 코드는 이미 존재(commit e1422a6/f382b6e), 본 변경은 contract 문서.
관련 코드 (Phase 11 S1~S3, 이미 commit·push — 본 CC 와 무관하게 선완료):
  backend/fastapi/llm/aliases.py     — alias 표 (planning→gpt-4o-mini, critic={standard:gpt-4o,
                                       cost_saving:gpt-4o-mini}, cross_validation→gemini-cross).
  backend/fastapi/llm/registry.py    — gemini-cross model_id = settings.cross_validation_model.
  backend/fastapi/config.py          — cross_validation_enabled (default False), cross_validation_model.
  backend/fastapi/orchestration/moa_orchestrator.py §5.5 — gated hook (default OFF, 로깅만).
```

## 3. 회귀 안전 근거 (behavior-preserving)

- **기존 정책 불변 ★**: §1~§10(설계 원칙 / 호출당·세션당·일일 상한 / 모델 선택 / 토큰 압축 / 초과 처리 / cost-review / 의존성 / Open Questions)은 0 변경. 본 변경은 §11·§12 **append만**.
- **현 모델 선택 byte-identical ★**: §11.2 표의 `free × standard` = 현 §5 default(workhorse gpt-4o-mini + Critic gpt-4o), `cost_saving` = 현 §5 마지막 줄(Critic gpt-4o→mini 폴백)을 alias 로 정식화 — **동일 해석**. gateway.resolve_model 단위 test(`resolve_model("planning")==gpt-4o-mini` / `("critic","-","standard")==gpt-4o` / `("critic","-","cost_saving")==gpt-4o-mini`)로 강제(ADR-039).
- **cross_validation 비용 증가 0 (default) ★**: §12.1 — cross_validation_enabled default False → orchestrator hook 미발화 → 비용 발생 0. 활성(flag + GOOGLE 키 opt-in) 시에만 Gemini 1회분 additive(recommended plan 1개, 세션당 +1회). 키 없으면 graceful skip(비용 0).
- **flagship 기본 호출 0 ★**: §11.2 "premium" mode + premium_review(flagship)는 후속 B안 표시만 — A안 미구현. Opus/GPT flagship 기본 호출 경로 0.
- **키 0 ★**: registry 는 env(`cross_validation_model` / `google_api_key`) 참조만 — 실 키 비포함. .env user-provided + .gitignore. CC 문서/commit 평문 키 0.

## 4. 검증 결과

```
cost_control_policy.md: §1~§10 diff 0 (보존) + §11·§12 신규 append (additive).
관련 코드 (Phase 11 S1~S3, 선완료): pytest 381 → 435 PASS (gateway 31 + cross-val 19 + wiring 4,
  기존 381 green 수정 0). 본 CC 는 문서 변경 — pytest 무관(435 유지).
alias 해석 byte-identical: gateway.resolve_model 단위 test 강제 (현 default 와 동일).
cross_validation gated default-off: cross_validation_enabled=False → hook 미발화 (Envelope 불변).
키 commit: 0 (.env user-provided, registry env 참조만).
```

## 5. Rollback

- `cost_control_policy.md` §11·§12 블록 git revert → §1~§10 만 남음(Phase 10 상태). 기존 비용 정책 불변.
- 관련 코드(llm/ alias 표)는 Phase 11 S1~S3 commit(e1422a6/f382b6e/1ee1c08) 단위 revert 가능(P-X1, 별도) — 본 CC 와 독립.

## 6. 변경 이력

- 2026-06-01: Phase 11 A안 정식화 — cost_control_policy §11(tier×mode→alias 표) + §12(cross_validation 비용, gated) additive 추가. 기존 §1~§10 보존. behavior-preserving + 키 0 (CC-010).
