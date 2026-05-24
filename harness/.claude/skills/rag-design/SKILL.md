---
name: rag-design
description: |
  RAG 시스템 자체를 설계할 때 사용한다 (≠ rag-update 운영 갱신). 새 RAG layer
  추가, 새 데이터 소스 도입, chunking 전략 변경, LLM Wiki vs RAG 분리 기준
  재검토 같은 구조적 변경을 다룬다. Phase 7 첫 구현과 Phase 21+ Custom RAG
  확장에서 주로 트리거.
  키워드: "RAG 설계", "RAG architecture", "custom RAG", "chunking 전략",
  "RAG sources", "retrieval 정책 설계", "LLM Wiki 분리".
applies_to: [claude]
phase: [phase-7, phase-21, ongoing]
related_contracts:
  - docs/contracts/rag_data_contract.md
  - docs/contracts/privacy_contract.md
related_state:
  - knowledge/rag/
  - knowledge/llm_wiki/
version: v1.0.0
---

# rag-design

RAG 시스템의 구조·정책·소스 선택을 새로 설계하거나 확장하는 절차. 일상적 지식 추가/승격은 `rag-update`가 담당하므로 본 Skill은 "구조" 만 다룬다.

## 트리거 조건

- Phase 7 진입 (RAG Lite 첫 구현)
- Phase 21+ Custom RAG 확장 단계 진입
- 새 데이터 소스 도입 검토 (외부 API, 사내 문서, 사용자 데이터)
- `chunking_policy.md` 변경 제안
- `retrieval_policy.md` 의 top_k / isolation / re-rank 룰 변경
- LLM Wiki vs RAG 분리 기준 재검토
- `metadata_schema.md` 필드 추가/변경

## 사용하지 않는 경우

```
- 일상적 지식 항목 추가 / 승격 → rag-update
- 단일 prompt 회귀 → prompt-version-review
- 데이터 PII / 인젝션 검사 → security-review
- 평가 차원 자체 → eval-design
```

## 절차

### 1. 현재 자산 로드

```
1. knowledge/rag/retrieval_policy.md
2. knowledge/rag/metadata_schema.md
3. knowledge/rag/chunking_policy.md
4. knowledge/rag/quality_filter.md
5. knowledge/rag/promotion_rule.md
6. knowledge/rag/sources.md
7. knowledge/llm_wiki/index.md
8. docs/contracts/rag_data_contract.md
9. docs/contracts/privacy_contract.md
```

각 파일이 다루는 영역을 표로 정리한다 (정책 / 스키마 / 운영 / 분리 기준).

### 2. retrieval_policy 점검

| 항목 | 확인 |
|---|---|
| top_k | 현재 값과 근거 (실험 데이터 있나?) |
| brand_id 격리 | retrieval 단계에서 강제되는가? |
| domain 격리 | 도메인 간 누출 차단? |
| re-rank | 적용 여부 + 비용 |
| dedupe | 동일 chunk 중복 차단 |

### 3. metadata_schema 점검

다음 필드가 필수로 존재해야 함:

```
- brand_id
- source_kind (llm_wiki / user_doc / external / generated)
- promoted_at
- quality_score
- pii_masked (bool)
```

누락 필드는 critical → `contract-change` 트리거.

### 4. chunking_policy 점검

- 토큰 범위 (예: 200~600)
- overlap (예: 50~100)
- 단위 (문장 / 단락 / heading)
- 한국어 / 영어 분리 처리

값의 근거가 없으면 §6에서 실험 제안.

### 5. quality_filter 점검

- 최소 길이, 최대 길이
- 광고 표현 차단
- 사실성 점수 임계값
- PII 마스킹 단계 (이전·이후)

`quality_filter`와 `promotion_rule`의 5단계 (pending → filtered → evaluated → approved → promoted)가 정합하는지 확인.

### 6. 새 소스 도입 검토

새 데이터 소스가 있다면 다음 체크리스트:

```
- 출처 (저작권 / 라이선스)
- PII 가능성
- 갱신 주기
- isolation 단위 (brand 별 / 전역)
- LLM Wiki vs RAG 분류 (자주 안 변하면 Wiki / 변하면 RAG)
```

→ security-review 트리거 후보.

### 7. LLM Wiki vs RAG 분리 기준 재검토

다음 룰을 검토:

```
- LLM Wiki: 정적, 도메인 보편 지식 (예: 영상 기획 best practice)
- RAG    : 브랜드별 동적 데이터 (예: 사용자 피드백, brand_memory)
```

경계가 모호한 항목은 표로 정리, 사용자 결정 요청.

### 8. 변경 제안서 작성

`docs/contract_changes/proposals/rag_design_{date}.md` 작성:

- 변경 항목 (정책 / 스키마 / 소스)
- 근거
- 영향 받는 contract / agent / Skill
- 후속 Skill 라우팅

→ `contract-change` Skill로 라우팅.

## 출력 형식

```
[rag-design 결과] 2026-05-24
범위 : Phase 7 진입 (RAG Lite 첫 구현)
강점 : promotion_rule 5단계 정합, brand_id 메타 필수
약점 : retrieval_policy의 domain 격리가 prompt context 단계에만 적용
      → retrieval 단계 추가 필요
누락 : chunking_policy의 한국어 분리 처리 미정
제안 :
  - retrieval_policy §3 갱신 (domain 격리를 retrieval 단계로 이동)
  - chunking_policy §2.1 추가 (한국어 sentence splitter 명시)
  - 새 소스 "user_feedback_v2" 도입은 security-review 후 결정
후속 : contract-change (proposals/rag_design_2026-05-24.md 작성됨)
```

## 금지 사항

- 정책/스키마 파일 직접 수정 (반드시 `contract-change`)
- 새 소스를 security-review 없이 승인
- LLM Wiki와 RAG 경계 결정을 단독 판단 (사용자 또는 multi-llm-validation)
- chunking 값을 근거 없이 변경

## 자주 발생하는 실수

1. **retrieval_policy 한 줄 변경**: top_k만 보고 isolation 누락 가능. 항상 isolation·re-rank·dedupe 함께.
2. **metadata 필수 누락 방치**: brand_id / pii_masked 같은 필수 필드 누락을 medium으로 분류. 사실 critical.
3. **새 소스 도입을 본 Skill에서 승인**: 라이선스/PII 검토는 security-review 절차. 본 Skill은 구조만.
4. **chunking 값 임의 변경**: 토큰 범위를 실험 데이터 없이 변경. 회귀 위험 큼.

## 종료 조건

- 변경 제안서가 `docs/contract_changes/proposals/`에 저장
- 모든 변경 항목에 영향 받는 contract / agent 명시
- 새 소스가 있으면 `security-review` 트리거 완료
- `contract-change` Skill로 라우팅됨
