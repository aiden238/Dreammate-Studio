# quality_filter.md — pending → filtered 자동 품질 필터

> 위치: `knowledge/rag/quality_filter.md`
> 단일 출처: `docs/contracts/rag_data_contract.md` §4.1 (pending 자동 필터)
> 연계: `docs/contracts/llm_security_contract.md` (PII), `docs/contracts/output_schema.md` §14 (광고 단어)

---

## 0. 이 문서의 위치

candidate_knowledge 가 pending 상태에서 filtered 로 진입하기 전 거치는 **자동 품질 필터**의 운영 룰을 정의한다. 5종 검사: PII / 광고 / 길이 / 언어 / 중복.

본 문서는 운영자 친화 해설서이며, 수치/정책 충돌 시 `rag_data_contract.md §4.1` 우선.

---

## 1. 필터 5종 한눈에 보기

```
┌───────────────────────────────────────────────────────────┐
│ candidate INSERT (pending)                                │
└───────────────────────────────────────────────────────────┘
   │
   ▼
┌───────────────────────────┐
│ 1) PII 검사 + 마스킹       │ ← llm_security_contract 연동
└───────────────────────────┘
   │ pass    ↘ rejected('pii_residual')
   ▼
┌───────────────────────────┐
│ 2) 광고 단어 검사          │ ← output_schema §14 ad_phrase_blocklist
└───────────────────────────┘
   │ pass    ↘ rejected('ad_phrase_violation')
   ▼
┌───────────────────────────┐
│ 3) 길이 검사               │
└───────────────────────────┘
   │ pass    ↘ rejected('too_short' | 'too_long')
   ▼
┌───────────────────────────┐
│ 4) 언어 검사               │
└───────────────────────────┘
   │ pass    ↘ rejected('non_korean')
   ▼
┌───────────────────────────┐
│ 5) 중복 검사 (cosine)     │
└───────────────────────────┘
   │ pass    ↘ rejected('duplicate')
   ▼
┌───────────────────────────┐
│ status = 'filtered'       │
└───────────────────────────┘
```

순서 중요: PII 마스킹이 광고 단어보다 먼저 (마스킹 후 광고 단어 패턴 탐지 정확도 ↑).

---

## 2. PII 검사 (필터 1)

`llm_security_contract.md` + `rag_data_contract.md §9` 정합.

### 2.1 마스킹 패턴

```yaml
patterns:
  phone:        '\d{2,3}-\d{3,4}-\d{4}'    → '010-****-****'
  email:        '\S+@\S+\.\S+'             → 'u***@***.com'
  ssn:          '\d{6}-\d{7}'              → '******-*******'
  card:         '\d{4}-\d{4}-\d{4}-\d{4}'  → '****-****-****-****'
  ip:           '\d+\.\d+\.\d+\.\d+'       → '192.168.1.*'
```

마스킹 성공 시 `pii_masked = true` 기록.

### 2.2 잔존 위험 판정

마스킹 후에도 다음 조합 발견 시 `rejected('pii_residual')`:

```
- 사람 이름 (한국 흔한 이름 1000개 사전) + 학교/소속 + 학번
- 사람 이름 + 주소(시/구/동) 패턴
- 사람 이름 + 직책 + 회사명
```

판정 알고리즘은 Phase 7+ privacy_contract에서 정형화. Phase 1에서는 단순 사전 매칭.

### 2.3 통과/실패 처리

```yaml
pass:
  pii_masked: true | false (필요 여부 따라)
  content: 마스킹된 본문으로 UPDATE
  next: 광고 단어 검사

fail (잔존 위험):
  status: rejected
  rejected_reason: 'pii_residual'
  retention: 90일 후 hard delete
```

---

## 3. 광고 단어 검사 (필터 2)

`output_schema.md §14` + `rag_data §10` 정합.

### 3.1 1차 차단 단어

```
예시 (knowledge/llm_wiki/style_guide/ad_phrase_blocklist.md 단일 출처):
  최저가 / 무조건 / 100% / 완벽한 / 최고의 / 절대 / 보장 / 단언
```

발견 시:

```yaml
status: rejected
rejected_reason: 'ad_phrase_violation'
ad_violations: ["최저가", "100%"]  # 발견된 단어 목록
ad_phrase_check: true
```

### 3.2 2차 경고 단어

```
예시: 놓치지 마세요 / 지금 바로 / 후회 / 마지막 기회
```

발견 시 통과하되:

```yaml
status: filtered (정상 진행)
metadata.has_ad_warning: true
ad_violations: ["놓치지 마세요"]   # 기록만, rejection 아님
```

### 3.3 사용자 직접 입력 예외

`output_schema §14.3` 정합: 사용자가 `direct_input`으로 직접 친 텍스트는 검사 안 함 (자기 표현 보장). 단 candidate_knowledge로 들어올 때는 검사 대상 (학습 신호로 사용되므로).

---

## 4. 길이 검사 (필터 3)

```yaml
min_length: 10자
max_length: 2000자
unit: 한국어 글자 단위 (공백 제외)

too_short:
  조건: len(content) < 10
  처리: rejected('too_short')
  사유: 의미 있는 영상기획 패턴이 되기에 너무 짧음

too_long:
  조건: len(content) > 2000
  처리: rejected('too_long')
  사유: chunking이 어렵고 다른 패턴과 섞일 위험
```

### 4.1 길이 권장 범위

```
영상기획 패턴 chunk 권장: 100~800자
짧은 hook 패턴: 50~150자 (단 너무 짧으면 의미 손실)
긴 케이스 스터디: 500~1500자 (이 이상은 chunking 후 INSERT)
```

---

## 5. 언어 검사 (필터 4)

Phase 1은 한국어 단일 운영.

### 5.1 언어 비율 측정

```python
def korean_ratio(text):
    korean_chars = len([c for c in text if '가' <= c <= '힣'])
    total_chars = len([c for c in text if c.isalnum()])
    return korean_chars / max(total_chars, 1)
```

### 5.2 판정

```yaml
pass:
  조건: korean_ratio >= 0.4
  처리: filtered 진행

fail:
  조건: korean_ratio < 0.4 (영어/일어/기타 60% 이상)
  처리: rejected('non_korean')

exception:
  source_kind = 'external_seed' AND
  metadata.language ∈ ['en-US', 'ja-JP']
  → Phase 2+ 다국어 도입 시 통과 허용 (현재는 안 함)
```

---

## 6. 중복 검사 (필터 5)

### 6.1 검사 알고리즘

```
1. candidate.content를 임베딩 (text-embedding-3-small, 1536)
2. 같은 brand_id 또는 brand_id=null인 기존 rag_chunks와 cosine similarity 계산
3. 최대 similarity 추출
4. 임계치 비교
```

### 6.2 임계치

```yaml
duplicate_threshold: 0.95

거의 동일:
  조건: similarity >= 0.95
  처리: rejected('duplicate')
  metadata.duplicate_chunk_id: 기존 chunk_id 기록

유사도 높음 (참고 정보만):
  조건: 0.85 <= similarity < 0.95
  처리: filtered 진행 (rejection 아님)
  metadata.similar_chunk_id: 유사 chunk_id 기록 (운영자 참고)
```

### 6.3 예외

```yaml
manual source_kind 예외:
  조건: source_kind = 'manual'
  처리: 중복 발견되어도 통과 (warning만)
  사유: 운영자가 의도적으로 변형/보강한 중복 데이터 허용
  기록: metadata.duplicate_chunk_id + metadata.manual_duplicate_allowed=true
```

### 6.4 brand 격리

```
같은 brand_id 내 중복만 검사:
  - 같은 brand의 동일 패턴은 노이즈 (rejected)
  - 다른 brand의 동일 패턴은 OK (브랜드별 학습 데이터 격리)
```

---

## 7. 필터 통과 후 기록

filtered 상태 진입 시 다음 metadata 추가:

```json
{
  "pii_masked": true,
  "ad_phrase_check": true,
  "ad_violations": [],
  "language_ratio": 0.85,
  "duplicate_max_similarity": 0.78,
  "filter_passed_at": "2026-05-26T10:30:00+09:00"
}
```

운영자가 어떤 필터 어떻게 통과했는지 추적 가능.

---

## 8. 필터 통계 / 모니터링

```yaml
일일 모니터링 (Slack #ops-daily 요약):
  - pending → filtered 통과율
  - 각 필터별 rejected 비율 (PII / 광고 / 길이 / 언어 / 중복)
  - 가장 자주 발견된 광고 단어 top 5
  - 가장 자주 중복으로 잡힌 chunk top 5

임계 알림 (즉시):
  - 1시간 내 pending INSERT 100건 이상 + 통과율 < 10% → 필터 너무 엄격 신호
  - PII 잔존 위험 1시간 내 5건 이상 → 패턴 검토 필요
```

---

## 9. Phase별 마일스톤

### Phase 1 (현재)

- 5종 필터 모두 적용
- 단순 패턴 기반 (regex / 사전 / cosine)
- 한국어 단일

### Phase 4+

- LLM 기반 PII 잔존 위험 판정 (정확도 ↑)
- 자동 ad_phrase_blocklist 확장 (운영자 신고 학습)

### Phase 7+

- 다국어 지원 (en/ja 별도 필터)
- privacy_contract 정형화 후 PII 판정 강화

### Phase 11+

- 운영자 admin UI에서 필터 임계값 조정 가능
- 필터 결과 A/B 테스트

---

## 10. Open Questions

1. 길이 max 2000자 — 긴 케이스 스터디를 chunking 전 분할할지 INSERT 시 분할할지.
2. 중복 threshold 0.95 — 너무 엄격하면 유사 데이터 학습 효과 손실.
3. korean_ratio 0.4 임계 — 일부 외국어 용어 포함 영상기획(예: "vlog", "shorts")의 영향.
4. PII 잔존 위험 사전 (한국 흔한 이름 1000개) — 외국인 이름은?
5. 광고 단어 2차 경고를 promoted까지 끌고 갈지 (검색 노출 차단할지).
6. manual source_kind 중복 예외 — 무한 중복 가능. 횟수 상한 둘지.

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 5종 필터 (PII/광고/길이/언어/중복) 상세 정의,
                      임계치/예외/모니터링 추가.
```
