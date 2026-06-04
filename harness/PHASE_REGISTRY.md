# PHASE_REGISTRY

## 운영 원칙

- 전체 Phase는 큰 지도 역할을 한다.
- 현재 active Phase만 상세히 작성한다.
- planned는 다음 2~3개만 중간 상세화한다.
- archive는 기본 참조하지 않는다.
- **active Phase는 항상 1개만.**

## Phase 목록

| Phase | 이름 | 상태 | 목적 |
|---|---|---|---|
| 0 | 하네스 초기화 (Migration) | **done** (2026-05-26) | GPT 골격 + 우리 콘텐츠 병합, Sprint S0~S5 완료 |
| 1 | MVP 기본 플로우 | **done** (2026-05-26) | 7 Slices + pytest 62/62 + automated smoke 5/5 + CC-001 + 회고 archive 완료 |
| 2 | design.md 기반 PWA 설계 (Discovery + Quick 분기) | **done** (2026-05-27) | 6 Slices + design_handoff 5/5 PASS + design-review 7원칙 + audit_naming 0 + P-AGENT-SCOPE-001 발견 |
| 3 | Next.js PWA 기본 UI 구현 (Discovery + Quick 분기) | **done** (2026-05-28) | 6 Slices + acceptance 10/10 + audit_naming + audit_page_component 0 drift + smoke 7/7 + 변경성 4/5+1 WARN + **P-X1 5/5 PASS + component_map 6연속 0줄** |
| 4 | FastAPI 기본 백엔드 구현 (확장) | **done** (2026-05-28) | 4 Slices (GPT 검토 6→4 채택) + acceptance 10/10 + audit_naming + audit_page_component 0 drift (D-1 해소) + smoke 8/8 + **P-X1 9연속 PASS + component_map 15연속 0줄 + PlanCard 4연속 0줄 + GPT 검토 ▼66% 시간** |
| 4.5 | Critic Revise Loop + Rewriter + Z-X3 + P-X2 | **done** (2026-05-28) | 4 Slices (모두 sub-agent) + A1~A10 + M1~M3 + P-X1 13연속 + PlanCard 9연속 + component_map 19연속 + P-X2 자동 게이트 첫 + multi-llm-validation formal 첫 + pytest 109/109 + smoke 9/9 |
| 6 | Output Schema + Agent IO Stabilization | **done** (2026-05-29) | 4 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 + P-X1 17연속 + PlanCard 12연속 + component_map 22연속 + pytest 144/144 + smoke 10/10 + Critic canonical (ADR-018) + Rewriter v1.1.0 (ADR-019) + agent-io-check 첫 정식 + contract-change 본격 + P-CONTRACT-FIRST-001 신규 |
| 5 | DB / Auth / RLS / SSE | **done** (2026-05-29) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 22연속** + PlanCard 17연속 + component_map 27연속 + pytest 170/170 (+26) + smoke 12/12 + scenario_sim v2 10/10 (P-X2 세 번째) + Supabase + JWT httpOnly + RLS (ADR-021) + SSE 4단계 (ADR-022) + ADR-020 + security-review 첫+두 번째 + contract-change 두 번째 본격 (db_schema.md) + agent-io-check 두 번째 회귀 + P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 신규 후보 + P-VALIDATION-FORMAL-001 정식 확정 |
| 5.5 | Legacy DB Consolidation + Validation 강화 + Phase 7 Prep | **done** (2026-05-29) | 4 Slices (모두 sub-agent) + A1~A8 + M1~M2 + **P-X1 26연속** + PlanCard 18연속 + component_map 28연속 + ADR-023 (Legacy DB 옵션 A) + ADR-024 (Phase 7 RAG scope evolution) + external × 3 self-strengthen V-form + Brand Memory Phase 9+ confirm + pytest 172/172 (+2 deprecation) + smoke 12/12 + scenario_sim v2 10/10 (P-X2 네 번째) + P-LEGACY-CONSOLIDATION-001 신규 후보 + legacy backward-compat 100% |
| 7 | RAG Lite (candidate_knowledge 5단계 MVP 전부) | **done** (2026-05-29) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 31연속** + PlanCard 19연속 + component_map 29연속 + ADR-025 (RAG architecture) + ADR-026 (5단계 promotion logic) + rag-design ★ 첫 정식 + rag-update ★ 첫 정식 + contract-change rag_data_contract §18 + pytest 223/223 (+51 신규) + smoke 13/13 + scenario_sim v3 15/15 (P-X2 다섯 번째) + P-RAG-5STAGE-001 신규 + P-RAG-GRACEFUL-001 신규 + P-LEGACY-CONSOLIDATION-001 누적 2회 (정식 채택 임박) + graceful 5종 marker |
| 8 | MOA Lite 본격 (orchestrator 추출 + SSE worker + prompt_registry 정식화) | **done** (2026-05-29) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M5 5/5 + **P-X1 36연속** + PlanCard 24연속 + component_map 34연속 + ADR-027 (MOA orchestrator behavior-preserving) + ADR-028 (SSE progress integration) + ADR-029 (prompt_registry semver) + ai-architecture-review ★ 첫 정식 + prompt-version-review ★ 첫 정식 + contract-change CC-003 (prompt_registry + agent_io_contract v1.2.0) + pytest 249/249 (+26 신규) + smoke 14/14 + scenario_sim v4 20/20 (P-X2 여섯 번째) + P-MOA-ORCHESTRATOR-001 신규 + P-BEHAVIOR-PRESERVING-001 신규 + plans.py 659→243 god-function 분해 + Critic v1.1.0 conservative adapter |
| 9 | 결과 저장 + 피드백 (selected_plans + feedback_events 영속화 + normalize wiring + Brand Memory 준비 + 피드백 UI) | **done** (2026-05-31) | 6 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 42연속** + PlanCard 30연속 + component_map 40연속 + ADR-030 (feedback/selection persistence) + ADR-031 (Brand Memory prep — P-AUX-2 설계 agent 미구현 Phase 10+) + ADR-032 (normalize_to_canonical wiring) + security-review 두 번째 정식 (피드백 PII) + contract-change CC-004 (db_schema.md 실 plans 정합) + pytest 249→293/293 (+44 신규, 기존 수정 0) + smoke 15/15 + scenario_sim v5 25/25 (P-X2 일곱 번째) + P-FEEDBACK-LOOP-001 신규 + P-CANONICAL-WIRING-001 신규 + 피드백 UI inline (PlanCard·component_map 0줄) + deprecated warnings 67→16 |
| 9.5 | eval-run 정식화 + Critic deprecated 0–5 Full 제거 | **done** (2026-05-31) | 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + **P-X1 47연속** + PlanCard 35연속 + component_map 45연속 + ADR-033 (eval-run harness mock-deterministic) + ADR-034 (Critic deprecated 0–5 Full 제거) + eval-design ★ 첫 정식 + eval-run ★ 첫 정식 + contract-change CC-005 (output_schema §9 + agent_io_contract §5 canonical-only + db_schema) + pytest 293→339/339 (+46) + smoke 16/16 + scenario_sim v6 30/30 (P-X2 여덟 번째) + eval gate PASS (revise mean_delta 0.092) + Critic warnings 16→0 + P-EVAL-HARNESS-001 신규 + P-DEPRECATED-REMOVAL-001 신규 + revise effect eval (Phase 4.5 D6 해소) + generate.py canonical wiring 보강 |
| **M0** | **Meta-Factory Prep (★ meta-phase — L3 Meta-Harness Factory skeleton)** | **done** (2026-05-31) | 3 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + **★ 런타임 변경 0 (A9 — FastAPI/Next.js/Supabase 0줄)** + **P-X1 50연속** + PlanCard 35연속 + component_map 45연속 + ADR-035 (L3 Meta-Factory 도입) + CC-006 (INDEX harness-factory #21 Skill 등록) + harness-factory Skill ★ 신규 등록 (proposal-only, 키워드 scoped) + multi-llm-validation formal 여덟 번째 (★ 첫 meta-phase, V1~V6) + pytest 339 유지 + smoke_test_phase_M0 6/6 + scenario_sim v7 33/33 (P-X2 아홉 번째, SM1~SM3) + Skill 20→21 + P-META-FACTORY-001 신규 + meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs (★ 제품 phase 번호 분리 detour) |
| **M1** | **Meta-Factory Sample Test (★ meta-phase dry-run — M0 machinery 팟캐스트 1회 검증)** | **done** (2026-05-31) | 2 Slice dry-run (sub-agent, outputs/TEST/ only) + doc-sync (main 별도 commit) + ★ 런타임 0 (A9) + dry-run outputs/TEST/ 외 0 (MG1) + **P-X1 52연속** + 6검증 PASS 5/PENDING 1 + with/without 6지표(누락 0v6/cross-ref 0v4/gate 1v0) + 5 gaps 전부 재현 + **GAP 8 백로그**(핵심 G2/G3/G5) + ADR-036 + harness-factory ★ 첫 실 트리거 (payoff deferred 첫 실증) + Skill 21 유지 + P-META-FACTORY-002 신규 + pytest 339 유지 (dry-run) |
| **M2** | **Meta-Factory GAP Remediation (★ meta-phase — M1 8 GAP machinery 반영 + 재검증)** | **done** (2026-05-31) | 3 Slice (S1 생성-입력/절차 + S2 scaffold/schema + S3 재검증) + doc-sync + ★ 런타임 0 (A9) + **additive-only** backward-compat + **P-X1 55연속** + 백로그 **8→0** (addressed 7 + expressible 1) + 6검증 재판정 PASS 5/PENDING-BY-DESIGN 1 + CC-007 (machinery 8 GAP) + ADR-037 + harness-factory 두 번째 실 트리거 + multi-llm formal 아홉 번째 + **self-improvement loop 완주** (M0→M1→M2) + P-ADDITIVE-COMPAT-001 신규 + Skill 21 유지 + pytest 339 유지 |
| **M3** | **이질 도메인 dry-run (★ meta-phase — 범용성 2차 검증, 재무)** | **done** (2026-05-31) | 2 Slice dry-run (S1 생성 + S2 validation) + doc-sync + ★ machinery 0줄(개선본 읽기만) + 런타임 0(A9) + outputs/TEST/ 외 0(MG1) + **P-X1 57연속** + 범용 **강함**(미디어 편향 0) + M2 개선 유효 7/부분 1/부적합 0 + 6검증 PASS 4/PENDING-BY-DESIGN 2 + 새 GAP 3(전부 minor/nice-to-have, blocking 0 → 백로그) + harness-factory 세 번째 실 트리거 + ★ **분기 = Phase 10 직행** + Skill 21 유지 + pytest 339 유지 |
| **10** | **MVP 통합 테스트 (scope C)** | **done** (2026-05-31) | 4 Slice + entry(multi-llm 10th) + ★ 제품 phase(런타임 有, behavior-preserving) + MVP end-to-end 통합 **PASS(결함 0)** + pytest 339→**381** + P-AUX-2 brand_memory_extractor 실구현(agent 5→6, CC-008) + 실 LLM eval mode capability(default mock) + RAG eval_rubric v1.0.0 + golden_set 11→15(CC-009) + 배포 Gate A 통과 + ADR-038 + P-X1 60연속 + PlanCard/component_map 0줄 유지 |
| **11** | **LLM Gateway (A안 + B안 — registry/alias + 3-provider + cross-validation)** | **done** (A안 2026-06-01 / B안 2026-06-02) | A안: gateway 골격 + cross_validation + orchestrator gated hook(ADR-039/CC-010). **B안 확장**: Anthropic adapter + 3-provider 분기 + 3-plan 다양성 alias + 펜스 stripping + `run_planning_multi_provider_3` + orchestrator gated 분기(`multi_provider_plans_enabled` default OFF) + gemini-flash model 교정. pytest 381→**471** + behavior-preserving + ★ **라이브 3-provider 3안 입증**(openai/anthropic/google 각 1안 실생성, FALLBACK 0). B안 정식화(ADR/cost) 일부 비차단 잔여. |
| **12** | **검증 페이즈 (Validation — MVP 품질·가치 실측)** | **done** (2026-06-02) | ★ 사용자 지침 "12=검증". 구조 정확성(완료)이 아닌 **출력 품질·가치** 실측. **깊이 격차 4.3x 실측**(compact 0.231 vs rich 1.000, 6/6 편차 0) → 결론(단순함=모델 한계 아님, prompt/schema 설계) + golden_set 15→25 + depth_actionability 차원(CC-011) + S4 human review kit. ★ **S4 사용자 실 채점 = deferred**(사용자 실 UI 직접 확인으로 결론 확정, kit 은 optional 보정 보존). ★ 운영 코드 0 수정 + behavior-preserving(pytest 471). P-VALIDATION-DEPTH-GAP-001(신규 후보). |
| **13** | **출력 확장 (Output Enrichment — compact→rich)** | **done** (2026-06-03) | ★ 이 프로젝트 **첫 의도적 출력 변경** phase를 gated 로 안전하게. Phase 12 가 입증한 깊이 격차를 운영 출력에 반영 — **깊이 0.231→1.000(≥0.8 PASS, OFF byte-identical)** + Critic depth(88점 함정 해소) + frontend rich + ★ 라이브 입증(/generate end-to-end rich HTTP 200). 6 Slice(S1 스키마 CC-012 / S2 프롬프트 P-006 v1.1.0 CC-013 / S3 gated wiring CC-014 / S4 Critic depth P-007 v1.2.0 CC-015 / S5 frontend + 품질점수 숨김 / S6 cost CC-016 + 깊이 재측정 + close). pytest 471→**499**(기존 471 수정 0 = OFF 회귀 0) + 키 0. ★ rich default 전환 미결정(non_goal — gated OFF 유지). |
| 14 | 위저드 ↔ 백엔드 실연결 (Scope A) | **done** (2026-06-03) | 위저드→실 3안 rich e2e PASS, 신규 endpoint 0, 랜딩 byte-identical (archive) |
| 15 | director 모드 (output_mode 3rd tier) | **done** (2026-06-03) | director gated/additive + 라이브 PASS + critic 10차원 (archive) |
| — | Intent 완화 (CC-021, focused fix) | **done** (2026-06-03) | P-001 v1.1.0 콘텐츠 토픽 기본 수용 + 차단→재작성 UX (미numbered, main merged) |
| 16 | A/B 실험 (Baseline 래퍼 vs Agent-grade PKM/RAG) | **done** (2026-06-04) | ★ 검증/실험 페이즈(런타임 0). **판정 GO(메커니즘)**: generic Δ+0.008(flat=commodity) vs ★fit Δ+0.425(agent-grade 압도). 주입 방식 결정적(rag_context 0 / binding 큰 효과). S1+S2(pytest 537→556) + S3 blind kit(사용자 채점 deferred) + A4 종적 이월. (archive) |
| 17 | 계정별 PKM 실빌드 (가 + 다) | **done** (2026-06-04) | ★ Phase 16 GO 기반 첫 production 빌드. 가(신원 plumbing+brand 주입+brand foundation) + 다(개인 PKM pkm_entries CC-022 + brand·개인 추출루프 + e2e). **PKM 루프 양쪽 폐쇄** + 라이브 3중 입증(brand steer/개인 e2e/Supabase 영속) + get_supabase service-key. gated default-OFF, pytest 470→608. (archive) |
| 18 | 브랜딩 세션 (Akinator 주제발굴) | **done** (2026-06-04) | LLM 동적 스무고개(카드+자유입력) → 후보 주제 3×브랜딩 방향 → planning + brand_memory(PKM) 시드. S1(P-AUX-3 agent)+S2(endpoint+상태)+S3(frontend /new/branding)+S4(택1→PKM 시드). ★ 발굴→축적→주입 루프 닫힘 + ★라이브 e2e(브라우저: 8질문→후보3→택1→생성). CC-023. gated/additive, pytest 608→641. (archive) |
| 19 | 2nd brain 시각화 (마이페이지 PKM 도식화) | **done** (2026-06-04) | `/brain` — 개인 PKM+브랜드 PKM 모바일 카드/리스트 + 데스크톱 react-flow 그래프(@xyflow lazy-load, 모바일 미포함) 하이브리드 + 큐레이션(잠금/편집/삭제). S1(/me/pkm-graph API)+S2(모바일 카드)+S3(데스크톱 그래프)+S4(PATCH/DELETE 큐레이션). ★ 발굴→축적→주입→**가시화** 루프 완성. 읽기 레이어(신규 데이터모델 0). CC-024. gated/additive, pytest 641→668. 라이브 시각 e2e 이월(@xyflow 재기동). (archive) |
| **20** | **commercial_viral 모드 (output_mode 4th tier)** | **active** (entry 2026-06-04) | `output_mode` 4-tier(compact<rich<director<**commercial_viral**) — 상업·전략급 기획 브리프(10슬롯 + scene 7필드 + Critic 17차원). director(P15) 패턴 직접 계승, 전부 gated/additive/OFF byte-identical. 보정1(보장 아님)·보정2(기획 브리프 한정, 영상제작 제외)·보정3(데이터레이어 의존, v1 LLM-only 추측표기). 선행조건(a/b/c)+데이터레이어 충족. S1(schema)→S2(prompt)→S3(wiring)→S4(critic)→S5(frontend)→S6(verify). 근거 `meta/proposals/2026-06-03_commercial-viral-mode-design.md` |
| 21~30 | 고도화 / 배포 | future | 배포 Gate B~G / Spring, Expo, Custom RAG, LangGraph |

### ★ PARKED 제안 (future direction — proposal-first, 선행조건 gated, 빌드 승격 X)

> 메인 세션 판정(2026-06-03): GPT 기획 2건은 하네스-정합적이나 **MVP 실사용 미검증 + 위저드 mock(랜딩 / 만 실동작)** 이라 **PARKED**. 선행조건(Phase 13 rich 실사용 검증 + 위저드 실연결 + human review) 통과 전 빌드 착수 금지. 페이즈 번호는 **provisional**.

| 제안 | 문서 | provisional 배치 | 선행조건 |
|---|---|---|---|
| **Commercial Viral Mode** (4-tier compact/rich/director/commercial_viral + 10섹션 + critic 8차원 + golden5) | `meta/proposals/2026-06-03_commercial-viral-mode-design.md` | director≈P15 → commercial_viral≈P18~19 | rich 실검증 + ★ 데이터레이어(PKM/RAG) |
| **PKM/RAG Orchestrator** (6 scope + Trend Snapshot + retrieval orchestrator + instruction search) | `meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md` | 1차≈P16~17 → 고도화≈P20~21 (= 위 21~30 Custom RAG 구체화) | 위저드 실연결 + 5단계 비충돌 |

★ 둘은 **결합**: commercial_viral 의 market/trend 품질 = PKM/RAG+Trend 레이어에 의존 → 데이터레이어 선행. 둘 다 additive Optional + default OFF + 검증 게이트 후에만 ON.

## Phase 13 done (archive) — 제품 phase (출력 확장 — Output Enrichment, compact→rich)

`phases/archive/phase-13-output-enrichment/`

```
Status     : ✅ DONE (2026-06-03)
유형       : 제품 phase (런타임 有 — ★ 이 프로젝트 첫 의도적 출력 변경) — gated 단계 롤아웃 + additive 스키마(flag OFF byte-identical, behavior-preserving)
Goal       : Phase 12 가 입증한 깊이 격차(compact 0.231 → rich 잠재 1.0, 4.3x)를 운영 출력에 반영 — compact 7필드 → rich(후크 변형·타임코드·화면·대사·자막·샷·썸네일·제목·CTA·레퍼런스·길이변형·타깃·톤). 목표 depth 0.231 → ≥0.8.
Result     : Entry + 6 Slice + ★ flag OFF byte-identical(behavior-preserving, 기존 471 test 수정 0) + pytest 471→499(+28: S1 10 + S2 5 + S3 7 + S4 6) + 키 0. 깊이 재측정(운영 run_planning OFF/ON 토글) OFF 0.231 / ON **1.000(≥0.8 PASS, 4/4 편차 0)** + Critic depth 88점 함정 해소 + frontend rich 조건부 8섹션 + ★ 라이브 입증(/generate end-to-end rich HTTP 200, rich 9슬롯 + beat visual/dialogue/caption + 화면 rich)
핵심 발견  : ★ 첫 의도적 출력 변경을 **gated + additive 스키마 + compact-serialize** 3중 안전장치로 회귀 0 롤아웃 (OFF byte-identical / ON rich). prompt gated 공존(P-006 v1.0.0 active/v1.1.0 gated, P-007 v1.1.0 active/v1.2.0 gated — deactivate 아님). Phase 12 측정 → Phase 13 운영 반영 → S6 운영 재측정 닫힌 루프(0.231→1.000).
★ 미결정/미완: rich default 전환 **미결정**(non_goal — gated OFF 유지, 사용자 opt-in / Phase 14) + 위저드(/new/*) ↔ 백엔드 실연결 미완(랜딩 / 만 실생성, 위저드 mock — Phase 14 후보) + 품질점수 숨김(SHOW_QUALITY_SCORE flag, 사용자 요청)
6 Slice    : S1 스키마(output_schema §8.1 v1.1.0→v1.2.0 + rich 12 슬롯 additive + model_dump_compact + agent-io-check PASS, CC-012) / S2 프롬프트(planning RICH_SYSTEM_PROMPT + P-006 v1.0.0→v1.1.0 gated 공존, prompt-version-review, CC-013) / S3 gated wiring(config rich_output_enabled default False + 직렬화·프롬프트 분기, OFF byte-identical, CC-014) / S4 Critic depth(9차원 depth_actionability + P-007 v1.2.0 gated + agent-io-check PASS, 88점 함정 해소, CC-015) / S5 frontend(PlanCard rich 조건부 8섹션 순수 additive + 품질점수 숨김) / S6 cost 재조정(CC-016 — rich 3~5배 × 3안 + B-RES-1 통합) + 깊이 재측정 + phase-complete
제품 경계  : ★ 확장본도 "기획 브리프"(촬영·편집 가이드) — 완성 대본/영상 제작 아님 (product_boundary 영구 non-goal)
Sub-agent  : Entry·S1~S5 (sub-agent / S6 main close), 충돌 0 — P-X1 PASS (S6 런타임 .py 0)
회고       : meta/retrospectives/phase-13.md
신규 패턴  : P-GATED-OUTPUT-CHANGE-001 (출력 변경 flag+additive+compact-serialize 회귀 0 신규 후보) + P-VALIDATION-DEPTH-GAP-001 update(Phase 12 계승 — 운영 재측정 입증) + P-BEHAVIOR-PRESERVING-001 update(출력 변경 phase) + P-CONTRACT-FIRST-001 update(CC-012~016 Phase 13 만 5 CC, 누적 17회) + P-X1-EFFECT-001 update
5 CC       : CC-012(스키마) + CC-013(프롬프트 P-006) + CC-014(gated wiring) + CC-015(Critic depth P-007) + CC-016(cost 재조정 rich/B-RES-1)
2 리포트   : eval/regression_results/2026-06-03_phase-13-s6-depth-remeasure.md (OFF 0.231/ON 1.000) + (S6 cost = cost_control_policy §13~§14)
핵심 성과  : **★ 첫 의도적 출력 변경 gated 안전 롤아웃(OFF byte-identical) + 깊이 0.231→1.000(≥0.8) + Critic depth 88점 함정 해소 + frontend rich + 라이브 입증 + pytest 471→499(OFF 회귀 0) + 키 0**
다음 Phase : **Phase 14 (pending_user_decision)** — rich default 전환 결정 / 위저드(/new/*) 실연결 / 배포 Gate B~G / Phase 12 S4 human review 실 채점 + 전수 실 LLM eval / B안 정식화 잔여(B-RES-2/B-RES-3)
```

## Phase 14 done (archive) — 제품 phase (위저드 ↔ 백엔드 실연결, Scope A)

`phases/archive/phase-14-wizard-backend-wiring/`

```
Status     : ✅ DONE (2026-06-03) — 사용자 결정 B + Scope A (최소 배선)
유형       : 제품 phase (프론트 배선 + 백엔드 additive) — ★ 랜딩 `/` byte-identical(behavior-preserving)
Goal       : mock 위저드(/new/quick 4 · /new/discovery 7)를 기존 endpoint(/plans/start→/wizard/{step}→/generate→/plan/[id])에 배선 → 위저드도 실 3안 rich(gated 상속). 신규 endpoint 0.
방향 근거  : project-1(메인 세션 6f30283a) 위저드 분석 — endpoint 이미 존재(배선만)·per-step LLM=PKM/RAG(PARKED, NG1)
Result     : Entry + S1(백엔드 wizard_data additive 조립) + S2(Quick 실연결) + S3(Discovery 실연결) + fix(StrictMode navigation) + ★ 사용자 라이브 e2e PASS(위저드→3안 rich→/plan/[id]). pytest 499→**508**(+9, 기존 499 수정 0=랜딩 byte-identical) + 프론트 build 12 routes + scenario_simulation 36/36 + 키 0. 신규 endpoint 0.
핵심 발견  : ★ 위저드 multi-step → 백엔드 wizard_data **additive** 조립(initial_input 우선=랜딩 byte-identical) + 최종 generate 집중 배선(중간 step UX 보존). 진단: stuck=백엔드 정상(plans=3)/프론트 StrictMode navigation 버그로 정확 분리.
★ 발견·수정 : StrictMode 1회-실행 effect cleanup 의 cancelled 플래그가 navigation 막음(fix 7cb52e2) + dev 중 next build 로 .next 청크 오염(복구, 학습)
후속(업그레이드): ★ **더 깊은 대본기획**(사용자 플래그) = PARKED commercial_viral/director + per-step 실 LLM(NG1) + PKM/RAG 데이터레이어 (provisional P15~21, 선행조건=본 위저드 실연결 ✅ 충족)
회고       : meta/retrospectives/phase-14.md
리포트     : eval/regression_results/2026-06-03_phase-14-wizard-wiring.md
신규 패턴  : P-STRICTMODE-ONESHOT-001 + P-NEXT-DEV-BUILD-001 + P-WIZARD-WIRING-001 + P-BEHAVIOR-PRESERVING-001 update(프론트 배선)
커밋       : entry(08b19a0)/S1(b6406b1)/S2(1d42dd1)/S3(0142233)/fix(7cb52e2)/chore(Temp untrack)
다음 Phase : **pending_user_decision** — rich default 전환(A) / 배포 Gate B~G(C) / 품질·정식화(D) / PARKED(PKM-RAG→commercial_viral, 선행조건=위저드 실연결 충족 → 후보 활성)
```

## Phase 15 done (archive) — 제품 phase (director 모드, output_mode 3rd tier)

`phases/archive/phase-15-director-mode/`

```
Status     : ✅ DONE (2026-06-03) — 로드맵 ① director (project-1 PARKED 제안서 기반)
유형       : 제품 phase (출력 tier 확장) — ★ compact/rich byte-identical(behavior-preserving) + additive/gated
Goal       : output_mode 를 compact/rich/director 3-tier 일반화 + director(rich + 연출·리텐션 슬롯) gated/additive. director=LLM-only(데이터레이어 비의존).
director슬롯: hook_system + retention_architecture + scene_breakdown[5필드] (제안서 open issue #1 확정). 상업필드=commercial_viral(NG).
Result     : Entry + S1(스키마 v1.3.0) + S2(P-006 v1.2.0) + S3(wiring) + S4(critic retention_design v1.3.0) + S5(frontend) + S6(director Plan-read fix + 라이브 검증 + cost). pytest 508→**536**(기존 508 수정 0=compact/rich byte-identical) + 프론트 build 12 routes + scenario_simulation 36/36 + 키 0. 신규 endpoint/agent 0.
라이브 검증 : ★ director API PASS — 슬롯 전부 채워짐(hook_system 2 / retention_architecture / scene_breakdown 2씬×5필드) + critic 10차원. 브라우저 확인.
★ 발견·수정 : Intent 오반려(맨 토픽→INV-001, 별개 후속) + director Plan-read wiring 누락(generate/orchestrator 가 LLM dict 에서 director 미read → 빈 출력, fix ce6cf99).
★ 사용자 피드백: director=**초안 수준**(기획 브리프 경계) — 대본 직접 쓰기엔 부족 → 품질 보강은 이후 phase(commercial_viral + PKM/RAG).
회고       : meta/retrospectives/phase-15.md
리포트     : eval/regression_results/2026-06-03_phase-15-director-verify.md
4 CC       : CC-017(스키마)+CC-018(P-006)+CC-019(critic P-007)+CC-020(cost)
신규 패턴  : P-OUTPUT-SLOT-WIRING-001(새 슬롯=6곳 wiring) + P-LIVE-VERIFY-001(자동 green≠동작) + P-GATED-OUTPUT-CHANGE-001 update
다음 Phase : **pending_user_decision** — ★ ① Intent 오반려 개선(다음 작업) / ② 검증 보강(human review + 전수 eval) / ③ PKM/RAG 데이터레이어 → commercial_viral / rich default 전환 / 배포 Gate B~G
```

## 🟡 잔존 후보 (Phase 15 done — A/C/D + commercial_viral/PKM-RAG 후속)

```
Phase 1~14 완료 + Phase 15 director active. 잔존 결정 후보:

A. rich default 전환 결정
  - flag `rich_output_enabled` default ON(전 사용자 rich) 전환 여부. cost(CC-016 — 출력 토큰 3~5배 × 3안, tier 유료/opt-in 권고) + 품질(feature 존재 ≠ 콘텐츠 우수성, human review 보강) 합의 후. 현재 = gated OFF 유지.

B. ✅ 위저드(/new/*) ↔ 백엔드 실연결 — **Phase 14 done (2026-06-03)**
  - 완료: 위저드 → startPlan→wizardStep×→generateMultiPlan → 실 3안 rich → /plan/[id]. 신규 endpoint 0, 랜딩 byte-identical, pytest 508. (더 깊은 대본기획 = PARKED 업그레이드.)

C. 배포 Gate B~G (운영 진행)
  - B Staging 배포(env/secret — ★ user-provided) → C 내부 알파 → D Beta(실 LLM opt-in) → E 제한 사용자 → F 비용/성능(cost-review — rich/다중-provider 합산 §13~§14) → G Production Readiness.

D. 품질·정식화 보강
  - Phase 12 S4 human review 실 채점 ↔ LLM-as-judge 신뢰도 대조 + 전수(golden_set 25) 실 LLM eval baseline / B안 정식화 잔여(B-RES-2 ADR / B-RES-3 agent_io·registry contract-change) / 4계층 linkage / SSE async worker / prompt A/B / 자동 promotion / M3 새 GAP 3(G9/G10/G11).

진입 전 권장 검토:
  - phases/archive/phase-13-output-enrichment/closing_notes.md (Phase 13 총괄 + 미결정/미완)
  - eval/regression_results/2026-06-03_phase-13-s6-depth-remeasure.md (깊이 재측정 OFF/ON)
  - ai_system/orchestration/cost_control_policy.md §13~§14 (rich/다중-provider cost, CC-016)
  - meta/retrospectives/phase-13.md (P-GATED-OUTPUT-CHANGE-001 + P-VALIDATION-DEPTH-GAP-001)
```

## Phase 0 완료 (archive)

`phases/archive/phase-0-migration/`

```
Status     : ✅ DONE (2026-05-26)
Goal       : GPT 골격 + 우리 콘텐츠 병합하여 운영 가능한 하네스 완성
Result     : 11/11 acceptance 통과, 6 commit (S0~S5), ~50,000줄 하네스
Acceptance : 모두 충족 (acceptance.md 참조)
다음 Phase : 1. MVP 기본 플로우 (active, 진입 대기)
```

## Phase 1 done (archive)

`phases/archive/phase-1-mvp-basic-flow/`

```
Status     : ✅ DONE (2026-05-26)
Goal       : 영상기획 AI 에이전트의 핵심 흐름 구현 (입력 → 기획 → 검증 → 저장)
Result     : 7 Slices + pytest 62/62 + automated smoke 5/5 + CC-001 + retrospective
Acceptance : 8/8 implementation pass + Manual smoke (사용자 release 단계, Phase 외)
Sub-agent  : 6 dispatches (Wave 1×2 + Wave 2 + Wave 3 + Wave 4×2), 충돌 0
회고       : meta/retrospectives/phase-1.md
개선 제안  : meta/proposals/2026-05-26_phase-1-retrospective-proposals.md (P1~P4)
다음 Phase : 2. design.md 기반 PWA 설계 (active, 진입 대기)
```

## Phase 2 done (archive)

`phases/archive/phase-2-pwa-design/`

```
Status     : ✅ DONE (2026-05-27)
Goal       : design.md 기반 PWA 설계 (Discovery wizard + Quick Mode 분기, 4계층 데이터 모델 화면 매핑)
Result     : 6 Slices + 5 Waves + acceptance 10/10 PASS + audit_naming 0 drift (모든 Slice) + 변경성 시뮬레이션 5/5 PASS + design-review 7 원칙 정합 + qa-check v1.2.0 11 카테고리 (5 PASS / 6 skip - spec phase)
산출물     : 17 신규/수정 (design_system 4 + ADR 2 + flow specs 4 + wireframes 4 + design_handoff 1 + page_map 1 + component_map 1) — apps/web/* 약 3962 insertions / 0 코드
Sub-agent  : 6 dispatches (Wave 1 + Wave 2 + Wave 3×2 + Wave 4 + Wave 5), 충돌 0
회고       : meta/retrospectives/phase-2.md
신규 패턴  : P-AGENT-SCOPE-001 (sub-agent forbidden 침범, 무충돌) + P-DESIGN-LAYERED-001 (변경성 보장 효과)
개선 제안  : meta/proposals/2026-05-27_phase-2-retrospective-proposals.md (P-X1~P-X5, proposed 상태)
다음 Phase : 3. Next.js PWA 기본 UI 구현 (active, 진입 대기)
```

## Phase 3 done (archive)

`phases/archive/phase-3-pwa-impl/`

```
Status     : ✅ DONE (2026-05-28)
Goal       : Next.js PWA UI 실 구현 (Phase 2 spec 기반)
Result     : 6 Slices + 5 Waves + acceptance 10/10 PASS + audit_naming 0 drift + audit_page_component.ps1 (D5) 신규 0 drift + 변경성 4/5 PASS + 1 WARN + design-review 7 원칙 정합 (impl) + qa-check v1.2.0 11 카테고리 (8 PASS / 3 skip) + smoke 7/7 PASS
산출물     : ~20 신규 (apps/web/* 18 + scripts 2) — 약 +2905 코드 / +6550 전체
Sub-agent  : 5 dispatches (Wave 1 + Wave 2 + Wave 3×2 + Wave 4), 충돌 0
회고       : meta/retrospectives/phase-3.md
신규 패턴  : P-X1-EFFECT-001 (P-X1 §SELF-VERIFICATION 5/5 효과 입증) + P-THIN-VERTICAL-001 (Thin Vertical Slice 효과)
Mitigated  : P-AGENT-SCOPE-001 (Phase 2 발견 → Phase 3 P-X1 적용 후 0건 재발)
개선 제안  : meta/proposals/2026-05-28_phase-3-retrospective-proposals.md (Y-X1~Y-X3, proposed 상태) + Phase 2 P-X2 채택 권장
다음 Phase : 4. FastAPI 기본 백엔드 구현 (active, 진입 대기)
```

## Phase 4 done (archive)

`phases/archive/phase-4-fastapi-extension/`

```
Status     : ✅ DONE (2026-05-28)
Goal       : 기존 /generate 유지 + 새 /plans/{plan_id}/generate + 3-plan + Critic verdict + 회귀 0
Result     : 4 Slices + 4 Waves (sequential) + acceptance 10/10 PASS + audit_naming + audit_page_component 0 drift (Slice 4 D-1 해소) + 변경성 4/5 + 1 WARN (Phase 3 결과 유지, Phase 4 +0 영향) + 보조 시나리오 3/3 PASS + design-review 7원칙 정합 (impl) + qa-check v1.2.0 (9 PASS / 2 skip) + smoke 8/8 PASS
산출물     : ~15 신규 + 8 수정 + 9 archive 이동 (backend +1850 / frontend +280 / docs/decisions ADR-014+015 / scripts +170 / QA 5 reports / 회고 + closing_notes)
Sub-agent  : 3 dispatches (Slice 1~3 — Slice 4 본 회고는 main session), 충돌 0
회고       : meta/retrospectives/phase-4.md
신규 패턴  : P-GPT-REVIEW-001 (외부 LLM 검토 채택 효과 — 6→4 Slices, ▼66% 시간) + P-X1-EFFECT-001 update (9연속)
Mitigated  : P-AGENT-SCOPE-001 (9연속 누적 입증 — Phase 3 5 + Phase 4 4)
개선 제안  : meta/proposals/2026-05-28_phase-4-retrospective-proposals.md (Z-X1~Z-X3, proposed) + Phase 2 P-X2 채택 권장 (우선순위 ↑)
GPT 검토   : 채택 (6→4 Slices ▼33% / 18~26h → 6~8h ▼66%)
핵심 성과  : **P-X1 9연속 PASS + component_map.md 15연속 0줄 + PlanCard.tsx 4연속 0줄 + GPT 검토 채택 효과 실증**
다음 Phase : Phase 4.5 mini-phase (사용자 결정 옵션 A 채택)
```

## Phase 4.5 done (archive)

`phases/archive/phase-4.5-critic-revise-loop/`

```
Status     : ✅ DONE (2026-05-28)
유형       : mini-phase (Phase 4 후속 + Phase 5 진입 전 안정화)
Goal       : Critic revise loop + Rewriter + Z-X3 best-plan + P-X2 자동 게이트
Result     : 4 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + smoke 9/9 + scenario_simulation 5/5 (P-X2 첫) + pytest 109/109 (+16) + audit 0 drift × 2
산출물     : ~12 신규 + ~10 수정 (backend +450 / frontend +45 / scripts +200 / docs +300 / meta +200)
Sub-agent  : 4 dispatches (Slice 1~4 모두), 충돌 0 — P-X1 §SELF-VERIFICATION 4/4 PASS
회고       : meta/retrospectives/phase-4.5.md
신규 패턴  : P-X2-EFFECT-001 + P-VALIDATION-FORMAL-001 + P-X1-EFFECT-001 update (13연속)
Mitigated  : P-AGENT-SCOPE-001 (13연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4)
사용자 결정 : Z-X3 포함 + P-X2 채택 + multi-llm-validation formal (Claude Code 자가 검증, 외부 placeholder 분리) + 4 Slice 모두 sub-agent
핵심 성과  : **P-X1 13연속 PASS + PlanCard 9연속 + component_map 19연속 + multi-llm-validation formal 첫 + P-X2 자동 게이트 첫**
다음 Phase : Phase 6 (Output Schema + Agent IO Stabilization, 옵션 B 변형 채택)
```

## Phase 6 done (archive)

`phases/archive/phase-6-output-schema-stabilization/`

```
Status     : ✅ DONE (2026-05-29)
유형       : stabilization mini-phase (Phase 5 DB/Auth 진입 전 contract 안정화)
Goal       : Critic verdict canonical 결정 + Rewriter contract 강화 + revise_history/recommended_plan_index 정식 등록 + DB 진입 전 schema drift 위험 0
Result     : 4 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + smoke 10/10 + schema_stress_test 5/5 (P-X2 v2) + scenario_simulation 5/5 (P-X2 두 번째) + pytest 144/144 (+35) + audit×2 0 drift
산출물     : ~10 신규 + ~10 수정 + 3 contract 갱신 (output_schema + agent_io_contract + api_contract) + ADR-018/019
Sub-agent  : 4 dispatches (Slice 1~4 모두), 충돌 0 — P-X1 4/4 PASS
회고       : meta/retrospectives/phase-6.md
신규 패턴  : P-CRITIC-CANONICAL-001 + P-CONTRACT-FIRST-001 (신규 후보) + P-X1-EFFECT-001 update (17연속) + P-VALIDATION-FORMAL-001 update (두 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (17연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4)
Skill 첫 정식: agent-io-check (첫 정식) + contract-change (본격 실 변경) + multi-llm-validation formal 두 번째 + phase-complete v1.2.0 두 번째 자동 게이트
GPT 검토안 정신: 6→4 Slice 압축 (▼33%) + 시간 8~12h → 실측 ~8h (▼20%, P-GPT-REVIEW-001 두 번째 적용)
핵심 성과  : **P-X1 17연속 PASS + PlanCard 12연속 + component_map 22연속 + Critic canonical 결정 + Rewriter v1.1.0 + agent-io-check 첫 정식 + contract-change 본격**
다음 Phase : **🟡 Phase 5 (DB/Auth) — pending entry** (사용자 결정 "Phase 6 → Phase 5 순차" 계승)
```

## Phase 5 done (archive)

`phases/archive/phase-5-db-auth/`

```
Status     : ✅ DONE (2026-05-29)
유형       : large phase (15~20h — MVP 본격 영속화)
Goal       : Supabase + PostgreSQL 영속화 + Supabase Auth + JWT + RLS + SSE Progress D7
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 12/12 (11 PASS + 1 WARN intended) + scenario_simulation v2 10/10 (P-X2 세 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 170/170 (+26) + audit_naming 0 drift × 2 + audit_page_component 2 intended drift WARN (Slice 3 AuthGuard + /login 신규)
산출물     : ~30 신규 + ~10 수정 (backend db/auth/sse +1500 / frontend AuthGuard + login + sse.ts +600 / tests +400 / docs/contracts/db_schema.md + ADR-020/021/022 / scripts/smoke_test_phase_5.ps1 / meta retrospectives/security_reviews/validations)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-5.md
신규 패턴  : P-RLS-001 + P-SSE-001 + P-SECURITY-REVIEW-001 (신규 후보) + P-X1-EFFECT-001 update (22연속) + P-VALIDATION-FORMAL-001 update (세 번째 정식 확정)
Mitigated  : P-AGENT-SCOPE-001 (22연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5)
Skill 첫 정식: security-review (★ 첫 정식 Slice 1 + 두 번째 final Slice 5) + contract-change (두 번째 본격 — db_schema.md) + multi-llm-validation formal 세 번째 (V1~V6) + phase-complete v1.2.0 세 번째 자동 게이트 + agent-io-check 두 번째 회귀
4 ADR      : ADR-020 Supabase + ADR-021 RLS Policy + ADR-022 SSE Progress
핵심 성과  : **P-X1 22연속 PASS + PlanCard 17연속 + component_map 27연속 + Supabase 영속화 + JWT httpOnly cookie + RLS 정책 + SSE 4단계 + security-review 첫 정식 + 두 번째 final + contract-change 두 번째 본격**
다음 Phase : **🟡 pending_user_decision** (Phase 7 RAG / Phase 6+ legacy / Phase 8 MOA / Phase 9 저장-피드백)
```

## Phase 5.5 done (archive)

`phases/archive/phase-5.5-legacy-db-consolidation/`

```
Status     : ✅ DONE (2026-05-29)
유형       : consolidation mini-phase (Phase 5 후속 + Phase 7 진입 전 정리)
Goal       : Legacy DB 옵션 A 채택 (ADR-023) + external validation × 3 self-strengthen + ADR-024 Phase 7 RAG scope evolution + Brand Memory Phase 9+ confirm + Phase 7 진입 baseline 확립
Result     : 4 Slices (모두 sub-agent) + A1~A8 8/8 + M1~M2 2/2 + smoke 12/12 (재실행) + scenario_simulation v2 10/10 (P-X2 네 번째) + schema_stress 5/5 + pytest 172/172 (+2 legacy deprecation) + audit_naming 0 drift + audit_page_component 2 intended WARN (Phase 5 baseline 유지)
산출물     : ~6 신규 + ~10 수정 (backend db/* deprecated note +~100 / docs/decisions ADR-023+024 +~250 / meta validations × 3 강화 + retrospective + closing_notes / state docs × 5)
Sub-agent  : 4 dispatches (Slice 1~4 모두), 충돌 0 — P-X1 4/4 PASS
회고       : meta/retrospectives/phase-5.5.md
신규 패턴  : P-LEGACY-CONSOLIDATION-001 신규 후보 + P-X1-EFFECT-001 update (26연속) + P-VALIDATION-FORMAL-001 update (self-strengthen V-form sub-pattern)
Mitigated  : P-AGENT-SCOPE-001 (26연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4)
사용자 결정 : 5건 1:1 mapping (legacy 옵션 A / external 강화 / Phase 7 Lite 유지 / 5단계 MVP 전부 / Brand Memory Phase 9+)
2 ADR      : ADR-023 Legacy DB 옵션 A + ADR-024 Phase 7 RAG scope evolution (5단계 MVP + 확대 지점 A~F)
핵심 성과  : **P-X1 26연속 PASS + PlanCard 18연속 + component_map 28연속 + legacy backward-compat 100% + Phase 7 진입 baseline 확립**
다음 Phase : **🟡 Phase 7 (RAG Lite — candidate_knowledge 5단계 MVP, 12~16h) — pending planning** (사용자 명시)
```

## Phase 7 done (archive)

`phases/archive/phase-7-rag-lite/`

```
Status     : ✅ DONE (2026-05-29)
유형       : large phase (12~16h — RAG Lite + candidate_knowledge 5단계 MVP 전부)
Goal       : candidate_knowledge 5단계 파이프라인 전부 (pending → filtered → evaluated → approved → promoted) + pgvector retrieval + LLM Wiki vs RAG 분리 + agents/rag.py 통합
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 13/13 (12 PASS + 1 WARN intended) + scenario_simulation v3 15/15 (P-X2 다섯 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 172 → 223/223 (+51 신규) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~22 신규 + ~10 수정 (backend rag layer +1500 / db/migrations/0004 / tests +500 / docs rag_data_contract §18 + ADR-025/026 / scripts smoke_test_phase_7 + scenario_simulation v3 / meta retrospectives + rag_updates + validations + patterns + skill_usage_log)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-7.md
신규 패턴  : P-RAG-5STAGE-001 (신규 후보) + P-RAG-GRACEFUL-001 (신규 후보) + P-X1-EFFECT-001 update (31연속) + P-VALIDATION-FORMAL-001 update (네 번째 입증) + P-LEGACY-CONSOLIDATION-001 update (누적 2회 — 정식 채택 임박)
Mitigated  : P-AGENT-SCOPE-001 (31연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5)
Skill 첫 정식: rag-design (★ 첫 정식, Slice 1 → ADR-025) + rag-update (★ 첫 정식, Slice 4 → meta/rag_updates/2026-05-29_phase-7-initial-promotion.md) + contract-change 세 번째 본격 (Slice 2 rag_data_contract.md §18) + multi-llm-validation formal 네 번째 (V1~V7 PASS) + phase-complete v1.2.0 다섯 번째 자동 게이트 + agent-io-check 세 번째 회귀
2 ADR      : ADR-025 RAG architecture + ADR-026 5단계 promotion logic
사용자 결정 : 3건 mapping (Phase 5.5에서 이미 명시 — RAG Lite scope 유지 / 5단계 MVP 전부 / Brand Memory Phase 9+ 이관)
핵심 성과  : **P-X1 31연속 PASS + PlanCard 19연속 + component_map 29연속 + 5단계 파이프라인 전부 MVP + rag-design/rag-update 둘 다 첫 정식 + ADR-025/026 + graceful 5종 marker 표준화 + Phase 1 legacy ↔ Phase 7 신규 공존 누적 2회**
다음 Phase : **🟡 Phase 8 (MOA Lite 본격) — done**
```

## Phase 8 done (archive)

`phases/archive/phase-8-moa-lite/`

```
Status     : ✅ DONE (2026-05-29)
유형       : large phase (12~16h — MOA Lite 본격 orchestration 추출 + SSE worker + prompt_registry 정식화)
Goal       : plans_generate() god-function의 MOA orchestration을 service layer orchestrator로 추출 (behavior-preserving) + SSE Progress 실 stage 연동 + prompt_registry P-001~P-008 semver 정식화
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M5 5/5 + smoke 14/14 (13 PASS + 1 WARN intended) + scenario_simulation v4 20/20 (P-X2 여섯 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 223 → 249/249 (+26 신규) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~13 신규 + ~10 수정 (backend orchestration layer +700 / tests +600 / docs ADR-027/028/029 + prompt_registry semver + agent_io_contract v1.2.0 + scripts smoke_test_phase_8 + scenario_simulation v4 + meta retrospectives + validations + patterns + skill_usage_log + closing_notes)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-8.md
신규 패턴  : P-MOA-ORCHESTRATOR-001 (god-function → service layer 추출 behavior-preserving 신규 후보) + P-BEHAVIOR-PRESERVING-001 (기존 test 수정 0 = 동작 불변 증거 신규 후보) + P-X1-EFFECT-001 update (36연속) + P-VALIDATION-FORMAL-001 update (다섯 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (36연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5)
Skill 첫 정식: ai-architecture-review (★ 첫 정식, Slice 1 → ADR-027 + Slice 5 회고) + prompt-version-review (★ 첫 정식, Slice 1 분석 + Slice 4 적용 → ADR-029) + contract-change 네 번째 본격 (Slice 4 CC-003 — prompt_registry + agent_io_contract v1.2.0) + multi-llm-validation formal 다섯 번째 (V1~V7 PASS) + phase-complete v1.2.0 여섯 번째 자동 게이트 + agent-io-check 네 번째 회귀
3 ADR      : ADR-027 MOA orchestrator behavior-preserving + ADR-028 SSE progress integration + ADR-029 prompt_registry semver
사용자 결정 : 3건 mapping (Scope 3개 모두 / Critic conservative adapter Phase 6 canonical 불변 / SSE progress_store 브릿지 background task 미도입)
핵심 성과  : **P-X1 36연속 PASS + PlanCard 24연속 + component_map 34연속 + MOA Orchestrator 추출 (plans.py 659→243 god-function 분해) + behavior-preserving (Envelope byte-identical, 기존 test 수정 0 의도된 2 version assertion 제외) + SSE 실 stage 통합 + prompt_registry semver 정식화 (NG8 누적 3회 해소) + Critic v1.1.0 conservative adapter + ai-architecture-review/prompt-version-review 둘 다 첫 정식**
다음 Phase : **🟡 pending_user_decision** (A Phase 9 저장-피드백 / B Phase 9.5+ eval-run / C Phase 10 통합 / D Phase 11+)
```

## Phase 9 done (archive)

`phases/archive/phase-9-result-feedback/`

```
Status     : ✅ DONE (2026-05-31)
유형       : large phase (10~14h — 결과 저장 + 피드백 + normalize wiring + Brand Memory 준비 + 피드백 UI)
Goal       : plan 선택/피드백 영속화(실 plans 정합) + normalize_to_canonical wiring(critic step canonical 0–1 live, deprecated 0–5 병행 회귀 0) + Brand Memory 준비(P-AUX-2 설계 agent 미구현 Phase 10+) + 피드백 UI wrapper(PlanCard·component_map 무수정)
Result     : 6 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 15/15 (14 PASS + 1 WARN intended) + scenario_simulation v5 25/25 (P-X2 일곱 번째) + schema_stress 5/5 (Phase 6 유지) + pytest 249 → 293/293 (+44 신규, 기존 수정 0) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~16 신규 + ~10 수정 (backend db/migrations/0005 + selection/feedback/brand_memory repo + rag/feedback_to_candidate + routers/plans select/feedback API + orchestration/moa_orchestrator normalize wiring + frontend lib/types+api+page.tsx inline 피드백 UI + tests +44 / docs db_schema.md + ADR-030/031/032 / scripts smoke_test_phase_9 + scenario_simulation v5 / meta retrospectives + security_reviews + validations + patterns + skill_usage_log + closing_notes)
Sub-agent  : 6 dispatches (Slice 1~6 모두), 충돌 0 — P-X1 6/6 PASS
회고       : meta/retrospectives/phase-9.md
신규 패턴  : P-FEEDBACK-LOOP-001 (피드백 영속 graceful + PII 마스킹 신규 후보) + P-CANONICAL-WIRING-001 (Phase N helper → live pipeline wiring additive 회귀 0 신규 후보) + P-X1-EFFECT-001 update (42연속) + P-VALIDATION-FORMAL-001 update (여섯 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (42연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5 + Phase 9:6)
Skill 첫 정식: security-review (두 번째 정식, Slice 1 — 피드백 reason PII T1~T6, P-SECURITY-REVIEW-001 강화) + contract-change 다섯 번째 본격 (Slice 2 CC-004 — db_schema.md selected_plans/feedback_events 실 plans 정합) + multi-llm-validation formal 여섯 번째 (V1~V7 PASS) + phase-complete v1.2.0 일곱 번째 자동 게이트 + agent-io-check 다섯 번째 회귀
3 ADR      : ADR-030 feedback/selection persistence + ADR-031 Brand Memory prep (P-AUX-2 설계) + ADR-032 normalize_to_canonical wiring
사용자 결정 : 3건 mapping (Brand Memory 준비만 agent Phase 10+ / 피드백 UI wrapper PlanCard·component_map 무수정 / normalize wiring critic step canonical deprecated 병행)
핵심 성과  : **P-X1 42연속 PASS + PlanCard 30연속 + component_map 40연속 + 결과저장(selected_plans) + 피드백(feedback_events) 영속화 graceful + PII 마스킹 + normalize_to_canonical wiring (canonical 0–1 live, deprecated 0–5 병행 회귀 0, warnings 67→16) + Brand Memory 준비 (feedback→candidate pending 적재, agent Phase 10+) + 피드백 UI inline (PlanCard·component_map 0줄) + security-review 두 번째 정식 + contract-change CC-004**
다음 Phase : Phase 9.5 eval-run 정식화 (✅ done 2026-05-31)
```

## Phase 9.5 done (archive)

`phases/archive/phase-9.5-eval-run/`

```
Status     : ✅ DONE (2026-05-31)
유형       : eval mini-phase (6~10h — eval-run 정식화 + Critic deprecated 0–5 Full 제거)
Goal       : golden_set 회귀 runner(mock-deterministic, CI 가능) + revise effect eval(Phase 4.5 D6 해소) → eval-design/eval-run Skill 첫 정식 + eval로 canonical-only 품질 검증 후 Critic deprecated 0–5 Full 제거(canonical 단일 표준)
Result     : 5 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M4 4/4 + smoke 16/16 (15 PASS + 1 WARN intended) + scenario_simulation v6 30/30 (P-X2 여덟 번째) + eval gate PASS (schema 1.0 / pass 1.0 / revise mean_delta 0.092 / improved 0.6 / regressed 0.2) + schema_stress 5/5 (Phase 6 유지) + pytest 293 → 339/339 (+46 신규) + audit_naming 0 drift × 1 + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승) + Critic deprecated warnings 16→0
산출물     : ~12 신규 + ~8 수정 (backend/fastapi/eval module 5: __init__/golden_set_loader/runner/revise_effect/report + scripts/eval_run.ps1 + tests test_eval_runner+test_revise_effect / agents/critic.py deprecated 제거 + schemas/output.py CriticEvaluation 제거 + routers/generate.py canonical wiring + apps/web/lib/types.ts canonical 전환 + tests/test_critic 의도 delta + docs ADR-033/034 + output_schema/agent_io_contract/db_schema CC-005 + scripts smoke_test_phase_9_5 + scenario_simulation v6 / meta retrospectives + validations + patterns + skill_usage_log + closing_notes + eval/regression_results × 3)
Sub-agent  : 5 dispatches (Slice 1~5 모두), 충돌 0 — P-X1 5/5 PASS
회고       : meta/retrospectives/phase-9.5.md
신규 패턴  : P-EVAL-HARNESS-001 (golden_set mock-deterministic 회귀 + 임계값 게이트 신규 후보) + P-DEPRECATED-REMOVAL-001 (eval 안전망으로 deprecated 제거 신규 후보) + P-X1-EFFECT-001 update (47연속) + P-VALIDATION-FORMAL-001 update (일곱 번째 입증)
Mitigated  : P-AGENT-SCOPE-001 (47연속 누적 입증 — Phase 3:5 + Phase 4:4 + Phase 4.5:4 + Phase 6:4 + Phase 5:5 + Phase 5.5:4 + Phase 7:5 + Phase 8:5 + Phase 9:6 + Phase 9.5:5)
Skill 첫 정식: eval-design (★ 첫 정식, Slice 1 — golden_set executable format + 채점 차원 + 임계값 게이트) + eval-run (★ 첫 정식, Slice 2~3 — mock-deterministic 회귀 + revise effect) + contract-change 여섯 번째 본격 (Slice 4 CC-005 — output_schema §9 + agent_io_contract §5 canonical-only) + multi-llm-validation formal 일곱 번째 (V1~V7 PASS) + phase-complete v1.2.0 여덟 번째 자동 게이트 + agent-io-check 여섯 번째 회귀
2 ADR      : ADR-033 eval-run harness (mock-deterministic primary + 실 LLM mode flag + 임계값 + §eval-design) + ADR-034 Critic deprecated 0–5 Full 제거 (fallback + CriticEvaluation Optional, run_critic 0–5 불변 P-007 NG3)
사용자 결정 : 2건 mapping (Critic deprecated Full 제거 eval 검증 후 / eval mock-deterministic primary + RAG eval_rubric Phase 10+ 이관)
핵심 성과  : **P-X1 47연속 PASS + PlanCard 35연속 + component_map 45연속 + eval-design + eval-run Skill 첫 정식 (golden_set 11 케이스 mock-deterministic runner + 임계값, ADR-033) + revise effect eval (Phase 4.5 D6 해소 — mean_delta 0.092 / regressed 20%) + Critic deprecated 0–5 Full 제거 (ADR-034 + CC-005, eval 제거 전/후 동일 입증, warnings 16→0) + generate.py canonical wiring 보강 (Phase 1 endpoint normalize 누락 회귀 방지)**
★ deviation : generate.py canonical wiring 보강 (수용 — Phase 1 endpoint normalize 누락 발견·보강, 향후 신규 critic consumer normalize_to_canonical 경유 필수)
다음 Phase : **🟡 pending_user_decision** (A Phase 10 통합 / B Phase 11+)
```

## Phase M0 done (archive) — ★ meta-phase

`phases/archive/phase-M0-meta-factory/`

```
Status     : ✅ DONE (2026-05-31)
유형       : ★ meta-phase (제품 phase 아님 — L3 Meta-Harness Factory skeleton + contract + validation, 4~7h)
Goal       : 현재 구현 하네스(L2) 유지 + 상위에 harness/meta_factory/ (L3) skeleton + factory_contract(8 규칙 proposal-first) + domain_brief/harness_blueprint schema + architecture_patterns(6 + Dreammate 매핑) + workflow + templates 6 + 현재 하네스 blueprint 실측 + harness-factory Skill(proposal-only). ★ 자동 generator 아니라 skeleton·contract·validation 까지만 (payoff deferred).
Result     : 3 Slices (모두 sub-agent) + A1~A10 10/10 + M1~M3 3/3 + ★ 런타임 변경 0 (A9 — backend/fastapi 0 / apps/web 0 / db/migrations 0, git diff fff913e..HEAD 게이트) + smoke_test_phase_M0 6/6 + scenario_simulation v7 33/33 (P-X2 아홉 번째) + pytest 339 유지 + audit_naming 0 drift + audit_page_component 2 intended drift WARN (Phase 5 baseline 계승)
산출물     : ~24 신규 + ~6 수정 (meta_factory 7 루트 + templates 6 + blueprint + outputs 2 + ADR-035 + validations 2 + harness-factory/SKILL.md + proposal + CC-006 + smoke_test_phase_M0 + retrospective + closing_notes / INDEX.md #21 + scenario_simulation v7 + patterns + skill_usage_log + state docs 4)
Sub-agent  : 3 dispatches (Slice 1~3 모두), 충돌 0 — P-X1 3/3 PASS
회고       : meta/retrospectives/phase-M0.md
신규 패턴  : P-META-FACTORY-001 (L3 proposal-first 메타 레이어 신규 후보) + P-X1-EFFECT-001 update (50연속) + P-VALIDATION-FORMAL-001 update (여덟 번째 ★ 첫 meta-phase 입증)
Mitigated  : P-AGENT-SCOPE-001 (50연속 누적 입증 — Phase 3:5 + ... + Phase 9.5:5 + Phase M0:3)
Skill 첫 정식: harness-factory (★ 신규 등록 #21, proposal-only 키워드 scoped — 트리거 0 payoff deferred) + contract-change 일곱 번째 (CC-006 INDEX Skill 등록) + multi-llm-validation formal 여덟 번째 (V1~V6, ★ 첫 meta-phase) + harness-audit 키워드 충돌 검토 (충돌 0) + phase-complete v1.2.0 아홉 번째 자동 게이트
1 ADR      : ADR-035 L3 Meta-Factory 도입 (L1/L2/L3 + proposal-first + payoff deferred + skeleton-only)
1 CC       : CC-006 INDEX harness-factory #21 Skill 등록 (Skill 도 contract 처럼 취급)
사용자 결정 : 3건 mapping (meta-phase 격리 제품 phase 번호 분리 / harness-factory proposal-only 키워드 scoping / proposal-first 생성물 outputs/meta proposals 격리)
핵심 성과  : **P-X1 50연속 PASS + ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9) + L3 Meta-Harness Factory skeleton (meta_factory/ 7 루트 + templates 6 + blueprint 실측 + outputs) + factory_contract 8 규칙(proposal-first) + harness-factory Skill proposal-only (21번째, 키워드 scoped 충돌 0) + validation_workflow ↔ eval-run 연동 + ★ 첫 meta-phase 제품 흐름 무오염**
다음 단계  : harness-factory dry-run / trigger validation 샘플 / with-without 비교 샘플 (Phase M1+) / Phase 10 연결 (meta_factory blueprint = 온보딩·감사 baseline) — meta-phase detour 종료, next_phase_status pending_user_decision
```

## Phase M1 done (archive) — ★ meta-phase dry-run

`phases/archive/phase-M1-meta-factory-sample-test/`

```
Status     : ✅ DONE (2026-05-31)
유형       : ★ meta-phase dry-run (제품 phase 아님 — M0 machinery 1회 실작동 검증, 2.5~4h)
Goal       : M0 meta_factory machinery(generation_workflow 11단계 + validation_workflow 6검증)를 인접 도메인 「팟캐스트 에피소드 기획 AI」에 1회 dry-run 적용 — ① blueprint 생성 가능한가 ② validation 검증 가능한가. 목적 = 성공 아니라 GAP 발견.
Result     : 2 Slice dry-run (sub-agent, outputs/TEST/ only) + doc-sync (main 별도 commit) + A1~A8 + MG1~MG3 PASS + ★ 런타임 0 (A9 — backend/apps/migrations 0) + ★ dry-run outputs/TEST/ 외 0줄 (MG1 — git diff 게이트 S1·S2 PASS) + pytest 339 유지 (dry-run) + 6검증 PASS 5/PENDING 1
산출물     : dry-run ~11 (전부 meta_factory/outputs/TEST/ — README + podcast/{_without_baseline, domain_brief, harness_blueprint, scaffolds 6} + sample_test_podcast_validation) / doc-sync ~6 (retrospective phase-M1 + ADR-036 + patterns P-META-FACTORY-002 + skill_usage_log + PROJECT_STATE + PHASE_REGISTRY)
Sub-agent  : 2 dispatches (S1 generation + S2 validation), 충돌 0 — P-X1 2/2 PASS (★ outputs/TEST/ 격리)
회고       : meta/retrospectives/phase-M1.md
신규 패턴  : P-META-FACTORY-002 (Meta-Factory 첫 dry-run — 실작동 입증 + GAP 백로그 신규 후보) + P-X1-EFFECT-001 update (52연속)
Mitigated  : P-AGENT-SCOPE-001 (52연속 누적 입증 — Phase 3:5 + ... + Phase M0:3 + Phase M1:2)
Skill 첫 정식: harness-factory ★ 첫 실 트리거 (M0 등록 proposal-only → M1 generation_workflow + validation_workflow 실행, payoff deferred 첫 실증) + meta-retrospective (phase-M1 회고)
1 ADR      : ADR-036 (Meta-Factory 첫 dry-run 방법·결과 — 팟캐스트 도메인, 6검증 PASS 5/PENDING 1, GAP 8)
GPT 보완 반영: ① with/without 6지표 수치화 / ② PASS·FAIL·PENDING·GAP 4상태 / ③ outputs 외 0 강제 + phase 기록 별도 doc-sync 분리 + meta-phase 분리
핵심 결과  : 6검증 PASS 5/PENDING 1 + with/without WITH≫WITHOUT(누락 0v6/cross-ref 0v4/gate 1v0) + 5 gaps 전부 재현(5/0/0) + GAP 8(핵심 G2 skill 재사용 결정트리/G3 conditional 슬롯/G5 제3자 PII) + machinery 작동 증거(검증2 podcast-eval-run 4중첩 검출→채택 차단)
핵심 성과  : **P-X1 52연속 + ★ 런타임 0(A9) + dry-run outputs/TEST/ 외 0(MG1) + machinery 실작동 입증 + GAP 8 백로그 + Skill 21 유지(신규 0) + PlanCard 35 / component_map 45 유지**
다음 단계  : 8 GAP machinery 보완 proposal (G2/G3/G5 우선, contract-change 경유, proposal-only) / 검증5 실측 1회 (eval-run §3~§6) / Phase 10 연결 (meta_factory blueprint + TEST 산출물 = 온보딩·감사 참고) — meta-phase detour 종료, next_phase_status pending_user_decision 불변
```

## Phase M2 done (archive) — ★ meta-phase (machinery 개선)

`phases/archive/phase-M2-meta-factory-gap-remediation/`

```
Status     : ✅ DONE (2026-05-31)
유형       : ★ meta-phase (machinery 개선 — L3 contract 변경 CC-007. M1 과 달리 machinery 실제 변경, 3~5h)
Goal       : M1 dry-run 발견 8 GAP(G1~G8)을 meta_factory machinery 에 additive 반영 + M1 TEST 재적용(re-validate)로 해소 입증
Result     : 3 Slice (S1 생성-입력/절차 G1·G2·G5·G6 + S2 scaffold/schema G3·G4·G7·G8 + S3 재검증) + doc-sync + A1~A8 + MG1~MG3 PASS + ★ 런타임 0 (A9) + additive-only backward-compat + 백로그 8→0 + pytest 339 유지 (machinery 문서 import 무관)
산출물     : machinery 7파일 additive (generation_workflow/architecture_patterns/domain_brief_schema/templates 4/harness_blueprint_schema) + 재검증 outputs/TEST/ (revalidation 리포트 + podcast 6 적용) + doc-sync (CC-007 + ADR-037 + retrospective + patterns + skill_usage_log + validation 2 + proposal + state 2)
Sub-agent  : 3 dispatches (S1·S2·S3), 충돌 0 — P-X1 3/3 PASS (S1·S2 machinery editable / S3 outputs/TEST/)
회고       : meta/retrospectives/phase-M2.md
신규 패턴  : P-ADDITIVE-COMPAT-001 (additive 개선 backward-compat 신규 후보) + P-META-FACTORY-002 update (self-improvement loop 완주) + P-X1-EFFECT-001 update (55연속)
Mitigated  : P-AGENT-SCOPE-001 (55연속 누적 — Phase 3:5 + ... + M0:3 + M1:2 + M2:3)
Skill 첫 정식: contract-change 여덟 번째 본격 CC-007 (machinery 8 GAP additive — L3 contract, P-CONTRACT-FIRST-001 누적 8회) + harness-factory 두 번째 실 트리거 (S3 재검증) + multi-llm-validation formal 아홉 번째 (V1~V5) + meta-retrospective
1 ADR / 1 CC: ADR-037 (8 GAP 반영 + 재검증) / CC-007 (machinery 8 GAP additive)
사용자 결정 : 2건 mapping (GAP 범위 = 전체 8개 / 검증 = M1 TEST 재적용 re-validate)
결과       : 백로그 8→0 (addressed 7 + expressible 1=G5 제3자 PII 등급은 승인 게이트) + 6검증 재판정 PASS 5/PENDING-BY-DESIGN 1 (검증3 조건부축 GAP 해소 / 검증5 G8 pending-by-design) + backward-compat ✅ (M1 blueprint 개선 machinery 하 valid)
핵심 성과  : **P-X1 55연속 + ★ 런타임 0(A9) + additive-only backward-compat + 백로그 8→0 + Meta-Factory self-improvement loop 첫 완주 (M0 도입 → M1 dry-run 검증·GAP 발견 → M2 반영·재검증) + Skill 21 유지 + PlanCard 35 / component_map 45 유지**
다음 단계  : 검증5 실 eval-run 표본 (pending-by-design 실측 해소, eval-run §3~§6) / 이질 도메인 dry-run (개선 machinery 범용성 2차 검증) / Phase 10 연결 — meta-phase detour(M0+M1+M2) 종료, next_phase_status pending_user_decision 불변
```

## Phase M3 done (archive) — ★ meta-phase (이질 도메인 범용성 2차)

`phases/archive/phase-M3-heterogeneous-dryrun/`

```
Status     : ✅ DONE (2026-05-31)
유형       : ★ meta-phase dry-run (M1 동형 — machinery 0 변경, 개선본 읽기만. 범용성 2차 검증, ~3h)
Goal       : M2 개선 machinery(G1~G8)를 이질 도메인「개인 재무 플래닝 AI」에 dry-run 적용 — 범용성 + M2 개선 유효성 + 새 GAP
Result     : 2 Slice dry-run (S1 생성 finance/ 9파일 + S2 validation) + doc-sync + ★ 런타임 0(A9) + machinery 0(개선본 읽기만) + outputs/TEST/ 외 0(MG1) + pytest 339 유지
산출물     : outputs/TEST/finance/ (without+brief+blueprint+scaffold 6) + sample_test_finance_validation + 백로그(improvement_reports/2026-05-31_M3-new-gaps-backlog) + doc-sync (retrospective + patterns + skill_usage_log + state 2 + closing)
Sub-agent  : 2 dispatches (S1·S2), 충돌 0 — P-X1 2/2 PASS (outputs/TEST/finance 격리)
회고       : meta/retrospectives/phase-M3.md
신규 패턴  : P-META-FACTORY-002 update (범용성 2차 — 인접+이질 양쪽 입증) + P-X1-EFFECT-001 update (57연속) + P-ADDITIVE-COMPAT-001 재확인
Mitigated  : P-AGENT-SCOPE-001 (57연속 — ... + M2:3 + M3:2)
Skill      : harness-factory 세 번째 실 트리거 (이질 도메인 생성·검증) + meta-retrospective
결과       : 범용 강함(미디어 편향 0) + M2 개선 유효 7/부분 1(G3 문서)/부적합 0 + 6검증 PASS 4/PENDING-BY-DESIGN 2(fail 0) + 새 GAP 3(NEW-G9 minor/G10 nice/G11 nice, blocking 0)
사용자 결정 : 2건 (이질 도메인 dry-run 진행 / 수정 요소 없으면 Phase 10 직행)
핵심 성과  : **P-X1 57연속 + machinery 0줄(개선본 읽기만) + 런타임 0(A9) + 도메인 범용성 입증(인접 M1 팟캐스트 + 이질 M3 재무) + Meta-Factory detour(M0~M3) 종료**
다음 단계  : ★ Phase 10 (MVP 통합 테스트) 기획 — 제품 로드맵 복귀. 새 GAP 3 백로그(Phase 10 후/차기 meta-phase, blocking 0)
```

## Phase 10 done (archive) — 제품 phase (MVP 통합)

`phases/archive/phase-10-mvp-integration/`

```
Status     : ✅ DONE (2026-05-31)
유형       : 제품 phase (large, ~12~15h, scope C) — 런타임 변경 有, meta detour(M0~M3) 종료 후 제품 복귀
Goal       : Phase 1~9.5 누적 MVP end-to-end 통합 검증 + P-AUX-2 agent 실구현 + 실 LLM eval mode capability(default mock) + RAG eval_rubric + golden_set 11→15 + 배포 게이트 A~G 준비
Result     : 4 Slice + entry(multi-llm 10th) + A1~A10 + MG1~MG4 + ★ behavior-preserving(기존 0 수정) + MVP end-to-end 통합 PASS(결함 0) + pytest 339→381(+42) + smoke_test_phase_10 12/12 + scenario_sim v8 36/36 + eval-run mock gate PASS(golden_set 15) + 배포 Gate A 통과
산출물     : 신규 ~10 (test_integration_mvp + smoke_test_phase_10 + brand_memory_extractor + eval/mode + rag_eval_rubric + deploy_test_gates + ADR-038 + regression_results/phase-10) + 수정 ~10 (scenario_sim v8 + eval/runner + golden_set + agent_io + plans.py additive + state docs)
Sub-agent  : S1·S2·S3 dispatch (S4 close main), 충돌 0 — P-X1 3/3 PASS
회고       : meta/retrospectives/phase-10.md
신규 패턴  : P-INTEGRATION-MVP-001 + P-CAPABILITY-DEFAULT-OFF-001 + P-BEHAVIOR-PRESERVING-001 update(제품 통합) + P-X1-EFFECT-001(60) + P-CONTRACT-FIRST-001(CC 누적 10)
Skill      : multi-llm-validation 10th + agent-io-check(P-AUX-2) + contract-change CC-008(agent_io)+CC-009(eval) + eval-design/eval-run(golden_set 확대+RAG rubric) + ai-architecture-review(P-AUX-2) + qa-check + design-review + phase-complete 10th
1 ADR / 2 CC: ADR-038(MVP 통합 scope C) / CC-008(agent_io P-AUX-2) + CC-009(eval golden_set/RAG rubric)
사용자 결정 : 2건 (범위 C 풀 / eval 실행 mock-deterministic 유지 → 실 LLM mode = capability·default off)
핵심 성과  : **P-X1 60연속 + behavior-preserving + MVP end-to-end 통합 결함 0 + P-AUX-2 brand_memory_extractor(agent 5→6) + eval golden_set 11→15 + RAG eval_rubric + 배포 Gate A 통과 + PlanCard 35/component_map 45 유지**
다음 단계  : 배포 Gate B~G (staging→알파→베타(실 LLM opt-in)→제한사용자→비용/성능→운영) / Phase 11+ (4계층 linkage / async worker / prompt A/B / 자동 promotion / 실 LLM eval default / M3 새 GAP 3) — 키·인프라 user-provided
```

## Phase 12 done (archive) — 검증 페이즈 (Validation)

`phases/archive/phase-12-validation/`

```
Status     : ✅ DONE (2026-06-02)
유형       : 검증/계획 phase (런타임 0 — 측정·문서만) — ★ behavior-preserving (운영 endpoint/agent/prompt/output_schema 0 수정, pytest 471 유지)
Goal       : MVP 출력(영상기획안) 품질·가치 실측 (구조 정확성 X) — golden_set 실 LLM eval baseline + 깊이 격차(depth gap) 정량 + human review 로 LLM-as-judge 신뢰도 대조. 산출 = Phase 13+ 확장 우선순위 데이터 근거.
Result     : Entry + 5 Slice + ★ 운영 코드 0 수정 + pytest 471 유지 + 키 0. 깊이 격차 실측(compact 0.231 vs rich 1.000 = 4.3x, 6/6 편차 0) + golden_set 15→25 + depth_actionability 차원(CC-011) + human review kit
핵심 발견  : 단순함 = **모델 한계 아니라 prompt/schema 설계** (같은 모델 gpt-4o-mini 프롬프트만으로 0.231→1.000). 결핍 10/13 feature, 다수가 출력 스키마(`Plan`) 슬롯 부재 → 확장 레버 = prompt + schema. + 88점 함정(compact 가 Critic 88점 받아도 depth 미반영)
★ S4 deferred : human review 실 채점은 deferred (kit 준비 = acceptance). 사용자 2026-06-02 실 UI(/generate)로 격차 직접 확인 → 결론 확정, kit 은 optional 보정(LLM-as-judge 신뢰도 대조) 보존
산출물     : entry 8 + validation self(11th) + golden_set 25(`eval/golden_set.md`) + depth_actionability(`eval/video_planning_eval.md` §2.A.1) + CC-011(`docs/contract_changes/2026-06-02_phase-12-s1-golden-set-depth.md`) + 깊이격차 리포트(`eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md`) + human kit(`eval/human_review/2026-06-02_phase-12-s4-review-kit.md`) + S5 종합 + retrospective + closing_notes
Sub-agent  : Entry·S1~S5 (sub-agent / main close), 충돌 0 — P-X1 PASS (운영 .py 0)
회고       : meta/retrospectives/phase-12.md
신규 패턴  : P-VALIDATION-DEPTH-GAP-001 (신규 후보 — 같은 모델 prompt/schema 격차 정량) + P-BEHAVIOR-PRESERVING-001 update(검증 phase) + P-CAPABILITY-DEFAULT-OFF-001 update(측정 전용 rich) + P-CONTRACT-FIRST-001 update(CC-011 누적 12) + P-X1-EFFECT-001 update
Skill      : eval-design(golden_set 25 + depth 차원) + eval-run(깊이 격차 측정) + contract-change(CC-011 additive) + multi-llm-validation(self 11th) + meta-retrospective(S5 종합) + phase-complete
1 CC       : CC-011 (golden_set 15→25 + depth_actionability 차원, additive)
사용자 결정 : 2건 (깊이 = 자동 eval + human review 표본, staging S4 제외 / golden_set = 확장 후 측정 ~25) + S4 실 채점 deferred (실 UI 직접 확인으로 결론 확정)
핵심 성과  : **깊이 격차 4.3x 정량 실측(편차 0) + 결론(prompt/schema 레버) + golden_set 25 + depth_actionability(CC-011) + human review kit + ★ 운영 코드 0 + behavior-preserving(pytest 471) + 키 0 + PlanCard 35/component_map 45 유지**
다음 Phase : **Phase 13 (Output Enrichment — compact→rich) — active**. 깊이 격차를 운영 출력에 반영 (gated 단계 롤아웃 + additive 스키마, 첫 의도적 출력 변경). 승계: B안 잔여(B-RES-1 cost 재조정=S6 흡수) + S4 human review 실 채점
```

## ⬛ Next phase (2026-05-31, ★ superseded — Phase 11~13 완료 후 위 "Phase 14 pending_user_decision (2026-06-03)" 블록이 현행)

```
[보존 — 2026-05-31 시점 Phase 10 직후 분기. 이후 Phase 11(LLM Gateway) + Phase 12(검증) + Phase 13(출력 확장) 완료. 현행 분기는 상단 Phase 14 블록 참조.]
Phase 1~10 + Meta-Factory detour(M0~M3) 완료. MVP end-to-end 통합 + 배포 Gate A 통과. 다음 사용자 결정 대기.

A. 배포 Gate B~G (운영 진행)
  - B Staging 배포(env/secret 주입 — ★ user-provided) → C 내부 알파(manual smoke) → D Beta(실 LLM eval opt-in) → E 제한 사용자 → F 비용/성능(cost-review) → G Production Readiness(보안 audit + RLS 운영 + SQL function)
  - 키·인프라 user-provided + 운영 단계

B. Phase 11+ (기능 확장)
  - 4계층 full linkage (plan_options/video_projects idealized schema, 누적 2회) / 사용자 데이터 자동 promotion (rag-update 두 번째) / SSE full async worker (누적 2회) / prompt A/B 인프라 / 실 LLM eval default 전환 / cost-review 정식화
  - M3 새 GAP 3 (G9 forbidden_scope 분리 / G10 risk 분해 / G11 conditional 문서화 — blocking 0, meta_factory/outputs/improvement_reports 백로그)

진입 전 권장 검토:
  - phases/archive/phase-10-mvp-integration/closing_notes.md (Phase 1~10 총괄 + baseline)
  - docs/deploy_test_gates.md (Gate A~G 통과 조건 + 현 준비 상태)
  - docs/decisions/phase_10_mvp_integration.md (ADR-038) + CC-008/CC-009
  - meta/retrospectives/phase-10.md (P-INTEGRATION-MVP-001 + P-CAPABILITY-DEFAULT-OFF-001)
```

## Phase 2~3 Hybrid UX 분기 (planned, 중간 상세화)

```
Phase 2. design.md 기반 PWA 설계 (Discovery + Quick)
  - 4계층 데이터 모델 (User → Brand → Domain → Series → Video) 화면 매핑
  - Discovery wizard 7단계 (Brand → Domain → Series → Target → Tone → Direction Summary → Generate)
  - Quick mode 흐름 (짧은 프롬프트 → 1–2 부족 정보 질문 → 한 줄 방향 승인)
  - Mode 자동 분기 규칙 (Brand/Domain/Series 컨텍스트 유무로)
  - page_map.md, component_map.md 작성

Phase 3. Next.js PWA UI 구현
  - Discovery wizard 화면 구현 (단계당 5 카드)
  - Quick mode 화면 구현
  - Direction Approval 카드 (양 모드 공통)
  - Plan 후보 3개 비교 카드
  - 진행 stepper (4단계 + 부분 결과 노출)
```

## 배포 테스트 게이트

- Deploy Test A: Local Smoke Test
- Deploy Test B: Staging 배포
- Deploy Test C: 내부 알파 테스트
- Deploy Test D: Beta Staging
- Deploy Test E: 제한 사용자 테스트
- Deploy Test F: 비용 / 성능 테스트
- Deploy Test G: Production Readiness
