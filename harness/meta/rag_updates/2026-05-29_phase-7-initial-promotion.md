# Phase 7 Initial RAG Promotion — rag-update Skill ★ 첫 정식 트리거

> Date: 2026-05-29
> Phase: 7 Slice 4
> Skill: rag-update (★ 첫 정식 트리거)
> Related: ADR-024 / ADR-025 / ADR-026 + knowledge/rag/promotion_rule.md
> Sub-agent: Phase 7 Slice 4 dispatch

---

## §1. Scope

Phase 7 Slice 4 진입 시 LLM Wiki 정적 항목 5개 + Phase 1~6 누적 사용자 입력 0개를
RAG 5단계 파이프라인으로 처리.

본 문서는 **rag-update Skill 첫 정식 트리거** 결과 — Phase 7 운영 단계 baseline 기록.

### Skill SKILL.md 절차 매핑

| Skill 단계 | 본 phase 적용 |
|---|---|
| Step 1 pending | 사용자 입력 0개 + LLM Wiki 5개 (정적 — `rag/llm_wiki.py` in-memory) |
| Step 2 filtered | quality_filter 적용 대상 없음 (LLM Wiki는 git-tracked + 시스템 신뢰) |
| Step 3 evaluated | eval_rubric 적용 대상 없음 |
| Step 4 approved | 본 phase 진입 데이터 0개 |
| Step 5 promoted | approved_knowledge 테이블 빈 상태 유지 |

---

## §2. 5단계 procedure 적용

### Stage 1: pending — 후보 수집

- **출처**: LLM Wiki 정적 5개
  - `hook_patterns` / `target_persona` / `tone_guide` / `structure_3act` / `cta_types`
- **메타**: `source_kind=llm_wiki`, type=`static_guide`
- **결정**: 정적 LLM Wiki는 본 phase에서 `rag/llm_wiki.py` in-memory 유지.
  RAG 5단계 파이프라인 진입은 Phase 11+ 사용자 데이터 누적 후 (NG7 정신 계승 +
  ADR-024 §A 확대 지점).

### Stage 2: filtered — 자동 품질 필터 (quality_filter)

- **적용 대상**: 본 phase 진입 데이터 없음 (LLM Wiki는 in-memory)
- **정책**: PII + 인젝션 + 광고적 표현 차단 (확정 결정 [9] + ADR-026 §1.1)
- **검증**: `rag/quality_filter.py` 활성 — 차후 사용자 입력 시 즉시 적용

### Stage 3: evaluated — 품질 평가 (eval_rubric)

- **적용 대상**: 본 phase 진입 데이터 없음
- **정책**: relevance + clarity + safety 3 dim (간이, ADR-026 §3)
- **Phase 9+ deprecated 예정** (golden_set 기반 정식 rubric으로 교체)

### Stage 4: approved — 승인 (hybrid)

- **적용 대상**: 본 phase 진입 데이터 없음
- **정책**:
  - 자동: `overall_score ≥ 0.8` (ADR-026 §1.3)
  - 수동 대기: `0.6 ≤ overall_score < 0.8`
  - 거부: `overall_score < 0.6` (transition 자체에서 차단)
- **검증**: `rag/promotion.py` `transition()` 활성

### Stage 5: promoted — approved_knowledge 승격

- **적용 대상**: 본 phase 진입 데이터 없음
- **이력**: `promotion_history` JSONB append-only 강제 (ADR-026 §1.5)

---

## §3. 본 phase 진입 결과

| 출처 | 개수 | 처리 |
|---|---|---|
| LLM Wiki 정적 5개 | 5 | `rag/llm_wiki.py` in-memory 유지 (★ Phase 11+에서 RAG 진입 재검토) |
| 사용자 입력 | 0 | 본 phase 종료 후 첫 사용자 입력부터 5단계 적용 |
| 외부 시드 | 0 | NG6 (Hybrid retrieval) 시점 도입 검토 |

- `candidate_knowledge` 테이블은 **빈 상태**로 본 phase 종료 (스키마 + 함수만 활성, 데이터는 운영 단계 누적).
- `approved_knowledge` 테이블도 **빈 상태**.
- LLM Wiki 5개 항목은 `rag/llm_wiki.py` in-memory에서 즉시 lookup 가능.

---

## §4. Skill SKILL.md 자주 발생하는 실수 회피 확인

- ❌ 사용자 raw 입력을 candidate_knowledge에 직접 INSERT 시도 — **본 phase 0건** (사용자 입력 0)
- ❌ 외부 시드 자동 승인 — **본 phase 해당 없음**
- ❌ 회귀 평가 생략 — **본 phase 5단계 데이터 0개라 생략 정상** (Phase 9+ eval-run 활성 이후 정식)
- ❌ 자동 승격 임계값 임의 조정 — **본 phase 0.8 / 0.6 유지** (ADR-026 §1.3, contract-change 절차 없이 변경 X)
- ❌ 사용자별 RAG와 global RAG 혼동 — `brand_id` 격리 retrieval 단계 강제 (ADR-025 §3 정합)
- ❌ 개인정보 마스킹 누락 — `rag/quality_filter.py` PII 패턴 활성 (즉시 적용 가능)

---

## §5. Phase 7 종료 후 rag-update 호출 예정 시점

| 시점 | 트리거 | 비고 |
|---|---|---|
| Phase 11+ 사용자 데이터 누적 후 | rag-update 두 번째 정식 호출 | ADR-024 §A 자동 promotion 확대 지점 |
| 새 외부 시드 데이터 도입 (NG6 시점) | rag-update 호출 (수동) | external_seed 사용자 명시 승인 필수 |
| 사용자 final_output → Brand Memory 후보 추출 | rag-update 호출 (자동 + Critic 평가) | Phase 9+ Brand Memory 활성 |
| LLM Wiki 신규 항목 추가 | rag-update 호출 (수동) | git commit + 본 문서 갱신 |

---

## §6. References

- ADR-024 (`docs/decisions/phase_7_rag_scope_evolution.md`) — Phase 5.5 RAG scope evolution
- ADR-025 (`docs/decisions/phase_7_rag_architecture.md`) — Slice 1 RAG architecture
- ADR-026 (`docs/decisions/phase_7_promotion_logic.md`) — Slice 1 5단계 promotion logic
- `knowledge/rag/promotion_rule.md` — 5단계 표준
- `knowledge/llm_wiki/index.md` — LLM Wiki baseline
- `.claude/skills/rag-update/SKILL.md` — ★ 첫 정식 트리거 절차
- `backend/fastapi/rag/llm_wiki.py` — 본 phase 신규 (정적 5개)
- `backend/fastapi/rag/promotion.py` — Slice 2 (transition + promotion_history)
- `backend/fastapi/rag/quality_filter.py` — Slice 2 (PII + 인젝션 + 광고)
- `backend/fastapi/rag/eval_rubric.py` — Slice 2 (3 dim)

---

## §7. 산출물 요약 (Skill SKILL.md "산출물" 정합)

| 산출물 | 본 phase 결과 |
|---|---|
| candidate_knowledge 상태 전이 로그 | 0건 (데이터 0) |
| knowledge/approved_knowledge/{brand_id}/*.md | 0개 (데이터 0) |
| rag_documents + rag_chunks INSERT | 0건 (데이터 0) |
| agent_io_logs (LLM Critic 평가 등) | 0건 (데이터 0) |
| 회귀 평가 결과 | N/A (Phase 9+ eval-run 정식화 이후) |

---

## §8. Skill trigger 기록

- **rag-update**: ★ 첫 정식 트리거 (Phase 7 Slice 4)
  - 절차 5단계 모두 매핑 (pending → filtered → evaluated → approved → promoted)
  - 본 phase 진입 데이터 0건이라 실제 transition 실행 없음 — 운영 baseline + 절차 활성화 확인
  - 후속: Phase 11+ 사용자 데이터 누적 후 두 번째 정식 호출 (ADR-024 §A 자동 promotion 확대)
  - skill_usage_log: rag-update 0 → 1 (active 전환 — Slice 5에서 기록)

---

## §9. Status timeline

- 2026-05-29 — Phase 7 Slice 4. **rag-update Skill 첫 정식 트리거**. 본 문서 작성.
  본 phase 진입 데이터 0건 + LLM Wiki 5개 in-memory 유지.
- (예정) Phase 9+ — eval-run Skill 정식화 후 회귀 평가 자동 실행 (golden_set 기반).
- (예정) Phase 11+ — 사용자 데이터 누적 후 자동 promotion 활성 (ADR-024 §A) + 두 번째 rag-update 정식 호출.
- (예정) Phase 21+ — Custom embedding 교체 검토 (ADR-024 §B) + rag-update 호출 (vector 재계산).
