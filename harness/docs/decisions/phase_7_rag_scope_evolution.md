# ADR-024 — Phase 7 RAG Scope Evolution

> Date: 2026-05-29
> Status: Accepted
> Phase: 5.5 (Phase 7 진입 전 prep)
> Related: ADR-020 (Supabase pgvector), ADR-023 (Phase 5.5 legacy DB consolidation), Phase 7 active (예정), rag-design / rag-update Skills, knowledge/rag/promotion_rule.md
> Sub-agent: Phase 5.5 Slice 3 dispatch

---

## Context

사용자 결정 (2026-05-29):

1. **결정 3**: Phase 7 RAG 범위를 **Lite로 유지** — 추후 확대 가능 지점을 별도 지침에 작성
2. **결정 4**: RAG에서 **candidate_knowledge 5단계 MVP에 전부 구현**
3. **결정 5** (cross-reference): Brand Memory 자동 추출은 **Phase 9+ 이관 확정** (Phase 5.5 NG2 명시)

Phase 7 RAG Lite의 정확한 scope를 본 ADR에서 확정 + 추후 확대 경로를 명시한다. 본 ADR은 Phase 5.5 Slice 3에서 작성되었으며 Phase 7 entry 시 첫 정식 rag-design Skill 트리거의 baseline 으로 활용된다.

---

## Decision

### Phase 7 RAG Lite scope (MVP)

#### 1. candidate_knowledge 5단계 파이프라인 전부 구현 (★ 사용자 결정 4)

- **Stage 1**: `pending` — 사용자 입력 / LLM Wiki 신규 항목 / 외부 시드 데이터 진입
- **Stage 2**: `filtered` — quality_filter 통과 (PII 마스킹 + 인젝션 차단 + 광고적 표현 차단 + 길이 + 언어 + 중복)
- **Stage 3**: `evaluated` — eval rubric 평가 (Phase 9+ 정식 eval 도입 전까지 간이 rubric, eval_score 0.0~1.0 + 5-dim)
- **Stage 4**: `approved` — 사용자 또는 자동 (간이) 승인 (자동 승격 조건: eval_score ≥ 0.85 AND dimensions 모두 ≥ 3 AND source_kind ∈ {final_output, manual, external_seed} AND same_pattern_count ≥ 3 AND pii_masked = false)
- **Stage 5**: `promoted` — `rag_chunks` 테이블로 승격 + retrieval 활성 (chunking 500자 + overlap 100자, embedding text-embedding-3-small dim=1536)

각 단계는 별도 컬럼 (`status: ENUM('pending', 'filtered', 'evaluated', 'approved', 'promoted', 'rejected')`) + 전환 로그 (`promotion_history JSONB`) + 시간 기반 timeout (pending 90일, filtered 60일, evaluated 60일, rejected 90일 → hard delete) 으로 추적.

상세 운영 룰은 `knowledge/rag/promotion_rule.md` 참조. 본 ADR은 scope 결정만 명시.

#### 2. Retrieval

- pgvector (Supabase 기본 제공) 활용 — ADR-020 정합
- chunk size 표준 결정: 500자 + overlap 100자 (promotion_rule.md §2.4 정합)
- embedding 모델: text-embedding-3-small (dim=1536, 배치 10개)
- top-k retrieval (k=5, MVP)
- relevance threshold (cosine similarity ≥ 0.7 ~ 0.75, Phase 7 측정 후 결정)

#### 3. LLM Wiki vs RAG 분리

- **LLM Wiki** = 정적 지식 (영상기획 도메인 기본 패턴, hook 유형, 타겟 페르소나, contract 정합 — `knowledge/llm_wiki/`)
- **RAG** = 동적 지식 (사용자 입력 + 외부 시드 + Phase 11+ 사용자 데이터 promotion — `candidate_knowledge` → `rag_chunks`)

분리 근거: LLM Wiki는 prompt-injection 무관 (시스템 신뢰), RAG는 사용자 입력 신뢰 단계별 필터 필수.

### Phase 7 추정 시간 (사용자 결정 4 반영)

- 원안: 8~12h (RAG Lite 일부)
- **갱신: 12~16h** (5단계 전부 + retrieval + chunking + promotion logic + tests)
- 4~5 Slice 분할 예상:
  - Slice 1: entry + scope 확정 + multi-llm-validation formal self
  - Slice 2: candidate_knowledge schema + 5단계 컬럼 + migrations
  - Slice 3: quality_filter (4종) + LLM 평가 (P-EVAL-1) + 자동 승격
  - Slice 4: ETL (chunking + embedding + rag_chunks INSERT) + retrieval
  - Slice 5: close + 회고 + Phase 8 prep

---

## 확대 지점 (다른 phase 확장 경로) ★ 사용자 결정 3

본 section은 Phase 7 RAG Lite 출시 후 어떤 시점에 어떤 확장을 검토할지 명시한다. 각 확장은 별도 ADR 작성 후 phase 진입.

### A. Phase 11+ — 사용자 데이터 자동 promotion

- **확장 내용**: 실 사용자 피드백 (선택 / 수정 / 반려) 기반 candidate → approved 자동 승격
- **트리거 조건**: 사용자 1000+ + 피드백 데이터 1만+ 누적
- **연관 ADR**: Phase 11+ 신규 ADR로 정식 결정
- **선행 조건**: Phase 9+ eval-run Skill 정식화 + 자동 승격 임계값 데이터 기반 조정 (promotion_rule.md §9 Phase 4+ 마일스톤 정합)

### B. Phase 21+ — Custom RAG

- **확장 내용**: 자체 embedding model (text-embedding-3-small 대체) + custom retrieval (re-ranking)
- **트리거 조건**: pgvector retrieval 정확도 한계 + embedding API 비용 ↑ 발견 (예: 월 비용 100만원 초과)
- **연관 ADR**: Phase 21+ 신규 ADR
- **선행 조건**: 사용자 데이터 누적 + GPU 인프라 준비

### C. Phase 21+ — Graph RAG

- **확장 내용**: 관계 graph 기반 retrieval (예: Brand → Domain → Series 관계 활용)
- **트리거 조건**: 4계층 데이터 모델 활성화 + 사용자 다중 Brand 운영
- **연관 ADR**: Phase 21+ 신규 ADR
- **선행 조건**: 4계층 데이터 모델 본격 활성화 (Phase 11~20에서 단계적 확장)

### D. Phase 7+ (선택) — Hybrid retrieval

- **확장 내용**: BM25 + vector retrieval 결합 (sparse + dense)
- **트리거 조건**: vector-only retrieval 검색 누락 발견 (예: 정확한 키워드 매칭 실패 케이스 누적)
- **연관 ADR**: Phase 7+ Slice 5~ 또는 별도 mini-phase
- **선행 조건**: Phase 7 RAG Lite 정상 동작 후 measurement

### E. Phase 8+ — Multi-modal RAG (제한)

- **확장 내용**: 이미지 + reference 영상 데이터의 embedding (MVP 영구 제외 영역과 무관, reference 검색 한정)
- **트리거 조건**: 사용자 reference 영상 업로드 기능 도입 (Phase 21+)
- **연관 ADR**: Phase 21+ 신규 ADR
- **제약**: MVP 영구 제외 영역 (mvp_non_goals.md 참조) 은 본 확장에서도 절대 포함 X — 본 확장은 reference 검색 한정

### F. Phase 9+ — Re-ranking model

- **확장 내용**: retrieval top-20 → cross-encoder re-rank → top-5
- **트리거 조건**: top-5 precision 개선 필요 발견 (eval-run 측정 결과 기반)
- **연관 ADR**: Phase 9+ ADR
- **선행 조건**: eval-run Skill 정식화 + golden_set 확장

---

## Brand Memory 자동 추출 별도 처리 ★ 사용자 결정 5

**Phase 9+ 이관 (confirmed by user 2026-05-29)**:

- Phase 5.5 NG2 명시 (`phases/active/phase-5.5-legacy-db-consolidation/non_goals.md`)
- **Phase 7 RAG에 통합 X** — RAG와 Brand Memory는 분리된 메커니즘
- 활성 조건: MVP 본격 운영 + 사용자 데이터 누적 후
- Phase 9+ Brand Memory ADR 별도 신규 작성 예정

**분리 근거**:

- RAG = 검색 가능한 지식 (candidate_knowledge 5단계 후 rag_chunks)
- Brand Memory = 사용자별 누적 컨텍스트 (Brand → Domain → Series 4계층 자동 학습)
- 두 메커니즘은 데이터 소스 + 활용 시점 + 저장 위치가 다름

---

## Skill 활용 계획

- **Phase 7 entry**: phase-start v1.3.0 + multi-llm-validation formal self V1~V (다수) + **rag-design (★ 첫 정식 트리거 — RAG architecture 설계)**
- **Phase 7 진행 중**: rag-update Skill (5단계 승격 절차 강제) + contract-change (필요 시 rag_data_contract.md 갱신)
- **Phase 7 종료**: phase-complete v1.2.0 + meta-retrospective + rag-design 회고

본 ADR은 Phase 7 rag-design Skill 첫 정식 트리거 시점의 baseline 문서. Phase 7 entry 4-check에서 본 ADR 참조 필수.

---

## Constraints

- **5단계 모두 구현** — 사용자 결정 4 명시. 일부만 구현 시 본 ADR 위반.
- **추정 시간 12~16h** — Phase 7 multi_slice_plan.md 에서 본 추정 기준 4~5 Slice 분할.
- **확대 지점 6개 (A~F)** — 본 ADR 명시 외 확대는 별도 ADR 신규 작성 필수.
- **Brand Memory 절대 통합 X** — Phase 9+ 별도 진행 (NG2 정합).
- **MVP 영구 제외 영역 보존** — mvp_non_goals.md 명시 영역은 본 ADR에서도 절대 포함 X.

---

## Trade-offs

- **5단계 전부 구현 (vs 일부)** → Phase 7 시간 8~12h → 12~16h 상향. 단, 후속 phase에서 candidate_knowledge 흐름 재작업 risk 0.
- **Lite scope 유지 (vs Full)** → Custom RAG / Graph RAG / Re-ranking은 Phase 21+ 이관. Phase 7 MVP 출시 속도 우선.
- **6개 확대 지점 명시 (vs 미정)** → 추후 phase 진입 시 의사결정 부담 감소, 단 트리거 조건 데이터가 누적되어야 활성화.
- **Brand Memory 분리 유지 (vs 통합)** → 두 메커니즘 동시 진입 시 phase 시간 ↑↑, scope creep 위험. 분리 후 Phase 9+ 별도 ADR 권장.

---

## Verification

### Phase 7 entry 시 verification 항목

- ✅ 본 ADR (ADR-024) 참조 → Phase 7 goals.md / scope.md 정합 확인
- ✅ candidate_knowledge 5단계 모두 scope.md 포함 여부
- ✅ Phase 추정 시간 12~16h 반영
- ✅ Brand Memory 통합 NG 명시 (Phase 7 non_goals.md)
- ✅ 확대 지점 6개 closing_notes.md 또는 ADR 참조

### Phase 7 종료 시 verification 항목

- ✅ 5단계 모두 실 구현 + 테스트 PASS
- ✅ promotion_rule.md §9 Phase 1 마일스톤 정합
- ✅ Phase 8 진입 시 Brand Memory 분리 유지 확인

---

## References

- `knowledge/rag/retrieval_policy.md` — retrieval 표준 (k, threshold, embedding model)
- `knowledge/rag/promotion_rule.md` — 5단계 표준 (Phase 1 마일스톤 §9)
- `knowledge/rag/quality_filter.md` — 4종 필터 (PII / 광고 / 길이 / 언어 / 중복)
- `knowledge/rag/metadata_schema.md` — RAG metadata 표준
- `docs/contracts/rag_data_contract.md` — rag_data 단일 출처 (§4 5단계 승격 흐름)
- `.claude/skills/rag-design/SKILL.md` — Phase 7 첫 정식 트리거
- `.claude/skills/rag-update/SKILL.md` — Phase 7 진행 중 운영
- ADR-020 (`docs/decisions/phase_5_supabase_adoption.md`) — Supabase pgvector baseline
- ADR-023 (`docs/decisions/phase_5_5_legacy_db_consolidation.md`) — Phase 1 legacy 통합 시점 cross-reference
- `phases/active/phase-5.5-legacy-db-consolidation/non_goals.md` — NG1 (RAG 본격 구현 Phase 7 이관) + NG2 (Brand Memory Phase 9+ 이관) + NG3 (prompt_registry 본문 Phase 7+ 이관)

---

## Status timeline

- 2026-05-29 — Phase 5.5 Slice 3 dispatch 에서 본 ADR 작성. 사용자 결정 3 (RAG Lite 유지) + 결정 4 (5단계 전부 구현) + 결정 5 (Brand Memory Phase 9+ confirm) 반영.
- (예정) Phase 7 entry — 본 ADR 참조 baseline으로 phase-start + rag-design Skill 첫 정식 트리거.
- (예정) Phase 7 종료 — 5단계 실 구현 verification + closing_notes 연결.
- (예정) Phase 9+ — Brand Memory 자동 추출 별도 ADR 작성 + 본 ADR §Brand Memory 별도 처리 cross-reference 활성.
