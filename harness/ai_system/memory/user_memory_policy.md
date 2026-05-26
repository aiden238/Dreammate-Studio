# user_memory_policy.md — 사용자 메모리 정책

> 위치: `ai_system/memory/user_memory_policy.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/db_schema.md` (brand_memory_entries), `docs/contracts/privacy_contract.md` (placeholder)
> 참조: `docs/contracts/data_retention_policy.md` (placeholder)
> 참조: `ai_system/agents/intent_agent.md`, `planning_agent.md`, `rewrite_agent.md`

---

## 1. 정의

**사용자 메모리(User Memory)**는 한 사용자의 누적된 선호/패턴/지양 사항을 4계층 컨텍스트(Brand) 단위로 저장한 데이터다. 본 정책에서는 Brand Memory를 중심으로 정의한다.

DB 위치: `brand_memory_entries`. 필드:
- `preferred_phrases`: 자주 사용하는/선호하는 구문
- `avoid_phrases`: 지양 구문 (광고 단어, 부정 표현 등)
- `preferred_tone`: 선호 톤 (친근/전문/유머 등)
- `success_patterns`: 좋은 반응을 얻은 패턴 (hook, 구조 등)
- `rejection_patterns`: 거절된 패턴

---

## 2. 추출 트리거

```
1. P-AUX-2 (Memory Extractor) 자동 추출:
   - 세션 종료 시 (video_projects.status='final')
   - 백그라운드 큐로 실행

2. 사용자 명시 피드백:
   - 단계별 평점 (1~5점)
   - "이런 패턴 좋아요" / "이런 표현은 피해주세요" 명시 입력

3. 사용자 선택 시그널:
   - 3개 plan 중 1개 선택 → 선택 plan의 hook/tone 학습 신호
   - 재방문 시 동일 brand에서 반복 사용한 패턴

4. 거절 시그널:
   - revise_round 반복 후 reject
   - Memory Extractor가 rejection_patterns에 자동 적재 (조건부)
```

---

## 3. 자동 INSERT 임계

agent_io §7.5 일치.

```
confidence ≥ 0.9 AND conflicts_with_existing=false:
  → brand_memory_entries 자동 INSERT

0.7 ≤ confidence < 0.9 AND conflicts_with_existing=false:
  → pending queue, 다음 세션 시작 시 사용자 승인 노출

confidence < 0.7:
  → 저장 안 함 (로그만 기록)

conflicts_with_existing=true:
  → 항상 사용자 승인 필요. 자동 적용 금지.

is_user_locked=true 충돌:
  → 무조건 폐기 (사용자 잠금 최우선)
```

---

## 4. 익명화 / PII 마스킹

```
저장 직전:
  - 이메일 / 전화번호 / 주소 자동 마스킹 (privacy_contract 정책)
  - 사람 이름은 그대로 저장 (브랜드명일 가능성 높음)
  - 카드 / 계좌 번호 자동 차단 (저장 거부)

저장 후:
  - user_id는 90일 후 hash 처리 (agent_io §11.2)
  - 사용자 삭제 요청 시 즉시 무효화 + 30일 후 물리 삭제
```

PII 검출은 정규식 + LLM hybrid (llm_security_contract).

---

## 5. 보존 기간

```
preferred_phrases / avoid_phrases:
  - 활성: 사용자 활성 동안 유지
  - 90일 미사용 brand: archive (읽기 전용)
  - 365일 미사용: hash + 익명화

preferred_tone / success_patterns / rejection_patterns:
  - 동일 정책

사용자 명시 삭제 요청:
  - 즉시 비활성화
  - 30일 grace period
  - 30일 후 물리 삭제 (또는 hash)
```

→ `docs/contracts/data_retention_policy.md` placeholder가 Phase 7+에서 본 정책을 정량화.

---

## 6. 주입 정책 (어떤 agent에 어떤 필드)

agent_io §13 일치.

| Agent | 주입 여부 | 사용 필드 |
|---|---|---|
| Intent P-AUX-1 | no | — |
| Intent P-001 (brand_card) | no | (첫 카드, memory 없음 가정) |
| Intent P-002~P-004 | partial | preferred_tone, avoid_phrases |
| Intent P-005 | partial | preferred_phrases, avoid_phrases |
| Planning P-006 | full | 5개 필드 전체 |
| Critic P-007 | partial | avoid_phrases, preferred_tone |
| Rewriter P-008 | full | 5개 필드 전체 |
| Memory Extractor P-AUX-2 | full (현재 상태) | 충돌 검사용 |

---

## 7. is_user_locked 규칙

사용자가 명시적으로 "이 항목은 절대 변경하지 마"라고 설정한 항목.

```
is_user_locked=true 항목:
  - 자동 추출에서 절대 변경/덮어쓰기 금지
  - Memory Extractor 충돌 시 무조건 폐기
  - 사용자만 명시적 unlock 가능
  - UI에 자물쇠 아이콘 표시
```

---

## 8. 의존성

- `docs/contracts/db_schema.md` (brand_memory_entries 스키마)
- `docs/contracts/privacy_contract.md` (placeholder, PII 정책)
- `docs/contracts/data_retention_policy.md` (placeholder, 보존 기간)
- `ai_system/prompts/prompt_registry.md` (P-AUX-2)
- `ai_system/agents/intent_agent.md`, `planning_agent.md`, `rewrite_agent.md`
- `knowledge/datasets/user_choice_data.md`, `user_feedback_data.md`

---

## 9. 확장 가능성

- Phase 11+: Domain Memory, Series Memory 분리 (현재 Brand 단위만).
- Phase 11+: 사용자별 선호 모델 학습 (gpt-4o vs Claude 선호도).
- Phase 21+: 사용자 동의 시 cross-brand 패턴 공유 (anonymized).

---

## 10. Open Questions

1. confidence ≥ 0.9 자동 INSERT 임계가 적정한지 — 사용자 데이터 누적 후 재조정.
2. pending queue 노출 빈도 — 매 세션 시작 시 표시 vs 모아서 주 1회.
3. PII 검출에 LLM 사용 시 cost 증가 — 정규식 only로 충분한지 검증.
4. cross-brand 패턴 공유의 사용자 동의 UX(현재 미정).
5. 90일 미사용 brand archive 시 사용자 알림 여부(현재 무음).
