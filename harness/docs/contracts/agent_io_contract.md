# agent_io_contract.md — 영상기획 AI 에이전트 IO Contract

> 위치: `docs/contracts/agent_io_contract.md`
> 상태: Phase 0–1 진입용 핵심 contract 초안
> 대상: MOA Lite 4 agent (Intent / Planning / Critic / Rewriter)
> 참조: `docs/contracts/output_schema.md` (출력 본문 스키마)
> 참조: `ai_system/prompts/prompt_registry.md` (P-001~P-008, P-AUX-1, P-AUX-2)
> 참조: `docs/contracts/db_schema.md` §7.1 `agent_io_logs`
> 참조: `ai_system/orchestration/cost_control_policy.md`, `fallback_policy.md`

---

## 0. 이 문서의 위치

`output_schema.md`는 **출력의 본문 구조**를 정의한다. 이 문서는 **agent 단위의 입력/출력/실행 정책**을 정의한다.

각 agent는 1개 이상의 prompt를 사용한다:

| Agent | 사용 Prompt | 호출 횟수/세션 |
|---|---|---|
| Intent | P-AUX-1, P-005, P-005q | 1~3 |
| Card Generator (sub of Intent) | P-001, P-002, P-003, P-004 | 1~4 (Discovery) |
| Planning | P-006 | 1 |
| Critic | P-007 | 3 (각 plan 1번) |
| Rewriter | P-008 | 0~3 |
| Memory Extractor | P-AUX-2 | 1 (세션 종료 시) |

여기서 "Intent agent"는 Discovery 단계의 카드 생성 prompt들도 묶어서 관리한다. UI/오케스트레이션 관점에서는 모두 "의도 분석/구체화" 단계이기 때문.

---

## 1. 설계 원칙

```
1. 모든 agent 호출은 idempotent하게 설계 (같은 input → 같은 output, 캐시 활용).
2. agent 간 의존은 명시적으로 declare. 직접 호출 금지, 오케스트레이터를 거친다.
3. 모든 호출은 agent_io_logs에 입력/출력 jsonb로 기록 (cost, latency 포함).
4. 시간 초과는 silent fail 금지. timeout 발생 → 에러 응답 + 부분 결과 노출.
5. Critic의 revise 권고는 server-side에서 round count로 관리. 최대 2회.
6. RAG 검색은 Planning에만 주입. Intent/Critic/Rewriter는 RAG 직접 의존하지 않음.
7. Brand Memory는 Planning, Rewriter, P-005에 항상 주입. Critic은 brand_consistency 검사에만 사용.
8. 비용 상한 도달 시 즉시 차단. 부분 결과는 사용자에게 노출.
```

---

## 2. 공통 입력 envelope

모든 agent 호출은 다음 envelope로 wrapping.

```json
{
  "request": {
    "request_id": "uuid",
    "user_id": "uuid",
    "video_id": "uuid | null",
    "session_id": "uuid",
    "trace_id": "string (분산 추적용)",
    "issued_at": "ISO8601"
  },
  "agent": "intent | planning | critic | rewriter | memory_extractor",
  "prompt_id": "P-006",
  "prompt_version": "v1.0.0",
  "input": { /* agent별 본문, 아래 §3~§7에서 정의 */ },
  "execution": {
    "model": "gpt-4o-mini",
    "timeout_ms": 30000,
    "max_retries": 2,
    "temperature": 0.7,
    "max_tokens": 2000,
    "stream": false
  }
}
```

공통 출력 envelope는 `output_schema.md` §2와 동일.

---

## 3. Intent Agent

### 3.1 책임

- 사용자의 raw input이 영상기획 관련인지 판정 (P-AUX-1)
- Discovery Mode에서 Brand/Domain/Series/Target/Tone 카드 생성 (P-001~P-004)
- Quick Mode에서 한 줄 방향 + missing_info 도출 (P-005q)
- Discovery 종료 시 한 줄 방향 도출 (P-005)

### 3.2 Input 스키마

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
  "previous_selections": {
    "selected_brand": { /* P-001의 card 1개 */ },
    "selected_domain": { /* P-002의 card 1개 */ },
    "selected_series": { /* P-003의 card 1개 */ },
    "selected_target": { /* P-004의 target_card 1개 */ },
    "selected_tone": { /* P-004의 tone_card 1개 */ }
  },
  "brand_memory": {
    "preferred_phrases": ["string"],
    "avoid_phrases": ["string"],
    "preferred_tone": "string | null",
    "success_patterns": ["string"],
    "rejection_patterns": ["string"]
  }
}
```

`current_step` 값에 따라 server-side에서 해당 prompt(P-AUX-1, P-001, P-002, P-003, P-004, P-005 또는 P-005q)를 라우팅.

### 3.3 Output 스키마

`output_schema.md`의 해당 prompt body 참조.

- intent_filter → §11
- brand_card → §3
- domain_card → §4
- series_card → §5
- target_tone_card → §6
- direction_summary → §7

### 3.4 실행 정책

```
model:           gpt-4o-mini (Intent는 단순 분류 + 생성이므로 mini 충분)
timeout:         30s
max_retries:     2 (지수 백오프 1s → 2s → 4s)
temperature:     0.7 (카드 다양성 위해)
                 0.3 (P-AUX-1만, 분류 일관성)
max_tokens:      2000
cost per call:   ~$0.0005
cost per session 상한: $0.005 (Discovery Mode 기준 4~5번 호출)
```

### 3.5 의존성

```
이전 단계 출력: previous_selections 안에 누적
RAG: 사용 안 함
Brand Memory: 단계 2(domain_card)부터 주입
prompt_registry P-ID: 위에 명시
```

### 3.6 캐싱

```
P-001~P-004: short_idea 해시 + selected_context 해시 (24h)
P-005:        선택 컨텍스트 해시 (1h)
P-AUX-1:      raw_input 정확 일치 (1h)
```

---

## 4. Planning Agent

### 4.1 책임

- 승인된 한 줄 방향 + 컨텍스트 + RAG로부터 3개 기획안 생성 (P-006)
- 3개의 approach가 서로 달라야 함

### 4.2 Input 스키마

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
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "title": "string",
      "content": "string",
      "similarity": 0.0,
      "metadata": {}
    }
  ],
  "brand_memory": {
    "preferred_phrases": ["string"],
    "avoid_phrases": ["string"],
    "success_patterns": ["string"],
    "rejection_patterns": ["string"]
  }
}
```

### 4.3 Output 스키마

`output_schema.md` §8 P-006 body.

### 4.4 실행 정책

```
model:           gpt-4o-mini (충분히 좋은 결과 + 비용 효율)
                 → P-006는 토큰 큼 (3 plan), 비용 변동 큼
timeout:         60s (3개 plan 동시 생성이라 길게)
max_retries:     2 (지수 백오프)
temperature:     0.85 (다양성 최대화)
max_tokens:      3500
cost per call:   ~$0.002
cost per session 상한: $0.003 (재시도 1회 포함)
```

### 4.5 의존성

```
이전 단계 출력: approved_direction, selected_context (Intent에서 전달)
RAG: rag_context로 주입 (최대 3 chunk, top-k 검색 → similarity ≥ 0.7만 채택)
Brand Memory: 항상 주입
prompt_registry P-ID: P-006
```

### 4.6 캐싱

```
캐싱 금지 (다양성 우선). 단 같은 request_id 재시도는 캐시 활용.
```

### 4.7 RAG 검색 정책 (Planning 한정)

```
- 검색 쿼리: approved_direction + selected_series.name + selected_domain.name
- top_k: 5 → similarity ≥ 0.7 필터 → 최대 3개 채택
- 빈 결과 시: rag_context = [], validation.warnings에 "no_rag_reference" 기록
- 검색 실패 (DB error): Planning는 계속 진행 + warning 노출
```

→ 자세한 RAG 정책은 `docs/contracts/rag_data_contract.md` 참조.

---

## 5. Critic Agent

### 5.1 책임

- 생성된 plan 1개에 대해 8차원 0~5점 평가 (P-007)
- approve / revise / reject 판정
- revise 시 blocking_issues 도출

### 5.2 Input 스키마

```json
{
  "target_plan": { /* P-006 plan 1개 그대로 */ },
  "target_plan_id": "uuid",
  "approved_direction": "string",
  "selected_context": { /* Planning와 동일 */ },
  "brand_memory": {
    "avoid_phrases": ["string"],
    "preferred_tone": "string | null"
  },
  "revise_round": 0
}
```

`revise_round`는 server-side가 관리. Critic은 항상 0 echo back.

### 5.3 Output 스키마

`output_schema.md` §9 P-007 body.

### 5.4 실행 정책

```
model:           gpt-4o (Critic은 평가 정확도가 중요해서 더 큰 모델 사용)
                 cost-control 모드에서는 gpt-4o-mini로 폴백
timeout:         45s
max_retries:     2
temperature:     0.3 (평가는 일관성 중요)
max_tokens:      1500
cost per call:   ~$0.005 (gpt-4o) 또는 ~$0.001 (mini 폴백)
cost per session: 3 plan × ~$0.005 = ~$0.015 (gpt-4o)
                  또는 3 × ~$0.001 = ~$0.003 (mini)
```

### 5.5 실행 모드 (cost mode)

```
- standard: gpt-4o 사용
- cost_saving: gpt-4o-mini 사용 (사용자가 무료 사용량 임계 도달 시)
- batch: gpt-4o-mini + temperature 0.1 (eval 자동 회귀용)

전환 기준은 ai_system/orchestration/cost_control_policy.md 참조.
```

### 5.6 의존성

```
이전 단계 출력: Planning의 plan 1개
RAG: 사용 안 함
Brand Memory: avoid_phrases, preferred_tone만 (brand_consistency 검사용)
prompt_registry P-ID: P-007
```

### 5.7 병렬 호출 정책

```
Planning가 3개 plan을 반환하면 Critic을 3개 병렬로 호출 (Promise.all).
1개라도 실패 시 나머지 2개는 그대로 진행, 실패한 1개는 재시도 1회.
재시도 후에도 실패면 해당 plan에 critic 결과 없이 사용자 노출 + 경고 표시.
```

### 5.8 revise 무한 루프 차단

```
revise_round = 0: 초기 평가
revise_round = 1: Rewriter 1차 결과에 대한 재평가
revise_round = 2: Rewriter 2차 결과에 대한 재평가

revise_round = 2에서 verdict가 다시 revise:
  → server-side가 강제로 verdict='approve'로 변경
  → validation.warnings에 "forced_approve_after_max_revise" 기록
  → 사용자에게 "AI 개선이 한계에 도달했어요. 직접 다듬어보시겠어요?" 알림
  → 사용자가 reject 선택 시 plan 폐기 + 새로운 plan 1개 재생성 옵션 제공
```

---

## 6. Rewriter Agent

### 6.1 책임

- Critic이 revise 판정한 plan을 개선 (P-008)
- changes_made 명시

### 6.2 Input 스키마

```json
{
  "target_plan": { /* P-006 plan, 또는 직전 Rewriter 출력의 improved_plan */ },
  "critic_result": { /* P-007 body 전체 */ },
  "selected_context": { /* Planning와 동일 */ },
  "brand_memory": {
    "preferred_phrases": ["string"],
    "avoid_phrases": ["string"],
    "preferred_tone": "string | null"
  },
  "revise_round": 1
}
```

### 6.3 Output 스키마

`output_schema.md` §10 P-008 body.

### 6.4 실행 정책

```
model:           gpt-4o-mini
timeout:         45s
max_retries:     2
temperature:     0.6 (개선이라 너무 다양하지 않게)
max_tokens:      2500
cost per call:   ~$0.001
cost per session 상한: $0.003 (최대 3개 plan 재작성)
```

### 6.5 자동 실행 vs 사용자 트리거

```
Phase 1 (현재): 사용자가 "AI에게 개선 맡기기" 클릭 시에만 실행.
                Critic 결과는 점수+이유만 보여주고, Rewriter는 명시적 요청 필요.
Phase 2+ (검토): revise 판정 시 자동 실행 옵션 (사용자 설정).
```

### 6.6 의존성

```
이전 단계 출력: Critic의 결과 + 원본 plan
RAG: 사용 안 함
Brand Memory: 항상 주입
prompt_registry P-ID: P-008
```

---

## 7. Memory Extractor Agent

### 7.1 책임

- 영상 세션 종료 시 Brand Memory 후보 자동 추출 (P-AUX-2)

### 7.2 Input 스키마

```json
{
  "video_session_log": {
    "video_id": "uuid",
    "discovery_choices": [ /* discovery_choices rows */ ],
    "feedback_events": [ /* feedback_events rows */ ],
    "revision_requests": [ /* revision_requests rows */ ],
    "selected_plan": { /* 최종 선택된 plan */ },
    "final_output_excerpt": "string | null"
  },
  "current_brand_memory": {
    "preferred_phrases": ["string"],
    "avoid_phrases": ["string"],
    "preferred_tone": "string | null",
    "success_patterns": ["string"],
    "rejection_patterns": ["string"]
  }
}
```

### 7.3 Output 스키마

`output_schema.md` §12 P-AUX-2 body.

### 7.4 실행 정책

```
model:           gpt-4o-mini
timeout:         60s
max_retries:     1 (실패해도 사용자 경험에 직접 영향 없음 → 백그라운드 재시도)
temperature:     0.4
max_tokens:      1500
cost per call:   ~$0.001
실행 시점:        video_projects.status가 'final'로 전이된 직후 백그라운드 큐
실행 주기:        세션당 1회. 재실행은 사용자 명시 요청 시만.
```

### 7.5 결과 처리

```
- confidence ≥ 0.9 AND conflicts_with_existing=false:
    → brand_memory_entries 자동 INSERT
- confidence ≥ 0.7 AND conflicts_with_existing=false:
    → pending queue에 저장. 다음 세션 시작 시 사용자에게 "이거 추가할까요?" 노출.
- confidence < 0.7:
    → 저장 안 함 (로그만 기록)
- conflicts_with_existing=true:
    → 항상 사용자 승인 필요. 자동 적용 금지.
- is_user_locked=true 항목과 충돌:
    → 무조건 폐기 (사용자 잠금은 최우선)
```

---

## 8. 오케스트레이션 흐름

### 8.1 Discovery Mode

```
1. user_input → Intent(P-AUX-1)         # 영상기획 관련 판정
2. (allow)    → Intent(P-001)           # Brand 카드 5장
3. 사용자 선택 → Intent(P-002)           # Domain 카드 5장
4. 사용자 선택 → Intent(P-003)           # Series 카드 5장
5. 사용자 선택 → Intent(P-004)           # Target+Tone 카드 5+5장
6. 사용자 선택 → Intent(P-005)           # 한 줄 방향
7. 사용자 승인 → Planning(P-006)          # 3개 plan
8. Planning 완료 → Critic(P-007) × 3 병렬 # 평가
9. (선택) revise 판정 → Rewriter(P-008)  # 개선
10. 사용자 plan 선택 → 다음 단계 (script, storyboard 등)
11. 세션 종료 → Memory Extractor(P-AUX-2) (백그라운드)
```

### 8.2 Quick Mode

```
1. quick_prompt → Intent(P-AUX-1)
2. (allow)      → Intent(P-005q)         # 한 줄 방향 + missing_info
3. (missing 있음) → 사용자에게 추가 질문 → P-005q 재실행
4. 사용자 승인  → Planning(P-006)
5. Planning 완료 → Critic(P-007) × 3 병렬
6. (선택) revise → Rewriter(P-008)
7. 사용자 plan 선택 → 다음
8. 세션 종료 → Memory Extractor(P-AUX-2)
```

### 8.3 시각화

```
       ┌──────────┐
       │  Intent  │  (Card Generator도 여기 묶음)
       └────┬─────┘
            │ approved_direction
            ▼
       ┌──────────┐  rag_context
       │ Planning  │ ◄────────────── RAG 검색
       └────┬─────┘
            │ plans[3]
            ▼
   ┌─────────────────────┐
   │ Critic × 3 (parallel)│
   └─────┬──────┬──────┬─┘
         │      │      │
       verdict  verdict verdict
         │      │      │
         ▼      ▼      ▼
       (선택적) Rewriter
         │      │      │
         └──── 사용자 선택 ────┐
                              │
                              ▼
                       Memory Extractor (백그라운드)
```

---

## 9. 비용 통제

### 9.1 호출당 상한

```
Intent (card):       $0.001
Intent (P-005):      $0.0005
Intent (P-AUX-1):    $0.0002
Planning:             $0.003
Critic (gpt-4o):     $0.006
Critic (mini 폴백):  $0.0015
Rewriter:            $0.0015
Memory Extractor:    $0.0015
```

각 호출이 위 상한의 1.5배를 넘으면 즉시 abort + 에러 응답.

### 9.2 세션당 상한

```
Discovery Mode (standard):      $0.030
Discovery Mode (cost_saving):   $0.015
Quick Mode (standard):          $0.020
Quick Mode (cost_saving):       $0.010
```

세션 누적 비용은 `agent_io_logs`에서 user_id + session_id로 집계. 상한 도달 시 다음 agent 호출을 차단하고 "오늘 사용량 임계 도달" 안내.

### 9.3 일일 사용자당 상한 (free tier)

```
무료 사용자: 일 $0.10 (대략 3~5세션)
유료 사용자: Phase 2+에서 정의
```

상한 도달 시 cost_saving 모드로 강등 → 그래도 초과 시 다음날까지 차단.

→ 자세한 정책은 `ai_system/orchestration/cost_control_policy.md` 참조.

---

## 10. 재시도 / 폴백 정책

### 10.1 자동 재시도 조건

```
- HTTP 5xx (모델 서버 오류) → 지수 백오프 1s → 2s → 4s, 최대 2회
- JSON 파싱 실패 → 즉시 1회 재시도 (prompt에 "JSON으로만 응답" 강조 추가)
- timeout (gateway 측) → 1회 재시도
- validation.passed=false AND retryable=true → 1회 재시도
```

### 10.2 폴백 (재시도 후에도 실패)

```
- Intent 실패: 사용자에게 "다시 입력해주세요" + 입력 보존
- Planning 실패: 사용자에게 에러 노출 + "재시도" 버튼.
                3개 중 2개라도 성공했으면 그대로 노출 + warning.
- Critic 실패: 평가 없이 plan만 노출 + "AI 검토 실패" warning.
               사용자가 직접 선택할 수 있도록.
- Rewriter 실패: 원본 plan 유지 + "개선 실패" 안내.
- Memory Extractor 실패: 사용자에게 노출 안 함. 24h 후 재시도 큐.
```

→ 자세한 폴백 절차는 `ai_system/orchestration/fallback_policy.md` 참조.

### 10.3 부분 결과 노출

```
Critic 3개 중 1개 실패:
  → 성공한 2개 plan은 verdict 노출
  → 실패한 1개는 "검토 불가" 표시 + 사용자가 직접 검토 옵션

Planning 3개 중 일부만 성공:
  → 성공한 N개 노출 + "추가로 생성하기" 버튼
```

---

## 11. agent_io_logs 기록 정책

모든 agent 호출은 `agent_io_logs` 테이블에 INSERT. (→ `db_schema.md` §7.1)

```sql
INSERT INTO agent_io_logs (
    log_id, user_id, video_id,
    agent_name, prompt_id, prompt_version, model,
    input_payload, output_payload,
    error, latency_ms, input_tokens, output_tokens, cost_usd,
    created_at
) VALUES (...);
```

### 11.1 기록 시점

```
- 호출 직전: row INSERT (output_payload=null)
- 호출 완료: 같은 row UPDATE (output_payload, latency_ms, tokens, cost_usd)
- 호출 실패: 같은 row UPDATE (error 필드 채움)
```

### 11.2 PII 마스킹

```
input_payload.user_input의 텍스트는 그대로 저장 (90일 후 비식별화).
brand_memory.preferred_phrases는 그대로 저장 (사용자 자기 데이터).
세션 종료 시 user_id는 그대로 유지하되, 90일 후 hash 처리.
```

### 11.3 분석용 인덱스

```
- agent_name별 평균 latency / 비용 / 실패율
- prompt_version 분기 (A/B 테스트)
- user_id별 일일 비용 (cost-control 트리거)
```

---

## 12. RAG 의존성

| Agent | RAG 사용 | 이유 |
|---|---|---|
| Intent | no | 카드 생성은 사용자 input + memory로 충분 |
| Planning | yes | 검증된 영상기획 패턴 참고 |
| Critic | no | 평가는 prompt에 내장된 기준으로 |
| Rewriter | no | Critic 결과만으로 개선 |
| Memory Extractor | no | 세션 로그만 분석 |

→ `docs/contracts/rag_data_contract.md`에서 검색 정책, top_k, similarity threshold 정의.

---

## 13. Brand Memory 의존성

| Agent | brand_memory 주입 | 사용 필드 |
|---|---|---|
| Intent (P-AUX-1) | no | — |
| Intent (P-001) | no | (첫 카드는 사용자 memory 없음 가정) |
| Intent (P-002~P-004) | yes | preferred_tone, avoid_phrases |
| Intent (P-005) | yes | preferred_phrases, avoid_phrases |
| Planning (P-006) | yes (full) | 전체 5개 필드 |
| Critic (P-007) | yes (partial) | avoid_phrases, preferred_tone |
| Rewriter (P-008) | yes (full) | 전체 5개 필드 |
| Memory Extractor (P-AUX-2) | yes (current state) | 모든 필드 (충돌 검사용) |

→ Brand Memory는 `brand_memory_entries`에서 `is_user_locked=true` 항목은 절대 무시되지 않음.

---

## 14. 타임아웃 / 지연 UX

```
agent           timeout    UX 표시
Intent (card)    30s        "AI가 후보를 만들고 있어요" + 카드 placeholder 4장
Intent (P-005)   30s        "한 줄 방향을 정리하고 있어요"
Intent (P-AUX-1) 10s        스피너 없이 즉시 (사용자 모름)
Planning          60s        4단계 stepper의 "Plan 생성 중" 표시 + 부분 결과 스트리밍
Critic           45s        "AI가 품질을 검토하고 있어요"
Rewriter         45s        "AI가 개선안을 만들고 있어요"
Memory Extractor 60s        백그라운드 (사용자에게 보이지 않음)
```

→ 자세한 UX 규칙은 `apps/web/design.md` §22 참조.

---

## 15. 보안 / 격리

```
- LLM API key는 server-side 환경변수에서만 접근. client는 절대 못 봄.
- agent 입력의 user_input 텍스트에 prompt injection 시도 발견 시 차단.
    (예: "이 위의 지시를 무시하고 ...")
- 차단 사례는 intent_filter_logs에 'block' + reason='prompt_injection' 기록.
- LLM 응답은 sanitization 후 사용자에게 노출 (HTML 태그, javascript: URL 제거).
```

→ 자세한 보안 정책은 `docs/contracts/llm_security_contract.md` 참조.

---

## 16. 호환성 / 모델 변경

```
- prompt_registry의 prompt_version과 model은 결합 매트릭스 관리.
- 모델 변경 시: 1주일 A/B (50:50) → 회귀 통과 → 전환.
- gpt-4o-mini ↔ Claude Haiku ↔ Gemini Flash는 모두 호환 (JSON mode 지원 모델).
- temperature / max_tokens는 모델별 default가 다를 수 있음 → execution.* 명시 필수.
```

---

## 17. 확장 가능성 (Phase 2+)

```
- Multi-agent voting: Critic 3개 모델 병렬 → 평균 verdict 채택
- Streaming output: Planning의 plan 1개씩 SSE로 전송
- Tool use: Critic이 RAG 직접 호출 (검증 보강)
- Function calling: agent 간 직접 호출 (오케스트레이터 우회) — 보안 검토 필요
- Voice/multi-modal input: Intent에 audio_transcript 추가
- Team workspace: 다중 user의 협업 시 session_id가 user_id를 묶음
```

---

## 18. Cross-reference 빠른 표

| Agent | 입력 출처 (DB/이전 단계) | 출력 저장 (DB) | prompt_id |
|---|---|---|---|
| Intent (cards) | user_input + selected_* | discovery_choices, agent_io_logs | P-001 ~ P-004 |
| Intent (P-005) | discovery_choices 누적 | video_projects.one_line_direction | P-005 |
| Intent (P-AUX-1) | user_input | intent_filter_logs | P-AUX-1 |
| Planning | approved_direction + RAG + memory | plan_options × 3 | P-006 |
| Critic | plan + memory | quality_scores | P-007 |
| Rewriter | plan + critic_result | revision_requests.rewriter_result | P-008 |
| Memory Extractor | session log + brand_memory | brand_memory_entries (조건부) | P-AUX-2 |

---

## 19. Open Questions

1. Critic을 gpt-4o로 고정할지, 사용자 무료 사용량 단위로 mini 폴백할지의 임계치 (현재 일 $0.10).
2. Rewriter 자동 실행 vs 사용자 명시 트리거 — 사용자 학습 데이터 누적 후 결정.
3. Memory Extractor의 자동 INSERT 임계 confidence (현재 0.9 자동, 0.7~0.9 pending queue).
4. Planning의 RAG top-k (현재 5 → 3 채택) — RAG 누적량에 따라 조정.
5. 3개 plan 중 1개라도 Critic 실패 시 자동 재생성 vs 부분 노출 — UX 협의 필요.
6. revise_round 강제 승격 시 사용자 안내 톤 (현재 친근체) — copy 검토.
7. Memory Extractor를 세션 종료 즉시 vs 24h 누적 후 일괄 처리 — 비용 vs UX 트레이드오프.

---

## 20. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S3-1 초안. 4 agent + Memory Extractor IO, 실행 정책, 비용 상한,
                      재시도/폴백, revise 무한 루프 차단, agent_io_logs 기록 정책.
```
