# mvp_scope.md — MVP 범위 정의

> 위치: `product/mvp_scope.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/mvp_non_goals.md` (영구 제외 목록)
> 참조: `docs/contracts/product_boundary.md`, `PHASE_REGISTRY.md`
> 참조: `product/vision.md`, `product/positioning.md`, `product/roadmap.md`

---

## 0. MVP 정의

```
MVP = Phase 1~10에서 출시할 영상기획 AI 에이전트의 첫 운영 가능 버전.
기간: 6~12개월 (Phase 0 종료 후 시작).
출시 형태: Next.js 14 PWA + FastAPI + Supabase (PostgreSQL + pgvector).
초기 사용자 가설: 1인 마케터 / 소규모 브랜드 / 콘텐츠 크리에이터.
```

→ Phase 11+ 안정화 / Phase 21+ 확장은 본 문서 범위 밖 (`product/roadmap.md`).

---

## 1. MVP 포함 범위 (반드시 출시)

### 1.1 UX 핵심

```
✓ Discovery Wizard 5단계 카드 (4추천 + 1직접입력)
✓ Quick Mode (짧은 프롬프트 + 1~2 부족 정보 질문)
✓ 자동 모드 분기 (Brand/Domain/Series 컨텍스트 유무 판단)
✓ 한 줄 기획 방향 승인 카드
✓ 4단계 progress stepper (Intent → RAG → Plan → Critic) + 부분 결과 노출
✓ 영상기획안 3개 비교 카드 + 사용자 1개 선택
```

### 1.2 데이터 모델

```
✓ 4계층 데이터 모델: User → Brand → Domain → Series → Video Project
✓ Brand Memory 자동 추출 (사용자 검토 가능)
✓ 사용자 피드백 저장 (선택 / 수정 / 반려 trace)
```

→ `docs/contracts/db_schema.md`

### 1.3 AI 시스템

```
✓ MOA Lite: Intent → Planning → Critic → Rewriter
✓ Critic revise 최대 2회 (무한 루프 차단)
✓ RAG Lite: candidate_knowledge 5단계 승격 파이프라인
✓ Intent Filter (영상기획 외 입력 차단)
✓ PII 마스킹 + 프롬프트 인젝션 차단 (자동 2단계 검사)
✓ 광고적 표현 차단 단어 검사 (출력 + 사용자 입력 양쪽)
```

→ `ai_system/architecture.md`, `docs/contracts/agent_io_contract.md`, `docs/contracts/llm_security_contract.md`

### 1.4 인프라

```
✓ Next.js 14 PWA (next-pwa, 오프라인 미지원)
✓ FastAPI + Pydantic v2 + SQLAlchemy 2.x
✓ Supabase Auth (email + Google/GitHub OAuth)
✓ PostgreSQL 15 + pgvector (1536 차원)
✓ Redis (rate limit, idempotency, 비용 누적)
✓ OpenAI gpt-4o-mini 기본 + gpt-4o (Critic만)
✓ Sentry 에러 추적
✓ rate_limit_policy (anonymous 5회/일, free tier 50회/월)
```

→ `docs/contracts/tech_stack_contract.md`, `docs/contracts/rate_limit_policy.md`

### 1.5 평가 / 운영

```
✓ Golden Set 회귀 평가 (11+ 케이스, eval/golden_set.md)
✓ video_planning_eval (영상기획 품질 6 차원)
✓ regression_eval (Phase 진입/배포 직전 자동)
✓ human_review 절차 (candidate_knowledge 승격 일부 단계)
✓ agent_io_logs / intent_filter_logs 운영 로그
```

→ `eval/`, `meta/human_review_policy.md`

---

## 2. MVP 제외 범위 (영구 제외)

영상 제작 기능은 **MVP뿐 아니라 본 서비스 전체에서 영구 제외.**
변경하려면 `contract-change` Skill + `multi-llm-validation` 절차 필수.

```
✗ 영상 자동 생성 / 자동 편집
✗ TTS (Text-to-Speech) 생성
✗ BGM 자동 삽입
✗ 자막 자동 합성
✗ 이미지 / 영상 소스 자동 생성
✗ 컷 편집 자동화
✗ 쇼츠 자동 조립
✗ YouTube / Instagram 자동 업로드
```

→ `docs/contracts/mvp_non_goals.md`, `docs/contracts/product_boundary.md`

이유:

```
1. 우리는 영상 제작이 아닌 영상기획 AI다 (vision.md 정합).
2. 영상 제작은 이미 충분히 많은 도구가 존재 (CapCut, Runway 등).
3. 영상 제작 자동화는 비용·인프라 부담이 크다 (GPU, 스토리지).
4. 기획 품질에 집중하는 것이 우리의 차별 가치.
```

---

## 3. MVP 제외 범위 (MVP 후 도입 가능)

영구 제외는 아니지만 MVP에서는 다루지 않음. Phase 11+ 또는 21+ 검토.

```
~ 모바일 네이티브 앱 (Expo React Native)
    → Phase 21+ 검토. MVP는 PWA로 모바일 친화 충족.

~ 협업 기능 (팀 단위 Brand 공유, 코멘트, 권한 관리)
    → Phase 11+ 검토. MVP는 단일 사용자 가정.

~ 다국어 (영어, 일본어)
    → Phase 21+ 글로벌 진출 시 검토. MVP는 한국어만.

~ 결제 / 유료 tier
    → Phase 11+ 검토. MVP는 무료 (사용량 제한).

~ 외부 도구 연동 (CapCut, Notion, Figma 등)
    → Phase 11+ 검토.

~ 영상 분석 도구 (영상 입력 → 패턴 분석)
    → Phase 11+ 검토.

~ Custom RAG 인프라 (Pinecone / Weaviate / 자체)
    → Phase 21+. MVP는 pgvector로 충분.

~ Spring Boot 백엔드 분리
    → Phase 21+ 트래픽 임계 도달 시.

~ 자체 fine-tuned LLM
    → Phase 21+. MVP는 OpenAI gpt-4o-mini/4o.

~ Full MOA (5+ agent 협업)
    → Phase 11+ 검토. MVP는 MOA Lite (4 agent).

~ Graph RAG
    → Phase 21+ 검토. MVP는 표준 vector RAG.

~ 대규모 fine-tuning
    → Phase 21+ 검토.
```

→ `docs/contracts/mvp_non_goals.md` §"MVP에서 하지 않을 것"과 정합

---

## 4. Phase 매핑

본 MVP는 Phase 1~10에 매핑된다. `PHASE_REGISTRY.md` 표 정합.

```
Phase 1.  기본 플로우 (입력 → 기획 → 검증 → 저장)
Phase 2.  design.md 기반 PWA 설계 (Discovery + Quick 분기)
Phase 3.  Next.js PWA UI 구현 (Discovery wizard, Quick mode, 비교 카드)
Phase 4.  FastAPI 기본 백엔드 (API 뼈대)
Phase 5.  Supabase / PostgreSQL / Auth 구조
Phase 6.  Output Schema + Agent IO 구현 (AI 입출력 안정화)
Phase 7.  RAG Lite 구현 (5단계 승격 + pgvector)
Phase 8.  MOA Lite 구현 (Intent, Planning, Critic, Rewriter)
Phase 9.  결과 저장 + 피드백 저장 + Brand Memory
Phase 10. MVP 통합 테스트 + 출시 준비
```

각 Phase의 acceptance 기준은 `phases/planned/phase-N-*/acceptance.md` (Phase 진입 시 작성).

---

## 5. 출시 기준 (Phase 10 acceptance)

다음 조건을 모두 만족하면 MVP 출시.

```
1. 사용자 가입 → 영상기획 1개 생성 → 결과 저장의 end-to-end 흐름이 동작.
2. Golden Set 회귀 90% 이상 통과 (현재 11 케이스 → Phase 10 시점 30+ 케이스).
3. Critic 점수 평균 >= 0.70 (eval/regression_eval.md 기준).
4. 광고 표현 차단 정확도 >= 95% (eval/brand_consistency_eval.md 기준).
5. PII 마스킹 / 프롬프트 인젝션 차단 100% (eval/security_eval.md 기준).
6. p95 응답 시간 <= 60초 (Discovery), <= 90초 (Critic 포함).
7. 일평균 영상 생성 50개 + 무료 사용자 100명 (Beta Staging 단계).
8. 운영 비용: 사용자당 월 평균 LLM 비용 <= $0.50 (rate_limit 적용 시).
9. Sentry 에러율 <= 1% (24시간 평균).
10. 데이터 노출 사고 0건 (security_review 통과).
```

위 기준 미달 시 Phase 10 acceptance 거절 → 보강 → 재평가.

→ `PHASE_REGISTRY.md` "Deploy Test E: 제한 사용자 테스트" 직전 게이트

---

## 6. MVP 후 1차 계획 (Phase 11~15)

본 문서는 MVP만 다루지만 정합 유지를 위해 직후 계획 명시.

```
Phase 11: 모바일 PWA UX 강화 (반응형 + 터치 최적화)
Phase 12: 유료 tier 도입 (Stripe 또는 토스페이먼츠)
Phase 13: 비동기 처리 (Celery / Arq 도입 검토)
Phase 14: A/B 실험 인프라 (prompt 변경 효과 정량 측정)
Phase 15: 협업 기능 alpha (팀 단위 Brand 공유)
```

→ 자세한 로드맵은 `product/roadmap.md`

---

## 7. 정합성 체크 (Cross-reference)

다음 25 결정이 본 문서에 반영됨 (PROJECT_STATE.md 정합).

```
[1] Hybrid UX           → §1.1
[2] Mode 자동 분기      → §1.1
[3] Discovery 5장 카드  → §1.1
[4] Plan 3 후보         → §1.1
[5] Critic revise 2회   → §1.3
[6] 4계층 데이터        → §1.2
[7] Intent Filter       → §1.3
[8] Brand Memory        → §1.2
[9] 광고 표현 차단      → §1.3
[10] 4단계 progress     → §1.1
[18] 5단계 승격         → §1.3
[19] PII + injection    → §1.3
```

---

## 8. 변경 절차

MVP 범위 변경 시:

```
1. contract-change Skill 절차 (PR + 회귀 평가 + 영향 분석)
2. mvp_non_goals.md 동시 갱신 (영구 제외 추가/변경 시)
3. PHASE_REGISTRY.md Phase 매핑 검토
4. multi-llm-validation Skill (큰 변경일 때만)
5. PROJECT_STATE.md "최근 변경" 섹션에 기록
```

영구 제외 항목 (영상 제작 일체)을 포함 후보로 변경하려면 추가:

```
6. 사용자(최종 결정자) 명시 승인 필수
7. meta-retrospective Skill로 결정 배경 기록
```

---

## 9. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  본 contract를 docs/contracts/mvp_non_goals.md와 통합 검토 (현재 분리).
Phase 10+: 출시 직전 §5 출시 기준 정량 갱신 (실 데이터 기반).
Phase 11+: §3 "MVP 후 도입 가능" 항목 중 도입 결정된 것은 본 문서에서 제거 + 적절 위치 이동.
```

---

## 10. Open Questions

1. §5 출시 기준 6 (p95 응답 시간 60초)은 LLM 응답 속도 의존이라 조정 가능성 — Phase 6 시점 재측정.
2. §5 출시 기준 8 (사용자당 월 평균 LLM 비용 $0.50)은 사용 패턴 미상이라 추정 — Beta 데이터 후 갱신.
3. §3 협업 기능을 Phase 11+로 미루는 것이 1인 마케터 타겟에 적절한지 — 사용자 인터뷰 후 결정.
4. Brand Memory 자동 추출의 사용자 검토 UI를 MVP에 포함할지 (§1.2) — Phase 9 진입 시 design.md 확정.
5. Intent Filter 거짓 양성 (false positive)이 사용자 경험을 해칠 수 있음 — Phase 8 시점 임계 조정.

---

## 11. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      MVP 포함/제외 범위, Phase 매핑, 출시 기준, 변경 절차,
                      25 결정과의 정합 체크.
```
