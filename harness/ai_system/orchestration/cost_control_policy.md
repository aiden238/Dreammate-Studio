# cost_control_policy.md — 비용 통제 정책

> 위치: `ai_system/orchestration/cost_control_policy.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/agent_io_contract.md` §9, `docs/contracts/rate_limit_policy.md`
> 참조: `eval/cost_snapshots/` (스냅샷), `cost-review` Skill

---

## 1. 목적

영상기획 AI는 LLM 호출 비용이 가변 비용의 대부분을 차지한다. 본 정책은 사용자별 / 세션별 / 호출별 한도를 정의하고, 한도 초과 시 처리 방식을 강제한다.

설계 원칙:
- **선제 차단**: 한도 초과가 예상되면 호출 전에 차단.
- **사후 기록**: 모든 호출은 cost 측정 후 agent_io_logs에 기록.
- **점진 강등**: standard → cost_saving → blocked 순으로 강등.

---

## 2. 호출당 (per-call) 상한

agent_io §9.1 일치. 단위: USD.

| Agent / Prompt | model | 상한/호출 |
|---|---|---|
| Intent P-AUX-1 | gpt-4o-mini | $0.0002 |
| Intent P-001~P-004 (cards) | gpt-4o-mini | $0.001 |
| Intent P-005 / P-005q | gpt-4o-mini | $0.0005 |
| Planning P-006 | gpt-4o-mini | $0.003 (1.5×: $0.0045 abort) |
| Critic P-007 standard | gpt-4o | $0.006 (cost_saving: $0.001) |
| Rewriter P-008 | gpt-4o-mini | $0.0015 |
| Memory Extractor P-AUX-2 | gpt-4o-mini | $0.0015 |
| Knowledge Evaluator P-EVAL-1 | gpt-4o-mini | $0.0005 |

호출 후 측정 cost가 상한의 1.5배 초과 시 즉시 abort + 에러 응답 (E-LLM-005).

---

## 3. 세션당 (per-session) 상한

| 모드 | Discovery | Quick |
|---|---|---|
| standard | $0.030 | $0.020 |
| cost_saving | $0.015 | $0.010 |

세션 누적은 `agent_io_logs` WHERE session_id GROUP BY user_id 집계.

세션 상한 도달 시:
- 진행 중 단계는 완료
- 다음 agent 호출 차단 (E-RL-002 응답)
- 사용자 메시지: "이번 세션 비용 한도에 도달했어요. 다음 영상부터 다시 사용 가능합니다."

---

## 4. 일일 사용자당 상한 (free tier)

```
무료 사용자: 일 $0.10 (대략 3~5세션)
유료 사용자: Phase 11+에서 정의
```

일 누적 cost는 KST 자정 리셋. 도달 시:
1. 즉시 cost_saving 모드로 강등
2. cost_saving에서도 초과 시 다음날까지 차단 (E-RL-002 + user_message)
3. 사용자에게 "오늘 사용량 한도 도달" + 다음날 가용 시점 안내

→ `docs/contracts/rate_limit_policy.md` rate-limit 응답과 정합.

---

## 5. 모델 선택 정책

기본:
- **gpt-4o-mini**: Intent, Planning, Rewriter, Memory Extractor, Knowledge Evaluator
- **gpt-4o**: Critic만 (정확도 중요)

cost_saving 모드에서는 Critic도 gpt-4o-mini로 폴백 (Critic agent §6).

모델 변경 시 절차:
1. prompt_registry semver bump
2. 1주일 A/B (50:50)
3. golden_set 회귀 평가 통과
4. 전환

---

## 6. 토큰 압축 전략

| 기법 | 적용 위치 | 효과 |
|---|---|---|
| System prompt 캐싱 | Anthropic/OpenAI cache 지원 시 | 입력 토큰 -50~80% |
| Brand Memory 요약 | 5개 필드 → 핵심 3개 (cost_saving 모드) | 입력 토큰 -20% |
| RAG chunk 길이 제한 | 1 chunk 500 토큰 이내 | 입력 토큰 -30% |
| history 압축 | 이전 turn 요약 (Quick 재진입) | 입력 토큰 -40% |

기법 적용 시 `agent_io_logs.metadata`에 적용 기법 기록.

---

## 7. 비용 초과 시 처리

```
호출 전 예측:
  expected_cost = input_tokens × input_rate + max_tokens × output_rate
  if (session_cumulative + expected_cost) > session_limit:
    block + E-RL-002 응답

호출 후 측정:
  actual_cost = input_tokens × input_rate + output_tokens × output_rate
  agent_io_logs.cost_usd = actual_cost
  if actual_cost > per_call_limit × 1.5:
    log warning, 다음 단계는 cost_saving 강제

세션 누적:
  매 호출 후 SUM(cost_usd) WHERE session_id, 한도 비교
```

---

## 8. cost-review Skill 연동

`.claude/skills/cost-review/SKILL.md`가 정기적으로:
- agent_io_logs에서 일/주/월 cost 집계
- prompt_id별 cost 분포
- 사용자별 상한 위반 사례
- 모델별 cost 분포 (gpt-4o vs mini)
- 결과를 `eval/cost_snapshots/{date}.md`에 적재

비용 폭증 의심 시 `cost-review` Skill 호출 권장.

---

## 9. 의존성

- `docs/contracts/agent_io_contract.md` §9 (호출당 상한)
- `docs/contracts/rate_limit_policy.md` (사용자/IP rate limit)
- `agent_io_logs` 테이블 (cost_usd, input_tokens, output_tokens)
- `eval/cost_snapshots/` (스냅샷 저장)
- `cost-review` Skill (운영 점검)

---

## 10. Open Questions

1. 무료 사용자 일 $0.10 적정성 — 평균 사용 패턴 누적 후 재조정.
2. cost_saving 모드 진입 시 사용자 UX(현재 무음 강등) — 명시 안내 옵션.
3. Critic gpt-4o → mini 폴백 시 품질 저하 정량(현재 미측정).
4. system prompt 캐싱이 모델 변경 시 깨지는 문제 (Phase 11+ 검토).
5. 유료 tier 가격 책정 (Phase 11+).

---

## 11. LLM Gateway — tier×mode → alias → model 표 (Phase 11 A안, ★ additive)

> 추가: 2026-06-01 (contract-change **CC-010**, Phase 11 A안 LLM Gateway)
> 근거: 제안서 `meta/proposals/2026-05-31_llm-gateway-design.md` §6 / §18.A·§18.D, ADR-039
> ★ **additive / behavior-preserving**: §1~§10(기존 user tier 무료/유료 + 호출당/세션당/일일 상한 + cost_saving Critic 폴백)은 **전부 보존**. 본 절은 §5 "모델 선택 정책"을 LLM Gateway alias 표로 **선언적 정식화**한 것(로직 분산 해소). 현 동작과 동일 해석.

### 11.1 alias 개념

agent 는 concrete 모델명이 아니라 **alias(논리명)**만 참조하고, LLM Gateway(`backend/fastapi/llm/`)가 **tier × mode** 를 입력으로 alias → registry key → concrete model_id 를 해석한다. → provider/모델 교체 시 agent 코드 0 변경(ADR-039).

- **tier**: 기존 §4 user tier(`free` 무료 / `paid` 유료). A안에서는 모델 분기에 미사용(B안 premium mode 도입 시 확장 — 제안서 §6 후속). 시그니처는 미리 수용.
- **mode**: 기존 §1·§5 cost mode(`standard` / `cost_saving`). Critic alias 만 분기.

### 11.2 tier×mode → alias → model 표 (제안서 §6 / §18.A)

| tier × mode | planning / intent / rewriter / memory | critic | cross_validation (신규, gated) |
|---|---|---|---|
| free × standard | gpt-4o-mini | **gpt-4o** | ❌ off (default) / ⚪ flag opt-in |
| free × cost_saving | gpt-4o-mini | **gpt-4o-mini** | ❌ off (default) / ⚪ flag opt-in |
| paid × standard | gpt-4o-mini | **gpt-4o** | ❌ off (default) / ⚪ flag opt-in |
| paid × premium (신규, **후속 B안**) | gpt-4o-mini | gpt-4o | ✅ 1회 교차검증 (제안서 §18.B) |

- ★ **현 동작 보존**: `free × standard` = 현 default(§5 — workhorse gpt-4o-mini + Critic gpt-4o). `cost_saving` = 현 Critic gpt-4o→gpt-4o-mini 폴백(§5 마지막 줄)을 alias 로 정식화 — **byte-identical** 해석(gateway.resolve_model 단위 test 강제).
- alias→registry: `planning/intent/rewriter/memory → gpt-4o-mini`, `critic → {standard: gpt-4o, cost_saving: gpt-4o-mini}`, `cross_validation → gemini-cross`(model_id = config `cross_validation_model`).
- "premium" mode + premium_review(flagship) 활성은 **후속 B안**(제안서 §7·§18.B) — A안 미구현. ★ Opus/GPT flagship 기본 호출 0.

## 12. cross_validation 비용 (Gemini 1회, ★ gated default-off)

> 추가: 2026-06-01 (CC-010, Phase 11 A안 Slice 2·3)

A안의 cross_validation 은 표준 Critic(OpenAI gpt-4o) 평가 후 **다른 family(Gemini) 1회 교차검증 pass**(Critic 의 추가 pass — MOA 4 agent 불변). single-model self-bias 완화용.

### 12.1 게이트 (★ 필수)
- config `cross_validation_enabled` default **False** → orchestrator hook 미발화 → **비용 증가 0**(기존 흐름 100% 동일).
- 활성 = 명시적 flag(`CROSS_VALIDATION_ENABLED=true`) + GOOGLE 키 opt-in. 키 없으면 graceful skip(비용 0).
- 모델: `gemini-cross`(default `cross_validation_model=gemini-3.5-flash`). ★ Gemini 가 동급 최저가(제안서 §18.0).

### 12.2 호출당 상한 (cross_validation 활성 시 — additive 권고)

| Alias / Pass | model | 상한/호출 |
|---|---|---|
| cross_validation (Gemini, gated) | gemini-cross (gemini-3.5-flash 등) | $0.002 (1.5×: $0.003 abort) |

- cross_validation_enabled=True 시, plan 생성당 **Gemini 1회분**(약 $0.002 추정 — registry cost input 0.002 / output 0.012 per-1M, max_tokens 1500)을 §2 호출당 / §3 세션당 상한에 **additive 반영 권고**(제안서 §18.D). recommended plan 1개에만 적용(전 3안 아님) → 세션당 +1회.
- ★ default OFF 면 본 비용 미발생. 활성 시 cost-review Skill(§8)로 Gemini 호출 분포 점검 권장.

### 12.3 B안 cost 재조정 (후속 — ★ 보관)
- B안(3-provider 다양성, 제안서 §18.B)은 신모델이 gpt-4o-mini 대비 **5~7배** → §2 호출당 / §3 세션당 상한 **전면 재조정 필수**(별도 contract-change). 본 CC-010 은 A안 cross_validation 1회분 additive 까지만.
