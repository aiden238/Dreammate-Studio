# flow.md — 영상기획 AI 에이전트 전체 흐름

> 위치: `ai_system/orchestration/flow.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/agent_io_contract.md` §8, `docs/contracts/output_schema.md`, `docs/contracts/api_contract.md` §13
> 참조: `ai_system/orchestration/moa_policy.md`, `fallback_policy.md`, `cost_control_policy.md`
> 명명: 모든 agent 명명은 MOA Lite 표준(Intent / Planning / Critic / Rewriter)

---

## 1. 전체 흐름도

```
사용자 입력
   │
   ▼
[1] Intent Agent (P-AUX-1)               ── intent_filter: planning_request | unrelated | ambiguous | block
   │
   ├─ unrelated / block → 거절 응답 + intent_filter_logs 기록 → 종료
   ├─ ambiguous          → 사용자에게 추가 질문 (1회)
   └─ planning_request  → 모드 분기
                          │
              ┌───────────┴────────────┐
              ▼                        ▼
         Discovery Mode            Quick Mode
              │                        │
[2a] Intent (P-001 brand_card)     [2b] Intent (P-005q)
[2a] Intent (P-002 domain_card)         + missing_info 보완 (최대 1~2회)
[2a] Intent (P-003 series_card)         │
[2a] Intent (P-004 target_tone)         │
[2a] Intent (P-005 direction_summary)   │
              │                        │
              └────────────┬───────────┘
                           ▼
                  사용자: 한 줄 방향 승인
                           │
                           ▼
[3] RAG Retrieval (Planning 한정)        ── top_k=5 → sim≥0.7 → 최대 3 채택
                           │
                           ▼
[4] Planning Agent (P-006)               ── 3 plan_candidates 생성
                           │
                           ▼
[5] Critic Agent × 3 병렬 (P-007)        ── 8 차원 채점 + verdict
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          approve       revise        reject
              │            │            │
              │            ▼            │
              │   [6] Rewriter (P-008)  │
              │    revise_round 0→1     │
              │            │            │
              │            ▼            │
              │       Critic 재평가     │
              │   (max revise_round=2)  │
              │            │            │
              └────────────┴────────────┘
                           ▼
                  사용자: plan 선택 (/select)
                           │
                           ▼
[7] Save: video_projects + plan_options
                           │
                           ▼
[8] Memory Extractor (P-AUX-2) [백그라운드]
                           │
                           ▼
                 Brand Memory 업데이트
```

---

## 2. 단계별 entry / exit condition

| # | Step | Entry | Exit |
|---|---|---|---|
| 1 | Intent (P-AUX-1) | user_input 수신 | intent_decision 반환 |
| 2a | Discovery cards (P-001~P-005) | planning_request 분류 + discovery mode | direction_summary 도출 |
| 2b | Quick (P-005q) | planning_request + quick mode | one_line + missing_info=[] |
| - | 사용자 한 줄 승인 | direction_summary 노출 | 사용자 클릭 (/approve) |
| 3 | RAG retrieval | approved_direction 확정 | rag_context 또는 [] + warning |
| 4 | Planning (P-006) | rag_context 확보 | plans[3] 생성 |
| 5 | Critic × 3 (P-007) | plans[3] 수신 | verdicts[3] |
| 6 | Rewriter (P-008) | verdict=revise + 사용자 트리거 | improved_plan |
| - | revise 루프 | revise_round 0→1→2 | revise_round=2 도달 시 강제 approve |
| - | 사용자 plan 선택 | verdicts 노출 | /select 호출 |
| 7 | Save | /select 수신 | video_projects.status='selected' |
| 8 | Memory Extractor (P-AUX-2) | status='final' 전이 [백그라운드] | brand_memory_entries 자동 INSERT (조건부) |

---

## 3. Discovery vs Quick 분기 결정

```
intent_decision = planning_request 일 때:
  1. project_context.video_id 존재? → quick (재진입)
  2. user_input 길이 < 30자 AND 4계층 모두 null → discovery 권장
  3. user_input 길이 ≥ 100자 AND 의도 명확 → quick 권장
  4. 그 외 → UI에서 사용자 선택 (Discovery 기본)
```

→ Intent Agent §4 routing 결정 로직과 일치.

---

## 4. 무한 루프 차단

| 루프 위치 | 차단 규칙 |
|---|---|
| Intent ambiguous 재질문 | 최대 1회 (2회 도달 시 block 처리) |
| Quick missing_info 보완 | 최대 2개 missing_info, 사용자 입력 2회 한정 |
| Critic revise | revise_round 0→1→2, 2 도달 시 강제 approve |
| Planning 재시도 | max_retries=1 (cost 큼) |
| Rewriter 재시도 | max_retries=1 |

server-side가 모든 카운터를 관리하며, client는 영향 불가 (agent_io §5.8).

---

## 5. 4단계 Progress Stepper 매핑

apps/web/design.md UX와 정합:

| Stepper | 표시 텍스트 | 백엔드 단계 |
|---|---|---|
| 1 / 4 | "의도 분석 중" | Intent (P-AUX-1 + 카드 생성) |
| 2 / 4 | "참고 자료 찾는 중" | RAG retrieval |
| 3 / 4 | "기획안 만드는 중" | Planning (P-006) |
| 4 / 4 | "품질 검토 중" | Critic × 3 |

Rewriter는 사용자 명시 트리거이므로 stepper에 포함 안 함 (별도 micro-spinner).

---

## 6. SSE 이벤트 발행 시점

api_contract §13 SSE 명세 준수. 발행 시점:

```
event: intent_started        → P-AUX-1 호출 시점
event: intent_completed      → intent_decision 반환 직후
event: cards_card_emitted    → 카드 1장 생성 완료 시 (P-001~P-004, 카드별 1회)
event: direction_summary     → P-005/P-005q 완료
event: rag_retrieved         → RAG 결과 확정
event: planning_started      → P-006 호출
event: planning_plan_emitted → plan 1개 완성 시 (3회 발행)
event: critic_started        → Critic × 3 호출
event: critic_result         → 각 Critic 완료 (3회)
event: rewriter_started      → 사용자 트리거 시
event: rewriter_completed    → improved_plan 완성
event: session_completed     → /select 완료
event: error                  → 단계별 실패 시
```

Heartbeat: 5초 주기 `event: ping`.

---

## 7. agent_io_logs 기록 정책

모든 agent 호출은 호출 직전 INSERT, 완료 시 UPDATE. agent_io §11.1 준수.

흐름과 무관하게 모든 단계가 동일 정책. 부분 실패도 row를 남긴다.

---

## 8. 비용 누적 체크

각 agent 호출 후 즉시 다음을 확인:
- 세션당 누적 cost vs cost_control_policy 상한
- 일일 사용자당 누적 cost vs free tier 상한
- 한도 초과 시 다음 agent 호출 차단 + E-RL-002 응답

→ `ai_system/orchestration/cost_control_policy.md` 참조.

---

## 9. 의존성

- agent_io_contract.md §8 (오케스트레이션 흐름)
- api_contract.md §13 (SSE 이벤트)
- output_schema.md (단계별 body)
- prompt_registry.md (P-001~P-008, P-AUX-1/2)
- moa_policy.md (4 agent 구조)
- fallback_policy.md (실패 처리)
- cost_control_policy.md (비용 한도)

---

## 10. Open Questions

1. RAG retrieval 단계를 Stepper에 별도 표시할지(현재 표시) vs Planning에 흡수할지.
2. Critic 재평가(revise_round 1, 2) 시 Stepper 진행률 표시 방법 — 현재 4/4 유지 + micro-spinner.
3. Memory Extractor 백그라운드 실행 실패를 사용자에게 알릴지(현재 무음).
4. SSE 연결 중단 시 client 재연결 정책(현재 last-event-id 기반 재개).
5. ambiguous 재질문 1회 한도 — 사용자 학습 데이터 누적 후 확대 검토.
