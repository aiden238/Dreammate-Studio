# Phase 7 Pre-Entry Multi-LLM Validation — Self (Claude Code)

> 검증 모델: Claude Code (자가, 지침 참조)
> 검증 일자: 2026-05-29
> 검증 유형: formal (네 번째 정식 트리거 — Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째)
> 외부 검증: `2026-05-29_phase-7-pre-entry_external.md` (별도 placeholder)
> Skill 의무 트리거: **rag-design (★ 첫 정식 트리거 — Slice 1)** + multi-llm-validation (formal 네 번째)

## 검증 대상

1. ADR-024 5단계 채택 정합 확인 (candidate_knowledge pending → filtered → evaluated → approved → promoted)
2. chunk size 512 tokens 적절성 (vs 256 / 1024)
3. top-k=5 + threshold=0.7 정합 (정확도 vs recall trade-off)
4. OpenAI embedding model (`text-embedding-3-small`) 채택 (vs large / Custom)
5. graceful fallback 정신 (RAG 실패 시 plan 차단 X) — Phase 5 P-GRACEFUL-001 계승
6. LLM Wiki vs RAG 분리 명확 (static vs dynamic, 우선순위)
7. 5단계 자동/수동 승인 정책 (간이 eval rubric + hybrid 임계)

## 참조한 지침

- `harness/CLAUDE.md` § RAG, 메타 개선, 큰 결정
- `harness/AGENTS.md` (구현/QA 모델 라우터)
- `harness/docs/contracts/rag_data_contract.md` (현 상태 — Slice 2 갱신 예정)
- `harness/docs/contracts/llm_security_contract.md` (Step 1+2 자동 검사 + §6 RAG poisoning + §7 비용 보호)
- `harness/knowledge/rag/promotion_rule.md` (5단계 표준 + §9 Phase 1 마일스톤)
- `harness/knowledge/rag/retrieval_policy.md` (top_k + threshold + isolation)
- `harness/knowledge/rag/quality_filter.md` (4종 필터)
- `harness/knowledge/rag/metadata_schema.md` (필수 필드: brand_id / source_kind / promoted_at / quality_score / pii_masked)
- `harness/knowledge/llm_wiki/index.md` (LLM Wiki vs RAG 분리 baseline)
- `harness/docs/decisions/phase_7_rag_scope_evolution.md` (ADR-024)
- `harness/docs/decisions/phase_5_supabase_adoption.md` (ADR-020 — Supabase pgvector baseline)
- `harness/meta/patterns.md` (P-GRACEFUL-001, P-CONTRACT-FIRST-001, P-X1-EFFECT-001, P-VALIDATION-FORMAL-001)
- Phase 5/5.5 closing_notes.md (Phase 7 진입 체크리스트)
- Phase 7 entry files (goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan)
- `.claude/skills/rag-design/SKILL.md` (★ 첫 정식 트리거 절차)
- `.claude/skills/multi-llm-validation/SKILL.md` (formal 절차)

## 검증 결과 (V1~V7)

### V1. ADR-024 5단계 채택 정합 — PASS

- **사용자 결정 4 확인**: Phase 5.5에서 사용자 명시 — `candidate_knowledge` 5단계 MVP 전부 구현 (pending → filtered → evaluated → approved → promoted).
- **ADR-024 §1 (Phase 7 RAG Lite scope)** 그대로 적용:
  - Stage 1: `pending` — 사용자 입력 / LLM Wiki 신규 항목 / 외부 시드 진입
  - Stage 2: `filtered` — quality_filter 통과 (PII 마스킹 + 인젝션 차단 + 광고적 표현 + 길이 + 언어 + 중복)
  - Stage 3: `evaluated` — eval rubric 평가 (Phase 9+ 정식 eval 도입 전까지 간이 rubric)
  - Stage 4: `approved` — 사용자 또는 자동 (간이) 승인
  - Stage 5: `promoted` — `rag_chunks` (또는 `approved_knowledge`) 테이블 승격 + retrieval 활성
- **잠재 risk**:
  - 5단계 모두 자동 transition 시 quality ↓ (false positive 누적)
  - eval_score 0.85 자동 승격 임계 (ADR-024 명시) — 사용자 데이터 누적 전에는 비관적 검증 부족
- **권장**:
  - V7에서 자동/수동 hybrid 정책 명시 (ADR-026에 반영)
  - Phase 11+ 사용자 데이터 누적 후 임계 재조정 (ADR-024 §A 확대 지점)
- **확정 결정 [18] 정합**: RAG candidate_knowledge 5단계 승격 파이프라인 MVP 구현 — 본 Phase 7에서 실현.

### V2. chunk size 512 tokens — PASS

- **현 상태**: ADR-024 §2 "chunk size 표준 결정: 500자 + overlap 100자" 명시 (글자 기준). 본 Phase 7에서 token 기준으로 재정의.
- **Phase 7 결정 안**:
  - **size**: 512 tokens (영상기획 도메인 적정 — 한 문장~짧은 문단)
  - **overlap**: 50 tokens (10% — 문맥 보존)
  - **strategy**: 문장 boundary 우선 + fallback에 token boundary
- **대안 비교**:
  - **A. 256 tokens** (반각): fragment 너무 작음 → context 손실 (단점)
  - **B. 512 tokens** (채택): 영상기획 hook + 한 문단 적정 + retrieval recall/precision 균형
  - **C. 1024 tokens** (배수): context wide → embedding 정확도 ↓ + top-k=5에서 token 5120개 → LLM context budget 압박
- **잠재 risk**:
  - 영상기획 hook 패턴은 짧은 문장이 다수 → 256 검토 가치
  - 한국어 token 효율 (영어 대비 1.5~2x token) → 효과 chunk 크기 작아짐
- **권장**:
  - ADR-025에 512 기본 + overlap 50 + 문장 boundary 우선 명시
  - Phase 9+ eval-run 정식화 후 256/512/1024 비교 실험 권장
  - 한국어/영어 분리 처리는 ADR-025에 명시 X (Phase 21+ 검토)

### V3. top-k=5 + threshold=0.7 — PASS

- **현 상태**: ADR-024 §2 "top-k=5 (MVP), relevance threshold cosine similarity ≥ 0.7~0.75" 명시.
- **Phase 7 결정 안**:
  - **top_k**: 5 (영상기획안 3개 생성에 적정 context — 3 plan × ~1~2 chunks)
  - **threshold**: 0.7 (cosine similarity 표준 cutoff)
  - **method**: pgvector cosine distance (`<=>` operator)
- **trade-off 분석**:
  - top_k=3: precision ↑, recall ↓ (3-plan 생성 시 plan별 1 chunk 부족 가능)
  - top_k=5 (채택): 균형
  - top_k=10: recall ↑, LLM context budget 압박 + noise ↑
  - threshold=0.65: recall ↑, false positive ↑
  - threshold=0.7 (채택): 표준
  - threshold=0.75: precision ↑, recall ↓ (candidate_knowledge 미숙성 단계에서 0 results 빈도 ↑)
- **잠재 risk**:
  - threshold 너무 높으면 recall ↓ → 영상기획안 context 부족
  - top_k=5에서 brand_id 격리 미적용 시 다른 brand 누출 → retrieval_policy.md §brand_id 격리 강제 필요
- **권장**:
  - ADR-025에 0.65~0.75 범위 명시 + Phase 9+ tuning
  - retrieval_policy.md (rag-update Skill Slice 4)에서 brand_id 격리 명시 (현재 ADR-024 cross-ref)
  - env 변수 `RAG_TOP_K`, `RAG_THRESHOLD` 노출 (operational tuning 가능)

### V4. OpenAI embedding (text-embedding-3-small) — PASS

- **현 상태**: ADR-024 §2 "embedding 모델: text-embedding-3-small (dim=1536, 배치 10개)" 명시.
- **Phase 7 결정 안**:
  - **model**: `text-embedding-3-small`
  - **dim**: 1536
  - **batch_size**: 10 (Phase 7 MVP — Phase 9+ 동적 조정)
- **채택 근거**:
  - 비용 효율적: $0.02/1M tokens (large 대비 1/6.5)
  - Phase 6 OpenAI baseline 정합 (gpt-4o-mini, gpt-4o)
  - 영상기획 도메인 한국어 + 영어 모두 충분 (다국어 지원)
- **대안 비교**:
  - `text-embedding-3-large` (3072 dim, $0.13/1M tokens): 더 정확하지만 비용 ↑ + dim 2x → pgvector ivfflat index 빌드 시간/공간 ↑
  - Custom embedding (NG2 Phase 21+): MVP 단계에서 미적용
  - 다국어 전용 (multilingual-e5-large 등): self-hosted 운영 부담 ↑
- **잠재 risk**:
  - Phase 21+ Custom embedding (NG2 / ADR-024 §B)으로 교체 시 dim 변경 → embedding 전체 재계산 + migration 필요
  - OpenAI API outage 시 embedding 불가 → graceful fallback 필요 (V5)
  - 비용 폭증 risk (사용자 입력 + LLM Wiki + 외부 시드 누적 시 월 비용 ↑)
- **권장**:
  - ADR-025에 `RAG_EMBEDDING_MODEL` env 변수 명시 + 교체 가능 구조
  - graceful: embedding 실패 시 None + warning (V5와 정합)
  - Phase 11+ cost-review Skill로 embedding 비용 추적 (현 Phase 외)

### V5. graceful fallback 정신 — PASS

- **현 상태**: Phase 5 P-GRACEFUL-001 패턴 정식 입증 (Supabase 미설정 시 in-memory dict 회귀 0).
- **Phase 7 결정 안**:
  - RAG 실패 시 plan 생성 차단 **X** (validation.warnings에 `rag_unavailable` 추가)
  - retrieval 실패 (pgvector 미설정 / Supabase outage): 빈 list + warning
  - embedding 실패 (OpenAI outage / quota 초과): chunk 저장 X + warning
  - quality_filter 실패 (PII detector library error): item을 `pending` 유지 + reason 메타
- **Phase 5 패턴 계승**:
  - P-GRACEFUL-001 (Supabase fallback)
  - Phase 6 ADR-019 Rewriter graceful (Pydantic 실패 시 raw dict fallback)
- **잠재 risk**:
  - RAG 실패 빈도가 높으면 plan 품질 ↓ (회피 — sustained outage 발견 시 alarm 필요)
  - `rag_unavailable` warning이 응답 schema에 영향 줄 수 있음 (Body.validation.warnings)
  - graceful 후 다음 단계 (chunking 후 embedding 실패) 시 partial state 남을 수 있음 → idempotent transition 필요
- **권장**:
  - ADR-026에 graceful 정책 명시 + transition idempotent 요구 (재시도 가능)
  - validation.warnings 표준 마커 정의 (`rag_unavailable`, `embedding_failed`, `chunking_failed` 등)
  - Phase 9+ eval-run에서 graceful 비율 측정 (sustained outage 감지)
  - llm_security_contract §7 비용 보호 정합 (RAG 실패 시 비용 0)

### V6. LLM Wiki vs RAG 분리 — PASS

- **현 상태**: ADR-024 §3 LLM Wiki (정적, `knowledge/llm_wiki/`) vs RAG (동적, `candidate_knowledge` → `rag_chunks`) 분리 명시.
- **Phase 7 결정 안**:
  - **LLM Wiki** = 정적 (영상기획 패턴, hook 유형, 타겟 페르소나, contract 정합 baseline)
  - **RAG** = 동적 (사용자 입력 + 외부 시드 + Phase 11+ 자동 promotion)
  - **우선순위**: RAG > LLM Wiki (동적이 최신)
  - **conflict 시**: RAG 결과 우선 + LLM Wiki는 보조
  - **구현**:
    - LLM Wiki: `rag/llm_wiki.py` (Slice 4) — in-memory dict from `knowledge/llm_wiki/`
    - RAG: `rag/retrieval.py` (Slice 3) — pgvector cosine
- **분리 근거** (ADR-024):
  - LLM Wiki = prompt-injection 무관 (시스템 신뢰 — `knowledge/llm_wiki/` git-tracked)
  - RAG = 사용자 입력 신뢰 단계별 필터 (5단계 + quality_filter)
- **잠재 risk**:
  - LLM Wiki와 RAG 결과 conflict 시 정책 부재 → V6 권장에서 우선순위 명시
  - LLM Wiki를 RAG에 흡수하려는 충동 (scope creep) → 분리 baseline 강제
  - rag-design Skill SKILL.md "경계가 모호한 항목은 표로 정리, 사용자 결정 요청" 명시 — 본 검증에서는 분리 baseline 채택, 모호 항목 0
- **권장**:
  - ADR-025에 우선순위 명시 (RAG > LLM Wiki)
  - agents/rag.py 통합 시 LLM Wiki + RAG 양쪽 조회 → merge 정책 명시
  - Slice 4 통합 시 conflict 케이스 test_rag_integration.py에 추가

### V7. 5단계 자동/수동 승인 정책 — PASS

- **현 상태**: ADR-024 §1 "자동 승격 조건: eval_score ≥ 0.85 AND dimensions 모두 ≥ 3 AND source_kind ∈ {final_output, manual, external_seed} AND same_pattern_count ≥ 3 AND pii_masked = false" 명시.
- **Phase 7 결정 안 (Hybrid 정책)**:
  - `pending → filtered`: **자동** (quality_filter 통과 조건 — PII 0 + 인젝션 0 + 광고적 표현 0 + 길이 OK + 언어 OK + 중복 0)
  - `filtered → evaluated`: **자동** (eval_rubric 종합 점수 ≥ 0.6)
  - `evaluated → approved`: **자동 + 수동 hybrid**
    - 종합 점수 ≥ 0.8 → 자동 approved
    - 0.6 ≤ 점수 < 0.8 → 수동 승인 대기
    - 점수 < 0.6 → evaluated 상태 유지 (재시도)
  - `approved → promoted`: **자동** (approved_knowledge 테이블 이동 + retrieval 활성)
- **간이 eval rubric** (Phase 9+ 정식화 전):
  - **relevance** (0~1): 영상기획 도메인 관련성 (도메인 키워드 매칭)
  - **clarity** (0~1): 문장 명료성 (길이 + 명료성 heuristic)
  - **safety** (0~1): PII/인젝션 재검사
  - **overall**: 평균 (3 dim 합 / 3)
- **자동 비율 목표** (ADR-026):
  - 자동 (evaluated → approved): 70%+
  - 수동 승인: 20~30%
  - 거부 (재시도): <10%
- **잠재 risk**:
  - 자동 비율 너무 높으면 quality ↓ (false positive)
  - 0.8 임계는 보수적 — Phase 11+ 데이터 누적 후 재조정 권장
  - ADR-024 명시 자동 승격 조건 (eval_score ≥ 0.85 AND ...)은 Phase 11+ "자동 promotion 활성화" 시점 임계 (현 Phase 7 hybrid 0.8과 다름) — ADR-026 §자동 비율 목표에 명시
- **권장**:
  - ADR-026에 hybrid 임계 명시 (0.8/0.6) + Phase 11+ 재평가
  - 수동 승인 endpoint: `POST /api/v1/rag/promote` (Slice 4 선택 구현)
  - test_rag_promotion.py에 5단계 transition 5+ 케이스 (hybrid 경계 포함)
  - knowledge/rag/promotion_rule.md §9 Phase 1 마일스톤 정합 확인

## 종합 판정

**Phase 7 entry 허용 — 7/7 PASS (V1~V7)**

| ID | 항목 | 결과 | 후속 조치 |
|---|---|---|---|
| V1 | ADR-024 5단계 채택 정합 | PASS | ADR-026 5단계 transition 명시 |
| V2 | chunk size 512 tokens | PASS | ADR-025 chunking §명시 |
| V3 | top-k=5 + threshold=0.7 | PASS | ADR-025 retrieval §명시 + env 변수 |
| V4 | OpenAI embedding | PASS | ADR-025 embedding §명시 + `RAG_EMBEDDING_MODEL` env |
| V5 | graceful fallback | PASS | ADR-026 graceful §명시 + warnings 표준 마커 |
| V6 | LLM Wiki vs RAG 분리 | PASS | ADR-025 분리 + 우선순위 §명시 |
| V7 | 5단계 hybrid 승인 정책 | PASS | ADR-026 promotion logic + hybrid 임계 §명시 |

다음: Slice 2 sub-agent dispatch — contract-change (rag_data_contract.md 갱신) + RAG 5단계 schema/migration/promotion/quality_filter/eval_rubric.

## Contract gap analysis (현 상태 vs Phase 7 목표)

| 항목 | docs/contracts | 실 backend | 차이 | Slice 작업 |
|---|---|---|---|---|
| RAG 5단계 stage | rag_data_contract.md (현 상태 — 5단계 명시 약함) | `agents/rag.py` stub | stage ENUM 정식 등록 + promotion_history JSONB schema | Slice 2 contract-change + 0004 migration |
| Retrieval 정책 | retrieval_policy.md (knowledge/rag/) | 미구현 | pgvector cosine + top-k=5 + threshold=0.7 정식 | Slice 3 rag/retrieval.py + ADR-025 |
| Chunking 표준 | promotion_rule.md §2.4 (500자 글자 기준) | 미구현 | 512 tokens 표준 (Phase 7 본 ADR-025 재정의) | Slice 3 rag/chunking.py + ADR-025 |
| Embedding | promotion_rule.md §2.5 (text-embedding-3-small) | 미구현 | OpenAI wrapper + graceful | Slice 3 rag/embedding.py + env 변수 |
| Quality filter | quality_filter.md (4종 명시) | 미구현 | PII + 인젝션 + 광고 + 길이/언어 | Slice 2 rag/quality_filter.py + tests |
| Eval rubric | (없음 — Phase 9+ 정식) | 미구현 | 간이 3 dim rubric (Phase 9+ deprecated 예정) | Slice 2 rag/eval_rubric.py + ADR-026 |
| LLM Wiki | knowledge/llm_wiki/index.md (정적 baseline) | 미구현 wrapper | rag/llm_wiki.py in-memory cache + 우선순위 정책 | Slice 4 rag/llm_wiki.py + ADR-025 |
| agents/rag.py | (Phase 1 stub 또는 simple wrapper) | Phase 1 baseline | retrieval.search() 호출 통합 + graceful | Slice 4 agents/rag.py 수정 |
| RAG mgmt API | api_contract.md /api/v1/rag/* 미명시 | 미구현 | (선택) POST /rag/promote + GET /rag/candidates | Slice 4 routers/rag.py (선택) + api_contract 갱신 |

## 외부 검증 연계

self-validation 단일 모델 (Claude Code) 결과. 외부 검증 결과 (GPT/Gemini)는 `2026-05-29_phase-7-pre-entry_external.md` placeholder에 사용자가 외부 진행 후 채울 수 있음.

Phase 7은 RAG architecture 영향 큰 phase (chunking + embedding + retrieval + 5단계 promotion) → 외부 검증 권장. 단 Phase 4.5/6/5/5.5 패턴 계승으로 external placeholder는 **사용자 외부 진행 권장** 형식 유지. self-validation V1~V7 PASS + Phase 5.5 self-strengthen V-form sub-pattern 가능성 명시. Phase 7 entry 진행 가능.

두 결과 차이 항목 발견 시:
- Phase 7 진행 중 `notes.md`에 기록
- Slice 5 회고 §개선 제안 반영
- Critical 차이 (chunk size / embedding model / 5단계 흐름 변경 등) 시 Slice 2 진입 전 사용자 알림

## Cross-reference (이전 Phase validations)

- Phase 4.5 self: `meta/validations/2026-05-28_phase-4.5-pre-entry_self.md` (V1~V4 PASS — 첫 formal)
- Phase 4.5 external: `meta/validations/2026-05-28_phase-4.5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 6 self: `meta/validations/2026-05-29_phase-6-pre-entry_self.md` (V1~V5 PASS — 두 번째 formal)
- Phase 6 external: `meta/validations/2026-05-29_phase-6-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 5 self: `meta/validations/2026-05-29_phase-5-pre-entry_self.md` (V1~V6 PASS — 세 번째 formal)
- Phase 5 external: `meta/validations/2026-05-29_phase-5-pre-entry_external.md` (placeholder + Phase 5.5 self-strengthen V-form)
- Phase 7 self: 본 문서 (V1~V7 PASS — 네 번째 formal)
- Phase 7 external: `meta/validations/2026-05-29_phase-7-pre-entry_external.md` (placeholder)

## Skill 트리거 기록

- **multi-llm-validation**: 네 번째 formal 트리거 (Phase 4.5 첫 + Phase 6 둘째 + Phase 5 셋째 + Phase 7 넷째) → P-VALIDATION-FORMAL-001 정식 패턴 입증 강화 (4회 누적)
- **rag-design**: ★ 첫 정식 트리거 (별도 §§ ADR-025 본문에 결과 통합) → unused → active 전환
- **phase-start**: 9번째 트리거 (Phase 1+2+3+4+4.5+6+5+5.5+7)
