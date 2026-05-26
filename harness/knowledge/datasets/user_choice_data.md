# user_choice_data.md — 사용자 선택 데이터

> 위치: `knowledge/datasets/user_choice_data.md`
> source_kind: `user_choice`
> 연계: `db_schema.md` §7 `choice_logs` / `discovery_choices`, `rag_data_contract.md` §8.1

---

## 0. 정의

**사용자 선택 데이터**: 사용자가 Discovery 5단계 또는 Quick Mode에서 **AI가 제안한 카드 / plan_option 중 선택**한 신호 데이터.

```
주요 테이블:
  - discovery_choices: Discovery 5단계 카드 선택
  - choice_logs:       범용 선택 로그 (plan_option / variant 등)

운영자가 묻는 질문:
  - 어떤 카드를 선택했는지?
  - 어떤 plan_option을 골랐는지?
  - 얼마나 망설였는지 (선택 시간)?
  - 몇 번 재시도했는지?
```

---

## 1. 데이터 출처 매핑

### 1.1 discovery_choices 테이블

```sql
-- db_schema §7 정합
create table discovery_choices (
    choice_id      uuid primary key default gen_random_uuid(),
    session_id     uuid not null,
    user_id        uuid not null,
    brand_id       uuid,
    step_name      text not null,           -- 'intent', 'target', 'tone', ...
    cards_shown    jsonb not null,          -- AI가 제안한 카드 목록
    selected_card  jsonb,                   -- 선택한 카드 (또는 null)
    direct_input   text,                    -- 사용자가 직접 친 답변 (또는 null)
    decision_ms    int,                     -- 선택까지 걸린 시간 (ms)
    retry_count    int default 0,           -- 카드 재생성 횟수
    created_at     timestamptz default now()
);
```

### 1.2 choice_logs 테이블 (범용)

```sql
create table choice_logs (
    log_id         uuid primary key default gen_random_uuid(),
    user_id        uuid,
    brand_id       uuid,
    video_id       uuid,
    target_kind    text not null,           -- 'discovery_card' | 'plan_option' | 'variant'
    target_id     uuid,                    -- 선택된 항목 ID
    options_shown  jsonb,                   -- 제안된 옵션들
    decision_ms    int,
    metadata       jsonb default '{}'::jsonb,
    created_at     timestamptz default now()
);
```

---

## 2. 학습 신호 종류

### 2.1 선택률 (selection_rate)

```
정의: AI가 제안한 카드 중 사용자가 선택한 비율

높음 (≥ 80%):
  - AI 추천 품질 양호
  - 해당 패턴 강화 학습 신호

낮음 (< 30%):
  - AI 추천 품질 저하
  - direct_input 비율 높을 가능성
  - prompt-version-review 트리거
```

### 2.2 선택 시간 (decision_ms)

```
정의: 카드 노출 후 선택까지 걸린 시간

빠름 (< 3초):
  - 명확한 선택 (강한 선호)
  - 또는 무관심 (대충 선택)

보통 (3-15초):
  - 정상 검토 패턴

느림 (> 15초):
  - 망설임 (여러 카드 매력적)
  - 또는 혼란 (카드 모호)

매우 느림 (> 60초):
  - 사용자 이탈 가능성
  - prompt 개선 필요
```

### 2.3 재시도 횟수 (retry_count)

```
정의: 사용자가 "다른 카드 보여줘" 요청한 횟수

0회 (선택 즉시):
  - 첫 추천 만족 (이상적)

1회:
  - 일부 카드 매력적이나 다양성 원함

2-3회:
  - AI 추천이 패턴 못 잡고 있음

≥ 4회:
  - prompt 품질 문제 (개선 필요)
  - 또는 사용자 의도 모호
```

---

## 3. candidate_knowledge 진입 조건

`rag_data §8.1` 정합:

```yaml
INSERT 조건 (모두 충족):
  - selected_card.confidence ≥ 0.7
  - 동일 brand_id에서 같은 카드 누적 ≥ 3회 (반복 신호)
  - direct_input is null (AI 추천 채택 신호)

미충족 시:
  - candidate INSERT 안 함
  - choice_logs 운영 테이블에만 기록 (학습 통계용)

자동 승격: 불가 (PII 위험 → 항상 수동 검수)
```

---

## 4. 추출 형식

```python
def extract_candidate_from_choice(choice):
    content = (
        choice.selected_card["name"]
        + " — "
        + choice.selected_card["description"]
    )
    metadata = {
        "step_name": choice.step_name,
        "brand_id": choice.brand_id,
        "domain_id": choice.domain_id,
        "series_id": choice.series_id,
        "video_id": choice.video_id,
        "confidence": choice.selected_card["confidence"],
        "decision_ms": choice.decision_ms,
        "retry_count": choice.retry_count
    }
    return {
        "source_kind": "user_choice",
        "source_id": choice.choice_id,
        "content": content,
        "metadata": metadata
    }
```

---

## 5. 익명화 정책

`db_schema §10` 정합:

```yaml
원본 (discovery_choices / choice_logs):
  - user_id 유지 (1년)
  - 1년 후 user_id = anon_<hash>
  - direct_input은 30일 후 마스킹 (PII 위험)

candidate_knowledge (RAG 진입 시):
  - user_id 메타데이터 30일 후 익명화
  - brand_id는 유지 (브랜드 통계)

rag_chunks (promoted 후):
  - user_id 없음 (이미 metadata에 ID만)
  - brand_id 유지
```

---

## 6. 사용처

### 6.1 prompt-version-review (A/B)

```
선택률 / 선택 시간 / 재시도 횟수를 prompt 버전별 비교:
  - v1 prompt: 선택률 75% / 평균 8초 / 평균 0.5회 재시도
  - v2 prompt: 선택률 85% / 평균 5초 / 평균 0.2회 재시도
  → v2 채택

자세한 절차는 ai_system/prompts/prompt_registry.md 참조.
```

### 6.2 Brand Memory 추출 보조 (P-AUX-2)

```
사용자가 일관되게 같은 카드 패턴 선택 시:
  - brand_memory.tone_profile 강화
  - brand_memory.vocabulary 누적
  - brand_memory.avoid_patterns (거절 카드)

P-AUX-2 prompt가 choice_logs 분석 후 brand_memory entry INSERT.
```

### 6.3 RAG 학습 (간접)

```
candidate → promoted 거치면 검색 대상.
선택률 높은 카드 패턴이 RAG에 누적 → 다음 사용자에게도 추천 우선.
```

### 6.4 운영자 분석

```
- 선택률 낮은 카드 → prompt 개선 우선순위
- 재시도 많은 단계 → UI 개선 필요
- 빠른 선택 → 명확한 추천 (긍정)
- 느린 선택 → 카드 다양성 부족 또는 모호
```

---

## 7. 데이터 누적 추정

### 7.1 Phase 1 (사용자 1000명)

```
Discovery 5단계 × 평균 4 카드 노출:
  사용자당 세션: 5단계 × 4 카드 = 20 노출 / 5 선택
  월간 (사용자 1000명 × 평균 5 세션):
    카드 노출: 1000 × 5 × 20 = 100K
    카드 선택: 1000 × 5 × 5 = 25K
  
choice_logs INSERT: 25K/월

candidate_knowledge 진입 (자동 INSERT 조건 충족 비율 5-10%):
  candidate INSERT: ~1250-2500/월
```

### 7.2 Phase 7+ (사용자 10000명)

```
choice_logs INSERT: 250K/월
candidate INSERT: ~12500-25000/월

→ 대규모 학습 신호 활용 가능
```

---

## 8. PII / 개인정보 정책

```yaml
discovery_choices.direct_input:
  - 사용자가 카드 대신 직접 친 답변
  - PII 위험 높음 (이름 / 회사명 / 학교 등 가능)
  - 30일 후 자동 마스킹

discovery_choices.metadata:
  - brand_id / domain_id / session_id 등 ID만
  - PII 직접 노출 없음

candidate 진입 시:
  - direct_input은 candidate content에 포함 안 함
  - selected_card의 정형화된 텍스트만 사용
  → PII 위험 ↓
```

---

## 9. 모니터링

```yaml
일일 지표:
  - choice_logs INSERT 수
  - 선택률 per step_name
  - 평균 decision_ms per step
  - 재시도 횟수 분포

주간 지표:
  - candidate 진입 비율
  - 자주 선택된 카드 top 20
  - 거의 안 선택되는 카드 (prompt 개선 후보)

월간 지표:
  - prompt 버전별 비교 (A/B)
  - brand_memory 추출 수
```

---

## 10. Phase별 마일스톤

### Phase 1 (현재)

- discovery_choices / choice_logs INSERT
- 자동 candidate 진입 조건
- 운영자 SQL 분석

### Phase 4+

- prompt-version-review A/B 자동화
- brand_memory 자동 추출 정확도 향상

### Phase 7+

- 사용자별 개인화 학습 (개인 선호 누적)
- 사용자 본인 선택 history export

### Phase 11+

- 운영자 admin UI에서 선택 데이터 시각화
- 실시간 prompt 품질 모니터링

---

## 11. Open Questions

1. selected_card.confidence ≥ 0.7 임계 — 너무 엄격한지.
2. 동일 카드 누적 ≥ 3회 — 너무 보수적인 기준일 수 있음.
3. direct_input의 PII 마스킹 30일 — 더 짧게 (7일) 검토 필요.
4. 선택 시간 (decision_ms) 의 학습 신호 활용 — 정확도 검증.
5. 사용자별 개인화를 RAG에 어떻게 반영할지 (Phase 7+).
6. dislike된 카드(거절 패턴)를 negative example로 사용할지.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. discovery_choices / choice_logs 매핑,
                      학습 신호 3종 (선택률/시간/재시도), candidate 진입 조건,
                      4 사용처 (A/B / brand_memory / RAG / 운영자 분석).
```
