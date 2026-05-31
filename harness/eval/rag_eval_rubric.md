# rag_eval_rubric.md — RAG 검색 품질 평가 rubric + golden_set

> 위치: `eval/rag_eval_rubric.md`
> 상태: **Phase 10 Slice 3 정식화 (v1.0.0)** — Phase 9.5 NG1 이관분 승격 (CC-009)
> 참조 (단일 출처):
> - 구현: `backend/fastapi/rag/eval_rubric.py` (Phase 7 간이 3 dim — relevance / clarity / safety)
> - 테스트: `backend/fastapi/tests/test_rag_eval_rubric.py` (3 dim 회귀)
> - 정책: `knowledge/rag/retrieval_policy.md` (§2 top_k=5 / threshold=0.7 / final_adoption=3, §7 빈 결과, §8 rag_used)
> - 승격: `knowledge/rag/promotion_rule.md` + `docs/decisions/phase_7_promotion_logic.md` (ADR-026 §3 filtered→evaluated)
> - 데이터: `docs/contracts/rag_data_contract.md` §5 검색 정책 / §10 광고·PII
> - 회귀: `eval/golden_set.md` (GS-007 RAG 채택 / GS-014 RAG graceful)

---

## 0. 이 문서의 위치

`rag_eval_rubric.md` 는 **RAG 검색·근거 활용 품질을 평가하는 단일 진실 소스(rubric)** 다.

두 가지를 정식화한다:

1. **knowledge 승격 단계** rubric — candidate_knowledge 가 RAG 본체로 승격(promoted)되기 전
   `filtered → evaluated` 자동 채점 (ADR-026 §3). **이 차원은 현재 코드로 구현됨**
   (`rag/eval_rubric.py` 3 dim — relevance / clarity / safety).
2. **검색 활용 단계** rubric — Planning(P-006) 이 검색 결과(chunk)를 기획안 근거로 사용할 때의
   품질 차원 (retrieval 관련성 / 근거 충실성 / 환각 부재 / top-k 정확도). **정식 정의 + golden_set
   케이스 형식**. 자동 매칭 가능 차원은 mock, 의미 차원은 실 LLM mode (eval/runner.py capability).

이 문서가 정의하지 않는 대상:
- 검색 파라미터 자체(top_k / threshold) → `knowledge/rag/retrieval_policy.md`
- 영상기획 8차원 critic 채점 → `eval/video_planning_eval.md`
- golden_set 전체 케이스 정의 → `eval/golden_set.md` (본 문서는 RAG 차원 + RG- 케이스 형식만)

---

## 1. 평가 차원 (dimensions)

### 1.A 승격 단계 (구현됨 — `rag/eval_rubric.py` 3 dim)

| 차원 | 정의 | 측정 (간이) | 범위 |
|---|---|---|---|
| **relevance** | 영상기획 도메인 적합도 | 도메인 키워드 매칭 비율 (3+ 매칭 → 1.0) | 0.0~1.0 |
| **clarity** | 문장 명료성 | 평균 단어 수 heuristic (5~20 단어 → 1.0) | 0.0~1.0 |
| **safety** | PII / 인젝션 부재 | quality_filter 재검사 (pass → 1.0, fail → 0.0) | 0.0~1.0 |

- `overall = (relevance + clarity + safety) / 3` (단순 평균 — `rag/eval_rubric.py:overall`).
- 승격 자동 조건 (ADR-026 §3): `overall ≥ 0.6` AND `safety == 1.0` → `evaluated`.
- ★ **회귀 보존**: `test_rag_eval_rubric.py` 의 3 dim 단언은 본 rubric v1.0.0 의 §1.A 와 정합
  (behavior-preserving — 구현 차원 변경 0).

### 1.B 검색 활용 단계 (정식 정의 — 검색 결과 → 기획 근거)

| 차원 | 정의 | mock (자동) | 실 LLM mode | 임계 |
|---|---|---|---|---|
| **retrieval_relevance** | 채택 chunk 가 쿼리 의도와 관련 있는가 | similarity ≥ threshold(0.7) 충족 비율 | LLM-as-judge 관련성 | ≥ 0.7 |
| **groundedness** (근거 충실성) | 기획안 주장이 채택 chunk 로 뒷받침되는가 | `rag_used[].used_reason` 비어있지 않음 | LLM 근거 일치 판정 | ≥ 0.7 |
| **hallucination_absence** (환각 부재) | 채택하지 않은/없는 자료를 인용하지 않는가 | `rag_used.source_id ⊆ 채택 chunk_id` | LLM 환각 검출 | == 1.0 |
| **topk_accuracy** (top-k 정확도) | threshold 통과 chunk 만 채택, 최대 3개 | `len(rag_used) ≤ 3` AND threshold 미만 chunk 미포함 | (동일, 자동) | == 1.0 |
| **graceful_empty** | 검색 0건 시 예외 없이 진행 + 경고 | `no_rag_reference` warning + plans 3개 | (동일, 자동) | == 1.0 |

- 자동 차원(retrieval_relevance/topk_accuracy/hallucination_absence/graceful_empty)은
  golden_set mock 채점으로 강제. groundedness 의미 판정은 실 LLM mode (opt-in, ADR-033 §2.2).
- `retrieval_policy.md` §2 수치(top_k=5 / threshold=0.7 / final_adoption=3) 가 단일 출처.

---

## 2. RAG golden_set 케이스 형식 (RG-XXX)

검색 활용 단계 회귀 케이스는 `eval/golden_set.md` 의 GS-XXX 와 동일한 yaml 형식을 따르되,
RAG 차원 전용 case_id prefix `RG-` 를 사용한다 (도메인별 prefix — golden_set.md §8 Open Q5 정합).
현 Phase 10 에서는 정식 형식 + 대표 2 케이스를 본 문서에 정의하고, golden_set.md 의 GS-007 /
GS-014 가 동일 차원을 회귀 커버한다 (중복 정의 회피 — golden_set.md 단일 출처 원칙).

```yaml
case_id: RG-XXX                  # 고정 ID (RG- prefix — RAG 검색 차원 전용)
name: "한 줄 설명"
priority: P1 | P2
mode: discovery | quick
prompt_target: "RAG 검색 + P-006"
input:
  approved_direction: "..."      # 검색 쿼리 시드
  rag_context_mock:              # 검색 mock 결과 (chunk_id / similarity / content)
    - { chunk_id: "c1", similarity: 0.85, content: "..." }
expected_output:
  dimensions:                    # §1.B 차원 기대치
    retrieval_relevance: ">= 0.7"
    topk_accuracy: "== 1.0"
    hallucination_absence: "== 1.0"
  validation:
    - <자동 검증 가능한 규칙>
  passing_criteria:
    - <케이스 단위 합/불 기준>
notes:
  - <설계 의도>
```

### 2.1 RG-001 · 검색 3개 채택 + 근거 인용 (정상)

```yaml
case_id: RG-001
name: "RAG top_k 5 → threshold 통과 3개 채택 + rag_used 근거 기록"
priority: P1
mode: discovery
prompt_target: "RAG 검색 + P-006"
input:
  approved_direction: "대학생 창업동아리 시행착오 30초 쇼츠"
  rag_context_mock:
    - { chunk_id: "c1", similarity: 0.85, content: "성장 기록 패턴 A" }
    - { chunk_id: "c2", similarity: 0.78, content: "동아리 운영 사례 B" }
    - { chunk_id: "c3", similarity: 0.72, content: "쇼츠 후킹 패턴 C" }
    - { chunk_id: "c4", similarity: 0.65, content: "threshold 미만 D" }
    - { chunk_id: "c5", similarity: 0.58, content: "threshold 미만 E" }
expected_output:
  dimensions:
    retrieval_relevance: ">= 0.7"
    topk_accuracy: "== 1.0"
    hallucination_absence: "== 1.0"
    groundedness: ">= 0.7"   # 실 LLM mode
  validation:
    - rag_used.length <= 3
    - rag_used.source_id ⊆ {c1, c2, c3}   # threshold 통과만
    - c4, c5 미포함 (hallucination_absence)
    - 각 rag_used.used_reason 비어있지 않음 (groundedness 대리)
  passing_criteria:
    - 검색 정책 정합 (retrieval_policy §2, §8)
    - no_rag_reference warning 없음
notes:
  - "검색 채택 정상 흐름. golden_set GS-007 과 동일 차원 — GS-007 이 회귀 단일 출처."
```

### 2.2 RG-002 · 검색 0건 graceful (no_rag_reference)

```yaml
case_id: RG-002
name: "RAG 검색 전부 threshold 미만 → 0건 채택 graceful 진행"
priority: P1
mode: discovery
prompt_target: "RAG 검색 + P-006"
input:
  approved_direction: "틈새 도메인 신규 주제 60초"
  rag_context_mock:
    - { chunk_id: "c1", similarity: 0.62, content: "관련 약함 A" }
    - { chunk_id: "c2", similarity: 0.55, content: "관련 약함 B" }
expected_output:
  dimensions:
    topk_accuracy: "== 1.0"
    graceful_empty: "== 1.0"
    hallucination_absence: "== 1.0"
  validation:
    - rag_used.length == 0
    - validation.warnings ⊇ ["no_rag_reference"]
    - plans.length == 3 (graceful degradation)
  passing_criteria:
    - 예외 없이 3안 생성 (rag_context=[] 주입)
    - retrieval_policy §7.1 빈 결과 처리 정합
notes:
  - "검색 빈 결과 graceful. golden_set GS-014 와 동일 차원 — GS-014 가 회귀 단일 출처."
```

---

## 3. 임계값 게이트 (eval-run 정합)

```
승격 단계 (§1.A):
  - safety == 1.0 (PII/인젝션 0 — 안전 강제, 미달 시 즉시 차단)
  - overall ≥ 0.6 → evaluated (그 미만 filtered 유지)

검색 활용 단계 (§1.B):
  - topk_accuracy == 1.0 (threshold 미만 chunk 채택 → fail)
  - hallucination_absence == 1.0 (없는 source 인용 → 즉시 fail)
  - retrieval_relevance ≥ 0.7 (mock: threshold 충족 비율)
  - groundedness ≥ 0.7 (실 LLM mode — opt-in 운영 배치)
```

- mock 강제 차원은 CI per-commit (비용 0). groundedness 의미 차원은 실 LLM mode flag
  (`eval/runner.py` ScoreContext — 키/caller opt-in, default mock fallback).

---

## 4. 실행 / 모드

- **mock (primary)**: golden_set GS-007 / GS-014 (검색 차원) 를 `eval/runner.py` mock-deterministic
  으로 회귀. 본 rubric §1.B 자동 차원 강제.
- **real (capability, opt-in)**: groundedness / retrieval_relevance 의미 판정 — 운영 단계 야간 배치.
  `ScoreContext(requested_mode="real", llm_caller=...)` + 키 제공 시 활성. CI 미실행 (실 호출 0).

→ 채점 코드는 `rag/eval_rubric.py` (§1.A 구현) + `eval/runner.py` (§1.B 검색 차원, golden_set 경유).

---

## 5. 케이스 추가 / 수정 절차

- RG-XXX 추가: §2 형식. priority + 근거 PR 본문 명시. case_id 재사용 금지.
- 검색 차원이 golden_set GS-XXX 와 중복되면 GS- 를 단일 출처로 (RG- 는 형식 참조 + cross-ref).
- rubric 차원/임계 변경은 contract-change Skill 절차 (본 문서는 eval contract).

---

## 6. 변경 이력

```
v1.0.0 (2026-05-31): Phase 10 Slice 3 정식화 (CC-009). Phase 9.5 NG1 이관분 승격.
                     §1.A 구현 3 dim (rag/eval_rubric.py 정합, 회귀 보존) +
                     §1.B 검색 활용 4+1 차원 정식 정의 + RG-XXX 케이스 형식 +
                     RG-001/RG-002 대표 케이스 (golden_set GS-007/GS-014 cross-ref).
```
