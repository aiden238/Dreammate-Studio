# ADR-025 — Phase 7 RAG Architecture (rag-design Skill 첫 정식)

> Date: 2026-05-29
> Status: Accepted
> Phase: 7 Slice 1 (Pre-Entry)
> Related: ADR-024 (Phase 5.5 RAG scope evolution), ADR-020 (Supabase pgvector), ADR-026 (Phase 7 promotion logic)
> Skill Trigger: **rag-design ★ 첫 정식 트리거** (Phase 7 entry — RAG architecture 결정)
> Sub-agent: Phase 7 Slice 1 dispatch

---

## Context

Phase 7 RAG Lite scope (ADR-024 기반): candidate_knowledge 5단계 MVP + retrieval + chunking + embedding + LLM Wiki vs RAG 분리.

ADR-024에서 scope를 결정했고, 본 ADR에서 구체적 architecture 결정 + alternative 비교 + 영향 받는 contract 명시.

본 ADR은 **rag-design Skill 첫 정식 트리거** 결과 — Phase 7 entry baseline 문서.

### rag-design Skill 절차 적용 (8단계)

#### 1. 현재 자산 로드 (Skill §1)

| 파일 | 영역 |
|---|---|
| `knowledge/rag/retrieval_policy.md` | retrieval 정책 (top_k / brand_id / re-rank / dedupe) |
| `knowledge/rag/metadata_schema.md` | 필수 필드 (brand_id / source_kind / promoted_at / quality_score / pii_masked) |
| `knowledge/rag/quality_filter.md` | 4종 필터 (PII / 인젝션 / 광고 / 길이/언어/중복) |
| `knowledge/rag/promotion_rule.md` | 5단계 표준 + §9 Phase 1 마일스톤 |
| `knowledge/llm_wiki/index.md` | LLM Wiki 정적 baseline |
| `docs/contracts/rag_data_contract.md` | rag_data 단일 출처 (Slice 2 갱신 예정) |
| `docs/contracts/llm_security_contract.md` | §6 RAG poisoning + §7 비용 보호 |
| `docs/decisions/phase_5_supabase_adoption.md` | ADR-020 pgvector baseline |
| `docs/decisions/phase_7_rag_scope_evolution.md` | ADR-024 (본 ADR baseline) |

#### 2~5. retrieval / metadata / chunking / quality_filter 점검

본 §Decision에서 결정 상세 명시.

#### 6. 새 소스 도입 검토

Phase 7 MVP는 신규 외부 소스 도입 X (사용자 입력 + LLM Wiki 정적 변환만). 신규 시드 데이터셋 (`knowledge/datasets/seed_youtube_planning.csv` 등) 도입은 Phase 7+ 별도 결정 (NG6 — Hybrid retrieval 결정 시 동반).

#### 7. LLM Wiki vs RAG 분리 재검토

본 §Decision §3 명시. 경계 모호 항목 0 (확정).

#### 8. 변경 제안서

본 ADR이 변경 제안서 본문 역할. Slice 2 contract-change Skill로 라우팅 (`docs/contracts/rag_data_contract.md` 갱신).

---

## Decision

### 1. Chunking (rag-design §4)

| 항목 | 값 | 근거 |
|---|---|---|
| **size** | **512 tokens** | 영상기획 도메인 적정 (한 문장~짧은 문단) |
| **overlap** | **50 tokens (10%)** | 문맥 보존 + retrieval recall ↑ |
| **strategy** | **문장 boundary 우선, fallback에 token boundary** | 의미 단위 보존 |
| **language** | 한국어 + 영어 혼재 OK | tiktoken-style tokenizer 사용 |

#### Alternative 비교

| 옵션 | 장점 | 단점 | 채택? |
|---|---|---|---|
| 256 tokens | precision ↑ | fragment 너무 작음, context 손실 | ❌ |
| **512 tokens** | 균형 (recall + precision) | 영상기획 hook 짧은 문장 일부 손실 | ✅ |
| 1024 tokens | context wide | embedding 정확도 ↓, top-k=5에서 token 5120 LLM context 압박 | ❌ |

#### ADR-024 §2 (500자 글자 기준)과의 관계

ADR-024 §2 "chunk size 500자 + overlap 100자" (글자 기준). 본 ADR-025에서 **token 기준으로 재정의** (`text-embedding-3-small` 입력 단위에 정합).

대략 1 token ≈ 2~3 한국어 글자 → 512 tokens ≈ 1000~1500 한국어 글자. ADR-024 500자보다 다소 크지만 한국어 token 효율을 고려해 적정.

### 2. Embedding (rag-design §6 새 소스 검토에 포함)

| 항목 | 값 | 근거 |
|---|---|---|
| **model** | **`text-embedding-3-small`** (OpenAI) | 비용 효율 + Phase 6 OpenAI baseline 정합 |
| **dim** | **1536** | text-embedding-3-small native |
| **batch_size** | **10** (Phase 7 MVP) | Phase 9+ 동적 조정 가능 |
| **env 변수** | **`RAG_EMBEDDING_MODEL`** | 교체 가능 (Phase 21+ Custom NG2 대비) |

#### Alternative 비교

| 옵션 | 장점 | 단점 | 채택? |
|---|---|---|---|
| **`text-embedding-3-small`** | 비용 1/6.5 + 한국어/영어 OK + 1536 dim | 다국어 전용 모델 대비 정확도 약 5% ↓ | ✅ |
| `text-embedding-3-large` (3072 dim) | 정확도 ↑ | 비용 ↑, pgvector ivfflat 빌드 시간/공간 2x | ❌ MVP |
| `multilingual-e5-large` (self-hosted) | 한국어 특화 | 운영 부담 ↑↑ (GPU 인프라) | ❌ MVP |
| Custom embedding | Phase 21+ NG2 — MVP 영역 외 | — | ❌ |

#### Graceful

- embedding 실패 시 None + warning (chunk 저장 X)
- OpenAI API outage 시: `validation.warnings` = `["embedding_failed"]` (V5 정합)

### 3. Retrieval (rag-design §2)

| 항목 | 값 | 근거 |
|---|---|---|
| **method** | **pgvector cosine similarity** (`<=>` operator) | Supabase 기본 + ADR-020 정합 |
| **top_k** | **5** | 3-plan 생성 시 plan별 ~1~2 chunks 적정 |
| **threshold** | **0.7** (cosine similarity) | 표준 cutoff (0.65~0.75 범위) |
| **env 변수** | **`RAG_TOP_K`, `RAG_THRESHOLD`** | operational tuning 가능 |
| **brand_id 격리** | **retrieval 단계에서 강제** (WHERE brand_id = $brand_id) | rag-design Skill SKILL.md §2 "isolation 단계 누락" 자주 발생하는 실수 회피 |
| **dedupe** | top-k 내 source_candidate_id 중복 제거 | rag-design §2 isolation·re-rank·dedupe 함께 |
| **re-rank** | **미적용** (Phase 9+ NG5) | MVP scope |

#### Alternative 비교

| 옵션 | 장점 | 단점 | 채택? |
|---|---|---|---|
| top_k=3 | precision ↑ | recall ↓, plan별 1 chunk 부족 | ❌ |
| **top_k=5** | 균형 | — | ✅ |
| top_k=10 | recall ↑ | noise ↑, LLM context 압박 | ❌ |
| threshold=0.65 | recall ↑ | false positive ↑ | ❌ |
| **threshold=0.7** | 표준 | — | ✅ |
| threshold=0.75 | precision ↑ | recall ↓, 미숙성 단계 0 results 빈도 ↑ | ❌ |
| BM25 hybrid | sparse + dense | 복잡도 ↑ | ❌ NG6 Phase 7+ |
| Cross-encoder re-rank | precision ↑↑ | 비용 ↑ | ❌ NG5 Phase 9+ |

### 4. LLM Wiki vs RAG 분리 (rag-design §7)

| 항목 | LLM Wiki | RAG |
|---|---|---|
| 타입 | 정적 (static) | 동적 (dynamic) |
| 위치 | `knowledge/llm_wiki/` (git-tracked) | `candidate_knowledge` → `approved_knowledge` DB |
| 신뢰 | 시스템 신뢰 (prompt-injection 무관) | 사용자 입력 신뢰 단계별 필터 (5단계 + quality_filter) |
| 구현 | `rag/llm_wiki.py` (Slice 4) — in-memory dict | `rag/retrieval.py` (Slice 3) — pgvector cosine |
| 갱신 | git commit | promotion (5단계) |
| 우선순위 | **2 (보조)** | **1 (우선)** |

#### 우선순위 정책: **RAG > LLM Wiki**

- **근거**: 동적이 최신 (사용자 데이터 누적 반영)
- **conflict 시**: RAG 결과 우선 + LLM Wiki는 보조 (fallback context)
- **merge 정책**: agents/rag.py (Slice 4)에서 RAG top-k=5 호출 → 결과 부족 (0 results) 시 LLM Wiki lookup fallback
- **경계 모호 항목**: 0 (확정 — 정적 vs 동적 명확)

#### rag-design Skill 자주 발생하는 실수 회피

- ❌ "LLM Wiki를 RAG에 흡수" (단일 source) → 분리 baseline 강제
- ❌ "RAG 결과 0일 때 LLM Wiki 무시" → fallback 정책 명시
- ❌ "단독 판단으로 경계 결정" (rag-design 금지 사항) → 본 ADR에서 baseline + Phase 9+ 재검토 시 사용자 또는 multi-llm-validation 트리거

### 5. Graceful Fallback (V5 + Phase 5 P-GRACEFUL-001 계승)

| 실패 유형 | 동작 | warning marker |
|---|---|---|
| retrieval 실패 (pgvector 미설정 / Supabase outage) | 빈 list 반환 + warning | `rag_unavailable` |
| embedding 실패 (OpenAI outage / quota 초과) | chunk 저장 X + warning | `embedding_failed` |
| chunking 실패 (tokenizer error) | item을 `pending` 유지 + reason 메타 | `chunking_failed` |
| quality_filter 실패 (PII detector error) | item을 `pending` 유지 + reason 메타 | `quality_filter_failed` |
| LLM Wiki lookup 실패 | RAG only로 진행 | `llm_wiki_unavailable` |

#### 통합 정책

- **plan 생성 차단 X** — RAG 실패는 graceful (Body.validation.warnings에 마커 추가)
- **transition idempotent** — partial state에서 재시도 가능 (promotion_history append-only)
- Phase 9+ eval-run에서 graceful 비율 측정 (sustained outage 감지)

---

## Metadata Schema (rag-design §3 — 필수 필드)

`candidate_knowledge.metadata JSONB`:

```json
{
  "brand_id": "string | null",  // 필수 (retrieval isolation)
  "source_kind": "user_input | llm_wiki | external_seed | final_output | manual | generated",  // 필수
  "promoted_at": "ISO8601 string | null",  // 필수 (promoted 단계 진입 시점)
  "quality_score": 0.0,  // 필수 (eval_rubric overall, 0.0~1.0)
  "pii_masked": false,  // 필수 (quality_filter 통과 시 true)
  "same_pattern_count": 0,  // ADR-024 자동 승격 조건 — Phase 11+ 활성
  "language": "ko | en | mixed",  // 검색 isolation 보조
  "domain": "string | null"  // Phase 8+ 4계층 Domain 정합
}
```

`approved_knowledge.metadata JSONB` 동일 + `source_candidate_id` (FK).

`promotion_history JSONB` (candidate_knowledge 컬럼):

```json
[
  {"from": "pending", "to": "filtered", "at": "ISO8601", "reason": "string"},
  {"from": "filtered", "to": "evaluated", "at": "ISO8601", "scores": {...}, "overall": 0.0},
  ...
]
```

(상세 schema는 ADR-026 §promotion_history JSONB schema 참조.)

---

## Constraints

- **Supabase pgvector extension 사용** (Phase 5 ADR-020 baseline)
- **mock 환경 unit test 가능** (실 Supabase / OpenAI 호출 없이)
- **Phase 11+ 자동 promotion 활성 가능 구조 유지** (promotion_history append-only)
- **Phase 21+ Custom embedding 교체 가능 구조** (`RAG_EMBEDDING_MODEL` env)
- **graceful fallback** — plan 생성 차단 X (V5)
- **brand_id 격리** retrieval 단계 강제 (rag-design §2)
- **promotion_history append-only** (이력 보존)
- **LLM Wiki vs RAG 분리 baseline** (단일 source 흡수 금지)
- **chunk size token 기준** (ADR-024 글자 기준 재정의)
- **NG2 / NG3 / NG4 / NG5 / NG6 / NG7 / NG10 / NG14 / NG15** Phase 7 non_goals.md 정합 — 본 ADR에서도 절대 포함 X

---

## Trade-offs

- **Lite scope 우선** → Hybrid (BM25) / Re-ranking / Custom embedding은 별도 phase 이관 (NG5/NG6/NG2)
- **1536 dim 채택** → 추후 3072 dim (text-embedding-3-large) 또는 Custom 교체 시 embedding 전체 재계산 + migration 필요
- **threshold=0.7** → recall vs precision 균형, Phase 9+ eval-run에서 tuning 필요
- **간이 eval rubric** (ADR-026) → Phase 9+ 정식 rubric (golden_set 기반)으로 deprecated 예정
- **자동 비율 70% 목표** (hybrid) → 너무 높으면 quality ↓, 너무 낮으면 사용자 부담 ↑
- **brand_id 격리 retrieval 단계 강제** → Phase 8+ 4계층 데이터 모델 활성 전까지 일부 항목은 brand_id=null 운영 (격리 효과 제한적)
- **RAG > LLM Wiki 우선순위** → LLM Wiki가 더 정확한 baseline 패턴인 경우 누락 risk (Phase 9+ conflict 측정 필요)

---

## Verification

### Slice 2 (RAG 5단계 schema + core) — pytest

- `test_rag_promotion.py`: 5단계 transition 5+ 케이스 (pending → filtered → evaluated → approved → promoted)
- `test_rag_quality_filter.py`: PII + 인젝션 + 광고 + 길이/언어/중복 3+ 케이스
- `test_rag_eval_rubric.py` (또는 test_rag_promotion 흡수): 3 dim + overall

### Slice 3 (Retrieval + Embedding) — pytest

- `test_rag_chunking.py`: 512 tokens + overlap 50 + 문장 boundary 3+ 케이스
- `test_rag_embedding.py`: OpenAI mock + graceful 2+ 케이스
- `test_rag_retrieval.py`: pgvector mock + top-k=5 + threshold=0.7 + brand_id 격리 3+ 케이스

### Slice 4 (LLM Wiki + 통합) — pytest

- `test_rag_integration.py`: end-to-end (chunking → embedding → promotion 5단계 → retrieval round-trip) 3+ 케이스
- LLM Wiki vs RAG 우선순위 case (RAG 결과 있을 때 RAG 우선)
- LLM Wiki fallback case (RAG 0 results 시 LLM Wiki lookup)
- graceful failure 통합 case (3개 실패 유형)

### Slice 5 (Close) — smoke + scenario_sim

- `scripts/smoke_test_phase_7.ps1`: 13/13 (Phase 5 12 + RAG 1 추가)
- `scripts/scenario_simulation.ps1` v3: 15/15 (Phase 6 v2 10 + Phase 7 5 추가 — S11~S15)

---

## References

- ADR-024 (`docs/decisions/phase_7_rag_scope_evolution.md`) — Phase 7 RAG scope evolution
- ADR-026 (`docs/decisions/phase_7_promotion_logic.md`) — Phase 7 5단계 promotion logic (cross-ref)
- ADR-020 (`docs/decisions/phase_5_supabase_adoption.md`) — Supabase pgvector baseline
- `meta/validations/2026-05-29_phase-7-pre-entry_self.md` §V1~V7
- `knowledge/rag/promotion_rule.md` — 5단계 표준
- `knowledge/rag/retrieval_policy.md` — top_k + threshold + isolation 표준
- `knowledge/rag/quality_filter.md` — 4종 필터
- `knowledge/rag/metadata_schema.md` — 필수 필드
- `knowledge/llm_wiki/index.md` — LLM Wiki baseline
- `.claude/skills/rag-design/SKILL.md` — **★ 첫 정식 트리거 절차**
- `docs/contracts/rag_data_contract.md` — Slice 2 contract-change 영역

---

## Skill 트리거 기록

- **rag-design**: ★ 첫 정식 트리거 (Phase 7 Slice 1 entry)
  - 절차 8단계 모두 적용 (현재 자산 로드 → retrieval/metadata/chunking/quality_filter 점검 → 새 소스 검토 → LLM Wiki vs RAG 분리 → 변경 제안서)
  - 결과: 본 ADR-025 본문
  - 후속: Slice 2 contract-change (rag_data_contract.md 갱신) + Slice 3 retrieval/embedding/chunking 구현 + Slice 4 LLM Wiki 통합 + rag-update Skill 첫 정식 (Slice 4)
  - skill_usage_log: rag-design 0 → 1 (active 전환)

---

## Status timeline

- 2026-05-29 — Phase 7 Slice 1 entry. **rag-design Skill 첫 정식 트리거**. ADR-025 본문 작성.
- (예정) Phase 7 Slice 2 — contract-change (rag_data_contract.md) + 5단계 schema/promotion/quality_filter/eval_rubric 구현.
- (예정) Phase 7 Slice 3 — chunking 512 tokens + embedding text-embedding-3-small + retrieval pgvector cosine top-k=5 threshold=0.7 구현.
- (예정) Phase 7 Slice 4 — LLM Wiki + agents/rag 통합 + rag-update Skill 첫 정식.
- (예정) Phase 7 Slice 5 — verification + smoke 13/13 + scenario_sim v3 15/15.
- (예정) Phase 9+ — eval-run 정식화 후 chunk size / threshold / 자동 비율 재평가.
- (예정) Phase 11+ — 사용자 데이터 누적 후 자동 promotion 활성 (ADR-024 §A).
- (예정) Phase 21+ — Custom embedding 교체 검토 (ADR-024 §B).
