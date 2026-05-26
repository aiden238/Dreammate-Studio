# critic_agent.md — Critic Agent

> 위치: `ai_system/agents/critic_agent.md`
> 상태: S4-3 deep contract
> 참조: `docs/contracts/agent_io_contract.md` §5, `docs/contracts/output_schema.md` §9
> 참조: `docs/contracts/error_response_contract.md` (E-LLM-010 한계)
> 참조: `ai_system/prompts/prompt_registry.md` (P-007)
> 참조: `eval/video_planning_eval.md` (8 차원 정의)

---

## 1. 역할

Critic Agent는 Planning Agent가 생성한 plan 1개를 **8 차원으로 채점**하고 verdict(approve/revise/reject)를 내리는 평가 agent다. 3개 plan에 대해 병렬로 3회 호출된다 (agent_io §5.7).

revise 판정 시 blocking_issues를 도출해 Rewrite Agent로 넘긴다. revise_round는 server-side가 관리하며 2 도달 시 강제 approve로 승격된다 (agent_io §5.8).

---

## 2. 입력 (Input)

agent_io §5.2 schema 준수.

```json
{
  "target_plan": { /* P-006 plan 1개 그대로 */ },
  "target_plan_id": "uuid",
  "approved_direction": "string",
  "selected_context": { /* Planning과 동일 */ },
  "brand_memory": {
    "avoid_phrases": ["string"],
    "preferred_tone": "string | null"
  },
  "revise_round": 0
}
```

`revise_round`는 server-side 카운터의 echo. Critic은 항상 입력 그대로 출력에 반환 (idempotency).

---

## 3. 8 차원 채점

각 차원 0~5점. 4점 이상이면 해당 차원 pass.

| # | dimension | 정의 | 가중 |
|---|---|---|---|
| 1 | intent_fit | approved_direction과 plan의 일치도 | 1.0 |
| 2 | target_clarity | 타겟 페르소나 명확도 | 1.0 |
| 3 | hook_strength | 첫 3초 hook의 임팩트 | 1.2 |
| 4 | message_clarity | 핵심 메시지 1개 이상 명확 | 1.0 |
| 5 | structure | outline 흐름 (hook → body → CTA) | 1.0 |
| 6 | feasibility | 30초 내 실행 가능성 | 0.8 |
| 7 | brand_consistency | Brand Memory avoid_phrases 위반 없음, preferred_tone 부합 | 1.2 |
| 8 | differentiation | 동일 batch의 다른 2 plan과의 차별 | 0.8 |

가중 합계 / 가중 총합 = overall_score (0~5 normalized).

→ 자세한 rubric은 `eval/video_planning_eval.md` 참조.

---

## 4. Verdict 결정

```
overall_score ≥ 4.0 AND blocking_issues.length == 0  → approve
overall_score < 4.0 AND revise_round < 2              → revise
overall_score < 2.0                                    → reject
revise_round = 2 도달 시 verdict가 revise            → 강제 approve (E-LLM-010 한계 처리)
                                                      → validation.warnings에 "forced_approve_after_max_revise"
                                                      → 사용자 안내 노출
```

blocking_issues는 차원별 점수가 2 미만일 때 자동 생성.

---

## 5. 출력 (Output)

`output_schema.md` §9 P-007 body. 핵심:

```json
{
  "target_plan_id": "uuid",
  "dimensions": {
    "intent_fit": { "score": 4, "reason": "string" },
    "target_clarity": { "score": 5, "reason": "string" },
    "hook_strength": { "score": 3, "reason": "string" },
    "message_clarity": { "score": 4, "reason": "string" },
    "structure": { "score": 4, "reason": "string" },
    "feasibility": { "score": 5, "reason": "string" },
    "brand_consistency": { "score": 4, "reason": "string" },
    "differentiation": { "score": 3, "reason": "string" }
  },
  "overall_score": 3.95,
  "verdict": "revise",
  "blocking_issues": ["hook 임팩트 부족", "타 plan과 hook 첫 3단어 중복"],
  "revise_round": 0
}
```

---

## 6. 실행 정책

```
model:           gpt-4o (정확도 중요. mini 폴백은 cost_saving 모드에서만)
timeout_ms:      20000
max_retries:     2 (지수 백오프 1s → 2s)
temperature:     0.3 (평가 일관성)
max_tokens:      1500
cost per call:   ~$0.005 (gpt-4o) / ~$0.001 (mini 폴백) / ~$0.02 (상한)
cost per session: 3 × $0.005 = $0.015 (gpt-4o)
                  3 × $0.001 = $0.003 (mini)
```

agent_io §5.4 + §9.1과 일치.

---

## 7. 병렬 호출 정책

agent_io §5.7 준수.

```
Planning이 plans[3] 반환 → Critic × 3 병렬 호출 (Promise.all)
1개 실패 → 나머지 2개는 그대로 진행 (격리)
실패한 1개 → 재시도 1회 → 그래도 실패 시 verdict 없이 사용자 노출 + "검토 불가" warning
```

---

## 8. revise 무한 루프 차단 (재확인)

agent_io §5.8 일치. server-side가 revise_round를 증가시키며, 2 도달 시:
- verdict를 강제로 approve로 변경
- validation.warnings에 `forced_approve_after_max_revise` 기록
- 사용자에게 "AI 개선이 한계에 도달했어요. 직접 다듬어보시겠어요?" 노출
- 사용자가 reject 선택 시 plan 폐기 + 새로운 plan 1개 재생성 옵션

이 정책은 클라이언트에서 우회할 수 없도록 backend가 강제한다.

---

## 9. 의존성

- **prompt_registry:** P-007
- **agent_io_contract.md §5, §13:** Critic IO + Brand Memory partial 주입
- **output_schema.md §9:** P-007 body
- **error_response_contract.md:** E-LLM-010 (revise 한계)
- **eval/video_planning_eval.md:** 8 차원 rubric 정의
- **Brand Memory:** partial (avoid_phrases, preferred_tone만)
- **RAG:** 사용 안 함 (agent_io §12)

---

## 10. 실패 / 폴백

```
1차 실패: 1회 재시도
2차 실패: 해당 plan에 verdict 없이 노출 + "검토 불가" warning
3개 모두 실패: 자동 approve 가정 (fallback_policy.md Critic 섹션)
                + 사용자에게 "AI 검토 실패. 직접 선택해주세요" 안내
cost_saving 모드: gpt-4o → gpt-4o-mini 폴백
```

→ fallback_policy.md Critic 섹션과 정합.

---

## 11. 금지

- Critic이 plan 본문을 직접 수정 금지 (Rewriter 책임).
- 8 차원 외 새로운 차원 추가 금지 (eval/video_planning_eval과 동기 필요).
- revise_round를 client에서 변경 금지 (server-side 강제).
- RAG 호출 금지 (agent_io §12).
- Brand Memory의 preferred_phrases / success_patterns 사용 금지 (Rewriter용).

---

## 12. 확장 가능성

- Phase 11+: Multi-agent voting (Critic 3 모델 병렬 → 평균 verdict).
- Phase 21+: Critic에 RAG 직접 호출 권한 부여 (검증 보강) — 보안 검토 필요.
- Phase 21+: 8 차원 가중치 사용자 데이터로 동적 조정.

---

## 13. Open Questions

1. Critic gpt-4o 고정 vs cost_saving 임계(현재 일 $0.10)에서 mini 폴백 — 품질 저하 측정 필요.
2. 8 차원 가중치 균일(1.0) vs 핵심 4개(hook/brand/intent/target) 가중(1.2) — 현재 후자.
3. revise_round=2 강제 approve 시 사용자 안내 톤(현재 친근체) — copy 검토.
4. 3개 plan 중 1개 Critic 실패 시 부분 노출 vs 자동 재생성(현재 부분 노출).
5. differentiation 차원을 Critic이 채점 vs 별도 후처리 단계로 분리(현재 Critic 내포).
