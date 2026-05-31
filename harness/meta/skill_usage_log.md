# meta/skill_usage_log.md

> 🚧 Placeholder (Phase 0 진입 직후 생성. 첫 Skill 트리거부터 자동 누적 시작)

## 목적

각 Skill의 실제 트리거 빈도를 추적한다.
- 6개월 이상 트리거되지 않은 Skill → 폐기 후보
- 한 세션에서 3회 이상 트리거된 Skill → 자동화 후보 (스크립트화 검토)

## 자동 갱신 주체

- `phase-complete` Skill이 Phase 종료 시 갱신
- `meta-retrospective` Skill이 회고 시 검토

## 항목 형식

```markdown
| Skill | 첫 트리거 | 마지막 트리거 | 누적 트리거 수 | 최근 30일 | 상태 |
|---|---|---|---|---|---|
| phase-start | 2026-05-24 | 2026-05-24 | 1 | 1 | active |
| contract-change | - | - | 0 | 0 | unused |
```

## 상태 분류

- `active`: 최근 30일 내 트리거됨
- `unused`: 한 번도 트리거 안 됨
- `dormant`: 90일 이상 트리거 안 됨
- `deprecated`: 폐기 결정됨

## 인덱스

> 누적 시작: 2026-05-26 (Phase 1 완료 시점)
> Phase 2 갱신: 2026-05-27 (Phase 2 종료 시점)
> Phase 3 갱신: 2026-05-28 (Phase 3 종료 시점)
> Phase 4 갱신: 2026-05-28 (Phase 4 종료 시점)
> Phase 4.5 entry 갱신: 2026-05-28 (Slice 1 sub-agent)
> Phase 4.5 종료 갱신: 2026-05-28 (Slice 4)
> Phase 6 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 6 종료 갱신: 2026-05-29 (Slice 4)
> Phase 5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5 종료 갱신: 2026-05-29 (Slice 5 sub-agent)
> Phase 5.5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5.5 종료 갱신: 2026-05-29 (Slice 4)
> Phase 7 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 7 종료 갱신: 2026-05-29 (Slice 5)
> Phase 8 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 8 종료 갱신: 2026-05-29 (Slice 5)
> Phase 9 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 9 종료 갱신: 2026-05-31 (Slice 6)
> Phase 9.5 entry 갱신: 2026-05-31 (Slice 1 sub-agent)
> Phase 9.5 종료 갱신: 2026-05-31
> Phase M0 entry 갱신: 2026-05-31 (Slice 1 sub-agent — ★ 첫 meta-phase, multi-llm-validation formal 여덟 번째, 런타임 변경 0)

| Skill | 첫 트리거 | 마지막 트리거 | 누적 | 최근 30일 | 상태 | 비고 |
|---|---|---|---|---|---|---|
| phase-start | 2026-05-26 | 2026-05-31 | 13 | 13 | active | v1.0.0 → v1.1.0 → v1.2.0 (P2) → v1.3.0 (P-X1 §6.3 §SELF-VERIFICATION). Phase 1+2+3+4+4.5+6+5+5.5+7+8+9+9.5+**M0** 진입 (Phase M0 entry Slice 1 트리거 — 누적 13, ★ 첫 meta-phase) |
| qa-check | 2026-05-26 | 2026-05-31 | 38 | 38 | active | v1.1.0 → v1.2.0 (P3, 카테고리 11). Phase 1:8 + Phase 2:7 + Phase 3:6 + Phase 4:5 + Phase 4.5:1 + Phase 6:2 + Phase 5:2 + Phase 5.5:1 + Phase 7:1 + Phase 8:2 + Phase 9:1 + Phase 9.5:1 + **Phase M0:1** (Slice 1 entry — meta-phase 경량: 런타임 변경 0 + proposal-first + MVP 범위 위반 0 점검). 누적 38 (Phase M0 Slice 1 포함) |
| contract-change | 2026-05-26 | 2026-05-31 | 9 | 9 | active | CC-001 (Option B) + P1~P4 Skill 갱신 + P-X1 phase-start v1.3.0 + **Phase 6 Slice 2 첫 본격 실 변경 ★** (output_schema §9 canonical + §10 Body + agent_io_contract §6 Rewriter v1.1.0 + api_contract §8.3 + ADR-018/019) + **Phase 5 Slice 2 두 번째 본격 ★** (`db_schema.md` 신규 — DB schema 첫 정식 contract + 4계층 + plans + users + JSONB 컬럼) + **Phase 7 Slice 2 세 번째 본격 ★** (`rag_data_contract.md §18` 신규 — 5단계 stage enum + promotion_history + retrieval 정책 정식 등록) + **Phase 8 Slice 4 네 번째 본격 ★ (CC-003)** (`prompt_registry.md` P-001~P-008 + AUX semver 정식화 + P-007 §0–5↔0–1 adapter + `agent_io_contract.md` v1.2.0 §5 Critic v1.1.0 adapter + §8 orchestrator 중개) + **Phase 9 Slice 2 다섯 번째 본격 ★ (CC-004)** (`db_schema.md` §4.3 selected_plans 실 plans 정합 plan_id + selected_option_index 0–2 + selection_reason + §5.2 feedback_events 보강 + brand_memory prep cross-ref) + **Phase 9.5 Slice 4 여섯 번째 본격 ★ (CC-005)** (`output_schema.md §9` canonical-only + `agent_io_contract.md §5` Critic canonical-only run_critic 0–5 불변 + `db_schema.md` critic_evaluation deprecated 0–5 제거 정합) + **Phase M0 Slice 3 일곱 번째 ★ (CC-006)** (`.claude/skills/INDEX.md` harness-factory #21 Skill 등록 — Skill 도 contract 처럼 취급, INDEX §Skill 신규/변경 절차 + 키워드 충돌 검토 0 + 우선순위 표 3 관계, 런타임 0) + **Phase M2 S1·S2 여덟 번째 ★ (CC-007)** (meta_factory machinery 8 GAP **additive** 반영 — generation_workflow/architecture_patterns/domain_brief_schema/templates 4/harness_blueprint_schema. L3 contract 문서(Skill 본문 아님). proposal M1 §D → 승인 → 반영 → S3 재검증. backward-compat 0 파괴). 회귀 0 유지. 누적 11. **P-CONTRACT-FIRST-001 정신 누적 8회 (Skill·machinery 도 contract)** |
| meta-retrospective | 2026-05-26 | 2026-05-31 | 13 | 13 | active | Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 4.5 + Phase 6 + Phase 5 + Phase 5.5 + Phase 7 + Phase 8 + Phase 9 + Phase 9.5 + **Phase M0** 회고 (★ 첫 meta-phase) |
| phase-complete | 2026-05-26 | 2026-05-31 | 13 | 13 | active | v1.0.0 → v1.1.0 (P4 §1.5 smoke test) → v1.2.0 (P-X2 §1.6 변경성 시뮬 자동 게이트, Phase 4.5 entry 도입). Phase 1+2+3+4+4.5+6+5+5.5+7+8+9+9.5+**M0** 종료 (Phase M0 = **아홉 번째** 자동 게이트, scenario_simulation v7 33/33 PASS — ★ 첫 meta-phase) |
| harness-audit | 2026-05-27 | 2026-05-31 | 10 | 10 | active | audit_naming + audit_page_component 모두 자동 호출 (Phase 4 D-1 정규화 보강 + Phase 4.5 Slice 1+4 + Phase 6 Slice 1+4 + Phase 5 Slice 1+5 + Phase 5.5 Slice 4 + Phase 7 Slice 5 + Phase 8 Slice 5 + Phase 9 Slice 6 + Phase 9.5 Slice 5 + **Phase M0 Slice 3** — 0 drift + 2 intended WARN 유지) + **Phase M0 Slice 3 §3 키워드 충돌 검토** (harness-factory description ↔ 기존 20 Skill 충돌 0 — harness-audit/meta-retrospective/phase-start/contract-change/eval-run 의미 명확 구분) |
| design-review | 2026-05-27 | 2026-05-31 | 10 | 10 | active | Phase 2 Slice 6 (spec-only 첫) + Phase 3 Slice 6 (impl 두 번째 §B) + Phase 4 Slice 4 (impl 세 번째 §B) + Phase 4.5 Slice 4 (impl 네 번째 §B) + Phase 6 Slice 4 (impl 다섯 번째 §B) + Phase 5 Slice 5 (impl 여섯 번째 §B, PlanCard 17연속 무수정 정합) + Phase 7 Slice 5 (impl 일곱 번째 §B, PlanCard 19연속 + component_map 29연속 무수정 검증) + Phase 8 Slice 5 (impl 여덟 번째 §B, frontend 변경 0 — PlanCard 24연속 + component_map 34연속 무수정 검증) + Phase 9 Slice 6 (impl 아홉 번째 §B, 피드백 UI page.tsx inline — PlanCard 30연속 + component_map 40연속 무수정 + design.md 정합 PASS) + **Phase 9.5 Slice 5 (impl 열 번째 §B, frontend canonical 전환 lib/types.ts + page.tsx — PlanCard 35연속 + component_map 45연속 무수정 + design.md 정합 PASS)** |
| multi-llm-validation | 2026-05-28 | 2026-05-31 | 9 (1 informal + 8 formal) | 9 | active | Phase 4 informal GPT 검토 + Phase 4.5 entry formal self V1~V4 PASS (외부 placeholder 분리) + Phase 6 entry formal self 두 번째 V1~V5 PASS + Phase 5 entry formal self 세 번째 V1~V6 PASS (Supabase / JWT / RLS / SSE / revise_history / canonical DB) + Phase 7 entry formal self 네 번째 V1~V7 PASS (ADR-024 5단계 / chunk 512 / top-k=5 threshold=0.7 / OpenAI embedding / graceful / LLM Wiki vs RAG / hybrid 승인) + Phase 8 entry formal self 다섯 번째 V1~V7 PASS (orchestrator 추출 behavior-preserving / ProgressSink / SSE 브릿지 / Critic adapter / prompt semver / 단일 출처 / SSE best-effort) + Phase 9 entry formal self 여섯 번째 V1~V7 PASS (selection/feedback 실 plans 정합 / normalize_to_canonical wiring 회귀 0 / Brand Memory 준비 경계 / 피드백 reason PII / repo graceful / 피드백 UI wrapper / feedback→candidate 적재) + Phase 9.5 entry formal self 일곱 번째 V1~V7 PASS (eval mock-deterministic primary / golden_set markdown→구조화 파싱 / revise effect mock metric / Critic deprecated 제거 경계 run_critic 0–5 불변 NG3 / 제거 순서 / 임계값 게이트 / frontend types 정합) + **Phase M0 entry formal self ★ 여덟 번째** V1~V6 PASS (L3 Meta-Factory 도입 타당성 기존 meta 문화 정합 / 런타임 변경 0 A9 / proposal-first 자동 적용 X / meta-phase 격리 제품 phase 오염 X / harness-factory Skill 키워드 scoping / blueprint 실측 golden_set 11 + .claude/agents 부재 + ADR-001~034 + P-X1 47). **P-VALIDATION-FORMAL-001 정식 패턴 확정 (8회 누적 — Phase M0 ★ 첫 meta-phase 적용)** |
| **agent-io-check** | **2026-05-29** | **2026-05-31** | **6** | 6 | **active** | Phase 6 Slice 4 첫 정식 트리거 (Rewriter v1.1.0 + Critic canonical 정합 PASS) + Phase 5 Slice 5 두 번째 회귀 검증 (Phase 6 baseline 유지 PASS) + Phase 7 Slice 5 세 번째 회귀 검증 (agents/rag.py Phase 1 baseline 호환 + Phase 7 RAG Lite 통합 wrapper) + Phase 8 Slice 5 네 번째 회귀 검증 (agent_io_contract §5 v1.1.0 + adapter ↔ critic.py drift 0 + §8 orchestrator 중개 검증, 회귀 0) + Phase 9 Slice 3 + Slice 6 다섯 번째 회귀 검증 (normalize_to_canonical wiring 후 agent_io_contract §5 Critic v1.1.0 adapter ↔ critic.py + moa_orchestrator critic step wiring canonical 정합 drift 0, deprecated 0–5 병행 회귀 0) + **Phase 9.5 Slice 4 + Slice 5 여섯 번째 회귀 검증** (Critic deprecated 0–5 Full 제거 후 agent_io_contract §5 **canonical-only** ↔ critic.py drift 0, run_critic 0–5 + normalize_to_canonical 불변) |
| **eval-design** | **2026-05-31** | **2026-05-31** | **1 ★ 첫 정식** | 1 | **active** | **Phase 9.5 Slice 1 entry ★ 첫 정식 트리거** — 절차 7단계 적용 (현재 평가 자산 로드 → 부족 차원 식별 → metric 정의 → golden_set executable format → eval-run 명세 → 임계값 게이트). 결과: ADR-033 §eval-design 통합 — golden_set_loader format (golden_set.md ` ```yaml ` 블록 GS- prefix 필터 → {id, input, expected_properties}, 단일 출처) + 채점 차원 (schema 준수 100% + structural: plan 3개/hook 존재/flow 비트/광고 단어 부재/차단 단어, 실 LLM 8차원은 mode flag) + revise effect metric (attempt별 canonical overall_score 0–1 delta, mock) + 임계값 게이트 (schema 100% / 점수 ±0.3 / 광고 >5% fail / 차단 단어 >0% fail). 후속: Slice 2~3 eval-run 첫 정식 실행 |
| **eval-run** | **2026-05-31** | **2026-05-31** | **1 ★ 첫 정식** | 1 | **active** | **Phase 9.5 Slice 2~3 ★ 첫 정식 트리거** — golden_set 회귀 실행 (mock-deterministic, CI 가능 비용 0) + revise effect eval + 임계값 게이트 (eval-run §6: schema 100% / 점수 ±0.3 / 광고 / 차단 단어) + regression_results 출력. 결과: `eval/regression_results/phase-9.5_baseline.md` (schema_rate 1.0 / pass_rate 1.0 / gate=pass) + `phase-9.5_pre-removal.md` + `phase-9.5_post-removal.md` (revise mean_delta 0.092 / improved 0.6 / regressed 0.2). **Critic deprecated 0–5 Full 제거 안전망** (제거 전/후 canonical-only 품질 동일 입증). eval-design Slice 1 설계 후 실행 — **eval-design + eval-run 둘 다 첫 정식** |
| **rag-design** | **2026-05-29** | **2026-05-29** | **1 ★ 첫 정식** | 1 | **active** | **Phase 7 Slice 1 entry ★ 첫 정식 트리거** — 절차 8단계 모두 적용 (현재 자산 로드 → retrieval/metadata/chunking/quality_filter 점검 → 새 소스 검토 → LLM Wiki vs RAG 분리 → 변경 제안서). 결과: ADR-025 (RAG architecture — chunking 512 tokens + overlap 50 + embedding text-embedding-3-small + retrieval pgvector cosine top-k=5 threshold=0.7 + LLM Wiki vs RAG 분리 RAG > LLM Wiki 우선순위 + graceful 5종 marker). 후속: Slice 2 contract-change (rag_data_contract.md §18) |
| **rag-update** | **2026-05-29** | **2026-05-29** | **1 ★ 첫 정식** | 1 | **active** | **Phase 7 Slice 4 ★ 첫 정식 트리거** — 5단계 승격 절차 강제 적용 (Skill 절차 따름): 후보 → 품질 필터 → 평가 → 승인 → 승격. 결과: `meta/rag_updates/2026-05-29_phase-7-initial-promotion.md` (initial promotion procedure baseline). 후속: Phase 11+ 사용자 데이터 자동 promotion 두 번째 트리거 예정 (ADR-024 §A 확대 지점) |
| **prompt-version-review** | **2026-05-29** | **2026-05-29** | **1 ★ 첫 정식 (Slice 1 분석 + Slice 4 적용 통합)** | 1 | **active** | **Phase 8 Slice 1 entry ★ 첫 정식 트리거 (분석) + Slice 4 적용** — 절차 7단계 적용 (contract-change 선행 + semver 부여 + golden_set 회귀 계획 + 활성화 + 모니터링/rollback baseline). 대상: P-007 Critic 0–5↔0–1 drift 분석 + conservative adapter (사용자 결정 — Phase 6 canonical 불변 + P-007 prompt 0–5 유지 + 코드 0–1 정규화 + P-007 v1.0.0→v1.1.0 minor). 결과: ADR-029 통합. **Slice 4 적용 완료** (P-007 v1.1.0 + critic.py normalize_to_canonical adapter + test_prompt_registry_consistency, CC-003). NG8 (Phase 6/5/7 defer 누적 3회) 해소 |
| **ai-architecture-review** | **2026-05-29** | **2026-05-29** | **2 ★ 첫 정식 + 회고 검토** | 2 | **active** | **Phase 8 Slice 1 entry ★ 첫 정식 트리거** — 절차 7단계 적용 (입력 자료 로드 + MOA 흐름 점검 + 정책 준수 검사 + 확장성/리스크 + multi-llm-validation 보강 + 보고 + 후속 라우팅). 대상: MOA orchestration 설계 (4 agent 분리 Intent/Planning/Critic/Rewriter + orchestrator 중개 moa_policy §2 정합 + cost/fallback policy 보존 + agent 격리 §7). 결과: ADR-027 §ai-architecture-review 결과 통합 (god-function → service layer 추출 behavior-preserving). + **Phase 8 Slice 5 회고 검토 (두 번째)** — MOA orchestration 추출 후 구조 PASS (orchestration/ 격리 + ProgressSink + progress_store 브릿지 + Critic conservative adapter, moa_policy §2 중개 정합 회복) |
| context-compact | - | - | 0 | 0 | unused | Phase 1~7 컨텍스트 충분 |
| phase-review | - | - | 0 | 0 | unused | Phase 중간 health check 시 활성화 |
| bug-triage | - | - | 0 | 0 | unused | 버그 발견 시 활성화 |
| **security-review** | **2026-05-29** | **2026-05-29** | **3 ★ Phase 5 첫 정식 + final + Phase 9 두 번째 정식** | 3 | **active** | **Phase 5 Slice 1 entry 첫 정식 트리거** — T1~T6 위협 모델 + §4 영역 1~10 점검. **Phase 5 Slice 5 final 두 번째 트리거** — Slice 2~4 실 구현 verify (T1 httpOnly cookie PASS / T2 RLS 0003 PASS / T4 Origin 검증 PASS). **Phase 9 Slice 1 entry ★ 두 번째 정식 트리거** — 피드백 reason PII (T1 저장 전 마스킹) + reject 사유 (T2) + feedback_events/selected_plans RLS user 격리 (T3) + GET /plans/{id}/feedback 본인 권한 (T4) + feedback→candidate 적재 quality_filter PII (T5) + SQL injection baseline (T6) + 영역 1~10 (4 PARTIAL → Slice 2~4 후 PASS). **P-SECURITY-REVIEW-001 강화 (Phase 5 + Phase 9 — 보안 영향 phase entry 정식 트리거 패턴)** |
| cost-review | - | - | 0 | 0 | unused | Phase 9+ 비용 본격 추적 시 |
| **harness-factory** | **2026-05-31** | **2026-05-31** | **3 (등록 1 + ★ 첫 실 트리거 2: Phase M1 S1·S2)** | 3 | **active** | **Phase M0 Slice 3 ★ 신규 등록 (#21, 키워드 scoped)** — L3 Meta-Harness Factory(`meta_factory/`) 진입점. domain_brief → harness blueprint 초안 + agent·skill·contract·eval scaffold 제안 + 기존 하네스 충돌 분석. ★ **proposal-only** — generated harness 자동 active 전환 X (factory_contract 규칙 7), 기존 AGENTS/CLAUDE/PROJECT_STATE/contracts/Skill 직접 수정 X (규칙 2/4/5/6). 키워드(하네스 blueprint/meta_factory/harness scaffold/도메인 하네스 생성)는 harness-audit/meta-retrospective/phase-start 와 충돌 0. **★ Phase M1 첫 실 트리거 (2026-05-31)** — S1(generation_workflow 11단계 → 팟캐스트 blueprint dbe43c5) + S2(validation_workflow 6검증 PASS 5/PENDING 1 + with/without 6지표 + GAP 8 83fc1ac). 산출물 전부 `meta_factory/outputs/TEST/` 격리 (MG1 — TEST/ 외 0줄), generated harness 는 6검증 PASS 에도 active 아님 (규칙 7). payoff deferred 첫 실증. **★ Phase M2 S3 두 번째 실 트리거 (2026-05-31)** — 개선 machinery 로 M1 TEST 재검증(validation_workflow 6검증 재실행 + 8 GAP before/after) + **★ Phase M3 S1·S2 세 번째 실 트리거 (2026-05-31)** — 개선 machinery 로 이질 도메인(재무) 생성+검증(범용성 2차, 범용 강함 + M2 개선 유효 7/부분 1). 누적 5 (등록 1 + M1 2 + M2 1 + M3 1). 등록 = CC-006 (M0 Slice 3) |

**Phase 1 사용 요약**: 4 Skill 활용 (phase-start + qa-check 8회 + contract-change + meta-retrospective). 16 Skill은 아직 unused.

**Phase 2 사용 요약**: 6 Skill 활용 (phase-start + qa-check 7회 + meta-retrospective + phase-complete + harness-audit + ★ design-review 첫 사용). Phase 1 누적 + Phase 2 = 7 Skill 활성화, 13 unused.

**Phase 3 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check 6회 + contract-change (P-X1 적용) + meta-retrospective + phase-complete + harness-audit (audit_page_component.ps1 신규) + design-review 두 번째 사용 — impl 절차 §B). Phase 1~3 누적 = 7 Skill 활성화, 13 unused.

**Phase 4 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check 5회 + meta-retrospective + phase-complete + harness-audit + design-review 세 번째 — impl §B + ★ multi-llm-validation 첫 사용 — informal GPT 검토). Phase 1~4 누적 = 8 Skill 활성화, 12 unused. **multi-llm-validation 첫 informal 트리거 — Phase 5+ 정식 호출 권장**.

**Phase 4.5 사용 요약**: 7 Skill 활용 (phase-start v1.3.0 + qa-check + meta-retrospective + phase-complete v1.2.0 ★ + harness-audit + design-review 네 번째 사용 + multi-llm-validation **formal** ★ 첫 정식 트리거). Phase 1~4.5 누적 = 9 Skill 활성화, 11 unused. **multi-llm-validation formal + P-X2 자동 게이트** 첫 트리거.

**Phase 6 사용 요약**: 9 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change ★ 본격 + multi-llm-validation formal 두 번째 + agent-io-check ★ 첫 정식 + harness-audit + design-review + meta-retrospective + phase-complete v1.2.0 두 번째). Phase 1~6 누적 = 10 Skill active, 10 unused. **agent-io-check + contract-change 본격 트리거** (Phase 5 진입 전 baseline 완성).

**Phase 5 사용 요약**: 11 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change (db_schema.md, Slice 2) + multi-llm-validation **formal 세 번째 (Slice 1)** + **security-review ★ 첫 정식 + 두 번째 final** (Slice 1 + Slice 5) + agent-io-check 두 번째 회귀 (Slice 5) + harness-audit (Slice 1+5) + design-review (Slice 5) + meta-retrospective (Slice 5) + phase-complete v1.2.0 세 번째 (Slice 5)). Phase 1~5 누적 = **12 Skill 활성화**, 8 unused. **security-review + contract-change 본격 안정화**.

**Phase 5 Slice 5 종료 갱신**: 7 Skill 추가 활용 (Slice 1 4 + Slice 5 7 = 누적 11) — contract-change 두 번째 + security-review 두 번째 final + agent-io-check 회귀 + harness-audit + design-review + meta-retrospective + phase-complete v1.2.0 세 번째. Phase 5 종료 의무 완료.

**Phase 5.5 사용 요약**: 5 Skill 활용 (phase-start v1.3.0 + qa-check + harness-audit + meta-retrospective + phase-complete v1.2.0 네 번째). Phase 1~5.5 누적 = **12 Skill 활성화**, 8 unused.

이번 Slice 미사용 Skill (의도된):
- contract-change (ADR만 신규, contract 직접 변경 없음)
- security-review (Phase 5에서 완료, 보안 변경 없음)
- agent-io-check (agents/* 변경 없음)
- design-review (frontend 변경 없음)
- multi-llm-validation (Phase 4.5/6/5에서 형식 정착, Phase 5.5는 강화 작업이므로 형식 재사용)

**Phase 7 사용 요약**: 11 Skill 활용 (phase-start v1.3.0 + qa-check + contract-change (rag_data_contract.md §18, Slice 2) + multi-llm-validation formal 네 번째 (Slice 1) + **rag-design ★ 첫 정식 (Slice 1)** + **rag-update ★ 첫 정식 (Slice 4)** + agent-io-check 세 번째 회귀 (Slice 5) + harness-audit (Slice 5) + design-review 일곱 번째 §B (Slice 5) + meta-retrospective (Slice 5) + phase-complete v1.2.0 다섯 번째 자동 게이트 (Slice 5)). Phase 1~7 누적 = **14 Skill 활성화**, 6 unused. **rag-design + rag-update 둘 다 첫 정식 트리거** (Phase 7 RAG Lite baseline 확립).

Phase 7 Slice 5 미사용 Skill (의도된):
- security-review (Phase 5에서 완료, RAG 보안은 quality_filter로 흡수)
- eval-design / eval-run (Phase 9+ eval-run Skill 정식화 시 동시 활성)
- prompt-version-review (Phase 8+ MOA Lite 본격화 시 — NG8)
- ai-architecture-review (Phase 8 MOA Lite 진입 시 권장)
- context-compact (Phase 1~7 컨텍스트 충분)
- phase-review (Phase 중간 health check 시 활성화)
- bug-triage (버그 발견 시)
- cost-review (Phase 9+)

**Phase 8 사용 요약 (확정, Slice 5 종료)**: 10 Skill 활용 (phase-start v1.3.0 10번째 (Slice 1) + qa-check (Slice 1 entry + Slice 5 close) + multi-llm-validation **formal 다섯 번째 (Slice 1)** + **ai-architecture-review ★ 첫 정식 (Slice 1) + 회고 검토 (Slice 5)** + **prompt-version-review ★ 첫 정식 (Slice 1 분석 + Slice 4 적용)** + contract-change CC-003 (Slice 4 — prompt_registry semver + agent_io_contract v1.2.0) + agent-io-check 네 번째 회귀 (Slice 5) + harness-audit (Slice 5) + design-review 여덟 번째 §B (Slice 5 frontend 변경 0) + meta-retrospective (Slice 5) + phase-complete v1.2.0 여섯 번째 자동 게이트 (Slice 5, scenario_simulation v4 20/20 PASS)). Phase 1~8 누적 = **16 Skill 활성화** (ai-architecture-review + prompt-version-review 첫 정식 전환), 4 unused. **ai-architecture-review + prompt-version-review 둘 다 첫 정식 트리거** (Phase 8 MOA Lite 본격 baseline 확립).

Phase 8 Slice 5 미사용 Skill (의도된):
- security-review (Phase 5 완료, Phase 8 보안 변경 0 — SSE Origin 검증 유지)
- rag-design / rag-update (Phase 7 완료, Phase 8 RAG 변경 0 — behavior-preserving)
- eval-design / eval-run (Phase 9+ eval-run Skill 정식화 시)
- context-compact (컨텍스트 충분)
- phase-review (Phase 중간 health check 시)
- bug-triage (버그 발견 시)
- cost-review (Phase 9+ 비용 본격 추적 시)

Phase 8 Slice 1 entry 미사용 Skill (의도된, Slice 2~5에서 활성):
- contract-change (Slice 4 — prompt_registry + agent_io_contract 실 변경)
- agent-io-check (Slice 2 orchestrator + Slice 4 prompt 정합 + Slice 5 회귀)
- harness-audit / design-review / meta-retrospective / phase-complete (Slice 5 close)
- security-review (Phase 5 완료, Phase 8 보안 변경 0 — SSE Origin 검증 유지)
- eval-design / eval-run (Phase 9+)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)

**Phase 9 사용 요약 (확정, Slice 6 종료)**: 11 Skill 활용 (phase-start v1.3.0 11번째 (Slice 1) + qa-check (Slice 1 entry — MVP 범위/실 plans 정합/PII 점검) + multi-llm-validation **formal 여섯 번째 (Slice 1, V1~V7 PASS)** + **security-review 두 번째 정식 (Slice 1 — 피드백 reason PII T1~T6)** + contract-change CC-004 (Slice 2 — db_schema.md feedback/selection 실 plans 정합) + agent-io-check 다섯 번째 회귀 (Slice 3 normalize wiring 정합 + Slice 6 회귀) + harness-audit (Slice 6) + design-review 아홉 번째 §B (Slice 6 피드백 UI page.tsx inline — PlanCard 30연속 + component_map 40연속) + meta-retrospective (Slice 6) + phase-complete v1.2.0 **일곱 번째** 자동 게이트 (Slice 6, scenario_simulation v5 25/25 PASS)). Phase 1~9 누적 = **16 Skill 활성화**, 4 unused. **security-review 두 번째 정식 트리거** (Phase 5 첫 정식 + final 에 이은 — P-SECURITY-REVIEW-001 강화: 보안 영향 phase entry 패턴 누적 2 phase) + **contract-change CC-004 (P-CONTRACT-FIRST-001 누적 5회)**.

Phase 9 Slice 6 종료 미사용 Skill (의도된):
- rag-design / rag-update (Phase 7 완료, Phase 9 feedback→candidate 적재 경로만 신규 — Skill 절차 비호출)
- eval-design / eval-run (Phase 9.5+ — Critic deprecated 0–5 완전 제거 NG3 + revise effect eval)
- prompt-version-review / ai-architecture-review (Phase 8 완료, Phase 9 변경 0 — normalize wiring은 Phase 8 helper 재사용)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)

**Phase 9.5 사용 요약 (확정, Slice 5 종료)**: 10 Skill 활용 (phase-start v1.3.0 12번째 (Slice 1) + qa-check (Slice 1 entry — MVP 범위/eval mock-deterministic/Critic deprecated 제거 경계 점검) + multi-llm-validation **formal 일곱 번째 (Slice 1, V1~V7 PASS)** + **eval-design ★ 첫 정식 (Slice 1 — golden_set executable format + 채점 차원 + revise effect metric + 임계값 게이트 → ADR-033 §eval-design)** + **eval-run ★ 첫 정식 (Slice 2~3 — mock-deterministic golden_set 회귀 + revise effect + 임계값 게이트 + regression_results, Critic deprecated 제거 안전망)** + contract-change CC-005 (Slice 4 — output_schema §9 canonical-only + agent_io_contract §5 + db_schema critic_evaluation deprecated 0–5 제거) + agent-io-check 여섯 번째 회귀 (Slice 4 canonical-only 정합 + Slice 5 회귀) + design-review 열 번째 §B (Slice 5 frontend canonical 전환 — PlanCard 35연속 + component_map 45연속) + meta-retrospective (Slice 5) + phase-complete v1.2.0 **여덟 번째** 자동 게이트 (Slice 5, scenario_simulation v6 30/30 PASS)). Phase 1~9.5 누적 = **18 Skill 활성화** (eval-design + eval-run 첫 정식 전환), 3 unused. **eval-design + eval-run Skill 둘 다 첫 정식 트리거** (Phase 9.5 eval-run 정식화 baseline 확립) + **contract-change CC-005 (P-CONTRACT-FIRST-001 누적 6회)**.

Phase 9.5 Slice 5 종료 미사용 Skill (의도된):
- prompt-version-review / ai-architecture-review (run_critic 0–5 prompt 불변 NG3 — bump 없음, MOA 구조 변경 0)
- rag-design / rag-update (RAG eval_rubric Phase 10+ NG1 — Phase 9.5 RAG 변경 0)
- security-review (Phase 9 완료, Phase 9.5 보안 변경 0)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)

**Phase M0 사용 요약 (Slice 1 entry — ★ meta-phase, 런타임 변경 0)**: 3 Skill 활용 (phase-start v1.3.0 13번째 (Slice 1, ★ 첫 meta-phase 진입) + qa-check (Slice 1 entry — meta-phase 경량: 런타임 변경 0 + proposal-first + MVP 범위 위반 0) + multi-llm-validation **formal 여덟 번째 (Slice 1, V1~V6 PASS — L3 도입 타당성/런타임0/proposal-first/meta-phase/Skill scoping/blueprint 실측)**). Phase 1~M0 누적 = **18 Skill 활성화**, 3 unused. **★ multi-llm-validation 첫 meta-phase 적용** (P-VALIDATION-FORMAL-001 8회 누적). harness-factory Skill 신규 등록은 Slice 3 (proposal-only, 키워드 scoped, 트리거 0 — proposal-only Skill).

Phase M0 Slice 1 entry 미사용 Skill (의도된, Slice 2~3 또는 해당 없음):
- contract-change (Slice 3 — harness-factory Skill INDEX 등록 CC-006, Skill 도 contract 처럼 취급)
- harness-audit (Slice 3 — harness-factory 키워드 충돌 검토)
- meta-retrospective / phase-complete (Slice 3 close)
- eval-design / eval-run (런타임 0 — eval 변경 없음)
- agent-io-check / design-review (런타임 0 — agents/frontend 변경 없음)
- security-review / prompt-version-review / ai-architecture-review / rag-design / rag-update (런타임 0 — 해당 없음)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)

**Phase M0 사용 요약 (확정, Slice 3 종료 — ★ 첫 meta-phase, 런타임 변경 0)**: 7 활성 Skill + harness-factory 신규 등록 (phase-start v1.3.0 13번째 (Slice 1, ★ 첫 meta-phase) + qa-check (Slice 1 entry — meta-phase 경량) + multi-llm-validation **formal 여덟 번째 (Slice 1, V1~V6 PASS)** + contract-change **일곱 번째 본격 CC-006 (Slice 3 — INDEX Skill 등록, Skill 도 contract 처럼 취급)** + harness-audit (Slice 3 — §3 harness-factory 키워드 충돌 검토 충돌 0) + meta-retrospective (Slice 3) + phase-complete v1.2.0 **아홉 번째** 자동 게이트 (Slice 3, scenario_simulation v7 33/33 PASS) + **harness-factory ★ 신규 등록 (proposal-only, 트리거 0)**). Phase 1~M0 누적 = **18 Skill 활성화 + harness-factory 등록(proposal-only, 트리거 0) = 19 Skill 존재**. ★ **multi-llm-validation 첫 meta-phase 적용** (P-VALIDATION-FORMAL-001 8회 누적). ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 (A9). harness-factory 실 트리거는 2nd 하네스 / generated harness 생성 시점 (payoff deferred).

Phase M0 Slice 3 종료 미사용 Skill (의도된, 런타임 0 — 해당 없음):
- eval-design / eval-run (런타임 0 — eval 변경 없음. validation_workflow 검증 5 는 eval-run 위임 cross-ref 만)
- agent-io-check / design-review (런타임 0 — agents/frontend 변경 없음, PlanCard·component_map 0줄)
- security-review / prompt-version-review / ai-architecture-review / rag-design / rag-update (런타임 0 — 해당 없음)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)

> Phase 6 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 6 종료 갱신: 2026-05-29 (Slice 4)
> Phase 5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5 종료 갱신: 2026-05-29 (Slice 5 sub-agent)
> Phase 5.5 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 5.5 종료 갱신: 2026-05-29 (Slice 4)
> Phase 7 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 7 종료 갱신: 2026-05-29 (Slice 5)
> Phase 8 entry 갱신: 2026-05-29 (Slice 1 sub-agent)
> Phase 8 종료 갱신: 2026-05-29 (Slice 5)
> Phase 9 entry 갱신: 2026-05-29 (Slice 1)
> Phase 9 종료 갱신: 2026-05-31
> Phase 9.5 entry 갱신: 2026-05-31 (Slice 1 sub-agent — eval-design ★ 첫 정식)
> Phase 9.5 종료 갱신: 2026-05-31 (Slice 5 — eval-run ★ 첫 정식 + contract-change CC-005 + phase-complete 여덟 번째 자동 게이트)
> Phase M0 entry 갱신: 2026-05-31 (Slice 1 sub-agent — ★ 첫 meta-phase, L3 Meta-Factory, multi-llm-validation formal 여덟 번째 V1~V6 PASS, 런타임 변경 0 A9)
> Phase M0 종료 갱신: 2026-05-31 (Slice 3 — harness-factory ★ 신규 등록 #21 proposal-only + contract-change CC-006 (INDEX Skill 등록) + harness-audit 키워드 충돌 검토 0 + phase-complete 아홉 번째 자동 게이트 (scenario_sim v7 33/33). Skill 20 → 21. ★ FastAPI/Next.js/Supabase 런타임 변경 0줄 A9. P-X1 50연속)
> Phase M1 종료 갱신: 2026-05-31 (S1·S2 — harness-factory ★ 첫 실 트리거 (Meta-Factory dry-run, 팟캐스트 도메인) + meta-retrospective (phase-M1) + ADR-036. 산출물 전부 outputs/TEST/ 격리 — MG1 (TEST/ 외 0줄) + A9 (런타임 0). 6검증 PASS 5/PENDING 1, GAP 8. Skill 21 유지 (신규 0). P-X1 52연속. ★ doc-sync 는 dry-run 과 별도 commit (GPT 보완 ③). phase-complete/scenario_sim 미실행 — dry-run meta-phase 경량 close)
> Phase M2 종료 갱신: 2026-05-31 (S1·S2·S3 — contract-change ★ 여덟 번째 본격 CC-007 (machinery 8 GAP additive 반영) + harness-factory 두 번째 실 트리거 (S3 재검증) + multi-llm-validation formal 아홉 번째 (V1~V5) + meta-retrospective (phase-M2) + ADR-037. machinery 7파일 additive + 재검증 outputs/TEST/. 백로그 8→0 (addressed 7 + expressible 1). ★ A9 런타임 0 + additive-only backward-compat. P-X1 55연속. Skill 21 유지. self-improvement loop 완주 M0→M1→M2)
> 검증5 표본 갱신: 2026-05-31 (203ced2 — eval-run 표본 mock-deterministic, podcast 검증5 PENDING-BY-DESIGN → measured baseline, G4 applies_when 실작동. outputs/TEST/ 격리 + A9. 실 LLM 미해당)
> Phase M3 종료 갱신: 2026-05-31 (S1·S2 — harness-factory ★ 세 번째 실 트리거 (이질 도메인 재무 dry-run, 범용성 2차) + meta-retrospective (phase-M3). 범용 강함(미디어 편향 0) + M2 개선 유효 7/부분 1/부적합 0 + 새 GAP 3 (전부 minor/nice-to-have → 백로그 improvement_reports). ★ machinery 0줄(개선본 읽기만) + A9 + MG1. P-X1 57연속. 분기 = Phase 10 직행)

**Phase M3 사용 요약 (이질 도메인 dry-run — 범용성 2차 검증)**: 2 활성 Skill (harness-factory ★ 세 번째 실 트리거 (S1 generation + S2 validation, 재무 도메인) + meta-retrospective (doc-sync 회고)). Phase 1~M3 누적 = **19 Skill active**. ★ **harness-factory 세 번째 실 트리거** (M1 인접 생성 → M2 재검증 → M3 이질 생성·검증) — Meta-Factory 도메인 범용성(인접·이질) 입증. machinery 0줄 변경(개선본 읽기만), 새 GAP 3은 즉시 반영 X(백로그). dry-run meta-phase 경량 — phase-start/qa-check/phase-complete/scenario_sim/audit/multi-llm 미트리거 (M2 개선 이미 검증됨, dry-run). 분기 권고 = Phase 10 직행 (blocking 0).

Phase M3 미사용 Skill (의도된, dry-run meta-phase — 런타임 0):
- contract-change (machinery 0 변경 — 새 GAP 은 백로그만, 반영 시 별도 CC)
- multi-llm-validation (M2 개선 이미 9번째 formal 검증 — M3 는 그 적용 dry-run, 신규 formal 불요)
- eval-run/eval-design (검증5 절차 적용성 — pending-by-design, 실측은 검증5 표본 203ced2 별도)
- agent-io-check/design-review/security-review/prompt-version-review/ai-architecture-review/rag-design/rag-update (런타임/agents/frontend/product contract 0)
- phase-start/qa-check/phase-complete (dry-run 경량 — entry main + close 별도 doc-sync)
- context-compact/phase-review/bug-triage/cost-review (해당 없음)

**Phase M2 사용 요약 (Meta-Factory GAP Remediation — machinery 개선)**: 4 활성 Skill (contract-change ★ 여덟 번째 본격 CC-007 (S1·S2 machinery 8 GAP) + harness-factory 두 번째 실 트리거 (S3 재검증) + multi-llm-validation formal 아홉 번째 (entry V1~V5 PASS) + meta-retrospective (doc-sync 회고)). Phase 1~M2 누적 = **19 Skill active** (harness-factory 실 트리거 유지). ★ **contract-change 가 machinery(L3 contract) 변경으로 확장** (CC-007 — Skill 본문도 machinery 문서도 contract 처럼 취급, P-CONTRACT-FIRST-001 누적 8회). ★ **multi-llm-validation 아홉 번째** (P-VALIDATION-FORMAL-001 — M0 meta-phase 도입 → M2 machinery 변경 영역 확장). ★ **harness-factory 두 번째 실 트리거** (M1 dry-run 생성 → M2 재검증). self-improvement loop 완주 (M0→M1→M2).

Phase M2 미사용 Skill (의도된, machinery 개선 — 런타임 0):
- eval-run / eval-design (재검증5 는 절차 적용성 — pending-by-design 으로 표현, 실 eval 미실행)
- agent-io-check / design-review / security-review / prompt-version-review / ai-architecture-review / rag-design / rag-update (런타임/agents/frontend/product contract 0 — 해당 없음)
- phase-start / qa-check / phase-complete (meta-phase 경량 — entry main 직접 + close 별도 doc-sync, scenario_sim/audit 미실행 — machinery 문서 변경, 런타임 0)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)

**Phase M1 사용 요약 (Meta-Factory dry-run — ★ harness-factory 첫 실 트리거)**: 2 활성 Skill (harness-factory ★ 첫 실 트리거 (S1 generation + S2 validation) + meta-retrospective (doc-sync 회고)). Phase 1~M1 누적 = **18 Skill 활성화 + harness-factory 실 트리거 전환 = 19 Skill active**. ★ harness-factory 가 M0 등록(proposal-only, 트리거 0)에서 M1 **첫 실 트리거**로 전환 — payoff deferred 의 첫 실증 (generation_workflow + validation_workflow 실행). 산출물 전부 outputs/TEST/ 격리 (MG1) — generated harness 6검증 PASS 에도 active 아님 (factory_contract 규칙 7). dry-run meta-phase 경량 — phase-start/qa-check/phase-complete/scenario_sim/audit 미트리거 (entry 는 main 세션 직접 작성, dry-run 은 sub-agent outputs only, close 는 별도 doc-sync). multi-llm-validation 미생성 (dry-run — M0 8회 formal 유지).

Phase M1 미사용 Skill (의도된, dry-run meta-phase — 런타임 0 / outputs/TEST/ 격리):
- eval-run / eval-design (검증5 는 절차 적용 가능성만 — 실 eval 미실행, eval-run §3~§6 cross-ref 위임)
- contract-change (machinery 0줄 변경 — GAP 보완은 proposal-only, 실 변경 시 별도 contract-change)
- agent-io-check / design-review / security-review / prompt-version-review / ai-architecture-review / rag-design / rag-update (런타임/agents/frontend 0 — 해당 없음)
- phase-start / qa-check / phase-complete (dry-run meta-phase 경량 — entry main 직접 + close 별도 doc-sync)
- context-compact / phase-review / bug-triage / cost-review (해당 없음)
