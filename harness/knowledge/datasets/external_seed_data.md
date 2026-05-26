# external_seed_data.md — 외부 시드 데이터

> 위치: `knowledge/datasets/external_seed_data.md`
> source_kind: `external_seed`
> 연계: `knowledge/llm_wiki/`, `knowledge/rag/sources.md`, `rag_data_contract.md` §8.5

---

## 0. 정의

**외부 시드 데이터**: 프로젝트 외부에서 가져온 영상기획 시드 데이터. Phase 1 초기 RAG를 부트스트랩하기 위한 외부 출처 데이터.

```
주요 출처:
  - 공개 영상기획 블로그
  - 강의 자료 (라이선스 검증)
  - 책 (인용 허용 범위)
  - 사례 분석 자료
  - 운영자 직접 작성 (외부 출처 참조하여 정리)

저장 위치:
  - knowledge/llm_wiki/ 6 파일 (markdown)
  - ETL 후 candidate_knowledge.source_kind='external_seed'
```

---

## 1. 외부 출처 분류

### 1.1 공개 블로그 (CC-BY / fair_use_quote)

```yaml
출처 예시:
  - 영상기획 전문가 개인 블로그
  - 마케팅 회사 공개 콘텐츠
  - YouTube 크리에이터 가이드 (공식)

처리:
  - 직접 인용 시 출처 명시 필수
  - 의역/정리 시 영감받은 출처 metadata.source_url 기록
  - CC 라이선스 검증 (BY / SA / NC / ND 등)

위험:
  - 출처 미확인 콘텐츠 사용 금지
  - 비공개 자료 사용 금지
```

### 1.2 강의 / 교육 자료

```yaml
출처 예시:
  - 무료 공개 강의 (유튜브 / Coursera 등)
  - 교육 기관 공개 자료

처리:
  - 강의 노트 직접 사용 금지 (저작권)
  - 핵심 원칙만 추출 + 자체 표현으로 재작성
  - 출처 명시 (강의명, 강사명)

위험:
  - 유료 강의 자료 사용 금지
  - 강의 슬라이드 직접 OCR/캡처 사용 금지
```

### 1.3 책 (인용 범위)

```yaml
출처 예시:
  - 영상기획 / 마케팅 / 콘텐츠 제작 서적
  - 학술서적 (영상학 / 미디어학)

처리:
  - 짧은 인용 허용 (저작권법 fair use)
  - 긴 발췌 금지
  - 출처 명시 (책 제목, 저자, 페이지)
  - 의역 / 정리 시 영감 출처 명시

위험:
  - 책 전체 디지털화 금지
  - 미공개/번역 안 된 외국 서적 사용 시 추가 검증
```

### 1.4 사례 분석 자료 (공개)

```yaml
출처 예시:
  - 광고/마케팅 사례 분석 (전문지)
  - 성공 / 실패 사례 모음
  - 업계 트렌드 리포트

처리:
  - 사례명 / 브랜드명 익명화 가능 시 익명화
  - 정확한 출처 기록
  - 통계 인용 시 원본 데이터 출처

위험:
  - 비공개 분석 자료 사용 금지
  - 개별 회사 내부 자료 금지
```

---

## 2. 라이선스 검증 절차

```
[외부 자료 발견]
  ↓
1. 라이선스 명시 확인:
   - CC0 / CC-BY-4.0 → OK
   - All Rights Reserved → 인용만 (fair use 범위)
   - 라이선스 불명 → 보류 / 운영자 검증

  ↓
2. 출처 메타데이터 기록:
   - source_url
   - source_author (가능 시)
   - source_published_at
   - source_license

  ↓
3. 운영자 검수:
   - 라이선스 정합성 확인
   - 인용 범위 확인 (짧은 인용 vs 발췌)
   - 의역 시 영감 출처 명시 확인

  ↓
4. candidate_knowledge INSERT (source_kind='external_seed')
   - rag_data_contract §8.5 흐름
   - 자동 승격 가능 (운영자 검수 거친 데이터)
```

---

## 3. 출처 메타데이터 기록 (sources.md §6 정합)

각 external_seed chunk의 metadata:

```json
{
  "source_kind": "external_seed",
  "source_url": "https://example.com/article/123",
  "source_author": "운영자A 또는 외부 저자명",
  "source_license": "CC-BY-4.0 | fair_use_quote | proprietary_internal",
  "source_published_at": "2025-03-15",
  "promoted_at": "2026-05-26T10:30:00+09:00",
  "promoter": "manual_reviewer"
}
```

---

## 4. 초기 시드 규모 추정 (Phase 1)

```
knowledge/llm_wiki/ 6 파일:
  - index.md: ~1000자 (운영자 작성)
  - shortform_planning.md: ~1500자 (외부 출처 + 운영자 정리)
  - branding_video.md: ~1500자 (동일)
  - promo_video.md: ~1500자 (동일)
  - hook_patterns.md: ~1500자 (외부 사례 분석 + 정리)
  - evaluation_criteria.md: ~1000자 (eval/ 폴더 정합 내부 작성)

총 텍스트: 약 8000자
ETL 후 chunks: 약 16-30개 (500자 단위 분할 + overlap)
임베딩 비용: < $0.001 (1회성)
ETL 시간: < 1분
```

### 4.1 Phase 4+ 추가 시드 계획

```
educational_video.md: ~1500자
vlog_planning.md: ~1500자
interview_planning.md: ~1500자
case_study_collection.md: ~3000자 (사례 5-10개)
target_audience_profiles.md: ~2000자
platform_specifics.md: ~1500자

추가 텍스트: 약 11000자
추가 chunks: 약 22-40개
누적 총 chunks: 약 40-70개
```

### 4.2 Phase 7+ 외부 사례 확장

```
공개 사례 100+ 케이스 수집 시:
  - 케이스 당 평균 500자
  - 추가 텍스트: 약 50000자
  - 추가 chunks: 약 100개
  - 누적: 약 200개

외부 API 연동 시 (YouTube Data API 등):
  - 트렌드 데이터 자동 수집
  - 라이선스 검증 후 시드 진입
```

---

## 5. 사용자 노출 정책

```yaml
external_seed 출처를 사용자에게 어떻게 노출할지:

Phase 1 (현재):
  - rag_used[]에 title + used_reason 노출
  - 출처 URL은 노출 안 함 (간단성)

Phase 4+ (검토):
  - 출처 URL 노출 (투명성)
  - "이 영상기획은 ____ 자료를 참고했어요" 안내

Phase 7+ (계획):
  - 사용자가 출처별 가중치 설정 가능 (개인화)
  - 신뢰하는 출처만 사용
```

---

## 6. 보존 정책

`db_schema.md` §10 정합:

```
external_seed candidates:
  pending:    90일
  filtered:   60일
  evaluated:  60일
  approved:   영구
  promoted:   영구
  rejected:   90일 후 hard delete

외부 데이터 권리자 신고 시:
  즉시 회수 (is_active=false)
  7일 내 검토
  정당한 신고면 hard delete + 신고자 회신
```

---

## 7. 운영 룰

### 7.1 신규 시드 추가 절차

```
1. 운영자가 외부 자료 발견
2. 라이선스 검증 (§2)
3. knowledge/llm_wiki/<file>.md 작성 또는 수정
4. ETL 트리거 (수동 또는 정기 5분 주기)
5. 자동 필터 통과 → LLM 평가 → 자동 승격
6. promoted 후 검색에서 즉시 사용 가능
```

### 7.2 기존 시드 갱신

```
1. wiki 파일 수정
2. ETL이 변경 감지 (file hash 비교)
3. 기존 chunks의 is_active=false
4. 새 chunks INSERT (versioning)
5. 사용자 노출은 새 버전부터
```

### 7.3 시드 품질 모니터링

```
- 시드 chunks가 실제 검색에서 얼마나 자주 사용되는지 (rag_used 통계)
- 사용자 피드백 (like/dislike) per chunk
- 거의 안 쓰이는 chunks → 시드 품질 재검토
```

---

## 8. Phase별 마일스톤

### Phase 1 (현재)

- llm_wiki/ 6 파일 시드
- 라이선스 검증 절차
- 자동 ETL

### Phase 4+

- 추가 wiki 6 파일
- 사례 시드 50개+
- 출처 URL 사용자 노출

### Phase 7+

- 외부 API 연동 (YouTube Data 등)
- 다국어 시드 (en/ja)
- 자동 라이선스 검증 (CC 매칭)

### Phase 21+

- 자동 크롤링 + 라이선스 검증
- 신뢰 도메인 화이트리스트

---

## 9. Open Questions

1. 라이선스 검증 자동화 — Phase 4+ CC 매칭 가능?
2. 외부 자료 권리자 신고 7일 SLA — 너무 느리지 않은지.
3. 시드 데이터 갱신 주기 — 월 1회 정기 vs 필요 시.
4. 사용자 출처 가중치 설정 (Phase 7+) — UI 복잡도 vs 가치.
5. 외부 API 도입 시점 (Phase 7+ vs Phase 11+) — 데이터 비중 변화.
6. 시드 chunks 보존 기간 — 영구 vs 사용 빈도 낮으면 정리.

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 4종 외부 출처 분류, 라이선스 검증 절차,
                      Phase 1 시드 규모 추정, 사용자 노출 정책, 운영 룰.
```
