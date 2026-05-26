# LLM Wiki Index — 영상기획 지식 색인

> 위치: `knowledge/llm_wiki/index.md`
> 목적: 영상기획 도메인 지식을 카테고리별로 색인, RAG 검색 범위 축소 + LLM context 추가 정보 제공
> 연계: `knowledge/rag/sources.md` (출처 정책), `knowledge/rag/metadata_schema.md` (태그)

---

## 0. 이 문서의 위치

영상기획 AI 에이전트가 사용하는 도메인 지식(LLM Wiki)을 카테고리별로 색인한다. 각 wiki 파일은 `candidate_knowledge.source_kind='external_seed'`로 ETL 진입하는 시드 데이터다. metadata.tags 기반 검색 필터 (Phase 2+)에 사용된다.

---

## 1. 카테고리 1: 영상 유형별

### 1.1 shortform_planning.md — 숏폼 기획 가이드

- 30-90초 영상 (YouTube Shorts / TikTok / Reels)
- Hook 첫 3초 / 구조 / CTA / 플랫폼별 차이
- 태그: `[shortform, hook, structure, cta, mobile]`

### 1.2 branding_video.md — 브랜드 영상 가이드

- 브랜드 정체성 전달 영상
- 4계층 데이터 (Brand → Domain → Series) 활용
- 톤앤매너 표준, 일관성 평가
- 태그: `[branding, identity, tone, consistency]`

### 1.3 promo_video.md — 프로모션 영상 가이드

- 특정 제품/서비스/이벤트 홍보
- 광고 단어 회피, CTA 패턴, 시즌별 변주
- 태그: `[promo, sales, cta, seasonal]`

---

## 2. 카테고리 2: 핵심 기법별

### 2.1 hook_patterns.md — Hook 패턴 카탈로그

- 첫 3-5초 hook 패턴 분류
- 질문 / 충격 / 약속 / 공감 / 데모
- 각 패턴 예시 2-3개
- 태그: `[hook, opening, attention, retention]`

### 2.2 evaluation_criteria.md — 평가 기준 백과

- eval/ 폴더 평가 차원의 LLM용 설명문
- 8 critic 차원 + hook quality / target fit / brand consistency
- 좋은 예 vs 나쁜 예
- 태그: `[evaluation, critic, quality, rubric]`

---

## 3. 카테고리 3: (Phase 4+ 보강 예정)

다음 wiki는 Phase 4+에서 추가 검토:

```yaml
educational_video.md:
  설명: 강의/튜토리얼 영상 기획
  내용: 학습 흐름 / 시청자 인지 부하 관리 / 챕터 구성
  태그: [educational, tutorial, cognitive_load]

vlog_planning.md:
  설명: 일상 vlog 기획
  내용: 내러티브 / 진정성 / 일상 vs 연출 균형
  태그: [vlog, narrative, authenticity]

interview_planning.md:
  설명: 인터뷰 / 대담 영상 기획
  내용: 질문 흐름 / 편집 리듬 / B-roll
  태그: [interview, qna, b_roll]

case_study_collection.md:
  설명: 성공 사례 모음
  내용: 사용자 동의 받은 예시 (PII 마스킹 후)
  태그: [case_study, examples, reference]

target_audience_profiles.md:
  설명: 타겟별 페르소나 가이드
  내용: 10대/20대/30대/40대+ 별 행동 패턴
  태그: [target, persona, demographics]

platform_specifics.md:
  설명: 플랫폼별 알고리즘/포맷 특성
  내용: YouTube/TikTok/Instagram 차이
  태그: [platform, algorithm, format]
```

---

## 4. 카테고리 4: 평가 기준별 (eval/ 정합)

eval/ 폴더의 평가 차원과 1:1 매핑되는 가이드:

| eval/ 파일 | wiki 매핑 | 상태 |
|---|---|---|
| `eval/hook_eval.md` | `hook_patterns.md` | 존재 |
| `eval/critic_eval.md` (8차원) | `evaluation_criteria.md` | 존재 |
| `eval/brand_consistency_eval.md` | `branding_video.md` | 일부 매핑 |
| `eval/target_fit_eval.md` | `target_audience_profiles.md` (Phase 4+) | 미작성 |
| `eval/ad_phrase_eval.md` | `style_guide/ad_phrase_blocklist.md` (별도 폴더, Phase 1 중) | 미작성 |

---

## 5. 카테고리 5: 플랫폼별 (Phase 4+ 보강)

```
YouTube Shorts:    shortform_planning.md (현재 포함)
TikTok:            shortform_planning.md (현재 포함)
Instagram Reels:   shortform_planning.md (현재 포함)
YouTube Long-form: educational_video.md (Phase 4+)
Vimeo Showcase:    (Phase 7+ 외부 API 연동 시)
```

---

## 6. 검색용 태그 표준

`metadata_schema.md` 정합. 모든 wiki chunk의 metadata.tags에 부착:

```yaml
type_tags:
  - shortform / longform / shorts_30s / shorts_60s
  - branding / promo / educational / vlog / interview

technique_tags:
  - hook / cta / structure / opening / ending
  - storytelling / demo / testimonial / challenge

platform_tags:
  - youtube / tiktok / instagram / vimeo / mixed

evaluation_tags:
  - clarity / utility / specificity / brand_safety
```

검색 시 metadata filter (Phase 2+):

```sql
where metadata @> '{"tags": ["shortform", "hook"]}'
```

---

## 7. 데이터 규모 (Phase 1)

```yaml
현재 wiki:
  파일: 6 (index 포함)
  평균 길이: ~1000-1500자/파일
  총 텍스트: 약 6-9K자
  ETL 후 chunks: 약 15-30개

Phase 4+ 확장 시:
  추가 파일: 6 (educational, vlog, interview, case_study, target, platform)
  총 chunks: 약 40-60개
```

---

## 8. wiki 갱신 절차

```
1. 운영자가 wiki/<file>.md 수정 또는 신규 파일 생성
2. ETL 트리거 (수동 또는 정기):
   - 기존 파일 변경: candidate_knowledge에 새 row INSERT
   - 기존 chunk의 promotion: 새 chunks로 INSERT (구 chunks는 is_active=false)
3. metadata.source_kind='external_seed' + source_url=file path
4. 자동 승격 (external_seed는 자동 가능, rag_data §4.3)
5. 검색에서 즉시 사용 가능
```

---

## 9. Phase별 마일스톤

### Phase 1 (현재)

- 6 wiki 파일 (index + 5 도메인)
- 단순 카테고리 분류

### Phase 4+

- 6 추가 wiki 파일 (educational / vlog / interview / case_study / target / platform)
- 자동 태깅 도입
- metadata filter 검색

### Phase 7+

- 외부 영상 사례 통합 (라이선스 검증 후)
- 다국어 wiki (ko/en/ja)

### Phase 11+

- 운영자 admin UI에서 wiki 직접 편집
- A/B 테스트 (wiki 변경 시 검색 품질)

---

## 10. Open Questions

1. wiki 파일 수 적정량 — 너무 많으면 운영 부담 / 너무 적으면 검색 빈약 (Phase 4+ 6개 추가 적정?).
2. 자동 태깅 정확도 — LLM 기반 vs 운영자 수동.
3. wiki 갱신 빈도 — 월 1회 정기 vs 필요 시.
4. wiki 외 외부 사례 (블로그 / 책) 시드 — 라이선스 검증 절차.
5. 운영자 admin UI 도입 시점 (Phase 11+) — SQL 직접 수정으로 충분한 기간.
6. wiki를 사용자에게 직접 노출할지 (학습 자료로) vs RAG로만 활용.

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 5개 카테고리 색인, Phase 4+ 6개 추가 wiki 후보,
                      태그 표준, eval/ 매핑, 갱신 절차.
```
