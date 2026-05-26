# internal_generated_data.md — 내부 생성 데이터

> 위치: `knowledge/datasets/internal_generated_data.md`
> 데이터 흐름: 사용자 입력 + LLM 출력 → candidate_knowledge
> 연계: `rag_data_contract.md` §8 (학습 신호), `knowledge/rag/promotion_rule.md`, `db_schema.md` §7

---

## 0. 정의

**내부 생성 데이터**: 영상기획 AI 에이전트 운영 과정에서 **사용자 입력 + LLM 출력**으로 생성되는 데이터. 외부 시드 데이터(`external_seed_data.md`)와 대비된다.

```
주요 source_kind:
  - final_output    (사용자 최종 영상기획안)
  - user_choice     (Discovery 카드 선택)
  - user_feedback   (like / dislike)

저장 위치:
  - 1차: db_schema 운영 테이블 (video_projects / discovery_choices / feedback_events)
  - 2차: candidate_knowledge (RAG 후보 진입)
  - 3차: rag_chunks (5단계 승격 후)
```

---

## 1. 데이터 흐름

```
[사용자 입력 / 선택 / 피드백]
   │
   ▼
[운영 테이블 INSERT]
   - discovery_choices / video_projects / feedback_events
   │
   ▼  자동 트리거 또는 정기 배치
   │
[candidate_knowledge INSERT (status='pending')]
   - source_kind = 'final_output' | 'user_choice' | 'user_feedback'
   │
   ▼  5단계 승격 (rag_data §4)
   │
[rag_chunks INSERT (검색 대상)]
```

---

## 2. source_kind 별 진입 흐름

### 2.1 final_output (가장 신뢰도 높음)

```
트리거: video_projects.status → 'final' 전이

추출 패턴 (rag_data §8.3):
  - final_output.hook → candidate 1건
  - final_output.structure[i] → candidate i건
  - final_output.shooting_notes → candidate 1건 (선택)

조건:
  - quality_score_avg (Critic 8차원 평균) ≥ 4.0
  - PII 마스킹 통과
  - 광고 단어 1차 차단 없음

자동 승격:
  - rag_data §4.3 자동 승격 조건 충족 시 가능
```

### 2.2 user_choice (반복 신호 기반)

```
트리거: discovery_choices INSERT

조건 (rag_data §8.1):
  - selected_card.confidence ≥ 0.7
  - 동일 brand_id에서 같은 카드 누적 ≥ 3회
  - direct_input is null (AI 추천 채택 신호)

추출 형식:
  content = selected_card.name + " — " + selected_card.description
  metadata = {step_name, brand_id, domain_id, series_id, confidence}

자동 승격: 불가 (사용자 PII 위험 → 항상 수동 검수)
```

### 2.3 user_feedback (긍정 신호)

```
트리거: feedback_events.event_type='like' AND target_kind='final'

조건 (rag_data §8.2):
  - 좋아요한 final_output 만 (dislike는 별도 처리)
  - 추출: hook + structure 첫 단계 (전체 영상기획 X)

자동 승격: 불가 (수동 검수)
```

---

## 3. 데이터 누적 추정

### 3.1 Phase 1 (사용자 100-1000명)

```yaml
사용자 1000명 × 월 평균 5건 영상기획 = 월 5000건
  - final_output (status='final'): 약 70% = 3500건
  - 추출 candidate per final = 3-5건
  - 월 candidate from final_output: ~12000-17500건

사용자 선택 카드:
  - 평균 Discovery 단계 4단계 × 카드 선택 = 4건
  - 1000명 × 5세션 × 4 = 20000건/월
  - 자동 INSERT 조건 충족 비율: 5-10% = 1000-2000건/월

피드백:
  - 영상기획 1건당 평균 0.3건 피드백
  - 5000 × 0.3 = 1500건
  - like 비율 70% = 1050건/월

총 candidate INSERT (월):
  ~ 15000-20000건
```

### 3.2 5단계 승격 후 chunks 누적

```
candidate → promoted 비율 (예상):
  - pending → filtered: ~70% (PII / 광고 / 중복 등 30% rejected)
  - filtered → evaluated: ~80% (LLM 평가)
  - evaluated → approved: ~40% (자동 승격 + 운영자 검수)
  - approved → promoted: ~95% (ETL 실패율 낮음)
  
종합 (pending → promoted):
  0.7 × 0.8 × 0.4 × 0.95 ≈ 21%

월 promoted chunks: ~3000-4000건
월 chunks 누적 (chunking 후 평균 1.5배): ~4500-6000개
연 누적: ~50000-70000 chunks
```

### 3.3 Phase 7+ 사용자 10000명

```
월 candidate INSERT: ~150000-200000건
월 promoted chunks: ~30000-45000개
연 누적: ~500K chunks

→ pgvector 인덱스 재구축 검토 임계 (rag_data §7.2)
→ sdk_rag_policy 전환 검토 (custom_rag_plan §1 트리거 근접)
```

---

## 4. 보존 정책

`db_schema.md` §10 정합 + `rag_data §4` 보관 기간:

```yaml
운영 테이블:
  video_projects (status='final'): 영구
  discovery_choices: 1년 (이후 익명화)
  feedback_events: 1년 (이후 익명화)

candidate_knowledge:
  pending: 90일
  filtered: 60일
  evaluated: 60일
  approved: 영구
  promoted: 영구 (user_id는 30일 후 익명화)
  rejected: 90일 후 hard delete

rag_chunks:
  promoted: 영구 (회수 시 is_active=false, hard delete는 운영자 결정)
```

### 4.1 익명화 시점

```
final_output → 30일 후:
  metadata.user_id = "anon_" + hash(user_id, salt)
  metadata.brand_id 는 유지 (브랜드 단위 통계 위해)

user_choice → 30일 후:
  metadata.user_id 익명화 + metadata.direct_input 마스킹 (입력했었으면)

user_feedback → 30일 후:
  metadata.user_id 익명화 + metadata.feedback_text 마스킹
```

---

## 5. PII 위험 관리

`rag_data §9` 정합. 내부 생성 데이터는 사용자 PII 노출 위험 ↑:

```yaml
1차 자동 마스킹:
  - 전화번호 / 이메일 / 주민번호 / 카드번호 / IP
  - candidate INSERT 직전 적용

2차 잔존 위험 판정:
  - 이름 + 학교 + 학번 조합
  - 이름 + 주소(시/구/동)
  - 이름 + 직책 + 회사
  → 발견 시 rejected('pii_residual')

3차 user_choice / user_feedback 보호:
  - 자동 승격 불가 (항상 수동 검수)
  - 운영자가 직접 한 번 더 확인
```

---

## 6. 데이터 정합성

### 6.1 운영 테이블 ↔ candidate_knowledge 연결

```sql
-- candidate_knowledge.source_id가 운영 테이블 row를 참조
candidate.source_id =
  case source_kind
    when 'final_output' then video_projects.video_id
    when 'user_choice' then discovery_choices.choice_id
    when 'user_feedback' then feedback_events.feedback_id
  end
```

원본 운영 테이블 row가 삭제되면 candidate 도 cascade 처리 (db_schema §10 정합).

### 6.2 chunks ↔ candidate 연결

```sql
-- promoted candidate는 promoted_chunk_id로 chunks 참조
candidate.promoted_chunk_id → rag_chunks.chunk_id (첫 chunk만 대표)
```

회수 시 양방향 업데이트:
- candidate.status='rejected'
- rag_documents.is_active=false (chunks는 유지)

---

## 7. 학습 신호 강도

source_kind 별 학습 신호 신뢰도 (sources.md §7 정합):

```
final_output:      1.0 (기준값, 사용자가 최종 확정)
user_feedback:     0.9 (긍정 신호이나 자동 추출 패턴)
user_choice:       0.8 (단순 선택 신호)
external_seed:     1.2 (운영자 검증된 외부 사례, 비교)
manual:            1.1 (운영자 직접 입력)
```

Phase 4+ reranking 가중치에 반영.

---

## 8. 운영 모니터링

```yaml
일일 지표:
  - candidate INSERT 수 per source_kind
  - 5단계별 통과율 (퍼널)
  - rejected 사유 분포
  - 자동 vs 수동 승격 비율

주간 지표:
  - promoted chunks per source_kind
  - 검색 시 자주 사용된 chunks (rag_used 통계)
  - 사용자 brand별 누적 chunks 수

월간 지표:
  - 데이터 품질 trend (eval_score 분포)
  - PII rejected 비율 (마스킹 강화 필요 여부)
  - 광고 단어 rejected 비율
```

---

## 9. Phase별 마일스톤

### Phase 1 (현재)

- 3 source_kind 자동 INSERT
- 5단계 승격 흐름
- 운영자 SQL 직접 검수

### Phase 4+

- 운영자 admin UI (검수 큐)
- 자동 익명화 정책 활성화
- 데이터 누적 trend 분석

### Phase 7+

- privacy_contract 정형화 후 PII 강화
- 사용자별 개인화 (검색 가중치)
- 사용자 본인 데이터 export / delete

### Phase 11+

- 대규모 누적 (500K+ chunks)
- pgvector → custom RAG 전환 검토
- A/B 테스트 (자동 승격 임계값)

---

## 10. Open Questions

1. candidate 진입 비율 — final_output 70%로 가정했으나 실제 사용자 행동 데이터 필요.
2. quality_score_avg ≥ 4.0 임계 — 너무 엄격하지 않은지.
3. user_choice 자동 승격 가능성 — PII 강화 후 일부 허용?
4. 익명화 30일 — 너무 짧거나 길지 않은지 (학습 신호 보존 vs PII).
5. 운영자 검수 큐 우선순위 (rag_data 정의) — 데이터 누적 후 재조정.
6. dislike 신호 활용 — negative example로 RAG에 넣을지 (rag_data §16 Open Q 정합).

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Sprint S4-2 초안. 3 source_kind 흐름, 데이터 누적 추정,
                      보존/익명화 정책, PII 위험 관리, 학습 신호 강도, 모니터링.
```
