# ADR-026 — Phase 7 RAG 5단계 Promotion Logic

> Date: 2026-05-29
> Status: Accepted
> Phase: 7 Slice 1 (Pre-Entry)
> Related: ADR-024 (Phase 5.5 5단계 정의), ADR-025 (Phase 7 RAG architecture), `knowledge/rag/promotion_rule.md`
> Sub-agent: Phase 7 Slice 1 dispatch

---

## Context

ADR-024에서 `candidate_knowledge` 5단계 (pending → filtered → evaluated → approved → promoted) MVP 전부 구현 결정 (사용자 결정 4).
ADR-025에서 RAG architecture (chunking + embedding + retrieval + LLM Wiki 분리) 결정.

본 ADR에서 **5단계 transition 규칙** + **간이 eval rubric** (Phase 9+ 정식 deprecated 전) + **사용자 승인 정책 (자동/수동 hybrid)** + **promotion_history JSONB schema** 결정.

self-validation V7 (5단계 자동/수동 승인 정책)이 본 ADR로 발화.

---

## Decision

### 1. 5단계 Transition 규칙

#### 1.1 `pending → filtered` (자동)

**조건**: `quality_filter` 4종 모두 통과
- PII 0 (이메일 / 전화번호 / 주민번호 / 카드번호 패턴 X)
- 인젝션 0 (system prompt 시도 패턴 X — Phase 1 baseline 패턴)
- 광고적 표현 0 (확정 결정 [9] — `광고적 표현 차단 단어 list`)
- 길이 / 언어 / 중복 OK (knowledge/rag/quality_filter.md 정합)

**실패 시**: `pending` 상태 유지 + `promotion_history`에 reason 메타 기록 (이력 보존)

```json
{"from": "pending", "to": "pending", "at": "...", "reason": "quality_filter_failed", "details": {"pii": false, "injection": true, "ad": false, "length": "ok"}}
```

#### 1.2 `filtered → evaluated` (자동)

**조건**: `eval_rubric` 종합 점수 ≥ 0.6

**평가 dim (3개)** (간이 rubric, Phase 9+ 정식 deprecated):
- `relevance` (0~1): 영상기획 도메인 관련성 (도메인 키워드 매칭 비율 기반)
- `clarity` (0~1): 문장 명료성 (길이 + 명료성 heuristic)
- `safety` (0~1): PII/인젝션 재검사 (false positive 방어)

**overall**: 평균 (3 dim 합 / 3)

**실패 시**: `filtered` 상태 유지 + 메타에 점수 기록 (재시도 가능 — eval_rubric 개선 후)

```json
{"from": "filtered", "to": "filtered", "at": "...", "reason": "low_eval_score", "scores": {"relevance": 0.5, "clarity": 0.4, "safety": 1.0}, "overall": 0.63}
```

#### 1.3 `evaluated → approved` (Hybrid 자동+수동) ★

**자동 임계 (점수 ≥ 0.8)**:
- → 자동 approved
- promotion_history `method`: `auto`

**수동 승인 대기 (0.6 ≤ 점수 < 0.8)**:
- → 사용자 수동 승인 대기 (UI 또는 API endpoint)
- 사용자 승인 endpoint: **`POST /api/v1/rag/promote`** (Slice 4 선택 구현)
- promotion_history `method`: `manual`

**자동 거부 (점수 < 0.6)**:
- → `evaluated` 상태 유지 (재시도 — eval_rubric 재평가 후)
- 단, 점수가 0.6 이하면 사실상 filtered → evaluated transition 자체에서 차단됨 (1.2 조건 정합)
- 본 case는 race condition (점수 측정 시점 차이)에서만 발생

```json
{"from": "evaluated", "to": "approved", "at": "...", "method": "auto", "threshold": 0.8, "overall": 0.85}
```

#### 1.4 `approved → promoted` (자동)

**조건**: 항상 approved 시점에 **즉시 promoted** (approved_knowledge 테이블 이동)

**메타**:
- `source_candidate_id` FK (candidate_knowledge.id)
- `promoted_at` timestamp
- retrieval 활성 (pgvector index 자동 update)

```json
{"from": "approved", "to": "promoted", "at": "..."}
```

#### 1.5 Idempotent transition (V5 graceful 정합)

- 같은 transition 재실행 시 promotion_history append 추가 X (idempotent)
- 단, **partial state** (예: chunking 완료 + embedding 실패) 후 재시도는 promotion_history append (graceful fallback recovery)
- promotion_history는 append-only — 삭제/수정 금지 (이력 보존)

### 2. promotion_history JSONB Schema

`candidate_knowledge.promotion_history JSONB DEFAULT '[]'::jsonb`:

```json
[
  {
    "from": "pending",
    "to": "filtered",
    "at": "2026-05-29T10:00:00Z",
    "reason": "quality_pass"
  },
  {
    "from": "filtered",
    "to": "evaluated",
    "at": "2026-05-29T10:01:00Z",
    "scores": {"relevance": 0.8, "clarity": 0.7, "safety": 1.0},
    "overall": 0.83
  },
  {
    "from": "evaluated",
    "to": "approved",
    "at": "2026-05-29T10:02:00Z",
    "method": "auto",
    "threshold": 0.8,
    "overall": 0.83
  },
  {
    "from": "approved",
    "to": "promoted",
    "at": "2026-05-29T10:02:00Z"
  }
]
```

#### 인덱싱

- **GIN 인덱싱 미적용** (현 Phase 7 MVP)
- **Phase 9+ 도입 검토** (사용자 데이터 누적 후 검색/분석 빈도 ↑ 시점)
- ADR-024 §확대 지점 정합

#### Append-only 강제

- DB layer (Supabase RLS / application repository)에서 promotion_history 컬럼 UPDATE는 **append만 허용**, 기존 항목 삭제/수정 차단
- 백엔드 repository 함수 `promotion.append_history(item, transition)` 로 표준화

### 3. 간이 eval rubric (Phase 9+ 정식화 전까지)

#### 3.1 위치

`backend/fastapi/rag/eval_rubric.py` (Slice 2 신규)

#### 3.2 API

```python
def evaluate(content: str, metadata: dict | None = None) -> dict[str, float]:
    """간이 eval — 3 dim 각 0.0~1.0."""
    return {
        "relevance": _score_relevance(content, metadata),  # 도메인 키워드 매칭 비율 기반
        "clarity": _score_clarity(content),  # 문장 길이 + 명료성 heuristic
        "safety": _score_safety(content),  # PII/인젝션 재검사
    }


def overall(scores: dict[str, float]) -> float:
    """3 dim 평균. 향후 가중 합 (Phase 9+ golden_set 기반)으로 교체."""
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)
```

#### 3.3 Heuristic 상세

| dim | heuristic | 비고 |
|---|---|---|
| relevance | 영상기획 도메인 키워드 (`hook / 타겟 / 페르소나 / 시리즈 / 영상기획 / 콘텐츠 / 채널 ...`) 매칭 비율 (0~1) | 키워드 list는 `knowledge/llm_wiki/index.md` 기반 |
| clarity | 문장 길이 평균 (한국어 10~80자 적정 — 0.0~1.0 normalize) + 띄어쓰기 비율 + 문장 종결 부호 | overall 가중 0.3 |
| safety | PII detector + 인젝션 detector false positive 재검사 (1.0 - false_positive_rate) | overall 가중 0.4 |

#### 3.4 Phase 9+ deprecated 경로

- Phase 9+ eval-run Skill 정식화 시 본 rubric은 **deprecated**
- `golden_set.md` 기반 정식 rubric으로 교체 (5~8 dim, cross-encoder)
- 본 ADR §3.3 heuristic은 Phase 9+에서 제거 예정 (P-CRITIC-CANONICAL-001 정책 계승 — deprecated + 단계적 축소)

### 4. 사용자 승인 정책

#### 4.1 비율 목표 (MVP 가정)

| 단계 | 목표 비율 | 비고 |
|---|---|---|
| 자동 (evaluated → approved, 점수 ≥ 0.8) | **70%+** | MVP 초기 — quality vs UX 균형 |
| 수동 승인 (0.6 ≤ 점수 < 0.8) | **20~30%** | 인간 검토 부담 적정 수준 |
| 거부 (점수 < 0.6, evaluated 유지) | **<10%** | quality_filter + 1.2 transition 자체에서 차단되므로 미미 |

#### 4.2 Phase 11+ 재평가

- 사용자 데이터 누적 후 비율 재조정 (ADR-024 §A 확대 지점)
- 자동 승격 조건 (eval_score ≥ 0.85 AND dimensions 모두 ≥ 3 AND ...) 활성화 시점 — Phase 11+
- 현 Phase 7 hybrid 0.8 임계는 보수적 (Phase 11+ 데이터 누적 후 0.85 등 상향 가능)

#### 4.3 endpoint (Slice 4 선택 구현)

```
POST /api/v1/rag/promote
Body: {"candidate_id": "uuid", "action": "approve" | "reject"}
Response: {"id": "uuid", "stage": "promoted" | "evaluated", "promotion_history": [...]}

GET /api/v1/rag/candidates?stage=evaluated
Response: {"items": [...], "total": N}
```

- RLS: 인증된 사용자만 (auth.uid() 검증)
- service_role: backend-only (admin batch promotion 시)

#### 4.4 사용자 부담 완화

- 자동 비율 70%+ 목표 → 수동 승인 부담 ≤ 30%
- 수동 승인 batch UI (Phase 8+ frontend) — Phase 7 Slice 4에서는 API만 (NG11 PlanCard 무수정 정합)

### 5. Graceful fallback (V5 + ADR-025 §5 정합)

- transition 실패 시 promotion_history에 reason 기록 + 이전 stage 유지
- retry 가능 (idempotent — 1.5 정합)
- plan 생성 차단 X (RAG 실패 시 빈 results + warning marker)
- warning markers (ADR-025 §5 표준):
  - `rag_unavailable` (retrieval 실패)
  - `embedding_failed` (embedding 실패)
  - `chunking_failed` (chunking 실패)
  - `quality_filter_failed` (PII detector 등 library error)
  - `llm_wiki_unavailable` (LLM Wiki lookup 실패)

---

## Constraints

- **자동 transition은 graceful** (실패 시 이전 stage 유지 + 메타 기록)
- **promotion_history append-only** (이력 보존, DB layer 강제)
- **GIN 인덱싱 미적용** (Phase 9+ 도입 검토)
- **idempotent transition** (재시도 가능, partial state recovery)
- **간이 eval rubric은 Phase 9+ deprecated** (golden_set 기반 정식 rubric 교체)
- **수동 승인 endpoint 인증 필수** (auth.uid() RLS)
- **사용자 부담 완화** — 자동 비율 70%+ 목표
- **NG7 (사용자 데이터 자동 promotion) 정합** — 현 Phase 7은 사용자 입력만 5단계, 사용자 피드백 기반 자동 promotion은 Phase 11+
- **NG8 (eval-run Skill + golden_set 자동 평가) 정합** — 간이 rubric만 (Phase 9+ deprecated 예정)

---

## Trade-offs

- **자동 비율 ↑** → 처리 속도 ↑ but quality risk ↑
- **수동 승인 ↑** → quality ↑ but 사용자 부담 ↑
- **0.8 임계 (자동) / 0.6 임계 (수동)** → 보수적, Phase 11+ 데이터로 조정 (예: 0.85 / 0.7로 상향)
- **3 dim 간이 rubric** → 단순 but 정확도 한계 (Phase 9+ 5~8 dim cross-encoder rubric으로 교체 시 자연 진화)
- **GIN index 미적용** → 검색/분석 성능 ↓ but storage cost ↓ (Phase 9+ 누적량 증가 시 도입)
- **append-only promotion_history** → storage 누적 but 이력 보존 (감사 / 디버깅 / 재분석)
- **endpoint 인증 필수** → anon endpoint에서 promote 불가 (이는 의도 — RAG poisoning 차단)
- **hybrid 정책** → 자동/수동 boundary 결정 (0.8 / 0.6 임계) — Phase 11+ tuning 필요

---

## Verification

### Slice 2 (5단계 schema + core) — pytest

#### `test_rag_promotion.py` 5+ 케이스

1. `pending → filtered` (자동, quality_filter PASS)
2. `pending → pending` (quality_filter 실패, reason 기록)
3. `filtered → evaluated` (자동, eval_rubric ≥ 0.6)
4. `filtered → filtered` (eval_rubric < 0.6, 점수 메타 기록)
5. `evaluated → approved` (자동, 점수 ≥ 0.8)
6. `evaluated → approved (수동)` (0.6 ≤ 점수 < 0.8 + 수동 승인)
7. `approved → promoted` (자동, approved_knowledge 이동)
8. idempotent 재시도 case (partial state recovery)
9. promotion_history append-only 검증 (UPDATE 시 기존 항목 보존)

#### `test_rag_quality_filter.py` 3+ 케이스

1. PII 검출 (이메일 / 전화번호 / 주민번호)
2. 인젝션 검출 (system prompt 시도)
3. 광고적 표현 검출 (확정 결정 [9] 차단 단어)

#### `test_rag_eval_rubric.py` (또는 test_rag_promotion 흡수) 3+ 케이스

1. 3 dim 각각 + overall 평균
2. low score case (overall < 0.6)
3. high score case (overall ≥ 0.8 자동 승격)

### Slice 4 (LLM Wiki + 통합) — pytest

- `test_rag_integration.py`:
  - end-to-end 5단계 transition 1회 통과 (chunking → embedding → promotion 5단계 → retrieval round-trip)
  - graceful failure 5종 (5 warning marker)
  - hybrid 자동/수동 boundary case

### Slice 5 (Close) — smoke + scenario_sim v3

- `scripts/smoke_test_phase_7.ps1` 13/13
- `scripts/scenario_simulation.ps1` v3 15/15 (S11~S15 RAG 시나리오)
- audit_naming 0 drift + audit_page_component 2 intended WARN (Phase 5 baseline 유지)

---

## References

- ADR-024 (`docs/decisions/phase_7_rag_scope_evolution.md`) — 5단계 정의 baseline
- ADR-025 (`docs/decisions/phase_7_rag_architecture.md`) — RAG architecture + graceful 표준 마커
- `knowledge/rag/promotion_rule.md` — 5단계 표준 + §9 Phase 1 마일스톤
- `knowledge/rag/quality_filter.md` — 4종 필터
- `knowledge/rag/metadata_schema.md` — 필수 필드
- `meta/validations/2026-05-29_phase-7-pre-entry_self.md` §V7
- `meta/patterns.md` (P-GRACEFUL-001, P-CRITIC-CANONICAL-001 deprecated 단계적 축소 정책 계승)

---

## Status timeline

- 2026-05-29 — Phase 7 Slice 1 entry. ADR-026 본문 작성 (5단계 transition + 간이 eval rubric + hybrid 승인 + promotion_history schema).
- (예정) Phase 7 Slice 2 — `rag/promotion.py` + `rag/quality_filter.py` + `rag/eval_rubric.py` 구현 + pytest.
- (예정) Phase 7 Slice 4 — `routers/rag.py` (선택) endpoint 구현 + agents/rag.py 통합.
- (예정) Phase 9+ — eval-run Skill 정식화 + golden_set 기반 rubric으로 본 §3 간이 rubric deprecated.
- (예정) Phase 11+ — 사용자 데이터 누적 후 자동 비율 / 임계값 (0.8 / 0.6) 재조정.
- (예정) Phase 11+ — 사용자 데이터 자동 promotion 활성 (ADR-024 §A + NG7 해소).
