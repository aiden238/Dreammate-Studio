# feedback_loop_policy.md — 피드백 루프 정책

> 위치: `ai_system/memory/feedback_loop_policy.md`
> 상태: S4-3 deep
> 참조: `ai_system/prompts/prompt_registry.md` (P-AUX-2), `docs/contracts/db_schema.md` (feedback_events, brand_memory_entries, candidate_knowledge)
> 참조: `ai_system/memory/user_memory_policy.md`, `candidate_knowledge_policy.md`

---

## 1. 정의

**피드백 루프(Feedback Loop)**는 사용자 행동/명시 피드백을 받아 다음 세션에 반영하는 메커니즘이다. 두 가지 경로로 작동:

1. **User Memory (Brand Memory) 자동 추출** — P-AUX-2가 세션 종료 시 실행, 사용자 본인의 다음 세션에만 영향.
2. **candidate_knowledge 진입** — 일부 우수 패턴이 글로벌 학습 자산 후보로 진입, 5단계 승격 파이프라인 거침.

---

## 2. 피드백 수집 채널

```
명시적 (explicit):
  - 단계별 평점 (1~5점)
  - "이 표현 좋아요" / "이 표현 피해주세요" 명시 입력
  - 단계 완료 후 만족도 (Discovery 종료, plan 선택 후)
  - 자유 텍스트 피드백 (선택)

암묵적 (implicit):
  - 3 plan 중 어떤 plan 선택했는지 (choice_logs)
  - revise_round 진행 패턴 (몇 번까지 revise 했는지)
  - reject 후 새 plan 요청 여부
  - 동일 brand에서 반복 사용한 패턴
  - 세션 중도 이탈 (abandon)
```

DB 위치: `feedback_events`, `choice_logs`, `revision_requests`, `agent_io_logs.metadata.user_satisfaction`.

---

## 3. P-AUX-2 자동 Brand Memory 추출

agent_io §7 정합.

```
실행 시점:
  - video_projects.status='final' 전이 직후
  - 백그라운드 큐 (사용자 무관)

실행 주기:
  - 세션당 1회
  - 재실행은 사용자 명시 요청 시만

입력:
  - video_session_log (discovery_choices + feedback_events + revision_requests + selected_plan)
  - current_brand_memory (충돌 검사)

출력:
  - 추출된 preferred_phrases / avoid_phrases / preferred_tone / success/rejection_patterns
  - 각 항목별 confidence (0~1)
  - conflicts_with_existing 표시
```

---

## 4. 자동 vs 수동 처리 분기

user_memory_policy §3 일치.

```
자동 INSERT (사용자 모름):
  - confidence ≥ 0.9 AND conflicts_with_existing=false
  - is_user_locked=false

Pending Queue (다음 세션 시작 시 사용자 승인):
  - 0.7 ≤ confidence < 0.9 AND conflicts_with_existing=false
  - 또는 conflicts_with_existing=true (사용자 승인 필수)

폐기 (저장 안 함):
  - confidence < 0.7
  - is_user_locked=true 충돌

명시 피드백 → 즉시 적용:
  - "이 표현 좋아요" → preferred_phrases 즉시 추가
  - "이 표현 피해주세요" → avoid_phrases 즉시 추가
```

---

## 5. 학습 신호

```
선택률 (choice_rate):
  - plan별 선택 횟수 / 노출 횟수
  - approach_label별 집계 (공감-스토리 vs 즉시-혜택 등)
  - hook 첫 단어별 집계

평균 만족도:
  - 단계별 평점 평균
  - plan별 평점

revise 패턴:
  - revise_round 평균 (1.5 이상이면 plan 품질 의심)
  - 자주 revise되는 차원 (hook? message?)

이탈률:
  - 어느 단계에서 가장 많이 이탈하는지
  - Discovery vs Quick 이탈률 비교
```

학습 신호는 `eval/cost_snapshots/`와 별도로 `eval/quality_snapshots/` (Phase 7+ 도입)에 적재.

---

## 6. candidate_knowledge 진입 흐름

`candidate_knowledge_policy.md` 참조. 피드백 → candidate_knowledge 진입 조건:

```
- 선택률 ≥ 0.5 (같은 plan 패턴이 절반 이상 선택)
- 평균 평점 ≥ 4.0
- 이상 outlier가 아닌 다수 사용자 패턴
- PII 마스킹 통과
- quality_filter 통과
```

진입 후 rag-update Skill의 5단계 파이프라인 통과.

---

## 7. 피드백 처리 우선순위

```
1. 사용자 명시 피드백 (preferred/avoid 즉시 입력) → 최우선, 즉시 반영
2. is_user_locked=true 보존 → 모든 자동 변경에 우선
3. P-AUX-2 자동 추출 (confidence ≥ 0.9) → 자동 INSERT
4. P-AUX-2 자동 추출 (0.7 ≤ confidence < 0.9) → pending → 사용자 승인
5. 암묵 신호 → 다음 plan 생성에 가중치 (직접 brand_memory_entries 변경 안 함)
```

---

## 8. 의존성

- `ai_system/prompts/prompt_registry.md` (P-AUX-2)
- `docs/contracts/db_schema.md` (feedback_events, brand_memory_entries, choice_logs)
- `ai_system/memory/user_memory_policy.md`
- `ai_system/memory/candidate_knowledge_policy.md`
- `knowledge/datasets/user_feedback_data.md` (피드백 데이터셋 정의)

---

## 9. 확장 가능성

- Phase 11+: 실시간 피드백 (plan 생성 중 사용자 개입).
- Phase 11+: 자동 A/B (사용자 그룹별 prompt 차별 시도).
- Phase 21+: 협업 단위 피드백 (team의 누적 학습).

---

## 10. Open Questions

1. confidence ≥ 0.9 자동 INSERT 임계 — 사용자 신뢰성 누적 후 재조정.
2. 명시 피드백 vs 암묵 신호 가중치 — 현재 명시가 절대 우선.
3. 이탈률 측정 단위 (페이지 단위 vs 단계 단위) — 현재 단계 단위.
4. candidate_knowledge 진입 임계(선택률 0.5, 평점 4.0) 적정성.
5. 학습 신호를 사용자에게 노출할지(투명성) vs 무음(현재 무음).
