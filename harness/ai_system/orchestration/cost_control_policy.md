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
