# ADR-031 — Phase 9 Brand Memory 준비 (P-AUX-2 설계, agent 미구현 Phase 10+)

> Date: 2026-05-29 (Slice 1 결정) / finalized 2026-05-30 (Slice 4 — 적재 경로 구현 반영)
> Status: Accepted (Slice 4 finalized)
> Phase: 9 (결과 저장 + 피드백)
> Slice: 4 (구현 — 적재 경로 + ADR finalize) / Slice 1 (본 ADR 결정)
> Related: ADR-024 (phase_7_rag_scope_evolution — Brand Memory Phase 9+ cross-ref), ADR-025/026 (Phase 7 RAG 5단계),
>          ADR-030 (phase_9_feedback_selection — feedback→candidate 적재 cross-ref)
> Skill: rag-update (Phase 11+ 두 번째 트리거 — 자동 승격) cross-ref

## Context

사용자 결정 5 (Phase 5.5 결정 5 + Phase 7 누적 confirm): **Brand Memory 자동 추출은 Phase 9 이후** (Phase 10+ — MVP 운영 + 데이터 누적 후). Phase 9 는 **준비만**.

**현 상태 (entry 시점)**:

- db_schema.md §6 `brand_memory_entries` 테이블 **정의만** (entry_type: preferred_tone / avoid_phrase / preferred_phrase / success_pattern / rejection_pattern + content + confidence + is_user_locked) — migration 미반영.
- ai_system/prompts/prompt_registry.md `P-AUX-2 · brand_memory_extractor` — **명세만** (Version v1.0.0, input: video_session_log + current_brand_memory, output: proposed_entries, "실 구현은 Phase 9+ — registry 명세만 보존"). agent 파일 미구현.
- db_schema §7.2 `candidate_knowledge.source_kind` enum 'user_choice' / 'user_feedback' / 'final_output' / 'manual' — Phase 7 5단계 진입점 (pending).

**Gap**: Brand Memory 자동 추출 인프라(schema + 적재 경로 + agent)가 미구축. 사용자 결정 5 에 따라 Phase 9 에서 **준비**(schema + ADR + 적재 경로)만 하고 agent 는 Phase 10+ 로 이관.

## Decision

### Phase 9 = 준비만 (4가지)

| 준비 항목 | Slice | 범위 |
|---|---|---|
| 1. `brand_memory_entries` schema | 2 | db_schema §6 정의를 0005 migration 에 등록 (RLS 포함) |
| 2. `BrandMemoryRepo` | 2 | graceful(PlansRepo 패턴) — **수동/준비용** entry CRUD (create/list). **자동 추출 X** |
| 3. feedback/selection → candidate_knowledge 적재 경로 | 4 | `rag/feedback_to_candidate.py` — source_kind='user_feedback'/'user_choice', status='pending' INSERT (자동 승격 X) |
| 4. P-AUX-2 설계 명세 ADR | 1+4 | 본 ADR §P-AUX-2 설계 (input/output/활성화 조건) — registry 명세 참조, 실행 X |

### §P-AUX-2 설계 명세 (Phase 10+ 활성화 — 참조만)

prompt_registry.md P-AUX-2 명세를 기반으로 한 설계 참조 (Phase 9 는 미구현):

```
agent       : brand_memory_extractor (Phase 10+ 구현 예정 — Phase 9 미구현)
input        : video_session_log (선택/거절/수정 이력) + current_brand_memory
output       : proposed_entries [{ entry_type, content, confidence 0–1, source_evidence }]
              entry_type: preferred_tone | avoid_phrase | preferred_phrase
                          | success_pattern | rejection_pattern
규칙 (registry §System) :
  - 1회성 결정 confidence ≤ 0.3 / 2회 이상 반복 ≥ 0.7 / 명시 선호 ≥ 0.9
  - 기존 Brand Memory 충돌 항목 우선 제외 + 별도 표시 / 최대 5개
활성화 조건  : MVP 운영 시작 + 피드백/선택 데이터 누적 (Phase 10+)
              — Phase 9 적재 경로(candidate_knowledge pending)가 데이터 누적 인프라 선 구축
```

- Phase 9 는 P-AUX-2 agent 파일 **미생성** + orchestration **미연결** + 자동 추출 **호출 0**.
- 본 ADR 은 설계 참조(input/output/활성화 조건)만 — registry 가 단일 출처(SoT).

### §P-AUX-2 설계 명세 구체화 (Slice 4 finalize — Phase 10+ 활성화 참조)

prompt_registry.md P-AUX-2 (SoT) 를 기반으로 Phase 10+ 활성화 시점의 설계 명세를 구체화한다 (Phase 9 는 미구현).

| 항목 | 명세 (Phase 10+) |
|---|---|
| **agent** | `brand_memory_extractor` (Phase 10+ 구현 — Phase 9 미구현, agent 파일/orchestration 연결 0) |
| **input** | `video_session_log` = feedback/selection 누적 이력 (선택/거절/수정 이벤트 — Phase 9 적재 경로가 candidate_knowledge pending 으로 선 축적) + `current_brand_memory` (brand_memory_entries 현 상태 — BrandMemoryRepo.list_for_brand) |
| **output** | `proposed_entries: [{ entry_type, content, confidence 0–1, source_evidence }]` — entry_type: preferred_tone \| avoid_phrase \| preferred_phrase \| success_pattern \| rejection_pattern |
| **규칙** (registry §System) | 1회성 결정 confidence ≤ 0.3 / 2회 이상 반복 ≥ 0.7 / 명시 선호 ≥ 0.9 / 기존 Brand Memory 충돌 항목 우선 제외 + 별도 표시 / 최대 5개 |
| **활성화 조건** | Phase 10+ MVP 운영 시작 **+** 피드백/선택 데이터 누적 N건 (운영 데이터 충분 시점 — 데이터 부족 시 confidence 신뢰도 ↓) |
| **승격 경로** | proposed_entries → (사용자 승인 or rag-update 5단계) → brand_memory_entries / approved_knowledge. **자동 승격 X** (NG12) |

- **input 흐름**: Phase 9 Slice 4 적재 경로(`feedback_to_candidate`)가 feedback/selection → candidate_knowledge(pending) 로 데이터를 선 축적 → Phase 10+ P-AUX-2 가 누적된 `video_session_log` 을 input 으로 소비. 즉 Phase 9 는 **데이터 누적 인프라 선 구축**, Phase 10+ 가 **추출 로직 활성화**.
- registry 가 단일 출처(SoT) — 본 표는 활성화 시점 설계 보존용 참조.

## Implementation (Slice 4 — 적재 경로)

Slice 4 는 P-AUX-2 활성화의 선행 인프라인 **feedback/selection → candidate_knowledge 적재 경로**를 구현한다 (자동 추출 agent 는 미구현).

### `backend/fastapi/rag/feedback_to_candidate.py` (신규)

| 함수 | 역할 | 경계 |
|---|---|---|
| `build_candidate_from_feedback(plan_id, event_type, *, reason, option_index, source_kind)` | feedback/selection → candidate_knowledge dict 구성 (저장 X). content = event_type 라벨 + option_index + reason. | **적재 전 PII 마스킹** (feedback_repo.mask_pii 재사용 — 단일 출처, T5). **status='pending' 고정**. |
| `enqueue_feedback_candidate(candidate, *, supabase_client, in_memory_store)` | candidate_knowledge pending INSERT (graceful — Supabase or in-memory list). | **status='pending' 강제** (어떤 경로로든 pending 아니면 pending 으로 reset — 자동 승격 차단). `rag.promotion.transition` **미호출** (NG12). |

- **source_kind** (db_schema §7.2 enum): `'user_feedback'` (like/dislike/reject/regenerate) / `'user_choice'` (select). `source_id` = plan_id (PII 삭제 요청 시 역추적 — T5 영역 9).
- **status='pending'**: Phase 7 5단계 파이프라인(pending → filtered → evaluated → approved → promoted) **진입점까지만**. promoted 진입 = rag-update Skill 5단계 절차 (Phase 11+).
- **PII 마스킹 (T5 이중 방어)**: ① feedback_repo 가 저장 전 마스킹한 reason(row) 사용 + ② build 시 content mask_pii 재적용. pending 단계는 RAG 노출 전이므로 다른 user 영향 0.
- **graceful**: Supabase INSERT 실패/미설정 시 in-memory list fallback (raise 0 — feedback 응답 차단 X).

### `backend/fastapi/routers/plans.py` (소폭)

- POST `/plans/{id}/feedback` 에서 `_feedback_repo.record()` **후** `build_candidate_from_feedback` + `enqueue_feedback_candidate` 를 **try/except graceful** 로 호출 — 적재 실패해도 feedback 응답 차단 X.
- `_candidate_store` (module-level in-memory list) = Supabase 미설정 시 fallback 저장소. Slice 3 endpoint 구조 보존 (응답/status 코드 변경 0).

### `backend/fastapi/rag/__init__.py` (export)

- `build_candidate_from_feedback` / `enqueue_feedback_candidate` / `SOURCE_KIND_FEEDBACK` / `SOURCE_KIND_CHOICE` / `PENDING_STATUS` export 추가. Phase 7 RAG 본체(promotion/retrieval/embedding/chunking/quality_filter/eval_rubric/llm_wiki) 0 변경 (additive).

## Non-activation (Phase 9 미활성화 경계 — NG1/NG12)

본 Slice 가 **하지 않은 것** (Phase 10+ 이관):

- ❌ **P-AUX-2 brand_memory_extractor agent 미구현** (NG1) — agent 파일 미생성 + orchestration 미연결 + 자동 추출 호출 0. 활성화는 Phase 10+ (MVP 운영 + 데이터 누적). 본 ADR 은 설계 명세 참조만 (실행 0).
- ❌ **자동 추출 미실행** — feedback/selection 이 자동으로 brand_memory_entries 로 변환되지 않음. proposed_entries 생성은 Phase 10+ agent 의 책임.
- ❌ **자동 승격 미호출** (NG12) — 적재는 candidate_knowledge **status='pending' 까지만**. `rag.promotion.transition` 호출 0 (pending → promoted 전이 X). 승격은 rag-update Skill 5단계 절차 (Phase 11+ 두 번째 트리거).
- ❌ **BrandMemoryRepo 자동 쓰기 X** — Slice 2 BrandMemoryRepo 는 수동/준비용 entry CRUD 만. feedback 으로부터의 자동 entry 생성 0.
- 검증: `test_brand_memory_prep.py` 에서 적재 후 status='pending' 고정 + promotion.transition 미호출 (status promoted 미진입) 확인.

## Constraints

- **agent 미구현 ★ (NG1)**: P-AUX-2 brand_memory_extractor agent 는 Phase 9 에서 구현하지 않음. 자동 추출 활성화는 Phase 10+ (MVP 운영 + 데이터 누적 후 — 사용자 결정 5). 본 ADR 은 설계 명세 참조만 (실행 0).
- **적재는 pending 까지만 (NG12)**: feedback/selection → candidate_knowledge 적재는 status='pending' 진입까지만. 자동 승격(pending → approved → promoted)은 rag-update Skill(Phase 11+ 두 번째 트리거). Phase 7 5단계 파이프라인 pending 진입점 정합.
- **BrandMemoryRepo 수동/준비용**: graceful entry CRUD(create/list)만 — 자동 추출 로직 미포함. db/client + 기존 repo 0 변경 (additive).
- **PII 차단 (security-review T5)**: feedback reason → candidate 적재 시 저장 전 마스킹(ADR-030 T1) 후 진입 + Phase 7 quality_filter 이중 방어 (pending 단계는 RAG 노출 전).
- **rag/{promotion,retrieval,...} 불변 (Phase 7 baseline)**: 적재 경로(feedback_to_candidate.py)만 신규 — Phase 7 RAG 본체 0 변경.

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| 준비만 (schema + 적재 경로 + ADR) | 사용자 결정 5 + 데이터 누적 후 자동 추출 정확도 ↑ + Phase 9 scope 절제 | Phase 9 자동 추출 구현 — NG1 (데이터 부족 + scope creep) |
| 적재 pending 까지만 | Phase 7 5단계 정합 + 자동 승격 위험 차단 (NG12) | 자동 승격 — RAG 오염 위험 (rag-update 절차 우회) |
| BrandMemoryRepo 수동/준비용 | graceful 인프라 선 구축 + 자동 추출 시 재사용 | repo 미생성 — Phase 10+ 인프라 0부터 |
| P-AUX-2 설계 명세 ADR (참조만) | Phase 10+ 활성화 시점 설계 보존 + 단일 출처 registry | ADR 미작성 — Phase 10+ 설계 재발명 |

## Verification

- `pytest backend/fastapi/tests/test_brand_memory_prep.py` (Slice 2 일부 + Slice 4 완성):
  - `build_candidate_from_feedback`: source_kind / status='pending' / content 구성 + **PII 마스킹** (이메일/전화 → [masked], T5)
  - `enqueue_feedback_candidate`: in-memory 적재 + Supabase mock INSERT + 실패 fallback (graceful) + status='pending' 검증
  - BrandMemoryRepo graceful add_entry/list (Slice 2 보강 — Supabase mock + in-memory)
  - **자동 승격 0 검증** (pending 고정, promoted 미진입 — `rag.promotion.transition` 미호출, NG12)
  - **P-AUX-2 agent 호출 0 검증** (자동 추출 미실행 — agent 파일 미생성, NG1)
- **기존 baseline 회귀 0** (additive — Phase 7 RAG 본체 불변, pytest 284 → 신규 additive).

## Cross-reference

- `ai_system/prompts/prompt_registry.md` **P-AUX-2 brand_memory_extractor** (§597 — 명세 SoT: input video_session_log + current_brand_memory / output proposed_entries / confidence 규칙). 본 ADR §P-AUX-2 설계 표는 활성화 시점 참조용.
- `docs/contracts/db_schema.md` **§7.2 candidate_knowledge** (source_kind enum 'user_feedback'/'user_choice' + status='pending' = Phase 7 5단계 진입점) + **§6 brand_memory_entries** (entry_type 5종 — 0005 등록) + §4.3 selected_plans + §5.2 feedback_events.
- `backend/fastapi/rag/promotion.py` (Phase 7 5단계 transition — 본 Slice 는 import/호출 0, pending 진입점만 정합). 승격은 rag-update Skill (Phase 11+).
- `backend/fastapi/rag/quality_filter.py` (PII 패턴 — feedback_repo.mask_pii 와 동일 출처 llm_security §3.2).

## References

- `docs/contracts/db_schema.md` §6 brand_memory_entries (정의 — 0005 등록) + §7.2 candidate_knowledge source_kind (pending 진입점)
- `backend/fastapi/rag/feedback_to_candidate.py` (Slice 4 — 적재 경로 구현)
- `ai_system/prompts/prompt_registry.md` P-AUX-2 brand_memory_extractor (명세 — 활성 Phase 9+, SoT)
- `docs/decisions/phase_7_rag_scope_evolution.md` (ADR-024 — Brand Memory Phase 9+ cross-ref)
- `docs/decisions/phase_9_feedback_selection.md` (ADR-030 — feedback/selection persistence)
- `.claude/skills/rag-update/SKILL.md` (5단계 승격 — Phase 11+ 두 번째 트리거)
- `meta/validations/2026-05-29_phase-9-pre-entry_self.md` §V3 (Brand Memory 준비 경계) + §V7 (feedback→candidate 적재)
- `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` §T5 (적재 PII 차단)
- `phases/active/phase-9-result-feedback/{goals,scope,non_goals,assumptions,multi_slice_plan}.md`
