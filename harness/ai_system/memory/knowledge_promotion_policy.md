# knowledge_promotion_policy.md — 지식 승격 정책 (rag-update Skill 운영 가이드)

> 위치: `ai_system/memory/knowledge_promotion_policy.md`
> 상태: S4-3 deep
> 참조: `knowledge/rag/promotion_rule.md`, `docs/contracts/rag_data_contract.md` §4
> 참조: `ai_system/memory/candidate_knowledge_policy.md`
> 참조: `.claude/skills/rag-update/SKILL.md`

---

## 1. 정의

본 정책은 `rag-update` Skill이 강제하는 **5단계 승격 파이프라인**의 운영 가이드다. RAG 지식을 추가하거나 candidate_knowledge를 approved_knowledge로 promotion할 때 항상 거치는 절차를 정의한다.

`promotion_rule.md`는 RAG 측면의 정책 정의이며, 본 문서는 **AI system 측의 운영 책임 분담**을 정의한다.

---

## 2. 5단계 파이프라인 (재확인)

```
1. pending     ─ 후보 진입 (사용자 피드백 / llm_wiki / 외부 시드 / 내부 생성)
2. filtered    ─ quality_filter.md 자동 적용 (PII, 금지어, 길이 등)
3. evaluated   ─ P-EVAL-1 자동 평가 (5 차원, 0~1 score)
4. approved    ─ 운영자 또는 자동 승격 (promotion_rule.md 임계)
5. promoted    ─ approved_knowledge에 INSERT, RAG 검색 대상 활성화
```

각 단계 통과 시 candidate_knowledge.status 업데이트.

---

## 3. 각 단계 책임자

| 단계 | 책임자 | 자동/수동 |
|---|---|---|
| 1. pending 진입 | system (feedback_loop, rag-update Skill) | 자동 |
| 2. filtered 전환 | system (quality_filter 적용) | 자동 |
| 3. evaluated 전환 | system (P-EVAL-1 호출) | 자동 |
| 4. approved 전환 | 운영자 OR system(임계 충족 시) | hybrid |
| 5. promoted | system (approved_knowledge INSERT) | 자동 |
| rejected 재진입 | 운영자 | 수동 |
| approved 강등 | 운영자 (rare) | 수동 |

운영자 = 프로젝트 owner (현재는 단일 사용자 본인, Phase 11+ 팀 도입 시 변경).

---

## 4. 자동 승격 임계

`promotion_rule.md` 정책 + 다음 조건 모두 만족 시 자동 승격:

```
- P-EVAL-1 score ≥ 0.85
- quality_filter 통과 (모든 5개 필터)
- 중복 검사 통과 (cosine similarity < 0.85 with approved_knowledge)
- 사용자 출처인 경우:
    - origin_user_id 동의 (피드백 진입 시 동의 확보)
    - 다중 사용자 공통 패턴 (≥ 3명)
- 외부 시드: 운영자 명시 승인 필요 (자동 승격 불가)
- llm_wiki: 운영자 명시 승인 필요
```

자동 승격 비활성(Phase 0~10): 운영자가 항상 명시 승인. Phase 11+에서 점진 활성화.

---

## 5. 강등 정책

approved_knowledge에서 candidate_knowledge로 강등하는 경우:

```
강등 트리거:
  - 운영자가 명시 강등
  - 사용자 신고 누적 (≥ 3건 동일 chunk)
  - 후속 evaluation에서 점수 ≤ 0.5 (모델 업데이트 후 재평가)
  - 안전성 위반 발견

강등 처리:
  1. approved_knowledge.status='archived'
  2. RAG 검색에서 즉시 제외
  3. candidate_knowledge로 복사 (rejected 또는 pending)
  4. 재평가 필요 시 status='pending' → 재진입
```

---

## 6. P-EVAL-1 평가 차원 (재확인)

prompt_registry P-EVAL-1과 정합:

```
1. accuracy       — 사실 정확도 (0~1)
2. relevance      — 영상기획 도메인 관련성
3. uniqueness     — 기존 knowledge와 중복 아님
4. safety         — 광고 단어, PII 부재
5. completeness   — 의미 단위 완결성

overall = weighted average (각 차원 가중치는 promotion_rule.md 정의)
pass: overall ≥ 0.85 AND 모든 차원 ≥ 0.6
```

---

## 7. 운영 흐름 (rag-update Skill)

```
1. 사용자 또는 시스템이 rag-update Skill 호출
2. Skill이 candidate_knowledge 신규 entry 생성 (status='pending')
3. 자동 quality_filter 적용 → filtered 또는 rejected
4. 자동 P-EVAL-1 호출 → evaluated (score 기록)
5. 운영자 검토 화면 노출 (Phase 0~10):
   - 콘텐츠 미리보기
   - P-EVAL-1 점수 + 이유
   - quality_filter 결과
   - "승격" / "거절" / "보류" 버튼
6. 승격 클릭 시 → approved_knowledge INSERT + 로그 기록
7. 거절 시 → status='rejected' + rejection_reason 기록
```

---

## 8. 의존성

- `knowledge/rag/promotion_rule.md` (정책 본문)
- `knowledge/rag/quality_filter.md` (필터 정의)
- `docs/contracts/rag_data_contract.md` §4 (5단계 정의)
- `ai_system/memory/candidate_knowledge_policy.md` (테이블 운영)
- `ai_system/prompts/prompt_registry.md` (P-EVAL-1)
- `.claude/skills/rag-update/SKILL.md` (운영 Skill 정의)
- `docs/contracts/privacy_contract.md` (placeholder, PII)

---

## 9. 확장 가능성

- Phase 11+: 자동 승격 임계 점진 활성화 (운영자 부담 감소).
- Phase 11+: 다중 운영자 (팀) 도입 시 승인 quorum.
- Phase 21+: 자동 재평가 (모델 업데이트 시 approved_knowledge 일괄 재평가).
- Phase 21+: cross-language promotion.

---

## 10. Open Questions

1. 자동 승격 임계(score 0.85, 다중 사용자 3명) 적정성 — 데이터 누적 후 재조정.
2. 운영자 검토 누적 부담 — Phase 11+ 자동화 시점.
3. 강등 신고 임계(3건)의 적정성 — 사용자 신뢰성 가중 필요할 수 있음.
4. 자동 재평가 trigger(모델 업데이트 시) — Phase 21+ 비용 vs 품질 트레이드오프.
5. cross-language metadata 정의 (Phase 21+).
