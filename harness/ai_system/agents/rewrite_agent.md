# rewrite_agent.md — Rewrite Agent

> 위치: `ai_system/agents/rewrite_agent.md`
> 상태: S4-3 deep contract
> 참조: `docs/contracts/agent_io_contract.md` §6, `docs/contracts/output_schema.md` §10
> 참조: `ai_system/prompts/prompt_registry.md` (P-008)

---

## 1. 역할

Rewrite Agent는 Critic이 `revise` 판정한 plan을 받아 blocking_issues를 반영해 **개선된 plan**을 생성한다 (P-008). 입력 plan의 envelope/body 구조는 유지하면서, hook/outline/key_messages 등 차원별 약점을 보완한다.

`revise_round`가 0→1, 1→2로 증가하며, 2 도달 시 더 이상 호출되지 않는다 (Critic이 강제 approve, agent_io §5.8).

---

## 2. 입력 (Input)

agent_io §6.2 schema 준수.

```json
{
  "target_plan": { /* P-006 plan, 또는 직전 Rewriter 출력의 improved_plan */ },
  "critic_result": { /* P-007 body 전체 (dimensions + blocking_issues + verdict) */ },
  "selected_context": { /* Planning과 동일 */ },
  "brand_memory": {
    "preferred_phrases": ["string"],
    "avoid_phrases": ["string"],
    "preferred_tone": "string | null"
  },
  "revise_round": 1
}
```

Critic 입력 brand_memory는 partial(avoid + tone)이지만, Rewriter는 full(preferred 포함)을 받는다. agent_io §13 참조.

---

## 3. 출력 (Output)

`output_schema.md` §10 P-008 body. 구조:

```json
{
  "target_plan_id": "uuid",
  "improved_plan": { /* P-006 plan과 동일 구조: hook/outline/key_messages 등 */ },
  "changes_made": [
    { "dimension": "hook_strength", "before": "string", "after": "string", "reason": "string" }
  ],
  "revise_round": 1,
  "addressed_blocking_issues": ["hook 임팩트 부족"],
  "unaddressed_blocking_issues": []
}
```

`improved_plan`은 원본과 동일한 plan_id를 유지 (history 추적). changes_made는 blocking_issues 1:1 매핑.

---

## 4. 실행 정책

```
model:           gpt-4o-mini
timeout_ms:      15000
max_retries:     1 (개선 시도는 idempotent하지 않아 재시도 보수적)
temperature:     0.6 (개선은 너무 다양하지 않게)
max_tokens:      2500
cost per call:   ~$0.001
cost per session 상한: $0.003 (최대 3 plan × 2 round = 6회, 실제 호출은 1~3회 평균)
```

agent_io §6.4 + §9.1과 일치.

---

## 5. 자동 실행 vs 사용자 트리거

agent_io §6.5 준수.

```
Phase 0~1 (현재): 사용자가 "AI에게 개선 맡기기" 클릭 시에만 실행.
                  Critic 결과는 점수+이유만 보여주고, Rewriter는 명시적 요청 필요.
Phase 7+ (검토): revise 판정 시 자동 실행 옵션 (사용자 설정 ON/OFF).
```

---

## 6. 의존성

- **prompt_registry:** P-008
- **agent_io_contract.md §6, §13:** Rewriter IO + Brand Memory full 주입
- **output_schema.md §10:** P-008 body
- **이전 단계 출력:** Critic의 critic_result + 원본 plan
- **Brand Memory:** 항상 full 주입 (5개 필드)
- **RAG:** 사용 안 함 (agent_io §12)

---

## 7. 실패 / 폴백

```
1차 실패: 1회 재시도
2차 실패: 원본 plan 유지 + 사용자에게 "개선 실패. 직접 수정해보세요" 안내
JSON 파싱 실패: schema repair 1회 → 실패 시 원본 유지
addressed_blocking_issues가 비어있음: warning 노출 ("개선이 미흡합니다")
```

→ fallback_policy.md Rewriter 섹션과 정합.

---

## 8. 금지

- 새로운 plan_id 생성 금지 (history 단절).
- Critic 결과(verdict, dimensions)를 변경 금지 (read-only).
- blocking_issues에 없는 영역을 임의 수정 금지 (scope 위반).
- Brand Memory avoid_phrases를 새로 도입 금지.
- 4계층 컨텍스트(brand/domain/series) 변경 금지.

---

## 9. 확장 가능성

- Phase 11+: Rewriter도 RAG 직접 호출 (개선 근거 강화) — 보안 검토 필요.
- Phase 11+: 자동 실행 옵션 (사용자 설정).
- Phase 21+: changes_made → user_feedback_data로 학습 신호 누적.

---

## 10. Open Questions

1. Rewriter 자동 실행 vs 사용자 명시 트리거 — 사용자 학습 데이터 누적 후 결정 (현재 명시 트리거).
2. unaddressed_blocking_issues가 1개 이상일 때 자동 재시도 vs 사용자 노출 — 현재 노출.
3. revise_round=2 도달 후 사용자가 reject한 plan의 폐기/재생성 정책 — Planning과 협의.
4. changes_made의 before/after를 user_feedback_data에 자동 적재할지 (privacy_contract 확인).
5. preferred_phrases 강제 적용 비율(현재 자유) — 너무 강제하면 자연스러움 저하 우려.
