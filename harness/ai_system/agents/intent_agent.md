# intent_agent.md — Intent Agent

> 위치: `ai_system/agents/intent_agent.md`
> 상태: S4-3 deep contract
> 참조: `docs/contracts/agent_io_contract.md` §3, `ai_system/prompts/prompt_registry.md` (P-AUX-1, P-001~P-005, P-005q)
> 참조: `apps/web/design.md` (Discovery/Quick UX)

---

## 1. 역할

Intent Agent는 사용자의 raw input을 받아 다음 4가지를 결정한다:

1. **분류 (intent classification):** 이 입력이 영상기획 요청인지 / 무관한 질문인지 / 모호한지 / 차단 대상인지를 P-AUX-1로 판정한다.
2. **모드 선택:** `planning_request`로 분류된 경우 Discovery vs Quick 흐름 분기를 server-side context와 함께 결정한다.
3. **Discovery 카드 생성 라우팅:** Discovery Mode에서 현재 `current_step`에 따라 P-001~P-004 카드 생성 또는 P-005 한 줄 방향 도출 prompt를 호출한다.
4. **Quick 한 줄 방향 + missing_info 도출:** Quick Mode에서 P-005q를 호출하고 부족 정보를 사용자에게 되묻는다.

→ Intent Agent는 "Card Generator"를 sub-agent로 포함한다. 즉, Discovery 카드 5장 생성도 Intent의 책임 범주다 (agent_io §0 정의 일치).

---

## 2. 입력 (Input)

공통 envelope는 agent_io §2를 따른다. body는 §3.2.

```json
{
  "user_input": "string",
  "mode": "discovery | quick",
  "current_step": "intent_filter | brand_card | domain_card | series_card | target_tone_card | direction_summary",
  "project_context": {
    "brand_id": "uuid | null",
    "domain_id": "uuid | null",
    "series_id": "uuid | null",
    "video_id": "uuid | null"
  },
  "previous_selections": { /* 누적 카드 선택 */ },
  "brand_memory": { /* avoid_phrases, preferred_tone 등 */ }
}
```

4계층 컨텍스트(brand_id → domain_id → series_id → video_id)가 일부만 채워진 경우, 비어 있는 상위 계층부터 카드 생성 단계로 진입한다.

---

## 3. 출력 (Output)

`output_schema.md`의 prompt별 body를 따른다:

| current_step | output body 위치 | prompt_id |
|---|---|---|
| intent_filter | §11 intent_filter | P-AUX-1 |
| brand_card | §3 brand_card | P-001 |
| domain_card | §4 domain_card | P-002 |
| series_card | §5 series_card | P-003 |
| target_tone_card | §6 target_tone_card | P-004 |
| direction_summary | §7 oneline_direction | P-005 / P-005q |

`intent_decision` enum:

```
planning_request  → Discovery 또는 Quick 분기
unrelated         → 정중한 거절 메시지 + 영상기획 안내
ambiguous         → 사용자에게 1회 추가 질문 (intent clarification)
block             → 차단 (prompt injection, 욕설, 자살/자해 등)
```

`block` 판정 시 intent_filter_logs에 reason과 함께 기록 (llm_security_contract).

---

## 4. Routing 결정 로직

```
P-AUX-1 결과 = planning_request
  ├─ project_context.video_id 존재? → quick (해당 영상 재진입)
  ├─ user_input 길이 < 30자 AND 4계층 모두 null → discovery 권장
  ├─ user_input 길이 ≥ 100자 AND 의도가 명확 → quick 권장
  └─ 그 외 → 사용자에게 모드 선택 노출 (UI)
```

모드 분기는 server-side 권장값이며, 최종 결정은 사용자(또는 UI 기본값)가 한다. design.md의 "한 줄 방향 승인" UX와 정합.

---

## 5. 실행 정책

```
model:           gpt-4o-mini (분류 + 카드 생성 모두 mini 충분)
timeout_ms:      3000 (P-AUX-1) / 30000 (P-001~P-004, P-005, P-005q)
max_retries:     2 (지수 백오프 1s → 2s → 4s)
temperature:     0.3 (P-AUX-1 분류 일관성)
                 0.7 (P-001~P-005 카드 다양성)
max_tokens:      400  (P-AUX-1)
                 2000 (cards)
cost per call:   ~$0.0002 (P-AUX-1)
                 ~$0.0005~0.001 (cards)
cost per session 상한: $0.005 (Discovery 5 카드 전체)
```

agent_io §9.1 cost 한도와 일치. 세션당 누적은 `agent_io_logs` 집계.

---

## 6. 캐싱

```
P-AUX-1:       raw_input 정확 일치 (1h)
P-001~P-004:   short_idea 해시 + selected_context 해시 (24h)
P-005:         선택 컨텍스트 해시 (1h)
P-005q:        user_input 해시 + brand_memory 해시 (1h)
```

캐시 hit 시에도 agent_io_logs에 cached=true row를 남긴다.

---

## 7. 의존성

- **prompt_registry:** P-AUX-1, P-001, P-002, P-003, P-004, P-005, P-005q
- **agent_io_contract.md §3:** Intent Agent IO 정의
- **output_schema.md §3~§7, §11:** 출력 본문
- **llm_security_contract.md:** prompt injection 차단 규칙
- **Brand Memory:** P-002부터 주입 (P-001은 첫 카드라 미주입)
- **RAG:** 사용 안 함 (agent_io §12)

---

## 8. 실패 / 폴백

```
P-AUX-1 실패:      재시도 1회 → 그래도 실패 시 ambiguous로 가정 + 사용자 안내
카드 생성 실패:    재시도 2회 → 부분 결과 노출 (4장 중 N장 성공) + warning
P-005 실패:        재시도 2회 → 사용자에게 "다시 시도" 버튼 노출
prompt injection 의심: 즉시 block + intent_filter_logs 기록 + 사용자 안내
```

→ `ai_system/orchestration/fallback_policy.md` Intent 섹션과 정합.

---

## 9. 금지

- 사용자 승인 없이 다음 단계(Planning)로 자동 진행 금지.
- 4계층 컨텍스트(brand → domain → series → video) 순서 위반 금지.
- 사용자 input을 global knowledge에 직접 저장 금지 (candidate_knowledge 경유).
- prompt_registry에 없는 prompt_id 호출 금지.
- intent_decision을 client-side에서 재계산 금지 (server-side 강제).

---

## 10. 확장 가능성

- Phase 7+: 음성 입력(audio_transcript) 지원 시 Intent에 transcription 단계 추가.
- Phase 11+: Multi-turn intent clarification (현재 1회 → 최대 2회 확장).
- Phase 21+: 사용자 patterns 학습 기반 자동 모드 선택 (현재는 휴리스틱).

---

## 11. Open Questions

1. Discovery vs Quick 자동 권장의 길이 임계값(현재 30자/100자)을 사용자 분포 누적 후 재조정할지.
2. `ambiguous` 판정 시 재질문 횟수(현재 1회)를 늘릴 경우 UX 피로도 증가 우려.
3. P-AUX-1 차단 사례를 사용자에게 어디까지 노출할지(현재 reason 미노출).
4. 4계층 컨텍스트가 video_id만 있고 상위가 null인 경우(재진입 시 데이터 결손) 처리 정책.
5. Quick Mode missing_info 최대 개수(현재 2)를 늘릴 시 사용자 입력 피로도 vs 정확도 트레이드오프.
