# ADR-031 — Phase 9 Brand Memory 준비 (P-AUX-2 설계, agent 미구현 Phase 10+)

> Date: 2026-05-29
> Status: Accepted
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
  - BrandMemoryRepo graceful create/list (Supabase mock + in-memory)
  - feedback/selection → candidate_knowledge 적재 (source_kind='user_feedback'/'user_choice' + status='pending')
  - **자동 승격 0 검증** (pending 고정, promoted 미진입 — NG12)
  - **P-AUX-2 agent 호출 0 검증** (자동 추출 미실행 — NG1)
- **기존 baseline 회귀 0** (additive — Phase 7 RAG 본체 불변).

## References

- `docs/contracts/db_schema.md` §6 brand_memory_entries (정의 — 0005 등록) + §7.2 candidate_knowledge source_kind (pending 진입점)
- `ai_system/prompts/prompt_registry.md` P-AUX-2 brand_memory_extractor (명세 — 활성 Phase 9+, SoT)
- `docs/decisions/phase_7_rag_scope_evolution.md` (ADR-024 — Brand Memory Phase 9+ cross-ref)
- `docs/decisions/phase_9_feedback_selection.md` (ADR-030 — feedback/selection persistence)
- `.claude/skills/rag-update/SKILL.md` (5단계 승격 — Phase 11+ 두 번째 트리거)
- `meta/validations/2026-05-29_phase-9-pre-entry_self.md` §V3 (Brand Memory 준비 경계) + §V7 (feedback→candidate 적재)
- `meta/security_reviews/2026-05-29_phase-9-feedback-pii.md` §T5 (적재 PII 차단)
- `phases/active/phase-9-result-feedback/{goals,scope,non_goals,assumptions,multi_slice_plan}.md`
