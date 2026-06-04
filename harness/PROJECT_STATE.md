# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 **하네스 마이그레이션(Phase 0) + Phase 1~4 + Phase 4.5 + Phase 6 + Phase 5 + Phase 5.5 + Phase 7 + Phase 8 + Phase 9 + Phase 9.5 + Phase M0(meta-phase) + Phase M1(meta-phase dry-run) + Phase M2(meta-phase machinery 개선) + Phase M3(meta-phase 이질 도메인 범용성 2차) + Phase 10(MVP 통합 테스트) 완료 + Phase 11(LLM Gateway A안 + B안 3-provider 확장) 완료**.
Next.js PWA **11 routes** (+/login) + FastAPI 17 endpoints (Phase 1~9 누적, /auth/* + /sse/* + /plans/{id}/select + /plans/{id}/feedback 신규) + 3-plan parallel + multi-model 인터페이스 + Critic canonical (overall_score + dimensions, **normalize wiring live**) + revise loop (max 2) + Rewriter v1.1.0 + recommended_plan_index + **Supabase 영속화 + JWT httpOnly cookie + RLS 정책 + SSE Progress 4단계 (실 stage 연동)** + **RAG Lite (candidate_knowledge 5단계 MVP 전부 + pgvector retrieval + LLM Wiki 보조)** + **MOA Orchestrator 추출 (orchestration/moa_orchestrator + ProgressSink + progress_store 브릿지) + prompt_registry semver 정식화 + Critic v1.1.0 conservative adapter** + **결과 저장(selected_plans) + 피드백(feedback_events) 영속화 graceful + PII 마스킹 + 피드백 UI inline + Brand Memory 준비(feedback→candidate pending 적재)** 모두 동작.
**Phase 9 ✅ done (2026-05-31)** — 결과 저장 + 피드백 (selected_plans/feedback_events 영속화 graceful + normalize_to_canonical wiring + Brand Memory 준비 + 피드백 UI wrapper, ADR-030/031/032, CC-004, large phase 6 Slice 실측 ~10~13h).
**🟢 최신 = Phase 19 2nd brain 시각화 (마이페이지 PKM 도식화) ✅ done (2026-06-04, archive)** — Phase 16(A/B fit +0.425 GO) → 17(계정별 PKM 실빌드) → 18(브랜딩 세션 발굴) → **19(가시화·큐레이션)**으로 **PKM 루프 4단계 완성**(발굴→축적→주입→가시화). `/brain` 하이브리드(모바일 카드 + 데스크톱 @xyflow 그래프 lazy-load) + 큐레이션(잠금/편집/삭제), GET /me/pkm-graph + PATCH/DELETE /me/pkm. pytest **668** + scenario_sim 36/36 + audit 0. gated/additive(OFF byte-identical). CC-024. **branch `phase-19-2nd-brain` (main 머지 진행).** 이월: /brain 라이브 시각 e2e(@xyflow 재기동) / 4계층 깊이·출처 엣지 / PlansRepo 영속(17 carryover) / **Phase 20 commercial_viral**(director 품질 보강) / 배포 Gate B~G. **다음 = pending_user_decision.**
> (과거 최신: Phase 13 출력 확장 done 2026-06-03 — 깊이 0.231→1.000 gated rich.)

## 🟢 Phase 11 A안 — LLM Gateway ✅ done (2026-06-01)

> 정식화 완료: `phases/archive/phase-11-llm-gateway/` + ADR-039 + CC-010(cost_control 확장) + 회고. 근거: `meta/proposals/2026-05-31_llm-gateway-design.md` + `meta/handoffs/2026-06-01_llm-gateway-handoff.md`.

- **LLM Gateway** (`backend/fastapi/llm/`) S1·S2·S3: registry/alias/gateway + OpenAI·Gemini adapter + cross_validation(cross_validate+compare) + orchestrator gated hook(default-off, 로깅만, Envelope 불변).
- pytest 381→**435** (gateway 31 + cross-val 19 + wiring 4). ★ behavior-preserving(기존 0 수정) + gated default-off + 키 커밋 0. P-X1 **63**.
- 라이브 검증: gateway 경유 OpenAI 생성 ✅ / Gemini 교차검증(8차원)+compare(consensus 0.7375 vs 0.72) ✅. Node.js v24.16.0. 키 3개(.env 인증 OK, Anthropic 오타 수정). ★ gemini-3.5-flash **회복됨**(기본값 그대로).
- ADR-039 + CC-010(cost_control tier×mode→alias 표 additive) + P-LLM-GATEWAY-001(신규 후보).
- 다음(B안+): full 라이브 /generate(wizard) 데모 ✅(consensus) / frontend 손-검증 / **B안(Phase 12) 진행 중** — 아래.

## 🟢 LLM Gateway B안 (Phase 11 확장) — 3-provider ✅ 기능 완성·라이브 입증 (2026-06-02)

> ★ 번호 확정: B안 = **Phase 11 확장**(LLM Gateway A안→B안, 같은 서브시스템). **Phase 12 = 검증 페이즈**로 비움(사용자 지침 "12=검증"). 확장 = Phase 13~20.

- **S1** (cac2b9b + b060c2b): Anthropic adapter + registry Claude·Gemini + gateway 3-provider 분기(openai/google/anthropic) + config. sonnet prefill 400 버그 수정. pytest 435→452.
- **S2a** (6948d3e): 3-plan 다양성 alias — plan_primary→GPT / plan_secondary→Claude(haiku) / plan_tertiary→Gemini(flash). 452→457.
- **S2b-1** (dcf46e5): Claude ```json 펜스 stripping(json_mode 정규화, haiku 대응). 457→465.
- **S2b-2a** (7e1e7a2): `run_planning_multi_provider_3`(gateway 3-provider 3안, graceful len-3) + `multi_provider_plans_enabled` flag(default False). 미연결. 465→469.
- **S2b-2b** (c9fe16d): orchestrator step-3 gated 분기(ON→multi-provider / OFF→기존 byte-identical, Envelope 불변). 469→**471**.
- **S2b-2c** (f2ae80d): gemini-flash registry model_id 'gemini-3-flash' 404 → config field(default live 'gemini-3.5-flash')로 교정.
- ★ **라이브 3-provider 3안 데모 (2026-06-02)**: slot0 openai/gpt-4o-mini · slot1 anthropic/claude-haiku-4-5 · slot2 google/gemini-3.5-flash — **3안 전부 실 생성, FALLBACK 0**, approach_label 다양(narrative/informational/experiment). gated default-off로 기존 단일-provider 흐름 100% 보존.
- pytest **471** + P-X1 유지 + behavior-preserving(flag OFF byte-identical) + 키 커밋 0.
- 남은 B안 정식화(비차단, 다음 세션/검증 entry 흡수 가능): cost_control_policy 다중-provider cost 재조정(§18.D) + ADR(B안 결정) + agent_io/registry contract-change 반영.

## ✅ Phase 12 = 검증 페이즈 (validation) — done (2026-06-02, archive)

- 목적: MVP 출력(영상기획안) **품질·가치** 실측(지금까지 구조 정확성만 검증). 확장(13~20) 우선순위 근거 확보.
- ★ 핵심 GAP = **깊이 격차(depth gap)**: 같은 모델(gpt-4o-mini)에 확장 프롬프트만으로 compact(name/concept/hook/2~4 beat/pros/risks 7필드)→rich(hook 3변형·타임코드·대사·자막·B-roll·썸네일/제목·CTA·레퍼런스·길이 변형). 2026-06-02 라이브 데모 입증 → 단순함=모델 한계 아니라 prompt/schema 설계 선택. Phase 12 = 이 격차를 수치(현재 X/잠재 Y/gap Z)로 확정.
- **사용자 확정 scope**: ① 깊이 = 자동 eval + **human review 표본**(staging S4 제외) ② golden_set = **확장 후 측정(~25)**.
- **확정 슬라이스 (entry + 5)** — ★ 운영 코드 0 수정 + behavior-preserving(pytest 471):
  - Entry ✅: phase entry 8파일 + multi-llm-validation self(11th). (`phases/active/phase-12-validation/` + `meta/validations/2026-06-02_phase-12-pre-entry_self.md`)
  - S1 ✅ (8ad9594): golden_set 15→**25** + **depth_actionability 차원** (CC-011, additive).
  - S2+S3 ✅ (ef165bb): **깊이 격차 실측** — 같은 모델(gpt-4o-mini) compact(run_planning) vs rich, 6 도메인, 13 feature → **compact 0.231 vs rich 1.000 = 4.3x, 편차 0**. compact 결핍 10/13. (`eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md`)
  - S4 ✅ kit (f991b0e): human review kit 3케이스(compact vs rich 실출력 + 5차원 채점 시트). ★ **사용자 실 채점 deferred** — 사용자 2026-06-02 실 UI(/generate)로 격차 직접 확인 → 결론 확정, kit 은 optional 보정 보존 (`eval/human_review/2026-06-02_phase-12-s4-review-kit.md`).
  - S5 ✅: 종합 + Phase 13 제안 (`phases/archive/phase-12-validation/s5_synthesis_and_phase13_proposal.md`).
- ★ **검증 결론**: MVP 출력 단순함 = **모델 한계 아님, prompt/schema 설계** (같은 모델 0.231→1.000). 결핍 다수가 스키마 슬롯 부재 → 확장 레버 = prompt+schema. + 88점 함정(compact 가 Critic 88점 받아도 depth 미반영).
- B안(Phase 11) 비차단 잔여 추적(Phase 13 승계): cost_control 다중-provider 재조정(B-RES-1 = Phase 13 S6 흡수) / B안 ADR / agent_io·registry contract-change.
- ★ **종료**: retrospective(`meta/retrospectives/phase-12.md`) + closing_notes + archive 이동(`phases/archive/phase-12-validation/`) + REGISTRY done. P-VALIDATION-DEPTH-GAP-001(신규 후보).
- 다음 액션: ✅ **Phase 13 = 출력 확장(Output Enrichment, compact→rich) active** — 깊이 격차를 운영 출력에 반영(gated 단계 롤아웃 + additive 스키마, 첫 의도적 출력 변경). (staging 실사용 = Phase 14+.)

## 🟢 Phase 13 = 출력 확장 (Output Enrichment, compact→rich) — ★ active (entry 작성 2026-06-02)

- 목적: Phase 12 가 입증한 깊이 격차(compact 0.231 → rich 잠재 1.0, 4.3x)를 **운영 출력에 반영** — compact 7필드 → rich(후크 변형·타임코드·화면·대사·자막·샷·썸네일·제목·CTA·레퍼런스·길이변형·타깃·톤). 목표 depth 0.231 → ≥0.8.
- ★ **이 프로젝트 첫 의도적 출력 변경** phase — 그래서 **gated 단계 롤아웃**(`rich_output_enabled` default **False** → 검증 후 ON) + **additive 스키마**(rich 슬롯 전부 Optional → 기존 회귀 0, flag OFF byte-identical).
- **사용자 확정**: 롤아웃 = **gated**(flag OFF → 검증 후 ON) / 범위 = **풀**(backend + frontend, /generate 화면까지 rich).
- **6 Slice (entry + 6)** — ★ flag OFF byte-identical(behavior-preserving) + additive:
  - Entry: entry 8파일 + multi-llm-validation self(12th).
  - S1 ✅ 스키마 확장 (2026-06-02, CC-012, commit 대기): `Plan` rich 9 + `PlanFlowBeat` rich 3 = **12 슬롯 전부 Optional/additive** + `PLAN_RICH_FIELDS`/`BEAT_RICH_FIELDS` 상수 + `Plan.model_dump_compact()`(A5-PP byte-identical capability, OFF 경로 wiring=S3) + output_schema §8.1 **v1.1.0→v1.2.0** + agent-io-check **PASS(발견 0)** + 신규 test 10 → **pytest 471→481 green** (기존 471 수정 0). 운영 .py = schemas/output.py(additive)만. 키 0.
  - S2 ✅ 프롬프트 확장 (2026-06-02, CC-013, commit 대기): planning `RICH_SYSTEM_PROMPT`(rich 12 슬롯 지시 + 브리프 경계) + `_build_rich_system_prompt_with_hint()` + `RICH_PROMPT_VERSION="v1.1.0"` + prompt_registry §7 **P-006 v1.0.0→v1.1.0**(prompt-version-review, ★ gated 공존 — deprecate 아님) + 신규 test 5 → **pytest 481→486 green**. ★ 기존 compact `SYSTEM_PROMPT`(v1.0.0) 보존 + rich 프롬프트 **런타임 미연결**(behavior-preserving, wiring=S3). depth 실측=S6. 키 0.
  - S3 ✅ gated wiring (2026-06-03, CC-014, commit 대기): config `rich_output_enabled` default **False** + `envelope_to_response_dict()` 헬퍼(`Plan.model_dump_compact()` 재사용) + planning 프롬프트 분기(run_planning/_run_planning_single/_via_gateway) + generate.py·moa_orchestrator·plans.py 직렬화 분기. **OFF=compact byte-identical**(/generate=JSONResponse+deprecation header / /plans POST=stored compact dict, POST 라우트 response_model 미지정이라 rich 누수 차단) **ON=rich** + revise 왕복 rich 보존 + 신규 test 7 → **pytest 486→493 green** (기존 486 수정 0 = OFF byte-identical 증거). 운영 .py 6 + frontend 0 + 키 0.
  - S4 ✅ Critic depth (2026-06-03, CC-015, commit 대기): critic `RICH_SYSTEM_PROMPT`(9차원 + depth rubric anchors) + `DIMENSIONS_RICH`(8+depth_actionability) + `RICH_PROMPT_VERSION=v1.2.0` + `run_critic` `rich_output_enabled` 분기(ON=9차원/검증/평균, OFF=8차원) + `_derive_verdict(dimensions=DIMENSIONS 기본)` + prompt_registry P-007 **v1.1.0(active/OFF)+v1.2.0(gated/ON)** + CriticEvaluation.dimensions 자유 dict additive(스키마 무수정) + agent-io-check **PASS(발견 0)** + 신규 test 6 → **pytest 493→499 green**(기존 493 수정 0 = OFF byte-identical). 88점 함정 해소: 얕은 plan(depth 낮음) ON avg 하락 단언. ★ 기존 8차원 SYSTEM_PROMPT/DIMENSIONS/PROMPT_VERSION/normalize 본문 무수정. planning/orchestrator/frontend 0 + 키 0.
  - S5 ✅ frontend (2026-06-03, commit 대기): `lib/types.ts`(PlanFlowBeat 3 + Plan 9 rich optional) + `components/PlanCard.tsx` rich **조건부 8섹션**(타깃·톤/대안후크/beat 화면·대사·자막/샷/썸네일·제목/CTA/레퍼런스/길이변형) — 값 있을 때만 렌더(compact=0개=기존 동일). typecheck+lint pass, **순수 additive(183/0·22/0)**, backend 0, design.md 준수(모바일/카드/제작UI 미포함). 다음=S6.
  - S6 cost 재조정(rich 토큰 × 3안 + B-RES-1 통합) + depth 재측정(≥0.8) + flag ON 라이브 데모 + phase-complete.
- ★ 제품 경계: 확장본도 **"기획 브리프"**(촬영·편집 가이드)지 완성 대본/영상 제작 아님 (product_boundary).
- 승계: B안 잔여(B-RES-1 cost 재조정 = S6 흡수 / B-RES-2 ADR / B-RES-3 contract-change) + Phase 12 S4 human review 실 채점.
- 근거: Phase 12 깊이 격차 리포트(`eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md`) + S5 종합 + depth_actionability rubric(CC-011).

## 현재 Active Phase

**🟢 Phase 19 = 2nd brain 시각화 (마이페이지 PKM 도식화) — ✅ done (2026-06-04, archive)** — 개인 PKM(pkm_entries) + 브랜드 PKM(brand_memory)을 `/brain`에서 **하이브리드**(모바일 카드/리스트 + 데스크톱 react-flow 그래프 @xyflow lazy-load, 모바일 미포함)로 도식화 + **큐레이션**(잠금/편집/삭제). 읽기 레이어(신규 데이터모델 0). ★ 발굴(18)→축적(brand_memory)→주입(17)→**가시화(19)** 루프 완성. **S1**(GET /me/pkm-graph 집계+RLS+graceful)·**S2**(모바일 카드/리스트+empty state)·**S3**(데스크톱 @xyflow 그래프 반응형 lazy-load+토글)·**S4**(PATCH/DELETE 큐레이션, prefix pkm:/bm: 라우팅+소유검증, user_locked 보호). pytest **641→668** + scenario_sim 36/36 + audit 0 + typecheck/lint + 모바일 무변경. CC-024(api §8.7 + page_map §1.4). gated/additive. 이월: **/brain 라이브 시각 e2e**(@xyflow 의존성 프론트 재기동 필요 — 유닛 668+typecheck로 기능 보증) / 4계층 깊이(domains·series 노드)+출처 엣지(feedback→PKM). 회고 `meta/retrospectives/phase-19.md`. branch `phase-19-2nd-brain`.

**🟢 Phase 18 = 브랜딩 세션 (Akinator 주제발굴) — ✅ done (2026-06-04, archive)** — 주제 모르는 사용자를 **LLM 동적 스무고개**(카드+자유입력)로 좁혀 **후보 주제 3개 × 브랜딩 방향** → 택1 → planning + brand_memory(PKM) 시드. Quick/Discovery에 더한 3번째 진입(gated/additive). ★ **발굴→축적(brand_memory)→주입(Phase 17) 루프 닫힘**. S1(topic_discovery P-AUX-3)·S2(endpoint+상태)·S3(frontend /new/branding+진입카드)·S4(/branding/select 택1→PKM 시드). ★ **라이브 e2e(브라우저)**: /new/branding → 8 적응형 질문(정보→…→김치 조리법) → 후보 3×방향 → 택1 → 생성 성공. pytest 608→**641** + scenario_sim 36/36 + audit 0 + CC-023(api_contract). 이월: 결과 view auth-gate UX / authed seed 라이브 e2e. 회고 `meta/retrospectives/phase-18.md`.

**🟢 Phase 17 = 계정별 PKM 실빌드 (가 + 다) — ✅ done (2026-06-04, archive)** — Phase 16 GO(Δfit +0.425) 기반 첫 **production 빌드**. **PKM 루프 양쪽 폐쇄**(feedback→추출≥0.9→brand_memory/pkm_entries→다음 생성 주입, personal>brand) + 라이브 3중 입증(brand steer / 개인 PKM e2e 실 LLM / Supabase 영속 — 개인3+브랜드4행) + get_supabase service-key(RLS 우회) + video_projects 소음 제거. 전부 gated default-OFF + behavior-preserving(pytest **470→608**, scenario_sim 36/36, audit 0). 가-S1(신원)·가-S2(brand 주입)·가-S3(brand foundation)·다-S3(pkm_entries CC-022)·다-S5/S6(추출루프)·다-S4(e2e). 이월: PlansRepo plan 영속 / Supabase 실계정 브라우저 e2e. 회고 `meta/retrospectives/phase-17.md`. 현재 "익명 생성"(generate user_id=NULL, orchestrator 신원 0) 해소 + 계정별 PKM(개인/브랜드) **구속 주입**(★ Phase 16 교훈: rag_context '참고' 아닌 **지시 슬롯**). 가=auth 신원→생성 연결 + brand_memory 구속 주입(gated/behavior-preserving — 익명·무메모리 byte-identical) / 다=개인 PKM(`pkm_entries`)+개인별 메모리+다계정 주입. **슬라이스: 가-S1(신원 plumbing, 익명 byte-identical) → 가-S2(brand_memory 구속 주입) → 다-S3(pkm_entries+PkmRepo) → 다-S4(통합+e2e)**. 진입 = phase-start 4점검(audit_naming 0) + entry 6파일. 동반 = S3 사람 blind(병행 채점 중). 근거 = `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md` §9 1차. baseline pytest 556 + scenario_sim 36/36.
- **가-S1 ✅ done (433167d)**: auth 신원(request.state.user)→라우터→`generate_plan(auth_user_id/brand_id optional)` plumbing + plan_entry stash(가-S2 hook) + 로깅. 익명 byte-identical. test +5. contract 변경 0(신원=쿠키/JWT, body 불변).
- **가-S2 ✅ done (8ebedc5)**: `brand_memory_injection_enabled`(gated default OFF) + `agents/brand_injection.build_brand_constraint_preamble`(entry_type별 구속 directive, production helper) + generate_plan 에서 brand 해결(explicit>resolver DI>brands query 최근1)→`list_for_brand`→**user_input 앞 prepend**(Phase 16 검증 메커니즘). flag OFF/익명/무brand/무메모리=byte-identical(133 ins/0 del). test +9 → pytest 570. ★ **라이브 검증**: 시드 brand_memory(톤"따뜻·솔직 동네") 주입 시 실 plan 톤이 브랜드 PKM 그대로 이동 + 정겨운 표현 출현 + 금지어 회피(P-LIVE-VERIFY-001).
- **가-S3 ✅ done (271e46a)**: brand foundation — 제품이 brands 행을 안 만들어 brand_memory anchor 부재(가-S2 prod 미fire) 발견 → `db/repositories/brand_repo.py` BrandRepo(get_or_create_default, idempotent query-before-insert, graceful) + generate_plan 게이트 경로 자동생성 배선. flag OFF/익명 → DB write 0, byte-identical. test +12 → pytest 582.
- ★ **"가"(실연결 파이프라인) 완전체** = 신원(S1) + brand_memory 구속 주입(S2) + 기본 brand 자동확보(S3). flag ON 시 인증 사용자 → 기본 brand → brand_memory 주입까지 연결.
- ★ **정직한 잔여 갭**: brand_memory_entries 가 **비어있음**(P-AUX-2 brand_memory_extractor 는 "준비만" — feedback→brand_memory 적재 미연결). 즉 파이프라인은 완성됐으나 **주입할 내용이 아직 없음** → 추출 루프 배선 필요(별도 슬라이스).
- **다-S5 ✅ done (566d18e)**: brand_memory 추출 루프 배선 — `/plans/{id}/feedback` 기록 후 gated 추출(`brand_memory_extract_enabled` default OFF). 인증+flag 시 BrandRepo.get_or_create → feedback/selection 로드 → `run_brand_memory_extractor(persist=True)`. ★ confidence≥0.9(명시 선호)만 자동 적재, 나머지 proposal(ADR-031 NG12 보존). graceful(추출 실패해도 feedback 차단 0). test +7.
- **다-S3 ✅ done (f1dbf2e, CC-022)**: 개인 PKM — `0006_pkm_entries.sql`(personal scope, auth_user_id 격리, RLS) + db_schema §6.2 + `PkmRepo` + config `personal_pkm_injection_enabled`(default OFF) + generate_plan 주입(personal preamble 을 **brand 앞** prepend, design §6.2 personal>brand). read-only(자동 쓰기 X). test +11 → pytest 600.
- ★ **Phase 17 "가"(실연결) + "다"(개인 메모리) 코어 완성**: 신원(가-S1)+brand 주입(가-S2)+brand foundation(가-S3)+brand 추출루프(다-S5)+개인 PKM(다-S3). 전부 gated default-OFF + behavior-preserving(pytest 470→600 누적, 기존 0 수정) + 라이브 검증(주입 steer). 모든 flag OFF = pre-Phase-17 byte-identical.
- **다-S6 ✅ done (708328b)**: 개인 PKM 추출 루프 — `personal_pkm_extract_enabled`(default OFF). plans_feedback 에서 `_run_personal_pkm_extract_hook`(brand 무관, auth_user_id 키) → `extract_brand_memory_candidates` → `PkmRepo.add_entry(scope=personal)`, ≥0.9 자동/나머지 proposal. test +8 → pytest 608.
- ★★ **PKM 루프 완전 폐쇄(brand + personal 양쪽)**: feedback → 추출(≥0.9) → (brand_memory_entries / pkm_entries) → 다음 생성 시 구속 주입(personal>brand). 전부 gated default-OFF + behavior-preserving(pytest 470→608 누적, 기존 0 수정) + graceful. 모든 flag OFF = pre-Phase-17 byte-identical. **flag ON + Supabase + 인증 사용자**면 "쓸수록 맞춰지는" agent-grade 동작.
- **다-S4 e2e ✅ PASS (ed0c710)**: 개인 PKM **전체 루프 라이브 입증**(실 LLM, DI 공유) — feedback(명시 reason)→추출 pkm_entries 4건(0.9)→같은 사용자 generate_plan→plan 톤="담백하고 솔직한 톤"(학습 선호 반영)+과장 회피. "쓸수록 맞춰지는" agent-grade 동작 닫힌 루프 입증. 리포트 `eval/regression_results/2026-06-04_phase-17-pkm-e2e.md`.
- **잔여**: B(S3 사람 blind — 사용자 채점 대기, fit→value 봉인) / Phase 17 phase-complete(회고/archive/게이트) / C(위저드 brand 명시 선택 — 다중 brand 시) / brand HTTP 다요청 e2e(Supabase 영속 — 배포 게이트) / series PKM·orchestrator vector·commercial_viral(후속).

**🟢 Phase 16 = A/B 실험 (Baseline 래퍼 vs Agent-grade PKM/RAG) — ✅ done (2026-06-04, archive)** — 검증/실험 페이즈(Phase 12 성격: 측정하고 빌드 안 함). moat 리서치 결론("MVP=복제 쉬운 래퍼, moat는 미구축 PKM/RAG=가설")을 **단일변수 통제 A/B 실험**으로 검증. **H1**(메커니즘: PKM/RAG 컨텍스트 주입이 동일 모델·프롬프트·output_mode에서 품질을 올리는가 — real-mode critic 8~10차원 + depth + 사람 blind) + **H2**(compounding: 누적 PKM N=0/5/20에서 단조 증가하는가). Arm A=현재 운영 경로(`use_rag=False`, byte-identical), Arm B=`use_rag=True`+brand_memory+시뮬 PKM context pack(PKM/RAG §7 형식 fixture). ★ 포크 아님 — 1 코드베이스 + 플래그. **산출 = go/no-go/partial 숫자** → PARKED 로드맵(PKM/RAG §9, P17~) 재우선순위 GATE. 선행조건 A(Phase 13 rich)·B(Phase 14 위저드) 충족. 사용자 결정: real-mode ON(키 제공). 진입 = phase-start 4점검(audit_naming 0 drift) + entry 6파일. branch `phase-16-ab-experiment`(main에 Intent CC-021 머지 완료). 근거 기획안 `meta/proposals/2026-06-03_ab-experiment-agent-vs-baseline.md`.
- **S1 ✅ done (2026-06-04, f22a53d 하네스 + bdff167 리포트)**: `eval/ab_experiment.py`(build_arms/run_arm/run_ab_pair) + `ab_personas.py`(시뮬 PKM 2종) + test 9(★ 통제 입증 mock — 두 arm 시스템 프롬프트가 '참고 자료' 블록만 차이). pytest 537→546(기존 0 수정). **real-mode 1차 실측**(카페, director, 3rep): Δ(B−A) mean **+0.013**(노이즈 −0.02~+0.033 내) = ★ **generic critic 으로 PKM lift 미검출**. 핵심 발견: critic=generic 품질만 재서 **개인화 fit 을 못 봄**(moat=fit/일관성/누적, 리서치 정합) → "PKM 무용"이 아니라 **측정 도구 한계**. 리포트 `eval/regression_results/2026-06-04_phase-16-s1-ab.md`.
- **S2 ✅ done (2026-06-04, abbc219)**: 강한(binding) 주입(`build_constraint_preamble` — PKM 을 user_input 구속 지시로, rag_context '복제금지 참고' framing 탈피) + **fit/adherence 측정**(`score_fit` = 객관 금지어 + LLM judge gpt-4o). `run_ab_pair_fit`(A vs B_strong). test 546→556. **real-mode 실측(2 페르소나×2rep)**: Δgeneric **+0.008**(flat 재확인) / ★**Δfit +0.425**(4/4 강한 양 +0.33~0.58, A 0.42~0.67 ≪ B 0.95~1.0). 리포트 `eval/regression_results/2026-06-04_phase-16-s2-fit.md`.
- ★ **체크포인트 판정 = GO(메커니즘)**: 구속 PKM 주입이 개인화 적합도를 크게·일관되게 올림 입증(주입 방식 결정적: rag_context 0 vs binding 큰 효과). moat=fit/일관성(commodity 아님)과 정합. **단 정직한 한계**: ⓐ judge 약한 순환성(주입 반영 여부 측정=부분 자명) ⓑ fit≠value(사람 blind S3 로 확인) ⓒ 시뮬 PKM(compounding/시장 moat 미증명).
- **다음 = 가/다 빌드 (사용자 나→가→다)**: 가=실 auth 신원→생성 연결 + 실 brand_memory **구속 주입**(S2 교훈: rag_context 아닌 지시 슬롯) / 다=개인 PKM 테이블·개인별 메모리 기능. **동반 = S3 사람 blind**(fit→value 확인). ★ 사용자 진행 결정 대기(가 직행 vs S3 먼저 vs 병행).

**🟢 Phase 15 = director 모드 (output_mode 3rd tier) ✅ done (2026-06-03, archive)** — 로드맵 ① director. project-1 PARKED 제안서 기반. `output_mode` 를 **compact/rich/director** 3-tier 일반화(rich_output_enabled→enum, backward-compat) + **director**(rich + `hook_system`/`retention_architecture`/`scene_breakdown`) gated/additive. **Entry + S1(스키마 v1.3.0) + S2(P-006 v1.2.0) + S3(wiring) + S4(critic retention_design v1.3.0) + S5(frontend) + S6(director Plan-read fix + 라이브 검증 + cost)**. pytest 508→**536**(기존 508 수정 0=compact/rich byte-identical) + 프론트 build 12 routes + scenario_simulation 36/36 + 신규 endpoint/agent 0 + 키 0. CC-017~020. ★ **director API 라이브 PASS**(슬롯 전부 채워짐 + critic 10차원). ★ 발견·수정: Intent 오반려(별개 후속) + director Plan-read wiring 누락(fix ce6cf99). ★ 사용자 피드백: director=**초안 수준(기획 브리프)** — 대본 직접 쓰기엔 부족, 품질 보강은 이후 phase(commercial_viral + PKM/RAG). **다음 = pending_user_decision** — ① **Intent 오반려 개선 ✅ done (2026-06-03, CC-021 — P-001 v1.0.0→v1.1.0 콘텐츠 토픽 기본 수용 + 차단→재작성 가이드 UX; 라이브: "대학생활 TIP" 통과/날씨·코딩 거부 유지; ★ focused fix — PKM/RAG 의 provisional P16~17 와 번호 충돌 피해 미numbered)** / ② 검증 보강(human review + 전수 eval) / ③ PKM/RAG→commercial_viral(director 품질 보강) / rich default 전환 / 배포 Gate B~G. 신규 패턴 P-OUTPUT-SLOT-WIRING-001 + P-LIVE-VERIFY-001.

**🟢 Phase 14 = 위저드 ↔ 백엔드 실연결 ✅ done (2026-06-03, archive)** — 사용자 결정 **B** + **Scope A**(최소 배선). mock 위저드(/new/quick 4 · /new/discovery 7)를 기존 endpoint(`/plans/start`→`/wizard/{step}`→`/generate`→`/plan/[id]`)에 배선 → 위저드도 **실 3안 rich**(gated 상속). 신규 endpoint 0. **Entry + S1(백엔드 wizard_data additive 조립, 랜딩 byte-identical) + S2(Quick 실연결) + S3(Discovery 실연결) + fix(StrictMode navigation) + ★ 사용자 라이브 e2e PASS**(위저드→3안 rich→/plan/[id]). pytest 499→**508**(+9, 기존 499 수정 0) + 프론트 build 12 routes + scenario_simulation 36/36 + 키 0. 방향 근거 = project-1(6f30283a) 위저드 분석. per-step P-001~P-005 실 LLM 카드 = NG1(PARKED). ★ 발견·수정: StrictMode navigation 버그(7cb52e2) + dev 중 build .next 오염(복구·학습). **다음 = pending_user_decision** — rich default 전환(A) / 배포 Gate B~G(C) / 품질·정식화(D) / PARKED(commercial_viral·PKM-RAG, 선행=위저드 실연결 ✅ 충족). ★ **더 깊은 대본기획**(사용자 플래그) = PARKED 추후 업그레이드. (Phase 13 done(2026-06-03, archive) — rich gated 깊이 0.231→1.000.)

**🟢 Phase 13 출력 확장(Output Enrichment, compact→rich) ✅ done (2026-06-03, archive)** — Phase 12 가 입증한 깊이 격차(compact 0.231 → rich 잠재 1.0, 4.3x)를 운영 출력에 반영. ★ **이 프로젝트 첫 의도적 출력 변경**을 gated 로 안전하게 — `rich_output_enabled` default **False**(OFF=compact byte-identical / ON=rich) + additive 스키마(rich 12 슬롯 전부 Optional). Entry + 6 Slice 전부 ✅ + pytest 471→**499**(기존 471 수정 0 = OFF 회귀 0) + 키 0. **깊이 재측정(운영 run_planning OFF/ON 토글, get_settings.cache_clear) OFF 0.231 / ON 1.000(≥0.8 PASS, 4/4 편차 0)** + Critic depth 88점 함정 해소 + frontend rich 조건부 8섹션 + ★ **라이브 입증**(/generate end-to-end rich HTTP 200, rich 9슬롯 + beat visual/dialogue/caption + 화면 rich).
- **S1 ✅** (CC-012): output_schema §8.1 v1.1.0→v1.2.0 + rich 12 슬롯 additive + `model_dump_compact()` + agent-io-check PASS + test 10 → 471→481.
- **S2 ✅** (CC-013): planning `RICH_SYSTEM_PROMPT` + P-006 v1.0.0→v1.1.0(gated 공존) + test 5 → 481→486.
- **S3 ✅** (CC-014): config `rich_output_enabled` default False + 직렬화·프롬프트 분기, OFF byte-identical / ON rich + test 7 → 486→493(기존 486 수정 0).
- **S4 ✅** (CC-015): critic 9차원 `depth_actionability` + P-007 v1.2.0 gated + agent-io-check PASS + test 6 → 493→499. 88점 함정 해소.
- **S5 ✅**: frontend PlanCard rich 조건부 8섹션 순수 additive + 품질점수 숨김(`SHOW_QUALITY_SCORE` flag, 사용자 요청). backend 0.
- **S6 ✅** (CC-016): cost 재조정(`cost_control_policy.md` §13~§14 — rich 토큰 3~5배 × 3안 + B-RES-1 다중-provider 합산 통합) + 깊이 재측정 리포트(`eval/regression_results/2026-06-03_phase-13-s6-depth-remeasure.md`) + phase-complete(retrospective + closing + archive + REGISTRY/STATE done + patterns). ★ S6 = 문서/종료만, 런타임 .py 0.
- ★ **미결정/미완 (Phase 14 후보)**: rich default 전환 **미결정**(non_goal — gated OFF 유지, 사용자 opt-in) + 위저드(/new/*) ↔ 백엔드 실연결 미완(랜딩 / 만 실생성, 위저드 mock).
- 신규 패턴: P-GATED-OUTPUT-CHANGE-001(출력 변경 flag+additive+compact-serialize 회귀 0) + P-VALIDATION-DEPTH-GAP-001 update(Phase 12 계승 — 운영 재측정).

<details><summary>과거 Active Phase 요약 (Phase 12/11/10 — 보존)</summary>

**🟢 Phase 12 검증 페이즈 done (2026-06-02)** — MVP 출력 품질·가치 실측. 깊이 격차 4.3x 실측(compact 0.231 vs rich 1.000, 6/6 편차 0) → 결론(단순함=모델 한계 아님, prompt/schema 설계) + golden_set 15→25 + depth_actionability(CC-011) + human review kit(S4 실 채점 deferred). 운영 코드 0 + pytest 471 + 키 0. P-VALIDATION-DEPTH-GAP-001(신규 후보). 다음 = Phase 13 출력 확장.

**🟢 Phase 11 A안+B안 done (2026-06-02)** — LLM Gateway(A안 골격+cross_validation+gated hook / B안 3-provider 3안 라이브 입증). pytest 471 + behavior-preserving + 키 0. 다음 = Phase 12 검증 페이즈.


**🟢 Phase 10 ✅ done (2026-05-31) — MVP 통합 완료, 배포 Gate A 통과** — Phase M0~M3(meta detour) + Phase 10(MVP 통합) 완료. 다음 = 배포 Gate B~G(staging→알파→베타→운영, 키·인프라 user-provided + 운영 phase) 또는 Phase 11+(4계층 linkage / async worker / prompt A/B / 자동 promotion / 실 LLM eval default / M3 GAP). 사용자 결정 대기.

</details>

**Phase 10. MVP 통합 테스트 ✅ done (2026-05-31, 제품 phase scope C)** — Phase 1~9.5 누적 MVP 를 end-to-end 통합 검증(결함 0) + P-AUX-2 brand_memory_extractor agent 실구현 + 실 LLM eval mode capability(default mock) + RAG eval_rubric 정식화 + golden_set 11→15 + 배포 게이트 A~G 준비. ★ 제품 phase(런타임 有) — behavior-preserving(기존 0 수정) + 키 0 + PlanCard/component_map 0줄.

- **4 Slice + entry**:
  - entry [multi-llm-validation formal 10th V1~V6 + entry 8파일] ✅ (b4202ef)
  - S1 [MVP end-to-end 통합 test(12) + smoke_test_phase_10(12/12) + scenario_sim v8(36/36)] ✅ (7fa5b00)
  - S2 [P-AUX-2 brand_memory_extractor agent — heuristic·graceful·PII, additive hook + CC-008 agent_io v1.4.0] ✅ (436b224)
  - S3 [eval — 실 LLM mode capability(default mock) + RAG eval_rubric v1.0.0 + golden_set 11→15 + CC-009] ✅ (56b541c)
  - S4 [배포 게이트 A~G + ADR-038 + close] ✅
- **결과**: MVP end-to-end 통합 **PASS(연결 결함 0)** + pytest **339→381**(+42: 통합 12 + P-AUX-2 14 + eval 16, 기존 339 green) + P-AUX-2 활성(agent 5→6) + eval 성숙(golden_set 15 + RAG rubric + 실 LLM capability) + 배포 **Gate A 통과**(B~G 준비/정의).
- ADR-038(MVP 통합 scope C) + CC-008(agent_io P-AUX-2) + CC-009(eval golden_set/RAG rubric) + multi-llm-validation **10th**.
- ★ eval mode 화해: "범위 C 실 LLM 활성"=capability 구축 / "mock 유지"=default 실행. 실 LLM run=Gate D opt-in(키). 실 호출 0, 키 커밋 0.
- **핵심 성과**: P-X1 60연속 + behavior-preserving(기존 endpoint/agent 0 수정) + MVP 통합 검증 결함 0 + P-AUX-2 brand_memory_extractor + eval golden_set 11→15 + 배포 Gate A 통과 + PlanCard 35 / component_map 45 유지.
- 신규 패턴: P-INTEGRATION-MVP-001 + P-CAPABILITY-DEFAULT-OFF-001 + P-BEHAVIOR-PRESERVING-001 update(제품 통합) + P-X1-EFFECT-001(60) + P-CONTRACT-FIRST-001(CC 누적 10회).
- baseline: pytest 381 + P-X1 60 + agent 6 + golden_set 15 + Skill 21. 실측 ~12~15h.
- 다음: 배포 Gate B~G / Phase 11+ (M3 새 GAP 3 백로그 포함).

**Phase M3. 이질 도메인 dry-run (범용성 2차 검증) ✅ done (2026-05-31, ★ meta-phase)** — M2 개선 machinery(G1~G8)를 이질 도메인 **「개인 재무 플래닝 AI」**에 1회 dry-run 적용하여 도메인 범용성 2차 검증. M1(인접 팟캐스트)과 달리 이질(금융). 2 Slice dry-run + doc-sync. ★ machinery 0줄(개선본 읽기만) + 런타임 0(A9) + dry-run outputs/TEST/ 외 0(MG1).

- 한 줄 정의: M2 개선본을 이질 도메인(재무)에 적용 — ① 범용성 ② M2 개선 8요소 실사용 유효성 ③ 새 GAP. 사용자 분기: 수정 요소 없으면 Phase 10 직행.
- **2 Slice dry-run + doc-sync**:
  - 진입 [Phase M3 entry 8파일 — main] ✅ (d4aa7c5)
  - Slice S1 [재무 harness 생성 — domain_brief(G6 data_model + G5 제3자 PII) + blueprint(G1 expert/단일) + scaffold(G3 conditional + G4 applies_when + G7 harness_status), outputs/TEST/finance] ✅ (dbd4f7e)
  - Slice S2 [validation 6검증 + M2 G1~G8 유효성 점검 + 범용성 판정 + 새 GAP + 분기 권고] ✅ (3ad817e)
  - doc-sync [retrospective + 백로그(improvement_reports) + patterns + skill_usage_log + state + archive — main] ✅
- **결과**: 범용 **강함**(미디어 편향 0 — 창의 hook/3-variant/썸네일 강요 X, 재무 고유 리스크/적합성/규제 forbidden 으로 재정의) + M2 개선 **유효 7 / 부분 1(G3 문서) / 부적합 0** + 6검증 PASS 4/PENDING-BY-DESIGN 2(fail 0) + 새 GAP 3(NEW-G9/G10/G11, 전부 minor/nice-to-have, **blocking 0**).
- ★ **분기 = Phase 10 직행 가능** (범용 강함 + blocking GAP 0 + 새 GAP 백로그로 충분). 새 GAP 3 = `meta_factory/outputs/improvement_reports/2026-05-31_M3-new-gaps-backlog.md` 등록.
- harness-factory **세 번째 실 트리거** (M1 생성 → M2 재검증 → M3 이질 생성·검증).
- **핵심 성과**: P-X1 57연속 + ★ machinery 0줄(개선본 읽기만) + 런타임 0(A9) + 이질 도메인 범용성 입증(인접 M1 + 이질 M3 양쪽) + Skill 21 유지 + PlanCard 35 / component_map 45 유지.
- 신규 패턴: P-META-FACTORY-002 update(범용성 2차) + P-X1-EFFECT-001 update(57연속) + P-ADDITIVE-COMPAT-001(M2 개선 backward-compat 깨짐 0 재확인).
- baseline: pytest 339 유지(무관) + P-X1 57 + Skill 21. dry-run 실측 ~3h.
- 다음: ★ Phase 10 (MVP 통합 테스트) 기획 — 제품 로드맵 복귀. 새 GAP 3 백로그(Phase 10 후/차기 meta-phase).

**Phase M2. Meta-Factory GAP Remediation ✅ done (2026-05-31, ★ meta-phase)** — Phase M1 dry-run 이 발견한 8 GAP(G1~G8)을 meta_factory machinery 에 **additive** 반영(CC-007) + M1 TEST 팟캐스트에 재적용하여 before/after 로 해소 입증 (백로그 8→0). ★ M1(dry-run, machinery 0 변경)과 달리 M2 는 machinery 문서를 실제 변경 (L3 contract). 3 Slice sub-agent + doc-sync. ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9) + additive-only (기존 필드·절차 삭제 0 → M1 blueprint backward-compat).

- 한 줄 정의: M1 8 GAP 을 machinery additive 반영 (S1 생성-입력/절차 G1·G2·G5·G6 + S2 scaffold/schema G3·G4·G7·G8) + S3 재검증 (M1 TEST 재적용 before/after). 사용자 결정: 전체 8개 + re-validate.
- **3 Slice sub-agent + doc-sync (★ self-improvement loop 완주)**:
  - 진입 [Phase M2 entry 8파일 + validation self 아홉 번째 + proposal(M1 §D 추적) — main] ✅ (4626ad2)
  - Slice S1 [생성-입력/절차 — generation_workflow §4.1(G2) + architecture_patterns §2.1(G1) + domain_brief_schema 제3자 PII(G5)·data_model(G6), additive] ✅ (131ee06)
  - Slice S2 [scaffold/schema — agent+contract conditional(G3) + eval applies_when(G4) + project_state harness_status(G7) + blueprint pending-by-design(G8), additive] ✅ (2058661)
  - Slice S3 [재검증 — M1 TEST 재적용 8 GAP before/after + 6검증 재판정, outputs/TEST/] ✅ (dd45cdc)
  - doc-sync [CC-007 + ADR-037 + retrospective + patterns + skill_usage_log + state + archive — ★ main 별도 commit] ✅
- **결과**: 백로그 **8→0** (addressed 7 + expressible 1=G5) + 6검증 재판정 **PASS 5 / PENDING-BY-DESIGN 1** (검증3 조건부축 GAP 해소 / 검증5 G8 pending-by-design 명시) + backward-compat ✅ (M1 blueprint 개선 machinery 하 valid).
- ADR-037 (8 GAP 반영 + 재검증) + CC-007 (machinery 8 GAP additive — L3 contract) + harness-factory **두 번째 실 트리거** (S3 재검증) + contract-change **여덟 번째** (CC-007).
- multi-llm-validation **formal 아홉 번째** (V1~V5 PASS — 8 GAP 반영 타당성 / additive backward-compat / A9 / CC-007 scope / 재검증 계획).
- ★ A9 런타임 변경: backend/fastapi 0 / apps/web 0 / db/migrations 0. additive-only — 기존 machinery 필드·절차 삭제·재명명 0.
- **핵심 성과**: P-X1 55연속 + ★ 런타임 0(A9) + additive-only backward-compat + 백로그 8→0 + **Meta-Factory self-improvement loop 첫 완주 (M0 도입 → M1 검증·GAP → M2 반영·재검증)** + Skill 21 유지 + PlanCard 35 / component_map 45 유지.
- 신규 패턴: P-ADDITIVE-COMPAT-001 (additive 개선 backward-compat) + P-META-FACTORY-002 update (loop 완주) + P-X1-EFFECT-001 update (55연속) + P-VALIDATION-FORMAL-001 (아홉 번째) + P-CONTRACT-FIRST-001 (CC-007 누적 8회).
- baseline: pytest 339 유지 (machinery 문서 — import 무관) + P-X1 55 + Skill 21. meta-phase 실측 ~4h.
- 다음: 검증5 실 eval-run 표본 ✅ **완료** (203ced2 — mock-deterministic 3케이스 pass, schema 100%, G4 applies_when 실작동 입증, 검증5 PENDING-BY-DESIGN → measured baseline, `outputs/TEST/podcast_eval_run_sample.md`. 단서: 실 LLM 채점은 팟캐스트 실 구현 후) / 이질 도메인 dry-run (범용성 2차) / Phase 10 연결.

**Phase M1. Meta-Factory Sample Test ✅ done (2026-05-31, ★ meta-phase dry-run)** — Phase M0 가 만든 meta_factory machinery(generation_workflow 11단계 + validation_workflow 6검증)를 인접 도메인 **「팟캐스트 에피소드 기획 AI」** 에 **1회 dry-run** 적용하여 "실제로 도는가"를 검증. 목적은 "성공"이 아니라 **machinery 실작동 입증 + GAP 발견**. 산출물 전부 `meta_factory/outputs/TEST/` 격리 (★ 사용자 지침). 2 Slice dry-run(sub-agent) + doc-sync(main 세션 별도 commit). ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9) + dry-run 변경 outputs/TEST/ 외 0줄 (MG1).

- 한 줄 정의: M0 machinery 를 팟캐스트 도메인에 1회 dry-run — generation_workflow 로 harness_blueprint 생성 + validation_workflow 6검증(PASS/FAIL/PENDING/GAP 4상태) + with/without 6지표 수치화 + GAP 백로그 도출. 모든 산출물 outputs/TEST/ 격리, generated harness 는 6검증 PASS 에도 active 아님 (factory_contract 규칙 7).
- **2 Slice dry-run + doc-sync (★ GPT 보완 ③ 분리)**:
  - 진입 [Phase M1 entry 8파일 + outputs/TEST/README — main 세션] ✅ (12a87c9)
  - Slice S1 [generation — without baseline + domain_brief + harness_blueprint + 6 scaffold, sub-agent outputs/TEST/ only] ✅ (dbe43c5)
  - Slice S2 [validation — 6검증 4상태 + with/without 6지표 + 5gaps 재현 + GAP 8, sub-agent outputs/TEST/ only] ✅ (83fc1ac)
  - doc-sync [retrospective + ADR-036 + patterns + skill_usage_log + state docs + archive — ★ main 세션 별도 commit] ✅
- **GPT M0 검토 보완 3건 반영**: ① with/without 6지표 수치화(주관 서술 0) / ② 판정 PASS·FAIL·PENDING·GAP 4상태(첫 dry-run fail/pending 정상) / ③ outputs 외 변경 0 강제 + phase 기록 별도 doc-sync 분리. + meta-phase 분리(제품 phase 무관).
- **결과**: 6검증 **PASS 5 / PENDING 1**(검증5 eval-run = 실측 미수행 정상) + blueprint validation 3필드 pass/pass/pass + with/without WITH≫WITHOUT(누락 0v6 / cross-ref 누락 0v4 / eval gate 1v0) + 5 gaps **전부 재현**(5/0/0) + **GAP 8개**(핵심 G2 skill 재사용 결정트리 / G3 conditional_execution 슬롯 / G5 제3자 PII).
- **machinery 작동 결정 증거**: 검증2(skill conflict)가 podcast-eval-run 신규 Skill 의 eval-run 키워드 4중첩 검출 → 채택 사전 차단.
- ADR-036 (Meta-Factory 첫 dry-run 방법·결과) + harness-factory Skill **★ 첫 실 트리거** (M0 등록 → M1 실 트리거, payoff deferred 첫 실증).
- **핵심 성과**: P-X1 52연속 + ★ 런타임 0(A9) + dry-run outputs/TEST/ 외 0(MG1) + machinery 실작동 입증 + GAP 8 백로그 + Skill 21 유지(신규 0) + PlanCard 35 / component_map 45 유지.
- 신규 패턴: P-META-FACTORY-002 (Meta-Factory 첫 dry-run — 실작동 입증 + GAP 백로그) + P-X1-EFFECT-001 update (52연속).
- baseline: pytest 339 유지 (런타임 무관 — dry-run) + P-X1 52 + Skill 21. meta-phase dry-run 실측 ~2.5~4h.
- 다음: 8 GAP machinery 보완 proposal (G2/G3/G5 우선, contract-change 경유) / 검증5 실측 1회 (eval-run §3~§6) / Phase 10 연결 (meta_factory blueprint + TEST 산출물 = 온보딩·감사 참고).

**Phase M0. Meta-Factory Prep ✅ done (2026-05-31, ★ meta-phase)** — 현재 구현 하네스(L2)를 유지하면서 상위에 `harness/meta_factory/` (L3 Meta-Harness Factory) skeleton + contract + validation 기준을 추가. proposal-first 메타 레이어 — ① 현재 하네스 blueprint 역정리 ② 새 도메인 하네스 생성 입력/출력 구조 ③ Agent/Skill/Contract/Eval/Phase 생성 전 검증 기준. **자동 generator 구현이 아니라 skeleton·contract·validation 정의까지만** (payoff deferred, NG11). 3 Slice 모두 sub-agent dispatch 완료. ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9).

- 한 줄 정의: L1 Product Runtime / L2 Implementation Harness / L3 Meta-Harness Factory 3계층 모델을 명문화하고, meta_factory/ skeleton + factory_contract(8 규칙, proposal-first) + domain_brief/harness_blueprint schema + architecture_patterns(6 + Dreammate 매핑) + workflow + templates + 현재 하네스 blueprint + harness-factory Skill(proposal-only)을 도입한다. ★ 런타임 변경 0 (A9).
- **3 Slice 모두 sub-agent dispatch 완료 (런타임 변경 0)**:
  - Slice 1 [Pre-Entry — validations(V1~V6 PASS) + ADR-035 + meta_factory 핵심 5 문서 (README/factory_contract/domain_brief_schema/harness_blueprint_schema/architecture_patterns)] ✅ (28f9634)
  - Slice 2 [generation_workflow + validation_workflow + templates(6) + 현재 하네스 blueprint 실측 역정리 + outputs .gitkeep] ✅ (780a615)
  - Slice 3 [harness-factory Skill (proposal-only, 키워드 scoped, #21) + INDEX 등록 + CC-006 + proposal + smoke_test_phase_M0 6/6 + scenario_sim v7 33/33 + 회고 + archive + state docs] ✅ (final)
- **사용자 결정 3건 반영 (2026-05-31)**:
  - **meta-phase (Phase M0, 3 Slice)** — PHASE_REGISTRY 제품 phase(10/11)와 번호 분리, archive/회고/P-X1 규율 유지.
  - **harness-factory Skill 추가** (proposal-only, 키워드 scoping) — Slice 3.
  - **proposal-first** — 생성물은 meta_factory/outputs/ 또는 meta/proposals/에 먼저 (자동 적용 X).
- ADR-035 (L3 Meta-Factory 도입 — L1/L2/L3 모델 + proposal-first + payoff deferred + skeleton-only) + CC-006 (INDEX harness-factory #21 Skill 등록 — Skill 도 contract 처럼 취급).
- multi-llm-validation **formal 여덟 번째** (V1~V6 PASS — L3 도입 타당성/런타임0/proposal-first/meta-phase/Skill scoping/blueprint 실측) + ★ 첫 meta-phase 적용.
- ★ A9 런타임 변경: backend/fastapi 0 / apps/web 0 (PlanCard·component_map 0줄) / db/migrations 0 (git diff fff913e..HEAD 게이트 PASS, smoke Step 1).
- **핵심 성과**: P-X1 50연속 + L3 Meta-Factory skeleton (meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs) + harness-factory Skill proposal-only (21번째, 키워드 scoped 충돌 0) + pytest 339 유지 + smoke 6/6 + scenario_sim v7 33/33 (P-X2 아홉 번째) + Skill 20→21.
- 신규 패턴: P-META-FACTORY-001 (L3 proposal-first 메타 레이어) + P-X1-EFFECT-001 update (50연속) + P-VALIDATION-FORMAL-001 update (여덟 번째).
- baseline: pytest 339 + P-X1 50 + PlanCard 35 + component_map 45 + Skill 21 (런타임 무관 — meta-phase). meta-phase 실측 ~4~7h.

**Phase 9.5. eval-run 정식화 + Critic deprecated 0–5 Full 제거 ✅ done (2026-05-31)** — golden_set 회귀 runner(mock-deterministic, CI 가능) + revise effect eval 구현 → eval-design/eval-run Skill 첫 정식 → eval 로 canonical-only 품질 검증 후 Critic deprecated 0–5 fallback + CriticEvaluation Optional deprecated 필드 Full 제거 (Critic 평가 체계 canonical 0–1 단일 표준화). 5 Slice 모두 sub-agent dispatch 완료 (P-X1 47연속 + pytest 339 + eval gate PASS + Critic warnings 0).

- 한 줄 정의: golden_set 11 케이스 회귀 runner(mock-deterministic primary + 실 LLM mode flag)와 revise effect eval 을 구현하여 eval-design/eval-run Skill 을 첫 정식 트리거하고, eval 로 canonical-only 품질을 검증한 뒤 Critic deprecated 0–5 fallback + CriticEvaluation Optional deprecated 필드를 Full 제거한다 (run_critic 0–5 출력 불변 — P-007 prompt contract).
- **5 Slice 모두 sub-agent dispatch (★ 순서: eval runner(2~3) → eval 검증 → deprecated 제거(4))**:
  - Slice 1 [Pre-Entry — validations(V1~V7 PASS) + eval-design Skill ★ 첫 정식 + ADR-033/034] ✅ (entry commit)
  - Slice 2 [eval-run golden_set runner — loader + mock 회귀 + 채점 + 임계값 + report + eval-run ★ 첫 정식] ✅ (bfac0c4)
  - Slice 3 [revise effect eval + eval-run 실행 (canonical-only 품질 baseline)] ✅ (8a18276)
  - Slice 4 [Critic deprecated 0–5 Full 제거 — eval 검증 후 + contract-change CC-005] ✅ (864e83e)
  - Slice 5 [Close] ✅ (fff913e)
- **사용자 결정 2건 반영 (2026-05-31)**:
  - **Critic deprecated 0–5: Full 제거** — select_best_plan_index fallback + DeprecationWarning + CriticEvaluation Optional deprecated 필드. ★ run_critic 0–5 출력 불변 (P-007 prompt contract, NG3). eval 검증 후 제거 (순서).
  - **eval-run: Mock-deterministic primary** + 실 LLM mode 문서. RAG eval_rubric Phase 10+ 이관 (NG1).
- ADR-033 (eval-run harness — mock-deterministic primary + 실 LLM mode + §eval-design 결과 + 임계값 게이트 + regression_results) + ADR-034 (Critic deprecated 0–5 Full 제거 — fallback + CriticEvaluation Optional 필드, run_critic 0–5 불변, eval 검증 순서).
- **eval-design Skill ★ 첫 정식 트리거** (Slice 1, ADR-033 §eval-design) + multi-llm-validation **formal 일곱 번째** (V1~V7 PASS).
- baseline: pytest 293 + smoke 15 + scenario_sim v5 25 + P-X1 42 + PlanCard 30 + component_map 40 (Phase 9 종료 baseline 유지).
- ★ golden_set 케이스 수 정정: 현 golden_set.md v1.0.0 §2 는 GS-001~GS-011 (11 케이스)만 정의 (entry plan 일부 "47" 기재 → 정정, 케이스 확대 NG10 Phase 10+).

**Phase 9. 결과 저장 + 피드백 ✅ done (2026-05-31)** — plan 선택/피드백 영속화(실 plans 테이블 정합) + normalize_to_canonical wiring(critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0) + Brand Memory 준비(P-AUX-2 설계, agent 미구현 Phase 10+) + 피드백 UI wrapper(PlanCard·component_map 무수정). 6 Slice 모두 sub-agent dispatch 완료.

- 한 줄 정의: 사용자 plan 선택/수정/반려/피드백을 영속화(Phase 5 PlansRepo graceful 패턴)하고, Critic canonical(0–1)을 live pipeline에 연결하며, Brand Memory 자동 추출 인프라(schema + ADR + 적재 경로)를 준비하고, 선택/반려 피드백 UI를 page.tsx inline wrapper로 추가하여 MVP 피드백 루프를 완성.
- **6 Slice 모두 sub-agent dispatch 완료**:
  - Slice 1 [Pre-Entry — validations + security-review(두 번째 정식, 피드백 PII) + ADR-030/031/032] ✅ (de92e37)
  - Slice 2 [Schema 0005 + Repo (selection/feedback/brand_memory) graceful + contract-change CC-004 + PII 마스킹] ✅ (56cd3f0)
  - Slice 3 [API endpoints (select/feedback) + normalize_to_canonical wiring, pytest 261→284] ✅ (d6e3fa0)
  - Slice 4 [Brand Memory 준비 — feedback→candidate 적재 경로 + ADR-031 finalize, pytest 284→293] ✅ (bc94e1b)
  - Slice 5 [Frontend 피드백 UI (page.tsx inline wrapper) — PlanCard·component_map 0줄, tsc 0 + build 11 routes] ✅ (4d38062)
  - Slice 6 [Close] ✅ (final)
- **사용자 결정 3건 반영 (2026-05-29)**:
  - Brand Memory: **준비만** (ADR + schema + 피드백 적재) — P-AUX-2 agent 미구현, 자동 추출 Phase 10+ (사용자 결정 5 누적 confirm)
  - Frontend: 피드백 UI 포함 (wrapper) — 선택/반려 page.tsx inline, PlanCard·component_map 무수정
  - normalize_to_canonical: Phase 9 연결 — critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0 (Phase 8 개선 §1)
- ADR-030 (feedback/selection persistence — 실 plans 정합, graceful PlansRepo 패턴) + ADR-031 (Brand Memory 준비 — P-AUX-2 설계, agent 미구현 Phase 10+) + ADR-032 (normalize_to_canonical wiring — critic step canonical, deprecated 병행) + CC-004 (db_schema.md feedback/selection 실 plans 정합).
- **핵심 성과**: P-X1 42연속 + PlanCard 30연속 + component_map 40연속 + pytest 249→293 (+44, 기존 수정 0) + smoke 15/15 + scenario_sim v5 25/25 (P-X2 일곱 번째) + security-review 두 번째 정식 + deprecated warnings 67→16.
- 신규 패턴: P-FEEDBACK-LOOP-001 + P-CANONICAL-WIRING-001 + P-X1-EFFECT-001 update (42연속) + P-VALIDATION-FORMAL-001 update (여섯 번째).
- baseline: pytest 293 + smoke 15 + scenario_sim v5 25 + P-X1 42 + PlanCard 30 + component_map 40.

**다음 phase 옵션 (사용자 결정 대기)**:
- **A. Phase 9.5 — eval-run Skill 정식화** (4~6h): golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 7회 해소) + Critic deprecated 0–5 fallback 완전 제거 (Phase 9 canonical live 활성 → 다음 단계) + 간이 RAG eval_rubric → 정식 + eval-design/eval-run 첫 정식 baseline
- **B. Phase 10 — MVP 통합 테스트** (6~8h): MVP end-to-end 검증 (Discovery + Quick → 3-plan → Critic revise (canonical) → save → select → feedback → SSE progress) + Phase 1~9 누적 baseline 통합 회귀 + P-AUX-2 brand_memory_extractor agent 실 구현 + 배포 테스트 게이트 준비
- **C. 다른 우선순위** (Phase 11+): 4계층 full linkage (plan_options/video_projects, 누적 2회) / 사용자 데이터 자동 promotion (rag-update 두 번째) / SSE full async worker / prompt A/B 실행 인프라 / Supabase SQL function 정의 / cost-review Skill

**Phase 8. MOA Lite 본격 ✅ done (2026-05-29)** — orchestrator 추출 (behavior-preserving) + SSE Progress worker 통합 + prompt_registry semver 정식화. 5 Slice 모두 sub-agent dispatch 완료.

- 한 줄 정의: `plans_generate()` god-function의 MOA orchestration을 service layer orchestrator로 추출(behavior-preserving) + SSE Progress 실 stage 연동 + prompt_registry P-001~P-008 + AUX semver 정식화.
- **5 Slice 모두 sub-agent dispatch 완료**:
  - Slice 1 [Pre-Entry — validations + ai-architecture-review + prompt-version-review(분석) + ADR-027/028/029] ✅ (8fbb645)
  - Slice 2 [MOA Orchestrator 추출 (behavior-preserving) + ProgressSink] ✅ (c25367a)
  - Slice 3 [SSE Progress worker 통합 — progress_store 브릿지] ✅ (f5c534a)
  - Slice 4 [prompt_registry 정식화 — contract-change CC-003 + prompt-version-review 적용] ✅ (c7c7376)
  - Slice 5 [Close] ✅ (final)
- **사용자 결정 3건 반영 (2026-05-29)**:
  - Scope: 3개 모두 (A orchestrator + B SSE + C prompt_registry, 5 Slice, 12~16h)
  - Critic drift: **Conservative adapter** — Phase 6 canonical(0–1) 불변 (ADR-018 보존) + P-007 prompt(0–5) 유지 + 코드 0–1 정규화 adapter + P-007 v1.0.0→v1.1.0
  - SSE: in-memory progress_store 브릿지 (graceful, background task 미도입 — moa_policy §4 sync, async Phase 11+)
- **★ behavior-preserving 입증**: orchestrator 추출 = Envelope byte-identical + 기존 pytest 223 수정 0 (의도된 2 version assertion 제외 — 회귀 0 = 동작 불변 증거)
- **첫 정식 트리거 2개 완료**: ai-architecture-review (MOA orchestration 설계 → ADR-027 + Slice 5 회고) + prompt-version-review (P-007 Critic semver → ADR-029, Slice 1 분석 + Slice 4 적용)
- ADR-027 (MOA orchestrator) + ADR-028 (SSE progress integration) + ADR-029 (prompt_registry semver) + CC-003 (prompt_registry + agent_io_contract).
- plans.py 659 → 243 LOC (god-function 분해) + PlanCard.tsx 0줄 + component_map.md 0줄 유지 (backend-only phase) ★.

**다음 phase 옵션 (사용자 결정 대기)**:
- **A. Phase 9 — 결과 저장 + 피드백** (6~10h): plan 선택/수정/반려 누적, Brand Memory 자동 추출 ADR 신규, normalize_to_canonical wiring, per-user rate-limit + audit-log
- **B. Phase 9.5+ — eval-run Skill 정식화** (4~6h): golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 6회 해소) + Critic deprecated 0–5 fallback 완전 제거 + 간이 RAG eval_rubric 정식
- **C. Phase 10 — MVP 통합 테스트** (6~8h): MVP end-to-end 검증 + Phase 1~8 누적 baseline 통합 회귀 + 배포 테스트 게이트 준비
- **D. 다른 우선순위** (Phase 11+): SSE full async worker / prompt A/B 실행 인프라 / 사용자 데이터 자동 promotion / Supabase SQL function 정의 / cost-review Skill

**Phase 1. MVP 기본 플로우 ✅ done (2026-05-26)** — archive 이동 완료

**Phase 2. design.md 기반 PWA 설계 ✅ done (2026-05-27)** — archive 이동 완료

**Phase 3. Next.js PWA 기본 UI 구현 ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS / audit_naming + audit_page_component 0 drift / 변경성 4/5+1 WARN / P-X1 5/5 / component_map 6연속 0줄

**Phase 4. FastAPI 기본 백엔드 구현 (확장) ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS / audit_naming + audit_page_component 0 drift (D-1 Slice 4 해소) / 변경성 4/5+1 WARN (Phase 3 결과 유지, Phase 4 +0 영향)
- **P-X1 9연속 PASS (Phase 3 5 + Phase 4 4) + component_map 15연속 0줄 + PlanCard 4연속 0줄** ★
- GPT 검토 채택 효과: 6→4 Slices (▼33%), 18~26h → 6~8h (▼66%)
- smoke_test_phase_4 8/8 PASS
- 신규 패턴: P-GPT-REVIEW-001 + P-X1-EFFECT-001 update (9연속)

**Phase 4.5. Critic Revise Loop + Rewriter + Z-X3 Best-Plan + P-X2 ✅ done (2026-05-28)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M3 3/3 PASS / audit_naming + audit_page_component 0 drift × 2 / 변경성 시뮬 5/5 PASS (P-X2 첫 자동 게이트) / smoke_test_phase_4_5 9/9 PASS / pytest 109/109 (+16 신규)
- **P-X1 13연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4) + PlanCard 9연속 0줄 + component_map 19연속 0줄** ★
- **multi-llm-validation formal 첫 트리거** (Claude Code 자가 검증 V1~V4 PASS + 외부 placeholder 분리)
- **P-X2 자동 게이트 첫 작동** (scenario_simulation.ps1 5/5 PASS via phase-complete v1.2.0 §1.6)
- 신규 패턴: P-X2-EFFECT-001 + P-VALIDATION-FORMAL-001 + P-X1-EFFECT-001 update (13연속)
- Sub-agent 4/4 (모두 sub-agent dispatch) + Slice 4 close (final)

**Phase 6. Output Schema + Agent IO Stabilization ✅ done (2026-05-29)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M3 3/3 PASS / audit_naming + audit_page_component 0 drift × 2 / scenario_simulation 5/5 (P-X2 두 번째 자동 게이트) / schema_stress_test 5/5 (P-X2 v2 신규) / smoke_test_phase_6 10/10 PASS / pytest 144/144 (+35 신규)
- **P-X1 17연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4) + PlanCard 12연속 0줄 + component_map 22연속 0줄** ★
- **Critic verdict canonical 결정** (overall_score + dimensions, ADR-018) + **Rewriter v1.0.0 → v1.1.0** (Pydantic + graceful, ADR-019)
- **contract-change Skill 첫 본격 실 변경 통과** (output_schema + agent_io_contract + api_contract 3 contract + 회귀 0)
- **agent-io-check Skill 첫 정식 트리거** (Rewriter v1.1.0 + Critic canonical 정합 PASS)
- **multi-llm-validation formal 두 번째 트리거** (V1~V5 PASS, P-VALIDATION-FORMAL-001 두 번째 입증 → 정식 패턴 확정)
- 신규 패턴: P-CRITIC-CANONICAL-001 + P-CONTRACT-FIRST-001 (신규 후보) + P-X1-EFFECT-001 update (17연속) + P-VALIDATION-FORMAL-001 update (두 번째)
- Sub-agent 4/4 (모두 sub-agent dispatch) + Slice 4 close (final)
- GPT 검토안 6→4 Slice 압축 (▼33%) + 시간 8~12h → 실측 ~8h (▼20%, P-GPT-REVIEW-001 두 번째 적용)

**Phase 5. DB / Auth / RLS / SSE ✅ done (2026-05-29)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M4 4/4 PASS / audit_naming 0 drift × 2 / audit_page_component 2 intended drift WARN (Slice 3 AuthGuard + /login route 신규) / scenario_simulation v2 10/10 (P-X2 세 번째 자동 게이트) / schema_stress_test 5/5 (Phase 6 v2 유지) / smoke_test_phase_5 12/12 (11 PASS + 1 WARN intended) / pytest 170/170 (+26 신규)
- **P-X1 22연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5) + PlanCard 17연속 0줄 + component_map 27연속 0줄** ★
- **Supabase + 4계층 schema migration + plans_repo** (Slice 2 — db_schema.md contract + ADR-020)
- **Auth + JWT (httpOnly cookie) + Frontend Login + AuthGuard wrapper** (Slice 3)
- **RLS 정책 (auth.uid() + 4 정책 + 2-hop subquery) + SSE Progress 4단계 D7** (Slice 4 — ADR-021/022)
- **security-review Skill 첫 정식 + 두 번째 final** (Slice 1 entry T1~T6 + Slice 5 verification)
- **contract-change Skill 두 번째 본격 실 변경 통과** (db_schema.md 신규)
- **multi-llm-validation formal 세 번째 트리거** (V1~V6 PASS, P-VALIDATION-FORMAL-001 정식 패턴 확정 — 3회 누적)
- **agent-io-check Skill 두 번째 회귀 검증** (Phase 6 baseline 유지 PASS)
- 4 ADR 신규 (ADR-020 Supabase + ADR-021 RLS + ADR-022 SSE)
- 신규 패턴: P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 (신규 후보) + P-X1-EFFECT-001 update (22연속) + P-VALIDATION-FORMAL-001 update (세 번째 정식 확정)
- Sub-agent 5/5 (모두 sub-agent dispatch) + Slice 5 close (final)
- graceful fallback 일관 적용 — Supabase 미설정 시 in-memory dict 회귀 0
- 실측 시간 ~14-16h (추정 15~20h 내)

**Phase 5.5. Legacy DB Consolidation + Validation Strengthening + Phase 7 Prep ✅ done (2026-05-29)** — archive 이동 완료
- A1~A8 8/8 PASS + M1~M2 2/2 PASS / audit_naming 0 drift / audit_page_component 2 intended drift WARN (Phase 5 baseline 유지) / scenario_simulation v2 10/10 (P-X2 네 번째 자동 게이트) / schema_stress 5/5 / smoke_test_phase_5 12/12 / pytest 170→172 (+2 legacy deprecation 검증)
- **P-X1 26연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4) + PlanCard 18연속 0줄 + component_map 28연속 0줄** ★
- **Legacy DB 옵션 A 채택** (ADR-023 — 공존 + deprecated note + 지연 통합) + **ADR-024 Phase 7 RAG scope evolution** (5단계 MVP + 확대 지점 A~F)
- **External validation × 3 self-strengthen** — V-form 합의 추정 PASS (Phase 4.5/6/5)
- **Brand Memory Phase 9+ confirmation** (NG2 + ADR-024 cross-ref)
- **legacy backward-compat 100% 유지** (Phase 1 baseline 보호 + Phase 5 baseline 보호 동시 달성)
- 신규 패턴: P-LEGACY-CONSOLIDATION-001 신규 후보 + P-X1-EFFECT-001 update (26연속) + P-VALIDATION-FORMAL-001 update (self-strengthen V-form sub-pattern)
- Sub-agent 4/4 (모두 sub-agent dispatch) + Slice 4 close (final)
- mini-phase consolidation 패턴 효과 입증 (실측 ~4-5h, 추정 4~6h 내)

**Phase 7. RAG Lite (candidate_knowledge 5단계 MVP 전부) ✅ done (2026-05-29)** — archive 이동 완료
- A1~A10 10/10 PASS + M1~M4 4/4 PASS / audit_naming 0 drift / audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) / scenario_simulation v3 15/15 (P-X2 다섯 번째 자동 게이트) / schema_stress 5/5 / smoke_test_phase_7 13/13 (12 PASS + 1 WARN intended) / pytest 172 → 223/223 (+51 신규)
- **P-X1 31연속 PASS (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5) + PlanCard 19연속 0줄 + component_map 29연속 0줄** ★
- **5단계 파이프라인 전부 MVP 구현** (사용자 결정 4 Phase 5.5 명시 — ADR-024 §5단계 MVP) — pending → filtered → evaluated → approved → promoted + hybrid 승인 (자동 ≥0.8 / 수동 0.6~0.8 / 거부 <0.6) + promotion_history JSONB
- **pgvector retrieval** (cosine + top-k=5 + threshold=0.7) + **OpenAI text-embedding-3-small** + **chunking 512 tokens + overlap 50** + **LLM Wiki vs RAG 분리 (RAG > LLM Wiki 우선순위)**
- **rag-design Skill ★ 첫 정식 트리거** (Slice 1, ADR-025 RAG architecture)
- **rag-update Skill ★ 첫 정식 트리거** (Slice 4, 5단계 승격 절차)
- **contract-change Skill 본격 세 번째** (rag_data_contract.md §18 신규 — 5단계 stage enum + promotion_history + retrieval 정책)
- **multi-llm-validation formal 네 번째 트리거** (V1~V7 PASS — ADR-024 / chunk 512 / top-k=5 threshold=0.7 / embedding / graceful / LLM Wiki vs RAG / hybrid)
- **agent-io-check Skill 세 번째 회귀 검증** (agents/rag.py Phase 1 baseline 호환 + Phase 7 통합 wrapper, Critic/Rewriter 회귀 0)
- 2 ADR 신규 (ADR-025 RAG architecture + ADR-026 5단계 promotion logic)
- 신규 패턴: P-RAG-5STAGE-001 (5단계 transition + hybrid 승인) + P-RAG-GRACEFUL-001 (5종 marker + RAG > LLM Wiki) + P-X1-EFFECT-001 update (31연속) + P-VALIDATION-FORMAL-001 update (네 번째) + P-LEGACY-CONSOLIDATION-001 update (누적 2회 — Phase 1 legacy rag ↔ Phase 7 신규 공존)
- Sub-agent 5/5 (모두 sub-agent dispatch) + Slice 5 close (final)
- graceful 5종 marker 표준화 (rag_unavailable / rag_no_results / llm_wiki_unavailable / embedding_failed / supabase_unconfigured) — P-GRACEFUL-001 (Phase 1) 정신 5번째 입증
- Phase 1 legacy rag/{retriever, fallback}.py + Phase 7 rag/retrieval.py 공존 (P-LEGACY-CONSOLIDATION-001 누적 2회 — Phase 11+ Custom RAG 시점 자연 통합)
- 실측 시간 ~13~14h (추정 12~16h 내)

**🟡 Now: pending_user_decision** — Phase M0 ✅ done (2026-05-31, ★ meta-phase). L3 Meta-Harness Factory skeleton + contract + validation 완료 (3 Slice 모두 sub-agent, ★ 런타임 변경 0 A9). meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs + harness-factory Skill proposal-only (#21) + ADR-035 + CC-006. P-X1 50연속 + Skill 20→21 + scenario_sim v7 33/33. Phase 9.5 ✅ done (2026-05-31). 제품 phase 옵션(A Phase 10 MVP 통합 / B Phase 11+)은 보존 — M0 meta-phase detour 종료, 제품 로드맵 복귀.

## 이전 결정 (옵션 B 변형: Phase 6 선행)

사용자 결정 (2026-05-29): 옵션 A/B/C 중 **옵션 B 변형 채택** → Phase 6 선행 → Phase 5 순차 진행.
- Phase 6 = Output Schema + Agent IO Stabilization (8~10h, mini-phase)
- Phase 5 = DB/Auth (Phase 6 종료 후 진입, formal external validation 의무)
- GPT 검토안 7.5/10 채택 (Critic canonical / Rewriter contract / fallback 축소 / frontend 정합)
- 6→4 Slice 압축 (P-GPT-REVIEW-001 정신)

## migration_progress

```yaml
current_sprint: "phase-M0-slice-3"
current_sprint_step: phase_m0_slice_3_close_done
total_steps_in_sprint: 3
last_completed_action: "Phase M0 (Meta-Factory Prep, ★ meta-phase) Slice 3 close — harness-factory Skill 신규 (.claude/skills/harness-factory/SKILL.md, proposal-only, 키워드 scoped, #21) + INDEX.md 등록 (20→21 + Meta-Factory 섹션 + 우선순위 3 관계 + 키워드 충돌 검토 0) + CC-006 (INDEX Skill 등록, Skill 도 contract 처럼 취급) + proposal + harness-audit §3 키워드 충돌 검토 (충돌 0) + smoke_test_phase_M0.ps1 (6/6 PASS — A9 런타임 0 + pytest 339 + audit_naming + meta_factory 구조 + Skill #21 + frontend 0) + scenario_simulation v7 (33/33, P-X2 아홉 번째, SM1~SM3) + retrospectives/phase-M0.md + patterns (P-X1 50연속 + P-META-FACTORY-001 신규 + P-VALIDATION-FORMAL-001 여덟 번째) + skill_usage_log (20→21) + closing_notes + archive 이동 + state docs. ★ A9 런타임 변경 0 (git diff fff913e..HEAD backend/fastapi 0 / apps/web 0 PlanCard·component_map / db/migrations 0). P-X1 50연속. baseline: pytest 339 + P-X1 50 + PlanCard 35 + component_map 45 + Skill 21 (런타임 무관)"
next_action: "다음 phase 사용자 결정 대기 (meta-phase detour 종료) — A Phase 10 MVP 통합 / B Phase 11+. Phase M0 후속: harness-factory dry-run / trigger validation 샘플 / with-without 비교 샘플 (Phase M1+) / Phase 10 연결 (meta_factory blueprint = 온보딩·감사 baseline)"
blocker: null
phase_m0_status: completed
phase_m0_type: meta-phase
phase_m0_entry_date: 2026-05-31
phase_m0_completion_date: 2026-05-31
phase_m0_archive_location: phases/archive/phase-M0-meta-factory/
phase_m0_total_slices: 3  # 모두 sub-agent
phase_m0_completed_slices: 3  # Slice 1~3 모두 PASS
phase_m0_estimated_hours_total: 4-7
phase_m0_actual_hours: ~4-7  # 3 sub-agent dispatch
phase_m0_acceptance_passed: 10/10  # A1~A10
phase_m0_meta_acceptance_passed: 3/3  # M1~M3
phase_m0_runtime_change: 0  # ★ A9 — FastAPI/Next.js/Supabase 0줄 (git diff fff913e..HEAD backend/apps/migrations = 0)
phase_m0_pytest_result: 339/339  # Phase 9.5 baseline 유지 (런타임 무관)
phase_m0_smoke_test: 6/6 PASS  # smoke_test_phase_M0.ps1 신규 (경량 meta-phase)
phase_m0_scenario_simulation_v7: 33/33 PASS (auto-gate, 아홉 번째)  # P-X2 아홉 번째 자동 게이트 (SM1~SM3 추가)
phase_m0_audit_naming_final: 0 drift
phase_m0_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 계승 (meta-phase frontend 0줄 +0)
phase_m0_p_x1_self_verification: 3/3 PASS  # Slice 1~3 모두
phase_m0_p_x1_cumulative_streak: 50  # Phase 3 5 + ... + Phase 9.5 5 + Phase M0 3 ★
phase_m0_component_map_zero_lines_streak: 45  # meta-phase frontend 0줄 (유지)
phase_m0_plan_card_zero_lines_streak: 35  # meta-phase frontend 0줄 (유지)
phase_m0_skill_count: 21  # 20 → 21 (harness-factory proposal-only)
phase_m0_deviation_count: 0
phase_m0_user_decisions_applied:
  meta_phase_isolation: yes  # phase-M0 제품 phase 번호 분리, 제품 로드맵 보존
  harness_factory_proposal_only: yes  # 키워드 scoped, generated harness 자동 active X
  proposal_first: yes  # 생성물 outputs/meta proposals 먼저
  all_slices_sub_agent: yes  # 3 Slice 모두 sub-agent dispatch
phase_m0_adr_created:
  - ADR-035  # L3 Meta-Factory 도입 (phase_M0_meta_factory.md)
phase_m0_contracts_changed:
  - .claude/skills/INDEX.md  # CC-006 — harness-factory #21 Skill 등록 (Skill 도 contract 처럼 취급)
phase_m0_skills_first_trigger:
  - harness_factory  # ★ 신규 등록 (#21, proposal-only, 트리거 0 — payoff deferred)
  - multi_llm_validation_formal_eighth  # 여덟 번째 (★ 첫 meta-phase, V1~V6)
  - contract_change_seventh  # CC-006 (INDEX Skill 등록)
  - phase_complete_v1_2_0_ninth  # P-X2 자동 게이트 아홉 번째 (scenario_sim v7 33/33)
phase_m0_new_patterns:
  - P-META-FACTORY-001  # L3 proposal-first 메타 레이어 (신규 후보)
  - P-X1-EFFECT-001 (update 50연속)  # ★ 첫 meta-phase 에서도 런타임 0줄 격리
  - P-VALIDATION-FORMAL-001 (update 여덟 번째)  # ★ 첫 meta-phase 적용
phase_m0_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 50연속 누적 입증 (Phase 3:5 + ... + Phase 9.5:5 + Phase M0:3)
phase_m0_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~3 (Phase M1+)
phase_m0_deferred_to_next:
  - auto_generator  # Phase M1+ (generation_workflow 실행 도구 — 2nd 하네스 착수 시점)
  - claude_agents_dir_generation  # Phase M1+ (agent_template.md 기반)
  - trigger_dry_run_with_without_sample  # Phase M1+ / generated harness 첫 생성 시점
  - harness_factory_dry_run  # Phase M1+ / 2nd 하네스 착수 시점
phase_0_status: completed
phase_0_completion_date: 2026-05-26
phase_1_status: completed
phase_1_completion_date: 2026-05-26
phase_1_archive_location: phases/archive/phase-1-mvp-basic-flow/
phase_1_retrospective_proposals: accepted_all + applied (P1~P4)
phase_2_status: completed
phase_2_completion_date: 2026-05-27
phase_2_archive_location: phases/archive/phase-2-pwa-design/
phase_2_retrospective_proposals: proposed (P-X1~P-X5, awaiting user review)
phase_2_total_slices_completed: 6  # Slice 1~6 모두 PASS
phase_2_total_waves: 5
phase_2_acceptance_passed: 10/10  # A1~A10
phase_2_changeability_simulation: 5/5 PASS
phase_2_design_review: 7 principles aligned (PASS)
phase_2_audit_naming_final: 0 drift
phase_2_simplicity_check: 5/5 PASS
phase_2_qa_check_v1_2_0: 11 categories applied (5 PASS / 6 skip - spec phase)
phase_2_new_patterns:
  - P-AGENT-SCOPE-001  # sub-agent forbidden 영역 침범 (Wave 3 Slice 3)
  - P-DESIGN-LAYERED-001  # 4-layer 4 + Variants 3 minimal 정책 효과
phase_2_deferred_to_phase_3:
  - Step_2_to_7_wireframe_detail
  - QuickInputCard_variants
  - PlanCard_4layer_reconcile
  - audit_page_component_script
phase_2_deferred_to_phase_4:
  - PlanComparisonCard_detailed
phase_3_status: completed
phase_3_entry_date: 2026-05-28
phase_3_completion_date: 2026-05-28
phase_3_archive_location: phases/archive/phase-3-pwa-impl/
phase_3_total_slices_completed: 6  # Slice 1~6 모두 PASS
phase_3_total_waves: 5
phase_3_acceptance_passed: 10/10  # A1~A10
phase_3_changeability_simulation: 4/5 PASS + 1 WARN  # 시나리오 5 code phase 자연 증가
phase_3_design_review: 7 principles aligned (PASS, impl phase)
phase_3_audit_naming_final: 0 drift
phase_3_audit_page_component_final: 0 drift  # D5 신규 도구
phase_3_smoke_test: 7/7 PASS  # pytest 62/62 + audit×2 + build + tsc + lint + BUILD_ID
phase_3_simplicity_check: 5/5 PASS
phase_3_qa_check_v1_2_0: 11 categories applied (8 PASS / 3 skip - AI/cost/logs Phase 4+)
phase_3_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두 sub-agent §SELF-VERIFICATION PASS
phase_3_component_map_zero_lines_streak: 6  # Slice 1~6 모두 0줄, 조정 4번 강제 성공
phase_3_deviation_count: 0
phase_3_new_patterns:
  - P-X1-EFFECT-001  # P-X1 §SELF-VERIFICATION 5연속 효과 측정
  - P-THIN-VERTICAL-001  # Thin Vertical Slice 효과 (코드 phase entry 표준)
phase_3_mitigated_patterns:
  - P-AGENT-SCOPE-001  # Phase 2 발견 → Phase 3 P-X1 적용 후 0건 재발
phase_3_d5_completed: audit_page_component.ps1  # Slice 6 신규
phase_3_deferred_to_phase_4:
  - D2_QuickInputCard_alt_variants
  - D3_PlanCard_4layer_reconcile  # 조정 3번 — PlanComparisonCard와 함께 재정의
  - D4_PlanComparisonCard_detailed
phase_3_retrospective_proposals: proposed (Y-X1~Y-X3 + Phase 2 P-X2 재평가)
phase_4_status: completed
phase_4_entry_date: 2026-05-28
phase_4_completion_date: 2026-05-28
phase_4_archive_location: phases/archive/phase-4-fastapi-extension/
phase_4_total_slices: 4  # GPT 검토 채택 (6→4)
phase_4_total_waves: 4  # all sequential (사용자 결정 2-a)
phase_4_completed_slices: 4  # Slice 1~4 모두 PASS
phase_4_estimated_hours_total: 7-11  # acceptance.md
phase_4_actual_hours: ~6-8  # 실측 (원안 18-26h 대비 ▼66%)
phase_4_acceptance_passed: 10/10  # A1~A10
phase_4_changeability_simulation: 4/5 PASS + 1 WARN  # Phase 3 결과 유지, Phase 4 +0 영향
phase_4_changeability_aux_scenarios: 3/3 PASS  # 보조 시나리오 6/7/8 (Phase 1 제거 / 3→5 plan / multi-provider)
phase_4_design_review: 7 principles aligned (PASS, impl phase, PlanCard 무수정 정합)
phase_4_audit_naming_final: 0 drift
phase_4_audit_page_component_final: 0 drift  # D-1 Slice 4 해소
phase_4_smoke_test: 8/8 PASS  # smoke_test_phase_4.ps1 신규
phase_4_simplicity_check: 5/5 PASS
phase_4_qa_check_v1_2_0: 11 categories applied (9 PASS / 2 skip - 관측성 Phase 5+ / RAG 본격 Phase 7+)
phase_4_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_4_p_x1_cumulative_streak: 9  # Phase 3 5 + Phase 4 4 ★
phase_4_component_map_zero_lines_streak: 15  # Phase 2 6 + Phase 3 5 + Phase 4 4 ★
phase_4_plan_card_zero_lines_streak: 4  # Phase 4 전체 (사용자 결정 6-a) ★
phase_4_deviation_count: 1  # D-1 audit drift (intended → Slice 4 해소)
phase_4_user_decisions_applied:
  decision_1: a  # 4 Slices
  decision_2: a  # Sequential
  decision_3: c  # 다음 phase Slice 4 결정 (옵션 A/B/C 명시)
  decision_4: b + multi-model  # 3 parallel + 모델 추가 가능 구조
  decision_5: a  # Phase 1 endpoint Phase 8+ 제거
  decision_6: a  # PlanCard 무수정 (4연속 0줄 PASS)
  decision_7: a  # 그대로 진입
  decision_8: deferred 명시 (D6/D7/D8/D3/D4/D2/Phase 1 endpoint 제거)
phase_4_new_patterns:
  - P-GPT-REVIEW-001  # 외부 LLM 검토 채택 효과 (6→4 Slices, ▼66% 시간)
  - P-X1-EFFECT-001 (update 9연속)  # P-X1 9연속 PASS — Phase 3 + Phase 4 누적
phase_4_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 9연속 누적 입증 (Phase 3 5 + Phase 4 4)
phase_4_d1_completed: audit_page_component_phase4_dynamic_route_normalize  # Slice 4 D-1 해소
phase_4_deferred_to_next:
  - D6_Critic_revise_loop_+_Rewriter  # Phase 4.5+ 또는 Phase 6
  - D7_SSE_Progress_streaming  # Phase 5+
  - D8_PlanComparisonCard_4layer  # Phase 5+
  - D3_PlanCard_4layer_redefinition  # Phase 5+ (D4와 함께, 조정 3번)
  - D4_PlanComparisonCard_detail  # Phase 5+
  - D2_QuickInputCard_alt_variants  # Phase 9
  - Phase_1_endpoint_removal  # Phase 8+
phase_4_retrospective_proposals: proposed (Z-X1~Z-X3 + Phase 2 P-X2 재평가, awaiting user review)
phase_4_5_status: completed
phase_4_5_entry_date: 2026-05-28
phase_4_5_completion_date: 2026-05-28
phase_4_5_archive_location: phases/archive/phase-4.5-critic-revise-loop/
phase_4_5_total_slices: 4  # 모두 sub-agent
phase_4_5_completed_slices: 4  # Slice 1~4 모두 PASS
phase_4_5_estimated_hours_total: 12-16
phase_4_5_actual_hours: ~12-14  # Z-X3/P-X2 추가에도 ▼20% 절감
phase_4_5_assumptions_check: PASS  # 4-check 통과 (entry)
phase_4_5_acceptance_passed: 10/10  # A1~A10
phase_4_5_meta_acceptance_passed: 3/3  # M1~M3
phase_4_5_pytest_result: 109/109  # Phase 4 baseline 93 + Phase 4.5 신규 16
phase_4_5_smoke_test: 9/9 PASS  # smoke_test_phase_4_5.ps1 신규
phase_4_5_scenario_simulation: 5/5 PASS (auto-gate)  # P-X2 첫 자동 게이트 트리거 ★
phase_4_5_audit_naming_final: 0 drift  # Slice 1 + Slice 4
phase_4_5_audit_page_component_final: 0 drift  # Slice 1 + Slice 4
phase_4_5_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_4_5_p_x1_cumulative_streak: 13  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 ★
phase_4_5_component_map_zero_lines_streak: 19  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 ★
phase_4_5_plan_card_zero_lines_streak: 9  # Phase 4 4 + Phase 4.5 5 ★
phase_4_5_deviation_count: 0
phase_4_5_user_decisions_applied:
  z_x3_include: yes  # Best-Plan Selection 본 scope 포함
  p_x2_adopt: yes  # phase-complete v1.2.0 §1.6 자동 게이트
  multi_llm_validation_formal: yes  # Claude Code 자가 검증, 외부 placeholder 분리
  all_slices_sub_agent: yes  # 4개 모두 sub-agent dispatch
phase_4_5_new_patterns:
  - P-X2-EFFECT-001  # 변경성 시뮬 자동 게이트 첫 트리거 (▼99% 시간)
  - P-VALIDATION-FORMAL-001  # multi-llm-validation formal self + 외부 분리 패턴
  - P-X1-EFFECT-001 (update 13연속)  # P-X1 13연속 PASS 누적 입증
phase_4_5_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 13연속 누적 입증 (Phase 3 5 + Phase 4 4 + Phase 4.5 4)
phase_4_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안에 직접 기록 (mini-phase)
phase_6_status: completed
phase_6_entry_date: 2026-05-29
phase_6_completion_date: 2026-05-29
phase_6_archive_location: phases/archive/phase-6-output-schema-stabilization/
phase_6_total_slices: 4  # 모두 sub-agent
phase_6_completed_slices: 4  # Slice 1~4 모두 PASS
phase_6_estimated_hours_total: 8-10
phase_6_actual_hours: ~8  # GPT 정신 계승 ▼20% (8~12h → ~8h)
phase_6_assumptions_check: PASS  # 4-check 통과 (entry)
phase_6_acceptance_passed: 10/10  # A1~A10
phase_6_meta_acceptance_passed: 3/3  # M1~M3
phase_6_pytest_result: 144/144  # Phase 4.5 baseline 109 + Phase 6 신규 35
phase_6_smoke_test: 10/10 PASS  # smoke_test_phase_6.ps1 신규
phase_6_scenario_simulation: 5/5 PASS (auto-gate, 두 번째)  # P-X2 두 번째 자동 게이트
phase_6_schema_stress_test: 5/5 PASS (P-X2 v2 신규)  # schema_stress_test.ps1 신규
phase_6_audit_naming_final: 0 drift  # Slice 1 + Slice 4
phase_6_audit_page_component_final: 0 drift  # Slice 1 + Slice 4
phase_6_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_6_p_x1_cumulative_streak: 17  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 ★
phase_6_component_map_zero_lines_streak: 22  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 ★
phase_6_plan_card_zero_lines_streak: 12  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 ★
phase_6_deviation_count: 0
phase_6_user_decisions_applied:
  next_phase_choice: phase_6_first_then_phase_5  # GPT 검토안 채택 (옵션 B 변형 — Phase 6 선행 → Phase 5)
  slice_compression: 6_to_4  # P-GPT-REVIEW-001 정신
  all_slices_sub_agent: yes
  multi_llm_validation_formal: yes  # 두 번째 트리거
  prompt_registry_defer_phase_7_plus: yes  # NG8
  critic_fallback_keep_with_deprecation: yes  # NG12
phase_6_skills_first_trigger:
  - agent_io_check  # 첫 정식 트리거 (Slice 4)
  - contract_change_formal  # 첫 본격 실 변경 (Slice 2 — output_schema + agent_io_contract + api_contract 3 contract + ADR-018/019)
  - multi_llm_validation_formal_second  # 두 번째 트리거 (Slice 1 V1~V5)
  - phase_complete_v1_2_0_second  # P-X2 자동 게이트 두 번째 트리거 (Slice 4)
phase_6_contracts_changed:
  - output_schema.md  # §9 CriticEvaluation canonical + §10 Body.revise_history Optional
  - agent_io_contract.md  # §6 Rewriter v1.0.0 → v1.1.0
  - api_contract.md  # §8.3 응답 필드 정식 등록
phase_6_adr_created:
  - ADR-018  # Critic verdict canonical (phase_6_critic_canonical.md)
  - ADR-019  # Rewriter contract v1.1.0 (phase_6_rewriter_contract.md)
phase_6_new_patterns:
  - P-CRITIC-CANONICAL-001  # 다중 fallback → canonical + deprecated 단계적 축소
  - P-CONTRACT-FIRST-001  # DB 진입 전 mini-phase로 contract 안정화 (신규 후보)
  - P-X1-EFFECT-001 (update 17연속)  # P-X1 17연속 PASS 누적 입증
  - P-VALIDATION-FORMAL-001 (update 두 번째)  # 두 번째 트리거로 정식 패턴 확정
phase_6_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 17연속 누적 입증 (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4)
phase_6_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안에 직접 기록 (mini-phase)
phase_6_deferred_to_next:
  - external_validation_fill  # Phase 5 entry 직전 사용자가 외부에서 채움
  - security_review_first_trigger  # Phase 5 entry
  - scenario_simulation_v2  # Phase 5 Slice 1 (DB/Auth 5 시나리오 추가)
  - prompt_registry_p_007_p_008_formal  # Phase 7+ (NG8)
  - critic_fallback_full_removal  # Phase 9+ eval-run 정식화 후
  - revise_effect_eval  # Phase 9+ eval-design (Phase 4.5 D6 effect 계속 deferred)
phase_5_status: completed
phase_5_entry_date: 2026-05-29
phase_5_completion_date: 2026-05-29
phase_5_archive_location: phases/archive/phase-5-db-auth/
phase_5_total_slices: 5  # 모두 sub-agent
phase_5_completed_slices: 5  # Slice 1~5 모두 PASS
phase_5_estimated_hours_total: 15-20
phase_5_actual_hours: ~14-16
phase_5_assumptions_check: PASS  # 4-check 통과 (entry, audit_naming 0 drift)
phase_5_acceptance_passed: 10/10  # A1~A10
phase_5_meta_acceptance_passed: 4/4  # M1~M4
phase_5_pytest_result: 170/170  # Phase 6 144 baseline + Phase 5 신규 26 (test_db 9 + test_auth 9 + test_rls 4 + test_sse 4)
phase_5_smoke_test: 12/12 (11 PASS + 1 WARN intended)  # smoke_test_phase_5.ps1 신규
phase_5_scenario_simulation_v2: 10/10 PASS (auto-gate, 세 번째)  # P-X2 세 번째 자동 게이트
phase_5_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_5_audit_naming_final: 0 drift  # Slice 1 + Slice 5
phase_5_audit_page_component_final: 2 intended drift WARN  # Slice 3 AuthGuard + /login route 신규, phase-complete v1.2.0 §1.6 허용
phase_5_audit_page_component_intended_drift:
  - AuthGuard  # Slice 3 신규 component (wrapper 패턴)
  - /login  # Slice 3 신규 route
phase_5_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두
phase_5_p_x1_cumulative_streak: 22  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 ★
phase_5_component_map_zero_lines_streak: 27  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 ★
phase_5_plan_card_zero_lines_streak: 17  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 ★
phase_5_deviation_count: 0
phase_5_user_decisions_applied:
  next_phase_order: phase_6_first_then_phase_5  # GPT 검토안 채택 + 사용자 명시
  all_slices_sub_agent: yes  # 5개 모두 sub-agent dispatch
  security_review_first_trigger: yes  # ★ 첫 정식 (Slice 1) + 두 번째 final (Slice 5)
  multi_llm_validation_formal: yes  # 세 번째 트리거 (Slice 1, V1~V6 PASS)
  external_validation_placeholder: yes  # Phase 4.5/6 패턴 계승
  supabase_adoption: yes  # ADR-020
  scenario_simulation_v2: yes  # 5 → 10 scenarios (Slice 1, 10/10 Slice 5)
phase_5_skills_first_trigger:
  - security_review_first_and_second  # 첫 정식 (Slice 1) + 두 번째 final (Slice 5)
  - contract_change_second_formal  # 두 번째 본격 실 변경 (Slice 2 db_schema.md 신규)
  - multi_llm_validation_formal_third  # 세 번째 트리거 (Slice 1 V1~V6) — 정식 패턴 확정
  - phase_complete_v1_2_0_third  # P-X2 자동 게이트 세 번째 트리거 (Slice 5)
  - agent_io_check_second  # 두 번째 회귀 검증 (Slice 5)
phase_5_contracts_changed:
  - db_schema.md  # 신규 (DB schema 첫 정식 contract — 4계층 + plans + users + JSONB)
phase_5_adr_created:
  - ADR-020  # Supabase 채택 (phase_5_supabase_adoption.md, Slice 1)
  - ADR-021  # RLS Policy (phase_5_rls_policy.md, Slice 4)
  - ADR-022  # SSE Progress (phase_5_sse_progress.md, Slice 4)
phase_5_new_patterns:
  - P-RLS-001  # RLS 정책 + 인증/익명 분리
  - P-SSE-001  # SSE 4단계 progress + Origin + cookie
  - P-SECURITY-REVIEW-001  # security-review 2-trigger 패턴 (신규 후보)
  - P-X1-EFFECT-001 (update 22연속)  # large + 보안 phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update 세 번째)  # 정식 패턴 확정 (3회 누적)
phase_5_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 22연속 누적 입증
phase_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 (Phase 6+ legacy 통합 외 5개)
phase_5_deferred_to_next:
  - legacy_db_integration  # Phase 6+ (개선 제안 §1)
  - testclient_cookies_migrate  # Phase 6+ (개선 제안 §2)
  - emailstr_dependency  # Phase 6+ (개선 제안 §3)
  - sse_worker_real_integration  # Phase 8+ MOA Lite (개선 제안 §4)
  - per_user_rate_limit_and_audit_log  # Phase 9+ (개선 제안 §5)
  - pgtap_rls_auto_verification  # Phase 9+ (개선 제안 §6)
  - refresh_token_rotation  # Phase 21+ MFA
phase_5_5_status: completed
phase_5_5_entry_date: 2026-05-29
phase_5_5_completion_date: 2026-05-29
phase_5_5_archive_location: phases/archive/phase-5.5-legacy-db-consolidation/
phase_5_5_total_slices: 4
phase_5_5_completed_slices: 4  # Slice 1~4 모두 PASS
phase_5_5_estimated_hours_total: 4-6
phase_5_5_actual_hours: ~4-5  # consolidation mini-phase 압축 효과
phase_5_5_assumptions_check: PASS
phase_5_5_acceptance_passed: 8/8  # A1~A8
phase_5_5_meta_acceptance_passed: 2/2  # M1~M2
phase_5_5_pytest_result: 172/172  # Phase 5 170 baseline + Phase 5.5 신규 2 (legacy deprecation 검증)
phase_5_5_smoke_test: 12/12 (11 PASS + 1 WARN intended)  # Phase 5 smoke 재실행
phase_5_5_scenario_simulation_v2: 10/10 PASS (auto-gate, 네 번째)  # P-X2 네 번째 자동 게이트
phase_5_5_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_5_5_audit_naming_final: 0 drift
phase_5_5_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 유지 (AuthGuard + /login), phase-complete v1.2.0 §1.6 허용
phase_5_5_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 신규 (baseline 유지)
  - /login  # Phase 5 Slice 3 신규 (baseline 유지)
phase_5_5_p_x1_self_verification: 4/4 PASS  # Slice 1~4 모두
phase_5_5_p_x1_cumulative_streak: 26  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 ★
phase_5_5_component_map_zero_lines_streak: 28  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 ★
phase_5_5_plan_card_zero_lines_streak: 18  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 ★
phase_5_5_deviation_count: 0
phase_5_5_legacy_backward_compat: 100  # Phase 1 baseline 보호 + Phase 5 baseline 보호 동시 달성
phase_5_5_user_decisions_applied:
  legacy_db_consolidation: yes  # 결정 1 (옵션 A 채택, ADR-023)
  external_validation_strengthen: yes  # 결정 2 (self-strengthen V-form × 3, V-form 합의 추정 PASS)
  phase_7_rag_lite_keep: yes  # 결정 3 (ADR-024)
  candidate_knowledge_5stage_mvp_all: yes  # 결정 4 (ADR-024 §5단계 MVP, 12~16h)
  brand_memory_phase_9_plus: yes  # 결정 5 (NG2 + ADR-024 cross-ref)
  all_slices_sub_agent: yes  # 4 Slice 모두 sub-agent dispatch
phase_5_5_skills_first_trigger:
  - phase_complete_v1_2_0_fourth  # P-X2 자동 게이트 네 번째 트리거 (Slice 4)
phase_5_5_adrs:
  - ADR-023  # Legacy DB consolidation 옵션 A (phase_5_5_legacy_db_consolidation.md)
  - ADR-024  # Phase 7 RAG scope evolution (phase_7_rag_scope_evolution.md)
phase_5_5_new_patterns:
  - P-LEGACY-CONSOLIDATION-001  # 다중 layer 공존 시 옵션 A (신규 후보)
  - P-X1-EFFECT-001 (update 26연속)  # consolidation mini-phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update self-strengthen V-form sub-pattern)
phase_5_5_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 26연속 누적 입증
phase_5_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~3
phase_5_5_deferred_to_next:
  - legacy_real_integration  # Phase 7+ RAG 통합 후 mini-phase (Phase 7.5? 권장)
  - external_validation_real_external_review  # 사용자 외부 GPT/Gemini (Phase 7+ 진입 전 권장)
  - adr_024_expansion_a_to_f_early_activation  # Phase 11+ 분기별 검토
  - brand_memory_auto_extract_adr  # Phase 9+ MVP 본격 운영 후
phase_7_status: completed
phase_7_entry_date: 2026-05-29
phase_7_completion_date: 2026-05-29
phase_7_archive_location: phases/archive/phase-7-rag-lite/
phase_7_total_slices: 5
phase_7_completed_slices: 5  # Slice 1~5 모두 PASS
phase_7_estimated_hours_total: 12-16  # ADR-024 추정
phase_7_actual_hours: ~13-14  # large phase 단일일 다중 sub-agent
phase_7_assumptions_check: PASS  # 4-check 통과 (C1~C11, U1~U6, audit_naming 0 drift)
phase_7_acceptance_passed: 10/10  # A1~A10
phase_7_meta_acceptance_passed: 4/4  # M1~M4
phase_7_pytest_result: 223/223  # Phase 5.5 172 baseline + Phase 7 신규 51 (promotion 10 + quality_filter 8 + eval_rubric 5 + chunking 7 + embedding 5 + retrieval 7 + integration 9)
phase_7_smoke_test: 13/13 (12 PASS + 1 WARN intended)  # smoke_test_phase_7.ps1 신규
phase_7_scenario_simulation_v3: 15/15 PASS (auto-gate, 다섯 번째)  # P-X2 다섯 번째 자동 게이트
phase_7_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_7_audit_naming_final: 0 drift  # Slice 5
phase_7_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 계승 (AuthGuard + /login)
phase_7_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 신규 (baseline 계승)
  - /login  # Phase 5 Slice 3 신규 (baseline 계승)
phase_7_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두
phase_7_p_x1_cumulative_streak: 31  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 ★
phase_7_component_map_zero_lines_streak: 29  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 ★
phase_7_plan_card_zero_lines_streak: 19  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 ★
phase_7_deviation_count: 0
phase_7_user_decisions_applied:
  rag_lite_scope_keep: yes  # 사용자 결정 3 (Phase 5.5 명시 — ADR-024 §확대 지점 별도 phase)
  candidate_knowledge_5stage_mvp_all: yes  # 사용자 결정 4 (Phase 5.5 명시 — ADR-024 §5단계 MVP)
  brand_memory_phase_9_plus_keep: yes  # 사용자 결정 5 (NG1 + ADR-024 §Brand Memory cross-reference)
  all_slices_sub_agent: yes  # 5 Slice 모두 sub-agent dispatch
  rag_design_first_trigger: yes  # Slice 1 ★ 첫 정식
  rag_update_first_trigger: yes  # Slice 4 ★ 첫 정식 완료
  multi_llm_validation_formal_4th: yes  # Slice 1 V1~V7 PASS
phase_7_skills_first_trigger:
  - rag_design_first_formal  # ★ 첫 정식 (Slice 1, ADR-025 결과)
  - rag_update_first_formal  # ★ 첫 정식 (Slice 4, initial promotion procedure)
  - contract_change_third_formal  # 세 번째 본격 (Slice 2 rag_data_contract.md §18)
  - multi_llm_validation_formal_fourth  # 네 번째 트리거 (Slice 1 V1~V7)
  - phase_complete_v1_2_0_fifth  # P-X2 자동 게이트 다섯 번째 트리거 (Slice 5)
  - agent_io_check_third  # 세 번째 회귀 검증 (Slice 5)
phase_7_contracts_changed:
  - rag_data_contract.md  # §18 신규 (5단계 stage enum + promotion_history + retrieval 정책)
phase_7_adrs:
  - ADR-025  # Phase 7 RAG architecture (phase_7_rag_architecture.md, rag-design Skill 첫 정식)
  - ADR-026  # Phase 7 5단계 promotion logic (phase_7_promotion_logic.md)
phase_7_new_patterns:
  - P-RAG-5STAGE-001  # 5단계 transition + hybrid 승인 + promotion_history (신규 후보)
  - P-RAG-GRACEFUL-001  # 5종 marker + RAG > LLM Wiki 우선순위 (신규 후보)
  - P-X1-EFFECT-001 (update 31연속)  # large RAG phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update 네 번째)  # 네 번째 입증 — RAG architecture V7
  - P-LEGACY-CONSOLIDATION-001 (update 누적 2회)  # Phase 1 legacy rag ↔ Phase 7 신규 공존 — 정식 채택 임박
phase_7_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 31연속 누적 입증
phase_7_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~6
phase_7_deferred_to_next:
  - chunking_tiktoken  # Phase 9+ (개선 제안 §1)
  - supabase_sql_function_match_approved_knowledge  # 운영 단계 필수 (개선 제안 §2)
  - phase_1_legacy_rag_real_consolidation  # Phase 11+ Custom RAG (개선 제안 §3)
  - rag_update_skill_second_trigger  # Phase 11+ 사용자 데이터 자동 promotion (개선 제안 §4)
  - brand_memory_auto_extract_adr  # Phase 9+ MVP 본격 운영 후 (개선 제안 §5)
  - rag_eval_rubric_formal_via_golden_set  # Phase 9+ eval-run Skill 정식화 (개선 제안 §6)
phase_8_status: completed
phase_8_entry_date: 2026-05-29
phase_8_completion_date: 2026-05-29
phase_8_archive_location: phases/archive/phase-8-moa-lite/
phase_8_total_slices: 5
phase_8_completed_slices: 5  # Slice 1~5 모두 PASS
phase_8_estimated_hours_total: 12-16
phase_8_actual_hours: ~12-14  # large orchestration phase 단일일 다중 sub-agent
phase_8_assumptions_check: PASS  # 4-check 통과 (C1~C11, U1~U6, audit_naming 0 drift)
phase_8_acceptance_passed: 10/10  # A1~A10
phase_8_meta_acceptance_passed: 5/5  # M1~M5
phase_8_pytest_result: 249/249  # Phase 7 223 baseline + Phase 8 신규 26 (test_moa_orchestrator + test_sse_integration + test_prompt_registry_consistency)
phase_8_smoke_test: 14/14 (13 PASS + 1 WARN intended)  # smoke_test_phase_8.ps1 신규
phase_8_scenario_simulation_v4: 20/20 PASS (auto-gate, 여섯 번째)  # P-X2 여섯 번째 자동 게이트, S16~S20 MOA 5 추가
phase_8_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_8_audit_naming_final: 0 drift  # Slice 5
phase_8_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 계승 (AuthGuard + /login)
phase_8_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 신규 (baseline 계승)
  - /login  # Phase 5 Slice 3 신규 (baseline 계승)
phase_8_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두
phase_8_p_x1_cumulative_streak: 36  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 ★
phase_8_component_map_zero_lines_streak: 34  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 ★
phase_8_plan_card_zero_lines_streak: 24  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 ★
phase_8_deviation_count: 0
phase_8_plans_py_loc: 659->243  # god-function 분해 (thin adapter)
phase_8_user_decisions_applied:
  scope_all_3_pillars: yes  # A orchestrator + B SSE + C prompt_registry (5 Slice)
  critic_conservative_adapter: yes  # Phase 6 canonical 불변 (ADR-018 보존) + P-007 v1.1.0
  sse_progress_store_bridge: yes  # background task 미도입 (moa_policy §4 sync)
  all_slices_sub_agent: yes  # 5 Slice 모두 sub-agent dispatch
  ai_architecture_review_first_trigger: yes  # Slice 1 ★ 첫 정식 + Slice 5 회고
  prompt_version_review_first_trigger: yes  # Slice 1 분석 + Slice 4 적용 ★ 첫 정식
phase_8_skills_first_trigger:
  - ai_architecture_review_first_formal  # ★ 첫 정식 (Slice 1 ADR-027 + Slice 5 회고)
  - prompt_version_review_first_formal  # ★ 첫 정식 (Slice 1 분석 + Slice 4 적용, ADR-029)
  - contract_change_fourth_formal  # 네 번째 본격 (Slice 4 CC-003 — prompt_registry semver + agent_io_contract v1.2.0)
  - multi_llm_validation_formal_fifth  # 다섯 번째 트리거 (Slice 1 V1~V7)
  - phase_complete_v1_2_0_sixth  # P-X2 자동 게이트 여섯 번째 트리거 (Slice 5)
  - agent_io_check_fourth  # 네 번째 회귀 검증 (Slice 5)
phase_8_contracts_changed:
  - prompt_registry.md  # P-001~P-008 + AUX semver 정식화 + P-007 §0–5↔0–1 adapter
  - agent_io_contract.md  # v1.2.0 §5 Critic v1.1.0 adapter + §8 orchestrator 중개
phase_8_contract_changes:
  - CC-003  # prompt_registry semver + agent_io_contract v1.2.0 (Slice 4)
phase_8_adrs: [ADR-027, ADR-028, ADR-029]  # MOA orchestrator + SSE progress integration + prompt_registry semver
phase_8_new_patterns:
  - P-MOA-ORCHESTRATOR-001  # god-function → service layer 추출 (behavior-preserving) 신규 후보
  - P-BEHAVIOR-PRESERVING-001  # 기존 test 수정 0 = 동작 불변 증거 신규 후보
  - P-X1-EFFECT-001 (update 36연속)  # orchestration-refactor phase 확장 입증
  - P-VALIDATION-FORMAL-001 (update 다섯 번째)  # 다섯 번째 입증 — V7 MOA orchestration
phase_8_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 36연속 누적 입증 (agents/* 재구조화 위험 영역, orchestration/ 격리로 0건)
phase_8_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~6
phase_8_deferred_to_next:
  - normalize_to_canonical_wiring  # Phase 9+ (개선 제안 §1 — 결과 저장 시점)
  - sse_full_async_worker  # Phase 11+ (개선 제안 §2, 누적 2회 Phase 5 + Phase 8)
  - prompt_ab_execution_infra  # Phase 11+ (개선 제안 §3 — multi-provider 대비)
  - critic_deprecated_0_5_fallback_full_removal  # Phase 9+ eval-run (개선 제안 §4, 누적 2회 Phase 6 + Phase 8)
  - brand_memory_auto_extract_adr  # Phase 9+ MVP 본격 운영 후 (개선 제안 §5, 누적 3회)
  - revise_effect_eval  # Phase 9+ eval-run (개선 제안 §6, Phase 4.5 D6 누적 6회)
phase_9_status: completed
phase_9_entry_date: 2026-05-29
phase_9_completion_date: 2026-05-31
phase_9_archive_location: phases/archive/phase-9-result-feedback/
phase_9_total_slices: 6
phase_9_completed_slices: 6  # Slice 1~6 모두 PASS
phase_9_estimated_hours_total: 10-14
phase_9_actual_hours: ~10-13  # large feedback phase 다중 sub-agent
phase_9_assumptions_check: PASS
phase_9_acceptance_passed: 10/10  # A1~A10
phase_9_meta_acceptance_passed: 4/4  # M1~M4
phase_9_pytest_result: 293/293  # Phase 8 249 baseline + Phase 9 신규 44 (selection_feedback + plans_feedback_api + critic_canonical_wiring + brand_memory_prep), 기존 수정 0
phase_9_smoke_test: 15/15 (14 PASS + 1 WARN intended)  # smoke_test_phase_9.ps1 신규
phase_9_scenario_simulation_v5: 25/25 PASS (auto-gate, 일곱 번째)  # P-X2 일곱 번째 자동 게이트, S21~S25 feedback/selection 5 추가
phase_9_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)
phase_9_audit_naming_final: 0 drift  # Slice 6
phase_9_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 계승 (AuthGuard + /login), 피드백 UI page.tsx inline 신규 route/component 미생성 → +0
phase_9_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 신규 (baseline 계승)
  - /login  # Phase 5 Slice 3 신규 (baseline 계승)
phase_9_deprecated_critic_warnings: 67->16  # normalize wiring canonical 우선 경로 정착
phase_9_p_x1_self_verification: 6/6 PASS  # Slice 1~6 모두
phase_9_p_x1_cumulative_streak: 42  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6 ★
phase_9_component_map_zero_lines_streak: 40  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 ★
phase_9_plan_card_zero_lines_streak: 30  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 (frontend slice 있어도 wrapper) ★
phase_9_deviation_count: 0
phase_9_user_decisions_applied:
  brand_memory_prep_only: yes        # P-AUX-2 agent 미구현, Phase 10+ (ADR-031, NG1)
  feedback_ui_wrapper: yes           # PlanCard·component_map 무수정 (page.tsx inline)
  normalize_canonical_wiring: yes    # critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0 (ADR-032)
  all_slices_sub_agent: yes          # 6 Slice 모두 sub-agent dispatch
phase_9_skills_first_trigger:
  - security_review_second_formal  # 두 번째 정식 (Slice 1 — 피드백 reason PII T1~T6, P-SECURITY-REVIEW-001 강화)
  - contract_change_fifth_formal  # 다섯 번째 본격 (Slice 2 CC-004 — db_schema.md selected_plans/feedback_events 실 plans 정합)
  - multi_llm_validation_formal_sixth  # 여섯 번째 트리거 (Slice 1 V1~V7)
  - phase_complete_v1_2_0_seventh  # P-X2 자동 게이트 일곱 번째 트리거 (Slice 6)
  - agent_io_check_fifth  # 다섯 번째 회귀 검증 (Slice 3 normalize wiring + Slice 6)
phase_9_contracts_changed:
  - db_schema.md  # §4.3 selected_plans (실 plans 정합 plan_id + selected_option_index 0–2 + selection_reason) + §5.2 feedback_events 보강 + brand_memory prep cross-ref
phase_9_contract_changes:
  - CC-004  # db_schema.md feedback/selection 실 plans 정합 (Slice 2)
phase_9_adrs: [ADR-030, ADR-031, ADR-032]  # feedback/selection persistence + Brand Memory prep + normalize_to_canonical wiring
phase_9_new_patterns:
  - P-FEEDBACK-LOOP-001  # 피드백 영속 graceful + PII 마스킹 (신규 후보)
  - P-CANONICAL-WIRING-001  # Phase N helper → live pipeline wiring (additive 회귀 0) 신규 후보
  - P-X1-EFFECT-001 (update 42연속)  # feedback-frontend phase 확장 입증 (frontend slice에서도 wrapper로 0줄)
  - P-VALIDATION-FORMAL-001 (update 여섯 번째)  # 여섯 번째 입증 — V7 selection/feedback + normalize wiring + Brand Memory 준비
phase_9_mitigated_patterns:
  - P-AGENT-SCOPE-001  # 42연속 누적 입증 (db migration + repo + router + orchestrator + frontend 전 영역, 0건 재발)
phase_9_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~5
phase_9_deferred_to_next:
  - p_aux_2_brand_memory_extractor_agent  # Phase 10+ (개선 제안 §1 — schema + 적재 경로 준비 완료, agent 실 구현)
  - critic_deprecated_0_5_fallback_full_removal  # Phase 9.5 eval-run (개선 제안 §2, Phase 6 + Phase 8 + Phase 9 누적 3회)
  - four_layer_full_linkage_plan_options  # Phase 11+ (개선 제안 §3, 누적 2회 Phase 5 + Phase 9 — selected_plans 실 plans 정합 → idealized schema 연결)
  - eval_run_formalization  # Phase 9.5 (개선 제안 §4 — Critic canonical live 활성으로 baseline 준비 완료)
  - user_data_auto_promotion  # Phase 10+/11+ (개선 제안 §5 — feedback→candidate pending 적재 완료, rag-update 두 번째)
phase_9_5_status: completed
phase_9_5_entry_date: 2026-05-31
phase_9_5_completion_date: 2026-05-31
phase_9_5_archive_location: phases/archive/phase-9.5-eval-run/
phase_9_5_total_slices: 5
phase_9_5_completed_slices: 5  # Slice 1~5 모두 PASS
phase_9_5_estimated_hours_total: 6-10
phase_9_5_actual_hours: ~7-10  # eval mini-phase 다중 sub-agent (Slice 5 세션 재개)
phase_9_5_assumptions_check: PASS  # 4-check 통과 (C1~C10, U1~U5, audit_naming 0 drift)
phase_9_5_acceptance_passed: 10/10  # A1~A10
phase_9_5_meta_acceptance_passed: 4/4  # M1~M4
phase_9_5_pytest_result: 339/339  # Phase 9 293 baseline + Phase 9.5 신규 46 (test_eval_runner + test_revise_effect 45 + test_critic 의도 delta), 회귀 0
phase_9_5_smoke_test: 16/16 (15 PASS + 1 WARN intended)  # smoke_test_phase_9_5.ps1 신규 (Phase 9 15 + eval-run 1)
phase_9_5_scenario_simulation_v6: 30/30 PASS (auto-gate, 여덟 번째)  # P-X2 여덟 번째 자동 게이트, S26~S30 eval/deprecated 5 추가
phase_9_5_eval_gate: PASS  # eval_run.ps1 — schema_rate 1.0 / pass_rate 1.0 / revise mean_delta 0.092 / improved 0.6 / regressed 0.2
phase_9_5_schema_stress_test: 5/5 PASS (Phase 6 v2 유지)  # CriticEvaluation deprecated 0–5 제거 정합
phase_9_5_audit_naming_final: 0 drift  # Slice 5
phase_9_5_audit_page_component_final: 2 intended drift WARN  # Phase 5 baseline 계승 (AuthGuard + /login), frontend canonical 전환 page.tsx inline 신규 route/component 미생성 → +0
phase_9_5_audit_page_component_intended_drift:
  - AuthGuard  # Phase 5 Slice 3 baseline 계승
  - /login route  # Phase 5 Slice 3 baseline 계승
phase_9_5_deprecated_critic_warnings: 16->0  # deprecated 0–5 fallback + CriticEvaluation Optional 필드 Full 제거
phase_9_5_p_x1_self_verification: 5/5 PASS  # Slice 1~5 모두
phase_9_5_p_x1_cumulative_streak: 47  # Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4 + Phase 7 5 + Phase 8 5 + Phase 9 6 + Phase 9.5 5 ★
phase_9_5_component_map_zero_lines_streak: 45  # Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 + Phase 9.5 5 ★
phase_9_5_plan_card_zero_lines_streak: 35  # Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1 + Phase 7 1 + Phase 8 5 + Phase 9 6 + Phase 9.5 5 (frontend canonical 전환에서도 wrapper) ★
phase_9_5_deviation_count: 0  # generate.py canonical wiring 보강은 deprecated 제거 정합 (수용, 회귀 방지)
phase_9_5_user_decisions_applied:
  critic_deprecated_full_removal: yes   # fallback + schema, run_critic 0–5 불변 (P-007 NG3), eval 검증 후 제거
  eval_mock_deterministic_primary: yes  # 실 LLM mode 문서 (CI 가능, 비용 0)
  rag_eval_rubric_phase_10_plus: yes    # NG1
  all_slices_sub_agent: yes             # 5 Slice 모두 sub-agent dispatch
phase_9_5_adrs: [ADR-033, ADR-034]  # eval-run harness (mock-deterministic) + Critic deprecated 0–5 Full 제거
phase_9_5_contracts_changed: [output_schema.md, agent_io_contract.md, db_schema.md]  # CC-005 — deprecated 0–5 제거 정합
phase_9_5_contract_changes:
  - CC-005  # output_schema §9 canonical-only + agent_io_contract §5 Critic canonical-only (run_critic 0–5 불변) + db_schema critic_evaluation deprecated 제거
phase_9_5_skills_first_trigger:
  - eval_design_first_formal  # ★ 첫 정식 (Slice 1, ADR-033 §eval-design)
  - eval_run_first_formal  # ★ 첫 정식 (Slice 2~3, mock-deterministic golden_set 회귀 + revise effect)
  - multi_llm_validation_formal_seventh  # 일곱 번째 트리거 (Slice 1 V1~V7)
phase_9_5_new_patterns:
  - P-EVAL-HARNESS-001  # golden_set mock-deterministic 회귀 + 임계값 게이트
  - P-DEPRECATED-REMOVAL-001  # eval 안전망으로 deprecated 제거 (제거 전/후 eval 동일 입증)
phase_9_5_updated_patterns:
  - P-X1-EFFECT-001  # 47연속
  - P-VALIDATION-FORMAL-001  # 일곱 번째 입증
phase_9_5_golden_set_case_count: 11  # GS-001~GS-011 (entry plan "47" 정정 — 케이스 확대 NG10 Phase 10+)
phase_9_5_revise_effect: mean_delta 0.092 / improved 0.6 / regressed 0.2  # Phase 4.5 D6 해소 (mock-based)
phase_9_5_generate_py_deviation: canonical_wiring_보강  # ★ Phase 1 endpoint normalize 누락 발견·보강, 향후 신규 critic consumer normalize_to_canonical 경유 필수
phase_9_5_eval_design_eval_run_first_formal: yes  # eval-design + eval-run 둘 다 첫 정식 트리거
phase_9_5_retrospective_proposals: in_retrospective  # 본 회고 §개선 제안 §1~3 (실 LLM eval mode / RAG eval_rubric / golden_set 확대 — 모두 Phase 10+)
phase_9_5_deferred_to_next:
  - real_llm_eval_mode  # Phase 10+ (실 LLM 8차원 eval 운영 활성)
  - rag_eval_rubric_golden_set  # Phase 10+ (NG1)
  - golden_set_expansion  # Phase 10+ (NG10, 11 → 47+)

phase_m0_status: in_progress
phase_m0_type: meta-phase   # 제품 phase 아님 (L3 Meta-Harness Factory skeleton)
phase_m0_entry_date: 2026-05-31
phase_m0_total_slices: 3
phase_m0_runtime_change: 0   # A9 — FastAPI/Next/Supabase 0줄
phase_m0_user_decisions_applied: {meta_phase: yes, harness_factory_skill: yes, proposal_first: yes}
phase_m0_adrs: [ADR-035]
phase_m0_slice_1_done:
  - validations_self_v1_v6_pass  # multi-llm-validation formal 여덟 번째 (첫 meta-phase)
  - validations_external_placeholder
  - adr_035_l3_meta_factory  # L1/L2/L3 모델 + proposal-first + payoff deferred + skeleton-only
  - meta_factory_readme  # L1/L2/L3 + proposal-first 명시
  - meta_factory_factory_contract  # 8 절대 규칙
  - meta_factory_domain_brief_schema
  - meta_factory_harness_blueprint_schema
  - meta_factory_architecture_patterns  # 6 패턴 + Dreammate 매핑 (Supervisor/Fan-out/Producer-Reviewer/Pipeline)
phase_m0_baseline_unchanged: "pytest 339 + P-X1 47 + PlanCard 35 + component_map 45 + Skill 20"  # 런타임 무관, 불변
phase_m0_p_x1_cumulative_streak_target: 50  # Phase 9.5:47 + M0:3
phase_m0_skills_first_trigger:
  - multi_llm_validation_formal_eighth  # 여덟 번째 (Slice 1 V1~V6) — ★ 첫 meta-phase 적용
phase_m0_next_slice: slice_2_workflow_blueprint_templates

total_commits: 90  # 89 (Phase 9.5 종료) + Phase M0 Slice 1 entry = 90
last_updated: 2026-05-31
```

## 확정 방향

### 제품 / UX
- 영상 제작 AI가 아닌 **영상기획 AI 에이전트**
- 4계층 데이터 모델: User → Brand → Domain → Series → Video Project
- Hybrid UX: **Discovery Wizard** (신규/콜드스타트, 5단계 카드) + **Quick Mode** (같은 Series 추가)
- Discovery 단계당 카드 5장 (4장 추천 + 1장 "직접 입력")
- 한 호출당 plan 후보 **3개** 생성 → 사용자가 1개 선택
- Intent Filter (영상기획 외 입력 차단)

### 기술 스택
- **MVP**: Next.js 14 PWA + FastAPI + Supabase(PostgreSQL + pgvector)
- **LLM**: gpt-4o-mini 기본, gpt-4o 일부 (Critic 등)
- **Phase 21+**: Expo React Native, Spring Boot, Custom RAG
- 영상 자동 편집 / TTS / BGM / 자동 업로드 → MVP 제외 (영구)

### AI 시스템
- **MOA Lite**: Intent → Planner → Critic → Rewriter
- **Critic revise 최대 2회** (무한 루프 차단)
- **RAG Lite**: candidate_knowledge 5단계 승격 (pending → filtered → evaluated → approved → promoted)
- **prompt-version-review**: semver + golden_set 회귀 + A/B (major 시 10%→50%→100%)
- PII 마스킹 + 프롬프트 인젝션 차단 (Step 1, Step 2 자동 검사)

### 운영
- Brand Memory 자동 추출 + 사용자 검토 가능
- 광고적 표현 차단 단어 검사 ("최고의", "혁신적인" 등)
- 30–60초 생성 대기 시 4단계 progress stepper + 부분 결과 즉시 노출

## confirmed_decisions (25)

```
[ 1] Discovery + Quick 하이브리드 UX (1.6x 비용 수용)
[ 2] Mode 자동 분기: 신규/Brand 없음 → Discovery, 기존 Series → Quick
[ 3] Discovery 단계당 카드 5장 (4추천 + 1직접입력)
[ 4] 3개 plan 후보 생성 (P-006 plan_candidates)
[ 5] Critic revise 최대 2회 (무한 루프 차단)
[ 6] 4계층 데이터 모델 (Brand/Domain/Series/VideoProject)
[ 7] Intent Filter (영상기획 외 입력 차단)
[ 8] Brand Memory 자동 추출 + 사용자 검토 가능
[ 9] 광고적 표현 차단 단어 검사
[10] 30–60초 생성 대기 시 4단계 progress + 부분 결과 노출
[11] Skill 14 → 20 (이번 세션, GPT 흡수 후)
[12] Skill 폴더: .claude/skills/ 단일 + applies_to 태그
     (v1.2.0 변경: .agents/.claude 분리 → 단일.
      이유: Claude Code Skill 자동 트리거는 .claude/skills/만 인식)
[13] 22 Phase 등록 (1~10 MVP, 11~20 안정화, 21~30 확장)
[14] Phase 0 = 마이그레이션 자체 (지금 active)
[15] context-compact가 모든 Skill 위 최우선
[16] multi-llm-validation 워크플로 (Claude/GPT/Gemini 교대)
[17] agent.html은 토큰 최적화 압축 레이어 (안정화 후 빌드)
[18] RAG candidate_knowledge 5단계 승격 파이프라인
[19] PII 마스킹 + 프롬프트 인젝션 차단 (자동 검사 2단계)
[20] prompt 변경 semver + 회귀 + A/B (major 시 10%→50%→100%)
[21] agent_html_spec v1.1.0 갱신 — v1.2.0 단일 폴더 결정으로 불필요해짐
[22] placeholder marker 표준 형식 (16개 stub 일관 적용)
[23] Sprint별 git commit + sanity script (시작/종료)
[24] PROJECT_STATE.migration_progress 필드로 부분 완료 감지
[25] Claude Code / Codex / Copilot Code 분담 (multi-llm-validation 활용)
```

## 주요 리스크

- `output_schema.md` 불명확 → Sprint S3에서 깊은 작성 (300줄+)
- Golden Set 부족 → Sprint S4에서 시드 10케이스 작성
- LLM 보안 contract 9줄 stub → Sprint S3 우선 보강
- 사용자 데이터 승격 정책 미흡 → Phase 7+ (rag-update Skill 절차로 강제)
- 9줄 stub 16개 (docs/contracts/) → Sprint S3에서 8 보강 + 8 placeholder marker

## 다음 액션

```
Phase 7 (RAG Lite) ✅ + Phase 8 (MOA Lite 본격) ✅ done (2026-05-29).
🟢 Phase 9 (결과 저장 + 피드백) active (2026-05-29 entry) — 6 Slice, 10~14h. Slice 1 (Pre-Entry) 진행.

이전 phase 옵션 (참고 — Phase 8/9 진행으로 일부 해소):

A. Phase 8 — MOA Lite 본격 (12~16h)
   - Intent / Planner / Critic / Rewriter 완전 분리
   - agents/* 모두 재구조화 (Phase 1 baseline + Phase 6 canonical + Phase 7 wrapper 공존 → 정리)
   - SSE Progress worker 통합 (Phase 5 Slice 4 mock → 실 worker callback)
   - prompt_registry P-007/P-008 정식화 (NG8 누적 3회 defer 해소)
   - ai-architecture-review Skill ★ 첫 정식 baseline

B. Phase 9 — 결과 저장 + 피드백 (6~10h)
   - 사용자 plan 선택 / 수정 / 반려 누적
   - Phase 5 plans_repo + RLS + Phase 7 RAG 활용
   - Brand Memory 자동 추출 ADR 신규 (Phase 7 개선 제안 §5, 사용자 결정 5 누적 2회 confirm)
   - per-user rate-limit + audit-log (Phase 5 §개선 제안 §5 흡수)

C. Phase 9.5+ — eval-run Skill 정식화 (4~6h)
   - golden_set 회귀 + revise effect eval (Phase 4.5 D6 누적 5회 deferred 해소)
   - Critic deprecated 4 fallback 완전 제거 (Phase 6 ADR-018 다음 단계)
   - 간이 RAG eval_rubric → golden_set 기반 정식 (Phase 7 개선 제안 §6)
   - eval-design + eval-run Skill 첫 정식 트리거 baseline

D. 다른 우선순위 (Phase 11+)
   - 사용자 데이터 자동 promotion (ADR-024 §A, Phase 7 개선 제안 §4 + rag-update Skill 두 번째 트리거)
   - Supabase SQL function `match_approved_knowledge` 정의 (Phase 7 개선 제안 §2 — 운영 단계 필수)
   - Phase 1 legacy rag/{retriever, fallback}.py 실 통합 (Phase 7 개선 제안 §3 — Phase 11+ Custom RAG)
   - cost-review Skill 정식화

확대 지점 (ADR-024 §확대 지점, 다른 phase 확장 경로):
   → Phase 11+ 사용자 데이터 자동 promotion (rag-update Skill 두 번째)
   → Phase 21+ Custom RAG / Graph RAG
   → Phase 11+ Hybrid retrieval (BM25 + vector)
   → Phase 8+ Multi-modal RAG (제한)
   → Phase 9+ Re-ranking model

Phase 7 deferred 처리 계획:
   → Phase 8+: MOA Lite 본격 + SSE worker 통합 + prompt_registry 정식화 + ai-architecture-review 첫 정식
   → Phase 9+: 결과 저장 + 피드백 + Brand Memory 자동 추출 ADR + per-user rate-limit + audit-log
   → Phase 9.5+: eval-run Skill 정식화 + revise effect eval + Critic 4 fallback 완전 제거 + RAG eval_rubric 정식
   → Phase 11+: 사용자 데이터 자동 promotion (rag-update 두 번째) + Phase 1 legacy rag 실 통합 + Custom RAG / Graph RAG / Hybrid retrieval
   → 운영 단계 필수: Supabase SQL function `match_approved_knowledge` 정의 (Phase 8+/9+ 운영 시작 직전)
```
