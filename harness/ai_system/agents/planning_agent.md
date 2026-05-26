# planning_agent.md — Planning Agent

> 위치: `ai_system/agents/planning_agent.md`
> 상태: S4-3 deep contract
> 참조: `docs/contracts/agent_io_contract.md` §4, `docs/contracts/output_schema.md` §8, `docs/contracts/rag_data_contract.md` §5
> 참조: `ai_system/prompts/prompt_registry.md` (P-006)
> 명명 참고: MOA Lite 4 agent 중 "Planning" (구 Planner). agent_io_contract Planner 표기는 동일 agent를 가리킨다.

---

## 1. 역할

Planning Agent는 승인된 한 줄 방향과 선택 컨텍스트, RAG 근거, Brand Memory를 받아 **3개 영상기획안(plan_candidates)**을 생성한다 (P-006). 3개의 approach가 명확히 달라야 한다 (구성/메시지/포맷 중 최소 1개 축에서 차별).

Discovery 5단계 카드 생성 자체는 Intent Agent의 책임이다. Planning Agent는 카드 결과를 사용자가 승인한 이후 단계만 담당한다.

---

## 2. 입력 (Input)

agent_io §4.2 schema 준수.

```json
{
  "approved_direction": "string (P-005의 one_line)",
  "direction_components": {
    "target": "string",
    "message": "string",
    "format": "string",
    "length_sec": 30
  },
  "selected_context": {
    "brand": { "name": "string", "description": "string", "tone": {} },
    "domain": { "name": "string", "description": "string" },
    "series": { "name": "string", "structure_type": "string", "cadence_hint": "string" },
    "target": { "name": "string", "pain_points": [] },
    "tone": { "name": "string", "example_sentences": [] }
  },
  "rag_context": [
    { "chunk_id": "uuid", "title": "string", "content": "string", "similarity": 0.0, "metadata": {} }
  ],
  "brand_memory": { /* preferred_phrases, avoid_phrases, success/rejection_patterns */ }
}
```

`rag_context`는 빈 배열일 수 있다 (RAG 검색 결과 0개). 빈 배열인 경우 validation.warnings에 "no_rag_reference" 기록.

---

## 3. 출력 (Output)

`output_schema.md` §8 P-006 body. 핵심 구조:

```json
{
  "plan_candidates": [
    {
      "plan_id": "uuid",
      "approach_label": "string (예: 공감-스토리, 즉시-혜택, 반전-훅)",
      "hook": "string",
      "outline": [ { "section": "string", "duration_sec": 5, "summary": "string" } ],
      "key_messages": ["string"],
      "rag_citations": ["chunk_id"]
    }
  ]
}
```

3개 plan은 `approach_label`이 서로 다르고, hook 첫 3단어가 겹치지 않아야 한다 (Critic이 검증).

---

## 4. Discovery vs Quick 분기

```
Discovery: approved_direction은 P-005(5단계 카드 누적) 결과
Quick:     approved_direction은 P-005q(짧은 입력 + missing_info 추가) 결과
```

Planning Agent 자체는 두 모드를 구분하지 않는다. envelope의 selected_context가 채워지는 출처만 다르며, 입력 schema는 동일하다 (agent_io §4.2).

---

## 5. RAG 검색 흐름 (Planning 한정)

agent_io §4.7 + rag_data_contract §5 준수.

```
1. 쿼리 생성: approved_direction + selected_series.name + selected_domain.name
2. top_k 검색: 5 chunk
3. similarity 필터: ≥ 0.7
4. 최대 채택: 3 chunk
5. 빈 결과 시: rag_context = [], validation.warnings += "no_rag_reference"
6. 검색 실패(DB error): Planning은 계속 진행 + warning + rag_context = []
```

RAG 사용 가능 layer: `approved_knowledge` (rag_data §3). `candidate_knowledge`는 직접 사용 금지.

---

## 6. 카드 5장 정책 (오해 방지)

카드 5장은 Discovery 단계(P-001~P-004) 산출물로, Intent Agent가 생성한다. AI 4장 + user_input_slot 1장 정책은 `apps/web/design.md`와 P-001~P-004 prompt에 정의되어 있다. Planning Agent는 5장 중 사용자가 선택한 결과(selected_*)만 입력으로 받는다.

---

## 7. 실행 정책

```
model:           gpt-4o-mini (P-006 토큰 큼, 비용 효율)
timeout_ms:      15000 (cards 단계는 Intent 책임)
                 30000 (plan_candidates P-006, 3 plan 동시 생성)
max_retries:     1 (LLM 호출 비용 큼, 2회 → 1회로 제한)
temperature:     0.85 (3 plan 다양성 최대화)
max_tokens:      3500
cost per call:   ~$0.002
cost per session 상한: $0.05 (재시도 포함, agent_io §9.2 Discovery 0.030 + 여유)
```

cost_saving 모드 진입 시 max_tokens를 2500으로 축소 (cost_control_policy 참조).

---

## 8. 캐싱

```
캐싱 금지 (다양성 우선).
단, 같은 request_id 재시도 시 캐시 활용 (idempotency 보장).
```

---

## 9. 의존성

- **prompt_registry:** P-006
- **agent_io_contract.md §4, §12:** Planning Agent IO + RAG 의존성
- **output_schema.md §8:** P-006 body
- **rag_data_contract.md §5:** retrieval 정책
- **Brand Memory:** 항상 주입 (5개 필드 full)
- **이전 단계 출력:** Intent의 approved_direction + selected_context

---

## 10. 실패 / 폴백

```
1차 실패 (5xx, timeout): 1회 재시도 (지수 백오프 2s)
2차 실패: 사용자에게 에러 노출 + "재시도" 버튼
부분 성공 (3개 중 N개): N개라도 노출 + "추가로 생성하기" 옵션
RAG 실패: rag_context=[] + warning + Planning 진행
JSON 파싱 실패: schema repair 1회 → 실패 시 전체 재시도 1회
```

→ fallback_policy.md Planning 섹션과 정합.

---

## 11. 금지

- 카드 생성(P-001~P-004) 직접 호출 금지 (Intent 책임).
- `candidate_knowledge`를 RAG 결과로 사용 금지 (approved만).
- 사용자 승인 없는 자동 다음 단계(Critic 자동 호출은 orchestrator 책임, Planning이 결정 안 함).
- 4계층 컨텍스트(brand → domain → series) 중 brand가 null인 채로 호출 금지.

---

## 12. 확장 가능성

- Phase 11+: SSE streaming으로 plan 1개씩 점진 노출.
- Phase 11+: cost_saving 모드에서 plan 3개 → 2개 축소 옵션.
- Phase 21+: Custom RAG 통합 시 rag_context의 chunk 출처가 자체 코퍼스로 확장.

---

## 13. Open Questions

1. P-006의 RAG 참고 자료를 최대 몇 chunk까지 주입할지 (현재 3개).
2. 3개 plan 중 1개라도 실패 시 자동 재생성 vs 부분 노출 (현재 부분 노출).
3. cost_saving 모드 진입 임계(현재 일 $0.10)에서 plan 3개 → 2개 축소 여부.
4. approach_label 다양성 강제 규칙(현재 first 3 words 비교)을 LLM 자가 검증 → Critic 검증으로 이관할지.
5. RAG 0건일 때 plan 품질 저하를 어떻게 측정/노출할지 (현재 warning만).
