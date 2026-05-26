# chunking_policy.md — 문서 분할 / chunking 정책

> 위치: `knowledge/rag/chunking_policy.md`
> 단일 출처: `docs/contracts/rag_data_contract.md` §4.4 (approved → promoted ETL)
> 연계: `docs/contracts/db_schema.md` §7.3 `rag_chunks.chunk_index`

---

## 0. 이 문서의 위치

candidate_knowledge.content 가 rag_chunks 로 변환될 때의 **분할 전략**을 정의한다. chunk 크기 / overlap / 의미 단위 분할 / 문서 유형별 차이 / 임베딩 비용 추정을 다룬다.

수치 충돌 시 `rag_data_contract.md §4.4` 우선.

---

## 1. 설계 원칙

```
1. 한 chunk = 한 개의 영상기획 원칙 또는 패턴 (의미 단위).
2. 너무 짧으면 임베딩 정보 부족, 너무 길면 검색 정확도 저하.
3. 한국어 기준 200-500 토큰 (대략 400-1000자) 범위.
4. overlap은 의미 연속성 유지용 (50 토큰 ~ 약 100자).
5. PII 포함 chunk 절대 금지 (마스킹 후에만 chunking).
6. 임베딩 비용은 모델 단가 × 토큰 수 × 1.1 (overlap 손실) 으로 추정.
7. 모델 변경 시 모든 chunks 재임베딩 (breaking change).
```

---

## 2. Phase 1 단순 chunking (현재)

### 2.1 분할 룰

```yaml
chunk_size: 500자 (한국어 글자 기준, 대략 250-300 토큰)
overlap: 100자
unit: 문자 단위 (의미 단위 미고려, Phase 4+ 보강)

알고리즘:
  for i in range(0, len(content), chunk_size - overlap):
      chunk = content[i : i + chunk_size]
      yield chunk
```

### 2.2 작은/큰 후보 처리

```
≤ 500자:     chunk 1개 (그대로 INSERT, chunk_index=0)
500-1500자:  chunk 2-3개 (overlap 100자)
≥ 1500자:    chunk 3개 이상 (overlap 100자)
≥ 2000자:    quality_filter §4에서 rejected (too_long)
```

### 2.3 chunk_index

```
chunk_index 0부터 순서대로 증가.
같은 document_id 내에서 unique.
검색 시 인접 chunk를 묶어 보여주는 옵션 (Phase 4+) 검토.
```

---

## 3. Phase 4+ 의미 단위 chunking (검토)

문자 단위 분할의 한계: 문장 중간 절단, 의미 손실. 의미 단위 분할 도입 검토:

### 3.1 의미 단위 분할 전략

```yaml
algorithm: recursive_text_splitter
priority:
  - "\n\n" (문단 구분)
  - "\n"   (줄바꿈)
  - ". "   (한국어: "다.", "요.")
  - " "    (공백)
target_size: 300-500 토큰
overlap: 50 토큰

라이브러리 후보:
  - langchain.text_splitter.RecursiveCharacterTextSplitter
  - llama_index NodeParser
```

### 3.2 문서 유형별 분할 전략

| 유형 | 권장 분할 | 사유 |
|---|---|---|
| llm_wiki/ (시드) | 의미 단위 (섹션 헤더 기준) | 운영자가 의도한 구조 보존 |
| user_generated (final_output) | 단순 500자 분할 | 사용자별 길이 편차 큼 |
| user_choice/feedback | 분할 안 함 (1 chunk) | 짧음 (대부분 < 500자) |
| external_seed | 의미 단위 | 외부 출처의 논리 구조 보존 |
| manual | 운영자 명시 분할 (마커 사용) | 의도 반영 |

### 3.3 manual chunking 마커 (Phase 4+ 검토)

```markdown
---chunk---
첫 번째 chunk 본문...

---chunk---
두 번째 chunk 본문...
```

운영자가 직접 분할 지점을 명시하면 ETL이 그대로 따른다.

---

## 4. overlap 정책

### 4.1 왜 overlap이 필요한가

```
chunk 경계에 걸친 의미가 검색에서 누락되는 것 방지.
예: 500자 경계가 "Hook은 시작" / "3초 안에 집중을 끌어야" 로 갈라지면 검색 실패.
overlap 100자 → 두 chunk 모두 "Hook은 시작 3초 안에 집중을" 포함 → 검색 가능.
```

### 4.2 overlap 크기

```yaml
Phase 1: 100자 (고정)
Phase 4+ 의미 단위 도입 시: 50 토큰 (~80-100자)
```

너무 크면 (≥ 200자) 중복 저장 비용 증가. 너무 작으면 (≤ 50자) 의미 손실 방지 효과 없음.

---

## 5. 임베딩 비용 추정

### 5.1 OpenAI text-embedding-3-small

```
단가: $0.02 / 1M tokens
한국어 토큰 비율: 약 1글자당 1.5-2 토큰 (UTF-8 멀티바이트)
한국어 500자 chunk ≈ 750-1000 토큰
overlap 손실: 약 10% (100자 중복 임베딩)
```

### 5.2 예상 비용 (Phase 1)

```
시드 데이터:
  - llm_wiki 6 파일 × 평균 1000자 = 6000자 ≈ 12K 토큰
  - 비용: 12K × ($0.02 / 1M) = $0.00024 (무시 가능)

사용자 데이터 누적 (월간):
  - 사용자 1000명 × 월 5 영상 × final_output 3000자 = 15M 글자 ≈ 30M 토큰
  - 비용: 30M × ($0.02 / 1M) = $0.60 / 월
  - overlap 손실 10% 포함: $0.66 / 월

월 운영 비용: < $1 (Phase 1)
```

### 5.3 모델 변경 시 비용

```
모든 chunks 재임베딩:
  - Phase 11+ 누적 100K chunks × 평균 800토큰 = 80M 토큰
  - 비용: 80M × ($0.02 / 1M) = $1.60 (1회성)
  - text-embedding-3-large 사용 시: $0.13/1M → $10.40 (1회성)
```

비용은 무시 가능 수준. 진짜 비용은 latency / 회귀 평가 시간.

---

## 6. chunking 검증 (ETL 단계)

ETL이 chunking 후 다음 검증:

```python
def validate_chunks(chunks):
    for c in chunks:
        assert 1 <= len(c) <= 2000           # 길이 검증
        assert not has_pii(c)                 # PII 잔존 확인 (마스킹 후이지만 재검사)
        assert not has_ad_phrase_1st(c)       # 1차 차단 광고 단어 잔존 확인
    assert len(chunks) >= 1
    assert len(set(c.content for c in chunks)) == len(chunks)  # 완전 중복 chunks 없음
```

실패 시 ETL 중단 + 운영자 알림.

---

## 7. chunking 후처리 (Phase 4+ 검토)

### 7.1 자동 제목 생성

```
각 chunk에 대해 LLM이 한 줄 제목 생성 (P-AUX-3 후보):
- rag_documents.title에 채택 (chunk 1개일 때)
- 검색 결과에 표시 (사용자 친화 출처 표기)
```

### 7.2 자동 태깅

```
chunk content 보고 LLM이 tags 추출:
- ["hook", "shorts", "growth_record"]
- metadata.tags 에 저장
- retrieval_policy §2 metadata filter (Phase 2+) 기반
```

### 7.3 인접 chunk 묶어 보여주기

```
검색 결과 chunk가 같은 document의 다른 chunk와 인접하면:
- 사용자 UI에서 묶어 표시 (맥락 연속성)
- Planning prompt에는 단일 chunk만 (토큰 비용)
```

---

## 8. Phase별 마일스톤

### Phase 1 (현재)

- 문자 단위 500자 + overlap 100자
- 단순 split
- 비용 모니터링

### Phase 4+

- 의미 단위 분할 (recursive splitter)
- 문서 유형별 전략 분리
- 자동 제목 / 태깅

### Phase 11+

- chunk 평균 크기 데이터 기반 조정
- 인접 chunk 통합 UI

### Phase 21+

- 멀티모달 chunking (이미지 + 텍스트, Phase 21+ 비디오 미리보기 도입 시)

---

## 9. Open Questions

1. chunk_size 500자 — Phase 4+ 의미 단위 분할로 300-700자 변동 허용 시 검색 품질 변화.
2. overlap 100자 — 의미 단위 분할에서는 50 토큰? 75 토큰?
3. 한국어 토큰 비율 1.5-2배 — text-embedding-3-small의 실제 한국어 토큰화 측정 필요.
4. manual chunking 마커 도입 시점 — Phase 4 vs Phase 11.
5. 자동 제목 생성 비용 — chunk마다 LLM 1회 호출이면 promoted ETL 비용 증가.
6. 인접 chunk 묶기 UI — 사용자에게 정말 도움 되는지 (UX 테스트 필요).

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. Phase 1 단순 chunking + Phase 4+ 의미 단위 검토,
                      overlap / 비용 추정 / 검증 / 후처리 / 문서 유형별 전략.
```
