# sources.md — RAG 지식 출처 정책

> 위치: `knowledge/rag/sources.md`
> 연계: `docs/contracts/rag_data_contract.md` §8 (학습 신호), `knowledge/datasets/` 4 파일
> 단일 출처: 본 문서 (출처 분류 + 라이선스 정책)

---

## 0. 이 문서의 위치

RAG 지식 데이터의 **출처 분류 / 라이선스 / 인용 정책**을 정의한다. `candidate_knowledge.source_kind` enum과 1:1 매핑된다. Phase 1 시드 데이터부터 Phase 21+ 외부 API 연동까지의 출처 로드맵을 포함한다.

---

## 1. 5종 출처 분류 (Phase 1)

`candidate_knowledge.source_kind`와 동일:

| source_kind | 출처 | 자동 승격 | 데이터 위치 |
|---|---|---|---|
| `manual` | 운영자 직접 입력 | 가능 | candidate_knowledge SQL INSERT |
| `external_seed` | 외부 사례 시드 | 가능 | `knowledge/llm_wiki/` markdown |
| `final_output` | 사용자 최종 영상기획 | 가능 (품질 조건) | `video_projects.status='final'` |
| `user_choice` | 사용자 카드 선택 | 불가 (수동) | `discovery_choices.selected_card` |
| `user_feedback` | 사용자 like/dislike | 불가 (수동) | `feedback_events.event_type='like'` |

---

## 2. Phase 1 초기 시드 데이터

### 2.1 knowledge/llm_wiki/ 6 파일 출처

```yaml
index.md:                운영자 작성 (LLM Wiki 색인)
shortform_planning.md:   외부 사례 분석 + 운영자 정리 (출처 명시 필수)
branding_video.md:       동일
promo_video.md:          동일
hook_patterns.md:        동일
evaluation_criteria.md:  eval/ 평가 차원의 LLM용 설명문 (내부 작성)
```

### 2.2 시드 데이터 규모 추정

```
6 파일 × 평균 1000자 = 6000자
의미 단위 분할 시: 약 15-30 chunks
임베딩 비용: < $0.001 (1회성)
ETL 시간: < 1분
```

### 2.3 시드 데이터 정합성 룰

```
1. 모든 시드 데이터는 ETL 시 source_kind='external_seed'로 진입
2. metadata.source_url 에 원본 출처 명시 (가능한 경우)
3. metadata.source_license 에 라이선스 명시 (CC / 인용 / 운영자 작성)
4. 운영자 검수 거친 후 자동 승격 가능 (안전)
5. 사용자에게 노출 시 "참고 자료: <title>" 표기
```

---

## 3. 사용자 생성 데이터 흐름

### 3.1 final_output (가장 신뢰도 높음)

```
사용자가 영상기획안 최종 확정 (video_projects.status → 'final')
   │
   ▼
quality_score_avg (Critic 8차원) ≥ 4.0 검사
   │ pass
   ▼
candidate_knowledge INSERT (source_kind='final_output')
   │
   ▼ 자동 필터 → LLM 평가 → 자동 승격 조건 충족 시
   │
   ▼
rag_chunks 등록
```

### 3.2 user_choice (반복 신호 기반)

```
사용자가 Discovery 카드 선택 (discovery_choices.selected_card)
   │
   ▼
selected_card.confidence ≥ 0.7 AND 같은 brand_id에서 동일 카드 ≥ 3회
   │
   ▼
candidate_knowledge INSERT (source_kind='user_choice')
   │
   ▼ 자동 필터 → LLM 평가 → **수동 검수 필수** (사용자 PII 위험)
```

### 3.3 user_feedback (긍정 신호)

```
사용자가 final_output에 like (feedback_events.event_type='like')
   │
   ▼
hook + structure 일부를 candidate로 추출
   │
   ▼
candidate_knowledge INSERT (source_kind='user_feedback')
   │
   ▼ 자동 필터 → LLM 평가 → **수동 검수 필수**
```

---

## 4. 라이선스 / 저작권 정책

### 4.1 license 분류

```yaml
manual:
  license: "proprietary"
  사용자 노출: OK (자체 데이터)
  외부 공유: 금지

external_seed (운영자 작성):
  license: "proprietary"
  사용자 노출: OK
  외부 공유: 금지

external_seed (외부 인용):
  license: "CC-BY-4.0" / "CC0" / "fair_use_quote"
  metadata.source_url 필수
  사용자 노출: 출처 표기 동반
  외부 공유: 라이선스 준수

final_output / user_choice / user_feedback:
  license: "user_consented"
  사용자 데이터 처리 동의 기반 (privacy_contract Phase 7+ 정형화)
  PII 마스킹 후에만 RAG 진입
  외부 공유: 금지
```

### 4.2 출처 표기

```
Planning 응답의 rag_used[] 에서:
- external_seed: title + source_url 노출
- manual: title만 노출
- final_output / user_choice / user_feedback: "다른 사용자의 영상기획에서" (익명)
```

### 4.3 저작권 침해 신고 대응

```
1. 신고 접수 (사용자 또는 외부 권리자)
2. 운영자가 해당 chunks 즉시 회수 (is_active=false)
3. 7일 내 검토 → 정당한 신고면 hard delete + 신고자 회신
4. 라이선스 위반 패턴이면 출처 정책 재검토
```

---

## 5. 외부 데이터 정책 (Phase 7+ 검토)

### 5.1 외부 API 연동 후보

```
- YouTube Data API (영상 트렌드, 조회수)
- Vimeo Showcase (참고 사례)
- 영상기획 공개 블로그 RSS (크롤링)
- 도서 출판사 API (저작권 협의 후)
```

### 5.2 도입 조건

```
1. 라이선스 명확 (API ToS 또는 별도 계약)
2. 비용 예측 가능 (월 운영비 합리적)
3. 데이터 품질 검증 (golden_set 회귀 평가)
4. Phase 7+ privacy_contract 정형화 후
5. 운영자 승인 (multi-llm-validation 절차)
```

### 5.3 도입 후 흐름

```
외부 API 데이터 → ETL 큐 → candidate_knowledge (source_kind='external_api')
   ↓
운영자 검수 필수 (수동 승격)
   ↓
promoted
```

`source_kind`에 'external_api' enum 추가는 Phase 7+ contract-change.

---

## 6. 출처 메타데이터 표준

각 chunk의 metadata에 출처 정보 포함 (`metadata_schema.md §2` 정합):

```json
{
  "source_kind": "external_seed",
  "source_id": "wiki-shortform-001",
  "source_url": "https://example.com/article",
  "source_license": "CC-BY-4.0",
  "source_author": "...",
  "source_published_at": "2025-03-15",
  "promoted_at": "2026-05-26T10:30:00+09:00"
}
```

---

## 7. 학습 신호 출처별 우선순위

검색 결과 reranking 시 (Phase 4+ 검토) 출처별 가중치:

```
external_seed:    1.2 (운영자 검증된 외부 사례 — 신뢰도 ↑)
manual:           1.1 (운영자 직접 입력)
final_output:     1.0 (사용자 영상기획 — 기준값)
user_feedback:    0.9 (긍정 신호이나 추출 패턴)
user_choice:      0.8 (단순 선택 신호)
```

가중치 곱하기 cosine similarity로 reranking. Phase 4+ 도입 검토.

---

## 8. Phase별 마일스톤

### Phase 1 (현재)

- 5종 source_kind
- llm_wiki/ 6 파일 시드
- 라이선스 정책 초안

### Phase 4+

- 출처별 reranking 가중치
- 자동 license 검증 (CC 라이선스 자동 매칭)

### Phase 7+

- privacy_contract 정형화 후 사용자 데이터 처리 강화
- 외부 API 연동 검토 시작

### Phase 21+

- YouTube / Vimeo 외부 API 도입
- source_kind='external_api' enum 추가

---

## 9. Open Questions

1. external_seed 출처를 사용자에게 어디까지 노출할지 (브랜드 보호 vs 투명성).
2. 라이선스 위반 신고 7일 검토 — 빠른 회수가 필요한 케이스 (SLA).
3. user_choice의 자동 승격 허용 조건 — PII 검증 강화 후 가능?
4. 외부 API 도입 시 Phase 7 vs Phase 11 — 사용자 데이터 누적이 더 먼저 가치 있을 수 있음.
5. 출처별 reranking 가중치 — 데이터 누적 후 실제 검색 품질 차이 측정.
6. final_output 출처 익명화 30일 — 너무 길거나 짧은지 (PII 위험 vs 학습 신호 보존).

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 5종 source_kind 분류, 라이선스 정책,
                      시드 데이터 규모, 외부 API 로드맵, 출처별 reranking 가중치.
```
