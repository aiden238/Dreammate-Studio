# Phase M1 회고 — Meta-Factory Sample Test (★ meta-phase, dry-run)

> 종료일: 2026-05-31
> 유형: meta-phase (제품 phase 아님 — M0 machinery 1회 dry-run 검증)
> 결과: ✅ A1~A8 + MG1~MG3 PASS / 6검증 PASS 5·PENDING 1 / GAP 8개 / ★ outputs/TEST/ 외 변경 0
> 트리거: phase-complete v1.2.0 §7 회고 자동 호출

---

## 1. 무엇을 했나

M0가 만든 meta_factory machinery(generation_workflow 11단계 + validation_workflow 6검증)를 **팟캐스트 에피소드 기획 AI** 도메인에 1회 dry-run 적용. 산출물 전부를 `meta_factory/outputs/TEST/` 에 격리(사용자 지침).

- **S1 (generation, dbe43c5)**: without baseline(machinery 미참조) → domain_brief → harness_blueprint + 6 scaffold. 9파일 996줄.
- **S2 (validation, 83fc1ac)**: 6검증(4상태) + with/without 6지표 수치화 + 5 gaps 재현 표 + GAP 8개. 2파일 320줄.
- **doc-sync (본 회고 포함)**: main 세션 별도 commit (GPT 보완 ③).

## 2. 핵심 결과

### machinery 가 "검증할 수 있다"는 것을 입증
- **6검증 PASS 5 / PENDING 1** (검증5 eval-run = 실측 미수행 정상). machinery 가 명확한 판정 기준을 제공.
- **가장 강한 증거 — 검증2 skill conflict**: machinery 가 반례 `podcast-eval-run` 신규 Skill의 eval-run 키워드 **4중첩**(eval 실행/golden_set/regression/품질 평가)을 정확히 검출 → 채택 사전 차단. "machinery 작동"의 결정적 사례.

### with/without 6지표 수치화 (주관 서술 0)
| 지표 | WITH | WITHOUT |
|---|---|---|
| 누락 필수파일 수 | 0 | 6 |
| forbidden_scope 반영 (0/1) | 1 | 0 |
| Skill trigger 충돌 수 | 0 | 0* |
| contract cross-ref 누락 수 | 0 | 4 |
| eval gate 존재 (0/1) | 1 | 0 |
| proposal-first 위반 (0=없음) | 0 | 0 |

\* 지표3 둘 다 0이나 의미 상이 — WITH은 검토 **수행** 후 0(machinery 작동), WITHOUT은 검토 절차 **부재**로 0(우연).

### 5 gaps 전부 재현 (재현 5 / 부분 0 / 비재현 0)
M0 blueprint §10이 명시한 현재 하네스 부족점 5개(생성 자동화 없음 / .claude/agents 자동생성 없음 / trigger dry-run 부족 / with-without 비교 부족 / acceptance 기준 부족)가 팟캐스트 도메인에서도 전부 재현. 부족점 4·5는 S2 절차 적용으로 **부분 완화**(절차는 작동, 도구·표본은 deferred). → M0의 "기준 정의 / payoff deferred" 구조와 정합.

## 3. GAP 8개 (= 다음 machinery 개선 입력, ★ 본 dry-run 의 핵심 산출)

| GAP | 내용 | 보완 대상 (proposal-only) |
|---|---|---|
| **G1** | expert_pool vs 단일 agent 파라미터화 결정 기준 부재 | architecture_patterns.md |
| **G2** ★ | skill 신규 vs 재사용 결정트리 부재 (검증4가 직접 입증) | generation_workflow.md 단계4 |
| **G3** ★ | conditional_execution 슬롯 부재 (agent+contract 양쪽 표현력) | agent_template + contract_template |
| **G4** | 조건부 eval 차원(applies_when) 미지원 | eval_template.md |
| **G5** ★ | 제3자(게스트) PII risk 격상 축 부재 (미해결 안전 risk) | domain_brief_schema risk_level |
| **G6** | domain_brief_schema data_model 전용 필드 부재 | domain_brief_schema.md |
| **G7** | meta-phase/dry-run 상태 표현 부재 | project_state_template harness_status enum |
| **G8** | validation enum이 pending-by-design 정상 케이스 미표현 | harness_blueprint_schema validation enum |

핵심 3개: **G2 / G3 / G5**. 실 보완은 contract-change 경유 + 사용자 승인 (S2는 제안만, machinery 0줄 변경).

## 4. 잘된 것

1. **outputs/TEST/ 격리 게이트(MG1) 작동** — S1·S2 모두 `git diff` 결과 TEST/ 외 0줄. 사용자 지침(테스트 산출물 격리) + GPT 보완 ③(outputs 외 변경 0)을 단일 게이트로 강제. dry-run이 실 하네스/런타임을 1줄도 건드리지 않음.
2. **dry-run ↔ doc-sync 분리(GPT 보완 ③)** — sub-agent는 outputs/TEST/만, phase 등록·회고·archive는 main 세션 별도 commit. 권한 분리로 게이트 무오염.
3. **4상태(PASS/FAIL/PENDING/GAP)가 첫 dry-run을 정직하게 표현** — 검증5/4 품질·일관성을 PENDING(소표본 정상)으로 기록, fail로 과장하지 않음. "성공"이 아니라 GAP 발견이 목적이라는 phase 정의 충실.
4. **without baseline 먼저 작성**(오염 최소화) — machinery 정독 전 naive 버전을 분리 파일로 → with/without 비교의 정직성 ↑ (잔존 오염은 한계로 명시).
5. **P-X1 52연속** — meta-phase dry-run에서도 sub-agent forbidden 0건 재발.

## 5. 아쉬운 것 / 한계

1. **검증5 실측 부재** — 실 LLM eval을 안 돌려 품질·일관성(검증4) 결론을 못 냄. 다음 개선: mock-deterministic eval 표본 1회라도 (eval-run §3~§6 위임).
2. **with/without 오염 잔존** — 단일 sub-agent가 without/with 둘 다 작성. 완전 순수 baseline 아님(machinery를 아는 상태). 별도 sub-agent 분리로 개선 가능하나 비용 trade-off.
3. **소표본(1 도메인 1회)** — 정량 우열 단정 불가. 방향성만. 인접 도메인(팟캐스트) 1개라 범용성은 1차 검증 수준.

## 6. 패턴

- **P-META-FACTORY-002 (신규 후보)** — Meta-Factory 첫 dry-run으로 machinery 실작동 + GAP 백로그 도출 (outputs/TEST/ 격리 + 4상태 + with/without 수치화). patterns.md 등록.
- **P-X1-EFFECT-001 update (52연속)** + **P-VALIDATION-FORMAL-001** (M1은 dry-run이라 신규 formal validation 미생성 — M0 8회 유지).

## 7. 다음 단계

1. **8 GAP을 machinery 개선 proposal로** — 핵심 G2/G3/G5 우선. 별도 meta-phase(M2?) 또는 Phase 10+ 사이 끼워넣기. contract-change 경유.
2. **검증5 실측 1회** — 팟캐스트 또는 Dreammate golden_set에 실 eval-run (mock-deterministic) 적용해 검증4 품질·일관성 PENDING 해소.
3. **Phase 10 (MVP 통합)** — 본 meta-phase와 독립. meta_factory blueprint + TEST 산출물 = 온보딩/감사 참고 자료.
4. (선택) 이질 도메인 dry-run — 범용성 2차 검증 (payoff deferred 해제 시점 재검토).

## 8. 메타 정합

- 제품 로드맵 0줄 진전(의식적 detour) — next_phase_status(pending_user_decision) 보존.
- runtime 0 (A9) + outputs/TEST/ 외 0 (MG1) — 격리 2중 게이트.
- ★ dry-run 의 핵심 산출은 "성공"이 아니라 **8 GAP 백로그** + "machinery는 검증 가능하다"는 입증.
