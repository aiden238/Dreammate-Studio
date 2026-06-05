# HIP-006~010 슬라이스 실행 플랜 (하네스 자기개선 로드맵)

> 위치: `meta/improvement_roadmap_hip006-010.md`
> 출처: `meta/audits/2026-06-05.md` (harness-audit 최초 완주) + `meta/harness_improvement_proposals.md` HIP-006~010
> 상태: 2026-06-05 수립. ★ self_improvement_loop §1.5 "반영" 단계 — 승인된 HIP를 slice 단위로 집행.
> 원칙: 하네스 규율 정합 — slice 작게 / 검증가능 / behavior-preserving(gated+additive) / proposal-first 결정은 사용자 게이트.

---

## 0. 한 줄

audit가 진단한 "현실 접지선 부재"를 HIP-006~010으로 메운다. 16 slice를 **의존성·레버리지** 순 4 wave로 집행하되, **코드/문서로 지금 가능한 것**과 **ops/사람이 필요한 것**을 분리한다.

범례: 🟢 지금 가능(코드/문서) · 🟡 코드 일부+ops/키 필요 · 🔴 사람/외부(handoff) · ✅ 완료

---

## 1. 슬라이스 표 (HIP × slice)

### HIP-006 텔레메트리 (P0) — 데이터 substrate
| slice | 내용 | 산출물 | 수락 | 구분 |
|---|---|---|---|---|
| 006-S1 | agent_io 발신기 + gateway 배선 | observability/agent_io_log.py, config flag | pytest 779→784, gated | ✅ 완료 |
| 006-S2 | cost-review reader/aggregator (JSONL→snapshot) | observability/cost_report.py + test + eval/cost_snapshots 부활 | 합성 JSONL→집계 정확 + md 렌더 | 🟢 |
| 006-S3 | 운영 승격: flag ON staging + agent_io_logs DB write + prompt_id/user_id passthrough | gateway/agent passthrough(코드) | flag ON 시 1행/호출, DB행 적재 | 🟡(passthrough 🟢 / DB·staging ops) |

### HIP-007 품질 접지 (P0) — 측정도구 신뢰
| slice | 내용 | 산출물 | 수락 | 구분 |
|---|---|---|---|---|
| 007-S1 | critic 낙관편향 보정 (adversarial/calibrated 채점, gated) | critic.py + prompt_registry P-007 bump + test | 얕은 plan ON-mode 점수 하락 단언 | 🟢 (prompt-version-review) |
| 007-S2 | real-LLM eval 정식 트리거 경로(mock 외) + regression_results | eval runner real-mode entrypoint + 리포트 | mock 회귀 불변 + real-mode 경로 존재 | 🟡(경로 🟢 / 실행=키 ops) |
| 007-S3 | human blind 채점 N=5 (kit 존재) | eval/human_review 채점 결과 | N≥5 채점 + critic↔human 괴리 측정 | 🔴 handoff(사람) |

### HIP-008 운영 도달성 (P1) — 만든 것이 쓰이게
| slice | 내용 | 산출물 | 수락 | 구분 |
|---|---|---|---|---|
| 008-S1 | "done" 정의 강화 (reachability acceptance) | qa-check/phase-complete SKILL + (contract-change) | acceptance에 도달성 항목 추가 | 🟢 |
| 008-S2 | match_approved_knowledge SQL function 정의 | db/migrations/000N_match_func.sql | RAG retrieval graceful→실동작 경로 | 🟡(SQL 🟢 / Supabase 적용 ops) |
| 008-S3 | PlansRepo 영속 (in-memory 탈피) | repositories/plans_repo persist 경로 | 재시작 후 plan 영속(코드) | 🟡(코드 🟢 / 실영속 DB ops) |
| 008-S4 | 홈/네비 진입 (AppShell + /new 링크) | apps/web AppShell + 홈 링크 | 홈→위저드 도달 경로 렌더 | 🟢 frontend |

### HIP-009 메타-메타 루프 (P1) — ★ meta/factory reflexive
| slice | 내용 | 산출물 | 수락 | 구분 |
|---|---|---|---|---|
| 009-S1 | 정기 트리거 + meta/audits 운영 명문화 | self_improvement_loop §5 + harness-audit cadence | 트리거 주기·산출 경로 명문 | 🟢 |
| 009-S2 | meta/factory validation_workflow를 우리 하네스 living blueprint에 reflexive 1회 실행 | outputs/improvement_reports/ 검증 리포트 | 6검증 우리 하네스 1회 기록 | 🟢 |
| 009-S3 | 보류 HIP-003/004/005 결착 | proposals 결정 갱신 | 3건 승인/반려 명시(004=006 데이터 후 임계) | 🟢 |

### HIP-010 유령/동결 정리 (P2) — 폐기 아닌 파생/정리
| slice | 내용 | 산출물 | 수락 | 구분 |
|---|---|---|---|---|
| 010-S1 | lookup_table.yaml → catalog.yaml 참조 수정 | harness-audit SKILL | §1/§5 참조 실존 | 🟢 trivial |
| 010-S2 | dreammate_current_harness_blueprint 현재 실측 갱신 = living blueprint 첫 갱신 | blueprint(Phase 26 / pytest 784 / contracts 등) | 실측 일치 + live 표기 | 🟢 |
| 010-S3 | 유령 eval 채널(cost_snapshots/design_reviews/security_reviews/qa_reports/bug_reports) 처분 | 재지정 or 폐기 결정(contract-change) | 각 채널 처분 명시 | 🟢 |
| 010-S4 | instruction_index self-map 파생/격하 결정 | dependency_map 처분 결정 | 파생 vs 격하 결정 기록 | 🟢(자동화=후속) |

---

## 2. 집행 wave (의존성·레버리지 순)

```
Wave 1 (this turn): 010-S1 → 006-S2 → 010-S2 → 009-S1
   (trivial 정리 + 텔레메트리 루프 폐쇄 + living blueprint + 메타-메타 cadence)
Wave 2: 007-S1(critic 보정) → 007-S2(real-eval 경로)         # P0 품질, focused
Wave 3: 008-S1 → 008-S4 → 008-S3 → 008-S2                    # 운영 도달성
Wave 4: 009-S2 → 009-S3 → 010-S3 → 010-S4                    # 메타-메타 완주 + 정리
Handoff(ops/사람): 006-S3 DB·staging / 007-S2 실행(키) / 007-S3 human N=5 / 008-S2 Supabase 적용
```

근거: 006-S1(발신기) 완료 → 006-S2(소비)가 텔레메트리 루프를 닫아 즉시 가치 입증. 010-S1/S2는 cheap+메타-메타 substrate. 그 위에서 009(루프)·007(품질)·008(운영)을 쌓는다.

---

## 3. 공통 수락 게이트 (매 slice)

- pytest 회귀 0 (기존 수정 0 = behavior-preserving) + 신규 test green
- scenario_simulation P-X2 게이트 유지(파일 구조 변경 시)
- gated default-off + graceful(런타임 변경) / proposal-first 결정(contract·skill 변경은 사용자 게이트)
- 산출물 경로·결정은 본 문서 + 해당 HIP §적용 결과에 기록

---

## 4. 진행 로그

- 2026-06-05: 플랜 수립 + Wave 1 착수. (slice별 결과는 아래 append)
- 2026-06-05 **Wave 1 완료 (4 slice)**:
  - 010-S1 ✅ harness-audit SKILL `lookup_table.yaml`(부재)→`catalog.yaml` 교정 (v1.2.0). audit M1 해소.
  - 006-S2 ✅ `observability/cost_report.py`(load/aggregate/render/build_cost_snapshot) + test 5 → pytest 784→**789**. cost-review 데이터 소비 경로 확보(cost_snapshots 부활 capability).
  - 010-S2 ✅ `dreammate_current_harness_blueprint` §0.1 LIVING UPDATE (Phase 26 / pytest 789 / meta 병합 / 4-tier / 관측성) — frozen self-map → living.
  - 009-S1 ✅ `self_improvement_loop` §5.1 메타-메타 루프 cadence (harness-audit 정기 + meta/factory validation_workflow reflexive + meta/audits) — Open Q5 해소.
  - 검증: full backend pytest **789 passed** (기존 779 수정 0 = behavior-preserving). 신규 파일만 추가 — scenario_sim 무영향.
- 다음: **Wave 2** (007-S1 critic 낙관편향 보정 P0 → 007-S2 real-eval 경로).
- 2026-06-05 **Wave 2 완료 (007-S1+S2 / 007-S3=human handoff)**:
  - 007-S1 ✅ critic 낙관편향 보정 — config flag(`critic_calibration_enabled`) + `CALIBRATION_PREAMBLE` + `_derive_verdict` 핵심차원 게이트(approve→revise) + P-007 v1.5.0(gated) + test 6 → pytest 789→**795**. "88점 함정" 게이트 차단. OFF byte-identical.
  - 007-S2 ✅ real-eval 정식 트리거 — `eval/run_eval.py`(run_and_report + build_real_llm_caller + CLI) — golden_set eval 한 명령 + regression_results 기록. mock 기본 + real opt-in(키 없으면 graceful mock). test 3 → pytest 795→**798**. "1회성→반복 가능" 해소.
  - 007-S3 🔴 human blind N=5 = handoff(사람, eval/human_review kit 존재).
- 다음: **Wave 3** (008 운영 도달성: S1 done정의 → S4 홈/네비 → S3 PlansRepo → S2 match SQL).
- 2026-06-05 **Wave 3 진행 (008-S1+S2 / S3·S4 다음)**:
  - 008-S1 ✅ qa-check **v1.3.0** 카테고리 12 "운영 도달성" — "동작≠도달" done 게이트(진입경로/flag ON/영속·운영의존 명시 or 이월). phase-complete 자동 포함.
  - 008-S2 ✅ `0008_match_approved_knowledge.sql` — RAG retrieval RPC 함수 정의(미정의→동작). Supabase 적용=ops(NG11). pytest 798 불변(retrieval RPC mock).
  - 008-S3 ✅ PlansRepo 영속 — `_persist_plan_envelope`(orchestrator seam, gated `plans_repo_enabled` default False, upsert+graceful) + config + test 4 → pytest 798→**802**. OFF byte-identical(기존 798 무수정). 실영속=Supabase ops.
  - 008-S4 ✅ 홈 진입 — `app/page.tsx` 에 /new·/new/branding 진입 카드(도달성) + stale footer 교정 + component_map AppShell deferred 주석. typecheck+lint pass. full AppShell=deferred.
- 2026-06-05 **Wave 3 완료** (008 전체: S1 done게이트 / S2 RAG RPC / S3 영속 / S4 홈진입). pytest 802.
- 2026-06-05 **Wave 4 완료 (009-S2/S3 + 010-S3/S4 — 문서·결정)**:
  - 009-S2 ✅ meta/factory validation_workflow 6검증을 우리 하네스에 **reflexive 적용(첫 실사용)** → `meta/factory/outputs/improvement_reports/2026-06-05_self-validation.md` (PASS 6 / fail 0 / pending-by-design 1, 신규 GAP 0 — audit 와 수렴).
  - 009-S3 ✅ 보류 HIP 결착 — HIP-003 **반려·흡수**(audit_naming) / HIP-004 **승인·정의**(HIP-006 데이터원 기반 multi-llm 임계) / HIP-005 **반려·흡수**(qa-check cat12+sanity).
  - 010-S3 ✅ 유령 eval 채널 처분(결정): `cost_snapshots`=부활(006-S2)·유지 / `design_reviews`·`eval/security_reviews`=흡수(회고 §B / meta/security_reviews) / `qa_reports`=historical 보존 / `docs/bug_reports`=on-demand(bug-triage). 빈 dedicated 채널은 "흡수" 확정 — 신규 산출은 실제 위치로.
  - 010-S4 ✅ `instruction_index/dependency_map.yaml` → **"frozen reference, 미유지" 격하**(헤더 주석) + living blueprint=canonical self-map 명시. 자동 파생=future.
- ★ **HIP-006~010 코드/문서 가능분 전부 집행 완료.** handoff(ops/사람): 006-S3 DB·staging / 007-S3 human N=5 / 008 Supabase 적용·full AppShell·실 e2e / HIP-004 multi-llm SKILL 반영(contract-change).
- 다음: **Phase C** 최종 검증 + 커밋.
