# roadmap.md — 제품 로드맵

> 위치: `product/roadmap.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `PHASE_REGISTRY.md` (22 Phase 매핑 원본)
> 참조: `product/mvp_scope.md`, `product/vision.md`, `product/pricing_model.md`

---

## 0. 로드맵 개요

본 로드맵은 `PHASE_REGISTRY.md`의 22 Phase를 **제품 관점**에서 재구성한다.

```
Phase 0       : 하네스 마이그레이션 (현재 진행)
Phase 1~10    : MVP (6~12개월)
Phase 11~20   : 안정화 + 확장 (12~24개월)
Phase 21~30   : 장기 확장 (24~36개월+)
```

각 Phase의 acceptance 후보 키워드 명시. 정식 acceptance는 Phase 진입 시 `phases/active/phase-N-*/acceptance.md`에 작성.

---

## 1. Phase 0 — 하네스 마이그레이션 (active, 현재)

```
기간:    2026-05 ~ 2026-06 (약 1개월)
목적:    GPT 골격 + 우리 콘텐츠 병합하여 운영 가능한 하네스 완성
Sprint: S0 (구조) → S1 (3 deep) → S2 (Skill 통합)
         → S3 (9 contracts deep + 11 placeholder)
         → S4 (eval / knowledge / ai_system)
         → S5 (product / meta / decisions / harness-audit)
acceptance 후보:
- migration_procedure.md v1.2.0 Sprint S0~S5 완료
- 9줄 stub 잔존 0건 (placeholder marker 또는 deep)
- harness-audit critical=0, high=0
- agent_html_spec v1.1.0+ 갱신
```

---

## 2. Phase 1~10 — MVP (6~12개월)

핵심 목표: **운영 가능한 영상기획 AI 에이전트 출시 + 사용자 100명 도달.**

### Phase 1 — 기본 플로우

```
기간:    1~2주
목적:    입력 → 기획 → 검증 → 저장의 end-to-end 흐름 (모형)
산출물: 단순 Next.js + FastAPI 로컬 동작
acceptance 후보 키워드:
- 영상기획 1건 end-to-end 동작 (수동)
- Supabase Auth 로그인 동작
- agent_io_logs 기록 시작
```

### Phase 2 — design.md 기반 PWA 설계

```
기간:    2~3주
목적:    Hybrid UX (Discovery + Quick) 화면 구조 확정
산출물: page_map.md, component_map.md
acceptance 후보:
- Discovery wizard 7단계 화면 설계 완료
- Quick mode 흐름 설계 완료
- Mode 자동 분기 규칙 명시
- 4계층 데이터 모델 ↔ 화면 매핑
```

### Phase 3 — Next.js PWA UI 구현

```
기간:    3~4주
목적:    Discovery + Quick + 비교 카드 UI 구현
산출물: 작동하는 PWA (백엔드는 mock)
acceptance 후보:
- Discovery 5단계 카드 동작 (4추천 + 1직접입력)
- Quick mode 화면 동작
- Direction Approval 카드 동작
- 3 plan 비교 카드 동작
- 4단계 progress stepper + 부분 결과 노출
```

### Phase 4 — FastAPI 기본 백엔드

```
기간:    2~3주
목적:    API 뼈대 + AI pipeline 골격
산출물: api_contract.md 준수하는 endpoint
acceptance 후보:
- 핵심 endpoint 5개 동작 (intent, plan, critic, save, feedback)
- error_response_contract envelope 준수
- request_id / trace_id 부착
```

### Phase 5 — DB / Auth 기본 구조

```
기간:    2주
목적:    Supabase + PostgreSQL 정착
산출물: db_schema.md 모든 테이블 생성
acceptance 후보:
- 4계층 데이터 모델 테이블 생성 (Brand / Domain / Series / Video)
- RLS policy 동작
- pgvector extension 활성화
- service role key 분리
```

### Phase 6 — Output Schema + Agent IO

```
기간:    2주
목적:    AI 입출력 안정화
산출물: output_schema.md validation 100%
acceptance 후보:
- agent_io_contract §3~§7 4 agent 모두 정의
- output_schema validation 통과율 95% 이상
- agent-io-check Skill 통과
```

### Phase 7 — RAG Lite 구현

```
기간:    3~4주
목적:    pgvector + candidate_knowledge 5단계 승격
산출물: rag_data_contract.md 동작
acceptance 후보:
- pgvector 검색 동작 (rag_chunks 시드 1000건)
- candidate_knowledge 5단계 흐름 (pending → promoted)
- quality_filter 동작
- 광고 단어 / PII 필터 100%
```

### Phase 8 — MOA Lite 구현

```
기간:    3~4주
목적:    Intent → Planning → Critic → Rewriter 동작
산출물: 4 agent 모두 작동
acceptance 후보:
- Intent agent (intent_filter 포함) 동작
- Planning agent 3 후보 생성
- Critic agent revise 최대 2회 강제
- Rewriter agent revise 결과 정상
- moa_policy.md 모든 정책 준수
```

### Phase 9 — 결과 저장 + 피드백 + Brand Memory

```
기간:    2~3주
목적:    저장 + 피드백 + Brand Memory 자동 추출
산출물: 결과 영구 저장 + memory_policy.md 동작
acceptance 후보:
- Video Project 영구 저장
- 사용자 선택 / 수정 / 반려 trace 기록
- Brand Memory 자동 추출 동작
- 사용자 수정 UI 동작
```

### Phase 10 — MVP 통합 테스트 + 출시 준비

```
기간:    3~4주
목적:    Beta 출시 + 사용자 100명
산출물: Beta staging 운영
acceptance 후보 (= MVP 출시 기준, mvp_scope.md §5):
- end-to-end 흐름 동작
- Golden Set 회귀 90% 이상 통과
- Critic 평균 점수 >= 0.70
- 광고 표현 차단 정확도 >= 95%
- PII / injection 차단 100%
- p95 응답 시간 60초 이하
- 일평균 영상 생성 50개 + 사용자 100명
- 사용자당 LLM 비용 <= $0.50/월
- Sentry 에러율 <= 1%
- 데이터 노출 사고 0건
```

---

## 3. Phase 11~20 — 안정화 + 확장 (12~24개월)

핵심 목표: **사용자 1만 명 + 유료 도입 + 협업 + 다국어 가능성.**

### Phase 11 — 모바일 PWA UX 강화

```
기간: 2~3주
acceptance 후보:
- 반응형 디자인 정밀화 (모바일 70% 사용자 가정)
- 터치 최적화 (스와이프 카드 등)
- next-pwa 설치 가능성 안정화
```

### Phase 12 — 유료 tier 도입

```
기간: 4~6주
acceptance 후보:
- 결제 인프라 (토스페이먼츠 또는 Stripe)
- paid tier ($9.99/월) 출시
- conversion funnel 동작
- 환불 정책 동작
- ARPU 측정 시작
```

### Phase 13 — 비동기 처리 (Celery / Arq)

```
기간: 3~4주
acceptance 후보:
- P-AUX-2 백그라운드 큐 도입
- 비동기 영상기획 (대기 60초+ 케이스)
- 큐 모니터링 / dead letter
```

### Phase 14 — A/B 실험 인프라

```
기간: 3주
acceptance 후보:
- prompt 변경 시 10% → 50% → 100% 자동 배포
- A/B 결과 자동 측정
- eval/multi_llm_results/ 자동 누적
```

### Phase 15 — 협업 기능 alpha

```
기간: 4~5주
acceptance 후보:
- 팀 단위 Brand 공유
- 권한 관리 (Owner / Editor / Viewer)
- 코멘트 + 멘션 기능
- team tier ($29.99/월) 출시
```

### Phase 16 — 다국어 (영어)

```
기간: 4~6주
acceptance 후보:
- 영어 UI 전체 번역
- 영어 prompt 세트 (P-001 ~ P-007 영어 버전)
- 영어 광고 표현 차단 사전
- 한국어 / 영어 자동 분기
```

### Phase 17 — API 공개

```
기간: 3~4주
acceptance 후보:
- 외부 도구 연동 API (paid+ tier)
- API rate limit + 인증
- API 사용량 dashboard
```

### Phase 18 — 운영자 대시보드

```
기간: 3주
acceptance 후보:
- 실시간 에러율 / 비용 / 사용량
- request_id 검색
- 사용자별 분석
```

### Phase 19 — 멀티 provider 라우팅

```
기간: 4주
acceptance 후보:
- Anthropic Claude 병행 지원
- Google Gemini 병행 지원
- 비용 / 품질 기반 자동 라우팅
- multi-llm-validation A/B
```

### Phase 20 — 안정화 마일스톤

```
기간: 2주
acceptance 후보:
- 사용자 1만 명 도달 확인
- 흑자 전환 확인 (ARPU + 비용 비교)
- 안정화 회고 (meta-retrospective)
- Phase 21+ 진입 결정
```

---

## 4. Phase 21~30 — 장기 확장 (24~36개월+)

핵심 목표: **Custom RAG + 글로벌 + 자체 모델 검토 + Spring Boot.**

### Phase 21 — Custom RAG 인프라

```
기간: 6~8주
acceptance 후보:
- Pinecone / Weaviate / 자체 중 선택
- migration plan (pgvector → custom)
- 사용자별 RAG 격리 (multi-tenant)
- enterprise tier 가능
```

### Phase 22 — Spring Boot 백엔드 후보 검토

```
기간: 4~6주
acceptance 후보:
- Spring Boot vs FastAPI 부하 테스트 비교
- multi-llm-validation 결과 정합
- 마이그레이션 비용 산정
- 진행 여부 결정 (다음 Phase로 갈지 또는 보류)
```

### Phase 23 — AWS 마이그레이션 (선택)

```
기간: 8~12주
acceptance 후보:
- Vercel → AWS Amplify or ECS
- Render → AWS ECS or EKS
- Supabase → AWS RDS (선택)
- 비용 / 성능 비교 후 결정
```

### Phase 24 — Expo React Native 앱

```
기간: 6~8주
acceptance 후보:
- iOS / Android 앱 출시
- App Store / Play Store 등록
- PWA → Native 사용자 이전
```

### Phase 25 — 일본어 / 동남아 확장

```
기간: 6~8주
acceptance 후보:
- 일본어 prompt + UI
- 동남아 (인도네시아 / 베트남) 검토
- 지역별 광고 단어 사전
```

### Phase 26 — 자체 모델 fine-tuning

```
기간: 8~12주
acceptance 후보:
- 영상기획 특화 fine-tuned 모델
- OpenAI 의존도 감소
- 비용 감소 검증 (50% 이상 목표)
```

### Phase 27 — Full MOA (5+ agent)

```
기간: 6주
acceptance 후보:
- 5+ agent 협업 (검증, 풍부화, 최적화 등 추가)
- LangGraph 또는 자체 orchestrator
- MOA Lite보다 품질 점수 +0.10 이상
```

### Phase 28 — Graph RAG

```
기간: 6~8주
acceptance 후보:
- 4계층 데이터 모델 ↔ Graph 변환
- Graph 기반 추천 (관련 Brand / Series 자동 추천)
- standard vector RAG 대비 정확도 +15%
```

### Phase 29 — 영상 분석 도구 연동

```
기간: 4~6주
acceptance 후보:
- 외부 영상 분석 API (YouTube Data API 등)
- 사용자 영상 input → 패턴 분석 → 기획 시드
- 영상 미리보기 (스토리보드 시각화)
```

### Phase 30 — 글로벌 마일스톤

```
기간: 2주
acceptance 후보:
- 사용자 10만 명 도달 확인
- 영어 + 일본어 + 한국어 + 1개 추가
- meta-retrospective + 비전 갱신 (2030년 비전)
```

---

## 5. 우선순위 / 의존성 매트릭스

다음 의존성이 강함 (앞 Phase 미완료 시 뒤 Phase 진입 불가).

```
Phase 1 → 2 → 3        : UX 흐름 (선형)
Phase 4 → 5 → 6        : 백엔드 + DB + Schema (선형)
Phase 7 → 8            : RAG가 MOA보다 먼저 (Planning이 RAG 의존)
Phase 9 → 10           : 저장 → 통합 테스트
Phase 12 → 15          : 결제가 협업보다 먼저 (team tier 매출)
Phase 21 → 26          : Custom RAG가 자체 모델보다 먼저
Phase 21 → 28          : Custom RAG가 Graph RAG보다 먼저
```

병렬 가능 (자원 충분 시 동시 진행).

```
Phase 11 ∥ Phase 12 ∥ Phase 13   (안정화 초반)
Phase 16 ∥ Phase 17               (다국어와 API 독립)
Phase 22 ∥ Phase 23 ∥ Phase 24    (인프라 / 앱 / 백엔드)
```

---

## 6. 마일스톤 (제품 관점)

```
M1: MVP 출시 (Phase 10 종료)
    - 사용자 100명, 일평균 50개 영상.

M2: 흑자 전환 (Phase 13~15 사이)
    - paid 전환율 5% + 사용자 5000명.

M3: 협업 도입 (Phase 15 종료)
    - team tier 출시 + 첫 enterprise 고객.

M4: 글로벌 alpha (Phase 16 종료)
    - 영어 사용자 1000명.

M5: 사용자 1만 (Phase 20 종료)
    - 안정화 완료.

M6: Custom RAG (Phase 21 종료)
    - enterprise tier 운영.

M7: 사용자 10만 (Phase 30 종료)
    - 글로벌 마일스톤.
```

---

## 7. 위험 / 가정

```
가정 1: MVP 6~12개월에 완성 가능.
        위험: Phase 4 (백엔드) / Phase 8 (MOA)에서 지연 가능.

가정 2: 사용자 100명 도달이 12개월 내 가능.
        위험: 마케팅 자원 부족 시 지연.

가정 3: paid tier 전환율 5% 도달 가능.
        위험: 무료 사용자 한도가 충분히 매력적이면 전환율 낮음.

가정 4: LLM 비용이 현재 수준 유지 또는 인하.
        위험: 가격 인상 시 가격 모델 재산정 필요.

가정 5: 한국어 사용자 30만 명 TAM.
        위험: 시장 추정 오차 가능. Phase 11+ 데이터로 재추정.
```

---

## 8. 로드맵 변경 절차

```
1. Phase 추가 / 제거 / 순서 변경 제안:
   - contract-change Skill 절차
   - PHASE_REGISTRY.md 동시 갱신
   - 영향 분석 (앞뒤 Phase 의존성)

2. acceptance 기준 변경:
   - 해당 Phase의 phases/active/*/acceptance.md만 갱신
   - 본 문서는 큰 변화만 반영

3. 마일스톤 / 타임라인 변경:
   - 분기별 phase-review Skill 시 검토
   - meta-retrospective Skill 기록
```

---

## 9. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 10 종료 시점: §2 MVP 결과 reflection (실 데이터 기반 Phase 11+ 조정).
Phase 20 종료 시점: §3 안정화 결과 reflection (Phase 21+ 조정).
Phase 30 종료 시점: 2030년 비전 갱신 + Phase 31+ 신규 추가.
```

---

## 10. Open Questions

1. Phase 1~10이 6~12개월에 정말 가능한지 — 자원 (인력) 가정 명시 필요.
2. Phase 13 (비동기)이 Phase 11/12보다 우선해야 할 가능성 — 대기 시간이 conversion 차단 요인이면.
3. Phase 16 (영어)이 Phase 15 (협업)보다 우선해야 할 가능성 — 영어 시장 진입이 매출에 더 큰 영향이면.
4. Phase 21 (Custom RAG)와 Phase 22 (Spring Boot)의 순서 — 인프라 우선 vs 백엔드 우선.
5. Phase 26 (자체 모델) 진입 트리거 — LLM 비용이 매출의 몇 % 도달 시.
6. M2 흑자 전환 시점 예측 정확도 — 가정 변경 시 marketing 전략 재구성.

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      Phase 0~30 (총 31 Phase, MVP 1~10 / 안정화 11~20 / 확장 21~30)
                      각 Phase의 acceptance 키워드, 의존성 매트릭스, 7 마일스톤.
```
