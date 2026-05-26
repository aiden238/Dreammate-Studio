# candidate_knowledge_policy.md — Candidate Knowledge 운영 정책

> 위치: `ai_system/memory/candidate_knowledge_policy.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/db_schema.md` (candidate_knowledge), `docs/contracts/rag_data_contract.md` §4
> 참조: `knowledge/rag/promotion_rule.md`, `knowledge/rag/quality_filter.md`
> 참조: `ai_system/memory/knowledge_promotion_policy.md`, `feedback_loop_policy.md`

---

## 1. 정의

**candidate_knowledge**는 RAG의 `approved_knowledge`로 승격되기 전 잠재적 학습 자산 후보를 저장하는 테이블이다. 사용자 피드백, LLM Wiki 신규 항목, 외부 시드 데이터 등이 진입한다.

진입 후 5단계 승격 파이프라인을 거쳐 `approved_knowledge`로 promotion되거나, rejected로 보관/삭제된다.

→ rag_data_contract §4와 정합.

---

## 2. DB 스키마 (요약)

```
candidate_knowledge:
  - chunk_id (uuid, PK)
  - content (text, 의미 단위 청크)
  - source ('user_feedback' | 'llm_wiki' | 'external_seed' | 'internal_generated')
  - origin_user_id (uuid, nullable)  -- 사용자 출처일 때만
  - origin_brand_id (uuid, nullable)
  - status ('pending' | 'filtered' | 'evaluated' | 'approved' | 'rejected')
  - evaluation_score (float, P-EVAL-1 결과, 0~1)
  - evaluation_reasons (jsonb)
  - quality_filter_result (jsonb)
  - metadata (jsonb, knowledge/rag/metadata_schema.md 정의 따름)
  - created_at, updated_at
  - approved_at (nullable)
  - rejected_at (nullable), rejection_reason
```

→ db_schema.md candidate_knowledge 정의가 정합.

---

## 3. 진입 트리거

```
1. 사용자 피드백 (feedback_loop_policy 경유):
   - 선택률 ≥ 0.5, 평균 평점 ≥ 4.0 patterns
   - feedback_loop가 candidate_knowledge에 자동 INSERT (status='pending')

2. llm_wiki 신규 항목:
   - knowledge/llm_wiki/ 에서 의미 단위 청크
   - 운영자가 rag-update Skill로 진입

3. 외부 시드 데이터:
   - knowledge/datasets/external_seed_data.md에 정의된 외부 source
   - 운영자가 batch INSERT

4. 내부 생성 데이터:
   - internal_generated_data.md (LLM이 합성한 데이터)
   - 자동 진입 (status='pending')

5. Memory Extractor 우수 패턴:
   - confidence ≥ 0.95 AND 다중 사용자 공통 패턴
   - 자동 진입
```

---

## 4. 5단계 승격 파이프라인 (rag_data §4)

```
1. pending     → 진입 직후 상태
2. filtered    → quality_filter.md 정책 통과 (PII, 광고 금지어, 길이 등)
3. evaluated   → P-EVAL-1 자동 평가 (5 차원, 임계 통과)
4. approved    → 운영자 또는 자동 승격 (promotion_rule.md)
5. → approved_knowledge로 INSERT, candidate_knowledge.status='approved'
```

각 단계는 rag-update Skill이 강제한다.

---

## 5. rejected 처리

```
rejection 사유 (rejection_reason):
  - 'pii_violation': PII 발견
  - 'quality_low': P-EVAL-1 평가 점수 미달
  - 'duplicate': 기존 approved_knowledge와 중복
  - 'banned_phrase': 광고 금지어 포함
  - 'incomplete': 의미 단위 미완결
  - 'safety': 안전성 위반

보존 기간:
  - rejected 상태 유지 30일 (재검토 가능)
  - 30일 후 status='archived' (읽기 전용)
  - 365일 후 물리 삭제

재진입 (re-evaluation):
  - 운영자가 명시적으로 trigger
  - rejection_reason 해결 시
```

---

## 6. 자동 vs 수동 처리

```
자동:
  - 1단계 pending 진입 (피드백/외부 시드/내부 생성)
  - 2단계 filtered 전환 (quality_filter 자동 적용)
  - 3단계 evaluated 전환 (P-EVAL-1 자동 호출)

수동 (운영자 승인):
  - 4단계 approved 전환 (promotion_rule.md 정책 + 운영자 검토)
  - rejected 재진입
  - approved 강등 (rare)
```

→ knowledge_promotion_policy.md가 각 단계 책임자를 정의.

---

## 7. 진입 시 PII 마스킹

```
사용자 출처 (user_feedback) 진입 시:
  1. 정규식 마스킹 (이메일, 전화, 주소)
  2. LLM 기반 PII 검출 (이름 + 식별 정보 조합)
  3. origin_user_id, origin_brand_id는 별도 컬럼 저장 (콘텐츠와 분리)
  4. content 자체에는 어떤 식별자도 남기지 않음

외부 시드 / llm_wiki 진입 시:
  - PII 발견 자체가 입력 오류 (운영자에게 알림)
```

---

## 8. 의존성

- `docs/contracts/rag_data_contract.md` §4 (5단계 파이프라인)
- `docs/contracts/db_schema.md` (candidate_knowledge 스키마)
- `knowledge/rag/promotion_rule.md` (승격 정책)
- `knowledge/rag/quality_filter.md` (품질 필터)
- `ai_system/prompts/prompt_registry.md` (P-EVAL-1)
- `ai_system/memory/feedback_loop_policy.md` (피드백 → candidate)
- `ai_system/memory/knowledge_promotion_policy.md` (승격 운영)
- `.claude/skills/rag-update/SKILL.md` (운영 Skill)

---

## 9. 확장 가능성

- Phase 11+: candidate_knowledge → approved 자동 승격 임계 도입 (현재 운영자 수동).
- Phase 11+: rejected 자동 재평가 (모델 업데이트 시).
- Phase 21+: cross-language candidate (다국어 영상기획).

---

## 10. Open Questions

1. 자동 진입 임계(선택률 0.5, 평점 4.0)의 정량 검증 — 데이터 누적 후 재조정.
2. 자동 승격(promotion) 도입 시점 — Phase 11+ 운영자 부담 감소 검토.
3. rejected 30일 보존 vs 즉시 삭제 — 재검토 빈도 관찰 후 결정.
4. PII 검출 LLM 사용 cost — 정규식 only로 충분한 경우 vs LLM 필수인 경우 구분.
5. cross-language 진입 시 metadata.language 처리 (Phase 21+).
