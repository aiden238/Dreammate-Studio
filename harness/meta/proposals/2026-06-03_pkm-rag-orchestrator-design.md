# Proposal: PKM/RAG Orchestrator — 계정별 PKM + 서버 공용 Wiki + Trend Snapshot + Instruction Search 통합

> 날짜: 2026-06-03
> 유형: **설계 제안 (proposal-only)** — ★ 코드/contract/migration/endpoint/schema **0 변경**. 본 문서는 제안서일 뿐, 전부 "제안".
> 작성 근거: 사용자 기획 + 13개 지정 문서 실측 (rag_data_contract §4/§18, knowledge/rag/* 4종, rag/feedback_to_candidate.py, 0004/0005 migration, ADR-025/031, llm_wiki/index.md, product/*)
> 대상 phase: **provisional P16~21 (잠정 — 선행조건 미충족 시 보류, 검증 후 재우선순위)**
> 절차: 실 착수 시 rag-design + ai-architecture-review + multi-llm-validation + contract-change 경유
> 상호참조: `meta/proposals/2026-06-03_commercial-viral-mode-design.md` (commercial_viral 모드의 market/trend 의존 = 본 문서 §5 trend_snapshot 레이어가 공급 — forward cross-ref)

---

## 0. ★★ 상태: PARKED / 선행조건 / provisional (최상위 framing)

### 0.1 상태 = PARKED (미래 방향, 지금 짓는 다음 빌드 **아님**)

본 proposal 은 **PARKED 미래 방향**이다. **지금 착수하는 다음 빌드가 아니다.** 메인 세션 객관 판정:

```
이유 1. MVP 실사용 미검증 — Phase 1~10 MVP(product/mvp_scope.md §4)의 end-to-end
        실사용/출시 검증이 아직 안 됨. 사용자 데이터 누적 0 → PKM 후보 source 자체가 비어 있음.
이유 2. 위저드 흐름 미완 — 랜딩(/)만 실동작. Discovery Wizard ↔ 백엔드 실연결 미통과.
        PKM 후보 source(feedback_events/final_outputs/agent_io_logs/human_review)는
        위저드↔백엔드가 실데이터를 흘려보내야 비로소 채워진다.
```

→ 따라서 본 문서는 **방향 보존 + 비충돌 설계 명세**이며, 즉시 구현 지시가 아니다.

### 0.2 선행조건 (PKM/RAG 빌드 착수 전 모두 충족 필수 — gate)

다음 **둘 다** 통과 전에는 PKM/RAG Orchestrator 빌드 착수를 **금지**한다:

```
선행조건 A. Phase 13 rich 출력 실사용 검증
   - CC-012(rich 슬롯 12종) + S2(P-006 rich 프롬프트 v1.1.0) 가 실제 운영 경로에서
     품질 향상을 입증 (depth_actionability 재측정 + human review).
선행조건 B. 위저드 ↔ 백엔드 실연결 통과
   - Discovery Wizard / Quick Mode 가 백엔드 /generate·/feedback 와 실연결되어
     feedback_events / selected_plans / final_output 이 실제로 누적되기 시작.
```

선행조건 미충족 시 → 본 제안 **보류 유지**. 충족 시 → 아래 §9 provisional 단계화를 **재우선순위 후** entry.

### 0.3 provisional (잠정) — 페이즈 번호 + 우선순위

- 본 문서의 **모든 페이즈 번호(P16~21)는 provisional(잠정)**이다. 확정 번호 아님.
- 선행조건(0.2) 충족 시점에 **재우선순위(re-prioritization)** 를 거쳐 실제 Phase 번호를 부여한다.
- commercial_viral 모드(상호참조) 진행 여부에 따라 §5 trend_snapshot 레이어 우선순위가 앞당겨질 수 있음.

### 0.4 핵심 비충돌 원칙 (절대 불변)

```
기존 candidate_knowledge 5단계 승격(rag_data_contract §4/§18)을 ★ 대체하지 않는다.
PKM/RAG Orchestrator 는 5단계를 source 중 하나로 "호출"하며, 그 "위에 얹는다"(additive, 비충돌).
5단계 / brand_memory_entries / rag_documents·approved_knowledge 는 전부 유지.
```

---

## 1. 요약 / 목표 / 비목표

### 1.1 요약

현재 RAG 자산은 **단일 전역 풀**이다: `candidate_knowledge`(5단계) → `approved_knowledge`(pgvector retrieval) + `brand_memory_entries`(prompt 직접 주입) + `rag_documents`/`rag_chunks`(Phase 1 계열). 본 제안은 이 자산을 **유지**하면서, 그 위에 **6개 scope 로 분리된 PKM/RAG Orchestrator** 레이어를 얹는다:

```
[기존 — 유지]                          [신규 제안 — 위에 얹기]
candidate_knowledge 5단계   ───소스 호출──▶  PKM/RAG Orchestrator
approved_knowledge (vector)  ◀──검색 소스──   ├─ 6 scope 분리 (개인/brand/series/global/trend/instruction)
brand_memory_entries         ◀──검색 소스──   ├─ retrieval orchestrator (DB+vector+BM25+instruction)
rag_documents/rag_chunks     ◀──검색 소스──   ├─ trend snapshot (단기 TTL)
                                              └─ context pack 조립 (trend_viral_director 등)
```

### 1.2 목표

```
1. candidate_knowledge 5단계 / brand_memory_entries / rag_documents 를 전부 "유지"한다.
2. 그 위에 6 scope (개인PKM / brandPKM / seriesPKM / globalWiki / trendSnapshot / instructionLibrary)
   레이어를 additive 로 얹는다 — 4계층(User→Brand→Domain→Series→Video)에 매핑.
3. 후보 source(feedback_events / final_outputs / agent_io_logs / human_review)를
   기존 5단계 진입점(candidate_knowledge pending)으로 흘려보내, 재사용 후 PKM/wiki 로 분기.
4. retrieval = DB filter + vector RAG + keyword/BM25 + instruction search 를 조합하는 orchestrator.
5. trend_snapshot 레이어가 commercial_viral 모드(상호참조)의 market/trend 의존을 공급.
6. trend_viral_director 등 모드별 "context pack" 을 scope 조합으로 조립.
```

### 1.3 비목표 (NON-GOALS — 본 제안이 하지 않을 것)

```
✗ 기존 5단계 승격 대체 — orchestrator 는 5단계를 "호출"만. 흐름 변경 0 (§3 비충돌).
✗ 자동 연결(자동 promotion) — feedback→PKM/wiki 의 자동 승격 절대 금지.
  적재는 candidate_knowledge pending 까지만(ADR-031 NG12 계승), 승격은 운영자 승인 후만(§8).
✗ user_locked memory 자동 갱신 — is_user_locked(0005 migration) 항목은 자동 갱신/덮어쓰기 금지(§6).
✗ 공용 wiki 에 원문 저장 — 익명화 패턴/구조만(§4). PII·사용자 원문 절대 전역 노출 0.
✗ 영상 제작 기능 — mvp_non_goals 영구 제외 계승 (본 제안 영상기획 PKM 한정).
✗ Custom RAG 인프라(Pinecone/Weaviate) / Graph RAG — pgvector + Supabase 유지 (Phase 21+ 별도).
✗ 코드/contract/migration 편집 — 본 문서는 전부 "제안". 실 변경은 각 절차 Skill 경유.
```

---

## 2. 6 scope 분리 표 (4계층 매핑)

> 4계층 데이터 모델(product/mvp_scope.md §1.2): **User → Brand → Domain → Series → Video Project**.
> 6 scope 는 이 계층에 **매핑**되며, 기존 자산(`auth_user_id` / `brand_id` 격리 — 0004/0005 migration)을 그대로 재사용한다.

| # | scope | 저장 대상 (무엇을) | 소유 (owner) | 4계층 매핑 | TTL / 보관 | 검색 우선순위 | 익명화 |
|---|---|---|---|---|---|---|---|
| 1 | **personal_pkm** (개인PKM) | 사용자 개인 선호·성공/거절 패턴·반복 신호 (계정 단위) | `auth_user_id` | **User** | 영구 (사용자 삭제 시 cascade) | **P1 (user_locked 최우선, §6)** | 본인 데이터 — 원문 보관 OK (RLS 격리, 전역 노출 X) |
| 2 | **brand_pkm** (brandPKM) | 브랜드 톤·금지어·선호 표현 (= 기존 brand_memory_entries 확장) | `brand_id` | **Brand** | 영구 | P2 | brand 내부 — brand 격리 (RLS) |
| 3 | **series_pkm** (seriesPKM) | 시리즈 단위 포맷·구조 패턴 (시리즈 일관성) | `series_id`(+brand_id) | **Domain→Series** | 영구 | P3 | brand 내부 |
| 4 | **global_wiki** (globalWiki) | 전 사용자 공용 영상기획 지식 (= 기존 llm_wiki + approved_knowledge external_seed/익명화 final_output) | 시스템(운영자) | (계층 무관 — 전역) | 영구 | P4 (보조) | **★ 원문 금지 — 익명화 패턴/구조만(§4)** |
| 5 | **trend_snapshot** (trendSnapshot) | 단기 트렌드 스냅샷 (emerging/peaking/declining) | 시스템 | (계층 무관 — 전역) | **단기 TTL (expires_at, §5)** | P-fresh (freshness 가중, §6) | 외부 신호 — 출처 표기, 원문 저장 금지(요약/패턴만) |
| 6 | **instruction_library** (instructionLibrary) | 운영자 작성 instruction/프롬프트 조각·정책 (instruction search 대상) | 시스템(운영자) | (계층 무관 — 시스템) | 영구 (버전) | P-inst (모드별 조립 시 결정) | 시스템 자산 — 사용자 데이터 아님 |

### 2.1 우선순위 충돌 규칙 (요약 — 상세 §6)

```
user_locked(personal_pkm 잠금 항목)  > 다른 모든 scope   # 사용자 명시 선호 최우선
personal_pkm > brand_pkm > series_pkm                     # 좁은 소유 우선 (개인 > 브랜드 > 시리즈)
trend_snapshot 는 freshness_score 로 가중 (모드별 — trend_viral_director 는 ↑↑)
global_wiki 는 보조(fallback) — 다른 scope 결과 부족 시 채움 (ADR-025 RAG>Wiki 정신 계승)
```

### 2.2 기존 자산과의 매핑 (재사용 — 신규 테이블 최소화)

```
brand_pkm        ← 기존 brand_memory_entries (0005) 를 그대로 재사용 (확장만, §8)
global_wiki      ← 기존 approved_knowledge(external_seed/익명화 final_output) + llm_wiki/index.md
personal/series  ← 신규 제안 pkm_entries (또는 brand_memory_entries 에 scope 컬럼 additive — §8 결정)
trend_snapshot   ← 신규 제안 trend_snapshots (단기 TTL — §5)
instruction      ← 신규 제안 instruction_index (instruction search — §6)
```

---

## 3. source → PKM 후보 흐름 (★ 5단계 비충돌)

### 3.1 핵심: orchestrator 는 5단계를 "대체"하지 않고 "호출"한다

```
[후보 source]                         [기존 5단계 — 유지·재사용]              [신규 분기]
feedback_events  ─┐                                                          ┌─▶ personal_pkm
final_outputs    ─┤                  candidate_knowledge                    ├─▶ brand_pkm
agent_io_logs    ─┼──build_candidate──▶  pending → filtered → evaluated ──▶ ├─▶ series_pkm
human_review     ─┘  (PII 마스킹)         → approved → promoted              ├─▶ global_wiki(익명화)
                     ★ ADR-031 NG12:       (rag-update 5단계 절차)            └─(trend 은 별도 §5)
                     pending 까지만 적재
                     자동 승격 X
```

- **진입점 재사용**: 후보 적재는 기존 `rag/feedback_to_candidate.py` 패턴 그대로 — `status='pending'` 고정, `rag.promotion.transition` 미호출(ADR-031 NG12). 즉 **자동 승격 0**.
- **5단계 통과 후 분기**: `promoted` 단계에서 비로소, candidate 의 `metadata.scope`(신규 제안 키)에 따라 6 scope 중 하나로 라우팅. 5단계 자체는 **흐름 변경 0**.
- **source 확장**: 기존 source_kind(`user_feedback`/`user_choice`/`final_output`/`manual`/`external_seed`)에 **`agent_io_logs`/`human_review`** 를 후보 source 로 추가 제안(§8). 적재 경로는 동일.

### 3.2 비충돌 표 (기존 vs 제안 — 무엇이 안 바뀌나)

| 항목 | 기존 (유지) | 제안 (위에 얹기) | 충돌? |
|---|---|---|---|
| 5단계 enum | `pending→filtered→evaluated→approved→promoted` (0004) | 그대로 호출 | ✗ 변경 0 |
| 적재 경로 | `feedback_to_candidate.py` pending 적재 | 동일 진입점 재사용 + source 2종 추가 | ✗ additive |
| 자동 승격 | 금지(ADR-031 NG12) | **금지 유지** (운영자 승인 후만, §8) | ✗ 동일 |
| brand_memory_entries | prompt 직접 주입 (RAG 우회) | brand_pkm scope 로 명명 + retrieval 소스로도 노출(선택) | ✗ additive |
| approved_knowledge retrieval | pgvector top_k=5 threshold=0.7 (ADR-025) | orchestrator 의 vector 단계로 호출 (래핑) | ✗ 래핑만 |
| promotion_history | append-only (0004) | 그대로 — scope 라우팅은 promoted 후 별도 | ✗ 변경 0 |

### 3.3 분기 규칙 (promoted → scope 라우팅)

```yaml
promoted candidate.metadata.scope 결정 (운영자 승인 시 부여):
  - auth_user_id 有 + 사용자 명시 선호      → personal_pkm (user_locked 후보)
  - brand_id 有 + 톤/금지어/선호표현 패턴   → brand_pkm (brand_memory_entries)
  - series_id 有 + 포맷/구조 반복            → series_pkm
  - PII 완전 제거 + 익명화 패턴 + 보편 가치  → global_wiki (★ 원문 금지, §4)
  - 외부 트렌드 신호                          → trend_snapshot (별도 파이프라인, §5)
  - 운영자 instruction/정책                   → instruction_library
```

---

## 4. 공용 wiki 익명화 규칙 (★ 원문 저장 금지)

### 4.1 절대 규칙

```
global_wiki(scope 4) 에는 사용자 원문(raw text)을 ★ 절대 저장하지 않는다.
저장 대상 = "익명화된 패턴/구조" 만. (rag_data_contract §1.10 "추출된 패턴/문장만 저장" 정신 계승·강화)
```

- 기존 `rag_data_contract §1.5/§1.10` 은 "promoted 항목은 추출된 패턴/문장만 저장(PII 우회)" 을 이미 명시. 본 제안은 이를 **global scope 한정으로 한 단계 더 엄격화**: 단순 PII 마스킹을 넘어, **개인 식별 가능 구조 자체를 제거**한 패턴만 허용.

### 4.2 익명화 파이프라인 (제안)

```
[사용자 원문 candidate] (auth_user_id/brand_id 有)
   │
   ▼  ① PII 마스킹 (기존 quality_filter.md §2 — 전화/이메일/주민/카드/IP) — 재사용
   │
   ▼  ② 잔존 위험 판정 (기존 quality_filter.md §2.2 — 이름+소속/주소/직책 조합) — 재사용
   │
   ▼  ③ ★ 신규: 패턴 추출 (de-identification)
   │     - 고유명사(브랜드명/제품명/인명/지명) → 일반 placeholder (예: "[브랜드]", "[제품]")
   │     - 수치/날짜/금액 → 일반화 (예: "구체 수치" → "특정 수치 강조")
   │     - 원문 문장 구조 → 패턴 라벨 (예: "질문형 hook + 반전 구조")
   │
   ▼  ④ ★ 신규: 원문-패턴 분리 검증 (패턴이 원문 복원 불가능함을 확인)
   │     - 패턴에서 원본 사용자/브랜드 역추적 불가 → pass
   │     - 역추적 가능 신호 잔존 → global_wiki 진입 거부 (brand_internal 로 강등 or reject)
   │
   ▼
[global_wiki entry] (auth_user_id=null, brand_id=null, access_scope='public')
   저장: 패턴/구조 라벨 + 익명화 요약만. 원문 0.
```

### 4.3 access_scope 연동 (기존 metadata_schema §2.2 재사용)

```
public          → global_wiki (익명화 패턴만 — 모든 사용자 검색 노출)
brand_internal  → brand_pkm (브랜드 내부 — 익명화 약함, brand 격리로 보호)
private         → personal_pkm (본인만 — 원문 OK, RLS 격리)
```

→ 기존 `metadata_schema.md §2.2` 의 access_scope 3종을 그대로 재사용. global_wiki = `public` 만 진입 가능하며, public 진입 = 익명화 파이프라인(§4.2) 통과 필수.

### 4.4 비충돌 확인

- 기존 5단계 PII 마스킹(`pending→filtered`, quality_filter §2)은 **그대로 유지**. 익명화 파이프라인은 그 **뒤에(promoted→global_wiki 분기 시점) 추가**되는 단계다. 5단계 내부 변경 0.

---

## 5. trend_snapshot 스키마 (단기 TTL)

> ★ commercial_viral 모드(상호참조 `2026-06-03_commercial-viral-mode-design.md`)의 market/trend 의존을 **본 레이어가 공급**한다.

### 5.1 스키마 (제안 — 신규 `trend_snapshots`)

```sql
-- ★ 제안 (미적용 — 실 적용은 contract-change + migration 절차)
CREATE TABLE trend_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic           TEXT NOT NULL,              -- 트렌드 주제 (익명화 — 원문 저장 X, 요약/패턴만)
    summary         TEXT NOT NULL,              -- 익명화 요약 (출처 표기, 원문 0)
    trend_stage     TEXT NOT NULL,              -- 'emerging' | 'peaking' | 'declining'
    freshness_score REAL NOT NULL,              -- 0.0~1.0, 신선도 (시간 경과에 따라 감쇠)
    captured_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,       -- ★ 단기 TTL (만료 후 검색 제외)
    source_ref      TEXT,                       -- 출처 참조 (URL/플랫폼 — 원문 캐싱 X)
    embedding       vector(1536),               -- pgvector (orchestrator vector 단계 호환)
    metadata        JSONB DEFAULT '{}'::jsonb,
    CHECK (trend_stage IN ('emerging','peaking','declining')),
    CHECK (freshness_score BETWEEN 0 AND 1)
);
CREATE INDEX idx_trend_expires ON trend_snapshots(expires_at);
CREATE INDEX idx_trend_stage   ON trend_snapshots(trend_stage);
```

### 5.2 TTL / 만료 정책 (제안)

```yaml
TTL 기본값 (trend_stage 별 — 단기):
  emerging:   expires_at = captured_at + 7일   (빠르게 변함, 짧게)
  peaking:    expires_at = captured_at + 14일  (활용 가치 최대 구간)
  declining:  expires_at = captured_at + 3일   (곧 무가치 — 매우 짧게)

freshness_score 감쇠:
  freshness_score = max(0, 1 - (now - captured_at) / (expires_at - captured_at))
  → captured 직후 1.0, 만료 시점 0.0 으로 선형 감쇠.

만료 처리:
  - 검색 단계에서 WHERE expires_at > now() 강제 (만료 즉시 검색 제외).
  - 만료 항목은 배치로 hard delete (보존 불필요 — 원문 0, 통계만 별도 집계).
  - ★ 자동 갱신/재캡처는 별도 파이프라인 (본 제안 범위 — 스키마+TTL만, 수집 로직은 후속).
```

### 5.3 trend_snapshot 의 비충돌·격리

- trend_snapshot 은 **기존 5단계와 별개 파이프라인**이다. candidate_knowledge 를 거치지 않는다(외부 신호 — 사용자 데이터 아님). 따라서 5단계 흐름과 충돌 0.
- 단 orchestrator 의 **vector 단계는 공유**: trend_snapshots.embedding 도 1536 dim(ADR-025 정합)으로, 동일 임베딩 모델 사용 → orchestrator 가 scope 통합 검색 가능.
- **원문 저장 금지**: summary/topic 은 익명화 요약만. source_ref 는 참조 링크만(원문 캐싱 X — 저작권·프라이버시).

### 5.4 commercial_viral 공급 인터페이스 (상호참조)

```
commercial_viral 모드 / trend_viral_director 가 요구하는 market/trend 의존:
  → orchestrator.retrieve(scope=['trend_snapshot'], stage_filter=['emerging','peaking'],
                          min_freshness=0.5)
  → 본 레이어가 freshness 가중 정렬된 trend pack 을 공급 (§7 context pack 예시 참조).
상호참조: meta/proposals/2026-06-03_commercial-viral-mode-design.md (해당 모드 설계가 단일 출처).
```

---

## 6. retrieval orchestrator (DB filter → vector → BM25 → instruction)

### 6.1 4단계 조합 파이프라인 (제안)

```
orchestrator.retrieve(query, *, scopes, owner_ctx, mode) :

 ① DB filter        : scope/owner/freshness 로 후보 모집단 축소
                       - scope ∈ {6종}, auth_user_id/brand_id/series_id 격리 (RLS 재사용)
                       - trend: expires_at > now() AND freshness_score ≥ min
                       - approved_knowledge.is_active / promoted 만 (기존 retrieval_policy §4 계승)
 ② vector RAG       : pgvector cosine (기존 ADR-025 retrieval.search 래핑)
                       - top_k=5 threshold=0.7 (기존 파라미터 — env tunable)
                       - scope 별로 호출 (personal/brand/series/global/trend 각각)
 ③ keyword / BM25   : ★ 신규 — sparse 검색 (정확 키워드·고유표현 매칭 보강)
                       - vector 가 놓치는 정확 용어(브랜드명·포맷명) 매칭
                       - ADR-025 에서 "BM25 hybrid = NG6 Phase 7+" 로 미룬 항목 — 본 레이어가 정식화 제안
 ④ instruction search: ★ 신규 — instruction_library 조회 (모드별 instruction 조각)
                       - mode(trend_viral_director 등) 에 맞는 instruction/정책 끌어옴
   │
   ▼
 [랭킹 / 머지]  : 4 채널 결과를 scope 우선순위 + freshness + similarity 로 통합 정렬
                  - user_locked 최우선 (아래 §6.2)
                  - 중복 제거 (기존 dedupe by content — ADR-025 §3 계승)
                  - scope 별 quota (예: personal ≤3, brand ≤2, global ≤2, trend ≤2)
   │
   ▼
 [context pack]  : 모드별 조립 규칙으로 최종 pack 구성 (§7 예시)
```

### 6.2 ★ user_locked 최우선 (절대 규칙)

```
personal_pkm 항목 중 is_user_locked = true (사용자가 명시 잠금) 는:
  - 랭킹에서 ★ 무조건 최상단 (similarity/freshness 무관하게 우선 주입).
  - 다른 scope 와 충돌 시 (예: brand_pkm 톤 vs user_locked 선호) → user_locked 승리.
  - ★ 자동 갱신/덮어쓰기 금지 — is_user_locked(0005 brand_memory_entries 컬럼) 정신 계승·확장.
    PKM 자동 추출/promotion 이 user_locked 항목을 변경하려 하면 차단(운영자 승인도 사용자 동의 필요).
```

→ 기존 `brand_memory_entries.is_user_locked`(0005 migration, "사용자 잠금 항목은 자동 갱신 금지 — Phase 10+") 를 **orchestrator 랭킹 최우선 규칙으로 승격**. 비충돌(기존 컬럼 의미 그대로, 적용 범위만 확장).

### 6.3 graceful (기존 ADR-025 §5 계승)

```
각 채널 독립 graceful — 한 채널 실패해도 pack 조립 차단 X:
  vector 실패      → warning 'rag_unavailable', 나머지 채널로 진행 (기존 retrieval.search 동작)
  BM25 실패        → warning 'bm25_unavailable', vector 결과로 진행
  trend 만료/0건   → warning 'no_fresh_trend', trend 없이 진행
  instruction 0건  → 모드 기본 instruction 으로 폴백
→ plan 생성 차단 0 (기존 V5 graceful 정신 계승).
```

### 6.4 비충돌·재사용 확인

- ② vector 단계는 기존 `rag/retrieval.py search()` 를 **래핑만** (재구현 X). top_k/threshold/dedupe/brand 격리 전부 기존 그대로.
- ① DB filter 의 격리는 기존 RLS(0004/0005)와 retrieval_policy §4 의 promoted/is_active 필터를 재사용.
- ③ BM25 / ④ instruction 만 신규. 기존 검색 정책(retrieval_policy.md)은 **vector 채널 정책으로 그대로 유효**, orchestrator 는 그 위 머지 레이어.

---

## 7. ★ trend_viral_director context pack 조립 예시 (구체)

> 구체 입력 1개에 대해, 어느 scope 에서 무엇을 끌어와 어떤 순서로 pack 을 조립하는지 실제 예시.

### 7.1 입력 (예시)

```json
{
  "mode": "trend_viral_director",
  "auth_user_id": "u-77a1",
  "brand_id": "b-카페브랜드",
  "series_id": "s-원두이야기",
  "approved_direction": "요즘 뜨는 '무인카페 브이로그' 포맷으로 신메뉴 원두를 후킹 강하게 소개",
  "query_text": "무인카페 브이로그 신메뉴 원두 후킹 | 원두이야기 | 카페"
}
```

### 7.2 orchestrator 조회 (scope 별 — DB filter → vector/BM25/trend/instruction)

| 순서 | scope / 채널 | 끌어온 것 (무엇을) | 적용 필터 | 결과 (예시) |
|---|---|---|---|---|
| 1 | **personal_pkm** (user_locked) | 사용자가 잠근 명시 선호 | `auth_user_id=u-77a1 AND is_user_locked=true` | "과한 자막 지양, 손글씨 톤 선호" (★ 최우선 고정) |
| 2 | personal_pkm (vector) | 본인 과거 성공 패턴 | `auth_user_id=u-77a1`, top_k cosine | "질문형 hook 3초 + 클로즈업" (sim 0.82) |
| 3 | **brand_pkm** (= brand_memory_entries) | 브랜드 톤·금지어 | `brand_id=b-카페브랜드` | preferred_tone="따뜻함", avoid_phrase="최저가"(광고차단 정합) |
| 4 | **series_pkm** | 시리즈 포맷 일관성 | `series_id=s-원두이야기` | "오프닝 5초 로스팅 b-roll 고정 포맷" |
| 5 | **trend_snapshot** (freshness 가중) | 신선 트렌드 | `stage∈{emerging,peaking} AND expires_at>now() AND freshness≥0.5` | "무인매장 브이로그 = peaking(fresh 0.78)", "ASMR 추출음 = emerging(0.91)" |
| 6 | **global_wiki** (보조 fallback) | 익명화 공용 패턴 | `access_scope=public`, 부족분만 | "브이로그 진정성 vs 연출 균형 패턴" |
| 7 | **instruction_library** | 모드 instruction | `mode=trend_viral_director` | "트렌드 stage 명시 + 후킹 강도 상향 + CTA 1개 고정" instruction |

### 7.3 랭킹 / 머지 (우선순위 적용 — §6.2)

```
[1] user_locked (personal)   ──▶ 무조건 최상단 1개 고정
[2] personal vector          ──▶ scope quota ≤3
[3] brand_pkm                ──▶ ≤2 (톤/금지어 — Critic brand_consistency 와도 정합)
[4] series_pkm               ──▶ ≤1 (포맷 1개)
[5] trend_snapshot           ──▶ freshness 내림차순 ≤2 (★ trend_viral_director 는 trend 가중 ↑↑)
[6] global_wiki              ──▶ 위 합산이 부족할 때만 채움 ≤2
[7] instruction              ──▶ pack 조립 규칙으로 별도 주입 (검색 결과 아님 — 지시문)
중복 제거(dedupe by content) + scope 별 quota 적용 → 최종 pack.
```

### 7.4 조립된 context pack (출력 예시 — P-006 prompt 주입용)

```json
{
  "mode": "trend_viral_director",
  "locked_preferences": [
    { "scope": "personal_pkm", "locked": true, "content": "과한 자막 지양, 손글씨 톤 선호" }
  ],
  "personal_patterns": [
    { "scope": "personal_pkm", "content": "질문형 hook 3초 + 클로즈업", "similarity": 0.82 }
  ],
  "brand_guide": [
    { "scope": "brand_pkm", "entry_type": "preferred_tone", "content": "따뜻함" },
    { "scope": "brand_pkm", "entry_type": "avoid_phrase", "content": "최저가" }
  ],
  "series_format": [
    { "scope": "series_pkm", "content": "오프닝 5초 로스팅 b-roll 고정" }
  ],
  "trends": [
    { "scope": "trend_snapshot", "topic": "ASMR 추출음", "trend_stage": "emerging", "freshness_score": 0.91 },
    { "scope": "trend_snapshot", "topic": "무인매장 브이로그", "trend_stage": "peaking", "freshness_score": 0.78 }
  ],
  "wiki_fallback": [
    { "scope": "global_wiki", "content": "브이로그 진정성 vs 연출 균형 패턴", "access_scope": "public" }
  ],
  "director_instruction": "트렌드 stage 명시 + 후킹 강도 상향 + CTA 1개 고정",
  "_warnings": []
}
```

### 7.5 다른 모드 대비 (조립 규칙만 다름 — 같은 orchestrator)

```
trend_viral_director : trend_snapshot 가중 ↑↑ + instruction(후킹/CTA) 강조 (위 예시).
brand_consistency_director(가정) : brand_pkm/series_pkm 가중 ↑, trend 가중 ↓.
→ scope 조회는 동일, "랭킹 quota + instruction" 만 모드별로 바뀐다 (orchestrator 1개, 모드 N개).
```

---

## 8. contract 변경안 (제안 — 전부 "제안")

> ★ 본 절은 **제안만**. 실 변경은 contract-change Skill + ai-architecture-review + multi-llm-validation 경유.

### 8.1 rag_data_contract.md 확장 (제안)

```
신규 §19 (제안): "PKM/RAG Orchestrator 레이어" 추가 — 기존 §4/§18 5단계 위에 얹는 6 scope.
  - §19.1  6 scope 정의 + 4계층 매핑 (본 문서 §2)
  - §19.2  source 확장: source_kind 에 'agent_io_logs' / 'human_review' 추가 (additive enum)
  - §19.3  promoted → scope 라우팅 규칙 (본 문서 §3.3)
  - §19.4  global_wiki 익명화 파이프라인 (본 문서 §4 — 원문 금지 강화)
  - §19.5  retrieval orchestrator (DB+vector+BM25+instruction, 본 문서 §6) — 기존 §5 retrieval 은 vector 채널로 유지
  - ★ 기존 §4/§18 5단계 본문은 변경 0 (additive 만).
```

### 8.2 신규 테이블 제안 (migration — 제안)

```sql
-- ★ 전부 제안 (미적용). 신규 3종 (additive only, 기존 0004/0005 불변):

-- (A) pkm_entries — personal/series scope (brand 은 기존 brand_memory_entries 재사용)
--     또는 대안: brand_memory_entries 에 scope 컬럼 additive (결정 사항 §8.5-1)
CREATE TABLE pkm_entries (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope         TEXT NOT NULL,        -- 'personal' | 'series'  (brand=기존 테이블)
    auth_user_id  UUID,                 -- personal 격리 (RLS)
    brand_id      UUID REFERENCES brands(id) ON DELETE SET NULL,
    series_id     UUID,                 -- series scope
    content       TEXT NOT NULL,
    entry_type    TEXT,                 -- brand_memory_entries enum 정합 (preferred_tone 등)
    is_user_locked BOOLEAN DEFAULT false,  -- ★ user_locked 최우선 (§6.2)
    confidence    REAL DEFAULT 0.5,
    embedding     vector(1536),
    source_candidate_id UUID,           -- promoted candidate 역추적
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    CHECK (scope IN ('personal','series'))
);

-- (B) trend_snapshots — §5.1 (단기 TTL)

-- (C) instruction_index — instruction search (§6 ④)
CREATE TABLE instruction_index (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mode        TEXT NOT NULL,          -- 'trend_viral_director' 등
    instruction TEXT NOT NULL,          -- 운영자 작성 instruction 조각
    version     TEXT NOT NULL DEFAULT 'v1.0.0',
    is_active   BOOLEAN DEFAULT true,
    embedding   vector(1536),
    metadata    JSONB DEFAULT '{}'::jsonb
);
```

### 8.3 ★ 자동 promotion 금지 (제안 — 명문화)

```
- feedback/agent_io_logs/human_review → candidate 적재는 pending 까지만 (ADR-031 NG12 계승).
- promoted → scope 분기는 ★ 운영자 승인 후에만 (rag-update 5단계 절차 통과 필수).
- PKM 자동 추출(P-AUX-2 brand_memory_extractor)이 활성화되어도, 그 산출(proposed_entries)은
  여전히 "제안" 상태 — 자동으로 personal/brand/series_pkm 에 쓰지 않는다 (ADR-031 §Decision 승격 경로 계승).
```

### 8.4 ★ user_locked 우선 (제안 — 명문화)

```
- is_user_locked=true 항목은 orchestrator 랭킹 최우선 + 자동 갱신/덮어쓰기 금지 (§6.2).
- 기존 brand_memory_entries.is_user_locked 의미를 pkm_entries 로 확장 (additive, 비충돌).
```

### 8.5 결정 필요 사항 (실 착수 시 사용자 승인)

```
1. personal/series scope 저장 = 신규 pkm_entries 테이블 vs brand_memory_entries 에 scope 컬럼 additive.
   (추천: brand 은 기존 테이블 재사용 + personal/series 는 신규 pkm_entries — 격리/RLS 명확)
2. source_kind enum 에 'agent_io_logs'/'human_review' 추가 = breaking 아님(additive)이나 contract-change 필요.
3. BM25 구현 = pg_trgm / tsvector(Postgres native) vs 외부 — pgvector 유지 원칙상 Postgres native 추천.
4. trend_snapshots 수집(캡처) 파이프라인 = 본 제안 범위 밖(스키마+TTL만). 수집 로직은 commercial_viral 설계와 동기.
5. instruction_index 버전 관리 = prompt_registry semver 패턴 재사용 여부.
```

---

## 9. 단계화 (provisional — ★ 선행조건 미충족 시 보류)

> ★ 페이즈 번호 전부 잠정(provisional). 선행조건(§0.2) 충족 + 재우선순위 후 확정.

### 9.1 provisional 단계 (잠정)

```
[GATE]  선행조건 A(Phase 13 rich 실사용 검증) + B(위저드↔백엔드 실연결) 통과 — 미충족 시 전체 보류.

P16~17 (잠정) — Orchestrator 1차: Trend + 개인/brand PKM
  - trend_snapshots 스키마 + TTL + freshness (§5)  ← commercial_viral 의존이 가장 급하면 이게 먼저
  - personal_pkm + brand_pkm(기존 brand_memory_entries 재사용) scope
  - retrieval orchestrator: DB filter + vector(기존 래핑) + 랭킹/머지 + user_locked 최우선 (§6)
  - trend_viral_director context pack 조립 (§7)
  - ★ BM25 / instruction / series / global 은 아직 (1차 = 핵심 3 scope + trend)

P20~21 (잠정) — Orchestrator 고도화: series / global / instruction
  - series_pkm + global_wiki(익명화 파이프라인 §4) scope
  - BM25 keyword 채널 (§6 ③) + instruction_library + instruction search (§6 ④)
  - 모드 확장 (trend_viral_director 외 다른 director 모드)
```

### 9.2 의존 / 보류 규칙

```
- commercial_viral 의존: §5 trend_snapshot 레이어는 commercial_viral 모드 설계와 동기화
  (상호참조 proposal). commercial_viral 이 먼저 가면 trend 레이어 우선순위 ↑ (재우선순위).
- 선행조건 미충족 시: 어느 단계도 착수 X (전면 보류). 본 문서는 방향 보존만.
- 재우선순위: GATE 통과 시점에 P16~21 잠정 번호를 실 Phase 번호로 재배정.
```

---

## 10. 리스크와 방어책

| 리스크 | 방어책 |
|---|---|
| **5단계 충돌** (orchestrator 가 5단계를 우회/대체) | orchestrator 는 5단계를 "호출"만 — promoted 후 분기. 5단계 enum/흐름 변경 0 (§3.2 비충돌 표). 적재는 기존 feedback_to_candidate 패턴 재사용 |
| **프라이버시** (사용자 원문 전역 노출) | global_wiki 원문 저장 금지 + 익명화 파이프라인(§4) + 역추적 불가 검증. access_scope public 진입 = 익명화 통과 필수. personal=RLS 격리(원문은 본인만) |
| **TTL** (만료 트렌드가 검색 오염) | 검색 단계 `WHERE expires_at > now()` 강제 + freshness 감쇠 + 만료 hard delete (§5.2). stage별 단기 TTL |
| **자동 promotion** (RAG 오염 / user_locked 덮어씀) | 자동 승격 금지(ADR-031 NG12 계승) + 운영자 승인 후만(§8.3) + user_locked 자동 갱신 금지(§6.2/§8.4) |
| **복잡도** (4채널 orchestrator 운영 부담) | provisional 단계화(§9): 1차=핵심 3 scope+trend, 고도화=BM25/instruction/series/global. graceful 채널 독립(§6.3) — 한 채널 실패해도 차단 0. 기존 retrieval.search 래핑(재구현 X) |
| **scope 격리 누락** (brand/user 데이터 교차 노출) | 기존 RLS(0004/0005 auth_user_id/brand_id) + retrieval 격리(ADR-025 §3) 재사용. DB filter 단계에서 owner 강제 |
| **선행조건 무시 조기 착수** | ★ 상태=PARKED + GATE(§0.2) 명문화 + provisional 번호. MVP 미검증/위저드 미완 시 보류 |
| **BM25 도입 scope creep** | Postgres native(pg_trgm/tsvector) 우선 — 외부 검색엔진 도입 X (pgvector 유지 원칙). 고도화 단계(P20~21)로 분리 |

---

## 11. 비충돌 / 우선순위 / 금지 요약 (최종 체크)

```
✓ 기존 5단계 비충돌  : orchestrator 가 5단계를 source 로 호출, 대체 X (§0.4 / §3 / §10).
✓ user_locked 최우선 : 랭킹 무조건 최상단 + 자동 갱신 금지 (§6.2 / §8.4).
✓ 자동 promotion 금지 : 적재 pending 까지만, 승격은 운영자 승인 후만 (§3.1 / §8.3).
✓ 공용 wiki 원문 금지 : 익명화 패턴/구조만, 역추적 불가 검증 (§4).
✓ trend 단기 TTL     : expires_at/freshness_score/trend_stage (§5).
✓ 6 scope + 4계층 매핑: User→Brand→Domain→Series 격리 재사용 (§2).
✓ director context pack: trend_viral_director 구체 조립 예시 (§7).
✓ 코드/contract/migration 0 수정 : 전부 "제안" — 실 변경은 각 절차 Skill 경유.
✓ 상태 PARKED + provisional + 선행조건 GATE (§0).
```

---

## 12. 다음 단계 (승인/검토 시)

```
1. 본 제안 검토 (메인 세션 + 사용자) — PARKED 유지 vs GATE 정의 확정.
2. (GATE 통과 후) rag-design + ai-architecture-review + multi-llm-validation 경유 → 재우선순위.
3. contract 변경(rag_data §19 / 신규 테이블)은 각 contract-change + ADR.
4. commercial_viral 설계(상호참조)와 trend 레이어 동기화.
```
