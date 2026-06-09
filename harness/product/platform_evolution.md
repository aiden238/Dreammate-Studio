# platform_evolution.md — MVP → 실사용 플랫폼 진화 의도 (지침/메모리)

> 위치: `product/platform_evolution.md`
> 상태: 2026-06-09~10 세션 분석 기반 (사용자 명시 의도 영속화)
> 참조: `PHASE_REGISTRY.md` Phase 27(active) · `BOUNDARIES.md` · `meta/factory/factory_contract.md` · 본 세션 워크플로우 감사 2건

---

## 0. 한 줄

1차 MVP(Phase 1~26, 코드 완성도 高)를 **실제 사용 가능한 플랫폼**으로 끌어올린다. 단 "기능 추가"가 아니라 **이미 만든 것을 켜고·측정하고·정리한 뒤** 확장한다 — measure-before-autonomy.

## 1. 핵심 진단 (이 세션 합의)

- 진짜 병목 = "자율성 부족"이 아니라 **측정 접지선(ground-wire) 부재 + 인간 승인 대역폭**.
- 증상 = "만들었지만 안 켜지고 안 측정됨": 핵심 기능 전부 default-off, 교차검증 로깅만, RAG 지식 0행, 2nd Brain 자가개선 0. → **검증 부채가 phase마다 복리로 누적**.
- 결론: 자율/하네스 강화를 **추가하기 전에**, 프로젝트(런타임)의 측정·가치를 먼저 닫는다.

## 2. 아키텍처 방향 결정

### 2.1 코어는 오케스트레이터-워커(결정론) 유지
- 현 MOA는 이미 오케스트레이터-워커(orchestrator 중개, agent간 직접호출 금지) = **유지가 정답**. 코레오그래피로 바꾸지 않는다(hermetic·감사성 우선).

### 2.2 코레오그래피는 "shell에서만 실험"
- 사용자 결정: 코레오그래피를 **실험적으로 도입**하되, **결정론 코어가 아니라 격리된 agentic shell**(research/meta 영역)에서만. audit log + 결정론 fallback 필수. 코어 오염 0.

### 2.3 GPT 제안 7-worker 다이어그램 = north-star, 즉시 빌드 아님
- Research/Code/Design/Content/Evaluation 워커 풀은 **목표 그림**이되, 지금 추가하면 build-before-measure 함정 재발. 현재 = Intent/Planning/Critic/Rewriter(=orchestrator+4워커+evaluator)로 **3~4단계에 이미 있음**. 워커는 **측정이 필요를 입증할 때** 추가.
- 롤아웃: 단일→라우터→오케스트레이터+워커→evaluator-optimizer→state machine→handoff→제한적 choreography(7단계, 보수적) 순서 동의. 현재 위치 = 3~4단계.

### 2.4 미래 오케스트레이터 확장 구조 (사용자 방향, 보존 — 지금 빌드 X)

현 MOA(Intent/Planning/Critic/Rewriter) 결정론 코어를 유지하되, 아래로 **확장 가능하게** 설계 (build-before-measure 회피 — 측정으로 필요 입증 시 레이어 추가):

```
├─ Query Analyzer            # 의도·엔티티 분석 (현 Intent 확장)
├─ Search Layer
│  ├─ Keyword Search         # BM25/키워드 (현재 없음)
│  ├─ Vector Search          # pgvector + gemini-embedding-2 (★ 지금 작동, 0.7 통과)
│  ├─ Metadata Filter        # brand/platform/tag 필터
│  └─ Reranker               # cross-encoder 재정렬 (현재 없음)
├─ Context Builder           # 검색결과 → 프롬프트 컨텍스트 조립
├─ Generation Layer          # ★ GPT 계열 (임베딩과 분리)
│  ├─ 기획 생성 모델
│  ├─ 대본 생성 모델
│  └─ 요약 모델
├─ Evaluation Layer          # 현 Critic 확장
└─ Memory / Log Layer        # 2nd Brain + agent_io 텔레메트리(A8 접지선)
```

- ★ **임베딩=Gemini, 생성=GPT 계열(분리 확정·구현됨)**: 검색 품질=gemini-embedding-2(ko 압도), 생성=GPT. 두 레이어 독립(provider 분리 = `rag_embedding_provider`).
- 확장 트리거: **LLM Wiki(2nd Brain) 코퍼스가 충분해지면** Search Layer(keyword/reranker) + Generation 세분화(기획/대본/요약) 추가.
- 원칙: 결정론 코어 유지 + 새 레이어 gated/additive + **측정 접지선(A8)으로 각 레이어 가치 실측 후 도입**(코어/셸 단방향 분리 계승).

### 2.5 2nd Brain 실제 동작 명문화 (★ 자가개선 없음 — 과대표현 정정)

★ 정직: 2nd Brain(brand_memory/pkm_entries)은 "학습/자가개선"이 **아니다**. 과거 "쓸수록 맞춰지는 agent-grade 메모리"는 과대표현이었음.
- **추출 = heuristic(LLM 0)**: `brand_memory_extractor` 가 빈도+reason 으로 confidence 0.3/0.7/0.9 **고정 매핑**. 의미 이해·적응 없음.
- **주입 = 결정론 template prepend**: `build_brand_constraint_preamble` 가 entry→bullet 로 user_input 앞에 붙임(동일 입력→동일 출력).
- **거버넌스**: confidence≥0.9(명시 reason)만 자동 적재, 나머지 제안(쓰기 0).
- 즉 "쓸수록 맞춰진다"의 실체 = **ETL 누적**(피드백→규칙추출→저장→다음 생성에 구속 주입)이지 **모델 학습이 아님**.
- 자가개선(LLM 추출/학습)은 **저장된 미래 방향**(heuristic→LLM 승격) — 단 ROI 음수 가능(자동 INSERT 게이트가 이미 결정론) → eval 선측정 필요.

### 2.6 2nd Brain 루프 검증 상태 (A10)
- ✅ 추출 hook 로직(DI wiring): confidence≥0.9 영속 / OFF·익명 no-write.
- ✅ Supabase 영속(uuid): R2 ignition 라운드트립.
- ✅ 주입+LLM 반영: phase-17 e2e(실 LLM).
- ✅ **HTTP+JWT 신원 배선(A10)**: TestClient e2e — 인증 요청이 JWT user_id 를 brand+personal 추출 hook 까지 정확 전달(mock-user-1), 익명→None. (`Temp/pkm_http_jwt_e2e.py`)
- ⚠️ **갭(정직)**: dev mock user `mock-user-1`=non-uuid → Supabase `pkm_entries`(uuid col) 끝단 영속 불가. **full HTTP+Supabase 루프는 실 Supabase Auth(uuid) 필요 = 배포 게이트.** ("실 체감 그대로일 가능성"의 일부 — 로컬 mock 로는 끝단 미검증, 또 코퍼스/품질 반영도 별개).

## 3. RAG / LLM Wiki 콜드스타트 전략

- 문제: RAG 가치는 "LLM이 모르는 독점/브랜드 지식"이 있을 때 발생. 현재 `approved_knowledge` 0행 = 무용지물(고장 아님, 빈 파이프).
- ★ "LLM으로 사용 데이터 수집"만이 답이 **아니다**. 콜드스타트 우선순위:
  1. **개인화 = 브랜드 메모리**(branding 세션 Phase 18). RAG가 아니라 brand_memory로 해결 — 이미 설계됨.
  2. **합성 시드**: 서브에이전트(도메인 전문가/합성 사용자)로 차별화 지식 초안 생성 → candidate_knowledge 드래프트 → 5단계 승격 + 사람 검토. (본 세션 착수)
  3. **전문가 큐레이션**: 고가치 패턴(후크·플랫폼 규범·리텐션)을 수작업 시드 → 최고 품질.
  4. **외부 수집**(research_agent, shell): 공개 패턴 ingest → candidate. (장기)
  5. **사용 데이터**: 위가 깔린 뒤 점진 축적(콜드스타트 해법 아니라 정상상태 보강).
- 결론: 차별화 지식이 쌓이기 전엔 RAG 보류 가능(`use_rag` off) — 빈 파이프 방치 금지. brand_memory(개인화)는 별개로 계속.

### 3.1 ★★ RAG 튜닝·임베딩 방향 (실측 확정 2026-06-10 — 강력 보존)

A9 실측(`approved_knowledge` 8건 투입 + 임베딩 모델 비교)으로 "RAG 무용"의 진짜 원인이 갱신됨.

**측정 (같은 8문서·3쿼리, top 코사인 유사도):**

| 모델 | Q1 무음후크 | Q2 챌린지 | Q3 리뷰 | 0.7 통과 | 비고 |
|---|---|---|---|---|---|
| text-embedding-3-small (현재) | 0.486 | 0.344 | 0.326 (오매칭) | 0/3 | ko 약함 |
| 3-large native (3072) | 0.592 | 0.388 | 0.382 | 0/3 | +0.10, 오매칭 교정 |
| **3-large @1536** | 0.617 | 0.403 | 0.400 | 0/3 | +0.13, pgvector dim 유지 |
| ★★ **gemini-embedding-2 @1536 (taskType)** | **0.818** | **0.738** | **0.740** | **3/3** ✅ | **압도 — 0.7 통과, key 배선됨(low-friction)** |
| gemini-embedding-2 @3072 (taskType) | 0.814 | 0.734 | 0.736 | 3/3 ✅ | @1536과 동급 |

**확정 방향 (강력 보존 — 2026-06-10 Gemini 측정으로 갱신):**
1. ★★ **gemini-embedding-2 @1536 = 단일 최대 레버.** taskType 비대칭(문서=RETRIEVAL_DOCUMENT, 쿼리=RETRIEVAL_QUERY)로 **3/3이 0.7 통과(0.74~0.82)**. OpenAI 3-large(0/3, top 0.617) 대비 +0.20~0.34 압도. → **threshold 안 내려도 RAG가 0.7에서 작동.** `google_api_key` 이미 배선 → low-friction(self-host 불필요). @1536≈@3072(0.818 vs 0.814)라 @1536이 실전(pgvector dim 유지).
2. **threshold 0.4는 OpenAI 잔류 시의 fallback** — Gemini 채택 시 불필요(0.7 그대로 OK). OpenAI 유지하면 `rag_threshold` 0.7→~0.4 필수.
3. **ko특화 self-host(BGE-M3 등)** = 더 먼 미래(인프라 부담). Gemini-embedding-2가 그 자리를 low-friction으로 대체.
4. **남은 진짜 블로커 = 코퍼스 빈약(현 8건).** 임베딩 레버는 풀렸으니 다음 병목은 차별화 지식 축적 — ① **2nd Brain 피드백** ② **사전 지식 주입(운영자 큐레이션)** ③ 코퍼스 확대.
5. **적용 트리거 = 사용자 결정**: Gemini-embedding-2 채택(RAG 실작동) vs OpenAI 유지 + brand_memory 집중. 채택 시 구현 = `embedding.py`에 Gemini provider+taskType 추가 + `approved_knowledge` 재임베딩(8건 trivial).

★ 핵심 통찰 (갱신): RAG "무용"의 원인은 **ko 임베딩 약함이 지배적**이었고, **gemini-embedding-2가 그걸 단번에 해소**(threshold·코퍼스보다 임베딩이 큰 레버였음). **측정 접지선(A8) 없이는 절대 안 보였던 것** — measure-before-autonomy의 결정적 실증.

## 4. 운영 불변식 (계승)

- L1 런타임(`backend/fastapi`·`apps/web`·`migrations`)은 결정론 코어 + 메타/자율은 read-only (`BOUNDARIES.md`).
- 모든 적응형/자율 기능 = gated default-off + behavior-preserving + 'OFF면 byte-identical' 회귀테스트.
- 어떤 로그/텔레메트리도 **소비 경로와 한 묶음**으로만 도입(stale 재발 방지).
- 계약/스킬 변경 = `contract-change` 절차. 메타-하네스 산출 = proposal-first.

## 5. 실행 연결

- **Phase 27(active) = 본 의도의 1차 실행**(실사용 마감 + 측정 그라운딩 addendum, notes.md 참조).
- **하네스 점검(스킬 통합/격하/게이트화 등) = Phase 27 완료 후**(프로젝트 먼저, 하네스 나중).

## 6. 변경 이력
- v1.0.0 (2026-06-09~10): MVP→플랫폼 의도 + 아키텍처 방향(코어 결정론/shell choreography 실험) + 콜드스타트 전략 + measure-before-autonomy 원칙 영속화.
