# Phase 27 — notes (진행 메모)

## 세션 2026-06-09~10 — 측정 그라운딩 addendum + 콜드스타트 시드 착수

### 컨텍스트
사용자 2단계 플랜("Phase 1=프로젝트 재점검 → Phase 2=하네스 점검")의 **Phase 1 = 본 Phase 27 연장**으로 확정 (하네스 규칙: active phase 1개). Phase 27 acceptance(A1~A6, 실사용 마감)에 **측정 그라운딩**을 addendum으로 추가.

### ★ PROJECT_STATE stale 정정 (라이브 검증)
- `pkm_entries`(0006)+`source_plan_id`(0007)+`brand_memory_entries` Supabase **적용 확인됨**. R2 영속 라운드트립 PASS(`Temp/ignite_r2.py`).
- `match_approved_knowledge` RPC(0008) **라이브 존재** — PROJECT_STATE §B "함수 미정의"는 stale.
- 단 `approved_knowledge`·`candidate_knowledge` **0행** → RAG는 함수 OK + 지식 비어 무용(빈 파이프).
- `DATABASE_URL` 비번 = `YOUR-PASSWORD` placeholder(직접 DDL 불가, REST만 동작).
- 기능 분석(워크플로우 감사 2건): 산물 = bounded workflow(에이전틱 과대평가 정정). 스킬 21개 중 실사용 11/잠재추종 6/dead 4/automated-away 1(cost_report).

### 측정 그라운딩 addendum (Phase 27 acceptance 후보 추가 — A7~A11)
- ✅ **A7 default-off flag audit (완결, `Temp/a7_flag_audit.py` 결정론 집계)**: 12 default-off bool flag.
  - 🟢 **활성+wired 8개**: agent_io_log/brand·personal PKM(4)/branding_seed/plans_repo/rich_output = realuse 핵심 루프(건강).
  - 🟡 **wired but 활성경로 0, 4개**(만들고 배선했으나 production ON 0): ① **critic_calibration_enabled**(critic.py — 88점 함정 보정, 가치 高, 묻힘 → 측정 후 활성 검토) ② **multi_provider_plans_enabled**(가치 미지 → A11 측정) ③ **cross_validation_enabled**(logging-only, 가치 低 → 의사결정 승격 or sunset) ④ agent_io_log_to_db(선택 sub-flag, 유지).
  - 결론: 진짜 죽은게이트(미배선)=0. "만들었지만 안 켠" 게이트 4개 = 부채. critic_calibration 활성/측정이 최우선 후속.
- ✅ **A8 측정 접지선 복구 (완결)**:
  - ① agent_io 접지선: `agent_io_log_enabled`를 realuse 프로파일에 추가(config.py) → 실사용 시 텔레메트리 기록 ON → `cost_report.py` 소비. **end-to-end 스모크 PASS**(기록 2건→집계 $0.001345). default OFF byte-identical(전체 812 passed).
  - ② skill 접지선: `scripts/skill_usage_report.py` 신설(코드 수집기, cost_report 동형) → `meta/skill_usage_report_generated.md`(6세션/18호출/phase-start 자동화후보★/폐기후보 13). stale `skill_usage_log.md`에 포인터.
  - ✅ 완결: intent·rewriter 배선 추가(planning 패턴, additive/gated/graceful) + gateway(cross_val/multi_provider)는 기존 배선 확인 → **4 에이전트 + gateway 전 LLM 경로 텔레메트리 커버**. 스모크 PASS(intent+rewriter 방출) + 전체 812 passed.
  - 참고 한계: skill 수집기는 트랜스크립트 의존(로컬 ops 툴, CI hermetic 아님). "폐기후보"=tool 미호출이지 dead 확정 아님.
- 🔄 **A9 RAG 결단 (rag-update 스킬 사용, 사용자 승인 대기)**:
  - 시드 40 draft → 적대검증(차별화 35~45% / 차단단어 / 태그전제 오류) → **candidate-ready 8건** 선별·정제 → `knowledge/rag/seed/2026-06-10_candidate-ready.md`.
  - 필수수정 3건 반영(차단단어 제거/법적단정 약화/태그=metadata 정정). **Step 1~2 PASS**(ad_language grep 검증 — content 차단단어 0).
  - ★ source_kind=external_seed → 사용자 승인 **GO(소량 투입+측정)**. 8건 embed(text-embedding-3-small)→`approved_knowledge` **8/8 INSERT**(RAG 첫 비-empty). `Temp/rag_seed_insert.py`. 롤백: `delete eq metadata->>source_kind=external_seed`.
  - 🔴 **첫 RAG 실측 — 결정적 발견**: 검색 메커니즘 작동(쿼리→정확 랭킹) BUT **유사도 0.33~0.50, 전부 production threshold 0.7 미달** → **0.7에선 지식 있어도 RAG=빈 결과**. 0.7은 ko + text-embedding-3-small엔 과도(영어 기준 default). 즉 RAG 무용의 진짜 원인 = 빈 파이프뿐 아니라 **threshold 미스튜닝**.
  - ✅ **임베딩 측정(비파괴 in-memory)**: OpenAI 3-small 0.486/0.344/0.326(0/3) → 3-large@1536 0.617/0.403/0.400(0/3, 오매칭 교정). `Temp/rag_embed_measure.py`.
  - 🚀 **gemini-embedding-2 @1536 측정(taskType 비대칭)**: **0.818/0.738/0.740 = 3/3 0.7 통과 + 전부 정확매칭**. OpenAI 최고 대비 +0.20~0.34 압도. @3072 동급(0.814). `Temp/rag_gemini_measure.py`. → **threshold 안 내려도 RAG 작동.** ko 임베딩 약함이 지배적 원인이었음.
  - ✅ **방향 강력 보존 갱신**: `product/platform_evolution.md §3.1` — gemini-embedding-2가 단일 최대 레버(google_api_key 배선됨=low-friction). threshold 0.4는 OpenAI 잔류 fallback. 남은 블로커=코퍼스 빈약.
  - ✅ **결정=Gemini 채택(option 1)**: 임베딩=Gemini, 생성=GPT(분리). 구현: config `rag_embedding_provider`(gated default openai) + `embedding.py` `_embed_gemini`(httpx, taskType) + `.env RAG_EMBEDDING_PROVIDER=gemini` 활성. **812 passed(default openai byte-identical)**.
  - ✅ **실 코드경로 검증**: 8건 Gemini DOC 재임베딩 → `retrieval.search()` threshold **0.7에서 Q1 3hit/Q2 2hit/Q3 1hit** = RAG 첫 실작동. `Temp/rag_gemini_adopt.py`. 롤백: delete external_seed.
  - ✅ **미래 오케스트레이터 확장 구조 보존**: `platform_evolution.md §2.4`(Query Analyzer→Search[keyword/vector/metadata/reranker]→Context→Generation[기획/대본/요약]→Eval→Memory). LLM Wiki 충분해지면 확장.
  - use_rag는 "보조" 유지(코퍼스 8건 빈약 — 다음 블로커는 지식 축적: 2nd Brain/큐레이션). 그 후 A7/A10/A11 측정.
- ✅ **A10 2nd Brain (완결)**:
  - ✅ **HTTP+JWT 배선 e2e PASS**: TestClient(dev mock auth) — 인증 요청이 JWT user_id(mock-user-1)를 brand+personal 추출 hook까지 정확 전달, 익명→None. 기존 wiring 테스트(DI/익명)가 못 닫은 auth 레이어 갭 닫음. `Temp/pkm_http_jwt_e2e.py`.
  - ✅ **자가개선 부재 명문화**: `platform_evolution.md §2.5/2.6` — 2nd Brain=heuristic ETL(학습 아님), "agent-grade" 과대표현 정정. 루프 검증 4축(DI/R2 uuid 영속/phase-17 LLM/A10 HTTP+JWT) + 갭(mock non-uuid → 끝단 Supabase 영속은 실 Auth 필요=배포게이트).
  - ⚠️ 정직: HTTP 루프·신원 배선은 입증, 단 "실 체감 품질 개선"은 코퍼스 빈약+생성 반영 미측정이라 별개(golden_set 후속).
- ✅ **A11 3-provider 다양성 측정 (완결, 실 LLM)** `Temp/a11_provider_diversity.py`:
  - **OFF 동일모델×3: pairwise_sim 0.959**(거의 복붙) vs **ON 3-provider: 0.680**(실제 다양) → **3-provider 다양성 실익 큼**(라벨만 다른 동일모델×3는 "3안" UX의 실제 약점=near-duplicate).
  - ⚠️ **취약성 발견**: 이번 측정 중 Gemini 생성(gemini-3.5-flash) **503 과부하** + Claude **malformed JSON** → 2/3 슬롯 폴백. multi-provider는 외부 실패표면 3배. (그래도 OFF보다 다양 — GPT+Claude+폴백 ≠ GPT×3).
  - **판정**: 다양성 이점 real & substantial(keep-off 단정 아님). 단 ① Claude JSON robustness ② provider 가용성 선결 필요. 비용·안정성 수용 시 활성 가치 有. golden_set 품질측정은 후속.
  - ★ **Gemini 티어 진단(사용자 질문)**:
    - 1차(무료): gemini-2.0/flash-latest=429 "check billing"(쿼터), gemini-3.5-flash=503(best-effort), gemini-2.5-flash·embedding-2=200.
    - 2차(사용자 유료 전환 후 재점검): **선결제 플랜 전환됨 BUT 크레딧 0(depleted)** → Gemini **전 모델 429 "prepayment credits depleted"** (생성+**임베딩 포함**). OpenAI gpt-4o-mini=200(메인 생성 정상).
    - ⚠️ **영향: RAG(Gemini 임베딩) 현재 막힘** — 단 graceful(embed None→retrieval empty, 앱 무중단, 메인 GPT 생성 무영향). A9 채택이 깨진 게 아니라 **크레딧 부재**.
    - **fix(사용자): ai.studio/pro 크레딧 충전** → RAG 즉시 복구. OpenAI 원복 비추(docs=Gemini 임베딩, 공간 불일치). 충전 전 RAG는 graceful-off로 둬도 무방.
    - ✅ **충전 후 복구 확인(2026-06-10)**: gemini-embedding-2 200 OK + `retrieval.search()` @0.7 = 3/2/1 hits(A9 그대로). 코드 이슈 0, 외부 크레딧만 문제였음.

## Phase 1(=프로젝트 재점검, Phase 27 연장) 완료 점검 (2026-06-10, 코드 검증)
- ✅ **측정 재점검 A7~A11 전부 완료**: A7 flag audit / A8 측정접지선 / A9 RAG(Gemini 채택+복구) / A10 2nd Brain(HTTP+JWT+명문화) / A11 3-provider 다양성.
- 🟡 **Phase 27 원래 realuse-마감 A1~A6**(재점검과 별개): A1 프로파일 ✅ / A4 plan영속+migration ✅(적용 확인) / **A2 AppShell 네비 ❌(컴포넌트 미구현)** / **A3 rate_limit ❌(backend 구현 0)** / **A5 첫-사용자 e2e ❌(전체 흐름 미실행)** / A6 게이트 🟡(pytest 812✅, frontend typecheck·scenario_sim·audit_naming 미실행).
- 결론: **"프로젝트 재점검(A7~A11)" = 완료.** Phase 27 전체 마감 기준이면 A2/A3/A5(실사용 마감 빌드) 미완.

### 완료(본 세션)
- ✅ 경계강화(이동 0): `BOUNDARIES.md` + `.github/CODEOWNERS` + `scripts/check_boundaries.py`(작동 검증). L1/L2 기계 가시화.
- ✅ 의도 영속: `product/platform_evolution.md`(MVP→플랫폼 + 아키텍처 방향 + 콜드스타트 전략).
- 🔄 RAG 콜드스타트 시드 워크플로우 착수(서브에이전트 합성 테스트 → candidate_knowledge 드래프트). 결과 → `knowledge/rag/seed/` 기록 예정.

### 다음
- A7~A11 순차 진행(측정 우선). 콜드스타트 드래프트 → `rag-update` 스킬 5단계 검토.
- Phase 27 A1~A6(기존 실사용 마감)와 병행 — A6 게이트(pytest 802 byte-identical) 유지.
- Phase 27 phase-complete 후에야 하네스 점검(Phase 2) 진입.
