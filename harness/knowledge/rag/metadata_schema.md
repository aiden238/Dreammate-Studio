# metadata_schema.md — RAG chunk 메타데이터 표준

> 위치: `knowledge/rag/metadata_schema.md`
> 참조: `docs/contracts/rag_data_contract.md` §11 (필수 키), `docs/contracts/db_schema.md` §7.3 `rag_chunks`
> 적용 범위: `rag_chunks.metadata` JSONB 컬럼 + 검색 결과 응답

---

## 0. 이 문서의 위치

모든 RAG chunk에 부착되는 **메타데이터 표준 스키마**를 정의한다. 메타데이터는 (a) 검색 필터링 (b) 출처 추적 (c) 품질 모니터링 (d) Phase 후속 확장에 사용된다. 본문 텍스트만으로 충분하지 않은 정보는 모두 메타데이터에 넣는다.

---

## 1. 설계 원칙

```
1. JSONB로 저장. 스키마 변경에 유연하되 필수 키는 검증.
2. PII는 메타데이터에 직접 넣지 않는다 (user_id 등 식별자만 ID 형태).
3. 모든 chunk는 source_kind + source_id를 가진다 (익명 출처 금지).
4. brand_id가 있는 항목은 brand 격리 검색의 기반 (Phase 2+).
5. pgvector 인덱스 컬럼은 별도 컬럼으로 분리 (JSONB 안에 두지 않음).
6. quality_score / language / status 등 필터 자주 사용하는 키는 인덱스 검토.
```

---

## 2. 필수 키 (Phase 1)

모든 promoted chunk는 다음 키를 가져야 한다:

```json
{
  "source_kind":   "user_choice | user_feedback | final_output | manual | external_seed",
  "source_id":     "uuid | string | null",
  "candidate_id":  "uuid",
  "promoted_at":   "2026-05-26T10:30:00+09:00",
  "language":      "ko-KR",
  "quality_score": 0.85,
  "brand_id":      "uuid | null",
  "domain_id":     "uuid | null",
  "series_id":     "uuid | null",
  "status":        "promoted",
  "access_scope":  "public | brand_internal | private"
}
```

### 2.1 각 키 의미

| 키 | 의미 | 예시 |
|---|---|---|
| source_kind | 원본 데이터의 출처 분류 | `"final_output"` |
| source_id | 원본 레코드의 ID (해당 테이블) | `"a3f9-..."` |
| candidate_id | candidate_knowledge.candidate_id | `"b1c2-..."` |
| promoted_at | promoted 상태 진입 시각 (KST) | `"2026-05-26T10:30:00+09:00"` |
| language | ISO 639 + region | `"ko-KR"` |
| quality_score | 0~1, P-EVAL-1 점수 (rag_data §4.2) | `0.85` |
| brand_id | 소속 brand. 없으면 null (manual / external) | `null` |
| domain_id | 소속 domain | `null` |
| series_id | 소속 series | `null` |
| status | candidate_knowledge.status (promoted 외 검색 안 함) | `"promoted"` |
| access_scope | 검색 노출 범위 | `"public"` |

### 2.2 access_scope 정책

```
public:           모든 사용자에게 검색 노출 (external_seed / manual / 익명화 final_output)
brand_internal:   해당 brand_id 소속 사용자에게만 (브랜드 내부 학습 데이터)
private:          현재 사용 안 함 (Phase 7+ team workspace 도입 시 검토)
```

---

## 3. 선택 키 (Phase 1 + Phase 2)

```json
{
  "tags":             ["hook", "shorts", "growth_record"],
  "structure_type":   "growth_record | tutorial | promo | branding | null",
  "approach_label":   "narrative | educational | challenge | testimonial | null",
  "format":           "shorts_30s | shorts_60s | long_3min | long_10min | null",
  "target_age":       "10s | 20s | 30s | 40s+ | mixed | null",
  "platform":         "youtube | tiktok | instagram | mixed | null",
  "has_ad_warning":   false,
  "pii_masked":       false,
  "promoter":         "auto | <reviewer_user_id>"
}
```

### 3.1 tags

- 자유 형식 문자열 배열
- 검색용 보조 필터 (Phase 2+ metadata filter 도입 시)
- 자동 태깅 (Phase 4+): LLM이 본문 보고 tag 추출

### 3.2 structure_type / approach_label / format

- `output_schema.md §8` P-006의 plan 분류와 정합
- 검색 결과 reranking에 사용 (예: 사용자가 shorts_30s 원할 때 shorts_30s tag chunk 우선)

---

## 4. pgvector 인덱스 필드 분리

다음 필드는 JSONB 내부가 아닌 **별도 컬럼**으로 두어 인덱스 효율 확보:

```sql
-- db_schema.md §7.3 rag_chunks (현재 + Phase 2 확장 검토)

create table rag_chunks (
    chunk_id      uuid primary key default gen_random_uuid(),
    document_id   uuid references rag_documents(document_id),
    chunk_index   int not null,
    content       text not null,
    embedding     vector(1536),
    metadata      jsonb default '{}'::jsonb,

    -- Phase 2 검토: 자주 쓰는 필터를 컬럼으로 승격
    brand_id      uuid,
    language      text default 'ko-KR',
    quality_score real,

    created_at    timestamptz default now()
);

create index idx_rag_brand   on rag_chunks (brand_id);
create index idx_rag_lang    on rag_chunks (language);
create index idx_rag_quality on rag_chunks (quality_score);
```

JSONB 내부 필드만으로 검색하면 GIN 인덱스가 필요하고 latency가 증가한다.

---

## 5. metadata 검증 (Phase 1)

ETL 시 (`approved → promoted`) 다음 검증:

```python
required_keys = {
    "source_kind", "source_id", "candidate_id", "promoted_at",
    "language", "quality_score", "status", "access_scope"
}

def validate_metadata(meta: dict) -> bool:
    if not required_keys.issubset(meta.keys()):
        raise ValueError("missing required key")
    if meta["source_kind"] not in ALLOWED_SOURCE_KINDS:
        raise ValueError("invalid source_kind")
    if not (0 <= meta["quality_score"] <= 1):
        raise ValueError("quality_score out of range")
    if meta["status"] != "promoted":
        raise ValueError("only promoted is searchable")
    return True
```

실패 시 ETL 중단 + 운영자 알림.

---

## 6. 검색 응답에 포함되는 필드

P-006 응답의 `rag_used[]` 항목에는 메타데이터 일부만 노출:

```json
{
  "source_id": "<chunk_id>",
  "title": "<rag_documents.title>",
  "used_reason": "<LLM 자유 텍스트>",
  "source_kind": "external_seed",
  "language": "ko-KR"
}
```

`brand_id` / `quality_score` 등은 사용자에게 노출하지 않음 (운영 정보).

---

## 7. Phase별 마일스톤

### Phase 1 (현재)

- 필수 키 11개 검증
- 인덱스: 없음 (chunks 500개 이하 예상)

### Phase 2+

- `brand_id` / `language` / `quality_score` 컬럼 승격 + 인덱스
- 자동 태깅 도입 (`tags` 키 활용)
- metadata filter 검색 정책 추가 (retrieval_policy §2)

### Phase 7+

- `access_scope` 활성화 (private / brand_internal 분리)
- PII 위험 신호를 metadata에 기록

### Phase 11+

- 운영자 검수 UI에서 metadata 직접 편집
- 사용자 그룹 (team workspace) 격리

---

## 8. Open Questions

1. `quality_score`를 promoted 단계에서 다시 재계산할지 (현재 candidate.eval_score 그대로 복사).
2. `tags` 자동 태깅을 어느 시점에 도입할지 — promoted 직후 vs 운영자 검수 시.
3. metadata 변경(예: tag 추가) 시 chunks를 UPDATE할지 새 chunks 생성할지 (versioning).
4. multi-brand 검색에서 brand_id null인 manual/external_seed의 가중치 정책.
5. `access_scope = private` 사용 사례 정의 — 사용자 본인 데이터 RAG vs brand_memory 직접 주입.
6. metadata size 상한 — 너무 큰 메타데이터는 검색 응답 페이로드 증가.

---

## 9. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 필수 키 11개, 선택 키 9개, pgvector 인덱스 분리,
                      검증 흐름, Phase 마일스톤 정리.
```
